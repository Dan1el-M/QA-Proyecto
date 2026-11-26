# Evidencias pendientes

Directorio para todos los comandos: QA-Proyecto/Entregables (desde el repositorio: `cd Entregables`). Terminal: Git Bash. Preparación: `source qa/scripts/env.sh`. Las actividades completadas se eliminan automáticamente de este registro al regenerar.

## José Daniel Morera Elizondo

### EV-P-INT-José · Figura 13. Evidencia de Funcional / Integración

Casos: INT-001, INT-002, INT-003.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: José Daniel Morera Elizondo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only integration
```

Archivo gráfico alternativo: qa/evidence/Figura_013.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-E2E-José · Figura 14. Evidencia de Funcional / Sistema

Casos: E2E-004, E2E-005, E2E-006.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: José Daniel Morera Elizondo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only e2e
```

Archivo gráfico alternativo: qa/evidence/Figura_014.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-UAT-José · Figura 18. Evidencia de Funcional / Aceptación

Casos: UAT-001, UAT-002.

Motivo: requiere participantes externos reales y confirmación de la sesión.

Responsable: José Daniel Morera Elizondo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
python qa/scripts/import_human.py qa/acceptance/resultados.csv
```

Seguir qa/acceptance/protocolo.md; preparar los perfiles indicados y servidor `bash qa/scripts/start.sh base`; usar http://127.0.0.1:3100. Completar qa/acceptance/resultados.csv con fecha real,consentimiento,observación,estado,evidencia yconfirmado=true; importar con `python qa/scripts/import_human.py qa/acceptance/resultados.csv`. No registrar personas que no participaron.

Archivo gráfico alternativo: qa/evidence/Figura_018.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

Confirmar aporte individual y revisar los hallazgos asignados en Distribucion_Trabajo.md; no se acredita autoría ni sesión a partir de la asignación.

## Jimena Vindas Acosta

### EV-P-INT-Jimena · Figura 13. Evidencia de Funcional / Integración

Casos: INT-004, INT-005, INT-006.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: Jimena Vindas Acosta. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only integration
```

Archivo gráfico alternativo: qa/evidence/Figura_013.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-E2E-Jimena · Figura 14. Evidencia de Funcional / Sistema

Casos: E2E-001, E2E-002, E2E-003.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: Jimena Vindas Acosta. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only e2e
```

Archivo gráfico alternativo: qa/evidence/Figura_014.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-ACC-Jimena · Figura 17. Evidencia de Accesibilidad / Sistema

Casos: ACC-001, ACC-002, ACC-003.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: Jimena Vindas Acosta. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only accessibility
```

Complementar axe con qa/accessibility/manual.md ymanual.csv; guardar capturas ACC-001_manual.png,ACC-002_manual.png,ACC-003_manual.png en qa/evidence; importar elCSV confirmado.

Archivo gráfico alternativo: qa/evidence/Figura_017.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-USA-Jimena · Figura 19. Evidencia de Usabilidad / Sistema

Casos: USA-001.

Motivo: requiere participantes externos reales y confirmación de la sesión.

Responsable: Jimena Vindas Acosta. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
python qa/scripts/import_human.py qa/usability/resultados.csv
```

Seguir qa/usability/protocolo.md; preparar los perfiles indicados y servidor `bash qa/scripts/start.sh base`; usar http://127.0.0.1:3100. Completar qa/usability/resultados.csv con fecha real,consentimiento,observación,estado,evidencia yconfirmado=true; importar con `python qa/scripts/import_human.py qa/usability/resultados.csv`. No registrar personas que no participaron.

Archivo gráfico alternativo: qa/evidence/Figura_019.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

Confirmar aporte individual y revisar los hallazgos asignados en Distribucion_Trabajo.md; no se acredita autoría ni sesión a partir de la asignación.

## César Gamboa Naranjo

### EV-P-INT-César · Figura 13. Evidencia de Funcional / Integración

Casos: INT-007, INT-008, INT-009.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: César Gamboa Naranjo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only integration
```

Archivo gráfico alternativo: qa/evidence/Figura_013.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-E2E-César · Figura 14. Evidencia de Funcional / Sistema

Casos: E2E-007, E2E-008, E2E-009.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: César Gamboa Naranjo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only e2e
```

Archivo gráfico alternativo: qa/evidence/Figura_014.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-SEG-César · Figura 16. Evidencia de Seguridad / Integración

Casos: SEG-001, SEG-002, SEG-003, SEG-004, SEG-005, SEG-006.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: César Gamboa Naranjo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only security
```

Archivo gráfico alternativo: qa/evidence/Figura_016.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-PERF-César · Figura 15. Evidencia de Rendimiento / Sistema

Casos: PERF-001, PERF-002.

