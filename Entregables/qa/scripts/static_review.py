"""Evidence from source at the frozen baseline. No automatic production edits."""
import argparse
import csv
import json
import re
from datetime import datetime,timezone,timedelta
from pathlib import Path
from design import ROOT,APP_ROOT,DOCS,J,V,C,csvwrite


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);args=parser.parse_args()
    findings=[]
    def add(title,file,needle,description,expected,severity,req,owner,minutes,category='Anomalía estática',confirmation='Confirmado estáticamente',case='EST-001'):
        source=(APP_ROOT/file).read_text(encoding='utf-8')
        line=next((i for i,s in enumerate(source.splitlines(),1) if needle in s),None)
        if line is None:raise ValueError(f'Evidence not found: {file}: {needle}')
        fid=f'DEF-{len(findings)+1:03}'
        findings.append(dict(id=fid,titulo=title,descripcion=description,severidad=severity,
            prioridad='P1' if severity=='Crítica' else 'P2' if severity=='Alta' else 'P3',
            pasos=f'Abrir {file}, línea {line}, en el commit de línea base; revisar {needle}. '+case,
            esperado=expected,actual=source.splitlines()[line-1].strip(),evidencia=f'{file}:{line};qa/reports/baseline/baseline.json',
            estado='Abierto',confirmacion=confirmation,tipo=category,responsable=owner,caso=case,requerimiento=req,
            caracteristica='Seguridad' if req=='RNF-03' else 'Capacidad de interacción' if 'WCAG' in title else 'Mantenibilidad' if req=='RNF-01' else 'Adecuación funcional',
            modulo=file.split('/')[1] if '/' in file else 'Documentación',archivo=file,linea=line,commit='789565ea61bae6a84cc8d9ae3be871f601f4a2d1',
            fecha=datetime.now(timezone(timedelta(hours=-6))).isoformat(),ambiente='Análisis del código fuente, sin ejecución de la ruta',
            impacto=description,recomendacion=expected,costo_minutos=minutes))
    add('Campo visitante enlazado a goles_local','app/views/partidos_grupo/calendario.html.erb','value: partido.goles_visitante',
        'Los dos campos de marcador usan form.number_field :goles_local; el formulario no envía goles_visitante y repite nombre e identificador.',
        'Cada equipo debe enviar su propio marcador; validar y persistir 2-1.', 'Alta','RF-03',J,45,case='E2E-004')
    add('mensaje no inicializado en guardado eliminatorio','app/controllers/eliminacion_directa_controller.rb','mensaje += " Partidos',
        'En la rama sin errores se concatena a mensaje, cuya única asignación previa ocurre en una rama que retorna. El valor local es nil.',
        'Inicializar el mensaje antes de concatenarlo; guardar resultados y responder sin error.', 'Alta','RF-06',C,30,case='E2E-008')
    add('Acumulación adicional después de callbacks','app/controllers/partidos_controller.rb','@partido.seleccion_local.registrar_resultado_grupo(',
        'El controlador suma puntos y goles después de update que ya activa el recálculo after_save del modelo; hay dos caminos de actualización.',
        'Un resultado 2-1 debe contabilizarse una sola vez:3 puntos,GF2,GC1.', 'Alta','RF-04',J,90,case='INT-003')
    add('Conversión de marcador no numérico a cero','app/controllers/partidos_grupo_controller.rb','resultado_params[:goles_local].to_i',
        'La conversión to_i acepta abc o cadena vacía como cero antes de que el modelo valide la entrada.',
        'Rechazar un marcador no numérico sin alterar el partido.', 'Alta','RNF-03',C,60,case='SEG-006')
    add('Método podio definido dos veces','app/controllers/campeones_controller.rb','def podio',
        'CampeonesController declara dos métodos podio; Ruby conserva el último y hace inalcanzable el cuerpo anterior.',
        'Consolidar una única responsabilidad de consulta del podio.', 'Media','RNF-01',J,30)
    add('README describe servicios y rutas ausentes','README.md','GroupStandingService',
        'El README describe GroupStandingService y rutas /groups y /teams; el código contiene Grupo y Seleccion con rutas en español.',
        'Alinear instrucciones con config/routes.rb y los cuatro servicios reales.', 'Media','RNF-01',J,45)
    add('Vistas de rutas declaradas no entregadas','app/controllers/clasificados_controller.rb','render :en_progreso',
        'No existe app/views/clasificados/en_progreso.html.erb. También faltan vistas implícitas de varios recursos declarados.',
        'Toda ruta HTML expuesta debe disponer de una respuesta renderizable; revisar inventario de rutas/vistas.', 'Alta','RF-05',C,180,case='E2E-007')
    add('Avance admite una etapa sin partidos','app/models/torneo.rb','pendientes.zero?',
        'La condición de avance solo consulta cero partidos pendientes; una colección vacía también satisface la condición.',
        'Exigir los partidos requeridos y su finalización antes de avanzar.', 'Alta','RF-08',C,90)
    add('Estadísticas de grupo mezclan partidos eliminatorios','app/services/actualizar_estadisticas_seleccion.rb','Partido.where(estado: "finalizado")',
        'El recálculo incluye todos los tipos de partido y los convierte en puntos. Recalcular grupos después de eliminación puede alterar la clasificación.',
        'Separar estadísticas de fase de grupos de otras fases según RF-04.', 'Alta','RF-04',J,120)
    add('Colisión de acrónimo genera caracteres rechazados','app/models/seleccion.rb','candidato = "#{base.first(2)}#{contador}"',
        'El generador resuelve colisiones con un dígito, pero la validación acepta únicamente letras mayúsculas.',
        'Resolver colisiones dentro del alfabeto permitido o informar un error claro.', 'Media','RF-01',V,60)
    add('WCAG: documento HTML sin idioma','app/views/layouts/application.html.erb','<html>',
        'El layout raíz carece del atributo lang. El criterio WCAG2.2 3.1.1 exige identificar el idioma de la página.',
        'Declarar el idioma principal en html y verificar las tres pantallas renderizadas.', 'Media','RNF-02',V,15)
    add('Lectura de rutas locales desde bandera_url','app/helpers/application_helper.rb','archivo = Rails.root.join(ruta)',
        'Se admiten rutas relativas sin comprobar que la ruta resuelta permanezca en flags o en un directorio de imágenes autorizado. La salida usa binread y Base64.',
        'Limitar las rutas resueltas al directorio permitido; confirmar exploit solo con un archivo sintético.', 'Alta','RNF-03',C,120,category='Candidato de seguridad',confirmation='Pendiente de verificación dinámica',case='SEG-005')
    csvwrite(DOCS/'Registro_Defectos.csv',findings)
    csvwrite(DOCS/'Deuda_Tecnica.csv',[dict(id='DT-'+f['id'][4:],defecto=f['id'],componente=f['archivo'],descripcion=f['titulo'],evidencia=f['evidencia'],impacto=f['impacto'],minutos=f['costo_minutos'],prioridad=f['prioridad'],recomendacion=f['recomendacion'],dependencias='Ratificar riesgo y reproducir; no duplicar tickets por herramienta',orden=i+1) for i,f in enumerate(sorted(findings,key=lambda f:(f['prioridad'],f['id'])))])
    reqs=json.loads((ROOT/'qa/data/design.json').read_text(encoding='utf-8'))['requirements']
    gaps={
      'RF-01':('No especifica dominios de puntajes ni reglas de edición','Registrar nombre único de1..100 caracteres,acrónimo de2..3 letras,grupo existente con capacidad y estadísticas enteras no negativas.'),
      'RF-02':('No indica qué sucede al eliminar un grupo con selecciones','Administrar grupos únicos A..L; rechazar eliminación si conserva selecciones y explicar el motivo.'),
      'RF-03':('No define edición ni dominio de marcadores','Registrar goles enteros>=0 de ambos equipos y actualizar cada estadística exactamente una vez; edición conserva consistencia.'),
      'RF-04':('No resuelve empate en los tres criterios','Ordenar puntos,DG,GF descendentes; si persiste empate, definir y aprobar criterio final antes de aceptación.'),
      'RF-05':('No declara cuándo habilitar la clasificación','Tras72 partidos completos de12 grupos con4 equipos, devolver24 directos y8 terceros distintos,ordenados por puntos,DG,GF.'),
      'RF-06':('No determina emparejamientos ni condición de avance','Definir bracket de32 selecciones y generar rondas16,8,4,2,tercer lugar y final sin duplicación.'),
      'RF-07':('No define penal incompleto ni empate de tanda','Para empate eliminatorio exigir ambos penales enteros>=0 y distintos antes de considerar resuelto el partido.'),
      'RF-08':('primera fase es ambiguo','Al finalizar todos los partidos de la ronda actual,crear exactamente la siguiente ronda con sus ganadores; no avanzar una ronda vacía.'),
      'RF-09':('No define cuándo publicar podio','Mostrar campeón y subcampeón del partido104 y tercero del103 únicamente con ambos partidos finalizados y ganadores válidos.')}
    review=[];spec_defects=[]
    original=(APP_ROOT/'Proyecto_4_POO_Mundial_2026.md').read_text(encoding='utf-8')
    requirements_section=original.split('## Requerimientos del sistema')[1].split('## Consideraciones')[0]
    for r in reqs:
        if r['id'] not in gaps:continue
        gap,rewrite=gaps[r['id']]
        match=re.search(r'(?ms)^'+str(int(r['original_id']))+r'\. (.*?)(?=^\d+\. |\Z)',requirements_section)
        original_text=match.group(0).strip()
        review.append(dict(id='REV-'+r['id'][3:],requerimiento=r['id'],fuente=r['fuente'],texto_original=original_text,
          ambiguedad='Cumple parcialmente',completitud='Cumple parcialmente',consistencia='Cumple parcialmente' if r['id']=='RF-08' else 'Cumple',
          correctitud='No verificable',verificabilidad='Cumple parcialmente',trazabilidad='Cumple parcialmente',hallazgo=gap,
          impacto='Oráculo incompleto y riesgo de implementaciones incompatibles',recomendacion='Ratificar la propuesta sin modificar la especificación fuente',propuesta=rewrite,responsable=r['responsable']))
        line=next(i for i,s in enumerate(original.splitlines(),1) if s.startswith(r['original_id']+'. '))
        spec_defects.append(dict(findings[0],id=f'DEF-{12+len(review):03}',titulo='Deficiencia de especificación de '+r['id'],descripcion=gap,
          severidad='Media',prioridad='P3',pasos='Leer '+r['fuente']+' y contrastar la lista de cotejo REV-'+r['id'][3:],
          esperado='Regla inequívoca,completa y verificable; propuesta: '+rewrite,actual=original_text,
          evidencia=f'Proyecto_4_POO_Mundial_2026.md:{line};docs/Revision_Requerimientos.csv',
          confirmacion='Confirmado estáticamente; propuesta pendiente de ratificación',tipo='Deficiencia de especificación',responsable=r['responsable'],
          caso='EST-001',requerimiento=r['id'],caracteristica='Adecuación funcional',modulo='Especificación',archivo='Proyecto_4_POO_Mundial_2026.md',linea=line,
          impacto='Interpretaciones incompatibles y oráculos incompletos',recomendacion=rewrite,costo_minutos='No estimado'))
    csvwrite(DOCS/'Revision_Requerimientos.csv',review)
    csvwrite(DOCS/'Registro_Defectos.csv',findings+spec_defects)
    relative=str(args.run.relative_to(ROOT))
    (args.run/'static-review.json').write_text(json.dumps({'findings':len(findings),'requirements_reviewed':len(review),'source':'app/ and original specification','status':'Fallido','remediation_minutes':sum(f['costo_minutos'] for f in findings),'development_assumption':'2 minutos por línea Ruby no vacía ni comentario; estimación interna, no medición SonarQube; no sumar hallazgos repetidos'},ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'qa/static').mkdir(exist_ok=True)
    (ROOT/'qa/static/Acta_Revision.md').write_text('# Revisión técnica de requerimientos y código\n\nArtefacto: línea base789565e. Análisis técnico documentado en Revision_Requerimientos.csv y Registro_Defectos.csv.\n\nSe evaluaron ambigüedad, completitud, consistencia, correctitud, verificabilidad y trazabilidad. La correctitud frente a usuarios reales permanece sin ratificación. Los nueve RF necesitan precisión adicional; no se alteró el original.\n\nNo se registra una reunión, asistentes ni firmas: la inspección formal del equipo sigue pendiente.\n\nLas estimaciones de deuda son minutos de trabajo: localizar y reproducir(15..30),corregir(15..90),verificar regresión(15..60),según alcance. No representan horas realmente trabajadas.\n\nReporte asociado: '+relative+'/static-review.json\n',encoding='utf-8')
    print('Source findings:',len(findings),'(including one unconfirmed security candidate); requirement reviews:',len(review))


def test_EST_001():
    main()


if __name__=='__main__':test_EST_001()
