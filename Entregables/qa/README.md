# Auditoría reproducible de Mundial-POO

Los comandos de este documento se ejecutan desde `QA-Proyecto/Entregables`. Desde la raíz del repositorio, ejecutar primero `cd Entregables`. Los lanzadores también funcionan desde la raíz como `bash Entregables/qa/scripts/run_all.sh` o `bash Entregables/qa/scripts/start.sh base`.

Las rutas `docs/`, `qa/`, `test/` y `.qa-runtime/` son relativas a Entregables. Las referencias a `app/`, `config/`, `db/`, `Gemfile`, `Gemfile.lock` y los documentos originales son relativas a la raíz del repositorio, un nivel arriba. El arnés resuelve ambas ubicaciones desde sus propios archivos. La base exclusiva queda en `Entregables/qa/data/qa.sqlite3`. GitHub Actions permanece en `.github/workflows/qa.yml`, en la raíz del repositorio, y ejecuta sus comandos dentro de Entregables.

Los reportes históricos conservan sus comandos y rutas originales como evidencia de las ejecuciones anteriores al traslado. Sus rutas relativas `qa/reports/...` ahora se consultan desde Entregables; no se reescribe la salida original de las herramientas.

La auditoría conserva app/,config/,db/,Gemfile yGemfile.lock originales. La línea base es789565ea61bae6a84cc8d9ae3be871f601f4a2d1 y la rama local esqa-auditoria-integral. No hay commits nipush automáticos.

## Preparación en Windows con Git Bash

Utilizar Ruby4.0.5 con Devkit(MSYS2),Bundler4.0.10,Node22 o superior yPython3.12. Si la ruta de instalación de MSYS2 contiene@,su instalador la rechaza: instalar el Devkit en una ruta sinese carácter y definir MSYS2_PATH. La aplicación y los artefactos permanecen en este repositorio.

```bash
source qa/scripts/env.sh
gem install bundler -v 4.0.10 --no-document
ridk install 3
bundle install
BUNDLE_GEMFILE="$(cygpath -w "$PWD/qa/unit.Gemfile")" bundle install
npm ci --prefix qa
node qa/node_modules/@playwright/test/cli.js install chromium
python -m pip install -r qa/requirements.txt
```

En Linux,eliminar cygpath: `BUNDLE_GEMFILE=qa/unit.Gemfile bundle install`. El pipeline prepara esta variante. La distribución Ruby portátil descargada se conserva en .qa-runtime y está excluida deGit; no se requiere para usar una instalación normal.

La preparación real encontró fallos de carga deDLL yglobs absolutos dentro del sandbox; RI_FORCE_PATH_FOR_DLL=1 resolvió el primero y la ejecución autorizada fuera del sandbox permitió la suite unitaria. MSYS2base se instaló en una carpeta temporal sin@; la descarga del toolchain falló por resolución/conexión de sus espejos. Consultar qa/reports/baseline. No desactivar validaciones niseguridad para conseguir aprobados.

## Comandos

```bash
# Inicia exclusivamente el ambiente de prueba local
bash qa/scripts/start.sh base

# Suite y conjuntos individuales; devuelve código no cero ante fallo/bloqueo
bash qa/scripts/run_all.sh
bash qa/scripts/run_all.sh --only unit
bash qa/scripts/run_all.sh --only integration
bash qa/scripts/run_all.sh --only e2e
bash qa/scripts/run_all.sh --only security
bash qa/scripts/run_all.sh --only accessibility
bash qa/scripts/run_all.sh --only performance --load
bash qa/scripts/run_all.sh --only static

# Minitest individual: el nombre coincide con el catálogo
ruby test/unit/qa_unit_test.rb --name test_UT_001

# Datos propios: vacío,base,grupos finalizados,eliminatoria o podio
ruby qa/scripts/prepare.rb base
ruby qa/scripts/prepare.rb finished
ruby qa/scripts/prepare.rb knockout
ruby qa/scripts/prepare.rb podium

# Resultados reales y regeneración
python qa/scripts/import_human.py qa/acceptance/resultados.csv
python qa/scripts/import_human.py qa/usability/resultados.csv
python qa/scripts/import_human.py qa/accessibility/manual.csv
python qa/scripts/import_human.py qa/static/inspeccion.json
python qa/scripts/recalculate_metrics.py
python qa/scripts/generate_report.py
bash qa/scripts/finalize_report.sh
bash qa/scripts/finalize_report.sh --final
python qa/scripts/verify_compliance.py --final
```

El modo final devuelve2 cuando faltan evidencias obligatorias omarcadores temporales; no declara listo un documento solo por tener estructura. Los formularios vacíos son rechazados por import_human.py. Los perfiles de datos eliminan exclusivamente los registros delSQLiteQA protegido por guardas de conexión.

Los casos y resultados esperados se congelaron antes de ejecutar en qa/data/design.json yCasos_Diseno_Pre_Ejecucion.csv. No editar esos archivos para adecuarlos a los resultados. Una corrección del arnés se documenta sin cambiar el oráculo.

## Evidencias y documento

Reportes: qa/reports/runs/FECHA/run.json,logs yreportes originales. Figuras reales: colocar imágenes con sus nombres establecidos en qa/evidence; consultar docs/PENDIENTES_EVIDENCIAS.md. Los diagramas y sus fuentes DOT/JSON están en docs/diagramas. Las carpetas de reportes no están excluidas; se excluyen dependencias,cachés,DB propias,copias de respaldo yPNG/PDF del renderizado interno. Los reportes ytrazas auténticos permanecen disponibles para conservarse enGit o como artefactos delpipeline.

El Word principal es docs/Informe_Final_QA_Mundial.docx. El generador lee contenido académico editable,CSV,JSON,diagramas yreportes; crea una copia previa en qa/reports/backups antes de sobrescribir. Para actualizar todos los campos en Word: Ctrl+A,F9; si pregunta,seleccionar «Actualizar toda la tabla»; guardar. Los índices de figuras/tablas usanSEQ yTOC.

La matriz de cumplimiento yel resumen se recalculan sin inventar actividades humanas. Las asignaciones no acreditan ejecución personal. Ver Distribucion_Trabajo.md ylos protocolos en acceptance/,usability/,accessibility/ ystatic/.

El workflow de ../.github/workflows/qa.yml se valida localmente. Su ejecución remota permanece sin acreditar hasta que el equipo publique ylo ejecute por decisión propia. No realizar push para generar evidencia automática.
