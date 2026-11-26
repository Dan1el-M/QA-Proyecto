"""Clarify notation and labels without changing frozen oracles or thresholds."""
import json,re
from design import ROOT,DOCS,J,V,C,csvwrite
from recalculate_metrics import readcsv


def main():
    definitions=[
      'Rd: número de RF seleccionados con al menos un caso diseñado. R: total de RF seleccionados. Se calcula100×Rd/R; los RF con evidencia aprobada se informan aparte.',
      'P: casos funcionales aprobados. E: casos funcionales con resultado Aprobado o Fallido. D: casos funcionales diseñados. Aprobación100×P/E; avance100×E/D; bloqueados yno ejecutados separados.',
      'LH: líneas ejecutables de app con contador de cobertura mayor que0. LE: líneas de app con contador no nulo. Cobertura100×LH/LE; unión de contadores del mismo commit por archivo ylínea.',
      'CCm:1 más decisiones del AST del método m,con la convención declarada en complexity.json. N:número de métodos. Promedio:sum(CCm)/N; máximo:max(CCm); distribución por bandas10 y15.',
      'LD: cantidad de pares(archivo,línea)únicos dentro de bloques clonados. LA: líneas analizables informadas por jscpd. Porcentaje100×LD/LA; se unen intervalos superpuestos para no duplicar el numerador.',
      'TR:minutos de remediación estimados para los12 hallazgos manuales inventariados. LOC:líneas Ruby de app no vacías nicomentarios. TD=2min/LOC×LOC. Razón100×TR/TD. Candidatos sin estimación excluidos ydeclarados.',
      'Vs:número de vulnerabilidades verificadas de severidad s,con s=crítica,alta,media,baja. Ks:candidatos pendientes. Se mantienen separados; una coincidencia de versión no demuestra explotación.',
      'SP:verificaciones de seguridad aplicables aprobadas. SE:verificaciones aplicables con resultado concluyente. Porcentaje100×SP/SE. Bloqueos,no aplicabilidad ypendientes fuera del denominador yreportados.',
      'n:solicitudes observadas por escenario,ruta ynivel estable. T(i):duración ordenada de la solicitud i. P95=T(ceil(0.95×n)); milisegundos de k6 convertidos a segundos. No incluir calentamiento nitransición.',
      'E:solicitudes con error de transporte,HTTP inesperado ofallo del contenido esperado; cada solicitud cuenta como máximo una vez. N:solicitudes del mismo escenario,ruta ynivel. Tasa100×E/N; causas desglosadas en reportes.',
      'TC:tareas completadas correctamente por personas reales. IV:intentos válidos confirmados,incluidos fallidos yabandonados. Éxito100×TC/IV; se requieren tres personas ylos intentos previstos.',
      'ti:segundos observados del intento i,incluso fallo oabandono. oi:objetivo previo120s paraT1 y90s paraT2/T3. ri=ti/oi. Se conservan tiempos individuales,media,mediana,mínimo ymáximo por tarea; la peor razón determina el criterio global.',
      'NC:número de pares(pantalla,criterio)con incumplimiento confirmado; los elementos afectados se describen en observaciones,sin duplicar pares. B:al menos una barrera bloqueante. Hallazgos automáticos sin ratificar ycriterios no evaluados ono aplicables se informan aparte.'
    ]
    sheets=readcsv('Fichas_Metricas.csv')
    for i,row in enumerate(sheets):row['variables']=definitions[i]
    # Record the actual alternative implementation; the frozen mathematical
    # criterion (one plus decisions) and its thresholds remain unchanged.
    sheets[3]['herramienta']='Prism AST (medición alternativa); RuboCop como análisis complementario'
    sheets[3]['formula']='1 + decisiones por método, según la convención AST documentada en complexity.json'
    sheets[3]['limitaciones']='Medición alternativa mediante Prism AST; no se declara equivalencia exacta con el cop de RuboCop ni complejidad cognitiva. Convención y ubicaciones conservadas en el reporte. Umbrales internos, no prescritos por ISO.'
    reasons=[
      'Detecta obligaciones sin diseño de prueba; una alta aprobación no revela los RF omitidos.',
      'Resume la corrección observada de los casos concluyentes; el avance separado impide ocultar una ejecución incompleta.',
      'Localiza regiones sin ejercicio desde una línea base sin suite; no se interpreta como ausencia de defectos.',
      'Identifica métodos con mayor cantidad de decisiones para orientar revisión yregresión,conservando outliers yubicaciones.',
      'Cuantifica superficie duplicada que exigiría cambios coordinados; el número de clones ola masa de Flay no representan un porcentaje de líneas.',
      'Relaciona el esfuerzo previsto de remediación con el tamaño considerado; traduce el inventario a una prioridad económica con supuestos explícitos.',
      'Distingue impacto de hallazgos verificados ycandidatos; un conteo total simple confundiría convenciones de estilo con vulnerabilidades.',
      'Verifica controles concretos ysu alcance ejecutado; evita atribuir un puntaje global de seguridad a una herramienta aislada.',
      'Observa la cola de latencia por ruta ycarga; el promedio puede ocultar respuestas lentas que afectan a personas usuarias.',
      'Complementa la latencia: responder rápido con errores no satisface el proceso de consulta.',
      'Mide que personas reales consigan su objetivo; una inspección automática de interfaz no sustituye el éxito de tarea.',
      'Compara duración con objetivos propios de tareas de distinta complejidad yconserva fallos yabandonos,además de promedios.',
      'Relaciona barreras confirmadas con criterios verificables ypantallas; una puntuación automática de rendimiento no mide conformidad WCAG.'
    ]
    for i,row in enumerate(sheets):row['justificacion']=reasons[i]
    sheets[11]['unidad']='Segundos por intento yrazón adimensional tiempo/objetivo'
    csvwrite(DOCS/'Fichas_Metricas.csv',sheets)
    content=json.loads((DOCS/'Contenido_Academico.json').read_text(encoding='utf-8'))
    for i,text in enumerate(content['references']):
        text=text.replace('Basili,V.R.(1992).','Basili, V. R. (1992).').replace('Standardization.(','Standardization. (').replace('Ruby on Rails.(','Ruby on Rails. (').replace('Consortium.(','Consortium. (').replace('.(2026).','. (2026).').replace('(s.f.)','(s. f.)').replace('25010:2023:','25010:2023: ').replace('25023:2016:','25023:2016: ').replace('29148:2018:','29148:2018: ')
        if text.startswith('Proyecto Mundial-POO.') and 'Proyecto4' in text:
            text='Proyecto 4 de POO: Sistema de gestión de la Copa Mundial FIFA 2026. (s. f.). [Especificación incluida en el repositorio, commit789565e; autoría no identificada en el documento].'
        elif text.startswith('Proyecto Mundial-POO.'):
            text='Arquitectura del proyecto Ruby on Rails; Guía: Sistema de cálculo de tablas de posiciones; Mundial-POO(README). (s. f.). [Documentación original del repositorio, commit789565e; autoría no identificada en los documentos].'
        text=text.replace('Ruby.(','Ruby. (').replace('Versión7.1','Versión 7.1').replace('paradigm(','paradigm (').replace('applications(','applications (').replace('Quality Guidelines(','Quality Guidelines (')
        text=re.sub(r'[ \t]{2,}',' ',text)
        content['references'][i]=text
    eol_url='https://rubyonrails.org/2025/10/29/new-rails-releases-and-end-of-support-announcement'
    content['references']=[text for text in content['references'] if eol_url not in text]
    content['references'].append('Ruby on Rails. (2025, 29 de octubre). New Rails releases and end of support announcement. '+eol_url)
    content['references']=list(dict.fromkeys(content['references']))
    (DOCS/'Contenido_Academico.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
    model=[
      dict(caracteristica='Adecuación funcional',proposito='Conservar resultados,posiciones,clasificación ypodio correctos',subcaracteristicas='Completitud,corrección,pertinencia',usuarios='Organizadores ypersonas que consultan el torneo',prioridad='Crítica',justificacion='Una inconsistencia de puntuación se propaga hasta la definición del campeón',requerimientos='RF-01..RF-09',pruebas='UT,INT,E2E,UAT',metricas='MET-01,MET-02'),
      dict(caracteristica='Mantenibilidad',proposito='Localizar ymodificar reglas sin regresiones',subcaracteristicas='Modularidad,reusabilidad,analizabilidad,modificabilidad',usuarios='Personas desarrolladoras ymantenedoras',prioridad='Alta',justificacion='Coexisten callbacks,controladores yservicios con responsabilidades de resultados',requerimientos='RNF-01',pruebas='EST-001 ySimpleCov deUT/INT',metricas='MET-03..MET-06'),
      dict(caracteristica='Seguridad',proposito='Proteger la integridad yla exposición de información',subcaracteristicas='Integridad,autenticidad,confidencialidad,resistencia',usuarios='Organizadores ydatos deltorneo',prioridad='Crítica',justificacion='Rutas de escritura sin identidad yvalidación dependiente de conversiones; candidato de archivo local',requerimientos='RNF-03',pruebas='SEG-001..SEG-006,Brakeman,advisories',metricas='MET-07,MET-08'),
      dict(caracteristica='Eficiencia de desempeño',proposito='Sostener consultas concurrentes con latencia acotada',subcaracteristicas='Comportamiento temporal,capacidad,utilización de recursos',usuarios='Personas consultando resultados al mismo tiempo',prioridad='Alta',justificacion='Consultas reiteradas ypersistenciaSQLite requieren medir cada nivel sin extrapolar',requerimientos='RNF-04',pruebas='PERF-001,PERF-002',metricas='MET-09,MET-10'),
      dict(caracteristica='Capacidad de interacción',proposito='Completar tareas einterpretar la información con modalidades diversas',subcaracteristicas='Operabilidad,inclusividad,aprendizaje,protección ante errores,asistencia',usuarios='Organizadores,espectadores ypersonas con necesidades de acceso',prioridad='Alta',justificacion='Formularios de marcador ytablas son esenciales para el uso ypueden presentar barreras',requerimientos='RNF-02',pruebas='USA-001,ACC-001..ACC-003,UAT',metricas='MET-11..MET-13')]
    csvwrite(DOCS/'Modelo_Calidad.csv',model)
    print('Metric notation clarified; frozen formulas and thresholds retained.')


if __name__=='__main__':main()
