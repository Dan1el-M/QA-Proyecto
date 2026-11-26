# Protocolo de aceptación

Responsable de coordinación: Jimena Vindas Acosta. Los responsables funcionales atienden las incidencias de sus RF. No hay sesiones registradas hasta importar formularios reales.

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
