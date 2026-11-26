"""Freeze test oracles and the quality model BEFORE executing the suite.

This command refuses to overwrite an existing design. Results live separately.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from paths import ROOT, APP_ROOT, DOCS, DATA
J = 'José Daniel Morera Elizondo'
V = 'Jimena Vindas Acosta'
C = 'César Gamboa Naranjo'
FUNCTIONAL = 'Adecuación funcional'


def csvwrite(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    if (DATA / 'design.json').exists():
        raise SystemExit('Design already frozen; use results import, not a redesign.')
    reqs = []
    texts = [
        ('Registrar selecciones con país, grupo, puntos y goles', V),
        ('Crear y administrar los doce grupos A a L', V),
        ('Registrar resultados de fase de grupos', J),
        ('Calcular posiciones por puntos, diferencia y goles a favor', J),
        ('Clasificar dos primeros por grupo y ocho mejores terceros', C),
        ('Gestionar eliminación desde dieciseisavos hasta final', C),
        ('Registrar resultados eliminatorios y penales', C),
        ('Avanzar automáticamente al ganador cuando se completa la ronda', C),
        ('Mostrar campeón, subcampeón y tercer lugar', C)]
    for i, (text, owner) in enumerate(texts, 1):
        reqs.append(dict(id=f'RF-{i:02}', original_id=str(i), tipo='Funcional', descripcion=text,
                         procedencia='Explícito', fuente=f'Proyecto_4_POO_Mundial_2026.md, Requerimientos del sistema, punto {i}',
                         seleccionado='Sí', responsable=owner, caracteristica=FUNCTIONAL,
                         criterio='Ver resultados esperados del catálogo congelado', prioridad='P1' if i >= 3 else 'P2'))
    nfs = [
        ('RNF-01','Código modular, comentado y estructurado; buenas prácticas POO y SOLID','Mantenibilidad',J,'Explícito','Consideraciones y aspectos técnicos, punto 2 y viñeta 3'),
        ('RNF-02','Interfaz comprensible y accesible WCAG 2.2 AA','Capacidad de interacción',V,'Derivado','Interfaz gráfica original; criterios ampliados de auditoría'),
        ('RNF-03','Proteger integridad de marcadores y evitar escritura no autorizada','Seguridad',C,'Derivado','Riesgo de modificación de información del torneo; política de acceso candidata a ratificación'),
        ('RNF-04','P95 <=1 s y errores <=1 % en consulta local con carga creciente','Eficiencia de desempeño',C,'Derivado','Criterios internos definidos antes de medir'),
        ('RNF-O1','Desarrollar en Ruby on Rails','Adecuación funcional',J,'Explícito','Consideraciones y aspectos técnicos, viñeta 1'),
        ('RNF-O2','Generar una interfaz gráfica','Capacidad de interacción',V,'Explícito','Consideraciones y aspectos técnicos, viñeta 2')]
    for rid, text, char, owner, origin, section in nfs:
        reqs.append(dict(id=rid,original_id='Sin identificador',tipo='No funcional',descripcion=text,
                         procedencia=origin,fuente='Proyecto_4_POO_Mundial_2026.md; '+section,
                         seleccionado='No' if rid.startswith('RNF-O') else 'Sí',responsable=owner,
                         caracteristica=char,criterio='Umbrales de las fichas MET-01 a MET-13',prioridad='P1' if rid=='RNF-03' else 'P2'))
    cases = []
    def add(cid, name, req, data, steps, expected, technique='Partición de equivalencia', char=FUNCTIONAL, kind='Funcional'):
        level = {'UT':'Unitaria','INT':'Integración','E2E':'Sistema','UAT':'Aceptación','PERF':'Sistema','SEG':'Integración','USA':'Sistema','ACC':'Sistema','EST':'Estática'}[cid.split('-')[0]]
        owner = next(x['responsable'] for x in reqs if x['id']==req.split(';')[0])
        prefix = cid.split('-')[0]
        files = {'UT':'test/unit/qa_unit_test.rb','INT':'test/integration/qa_integration_test.rb',
                 'SEG':'test/integration/qa_security_test.rb','E2E':'qa/e2e/mundial.spec.cjs',
                 'PERF':'qa/performance/load.js','ACC':'qa/accessibility/scan.cjs',
                 'USA':'qa/usability/protocolo.md','UAT':'qa/acceptance/protocolo.md','EST':'qa/scripts/static_review.py'}
        commands = {'UT':'bash qa/scripts/run_all.sh --only unit','INT':'bash qa/scripts/run_all.sh --only integration',
                    'SEG':'bash qa/scripts/run_all.sh --only security','E2E':'bash qa/scripts/run_all.sh --only e2e',
                    'PERF':'bash qa/scripts/run_all.sh --only performance --load','ACC':'bash qa/scripts/run_all.sh --only accessibility',
                    'EST':'bash qa/scripts/run_all.sh --only static','USA':'python qa/scripts/import_human.py qa/usability/resultados.csv',
                    'UAT':'python qa/scripts/import_human.py qa/acceptance/resultados.csv'}
        metrics = {'UT':'MET-02;MET-03','INT':'MET-02;MET-03','E2E':'MET-01;MET-02','UAT':'MET-02',
                   'SEG':'MET-07;MET-08','PERF':'MET-09;MET-10','USA':'MET-11;MET-12','ACC':'MET-13','EST':'MET-04;MET-05;MET-06'}
        cases.append(dict(id=cid,nombre=name,objetivo=name,requerimiento=req,tipo=kind,nivel=level,prioridad='P1' if prefix in ['INT','SEG'] else 'P2',
                          caracteristica=char,precondiciones='Datos sintéticos; componente aislado con dobles' if prefix=='UT' else 'Ambiente QA local aislado y datos sintéticos preparados; para actividades humanas, consentimiento anónimo',
                          datos=data,pasos=steps,esperado=expected,obtenido='Sin ejecución',estado='No ejecutado',evidencia='',responsable=owner,
                          tecnica=technique,postcondiciones='Sin cambios en datos ajenos a QA; restaurar transacción o dataset propio',
                          metrica=metrics[prefix],defecto='',implementacion=files[prefix],automatizada='No' if prefix in ['UAT','USA'] else 'Sí',
                          funcion='manual' if prefix in ['UAT','USA'] else 'test_'+cid.replace('-','_'),comando=commands[prefix],fecha='',ambiente='Windows; loopback; RAILS_ENV=test',version='789565ea61bae6a84cc8d9ae3be871f601f4a2d1'))
    unit = [
      ('Ganador local regular','RF-03','2-1, finalizado','CalcularGanadorPartido con doble','Retorna local'),
      ('Empate de grupos','RF-03','0-0, fase_grupos','CalcularGanadorPartido con doble','Retorna nil'),
      ('Victoria suma tres puntos','RF-04','doble selección; un partido 2-1','ActualizarEstadisticasSeleccion#calcular','3 puntos, GF2, GC1, DG1'),
      ('Empate suma un punto','RF-04','un partido 0-0','ActualizarEstadisticasSeleccion#calcular','1 punto; goles 0'),
      ('Derrota visitante no suma','RF-04','visitante pierde 1-2','ActualizarEstadisticasSeleccion#calcular','0 puntos; GF1 GC2'),
      ('Recalcular dos veces es idempotente','RF-04','un 2-1; cálculo repetido','ActualizarEstadisticasSeleccion#calcular dos veces','Mismo hash ambas veces'),
      ('Nombre legible de selección','RF-01','acronimo QAA, nombre Equipo QA, grupo A','Seleccion#to_s con atributos dobles','QAA - Equipo QA (Grupo A)'),
      ('Diferencia de goles','RF-01','GF7 GC3','Seleccion#calcular_diferencia_goles con dobles','DG=4'),
      ('Normalización de grupo','RF-02','letra: espacio a espacio','Grupo#normalizar_letra con dobles','A'),
      ('Grupo con cuatro equipos completo','RF-02','doble asociación con count4','Grupo#completo?','true'),
      ('Grupo con tres equipos tiene espacio','RF-02','doble asociación con count3','Grupo#tiene_espacio?','true'),
      ('Orden de posiciones delegado','RF-04','doble asociación captura reorder','Grupo#tabla_posiciones','Orden puntos,diferencia,goles DESC e id ASC'),
      ('Penales resuelven empate','RF-07','1-1, penales 5-4','CalcularGanadorPartido con doble','Retorna local'),
      ('Partido pendiente sin ganador','RF-07','programado, goles nil','CalcularGanadorPartido con doble','nil sin excepción'),
      ('Mejores terceros por puntos','RF-05','12 dobles con puntos0..11','DeterminarClasificados#mejores_terceros','8 equipos; primeros con puntos11..4'),
      ('Progreso de grupos en frontera','RF-05','36 partidos concluidos de72','DeterminarClasificados#progreso_fase_grupos','0.5'),
      ('Torneo incompleto sin podio','RF-09','campeon y subcampeon; tercero nil','Torneo#finalizado? con atributos dobles','false'),
      ('Torneo con tres lugares finalizado','RF-09','campeon1,subcampeon2,tercero3','Torneo#finalizado? con atributos dobles','true')]
    for i, values in enumerate(unit,1): add(f'UT-{i:03}',*values)
    integ = [
      ('Registrar marcador persiste y recalcula','RF-03','Partido QA 2-1','PATCH /partidos_grupo/:id/registrar_resultado','302; partido finalizado 2-1; local3 visitante0'),
      ('Editar resultado conserva consistencia','RF-03','Marcador2-1 cambiado a0-0','Invocar modelo real registrar_resultado! dos veces','1 punto por equipo; sin acumulación anterior'),
      ('Ruta alternativa no duplica puntos','RF-04','Partido QA2-1','PATCH /partidos/:id/registrar_resultado','Local3 GF2; visitante0 GC2'),
      ('Alta de selección por interfaz HTTP','RF-01','Equipo QA,QAA,grupoA','POST /selecciones y recargar registro','Una selección persistida con grupo y acrónimo'),
      ('Quinta selección rechazada','RF-01','grupo con4; candidato quinto','POST /selecciones y comparar conteo','422; ninguna alta; datos previos iguales'),
      ('Grupo válido y eliminación restringida','RF-02','grupoA con equipo','GET /grupos/:id; DELETE mismo grupo','200 con grupo; eliminación rechazada y equipo intacto'),
      ('Clasificación de 48 selecciones','RF-05','12 grupos de4 con 72 resultados','Servicio real DeterminarClasificados.obtener','12 primeros+12 segundos+8 terceros;32 distintos'),
      ('Avance automático entre rondas','RF-06;RF-08','16 partidos73..88 finalizados','SiguienteRonda#avanzar','8 partidos89..96; ganadores correctos; repetición no duplica'),
      ('Cierre persiste podio','RF-09;RF-07','partidos103y104 con cuatro equipos','Registrar finales; recargar Torneo','campeón y subcampeón de104; tercero de103; finalizado')]
    for i, values in enumerate(integ,1): add(f'INT-{i:03}',*values,technique='Caja gris; contrato HTTP o servicio y efecto persistido')
    e2e = [
      ('Consulta de selecciones','RF-01','dataset base;QAA','Abrir /; verificar fila Equipo QA A','Selección y grupo visibles'),
      ('Registro de selección','RF-01','Equipo UI,QAZ,grupoA libre','Completar formulario Nueva Seleccion y enviar','Fila Equipo UI después de recargar'),
      ('Consulta de grupo','RF-02','grupoA y equipos sintéticos','Abrir /grupos/:id','Detalles y equipos de A visibles'),
      ('Registro de marcador por calendario','RF-03','partido1 sin marcador;2-1','Abrir calendario; completar local2 visitante1; guardar; recargar','Marcador2-1 y3 puntos; campos de ambos equipos independientes'),
      ('Frontera de marcador negativo','RF-03','-1 y0','Intentar enviar formulario calendario; observar validez','Navegador o servidor rechaza; sin persistencia'),
      ('Consulta de tabla de posiciones','RF-04','un partido2-1 ya finalizado','Abrir calendario de grupoA','Ganador primero con3 puntos,GF2,GC1'),
      ('Bloqueo de avance prematuro','RF-05','72 partidos pendientes','Abrir /fase_eliminatoria','No genera eliminación; muestra advertencia o estado de progreso'),
      ('Guardar eliminatoria y generar octavos','RF-06;RF-07;RF-08','72 grupos completos;16 eliminatorios pendientes','Completar marcadores de dieciseisavos desde formulario; guardar','Navega sin error500; ocho octavos y aviso de avance'),
      ('Podio final en interfaz','RF-09','partidos103/104 finalizados','Abrir /campeones/podio','Nombres correctos en campeón,subcampeón,tercero')]
    for i, values in enumerate(e2e,1): add(f'E2E-{i:03}',*values,technique='Caja negra; recorrido del navegador')
    for i, values in enumerate([
      ('Registrar un resultado real de uso','RF-03','Partido QA1;2-1','P01..P03: localizar partido y registrar2-1','Marcador y posiciones coinciden tras volver a abrir'),
      ('Interpretar tabla y clasificación','RF-04;RF-05','grupoA finalizado','P01..P03: identificar líder y un clasificado explicando puntos','Respuestas correctas respecto al dataset'),
      ('Consultar avance y podio','RF-06;RF-09','dataset de cierre','P01..P03: localizar fase y podio','Identificar fase y tres lugares sin orientación del evaluador')],1): add(f'UAT-{i:03}',*values,technique='Validación con usuarios externos')
    for i, loads in enumerate(['5,10,20','25,50,100'],1):
        add(f'PERF-{i:03}','Consulta local con carga '+loads,'RNF-04',loads+' VU;30s calentamiento,60s/nivel,30s descenso,30s recuperación',
            'k6; GET / y /partidos_grupo/calendario; validar contenido; abortar error>10% tras30s',
            'Por ruta y nivel: P95<=1s y errores<=1%; máximo100VU',technique='Carga creciente basada en riesgo',char='Eficiencia de desempeño',kind='Rendimiento')
    security = [
      ('Consulta parametrizada ante SQLi','grupo_letra: A OR 1=1','GET /selecciones con filtro malicioso; comparar DB','Sin excepción SQL ni filas fuera del filtro ni cambios'),
      ('Salida de texto ante XSS','nombre: <script>window.qaXss=1</script>','Persistir dato sintético y GET /; inspeccionar HTML','Script escapado; ninguna etiqueta script del dato'),
      ('Acceso anónimo de escritura','sesión sin identidad;selecciónQA','POST /selecciones; comparar conteos','Rechazo de escritura anónima según criterio derivado; política pendiente de ratificación'),
      ('Protección CSRF efectiva','POST sin token; forgery_protection=true solo durante caso','Activar control original y POST; comparar DB','422 o excepción InvalidAuthenticityToken; sin cambios'),
      ('Errores sin datos internos','id inexistente','GET /grupos/999999999; comparar DB','Respuesta controlada o redirección; sin stacktrace ni cambios'),
      ('Entradas inválidas sin corrupción','goles abc y1','PATCH /partidos_grupo/:id/registrar_resultado','Rechazo del valor no numérico; marcador sin cambios')]
    for i,(name,data,steps,expected) in enumerate(security,1): add(f'SEG-{i:03}',name,'RNF-03',data,steps,expected,technique='Prueba dirigida local; caja gris',char='Seguridad',kind='Seguridad')
    add('USA-001','Éxito y tiempo de tres tareas con tres personas','RNF-02','P01..P03;T1=120s,T2=90s,T3=90s',
        'Ejecutar protocolo, cronometrar y registrar todos los intentos','100% tareas correctas; tiempos dentro de objetivo; fallos y abandonos incluidos',technique='Observación humana',char='Capacidad de interacción',kind='Usabilidad')
    for i,path in enumerate(['/partidos_grupo/calendario','/grupos/ID','/fase_eliminatoria'],1):
        add(f'ACC-{i:03}','Accesibilidad de '+path,'RNF-02',path,'axe WCAG2A/AA,21A/AA,22AA más teclado,zoom400%,reflujo,contraste y foco',
            'Ningún incumplimiento confirmado; no declarar conformidad completa sin revisión manual',technique='Automática y revisión manual',char='Capacidad de interacción',kind='Accesibilidad')
    add('EST-001','Revisión estática de código y especificación','RNF-01','Commit base; app/**/*.rb y vistas','RuboCop, Reek, Flay, Brakeman, duplicación y revisión trazable',
        'Complejidad<=10;duplicación<=3%;deuda<=5%;hallazgos registrados',technique='Análisis estático',char='Mantenibilidad',kind='Estática')
    chars = [FUNCTIONAL,'Mantenibilidad','Seguridad','Eficiencia de desempeño','Capacidad de interacción']
    gqm = []
    qs = [
      [('¿Qué RF tienen casos diseñados?','MET-01'),('¿Qué proporción funcional aprueba?','MET-02'),('¿Qué RF disponen de validación exitosa y evidencia?','MET-01;MET-02')],
      [('¿Cuánto código se ejercita?','MET-03'),('¿Qué métodos exceden complejidad o duplicación?','MET-04;MET-05'),('¿Cuál es el costo relativo de remediar?','MET-06')],
      [('¿Cuántas vulnerabilidades confirmadas hay por severidad?','MET-07'),('¿Qué controles aplicables funcionan?','MET-08'),('¿Qué riesgo queda sin verificación?','MET-07;MET-08')],
      [('¿Cuál es el P95 por escenario y nivel?','MET-09'),('¿Qué porcentaje de solicitudes falla?','MET-10'),('¿En qué nivel se incumplen los umbrales?','MET-09;MET-10')],
      [('¿Pueden completar las tareas?','MET-11'),('¿Cuánto tardan los intentos?','MET-12'),('¿Qué barreras WCAG se confirman?','MET-13')]]
    for i,char in enumerate(chars,1):
        related = [r['id'] for r in reqs if r['caracteristica']==char and r['seleccionado']=='Sí']
        goal = f'Analizar la aplicación Mundial POO con el propósito de evaluar su aptitud respecto a {char.lower()} desde el punto de vista del equipo auditor y las personas usuarias en el contexto del ambiente local aislado del curso IC-6831.'
        for j,(question,metric) in enumerate(qs[i-1],1):
            linked = [c['id'] for c in cases if set(c['metrica'].split(';')) & set(metric.split(';'))]
            gqm.append(dict(objetivo_id=f'GQM-{i:02}',objetivo=goal,pregunta_id=f'GQM-{i:02}-P{j}',pregunta=question,caracteristica=char,requerimientos=';'.join(related),metricas=metric,casos=';'.join(linked),evidencia='Reportes asociados a cada caso; actualizados por finalize'))
    metrics = []
    names = ['Cobertura de RF','Casos funcionales aprobados','Cobertura de código','Complejidad ciclomática','Código duplicado','Razón de deuda técnica','Vulnerabilidades por severidad','Seguridad aprobada','Tiempo P95','Errores bajo carga','Éxito de tareas','Tiempo de tareas','Incumplimientos WCAG']
    formulas = ['RF con caso / RF seleccionados ×100','Aprobados / funcionales concluyentes ×100','Líneas ejecutadas / ejecutables ×100','Decisiones independientes +1 por método; RuboCop Metrics/CyclomaticComplexity','Líneas únicas incluidas en bloques clonados / líneas analizables ×100','Minutos remediación / minutos desarrollo estimado ×100','Conteo confirmado por severidad; candidatos separados','Controles aprobados / controles concluyentes aplicables ×100','Percentil95 por ruta,escenario y carga','Errores inesperados / solicitudes ×100','Tareas correctas / intentos válidos ×100','Segundos por intento y razón tiempo/objetivo por tarea','Conteo de incumplimientos confirmados por pantalla y criterio']
    thresholds = [('100%','80..<100%','<80%'),('>=95%','80..<95%','<80%'),('>=80%','60..<80%','<60%'),('<=10','11..15','>15'),('<=3%','>3..5%','>5%'),('<=5%','>5..10%','>10%'),('0 altas/críticas','1 alta y0 críticas','>=1 crítica o>1 alta'),('100%','80..<100%','<80%'),('<=1s','>1..2s','>2s'),('<=1%','>1..5%','>5%'),('100%','80..<100%','<80%'),('<=objetivo','>objetivo..1.5×objetivo','>1.5×objetivo'),('0 confirmados','Solo no bloqueantes','>=1 bloqueante')]
    tools = ['Catálogo CSV','Resultados normalizados','SimpleCov','RuboCop','jscpd más unión de intervalos','Inventario de deuda; estimación explícita','Brakeman, Bundler Audit y controles dirigidos','Minitest Rails','k6','k6','Formularios reales','Cronómetro y formularios reales','axe-core más revisión manual']
    for i,name in enumerate(names,1):
        mid=f'MET-{i:02}'
        char=chars[0 if i<=2 else 1 if i<=6 else 2 if i<=8 else 3 if i<=10 else 4]
        questions=[x['pregunta_id'] for x in gqm if mid in x['metricas'].split(';')]
        metrics.append(dict(id=mid,nombre=name,caracteristica=char,objetivo='Responder '+ ';'.join(questions),preguntas=';'.join(questions),formula=formulas[i-1],variables='Numerador y denominador documentados en el resultado; desconocidos se conservan como null',unidad='segundos' if i in [9,12] else 'conteo' if i in [4,7,13] else '%',escala='Razón',herramienta=tools[i-1],metodo='Recoger reportes originales; normalizar sin omitir fallos, bloqueos o abandonos',frecuencia='En cada corrida y después de incorporar evidencia humana',justificacion='Informa directamente la decisión sobre '+char.lower(),umbral_general=thresholds[i-1][0],total=thresholds[i-1][0],parcial=thresholds[i-1][1],rechazo=thresholds[i-1][2],decision='Aceptar el criterio, condicionar o rechazar; si falta evidencia, no evaluado',responsable=J if char=='Mantenibilidad' or i<=2 else C if i<=10 else V,fuente='Reportes por corrida y formularios preservados',alcance='Código app/ de línea base y casos vinculados',exclusiones='Dependencias y código generado; no sustituir datos humanos',limitaciones='Umbrales internos; no prescritos por ISO. Texto íntegro de normas no consultado. No confundir diseño con ejecución.'))
    csvwrite(DOCS/'Inventario_Requerimientos.csv',reqs)
    csvwrite(DATA/'Casos_Diseno_Pre_Ejecucion.csv',cases)
    csvwrite(DOCS/'Casos_de_Prueba.csv',cases)
    csvwrite(DOCS/'GQM.csv',gqm)
    csvwrite(DOCS/'Fichas_Metricas.csv',metrics)
    design={'frozen_at':datetime.now(timezone(timedelta(hours=-6))).isoformat(),'requirements':reqs,'cases':cases,'gqm':gqm,'metrics':metrics}
    (DATA/'design.json').write_text(json.dumps(design,indent=2,ensure_ascii=False),encoding='utf-8')
    (DATA/'design.sha256').write_text(hashlib.sha256((DATA/'design.json').read_bytes()).hexdigest(),encoding='ascii')
    print('Frozen:',len(reqs),'requirements,',len(cases),'cases,',len(gqm),'questions,',len(metrics),'metrics')


if __name__=='__main__': main()