Motivo: la ejecución o la revisión complementaria no produjo evidencia concluyente; consultar el último log asociado al caso.

Responsable: César Gamboa Naranjo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
bash qa/scripts/run_all.sh --only performance --load
```

Archivo gráfico alternativo: qa/evidence/Figura_015.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

### EV-P-UAT-César · Figura 18. Evidencia de Funcional / Aceptación

Casos: UAT-003.

Motivo: requiere participantes externos reales y confirmación de la sesión.

Responsable: César Gamboa Naranjo. Sección Word:12 y25; tabla de cada caso en13; métricas de18. Prerrequisitos: Ruby4.0.5,Devkit,Bundler y bundle deQA instalados; navegador para E2E/ACC; k6 para PERF. Base exclusiva qa/data/qa.sqlite3; nunca producción.

Comando exacto:

```bash
python qa/scripts/import_human.py qa/acceptance/resultados.csv
```

Seguir qa/acceptance/protocolo.md; preparar los perfiles indicados y servidor `bash qa/scripts/start.sh base`; usar http://127.0.0.1:3100. Completar qa/acceptance/resultados.csv con fecha real,consentimiento,observación,estado,evidencia yconfirmado=true; importar con `python qa/scripts/import_human.py qa/acceptance/resultados.csv`. No registrar personas que no participaron.

Archivo gráfico alternativo: qa/evidence/Figura_018.png. Debe mostrar el resultado real ysu identificación; para pruebas automáticas se prefieren reportes,backtraces ytrazas originales. Las visualizaciones derivadas se generan automáticamente cuando hay resultados auténticos. Nunca fabricar una captura de terminal.

Resultado a registrar: estado observado ydatos requeridos por elcaso; conservar también fallos ybloqueos. Actualiza Casos_de_Prueba,Matriz_Trazabilidad,Resultados_Metricas eInventario_Evidencias. Después ejecutar `bash qa/scripts/finalize_report.sh`; abrir elWord yactualizar campos conCtrl+A,F9.

Confirmar aporte individual y revisar los hallazgos asignados en Distribucion_Trabajo.md; no se acredita autoría ni sesión a partir de la asignación.

## Inspección formal del equipo · Figura20

Responsables: los tres integrantes con rotación porautoría. Directorio Entregables; leer qa/static/Inspeccion_Formal.md. Preparar20min de revisión individual ysesión con moderador,revisor yescriba reales. Consultar autoría con `git -C .. log --format="%h %an" -- app/controllers/partidos_controller.rb app/models/partido.rb`; el autor no modera niregistra. Guardar acta auténtica en qa/evidence/Inspeccion_Formal_Acta.md; completar qa/static/inspeccion.json. Importar `python qa/scripts/import_human.py qa/static/inspeccion.json`; regenerar. Figura20 enanexos; sección11.3. No inventar asistentes,fechas,acuerdos nifirmas.

## Figura21. pantalla principal

Responsable: Jimena Vindas Acosta. Preparar Ruby,dependencias ybaseQA; ejecutar `bash qa/scripts/start.sh base`. Abrir http://127.0.0.1:3100/; mostrar URL,pantalla completa ydatos EquipoQA. Guardar qa/evidence/Figura_021.png. Capítulos6.4,10.6 yanexos; regenerar con finalize_report.sh. La imagen se incorpora automáticamente si existe.

## Figura22. calendario

Responsable: José Daniel Morera Elizondo. Preparar Ruby,dependencias ybaseQA; ejecutar `bash qa/scripts/start.sh base`. Abrir http://127.0.0.1:3100/partidos_grupo/calendario; mostrar URL,pantalla completa ydatos EquipoQA. Guardar qa/evidence/Figura_022.png. Capítulos6.4,10.6 yanexos; regenerar con finalize_report.sh. La imagen se incorpora automáticamente si existe.

## Figura23. podio

Responsable: César Gamboa Naranjo. Preparar Ruby,dependencias ybaseQA; ejecutar `bash qa/scripts/start.sh podium`. Abrir http://127.0.0.1:3100/campeones/podio; mostrar URL,pantalla completa ydatos EquipoQA. Guardar qa/evidence/Figura_023.png. Capítulos6.4,10.6 yanexos; regenerar con finalize_report.sh. La imagen se incorpora automáticamente si existe.

## GitHub Actions · Figura24

Responsable de automatización: José Daniel Morera Elizondo. Elworkflow local está en ../.github/workflows/qa.yml. La ejecución remota requiere que el equipo decida publicar la rama; no se hace push automáticamente. Después,abrir Actions→QA auditoría→Run workflow; guardar una captura auténtica qa/evidence/Figura_024_CI.png con nombre yresultado de la corrida. Regenerar. La configuración yla ejecución son evidencias distintas.
