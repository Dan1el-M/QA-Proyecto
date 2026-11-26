"""Reviewable inventory of additions; never stages, commits or pushes."""
import hashlib,json,subprocess
from datetime import datetime,timezone,timedelta
from design import ROOT,APP_ROOT,DOCS,csvwrite


def main():
    paths=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=APP_ROOT).decode('utf-8').split('\0')
    records=[]
    for name in sorted(x for x in paths if x):
        file=APP_ROOT/name
        if not file.is_file():continue
        local=file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else name
        reference=local.startswith('Screenshot ') or local=='Proyecto-Integrado-2026-II.pdf'
        if local.startswith('qa/scripts/'):reason='Automatización, validación, medición y regeneración reproducible'
        elif local.startswith('test/'):reason='Pruebas nativas de QA y reporte de resultados; no altera negocio'
        elif local.startswith('qa/reports/'):reason='Reporte o evidencia auténtica de la ejecución o inspección'
        elif local.startswith('docs/'):reason='Entregable académico o matriz editable derivada de fuentes'
        elif local.startswith('.github/'):reason='Integración continua preparada; no se ejecutó push'
        elif local.startswith('.qa-runtime/'):reason='Exclusión de herramientas y dependencias descargadas'
        elif reference:reason='Archivo de referencia añadido y trasladado por el usuario; conservado sin modificación'
        else:reason='Configuración, instrumento o datos sintéticos exclusivos de QA'
        records.append(dict(archivo=name,accion='Referencia del usuario' if reference else 'Creado',justificacion=reason,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    stamp=datetime.now(timezone(timedelta(hours=-6))).isoformat()
    lines=['# Registro de cambios de QA','',f'Actualizado: {stamp}.', '', 'Rama: qa-auditoria-integral. Línea base:789565ea61bae6a84cc8d9ae3be871f601f4a2d1. El inventario completo está en Registro_Cambios_QA.csv. No se realizaron commits,push,merge nireescritura de historial.', '', 'Los342 archivos originales se comprueban mediante SHA256 en qa/reports/baseline/baseline.json e integrity.json. Ningún archivo original fue modificado. Los cambios son adiciones de pruebas,configuración deQA,instrumentos,reportes ydocumentación.', '', 'Ajustes del arnés: escape de espacios de DATABASE_URL; bundle unitario separado para métodos aislados; carga nativa con RI_FORCE_PATH_FOR_DLL; búsqueda absoluta de ejecutables en Windows; doble de reorder compatible con keywords; identificador de Minitest corregido para conservar resultados; Brakeman secuencial para Windows. Ningún ajuste cambió los resultados esperados congelados.', '', 'Soporte de entorno: Ruby4.0.5 ygemas en .qa-runtime; MSYS2 base temporal fuera de rutas con@. Se conserva una unión temporal al proyecto como diagnóstico de globs; no cambia archivos. El toolchain no pudo descargarse desde los espejos. Runtimes,cachés yDB están excluidos deGit; los reportes originales por corrida permanecen disponibles.', '', 'La notación de variables de métricas se precisó sin cambiar fórmulas,umbrales nioráculos de qa/data/design.json. Las observaciones automáticas no se convierten en defectos confirmados sin clasificación.', '', '| Grupo | Archivos inventariados |','|---|---|']
    from collections import Counter
    lines[10:10]=['Traslado solicitado por el usuario: docs/, qa/, test/, .qa-runtime/ y las referencias están ahora dentro de Entregables/. Se actualizaron las rutas del arnés y la documentación; app/, config/, db/ y los Gemfile originales permanecen en la raíz. GitHub Actions permanece en .github/ y ejecuta desde Entregables. Los reportes históricos y los oráculos congelados conservan su contenido.', '']
    for group,n in sorted(Counter(r['archivo'].split('/')[0] for r in records).items()):lines.append(f'| {group} | {n} |')
    (DOCS/'Registro_Cambios_QA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for record in records:
        if APP_ROOT/record['archivo']==DOCS/'Registro_Cambios_QA.csv':
            record['sha256']=''
            record['justificacion']+='; hash propio omitido para evitar autorreferencia'
        elif APP_ROOT/record['archivo']==DOCS/'Registro_Cambios_QA.md':
            record['sha256']=hashlib.sha256((APP_ROOT/record['archivo']).read_bytes()).hexdigest()
    csvwrite(DOCS/'Registro_Cambios_QA.csv',records)
    print('Added/reference files:',len(records),'; original tracked modifications:',subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).strip() or 'none')


if __name__=='__main__':main()
