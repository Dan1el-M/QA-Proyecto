"""Keep all automatic observations; group conventions without inflating defects."""
import json
from collections import defaultdict
from design import ROOT,DOCS,J,C,csvwrite
from recalculate_metrics import readcsv


def main():
    found=sorted((ROOT/'qa/reports/runs').glob('*/rubocop.json'))
    observations=[];groups=defaultdict(list)
    if found:
        source=found[-1];data=json.loads(source.read_text(encoding='utf-8'))
        for file in data['files']:
            for item in file['offenses']:
                row=dict(id=f'HERR-{len(observations)+1:04}',herramienta='RuboCop',regla=item['cop_name'],archivo=file['path'],linea=item['location']['start_line'],mensaje=item['message'],severidad_herramienta=item['severity'],evidencia=str(source.relative_to(ROOT)),estado='Pendiente de revisión humana')
                observations.append(row);groups[('RuboCop',item['cop_name'])].append(row)
    reek=sorted((ROOT/'qa/reports/runs').glob('*/reek.log'))
    if reek:
        source=reek[-1];text=source.read_text(encoding='utf-8');start=text.find('[{"context"')
        if start>=0:
            try:data,_=json.JSONDecoder().raw_decode(text[start:])
            except json.JSONDecodeError:data=[]
            for item in data:
                row=dict(id=f'HERR-{len(observations)+1:04}',herramienta='Reek',regla=item['smell_type'],archivo=item['source'],linea=item['lines'][0],mensaje=item['context']+': '+item['message'],severidad_herramienta='Smell candidato',evidencia=str(source.relative_to(ROOT)),estado='Pendiente; hubo errores parciales del parser')
                observations.append(row);groups[('Reek',item['smell_type'])].append(row)
    defects=[d for d in readcsv('Registro_Defectos.csv') if d['tipo'] not in ['Anomalía automática candidata','Dependencia sin soporte','Hallazgo descartado de seguridad']]
    template=defects[0]
    for i,((tool,rule),items) in enumerate(sorted(groups.items()),22):
        # Duplicate method declaration is already DEF-005.
        if rule=='Lint/DuplicateMethods':
            defects[4]['evidencia']+=';'+items[0]['evidencia'];continue
        file=items[0]['archivo'];line=items[0]['linea']
        defects.append(dict(template,id=f'DEF-{i:03}',titulo=f'{tool}: {rule}',descripcion=f'{len(items)} observaciones automáticas agrupadas por regla; necesitan clasificación. No equivalen a {len(items)} defectos funcionales.',
          severidad='Baja',prioridad='P4',pasos=f'Consultar {tool},regla {rule},en Hallazgos_Herramientas.csv y su reporte original.',
          esperado='Revisar aplicabilidad de la regla y aceptar,rechazar o vincular a un hallazgo existente con una decisión explícita.',actual=items[0]['mensaje'],
          evidencia=items[0]['evidencia']+';docs/Hallazgos_Herramientas.csv',estado='Pendiente de clasificación',confirmacion='Candidato de herramienta; no validado',tipo='Anomalía automática candidata',responsable=J,caso='EST-001',requerimiento='RNF-01',caracteristica='Mantenibilidad',
          modulo=file.split('/')[1],archivo=file,linea=line,impacto='Riesgo potencial de analizabilidad o modificación; no se infiere afectación funcional de una convención',recomendacion='Revisar cada ubicación; evitar corrección automática durante auditoría',costo_minutos='No estimado'))
    # Advisories match versions; affected feature/exploitability remains unverified.
    advisories=defaultdict(list)
    audit=sorted((ROOT/'qa/reports/runs').glob('*/bundler-audit.log'))
    if audit:
        source=audit[-1];text=source.read_text(encoding='utf-8');start=text.find('{"version"')
        if start>=0:
            data,_=json.JSONDecoder().raw_decode(text[start:])
            for result in data.get('results',[]):
                if result.get('advisory'):advisories[result['advisory']['id']].append(result)
            (DOCS/'Dependencias_Advisories.json').write_text(json.dumps({'evidence':str(source.relative_to(ROOT)),'results':data.get('results',[]),'interpretation':'Version matches only; feature applicability and exploitability unconfirmed'},indent=2,ensure_ascii=False),encoding='utf-8')
            # Remove previous automatic advisory candidates on repeat regeneration.
            defects=[d for d in defects if d['tipo']!='Dependencia vulnerable candidata']
            next_id=max(int(d['id'][4:]) for d in defects)+1
            for i,(aid,items) in enumerate(sorted(advisories.items()),next_id):
                advisory=items[0]['advisory'];packages=';'.join(x['gem']['name']+'@'+x['gem']['version'] for x in items)
                defects.append(dict(template,id=f'DEF-{i:03}',titulo=aid+': '+advisory['title'],descripcion='Coincidencia de versiones: '+packages+'. Aplicabilidad funcional y explotación pendientes; no se afirma una vulnerabilidad confirmada de la aplicación.',
                  severidad='Media',prioridad='P3',pasos='Ejecutar Bundler Audit contra Gemfile.lock y revisar las condiciones del advisory '+aid,
                  esperado='Determinar si la función afectada está habilitada y clasificar el riesgo con evidencia; no actualizar producción durante auditoría.',actual=packages,
                  evidencia=str(source.relative_to(ROOT))+';'+advisory['url'],estado='Pendiente de aplicabilidad',confirmacion='Candidato de dependencia; severidad provisional',tipo='Dependencia vulnerable candidata',responsable=C,caso='SEG-005',requerimiento='RNF-03',caracteristica='Seguridad',modulo='Dependencias',archivo='Gemfile.lock',linea=1,
                  impacto='Depende de las funciones habilitadas,exposición yprerrequisitos del advisory',recomendacion='Confirmar aplicabilidad yseveridad antes de proponer remediación',costo_minutos='No estimado'))
    brakeman=sorted((ROOT/'qa/reports/runs').glob('*/brakeman.json'))
    if brakeman:
        source=brakeman[-1];scan=json.loads(source.read_text(encoding='utf-8'))
        next_id=max(int(d['id'][4:]) for d in defects)+1
        for i,w in enumerate(scan.get('warnings',[]),next_id):
            observations.append(dict(id=f'HERR-{len(observations)+1:04}',herramienta='Brakeman',regla=w['warning_type'],archivo=w['file'],linea=w['line'],mensaje=w['message'],severidad_herramienta=w['confidence'],evidencia=str(source.relative_to(ROOT)),estado='Revisión de aplicabilidad documentada en Registro_Defectos.csv'))
            if w['warning_type']=='Mass Assignment':
                kind='Hallazgo descartado de seguridad';confirmation='Falso positivo revisado estáticamente'
                explanation='permit! amplía los parámetros de entrada,pero el flujo extrae explícitamente los cuatro valores de marcador ylos pasa como argumentos escalares a registrar_resultado!; el hash completo no se asigna al modelo. No se confirma asignación masiva arbitraria. La validación de tipos permanece cubierta por DEF-004.'
            else:
                kind='Dependencia sin soporte';confirmation='Confirmado documentalmente'
                explanation='Rails7.1.6 pertenece a una serie fuera de soporte,según el aviso oficial del29octubre2025. Esto es un riesgo de mantenimiento yno demuestra por sí solo la explotación de una vulnerabilidad.'
            defects.append(dict(template,id=f'DEF-{i:03}',titulo='Brakeman: '+w['warning_type'],descripcion=explanation,severidad='Baja' if kind.startswith('Hallazgo') else 'Media',prioridad='P4' if kind.startswith('Hallazgo') else 'P2',
              pasos='Ejecutar Brakeman con --no-threads yrevisar '+w['file']+':'+str(w['line']),esperado='Confirmar flujo real ycondiciones del hallazgo antes de clasificarlo como vulnerabilidad.',actual=w['message'],
              evidencia=str(source.relative_to(ROOT))+';'+('app/controllers/eliminacion_directa_controller.rb:172' if kind.startswith('Hallazgo') else 'https://rubyonrails.org/2025/10/29/new-rails-releases-and-end-of-support-announcement'),estado='Descartado como asignación masiva' if kind.startswith('Hallazgo') else 'Abierto',confirmacion=confirmation,tipo=kind,responsable=C if kind.startswith('Hallazgo') else J,caso='EST-001',requerimiento='RNF-03' if kind.startswith('Hallazgo') else 'RNF-01',caracteristica='Seguridad' if kind.startswith('Hallazgo') else 'Mantenibilidad',modulo='Controladores' if kind.startswith('Hallazgo') else 'Dependencias',archivo=w['file'],linea=w['line'],impacto=explanation,recomendacion='Conservar la revisión; priorizar validación de tipos' if kind.startswith('Hallazgo') else 'Planificar migración a una serie soportada en un trabajo posterior,con regresión ycontrol de cambios',costo_minutos='No estimado'))
    csvwrite(DOCS/'Hallazgos_Herramientas.csv',observations)
    for defect in defects:
        defect['evidencia']=';'.join(dict.fromkeys(item.strip() for item in defect['evidencia'].split(';') if item.strip()))
    csvwrite(DOCS/'Registro_Defectos.csv',defects)
    print('Automatic observations:',len(observations),'; groups:',len(groups),'; no automatic correction applied.')


if __name__=='__main__':main()
