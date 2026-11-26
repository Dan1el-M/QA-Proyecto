"""Create editable operational instruments without fabricating participation."""
import json
from pathlib import Path
from design import ROOT,DOCS,J,V,C,csvwrite


def write(path,text):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():path.write_text(text,encoding='utf-8')


def main():
    design=json.loads((ROOT/'qa/data/design.json').read_text(encoding='utf-8'))
    write('qa/acceptance/protocolo.md',f'''# Protocolo de aceptación

Responsable de coordinación: {V}. Los responsables funcionales atienden las incidencias de sus RF. No hay sesiones registradas hasta importar formularios reales.

## Preparación
1. Desde QA-Proyecto/Entregables (primero `cd Entregables`), en Git Bash: `source qa/scripts/env.sh` y `bundle install`.
2. Terminal de servidor: `bash qa/scripts/start.sh base`. Abrir http://127.0.0.1:3100. Verificar que los datos dicen Equipo QA y que DATABASE_URL termina en qa/data/qa.sqlite3.
3. Explicar propósito, participación voluntaria y uso anónimo de resultados. Obtener consentimiento sin nombre ni firma en el repositorio. Registrar P01, P02 o P03 y external=true. Confirmar que no pertenecen al equipo.
4. Antes de cada persona restaurar el perfil apropiado, con el navegador sin solicitudes activas: `ruby qa/scripts/prepare.rb base` para UAT-001; `finished` para UAT-002; `podium` para UAT-003.
5. No facilitar la solución. Leer: «Queremos comprobar si esta aplicación permite completar actividades del torneo. Puede expresar dudas o detenerse; evaluamos el sistema. Sus resultados se identificarán mediante un código anónimo».

## UAT-001: registrar un resultado
Perfil: persona organizadora sin conocimientos de programación. Necesidad: conservar un marcador y consultar sus efectos. Estado: base. Dato entregado: primer partido del grupo A termina2-1.
Instrucción: «Localice el primer partido del grupo A, registre2-1 y vuelva a consultar el marcador y la tabla».
Aceptación: ambos marcadores coinciden después de recargar; local recibe3 puntos,GF2,GC1 y visitante0 puntos. Si falta un campo o la escritura es incorrecta, registrar Fallido y la incidencia; no dar por aceptada una operación parcialmente guardada.

## UAT-002: consultar posiciones y clasificados
Perfil: persona espectadora. Necesidad: reconocer la situación competitiva. Estado: finished. Instrucción: «Indique cuál equipo lidera el grupo A y explique qué dos equipos clasifican directamente. Localice un tercer lugar clasificado».
Aceptación: coincide con el orden de los datos almacenados y los32 clasificados; registrar la explicación observada. Un error del sistema que impida acceder es Fallido, no una respuesta inventada del participante.

## UAT-003: consultar avance y podio
Perfil: persona organizadora o espectadora. Estado: podium. Instrucción: «Identifique la etapa actual y encuentre campeón, subcampeón y tercer lugar».
Aceptación: aparecen Equipo QA A1, A2 y A3 en los lugares correspondientes a partidos104 y103; registrar diferencias y barreras.

## Registro y análisis
Completar qa/acceptance/resultados.csv: participante,caso,external,consentimiento,fecha_real,estado,observacion,decision,evidencia,confirmado. Estado solo Aprobado o Fallido; no llenar las filas de quienes no participaron. Evidencias como qa/evidence/UAT_P01_UAT-001.png, sin caras ni información personal.
Por escenario, registrar decisiones individuales y aprobar globalmente solo cuando todas las ejecuciones requeridas sean satisfactorias. El mínimo académico es tres escenarios con al menos dos personas externas; se planifican tres. Guardar incidencias aunque repitan un defecto existente.
Incorporación: `python qa/scripts/import_human.py qa/acceptance/resultados.csv`; luego `bash qa/scripts/finalize_report.sh`.
''')
    write('qa/usability/protocolo.md',f'''# Prueba de usabilidad

Coordinación: {V}. Muestra prevista: tres personas externas P01,P02,P03; no se simulan intentos. Esta evaluación se registra aparte de aceptación aunque compartan personas.

Preparar el entorno y consentimiento según qa/acceptance/protocolo.md. Utilizar un navegador limpio y la misma pantalla/zoom inicial para todas las personas. Iniciar cronómetro al terminar de leer la tarea y detenerlo al cumplir el objetivo, declarar abandono o alcanzar240s. No corregir ni orientar; registrar toda ayuda solicitada. Si la aplicación se bloquea, detener el intento como Fallido y conservar su tiempo.

| Tarea | Estado inicial e instrucción | Éxito observable | Objetivo previo |
|---|---|---|---|
| T1 | base; localizar el primer partido A y registrar2-1 | marcador correcto persistido y3 puntos al ganador |120s: localizar,editar y comprobar |
| T2 | finished; abrir tablaA e indicar líder,puntos y diferencia | tres datos coinciden con tabla y dataset |90s: consulta e interpretación |
| T3 | podium; localizar final y tres puestos | identificar campeón,subcampeón y tercero correctos |90s: navegación y consulta |

Restaurar datos antes de cada tarea con `ruby qa/scripts/prepare.rb base`, `finished` o `podium`. La interfaz inicial es http://127.0.0.1:3100. Los errores observables son navegación equivocada, intento de enviar datos inválidos, lectura incorrecta y fallo de persistencia. A240s o a petición de la persona se registra Abandonado. No retirar del denominador los fallos ni los abandonos.

Completar qa/usability/resultados.csv: participante,tarea,external,consentimiento,fecha_real,estado,segundos,errores,ayuda,dudas,observacion,satisfaccion,evidencia,confirmado. La escala de satisfacción propia va1=muy difícil a5=muy fácil; es descriptiva y no se denomina SUS. Valores faltantes quedan vacíos.

Tras cada tarea preguntar: «¿Qué le resultó confuso?» y «¿Qué tan fácil fue de1a5?». Registrar literalmente solo observaciones pertinentes y anónimas. Capturas sin rostros ni datos personales con nombres USA_P01_T1.png,etc. Importar `python qa/scripts/import_human.py qa/usability/resultados.csv` y ejecutar `bash qa/scripts/finalize_report.sh`.

MET-11 se calcula con nueve intentos válidos de tres personas: correctos/intentos×100. MET-12 conserva tiempos individuales,media,mediana,mínimo,máximo y razones respecto al objetivo; el peor intento determina el criterio global,con desglose por tarea. Los límites internos son1× y1.5×. No declarar representatividad poblacional con esta muestra.
''')
    acceptance=[];usability=[]
    for person in ['P01','P02','P03']:
        for i in range(1,4):
            acceptance.append(dict(participante=person,caso=f'UAT-{i:03}',external='',consentimiento='',fecha_real='',estado='',observacion='',decision='',evidencia='',confirmado=''))
            usability.append(dict(participante=person,tarea=f'T{i}',external='',consentimiento='',fecha_real='',estado='',segundos='',errores='',ayuda='',dudas='',observacion='',satisfaccion='',evidencia='',confirmado=''))
    for file,rows in [('qa/acceptance/resultados.csv',acceptance),('qa/usability/resultados.csv',usability)]:
        if not (ROOT/file).exists():csvwrite(ROOT/file,rows)
    criteria=[('1.1.1','A','Alternativas de imágenes e iconos'),('1.3.1','A','Etiquetas,estructura y encabezados de tablas'),('1.4.1','A','Información no exclusiva del color'),('1.4.3','AA','Contraste4.5:1 texto normal,3:1 texto grande'),('1.4.4','AA','Ampliación200%'),('1.4.10','AA','Reflujo a320CSSpx o400% sin doble desplazamiento'),('2.1.1','A','Completar funciones solo con Tab,ShiftTab,Enter,Espacio y flechas'),('2.4.3','A','Orden lógico y retorno de foco al cerrar modal'),('2.4.7','AA','Foco visible'),('2.4.11','AA','Foco no totalmente oculto'),('3.3.1','A','Error identificado y comprensible'),('4.1.2','A','Nombre,función y estado accesibles')]
    rows=[dict(pantalla=f'ACC-{s:03}',criterio=k,nivel=l,procedimiento=p,estado='',evidencia='',observacion='',bloqueante='',confirmado='') for s in range(1,4) for k,l,p in criteria]
    if not (ROOT/'qa/accessibility/manual.csv').exists():csvwrite(ROOT/'qa/accessibility/manual.csv',rows)
    write('qa/accessibility/manual.md','''# Verificación manual WCAG2.2 AA

Abrir tres pantallas reales: calendario,detalle de grupoA y fase eliminatoria; preparar perfil knockout y servidor de qa/scripts/start.sh. Usar manual.csv para registrar las36 verificaciones; una evaluación automática no las sustituye. Utilizar teclado sin ratón,zoom200% y400%,ancho320CSSpx; comprobar etiquetas con árbol de accesibilidad del navegador,encabezados y relaciones de tablas,errores y nombres de botones. Medir colores efectivos con herramienta de contraste; documentar pares RGB y razón. Verificar cada criterio de la lista en todas las pantallas; si no aplica,explicar el elemento ausente. Un fallo bloqueante impide completar una operación esencial con la modalidad evaluada; severidad no equivale automáticamente al nivel WCAG.

Guardar ACC-001_manual.png,ACC-002_manual.png,ACC-003_manual.png en qa/evidence. En manual.csv,estado=Aprobado/Fallido/No aplica,confirmado=true,bloqueante=true/false,observación y evidencia. Importar `python qa/scripts/import_human.py qa/accessibility/manual.csv`; finalizar el informe. Mantener criterios no evaluados visibles y no emitir conformidad total por ausencia de hallazgos de axe.
''')
    write('qa/static/Inspeccion_Formal.md',f'''# Inspección formal pendiente

Objetivo: verificar integridad del registro de resultados y separación de responsabilidades. Artefactos: app/controllers/partidos_controller.rb,app/models/partido.rb y app/services/actualizar_estadisticas_seleccion.rb del commit789565e.

Antes de asignar roles, consultar `git -C .. log --format="%h %an" -- app/controllers/partidos_controller.rb app/models/partido.rb`. Identificar al autor histórico sin modificar contribuidores. Propuesta inicial: moderador {J}; revisor {C}; escriba {V}. Si el moderador o escriba es autor del artefacto,rotar dichos roles hacia personas que no lo sean. El autor explica y no modera ni registra su propia inspección. Documentar la rotación real.

Agenda propuesta: preparación individual20min,apertura5min,lectura estructurada20min,clasificación10min y seguimiento5min. Son duraciones previstas, no una reunión celebrada. Lista de cotejo: contrato3/1/0 puntos; un único recálculo; transacciones; entradas inválidas; aislamiento entre fases; conservación tras errores; rutas y vistas; claridad de responsabilidades; complejidad y duplicación. Hallazgos preliminares: consultar DEF-001..DEF-012; no aceptarlos sin revisión.

Completar qa/static/inspeccion.json con fecha_real,roles_reales,autor_artefacto,confirmado,decision_por_hallazgo,evidencias y acciones. No incluir firmas ficticias. Guardar acta real como qa/evidence/Inspeccion_Formal_Acta.md. Importar el JSON y regenerar. El registro de la revisión técnica automática no acredita esta reunión.
''')
    write('qa/static/inspeccion.json',json.dumps({'fecha_real':None,'roles_reales':{},'autor_artefacto':None,'confirmado':False,'decision_por_hallazgo':[],'evidencias':[],'acciones':[]},ensure_ascii=False,indent=2))
    risks=[]
    for i,(title,cause,effect,p,impact,req,owner,control,treat) in enumerate([
      ('Corrupción de marcador','Campos duplicados y conversiones implícitas','Clasificación incorrecta',5,5,'RF-03',J,'Validaciones numéricas en modelo','Reproducir por UI y HTTP; condicionar liberación'),
      ('Doble cómputo de estadísticas','Callback y suma en controlador','Puntos y goles inflados',4,5,'RF-04',J,'Servicio de recálculo','Comparar DB con oráculo y revisar rutas alternativas'),
      ('Bloqueo de fases','Vistas faltantes y mensaje nil','No completar torneo',5,4,'RF-06',C,'Servicios de fases','Ejecutar recorridos completos; mantener defectos abiertos'),
      ('Escritura anónima','Sin roles observados','Cambios no autorizados si se comparte instancia',4,4,'RNF-03',C,'CSRF en ejecución del navegador','Ratificar política; prueba dirigida; limitar exposición a loopback'),
      ('Divulgación de archivo local','Ruta de bandera sin confinamiento','Lectura de archivos accesibles al proceso',3,5,'RNF-03',C,'Comprobación de existencia','Confirmar con archivo sintético; registrar candidato'),
      ('Saturación bajo concurrencia','SQLite y consultas repetidas','Latencia y fallos de consulta',3,4,'RNF-04',C,'Pool y timeoutSQLite','Carga escalonada local; abortar errores persistentes'),
      ('Barreras de interacción','Idioma,etiquetas,modal y foco sin verificar','Personas excluidas del flujo',4,4,'RNF-02',V,'Formularios HTML','axe y revisión manual; prueba con tres personas'),
      ('Regresión costosa','Lógica extensa y duplicada; sin suite previa','Corrección introduce nuevos fallos',4,4,'RNF-01',J,'Service Objects','Medir cobertura y deuda; priorizar regresión'),
      ('Oráculos ambiguos','Desempate y condiciones de avance incompletos','Falsos criterios de aceptación',4,3,'RF-05',C,'Especificación enumerada','Ratificar propuestas de requerimientos antes de UAT')],1):
        score=p*impact
        risks.append(dict(id=f'RSK-{i:03}',descripcion=title,causa=cause,consecuencia=effect,probabilidad=p,impacto=impact,exposicion=score,nivel='Crítico' if score>=16 else 'Alto' if score>=10 else 'Medio' if score>=5 else 'Bajo',controles=control,tratamiento=treat,requerimiento=req,pruebas=';'.join(c['id'] for c in design['cases'] if req in c['requerimiento'].split(';')),responsable=owner,residual='No recalculado: no se implementaron correcciones; permanece la exposición inicial'))
    csvwrite(DOCS/'Matriz_Riesgos.csv',risks)
    scope=[]
    for r in design['requirements']:
        if r['seleccionado']=='Sí':scope.append(dict(modulo=r['descripcion'],funcionalidad=r['descripcion'],requerimiento=r['id'],riesgo=';'.join(x['id'] for x in risks if x['requerimiento']==r['id']) or 'Dependencia de flujo crítico',justificacion='Parte del proceso del torneo o calidad exigida',responsable=r['responsable'],nivel=';'.join(sorted({c['nivel'] for c in design['cases'] if r['id'] in c['requerimiento'].split(';')})),tipo=';'.join(sorted({c['tipo'] for c in design['cases'] if r['id'] in c['requerimiento'].split(';')}))))
    csvwrite(DOCS/'Alcance.csv',scope)
    csvwrite(DOCS/'Exclusiones.csv',[
      dict(elemento='Infraestructura pública y despliegue de producción',motivo='No existe ambiente de producción autorizado',riesgo_residual='Configuración de hosting sin evaluar',impacto='No extrapolar seguridad o capacidad del equipo local',aceptacion='El objeto es la versión local; no se recomienda producción sin revisión propia'),
      dict(elemento='CDN de estilos,Google Fonts y servicios de terceros',motivo='No son sistemas propios; las cargas y escaneos están restringidos a loopback',riesgo_residual='Disponibilidad y presentación dependientes de red',impacto='La presentación puede variar sin conectividad',aceptacion='Evaluar dependencia por inspección; no ejecutar ataques ni carga externa'),
      dict(elemento='Contraseñas y roles existentes',motivo='No se encontraron modelos de identidad ni login',riesgo_residual='Escritura abierta en instancia compartida',impacto='La falta de autenticación requiere decisión de producto',aceptacion='No se añade identidad; SEG-003 prueba el criterio de seguridad derivado'),
      dict(elemento='Conformidad completa de navegadores e infraestructura',motivo='La muestra E2E es Chromium local y no existe contrato de interoperabilidad',riesgo_residual='Diferencias en otros navegadores',impacto='No generalizar la compatibilidad',aceptacion='Se prioriza integridad; integración e instalación permanecen incluidas')])
    write('docs/Distribucion_Trabajo.md',f'''# Distribución de responsabilidades

| Integrante | RF | RNF | Especialidad y entregables |
|---|---|---|---|
| {J} |RF-03,RF-04|RNF-01|Mantenibilidad,automatización,cobertura,casos propios y reporte |
| {V} |RF-01,RF-02|RNF-02|Validación funcional,aceptación,usabilidad y accesibilidad |
| {C} |RF-05,RF-06,RF-07,RF-08,RF-09|RNF-03,RNF-04|Seguridad,desempeño,persistencia,integración y fases |

Se ampliaron los seis RF mínimos a los nueve RF originales para cubrir penales,avance y podio. Las etiquetas de responsable indican asignación y custodia de evidencia; no prueban ejecución personal. La confirmación del aporte real y la inspección formal se incorporarán con actas auténticas. Cada integrante revisará sus casos de los niveles aplicables. No se atribuyen reuniones ni horas trabajadas.
''')
    write('docs/Discrepancias_y_Fuentes.md','''# Control de fuentes y discrepancias

Fuente principal: Proyecto-Integrado-2026-II.pdf,8 páginas, localizado en Entregables/Proyecto-Integrado-2026-II.pdf; extracción íntegra y representación visual en qa/reports/sources. Imagen académica: Screenshot 2026-11-25 144953.png en Entregables, revisada directamente. La imagen exige portada,tabla de contenidos,introducción,problema,diseño,diagramas,prototipo,instalación,instructivo,conclusiones,distribución y referencias; se incluyen esas secciones.

La asignación inicial de18UT,9INT,9E2E,13métricas yGitHubActions es una ampliación interna: el enunciado no fija esas cantidades y considera CI opcional. Se conservan las ampliaciones compatibles. MET-01 mide cobertura de diseño y se reporta aparte la evidencia aprobada,como exige distinguir el enunciado.

La tabla académica de25010,página2,ubica «capacidad de ser probado» en Flexibilidad. La nomenclatura normativa completa no se pudo contrastar contra texto íntegro de pago; no se atribuye esa clasificación como cita directa de ISO. El informe conserva los cinco ejes y aplica los criterios de la consigna; prueba de instalación y testabilidad no se omiten.

La fecha administrativa de2025 del documento original dePOO no se usa como fecha de entrega del curso QA2026. El README nombra servicios y rutas que difieren del código. El curso de origen es Programación Orientada a Objetos; no se verificó la nómina completa del equipo original.

Materiales encontrados: Apuntes_4.6_Ejercicios_de_Pruebas_estaticas.pdf; Apuntes_04_Metricas_-_calidad_de_software_(v2)_[Repaired].pdf; Apuntes_7.0_Laboratorio_pruebas_de_Integracion.pdf; Laboratorio de pruebas de integración.pdf; Ejercicio_de_pruebas_sistema_23_Oct.xlsx. Se utilizan como referencias metodológicas sin importar obligaciones particulares. No se localizaron bajo los nombres solicitados el programa completo,06-Pruebas-dinamicas_2,11.Clase_QA_Herramientas_y_Certificaciones,00.Contexto ni01.Calidad. No se inventa su contenido.
''')
    print('Human protocols, risk and scope matrices created; blank forms remain unexecuted.')


if __name__=='__main__':main()
