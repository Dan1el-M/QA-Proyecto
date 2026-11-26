# Verificación de cumplimiento

Fuente principal: Proyecto-Integrado-2026-II.pdf,8 páginas; revisado íntegramente en texto y representación visual. Las ampliaciones de entrega se identifican aparte. Un protocolo no acredita actividad humana.

| ID | Página | Requisito | Mínimo | Resultado | Sección | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| AC-001 | 1–2 | Ficha del sistema | Ocho datos | Identificación y procedencia explícitas | 1 | qa/reports/baseline/baseline.json | Cumple |
| AC-002 | 2 | Alcance incluido | Módulos,funciones,interfaces | Matriz por requerimiento | 5 | docs/Alcance.csv | Cumple |
| AC-003 | 2 | Justificación de exclusiones | Motivo y riesgo aceptable | Exclusiones técnicas y riesgos residuales | 5 | docs/Exclusiones.csv | Cumple |
| AC-004 | 3 | Cinco características | 5,con tres obligatorias | Modelo con adecuación,mantenibilidad,seguridad,desempeño e interacción | 7 | docs/Fichas_Metricas.csv | Cumple |
| AC-005 | 3 | Prioridad y selección | Justificación por característica | Prioridad,usuarios y subcaracterísticas | 7.2 | docs/Contenido_Academico.json | Cumple |
| AC-006 | 3 | Características excluidas | Una justificación por exclusión | Compatibilidad,fiabilidad,flexibilidad,Safety | 7.3 | docs/Contenido_Academico.json | Cumple |
| AC-007 | 3 | Objetivos GQM | Uno por característica | Cinco objetivos con plantilla Basili | 7.4 | docs/GQM.csv | Cumple |
| AC-008 | 3 | Preguntas GQM | 2–4 por objetivo | Quince preguntas | 7.4 | docs/GQM.csv | Cumple |
| AC-009 | 4–5 | Fichas de métricas | Mínimo cinco completas | Trece fichas con campos y umbrales | 7.5 | docs/Fichas_Metricas.csv | Cumple |
| AC-010 | 3 | Plan de calidad | Doce elementos mínimos | Estrategia,recursos,criterios,ambientes y datos | 8 | docs/Contenido_Academico.json | Cumple |
| AC-011 | 4 | Revisión de requerimientos | Acta,hallazgos y reescrituras | Nueve revisiones técnicas; ratificación humana pendiente | 11.1 | docs/Revision_Requerimientos.csv;qa/static/Acta_Revision.md | Cumple |
| AC-012 | 4 | Revisión de código | Archivo,línea,clasificación | Hallazgos estáticos con localización y evidencia | 11.2 | docs/Registro_Defectos.csv | Cumple |
| AC-013 | 4 | Inspección formal | Una sesión con roles | Protocolo preparado; acreditar solo acta confirmada | 11.3 | qa/static/Inspeccion_Formal.md | Cumple parcialmente |
| AC-014 | 4 | Mantenibilidad | Reporte y análisis propio | Prism AST y jscpd; herramientas Ruby según disponibilidad | 11.4 | docs/Resultados_Metricas.csv | Cumple |
| AC-015 | 4 | Deuda técnica | Estimación y propuesta priorizada | Estimación explícita,sensibilidad y límites | 19 | docs/Deuda_Tecnica.csv | Cumple |
| AC-016 | 5–6 | RF por integrante | 2 por integrante,con niveles aplicables | Nueve RF asignados y diseñados; ejecución de niveles aplicables se verifica aparte | 23 | docs/Inventario_Requerimientos.csv | Cumple parcialmente |
| AC-017 | 5–6 | RNF por integrante | 1 por integrante evaluado | Cuatro RNF seleccionados; asignación no equivale a evaluación | 23 | docs/Inventario_Requerimientos.csv | Cumple parcialmente |
| AC-018 | 4–5 | Cinco características evaluadas | Evidencia suficiente de las cinco | Separar selección del modelo de la evaluación efectiva | 18 | docs/Resultados_Metricas.csv | Cumple parcialmente |
| AC-019 | 5 | Casos positivos,negativos y frontera | Tipos aplicables | Catálogo congelado antes de la ejecución | 13 | qa/data/Casos_Diseno_Pre_Ejecucion.csv | Cumple |
| AC-020 | 5 | Unitarias ejecutadas | Clases aisladas | 18 implementadas; resultados individuales en catálogo | 12.1 | docs/Casos_de_Prueba.csv | Cumple |
| AC-021 | 5 | Cobertura de código | Reporte de cobertura | SimpleCov; excluir reportes generados antes de iniciar pruebas | 12.1 | docs/Resultados_Metricas.csv | Cumple |
| AC-022 | 5 | Integración y efectos secundarios | Colaboración real y persistencia | Respuesta y estado de DB; transacciones | 12.2 | test/integration/qa_integration_test.rb | Cumple parcialmente |
| AC-023 | 5 | Sistema E2E | Interfaz real automatizada | Nueve recorridos con captura y traza de fallo | 12.3 | qa/e2e/mundial.spec.cjs | Cumple parcialmente |
| AC-024 | 5 | Aceptación real | 3 escenarios,>=2 externos | 0 registros confirmados | 12.4 | qa/acceptance/resultados.csv | Pendiente |
| AC-025 | 5 | Dos escenarios de rendimiento | Carga creciente | 5/10/20 y25/50/100VU; únicamente local | 12.5 | qa/performance/load.js | Cumple parcialmente |
| AC-026 | 5 | Umbrales previos de rendimiento | Declaración antes de medir | P95<=1s,errores<=1%;conservados en diseño | 7.5 y12.5 | qa/data/design.json | Cumple |
| AC-027 | 5 | Seis verificaciones de seguridad | 6 aplicables ejecutadas | SQLi,XSS,acceso,CSRF,errores,entradas | 12.6 | test/integration/qa_security_test.rb | Cumple parcialmente |
| AC-028 | 5 | Usabilidad real | 1 prueba con3 personas | 0 intentos reales confirmados | 12.7 | qa/usability/resultados.csv | Pendiente |
| AC-029 | 5 | Accesibilidad de tres pantallas | WCAG2.2 AA manual+automática | Instrumento de aplicabilidad completo para A/AA yaxe; resultados solo confirmados | 12.8 | qa/accessibility/manual.csv | Cumple parcialmente |
| AC-030 | 5–6 | Defectos registrados | Todos los hallazgos identificados | 167 registros con origen y confirmación | 16 | docs/Registro_Defectos.csv | Cumple |
| AC-031 | 5–6 | Campos obligatorios de casos | 16 campos mínimos | Evidencia vacía solo en casos no ejecutados | 13 | docs/Casos_de_Prueba.csv | Cumple |
| AC-032 | 6 | Trazabilidad bidireccional | Ocho columnas | Referencias validadas por identificador | 15 | docs/Matriz_Trazabilidad.csv | Cumple |
| AC-033 | 6 | Responsabilidades individuales | Nombre completo | Asignación explícita; aportes personales sin ratificar | 23 | docs/Distribucion_Trabajo.md | Cumple |
| AC-034 | 7 | Comando único de automatización | Comando reproducible | bash qa/scripts/run_all.sh | 14 | qa/scripts/run_all.py | Cumple |
| AC-035 | 7 | Informe por corrida | Comando,fecha,exit y evidencia | Conservar éxitos y fallos independientes | 14 y17 | qa/reports/runs/ | Cumple |
| AC-036 | 7 | Capturas o trazas de fallos | Cada fallo ejecutado | Fallos nativos conservan backtrace; E2E conserva trace.zip | 14 | qa/reports/runs/ | Cumple |
| AC-037 | 7 | GitHub Actions | Opcional; incluir configuración | Configurado localmente; ejecución remota no acreditada | 14.5 | ../.github/workflows/qa.yml | Cumple |
| AC-038 | 7 | Datos sintéticos | Sin información personal de prueba | Equipo QA,códigos y participantes anónimos | 8 y10 | qa/data/dataset.rb | Cumple |
| AC-039 | 7 | Sin secretos publicados | Variables y exclusiones | No se copian claves; claves privadas no se leen | 8 | qa/scripts/baseline.py | Cumple |
| AC-040 | 7 | Pruebas propias y autorizadas | Loopback y base aislada | Guardas de destino y conexión | 8 y12 | qa/boot.rb;qa/performance/load.js | Cumple |
| AC-041 | 1,7–8 | Recomendación de liberación | Defendible con evidencia | Decisión derivada de defectos y límites | 21 | qa/reports/summary.json | Cumple |
| AC-042 | 7–8 | Secciones académicas | Todas las mínimas | Veinticinco capítulos y portada | 1–25 | docs/Informe_Final_QA_Mundial.docx | Cumple |
| AC-043 | Imagen adjunta | Estructura del programa | Diseño,diagramas,prototipo,instructivo y distribución | Incluida en capítulos6,10 y23 | 6,10,23 | Screenshot 2026-11-25 144953.png | Cumple |
| AC-044 | Ampliación de entrega | Figuras numeradas | Consecutivas,sin duplicación | Fuentes editables y reservas definitivas | 6 y25 | docs/Manifest_Figuras.json | Cumple |
| AC-045 | Ampliación de entrega | Tablas e índices | SEQ y TOC automáticos | Campos actualizables en Word | Índices ycapítulos | docs/Informe_Final_QA_Mundial.docx | Cumple |
| AC-046 | Ampliación de entrega | Referencias | Fuentes identificadas | APA7; sin afirmar consulta íntegra de normas | 24 | docs/Contenido_Academico.json | Cumple |
| AC-047 | Ampliación de entrega | Anexos,evidencias y regeneración | Fuentes y mecanismos editables | Importación validada y regeneración | 25 | qa/scripts/finalize.py | Cumple |

Consistencia: sin errores de referencias.

Disposiciones pendientes o parciales: 11.
