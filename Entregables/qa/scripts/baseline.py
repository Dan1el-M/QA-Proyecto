"""Record the original, tracked application without reading secret values."""
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

from paths import ROOT, APP_ROOT


def git(*args):
    return subprocess.check_output(['git', *args], cwd=APP_ROOT, text=True, encoding='utf-8').strip()


def main():
    target = ROOT / 'qa/reports/baseline/baseline.json'
    if target.exists():
        old = json.loads(target.read_text(encoding='utf-8'))
        changed = [p for p, digest in old['sha256'].items()
                   if not (APP_ROOT / p).exists() or hashlib.sha256((APP_ROOT / p).read_bytes()).hexdigest() != digest]
        report = {'baseline_commit': old['commit'], 'changed_original_files': changed,
                  'checked_at': datetime.now(timezone(timedelta(hours=-6))).isoformat(),
                  'status': git('status', '--short')}
        (target.parent / 'integrity.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=True))
        return int(bool(changed))
    files = git('ls-files').splitlines()
    data = {'commit': git('rev-parse', 'HEAD'), 'branch_audited': 'main',
            'working_branch': git('branch', '--show-current'), 'remote': git('remote', 'get-url', 'origin'),
            'recorded_at': datetime.now(timezone(timedelta(hours=-6))).isoformat(),
            'os': platform.platform(), 'initial_tracked_changes': git('diff', '--name-only'),
            'sha256': {p: hashlib.sha256((APP_ROOT / p).read_bytes()).hexdigest() for p in files}}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Recorded', len(files), 'original files at', data['commit'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
