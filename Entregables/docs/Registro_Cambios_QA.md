# Registro de cambios de QA

Actualizado: 2026-11-25T22:54:35.200487-06:00.

Rama: qa-auditoria-integral. Línea base:789565ea61bae6a84cc8d9ae3be871f601f4a2d1. El inventario completo está en Registro_Cambios_QA.csv. No se realizaron commits,push,merge nireescritura de historial.

Los342 archivos originales se comprueban mediante SHA256 en qa/reports/baseline/baseline.json e integrity.json. Ningún archivo original fue modificado. Los cambios son adiciones de pruebas,configuración deQA,instrumentos,reportes ydocumentación.

Ajustes del arnés: escape de espacios de DATABASE_URL; bundle unitario separado para métodos aislados; carga nativa con RI_FORCE_PATH_FOR_DLL; búsqueda absoluta de ejecutables en Windows; doble de reorder compatible con keywords; identificador de Minitest corregido para conservar resultados; Brakeman secuencial para Windows. Ningún ajuste cambió los resultados esperados congelados.

Traslado solicitado por el usuario: docs/, qa/, test/, .qa-runtime/ y las referencias están ahora dentro de Entregables/. Se actualizaron las rutas del arnés y la documentación; app/, config/, db/ y los Gemfile originales permanecen en la raíz. GitHub Actions permanece en .github/ y ejecuta desde Entregables. Los reportes históricos y los oráculos congelados conservan su contenido.

Soporte de entorno: Ruby4.0.5 ygemas en .qa-runtime; MSYS2 base temporal fuera de rutas con@. Se conserva una unión temporal al proyecto como diagnóstico de globs; no cambia archivos. El toolchain no pudo descargarse desde los espejos. Runtimes,cachés yDB están excluidos deGit; los reportes originales por corrida permanecen disponibles.

La notación de variables de métricas se precisó sin cambiar fórmulas,umbrales nioráculos de qa/data/design.json. Las observaciones automáticas no se convierten en defectos confirmados sin clasificación.

| Grupo | Archivos inventariados |
|---|---|
| .github | 1 |
| Entregables | 482 |
