# Entregables de la auditoría QA

Esta carpeta contiene el informe Word y sus matrices en `docs/`, el arnés y los reportes en `qa/`, las pruebas en `test/`, las herramientas locales excluidas de Git en `.qa-runtime/`, el enunciado PDF y la imagen de referencia.

Desde la raíz de QA-Proyecto:

```bash
cd Entregables
source qa/scripts/env.sh
bash qa/scripts/run_all.sh
```

Consultar [qa/README.md](qa/README.md) para instalar dependencias, iniciar el sistema, ejecutar conjuntos específicos e incorporar evidencias. El informe está en [docs/Informe_Final_QA_Mundial.docx](docs/Informe_Final_QA_Mundial.docx), y las actividades pendientes en [docs/PENDIENTES_EVIDENCIAS.md](docs/PENDIENTES_EVIDENCIAS.md).

La aplicación evaluada permanece un nivel arriba. No mover `.github/` a esta carpeta: GitHub necesita sus workflows en la raíz del repositorio. El arnés resuelve la aplicación original y los entregables por separado, sin enlaces simbólicos ni copias duplicadas.
