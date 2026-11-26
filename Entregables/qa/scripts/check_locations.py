"""Verify the relocated harness without changing application code or historic evidence."""
import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone, timedelta
from paths import ROOT, APP_ROOT
from run_all import environment


def main():
    checks = []
    def add(name, passed, **details):
        checks.append(dict(name=name, passed=bool(passed), **details))
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    add('Separate application and deliverables roots', ROOT.name == 'Entregables' and (APP_ROOT/'config/application.rb').is_file())
    baseline = json.loads((ROOT/'qa/reports/baseline/baseline.json').read_text(encoding='utf-8'))
    changed = [name for name, sha in baseline['sha256'].items() if not (APP_ROOT/name).is_file() or digest(APP_ROOT/name) != sha]
    add('Original tracked application files', not changed, count=len(baseline['sha256']), changed=changed)
    frozen = ROOT/'qa/data/design.json'
    add('Frozen test design', digest(frozen) == (ROOT/'qa/data/design.sha256').read_text().strip())
    design = json.loads(frozen.read_text(encoding='utf-8'))
    missing = [case['id'] for case in design['cases'] if not (ROOT/case['implementacion']).is_file()]
    add('Case implementation paths', not missing, count=len(design['cases']), missing=missing)
    snapshot = json.loads((ROOT/'qa/reports/baseline/relocation-preserved.json').read_text(encoding='utf-8'))
    altered = [name for name, sha in snapshot['sha256'].items() if not (ROOT/name).is_file() or digest(ROOT/name) != sha]
    add('Historic raw evidence, frozen files and user references preserved', not altered, count=len(snapshot['sha256']), changed=altered)
    config = subprocess.run([shutil.which('node'), str(ROOT/'qa/scripts/check_config.cjs')], cwd=APP_ROOT, capture_output=True, text=True, encoding='utf-8')
    add('CI location and YAML configuration from repository root', config.returncode == 0, output=config.stdout.strip(), error=config.stderr.strip())
    latest = ROOT/json.loads((ROOT/'qa/reports/latest.json').read_text(encoding='utf-8'))['path']
    units = json.loads((latest/'unit.json').read_text(encoding='utf-8'))
    add('Relocated native unit execution', len(units) == 18 and all(row['status'] == 'Aprobado' for row in units), run=latest.name, cases=len(units), assertions=sum(row['assertions'] for row in units))
    metrics = list(csv.DictReader((ROOT/'docs/Resultados_Metricas.csv').open(encoding='utf-8-sig')))
    coverage = next(row for row in metrics if row['id'] == 'MET-03')
    add('Application coverage scope retained', int(coverage['numerador']) == 208 and int(coverage['denominador']) == 1629, numerator=coverage['numerador'], denominator=coverage['denominador'])
    measured = json.loads((ROOT/'qa/reports/relocation/complexity.json').read_text(encoding='utf-8'))
    add('Static analysis finds original application', measured['count'] == 210 and measured['max'] == 14 and not measured['parse_errors'], methods=measured['count'], maximum=measured['max'])
    missing_evidence = [case['id'] for case in csv.DictReader((ROOT/'docs/Casos_de_Prueba.csv').open(encoding='utf-8-sig')) if case['estado'] != 'No ejecutado' and any(not (ROOT/item).is_file() for item in case['evidencia'].split(';') if item)]
    add('Case evidence paths resolve after relocation', not missing_evidence, missing=missing_evidence)
    env = environment()
    boot = subprocess.run([shutil.which('ruby', path=env['PATH']) or 'ruby', '-r', str(ROOT/'qa/scripts/stdio.rb'), '-e', 'require ARGV.fetch(0); puts "QA boot ready"', str(ROOT/'qa/boot.rb')], cwd=ROOT, env=env, capture_output=True, timeout=30)
    log = ROOT/'qa/reports/relocation/boot.log'
    output = (boot.stdout+boot.stderr).decode('utf-8', errors='replace')
    log.write_text(output, encoding='utf-8')
    known_block = boot.returncode != 0 and 'Bundler::GemNotFound' in output and 'sqlite3' in output
    add('Boot reaches original Gemfile without missing relocated files', boot.returncode == 0 or known_block)
    report = dict(checked_at=datetime.now(timezone(timedelta(hours=-6))).isoformat(), application_root=str(APP_ROOT), deliverables_root=str(ROOT), checks=checks, relocation_checks_passed=all(row['passed'] for row in checks), application_bundle_ready=boot.returncode == 0, existing_environment_blocker='Missing sqlite3 native gem' if known_block else output.strip() if boot.returncode else None, boot_exit_code=boot.returncode, boot_log=str(log.relative_to(ROOT)), note='Historic reports retain their original command paths; current QA paths are relative to Entregables, original source paths to the repository root.')
    (ROOT/'qa/reports/Relocation_Validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checks':len(checks), 'failures':[row['name'] for row in checks if not row['passed']], 'application_bundle_ready':report['application_bundle_ready'], 'existing_environment_blocker':report['existing_environment_blocker']}, ensure_ascii=True))
    return int(not report['relocation_checks_passed'])


if __name__ == '__main__':
    raise SystemExit(main())
