"""Validate and preserve real, confirmed human results; blank forms are not results."""
import csv,hashlib,json,sys
from datetime import datetime
from pathlib import Path
from design import ROOT


def evidence(path):
    target=(ROOT/path).resolve()
    if not target.is_relative_to((ROOT/'qa/evidence').resolve()) or not target.is_file():
        raise ValueError('Evidence must exist under qa/evidence: '+path)
    return path


def validate(source):
    if source.suffix.lower()=='.json':
        data=json.loads(source.read_text(encoding='utf-8-sig'))
        if data.get('confirmado') is not True:raise ValueError('Inspection has not been confirmed')
        datetime.fromisoformat(data['fecha_real'])
        roles=data['roles_reales'];author=data['autor_artefacto']
        if set(roles)!= {'moderador','revisor','escriba'} or len(set(roles.values()))!=3:raise ValueError('Three distinct inspection roles required')
        if author in [roles['moderador'],roles['escriba']]:raise ValueError('Author cannot moderate or record own inspection')
        for e in data['evidencias']:evidence(e)
        if not data['evidencias'] or not data['decision_por_hallazgo']:raise ValueError('Missing inspection evidence or decisions')
        return 'inspection',data
    rows=list(csv.DictReader(source.open(encoding='utf-8-sig',newline='')))
    result=[];keys=set()
    kind='usability' if 'usability' in source.parts else 'accessibility' if 'accessibility' in source.parts else 'acceptance'
    for row in rows:
        if not row.get('estado'):continue
        if row.get('confirmado','').lower()!='true':raise ValueError('A filled row needs confirmado=true')
        evidence(row['evidencia'])
        if kind=='accessibility':
            criteria_path=ROOT/'qa/accessibility/criterios.json'
            if criteria_path.exists() and row['criterio'] not in json.loads(criteria_path.read_text())['criteria']:raise ValueError('Unknown WCAG criterion')
            if row['pantalla'] not in ['ACC-001','ACC-002','ACC-003']:raise ValueError('Unknown accessibility screen')
            key=(row['pantalla'],row['criterio'])
            if row['estado'] not in ['Aprobado','Fallido','No aplica']:raise ValueError('Invalid accessibility state')
            if row['estado']=='No aplica' and not row['observacion']:raise ValueError('Explain non-applicability')
            if row['bloqueante'] not in ['true','false']:raise ValueError('Declare blocking impact')
        else:
            if row['participante'] not in ['P01','P02','P03']:raise ValueError('Only anonymous P01..P03 identifiers allowed')
            if row['external'].lower()!='true' or row['consentimiento'].lower()!='true':raise ValueError('Confirm external participation and consent')
            datetime.fromisoformat(row['fecha_real'])
            key=(row['participante'],row.get('tarea',row.get('caso')))
            if row['estado'] not in ['Aprobado','Fallido','Abandonado']:raise ValueError('Invalid human state')
            if kind=='usability':
                if row['tarea'] not in ['T1','T2','T3'] or float(row['segundos'])<0:raise ValueError('Invalid task or seconds')
                if row['satisfaccion'] and not 1<=int(row['satisfaccion'])<=5:raise ValueError('Satisfaction must be1..5')
            elif row['caso'] not in ['UAT-001','UAT-002','UAT-003'] or not row['decision']:raise ValueError('Missing UAT case/decision')
        if key in keys:raise ValueError('Duplicate human result: '+str(key))
        keys.add(key);result.append(row)
    if not result:raise ValueError('Form is blank: no human activities can be credited')
    return kind,result


def main():
    source=Path(sys.argv[1]).resolve();kind,rows=validate(source)
    out=ROOT/'qa/data/human';out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now().strftime('%Y%m%dT%H%M%S%f')
    payload={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'kind':kind,'rows':rows,'imported_at':datetime.now().isoformat()}
    (out/f'{stamp}-{kind}.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Validated and imported',kind,'; run bash qa/scripts/finalize_report.sh')


if __name__=='__main__':main()
