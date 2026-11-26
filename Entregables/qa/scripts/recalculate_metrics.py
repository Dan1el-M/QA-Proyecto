"""Refresh traceability and metrics only from preserved reports."""
import csv,hashlib,json,math,statistics
from collections import Counter
from pathlib import Path
from design import ROOT,APP_ROOT,DOCS,csvwrite


def readcsv(name):
    p=DOCS/name
    return list(csv.DictReader(p.open(encoding='utf-8-sig',newline=''))) if p.exists() else []


def human_data():
    found={}
    for p in sorted((ROOT/'qa/data/human').glob('*.json')):
        data=json.loads(p.read_text(encoding='utf-8'));found[data['kind']]=data
    return found


def recalculate():
    path=ROOT/'qa/data/design.json'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=(ROOT/'qa/data/design.sha256').read_text().strip():raise ValueError('Frozen design changed')
    design=json.loads(path.read_text(encoding='utf-8'));cases=design['cases'];byid={c['id']:c for c in cases}
    artifacts={};executions=[]
    groups={'unit':'UT','integration':'INT','security':'SEG','e2e':'E2E','accessibility':'ACC','performance-normal':'PERF-001','performance-high':'PERF-002'}
    for p in sorted((ROOT/'qa/reports/runs').glob('*/run.json')):
        run=json.loads(p.read_text(encoding='utf-8'));directory=p.parent
        for f in ['complexity.json','static-review.json','rubocop.json','brakeman.json']:
            if (directory/f).exists():artifacts[f]=directory/f
        if (directory/'jscpd/jscpd-report.json').exists():artifacts['duplication']=directory/'jscpd/jscpd-report.json'
        for job in run['jobs']:
            executions.append(job|{'run':run['run_id']})
            prefix=groups.get(job['name'])
            if prefix:
                matched=[c for c in cases if c['id']==prefix or c['id'].startswith(prefix+'-')]
                for c in matched:
                    if job.get('exit_code') is not None:
                        c.update(estado='Bloqueado',obtenido='El proceso no produjo un resultado individual concluyente; consultar el registro y el código de salida '+str(job['exit_code']),evidencia=job['log'],fecha=run['run_id'])
            resultfile=directory/(job['name']+'.json')
            if job['name'] in ['unit','integration','security'] and resultfile.exists():
                for result in json.loads(resultfile.read_text(encoding='utf-8')):
                    c=byid[result['id']];c.update(estado=result['status'],obtenido=result['observed'] or f"Aserciones: {result['assertions']}; tiempo: {result['seconds']:.3f}s",evidencia=str(resultfile.relative_to(ROOT)),fecha=run['run_id'])
                    c['aserciones']=result['assertions']
            if job['name']=='static-review' and (directory/'static-review.json').exists():
                c=byid['EST-001'];c.update(estado='Fallido',obtenido='Hallazgos estáticos registrados; no se realizaron correcciones',evidencia=str((directory/'static-review.json').relative_to(ROOT)),fecha=run['run_id'])
        browser=directory/'playwright.json'
        if browser.exists():
            data=json.loads(browser.read_text(encoding='utf-8'))
            def walk(suite):
                for spec in suite.get('specs',[]):
                    cid=spec['title'].split(' ')[0]
                    if cid not in byid:continue
                    tests=spec.get('tests',[]);result=tests[0].get('results',[])[-1] if tests and tests[0].get('results') else None
                    if result:
                        status=result['status'];byid[cid].update(estado='Aprobado' if status=='passed' else 'Bloqueado' if status=='skipped' else 'Fallido',obtenido='\n'.join(e.get('message','') for e in result.get('errors',[])) or status,evidencia=str(browser.relative_to(ROOT)),fecha=run['run_id'])
                for child in suite.get('suites',[]):walk(child)
            for suite in data.get('suites',[]):walk(suite)
        for axe in directory.glob('axe-ACC-*.json'):
            cid=axe.stem.removeprefix('axe-');data=json.loads(axe.read_text(encoding='utf-8'))
            if cid in byid:byid[cid].update(estado='Bloqueado',obtenido=f"axe ejecutado: {len(data['violations'])} reglas con hallazgos. Falta ratificación y revisión manual",evidencia=str(axe.relative_to(ROOT)),fecha=run['run_id'])
    humans=human_data()
    if 'acceptance' in humans:
        for cid in ['UAT-001','UAT-002','UAT-003']:
            rows=[r for r in humans['acceptance']['rows'] if r['caso']==cid]
            complete=len({r['participante'] for r in rows})>=2
            if rows:byid[cid].update(estado='Aprobado' if complete and all(r['estado']=='Aprobado' for r in rows) else 'Fallido' if any(r['estado']!='Aprobado' for r in rows) else 'Bloqueado',obtenido=f'{len(rows)} observaciones humanas confirmadas',evidencia=';'.join(r['evidencia'] for r in rows))
    if 'usability' in humans:
        rows=humans['usability']['rows'];complete=len(rows)==9 and len({r['participante'] for r in rows})==3
        byid['USA-001'].update(estado='Aprobado' if complete and all(r['estado']=='Aprobado' for r in rows) else 'Fallido' if complete else 'Bloqueado',obtenido=f'{len(rows)} intentos humanos confirmados',evidencia=';'.join(r['evidencia'] for r in rows))
    if 'accessibility' in humans:
        expected_per_screen=json.loads((ROOT/'qa/accessibility/criterios.json').read_text())['per_screen'] if (ROOT/'qa/accessibility/criterios.json').exists() else 12
        for cid in ['ACC-001','ACC-002','ACC-003']:
            rows=[r for r in humans['accessibility']['rows'] if r['pantalla']==cid]
            if len(rows)>=expected_per_screen and 'axe' in byid[cid]['evidencia']:
                byid[cid]['estado']='Fallido' if any(r['estado']=='Fallido' for r in rows) else 'Aprobado'
                byid[cid]['evidencia']+=';'+';'.join(r['evidencia'] for r in rows)
    defects=readcsv('Registro_Defectos.csv')
    for c in cases:
        associated=[d for d in defects if c['id'] in d['caso'].split(';')]
        c['defecto']=';'.join(d['id'] for d in associated)
    csvwrite(DOCS/'Casos_de_Prueba.csv',[{k:c.get(k,'') for k in design['cases'][0]} for c in cases])
    trace=[]
    for c in cases:
        for req in c['requerimiento'].split(';'):
            trace.append(dict(requerimiento=req,caracteristica=c['caracteristica'],caso=c['id'],tipo_nivel=c['tipo']+' / '+c['nivel'],prueba_automatizada=c['funcion'] if c['automatizada']=='Sí' else 'Manual',resultado=c['estado'],defecto=c['defecto'],responsable=c['responsable'],metrica=c['metrica'],evidencia=c['evidencia'],implementacion=c['implementacion'],pregunta_gqm=';'.join(q['pregunta_id'] for q in design['gqm'] if set(c['metrica'].split(';'))&set(q['metricas'].split(';')))))
    csvwrite(DOCS/'Matriz_Trazabilidad.csv',trace)
    metrics=[]
    def met(mid,value,interpretation,evidence='',state=None,numerator='',denominator=''):
        i=int(mid[-2:]);sheet=design['metrics'][i-1]
        if value is None:status='No evaluado'
        elif state:status=state
        elif i in [1,2,3,8,11]:
            a,b={1:(100,80),2:(95,80),3:(80,60),8:(100,80),11:(100,80)}[i]
            status='Aceptación total' if value>=a else 'Aceptación parcial' if value>=b else 'Rechazo'
        elif i in [4,5,6,9,10,12]:
            a,b={4:(10,15),5:(3,5),6:(5,10),9:(1,2),10:(1,5),12:(1,1.5)}[i]
            status='Aceptación total' if value<=a else 'Aceptación parcial' if value<=b else 'Rechazo'
        else:status='Evaluación parcial'
        metrics.append(dict(id=mid,nombre=sheet['nombre'],resultado='No evaluado' if value is None else round(value,3) if isinstance(value,(int,float)) else value,estado=status,numerador=numerator,denominador=denominator,unidad=sheet['unidad'],interpretacion=interpretation,evidencia=evidence,total=sheet['total'],parcial=sheet['parcial'],rechazo=sheet['rechazo']))
    rf=[r for r in design['requirements'] if r['tipo']=='Funcional' and r['seleccionado']=='Sí']
    covered=[r for r in rf if any(r['id'] in c['requerimiento'].split(';') for c in cases)]
    validated=[r for r in rf if any(r['id'] in c['requerimiento'].split(';') and c['estado']=='Aprobado' for c in cases)]
    met('MET-01',len(covered)/len(rf)*100,f'Diseño: {len(covered)}/{len(rf)}. RF con al menos evidencia aprobada: {len(validated)}. No equivale a validación integral.','qa/data/Casos_Diseno_Pre_Ejecucion.csv',numerator=len(covered),denominator=len(rf))
    functional=[c for c in cases if c['tipo']=='Funcional'];conclusive=[c for c in functional if c['estado'] in ['Aprobado','Fallido']];passed=sum(c['estado']=='Aprobado' for c in conclusive)
    met('MET-02',passed/len(conclusive)*100 if conclusive else None,f'{len(conclusive)}/{len(functional)} casos funcionales concluyentes; avance {len(conclusive)/len(functional)*100:.2f}%. Bloqueados y no ejecutados se reportan aparte.','docs/Casos_de_Prueba.csv',numerator=passed,denominator=len(conclusive))
    coverage={}
    for p in (ROOT/'qa/reports/runs').glob('*/coverage-*/.resultset.json'):
        group=p.parent.name.removeprefix('coverage-')
        if not (p.parent.parent/(group+'.json')).exists():continue
        for result in json.loads(p.read_text(encoding='utf-8')).values():
            for file,lines in result['coverage'].items():
                values=lines['lines'] if isinstance(lines,dict) else lines
                old=coverage.setdefault(file,[None]*len(values))
                for index,n in enumerate(values):
                    if n is not None:old[index]=max(old[index] or 0,n)
    executable=sum(n is not None for values in coverage.values() for n in values);hit=sum(n is not None and n>0 for values in coverage.values() for n in values)
    met('MET-03',hit/executable*100 if executable else None,'Unión de líneas SimpleCov en corridas del mismo commit; app/**/*.rb; sin dependencias ni código generado.','qa/reports/runs/*/coverage-*/.resultset.json' if coverage else '',numerator=hit if coverage else '',denominator=executable if coverage else '')
    if 'complexity.json' in artifacts:
        p=artifacts['complexity.json'];data=json.loads(p.read_text(encoding='utf-8'))
        met('MET-04',data['max'],f"{data['count']} métodos; promedio {data['average']:.2f}; distribución {data['distribution']}. Convención AST declarada; no es complejidad cognitiva.",str(p.relative_to(ROOT)))
    else:met('MET-04',None,'Sin reporte AST válido')
    if 'duplication' in artifacts:
        p=artifacts['duplication'];data=json.loads(p.read_text(encoding='utf-8'));intervals={}
        for clone in data.get('duplicates',[]):
            for side in ['firstFile','secondFile']:
                f=clone[side];name=f['name'].replace('\\','/')
                intervals.setdefault(name,set()).update(range(f['start'],f['end']+1))
        total=data.get('statistics',{}).get('total',{}).get('lines',0)
        duplicated=sum(len(lines) for lines in intervals.values())
        met('MET-05',duplicated/total*100 if total else None,'Unión de intervalos de líneas duplicadas por archivo; bloques de>=5 líneas y>=50 tokens; denominador de jscpd. No se usa el número de clones como porcentaje.',str(p.relative_to(ROOT)),numerator=duplicated,denominator=total)
    else:met('MET-05',None,'Sin reporte de duplicación válido')
    minutes=sum(float(d['costo_minutos']) for d in defects if str(d['costo_minutos']).replace('.','',1).isdigit())
    loc=sum(1 for p in (APP_ROOT/'app').rglob('*.rb') for s in p.read_text(encoding='utf-8').splitlines() if s.strip() and not s.lstrip().startswith('#'))
    met('MET-06',minutes/(2*loc)*100 if defects and loc else None,f'Estimación de los12 hallazgos manuales: remediación {minutes:g}min; desarrollo {loc}LOC×2min/LOC. Los candidatos automáticos sin estimación se excluyen; es un piso del costo. Sensibilidad: a1 y4min/LOC el cociente se duplica o reduce a la mitad. No es SonarQube.','docs/Deuda_Tecnica.csv',numerator=minutes,denominator=2*loc)
    security=[c for c in cases if c['id'].startswith('SEG-')];con=[c for c in security if c['estado'] in ['Aprobado','Fallido']]
    confirmed=[d for d in defects if d['tipo']=='Vulnerabilidad confirmada']
    met('MET-07',None if len(con)<6 else '; '.join(f'{k}:{v}' for k,v in Counter(d['severidad'] for d in confirmed).items()) or '0 confirmadas',f"Candidatos sin verificar: {sum(d['tipo'] in ['Candidato de seguridad','Dependencia vulnerable candidata'] for d in defects)}. No inferir ausencia de vulnerabilidades de controles incompletos.",'docs/Registro_Defectos.csv',state='Evaluación parcial')
    met('MET-08',sum(c['estado']=='Aprobado' for c in con)/len(con)*100 if con else None,f'{len(con)}/6 controles concluyentes. Bloqueos y candidatos separados.','docs/Casos_de_Prueba.csv',numerator=sum(c['estado']=='Aprobado' for c in con),denominator=len(con))
    # k6 per-sample output is the authoritative source for route/load percentiles.
    perf=[]
    for p in sorted((ROOT/'qa/reports/runs').glob('*/k6-*.jsonl')):
        groups={}
        for line in p.open(encoding='utf-8'):
            item=json.loads(line)
            if item.get('type')!='Point' or item.get('metric') not in ['qa_latency','qa_invalid_content']:continue
            d=item['data'];tags=d.get('tags',{});level=tags.get('load')
            if level not in ['5','10','20','25','50','100']:continue
            key=(tags.get('scenario'),tags.get('route'),level);groups.setdefault(key,{'times':[],'errors':[]})['times' if item['metric']=='qa_latency' else 'errors'].append(d['value'])
        for (scenario,route,load),values in groups.items():
            t=sorted(values['times']);n=len(t);e=values['errors']
            if n:perf.append(dict(escenario=scenario,ruta=route,carga=load,solicitudes=n,promedio_ms=statistics.mean(t),mediana_ms=statistics.median(t),p90_ms=t[math.ceil(.90*n)-1],p95_ms=t[math.ceil(.95*n)-1],p99_ms=t[math.ceil(.99*n)-1],errores_pct=sum(e)/len(e)*100 if e else None,evidencia=str(p.relative_to(ROOT))))
    if perf:csvwrite(DOCS/'Resultados_Rendimiento.csv',perf)
    met('MET-09',max(r['p95_ms'] for r in perf)/1000 if perf else None,'Peor P95 por ruta y carga; conservar desglose. No extrapolar capacidad del equipo local.','docs/Resultados_Rendimiento.csv' if perf else '')
    met('MET-10',max(r['errores_pct'] for r in perf if r['errores_pct'] is not None) if perf else None,'Peor tasa por nivel; transporte,HTTP y contenido se preservan en JSONL.','docs/Resultados_Rendimiento.csv' if perf else '')
    rows=humans.get('usability',{}).get('rows',[]);complete=len(rows)==9 and len({r['participante'] for r in rows})==3
    if rows:
        descriptives=[]
        for task in ['T1','T2','T3']:
            attempts=[r for r in rows if r['tarea']==task]
            if not attempts:continue
            seconds=[float(r['segundos']) for r in attempts]
            descriptives.append(dict(tarea=task,intentos=len(attempts),aprobados=sum(r['estado']=='Aprobado' for r in attempts),fallidos=sum(r['estado']=='Fallido' for r in attempts),abandonados=sum(r['estado']=='Abandonado' for r in attempts),media_segundos=statistics.mean(seconds),mediana_segundos=statistics.median(seconds),minimo_segundos=min(seconds),maximo_segundos=max(seconds),objetivo_segundos=120 if task=='T1' else 90))
        csvwrite(DOCS/'Resultados_Usabilidad.csv',descriptives)
    met('MET-11',sum(r['estado']=='Aprobado' for r in rows)/len(rows)*100 if complete else None,'Solo intentos reales confirmados; incluir fallos y abandonos.','qa/usability/resultados.csv' if rows else '',numerator=sum(r['estado']=='Aprobado' for r in rows),denominator=len(rows))
    ratios=[float(r['segundos'])/({'T1':120,'T2':90,'T3':90}[r['tarea']]) for r in rows]
    met('MET-12',max(ratios) if complete else None,'Razón del peor tiempo respecto al objetivo; segundos individuales permanecen en formularios.','qa/usability/resultados.csv' if rows else '')
    manual=humans.get('accessibility',{}).get('rows',[]);failed=[r for r in manual if r['estado']=='Fallido']
    acc_complete=all(byid[cid]['estado'] in ['Aprobado','Fallido'] for cid in ['ACC-001','ACC-002','ACC-003'])
    blocking=any(r['bloqueante']=='true' for r in failed)
    met('MET-13',len(failed) if acc_complete or blocking else None,f'Revisión manual y automática deben contrastarse. Pares pantalla/criterio con incumplimiento confirmado: {len(failed)}; no equivale a una declaración global de conformidad.','qa/accessibility/manual.csv' if manual else '',state='Rechazo' if blocking else 'Aceptación parcial' if failed else 'Aceptación total')
    csvwrite(DOCS/'Resultados_Metricas.csv',metrics)
    summary={'designed':len(cases),'automated':sum(c['automatizada']=='Sí' for c in cases),'implemented':sum((ROOT/c['implementacion']).exists() for c in cases),'states':dict(Counter(c['estado'] for c in cases)),
             'conclusive':sum(c['estado'] in ['Aprobado','Fallido'] for c in cases),'rf_selected':len(rf),'rnf_selected':sum(r['tipo']=='No funcional' and r['seleccionado']=='Sí' for r in design['requirements']),
             'rf_with_passed_evidence':len(validated),'metrics_evaluated':sum(m['estado']!='No evaluado' for m in metrics),'metrics_pending':sum(m['estado']=='No evaluado' for m in metrics),
             'defects_confirmed':sum(d['confirmacion'].startswith('Confirmado') for d in defects),'security_candidates':sum(d['tipo'] in ['Candidato de seguridad','Dependencia vulnerable candidata'] for d in defects),
             'by_level':{},'by_characteristic':{},'by_owner':{},'by_requirement':{},'release':'Liberación no recomendada' if any(d['severidad'] in ['Alta','Crítica'] and d['confirmacion'].startswith('Confirmado') for d in defects) else 'Evidencia insuficiente para emitir una recomendación definitiva'}
    for field,key in [('nivel','by_level'),('caracteristica','by_characteristic'),('responsable','by_owner')]:
        summary[key]={v:dict(Counter(c['estado'] for c in cases if c[field]==v)) for v in sorted({c[field] for c in cases})}
    for r in design['requirements']:
        summary['by_requirement'][r['id']]=dict(Counter(c['estado'] for c in cases if r['id'] in c['requerimiento'].split(';')))
    (ROOT/'qa/reports/summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    (ROOT/'qa/reports/executions.json').write_text(json.dumps(executions,indent=2,ensure_ascii=False),encoding='utf-8')
    return design,cases,metrics,summary,artifacts


if __name__=='__main__':
    _,_,_,summary,_=recalculate();print(json.dumps(summary,ensure_ascii=True,indent=2))
