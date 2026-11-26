"""Finish from existing evidence. Does not invent missing measurements."""
import hashlib,json,subprocess,sys
from datetime import datetime
from pathlib import Path
from design import ROOT,DOCS,J,V,C,csvwrite
from recalculate_metrics import recalculate,readcsv,human_data


def inventory(cases):
    records=[];seen=set()
    for case in cases:
        for source in case['evidencia'].split(';'):
            if not source:continue
            path=ROOT/source
            if not path.is_file() or source in seen:continue
            seen.add(source);records.append(dict(id=f'EV-{len(records)+1:03}',fecha=case['fecha'] or datetime.fromtimestamp(path.stat().st_mtime).isoformat(),herramienta=case['tipo']+' / '+case['nivel'],comando=case['comando'],ambiente=case['ambiente'],commit=case['version'],caso=';'.join(c['id'] for c in cases if source in c['evidencia'].split(';')),metrica=case['metrica'],responsable=case['responsable'],ruta=source,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for path in sorted((ROOT/'qa/reports/runs').glob('*/*.log')):
        source=str(path.relative_to(ROOT))
        if source not in seen:
            seen.add(source);records.append(dict(id=f'EV-{len(records)+1:03}',fecha=datetime.fromtimestamp(path.stat().st_mtime).isoformat(),herramienta=path.stem,comando='Véase run.json en el mismo directorio',ambiente='Windows;QA local',commit='789565ea61bae6a84cc8d9ae3be871f601f4a2d1',caso='',metrica='',responsable=J if path.stem in ['unit','rubocop','reek','flay','complexity','duplication'] else C,ruta=source,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    csvwrite(DOCS/'Inventario_Evidencias.csv',records)


def pending(cases):
    fig={'UT':12,'INT':13,'E2E':14,'PERF':15,'SEG':16,'ACC':17,'UAT':18,'USA':19}
    text='# Evidencias pendientes\n\nDirectorio para todos los comandos: QA-Proyecto/Entregables (desde el repositorio: `cd Entregables`). Terminal: Git Bash. Preparación: `source qa/scripts/env.sh`. Las actividades completadas se eliminan automáticamente de este registro al regenerar.\n'
    for owner in [J,V,C]:
        text+='\n## '+owner+'\n'
        for prefix in ['UT','INT','E2E','SEG','PERF','ACC','UAT','USA']:
            subset=[c for c in cases if c['responsable']==owner and c['id'].startswith(prefix+'-') and c['estado'] in ['Bloqueado','No ejecutado']]
            if not subset:continue
            sample=subset[0];figure=fig[prefix]
            text+=f"\n### EV-P-{prefix}-{owner.split()[0]} · Figura {figure}. Evidencia de {sample['tipo']} / {sample['nivel']}\n\n"
            text+='Casos: '+', '.join(c['id'] for c in subset)+'.\n\n'
            text+='Motivo: '+('requiere participantes externos reales y confirmación de la sesión.' if prefix in ['UAT','USA'] else 'la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.')+'\n\n'
            text+=f"Responsable: {owner}. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.\n\n"
            text+='Comando exacto:\n\n```bash\n'+sample['comando']+'\n```\n\n'
            if prefix in ['UAT','USA']:
                folder='acceptance' if prefix=='UAT' else 'usability'
                text+=f'Seguir qa/{folder}/protocolo.md; preparar los perfiles indicados y servidor `bash qa/scripts/start.sh base`; usar http://127.0.0.1:3100. Completar qa/{folder}/resultados.csv con fecha real,consentimiento,observación,estado,evidencia yconfirmado=true; importar con `python qa/scripts/import_human.py qa/{folder}/resultados.csv`. No registrar personas que no participaron.\n\n'
            elif prefix=='ACC':text+='Complementar axe con qa/accessibility/manual.md ymanual.csv; guardar capturas ACC-001_manual.png,ACC-002_manual.png,ACC-003_manual.png en qa/evidence; importar elCSV confirmado.\n\n'
            text+=f'Archivo gráfico alternativo: qa/evidence/Figura_{figure:03}.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.\n\n'
            text+='Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.\n'
        text+='\nConfirmar aporte individual y revisar los hallazgos asignados en Distribucion_Trabajo.md; no se acredita autoría ni sesión a partir de la asignación.\n'
    if 'inspection' not in human_data():
        text+='\n## Inspección formal del equipo · Figura20\n\nResponsables: los tres integrantes con rotación porautoría. Directorio Entregables; leer qa/static/Inspeccion_Formal.md. Preparar20min de revisión individual ysesión con moderador,revisor yescriba reales. Consultar autoría con `git -C .. log --format="%h %an" -- app/controllers/partidos_controller.rb app/models/partido.rb`; el autor no modera niregistra. Guardar acta auténtica en qa/evidence/Inspeccion_Formal_Acta.md; completar qa/static/inspeccion.json. Importar `python qa/scripts/import_human.py qa/static/inspeccion.json`; regenerar. Figura20 enanexos; sección11.3. No inventar asistentes,fechas,acuerdos nifirmas.\n'
    for number,title,path in [(21,'pantalla principal','/'),(22,'calendario','/partidos_grupo/calendario'),(23,'podio','/campeones/podio')]:
        basename={21:'pantalla_selecciones.png',22:'pantalla_calendario.png',23:'pantalla_podio.png'}[number]
        if not any((ROOT/'qa/reports/runs').glob('*/'+basename)) and not (ROOT/f'qa/evidence/Figura_{number:03}.png').exists():
            text+=f'\n## Figura{number}. {title}\n\nResponsable: '+(V if number==21 else J if number==22 else C)+f'. Preparar Ruby,dependencias ybaseQA; ejecutar `bash qa/scripts/start.sh '+('podium' if number==23 else 'base')+f'`. Abrir http://127.0.0.1:3100{path}; mostrar URL,pantalla completa ydatos EquipoQA. Guardar qa/evidence/Figura_{number:03}.png. Capítulos6.4,10.6 yanexos; regenerar con finalize_report.sh. La imagen se incorpora automáticamente si existe.\n'
    text+='\n## GitHub Actions · Figura24\n\nResponsable de automatización: José Daniel Morera Elizondo. Elworkflow local está en ../.github/workflows/qa.yml. La ejecución remota requiere que el equipo decida publicar la rama; no se hace push automáticamente. Después,abrir Actions→QA auditoría→Run workflow; guardar una captura auténtica qa/evidence/Figura_024_CI.png con nombre yresultado de la corrida. Regenerar. La configuración yla ejecución son evidencias distintas.\n'
    (DOCS/'PENDIENTES_EVIDENCIAS.md').write_text(text,encoding='utf-8')


def main():
    from polish_metadata import main as polish
    polish()
    from import_static_findings import main as import_static
    import_static()
    design,cases,metrics,summary,_=recalculate();inventory(cases);pending(cases)
    subprocess.run([sys.executable,'qa/scripts/visuals.py'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'qa/scripts/generate_report.py'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'qa/scripts/baseline.py'],cwd=ROOT,check=True,stdout=subprocess.PIPE)
    from verify_compliance import verify
    code,result=verify('--final' in sys.argv)
    (ROOT/'qa/reports/PROGRESO.json').write_text(json.dumps({'updated_at':datetime.now().isoformat(),'baseline':True,'design_frozen':True,'implemented_cases':summary['implemented'],'results':summary,'compliance':result,'human_activities_confirmed':list(human_data()),'original_logic_changes':0},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Report regenerated. '+('READY' if result['ready'] else 'NOT READY: evidence or mandatory activities remain.'))
    return code


if __name__=='__main__':raise SystemExit(main())
