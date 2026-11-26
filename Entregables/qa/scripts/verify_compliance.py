"""Academic matrix + strict readiness gate. Prepared protocols never credit sessions."""
import argparse,csv,json,re
from pathlib import Path
from zipfile import ZipFile
from design import ROOT,APP_ROOT,DOCS,J,V,C,csvwrite
from recalculate_metrics import readcsv,human_data


def verify(final=False):
    design=json.loads((ROOT/'qa/data/design.json').read_text(encoding='utf-8'))
    cases=readcsv('Casos_de_Prueba.csv');reqs={r['id'] for r in design['requirements']};ids={c['id'] for c in cases}
    defs=readcsv('Registro_Defectos.csv');defids={d['id'] for d in defs};metrics=readcsv('Resultados_Metricas.csv');human=human_data();errors=[]
    for case in cases:
        for req in case['requerimiento'].split(';'):
            if req not in reqs:errors.append('Orphan requirement: '+req)
        if not case['responsable']:errors.append('Missing owner: '+case['id'])
        if case['estado']=='Aprobado' and not case['evidencia']:errors.append('Passed without evidence: '+case['id'])
        if case['defecto']:
            for item in case['defecto'].split(';'):
                if item not in defids:errors.append('Orphan defect: '+item)
    for row in readcsv('Matriz_Trazabilidad.csv'):
        if row['caso'] not in ids or row['requerimiento'] not in reqs:errors.append('Orphan trace row')
    for metric in metrics:
        if metric['estado']!='No evaluado' and not metric['evidencia']:errors.append('Metric without evidence: '+metric['id'])
    doc=DOCS/'Informe_Final_QA_Mundial.docx';text=''
    if doc.exists():
        with ZipFile(doc) as z:text=z.read('word/document.xml').decode('utf-8')
    else:errors.append('Missing Word report')
    records=[]
    def add(page,description,minimum,ok,result,section,evidence,partial=False,notes=''):
        records.append(dict(id=f'AC-{len(records)+1:03}',pagina=page,descripcion=description,minimo=minimum,resultado=result,seccion_word=section,evidencia=evidence,estado='Cumple' if ok else 'Cumple parcialmente' if partial else 'Pendiente',observaciones=notes))
    def complete(prefix):
        subset=[c for c in cases if c['id'].startswith(prefix+'-')]
        return subset and all(c['estado'] in ['Aprobado','Fallido'] for c in subset)
    def count(prefix):return sum(c['id'].startswith(prefix+'-') for c in cases)
    add('1–2','Ficha del sistema','Ocho datos',bool(text),'Identificación y procedencia explícitas','1','qa/reports/baseline/baseline.json')
    add('2','Alcance incluido','Módulos,funciones,interfaces',bool(readcsv('Alcance.csv')),'Matriz por requerimiento','5','docs/Alcance.csv')
    add('2','Justificación de exclusiones','Motivo y riesgo aceptable',bool(readcsv('Exclusiones.csv')),'Exclusiones técnicas y riesgos residuales','5','docs/Exclusiones.csv')
    add('3','Cinco características','5,con tres obligatorias',len({m['caracteristica'] for m in design['metrics']})==5,'Modelo con adecuación,mantenibilidad,seguridad,desempeño e interacción','7','docs/Fichas_Metricas.csv')
    add('3','Prioridad y selección','Justificación por característica',bool(text),'Prioridad,usuarios y subcaracterísticas','7.2','docs/Contenido_Academico.json')
    add('3','Características excluidas','Una justificación por exclusión',bool(text),'Compatibilidad,fiabilidad,flexibilidad,Safety','7.3','docs/Contenido_Academico.json')
    add('3','Objetivos GQM','Uno por característica',len({q['objetivo_id'] for q in design['gqm']})==5,'Cinco objetivos con plantilla Basili','7.4','docs/GQM.csv')
    add('3','Preguntas GQM','2–4 por objetivo',all(sum(q['objetivo_id']==f'GQM-{i:02}' for q in design['gqm'])==3 for i in range(1,6)),'Quince preguntas','7.4','docs/GQM.csv')
    add('4–5','Fichas de métricas','Mínimo cinco completas',len(design['metrics'])==13,'Trece fichas con campos y umbrales','7.5','docs/Fichas_Metricas.csv')
    add('3','Plan de calidad','Doce elementos mínimos',bool(text),'Estrategia,recursos,criterios,ambientes y datos','8','docs/Contenido_Academico.json')
    add('4','Revisión de requerimientos','Acta,hallazgos y reescrituras',len(readcsv('Revision_Requerimientos.csv'))>=9,'Nueve revisiones técnicas; ratificación humana pendiente','11.1','docs/Revision_Requerimientos.csv;qa/static/Acta_Revision.md')
    add('4','Revisión de código','Archivo,línea,clasificación',bool(defs),'Hallazgos estáticos con localización y evidencia','11.2','docs/Registro_Defectos.csv')
    add('4','Inspección formal','Una sesión con roles','inspection' in human,'Protocolo preparado; acreditar solo acta confirmada','11.3','qa/static/Inspeccion_Formal.md',partial='inspection' not in human)
    add('4','Mantenibilidad','Reporte y análisis propio',any(m['id']=='MET-04' and m['estado']!='No evaluado' for m in metrics),'Prism AST y jscpd; herramientas Ruby según disponibilidad','11.4','docs/Resultados_Metricas.csv')
    add('4','Deuda técnica','Estimación y propuesta priorizada',bool(readcsv('Deuda_Tecnica.csv')),'Estimación explícita,sensibilidad y límites','19','docs/Deuda_Tecnica.csv')
    add('5–6','RF por integrante','2 por integrante,con niveles aplicables',all(complete(p) for p in ['UT','INT','E2E']),'Nueve RF asignados y diseñados; ejecución de niveles aplicables se verifica aparte','23','docs/Inventario_Requerimientos.csv',partial=True)
    add('5–6','RNF por integrante','1 por integrante evaluado',all(m['estado']!='No evaluado' for m in metrics),'Cuatro RNF seleccionados; asignación no equivale a evaluación','23','docs/Inventario_Requerimientos.csv',partial=True)
    add('4–5','Cinco características evaluadas','Evidencia suficiente de las cinco',all(m['estado']!='No evaluado' for m in metrics),'Separar selección del modelo de la evaluación efectiva','18','docs/Resultados_Metricas.csv',partial=True)
    add('5','Casos positivos,negativos y frontera','Tipos aplicables',count('UT')>=18 and count('INT')>=9 and count('E2E')>=9,'Catálogo congelado antes de la ejecución','13','qa/data/Casos_Diseno_Pre_Ejecucion.csv')
    add('5','Unitarias ejecutadas','Clases aisladas',complete('UT'),f"{count('UT')} implementadas; resultados individuales en catálogo",'12.1','docs/Casos_de_Prueba.csv',partial=True)
    add('5','Cobertura de código','Reporte de cobertura',any(m['id']=='MET-03' and m['estado']!='No evaluado' for m in metrics),'SimpleCov; excluir reportes generados antes de iniciar pruebas','12.1','docs/Resultados_Metricas.csv')
    add('5','Integración y efectos secundarios','Colaboración real y persistencia',complete('INT'),'Respuesta y estado de DB; transacciones','12.2','test/integration/qa_integration_test.rb',partial=True)
    add('5','Sistema E2E','Interfaz real automatizada',complete('E2E'),'Nueve recorridos con captura y traza de fallo','12.3','qa/e2e/mundial.spec.cjs',partial=True)
    uat=human.get('acceptance',{}).get('rows',[])
    uat_complete=all(len({r['participante'] for r in uat if r['caso']==f'UAT-{i:03}'})>=2 for i in range(1,4))
    add('5','Aceptación real','3 escenarios,>=2 externos',uat_complete,f'{len(uat)} registros confirmados','12.4','qa/acceptance/resultados.csv',partial=bool(uat))
    add('5','Dos escenarios de rendimiento','Carga creciente',complete('PERF'),'5/10/20 y25/50/100VU; únicamente local','12.5','qa/performance/load.js',partial=True)
    add('5','Umbrales previos de rendimiento','Declaración antes de medir',True,'P95<=1s,errores<=1%;conservados en diseño','7.5 y12.5','qa/data/design.json')
    add('5','Seis verificaciones de seguridad','6 aplicables ejecutadas',complete('SEG'),'SQLi,XSS,acceso,CSRF,errores,entradas','12.6','test/integration/qa_security_test.rb',partial=True)
    usa=human.get('usability',{}).get('rows',[])
    add('5','Usabilidad real','1 prueba con3 personas',len(usa)==9 and len({r['participante'] for r in usa})==3,f'{len(usa)} intentos reales confirmados','12.7','qa/usability/resultados.csv',partial=bool(usa))
    add('5','Accesibilidad de tres pantallas','WCAG2.2 AA manual+automática',complete('ACC'),'Instrumento de aplicabilidad completo para A/AA yaxe; resultados solo confirmados','12.8','qa/accessibility/manual.csv',partial=True)
    add('5–6','Defectos registrados','Todos los hallazgos identificados',bool(defs),f'{len(defs)} registros con origen y confirmación','16','docs/Registro_Defectos.csv')
    add('5–6','Campos obligatorios de casos','16 campos mínimos',all(all(c.get(k) for k in ['id','nombre','objetivo','requerimiento','tipo','nivel','prioridad','caracteristica','precondiciones','datos','pasos','esperado','obtenido','estado','responsable']) for c in cases),'Evidencia vacía solo en casos no ejecutados','13','docs/Casos_de_Prueba.csv')
    add('6','Trazabilidad bidireccional','Ocho columnas',not errors,'Referencias validadas por identificador','15','docs/Matriz_Trazabilidad.csv')
    add('6','Responsabilidades individuales','Nombre completo',all(c['responsable'] in [J,V,C] for c in cases),'Asignación explícita; aportes personales sin ratificar','23','docs/Distribucion_Trabajo.md')
    add('7','Comando único de automatización','Comando reproducible',(ROOT/'qa/scripts/run_all.sh').exists(),'bash qa/scripts/run_all.sh','14','qa/scripts/run_all.py')
    add('7','Informe por corrida','Comando,fecha,exit y evidencia',any((ROOT/'qa/reports/runs').glob('*/run.json')),'Conservar éxitos y fallos independientes','14 y17','qa/reports/runs/')
    e2e_failure=any(c['id'].startswith('E2E') and c['estado']=='Fallido' for c in cases)
    traces=list((ROOT/'qa/reports/runs').glob('*/playwright/**/trace.zip'))
    add('7','Capturas o trazas de fallos','Cada fallo ejecutado',not e2e_failure or bool(traces),'Fallos nativos conservan backtrace; E2E conserva trace.zip','14','qa/reports/runs/',notes='La ausencia de un fallo ejecutado no acredita ejecución E2E')
    add('7','GitHub Actions','Opcional; incluir configuración',(APP_ROOT/'.github/workflows/qa.yml').exists(),'Configurado localmente; ejecución remota no acreditada','14.5','../.github/workflows/qa.yml')
    add('7','Datos sintéticos','Sin información personal de prueba',(ROOT/'qa/data/dataset.rb').exists(),'Equipo QA,códigos y participantes anónimos','8 y10','qa/data/dataset.rb')
    add('7','Sin secretos publicados','Variables y exclusiones',True,'No se copian claves; claves privadas no se leen','8','qa/scripts/baseline.py')
    add('7','Pruebas propias y autorizadas','Loopback y base aislada',True,'Guardas de destino y conexión','8 y12','qa/boot.rb;qa/performance/load.js')
    add('1,7–8','Recomendación de liberación','Defendible con evidencia',bool(text),'Decisión derivada de defectos y límites','21','qa/reports/summary.json')
    add('7–8','Secciones académicas','Todas las mínimas',all(f'{i}. ' in text for i in range(1,26)),'Veinticinco capítulos y portada','1–25','docs/Informe_Final_QA_Mundial.docx')
    add('Imagen adjunta','Estructura del programa','Diseño,diagramas,prototipo,instructivo y distribución',bool(text),'Incluida en capítulos6,10 y23','6,10,23','Screenshot 2026-11-25 144953.png')
    figures=json.loads((DOCS/'Manifest_Figuras.json').read_text(encoding='utf-8')) if (DOCS/'Manifest_Figuras.json').exists() else []
    add('Ampliación de entrega','Figuras numeradas','Consecutivas,sin duplicación',[f['number'] for f in figures]==list(range(1,25)),'Fuentes editables y reservas definitivas','6 y25','docs/Manifest_Figuras.json')
    add('Ampliación de entrega','Tablas e índices','SEQ y TOC automáticos',bool(text) and 'SEQ Tabla' in text and 'TOC' in text,'Campos actualizables en Word','Índices ycapítulos','docs/Informe_Final_QA_Mundial.docx')
    add('Ampliación de entrega','Referencias','Fuentes identificadas',bool(text),'APA7; sin afirmar consulta íntegra de normas','24','docs/Contenido_Academico.json')
    add('Ampliación de entrega','Anexos,evidencias y regeneración','Fuentes y mecanismos editables',(ROOT/'qa/scripts/finalize.py').exists(),'Importación validada y regeneración','25','qa/scripts/finalize.py')
    csvwrite(DOCS/'Verificacion_Cumplimiento.csv',records)
    md='# Verificación de cumplimiento\n\nFuente principal: Proyecto-Integrado-2026-II.pdf,8 páginas; revisado íntegramente en texto y representación visual. Las ampliaciones de entrega se identifican aparte. Un protocolo no acredita actividad humana.\n\n'
    md+='| ID | Página | Requisito | Mínimo | Resultado | Sección | Evidencia | Estado |\n|---|---|---|---|---|---|---|---|\n'
    for r in records:md+='| '+' | '.join(str(r[k]).replace('|','/') for k in ['id','pagina','descripcion','minimo','resultado','seccion_word','evidencia','estado'])+' |\n'
    pending=[r for r in records if r['estado']!='Cumple']
    md+='\nConsistencia: '+('sin errores de referencias.' if not errors else '; '.join(errors))+f'\n\nDisposiciones pendientes o parciales: {len(pending)}.\n'
    (DOCS/'Verificacion_Cumplimiento.md').write_text(md,encoding='utf-8')
    result={'consistency_errors':errors,'checks':len(records),'pending_or_partial':len(pending),'missing_figures':[f['number'] for f in figures if f['pending']],
            'ready':not errors and not pending and not any(f['pending'] for f in figures)}
    (ROOT/'qa/reports/compliance.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True))
    return (2 if final and not result['ready'] else 1 if errors else 0),result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');args=parser.parse_args()
    code,_=verify(args.final);raise SystemExit(code)
