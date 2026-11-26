# Inspección formal pendiente

Objetivo: verificar integridad del registro de resultados y separación de responsabilidades. Artefactos: app/controllers/partidos_controller.rb,app/models/partido.rb y app/services/actualizar_estadisticas_seleccion.rb del commit789565e.

Antes de asignar roles, consultar `git -C .. log --format="%h %an" -- app/controllers/partidos_controller.rb app/models/partido.rb`. Identificar al autor histórico sin modificar contribuidores. Propuesta inicial: moderador José Daniel Morera Elizondo; revisor César Gamboa Naranjo; escriba Jimena Vindas Acosta. Si el moderador o escriba es autor del artefacto,rotar dichos roles hacia personas que no lo sean. El autor explica y no modera ni registra su propia inspección. Documentar la rotación real.

Agenda propuesta: preparación individual20min,apertura5min,lectura estructurada20min,clasificación10min y seguimiento5min. Son duraciones previstas, no una reunión celebrada. Lista de cotejo: contrato3/1/0 puntos; un único recálculo; transacciones; entradas inválidas; aislamiento entre fases; conservación tras errores; rutas y vistas; claridad de responsabilidades; complejidad y duplicación. Hallazgos preliminares: consultar DEF-001..DEF-012; no aceptarlos sin revisión.

Completar qa/static/inspeccion.json con fecha_real,roles_reales,autor_artefacto,confirmado,decision_por_hallazgo,evidencias y acciones. No incluir firmas ficticias. Guardar acta real como qa/evidence/Inspeccion_Formal_Acta.md. Importar el JSON y regenerar. El registro de la revisión técnica automática no acredita esta reunión.
