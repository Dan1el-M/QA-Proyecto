# Prueba de usabilidad

Coordinación: Jimena Vindas Acosta. Muestra prevista: tres personas externas P01,P02,P03; no se simulan intentos. Esta evaluación se registra aparte de aceptación aunque compartan personas.

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
