"""Preserve academic source metadata and text; read-only with respect to sources."""
import hashlib,json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from pypdf import PdfReader
from design import ROOT,APP_ROOT,csvwrite


def main():
    course=APP_ROOT.parents[1];downloads=Path.home()/'Downloads';out=ROOT/'qa/reports/sources';out.mkdir(exist_ok=True)
    principal=next((p for p in [ROOT/'Proyecto-Integrado-2026-II.pdf',APP_ROOT/'Proyecto-Integrado-2026-II.pdf',APP_ROOT.parent/'Proyecto-Integrado-2026-II.pdf'] if p.is_file()),ROOT/'Proyecto-Integrado-2026-II.pdf')
    sources=[principal,course/'Apuntes_4.6_Ejercicios_de_Pruebas_estaticas.pdf',course/'Metricas/Apuntes_04_Metricas_-_calidad_de_software_(v2)_[Repaired].pdf',downloads/'Apuntes_7.0_Laboratorio_pruebas_de_Integracion.pdf',course/'APIs_Lab/Laboratorio de pruebas de integración.pdf']
    manifest=[]
    for i,p in enumerate(sources,1):
        if not p.exists():continue
        reader=PdfReader(p)
        text='\n'.join(f'=== PÁGINA {j+1} ===\n'+(page.extract_text(extraction_mode='layout') or '') for j,page in enumerate(reader.pages))
        if i>1:
            import re
            text='\n'.join('[Línea de ejemplo con credenciales omitida]' if re.search(r'password\s*[:=]|contraseña\s*[:=]|\b[A-Z_]*(?:TOKEN|SECRET|API_KEY)\s*[:=]',line,re.I) else line for line in text.splitlines())
        target=out/f'Fuente_{i:02}.txt';target.write_text(text,encoding='utf-8')
        manifest.append(dict(id=f'SRC-{i:02}',nombre=p.name,paginas=len(reader.pages),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),extraction=str(target.relative_to(ROOT)),uso='Enunciado principal; lectura completa y revisión visual' if i==1 else 'Referencia metodológica; no impone obligaciones del proyecto'))
    xlsx=course/'pruebas de sistema/Ejercicio_de_pruebas_sistema_23_Oct.xlsx'
    if xlsx.exists():
        with ZipFile(xlsx) as z:
            ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            shared=[]
            if 'xl/sharedStrings.xml' in z.namelist():
                shared=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
            strings=[]
            for item in z.namelist():
                if item.startswith('xl/worksheets/sheet') and item.endswith('.xml'):
                    root=ET.fromstring(z.read(item))
                    for row in root.findall('.//s:row',ns)[:2]:
                        for c in row.findall('s:c',ns):
                            value=c.find('s:v',ns)
                            if value is not None:strings.append(shared[int(value.text)] if c.get('t')=='s' else value.text)
        (out/'Referencia_Casos_XLSX.json').write_text(json.dumps({'file':xlsx.name,'headers_only':strings[:11],'use':'Solo formato metodológico; filas con datos y credenciales excluidas'},ensure_ascii=False,indent=2),encoding='utf-8')
        manifest.append(dict(id='SRC-XLSX',nombre=xlsx.name,paginas='No aplica',sha256=hashlib.sha256(xlsx.read_bytes()).hexdigest(),extraction='qa/reports/sources/Referencia_Casos_XLSX.json',uso='Formato metodológico de casos'))
    csvwrite(out/'Fuentes.csv',manifest)
    print(json.dumps(manifest,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
