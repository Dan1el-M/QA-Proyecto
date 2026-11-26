"""Rebuild the editable Word report from source prose, matrices and real evidence."""
import csv,json,re,shutil
from datetime import datetime
from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION_START,WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches,Pt,RGBColor
from design import ROOT,DOCS,J,V,C


def rows(name):
    path=DOCS/name
    return list(csv.DictReader(path.open(encoding='utf-8-sig',newline=''))) if path.exists() else []


def compact_defects(value):
    identifiers=value.split(';')
    if len(identifiers)<7:return value
    if not all(re.fullmatch(r'DEF-\d+',item.strip()) for item in identifiers):return value
    numbers=sorted(set(int(item.strip()[4:]) for item in identifiers));groups=[];start=last=numbers[0]
    for number in numbers[1:]+[None]:
        if number is not None and number==last+1:last=number;continue
        groups.append(f'DEF-{start:03} a DEF-{last:03}' if last>start else f'DEF-{start:03}')
        if number is not None:start=last=number
    return '; '.join(groups)


def clean(text):
    text=str(text)
    # Repair spacing in authored prose while preserving identifiers, paths and quoted code.
    joined_y='BundlerAudit CSRF JSON Lighthouse No P03 Python RNF accesibilidad actualiza bloqueos candidatos carga commit compatibilidad confirmación conservando conservar corrección custodia datos declara desarrollo deuda documentación duplicación el estadísticas evidencia evidencias formularios gestión guardas la las los máximo mediciones métricas mantenedoras no nivel orden pantallas personas podio podium presentación problemas procedimiento pruebas recomendaciones recomendación recorrer reducir regenerar regresión reportan reportes responsable resultados revisión riesgo ruta se servicios su tiempo tipos un una ubicaciones vacíos volver'.split()
    for word in sorted(joined_y,key=len,reverse=True):
        text=re.sub(r'\by(?='+re.escape(word)+r'\b)','y ',text)
    for source,target in {'muestranfecha':'muestran fecha','niaprobación':'ni aprobación','niresultados':'ni resultados','nitransición':'ni transición','nicomentarios':'ni comentarios','porlíneas':'por líneas','porlínea':'por línea','vacíosde':'vacíos de','estimacióncuando':'estimación cuando','laexposición':'la exposición','preguntaGQM':'pregunta GQM','conformidadWCAG':'conformidad WCAG','epersistencia':'e persistencia','einterfaces':'e interfaces','einclusión':'e inclusión','eintegración':'e integración','ofallo':'o fallo','oabandono':'o abandono','ovisualizaciones':'o visualizaciones','ointegridad':'o integridad','oconsultadas':'o consultadas','ono aplicables':'o no aplicables','ola masa':'o la masa','pruebasprioritarias':'pruebas prioritarias','respuestasHTTP':'respuestas HTTP','conP01':'con P01','paraT1':'para T1','paraT2':'para T2','del torneo':'del torneo','deltorneo':'del torneo','persistenciaSQLite':'persistencia SQLite','ypruebasde':'y pruebas de','contraCDN':'contra CDN'}.items():text=text.replace(source,target)
    text=re.sub(r'\b(Ruby|Rails|Bundler|FIFA|contempla|constituyen|escalas|originales|página|partidos|partido|superan|calcula|Aprobación|avance|Cobertura|Porcentaje|Razón|Tasa|Éxito|previo|son|es|alcance|como|commit|el|en|Los|a|que|bandas|Tras|devolver|rondas)(?=\d)',r'\1 ',text)
    for source,target in {'einterpretar':'e interpretar','yrazón':'y razón','ylínea':'y línea','deDLL':'de DLL','BundlerAudit':'Bundler Audit','ydb':'y db'}.items():text=text.replace(source,target)
    text=re.sub(r'\by(?=\d)','y ',text)
    text=text.replace('de1a5','de 1 a 5').replace('2minutos','2 minutos').replace('4minutos','4 minutos')
    text=re.sub(r'(?<=[A-Za-záéíóúñ])(?=\((?:ISO|Basili|Escuela|W3C|Safety|s\.|README|202\d))',' ',text)
    text=re.sub(r',(?=\S)',', ',text)
    text=re.sub(r';(?=\S)','; ',text)
    text=re.sub(r'(?<=[A-Za-záéíóúñ0-9])(?=\((?:ISO|Basili|Escuela|W3C|Safety|s\.|README|202\d))',' ',text)
    text=re.sub(r'\b(pp?\.)(?=\d)',r'\1 ',text)
    text=text.replace('ISO/IEC250','ISO/IEC 250').replace('ISO/IEC/IEEE29148','ISO/IEC/IEEE 29148').replace('WCAG2.2','WCAG 2.2')
    replacements={'suautoría':'su autoría','delauditoría':'de la auditoría','laautoría':'la autoría','deauditoría':'de auditoría','deQA':'de QA','elrepositorio':'el repositorio','laauditoría':'la auditoría','deSonarQube':'de SonarQube','deWCAG':'de WCAG','deaccesibilidad':'de accesibilidad','enla':'en la','deintegración':'de integración','sinrealizar':'sin realizar','la aplicación evaluadasin':'la aplicación evaluada sin','de regresión.':'de regresión.','reproducirel':'reproducir el','nivelespertinentes':'niveles pertinentes','riesgosfuturos':'riesgos futuros','dela línea':'de la línea','degoles':'de goles','de los nivelesaplicables':'de los niveles aplicables','y15':'y 15'}
    for a,b in replacements.items():text=text.replace(a,b)
    text=re.sub(r'\b(de|del|los|las|con|a|en|por|entre|hasta)(?=\d)',r'\1 ',text)
    text=re.sub(r'\by(?=(?:el|la|los|las|un|una|su|sus|datos|evidencia|resultados|seguridad|accesibilidad|rendimiento|métricas|pruebas|anexos|trazas|configuración|vistas|prioridad|entorno|losdatos|guardar)\b)','y ',text)
    for a,b in {'laauditoría':'la auditoría','lasvalidaciones':'las validaciones','nicomentario':'ni comentario','nivelesaplicables':'niveles aplicables','residual.':'residual.','sinrealizar':'sin realizar','de laauditoría':'de la auditoría','laspersonas':'las personas','asustareas':'a sus tareas','porintegrante':'por integrante','de laaplicación':'de la aplicación','enel':'en el','delpipeline':'del pipeline','sin modificar':'sin modificar','decasos':'de casos','declararconformidad':'declarar conformidad','reproducirel':'reproducir el','de laauditoría':'de la auditoría','intervenciónposterior':'intervención posterior'}.items():text=text.replace(a,b)
    return text


class Report:
    def __init__(self):
        self.doc=Document();self.table_number=0;self.figure_number=0;self.manifest=[];self.deferred={};self.rendering_annex=False;self.skip_next_chapter_break=False
        section=self.doc.sections[0];section.page_width=Inches(8.5);section.page_height=Inches(11)
        section.top_margin=section.bottom_margin=section.left_margin=section.right_margin=Inches(1)
        for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
            style=self.doc.styles[name];style.font.name='Arial';style.font.color.rgb=RGBColor(0,0,0)
            style._element.get_or_add_rPr().rFonts.set(qn('w:ascii'),'Arial');style._element.get_or_add_rPr().rFonts.set(qn('w:hAnsi'),'Arial')
        normal=self.doc.styles['Normal'];normal.font.size=Pt(12);normal.paragraph_format.line_spacing=1.5
        language=OxmlElement('w:lang');language.set(qn('w:val'),'es-CR');normal._element.get_or_add_rPr().append(language)
        normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        for name in ['TOC 1','TOC 2','Table of Figures']:
            style=self.doc.styles[name] if name in self.doc.styles else self.doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
            style.base_style=normal;style.font.name='Arial';style.font.size=Pt(12);style.font.color.rgb=RGBColor(0,0,0)
            style.paragraph_format.line_spacing=1.5;style.paragraph_format.space_after=Pt(0);style.paragraph_format.space_before=Pt(0)
        for name,size in [('Title',18),('Heading 1',14),('Heading 2',12),('Heading 3',12)]:
            s=self.doc.styles[name];s.font.size=Pt(size);s.font.bold=True;s.paragraph_format.keep_with_next=True
            s.paragraph_format.space_before=Pt(12);s.paragraph_format.space_after=Pt(6)
        self.doc.styles['Caption'].font.size=Pt(10)
        footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
        self.field(footer,'PAGE','1')
        settings=self.doc.settings.element;update=OxmlElement('w:updateFields');update.set(qn('w:val'),'true');settings.append(update)
        compatibility=settings.find(qn('w:compat'))
        if compatibility is None:compatibility=OxmlElement('w:compat');settings.append(compatibility)
        compatibility.append(OxmlElement('w:doNotExpandShiftReturn'))
        self.doc.core_properties.title='Proyecto Integrado de Auditoría y Validación de Sistemas de Información'
        self.doc.core_properties.author=f'{J}; {V}; {C}'
        self.doc.core_properties.subject='Evaluación de Mundial-POO; IC-6831'
    def field(self,p,instruction,cached):
        field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),instruction)
        run=OxmlElement('w:r');text=OxmlElement('w:t');text.text=str(cached);run.append(text);field.append(run);p._p.append(field)
    def para(self,text='',style=None):return self.doc.add_paragraph(clean(text),style)
    def heading(self,text,level=1):return self.doc.add_heading(clean(text),level)
    def orientation(self,landscape):
        s=self.doc.add_section(WD_SECTION_START.NEW_PAGE)
        s.orientation=WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
        s.page_width=Inches(11 if landscape else 8.5);s.page_height=Inches(8.5 if landscape else 11)
        if not landscape:self.skip_next_chapter_break=True
    def table(self,title,headers,data,widths=None,size=10.5):
        self.table_number+=1;n=self.table_number
        p=self.para(f'La Tabla {n} presenta {title[0].lower()+title[1:]}.');p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(6)
        cap=self.doc.add_paragraph(style='Caption');cap.paragraph_format.keep_with_next=True
        cap.add_run('Tabla ');self.field(cap,'SEQ Tabla \\* ARABIC',n);cap.add_run('. '+clean(title))
        table=self.doc.add_table(rows=1,cols=len(headers));table.autofit=False
        if widths:
            for column,width in zip(table.columns,widths):column.width=Inches(width)
        header=table.rows[0];repeat=OxmlElement('w:tblHeader');header._tr.get_or_add_trPr().append(repeat)
        for i,h in enumerate(headers):header.cells[i].text=clean(h)
        for data_row in data:
            cells=table.add_row().cells
            for i,value in enumerate(data_row):cells[i].text=clean(value)
        borders=OxmlElement('w:tblBorders')
        for edge in ['top','left','bottom','right','insideH','insideV']:
            item=OxmlElement('w:'+edge);item.set(qn('w:val'),'single');item.set(qn('w:sz'),'4');item.set(qn('w:color'),'D9D9D9');borders.append(item)
        table._tbl.tblPr.append(borders)
        for ri,row in enumerate(table.rows):
            cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
            for ci,cell in enumerate(row.cells):
                if widths:cell.width=Inches(widths[ci])
                tcpr=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E6E6E6' if ri==0 else 'FFFFFF');tcpr.append(shade)
                margins=OxmlElement('w:tcMar')
                for edge in ['top','left','bottom','right']:
                    item=OxmlElement('w:'+edge);item.set(qn('w:w'),'85');item.set(qn('w:type'),'dxa');margins.append(item)
                tcpr.append(margins)
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3)
                    p.alignment=WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.keep_with_next=ri==0
                    for run in p.runs:run.font.name='Arial';run.font.size=Pt(size);run.font.bold=ri==0
        return n
    def figure(self,number,title,path,source,pending=''):
        if number>=9 and not self.rendering_annex:
            self.deferred[number]=(title,path,source,pending)
            return
        intro=self.para(f'La Figura {number} muestra {title[0].lower()+title[1:]}.');intro.paragraph_format.keep_with_next=True
        if path is None or not path.is_file():
            alternate=ROOT/f'qa/evidence/Figura_{number:03}.png'
            if alternate.is_file():path=alternate
        exists=path is not None and path.is_file()
        if exists:
            section=self.doc.sections[-1];width=(section.page_width-section.left_margin-section.right_margin)/914400
            p=self.doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
            from PIL import Image
            with Image.open(path) as im:iw,ih=im.size
            maximum_height=(section.page_height-section.top_margin-section.bottom_margin)/914400-1.6
            picture_width=min(width,8,maximum_height*iw/ih)
            run=p.add_run();run.add_picture(str(path),width=Inches(picture_width))
            pic=run._r.xpath('.//wp:docPr')[0];pic.set('descr',title)
        else:self.para('EVIDENCIA PENDIENTE. '+pending).paragraph_format.keep_with_next=True
        cap=self.doc.add_paragraph(style='Caption');cap.paragraph_format.keep_with_next=True;cap.add_run('Figura ');self.field(cap,'SEQ Figura \\* ARABIC',number);cap.add_run('. '+clean(title))
        self.para('Fuente: '+source)
        self.manifest.append(dict(number=number,title=title,path=str(path.relative_to(ROOT)) if exists else '',pending=not exists,instructions=pending))
    def csvtable(self,name,title,columns,headers=None,widths=None):
        data=rows(name);return self.table(title,headers or columns,[[r.get(k,'') for k in columns] for r in data],widths)


def result_visuals():
    from visuals import bars
    from recalculate_metrics import human_data
    for prefix,number,title in [('unit',12,'Resultados unitarios'),('integration',13,'Resultados de integración'),('security',16,'Controles de seguridad')]:
        files=sorted((ROOT/'qa/reports/runs').glob('*/'+prefix+'.json'))
        if files:
            from collections import Counter
            r=json.loads(files[-1].read_text(encoding='utf-8'));bars(number,title,dict(Counter(x['status'] for x in r)),str(files[-1].relative_to(ROOT)))
    human=human_data()
    if 'acceptance' in human:
        from collections import Counter
        bars(18,'Decisiones reales de aceptación',dict(Counter(r['estado'] for r in human['acceptance']['rows'])),human['acceptance']['source'])
    if 'usability' in human:
        r=human['usability']['rows'];bars(19,'Tiempo medio observado por tarea',{t:sum(float(x['segundos']) for x in r if x['tarea']==t)/sum(x['tarea']==t for x in r) for t in ['T1','T2','T3'] if any(x['tarea']==t for x in r)},human['usability']['source'])
    if 'inspection' in human:
        real=human['inspection']['rows']
        bars(20,'Inspección formal confirmada',{'Hallazgos revisados':len(real['decision_por_hallazgo']),'Acciones registradas':len(real['acciones'])},human['inspection']['source'])
    browser=sorted((ROOT/'qa/reports/runs').glob('*/playwright.json'))
    if browser:
        from collections import Counter
        states=[]
        def walk(suite):
            for spec in suite.get('specs',[]):
                for test in spec.get('tests',[]):
                    if test.get('results'):states.append(test['results'][-1]['status'])
            for child in suite.get('suites',[]):walk(child)
        for suite in json.loads(browser[-1].read_text(encoding='utf-8')).get('suites',[]):walk(suite)
        if states:bars(14,'Resultados del runner de sistema',dict(Counter(states)),str(browser[-1].relative_to(ROOT)))
    perf=rows('Resultados_Rendimiento.csv')
    if perf:bars(15,'P95 observado por escenario y carga',{r['escenario']+' VU'+r['carga']:max(float(x['p95_ms']) for x in perf if x['escenario']==r['escenario'] and x['carga']==r['carga'])/1000 for r in perf},'docs/Resultados_Rendimiento.csv; segundos')
    axe=sorted((ROOT/'qa/reports/runs').glob('*/axe-ACC-*.json'))
    if axe:bars(17,'Hallazgos automáticos de accesibilidad',{p.stem:len(json.loads(p.read_text(encoding='utf-8'))['violations']) for p in axe[-3:]},'Reportes axe por pantalla; requiere ratificación manual')


def main():
    result_visuals();content=json.loads((DOCS/'Contenido_Academico.json').read_text(encoding='utf-8'))
    summary=json.loads((ROOT/'qa/reports/summary.json').read_text(encoding='utf-8'))
    design=json.loads((ROOT/'qa/data/design.json').read_text(encoding='utf-8'))
    report=Report();d=report.doc
    for text in ['Instituto Tecnológico de Costa Rica','Escuela de Computación','Ingeniería en Computación','IC-6831 Aseguramiento de la Calidad del Software']:
        p=report.para(text);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p=report.para('Proyecto Integrado de Auditoría y Validación de Sistemas de Información','Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p=report.para('Sistema evaluado: Mundial-POO');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for text in ['Profesora: Alicia Salazar Hernández',J,V,C,'II Semestre 2026','Fecha de entrega: 30 de noviembre de 2026']:
        p=report.para(text);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for title,field in [('Tabla de contenidos','TOC \\o "1-2" \\h \\z \\u'),('Índice de figuras','TOC \\h \\z \\c "Figura"'),('Índice de tablas','TOC \\h \\z \\c "Tabla"')]:
        heading=report.para(title);heading.paragraph_format.page_break_before=True
        heading.paragraph_format.keep_with_next=True;heading.runs[0].bold=True;heading.runs[0].font.size=Pt(14)
        report.field(report.para(),field,'Actualizar campos en Word')
    for number,(title,sections) in enumerate(content['chapters'],1):
        heading=report.heading(f'{number}. {title}')
        heading.paragraph_format.page_break_before=not report.skip_next_chapter_break
        report.skip_next_chapter_break=False
        intros={1:'La ficha identifica el producto,la procedencia yel entorno de la auditoría.',7:'El modelo conecta riesgos,requerimientos,preguntas ymétricas para interpretar la evidencia.',13:'Los registros siguientes conservan el diseño previo ylos resultados observados sin alterar el oráculo.',17:'Este capítulo presenta cantidades derivadas del catálogo ylos reportes originales.',24:'Se incluyen únicamente referencias identificadas oconsultadas de forma verificable.'}
        introductions={2:'El registro de un marcador repercute en estadísticas,clasificación ypodio. Esta auditoría sigue ese encadenamiento para evaluar la calidad del producto.',3:'Los objetivos delimitan la evaluación ylas decisiones que debe sustentar la evidencia.',4:'La descripción relaciona las funciones documentadas con los componentes ylas interfaces realmente presentes en la línea base.',5:'El alcance prioriza las reglas einterfaces cuya falla afecta la integridad yel uso del torneo; cada exclusión conserva su riesgo residual.',6:'Se describe la arquitectura existente yel diseño de la infraestructura de auditoría,con diagramas de fuentes verificables.',8:'El plan establece recursos,orden de trabajo,criterios de control ygestión de datos para ejecutar la auditoría de manera reproducible.',9:'La selección de herramientas responde al lenguaje Ruby,la interfaz Rails ylos tipos de evidencia exigidos; su ejecución se acredita mediante reportes.',10:'El procedimiento utiliza un ambiente test aislado ydatos sintéticos para instalar,ejecutar yrecorrer el producto sin alterar bases existentes.',11:'La revisión estática contrasta especificación,código yreportes de herramientas antes de interpretar sus riesgos de mantenimiento.',12:'Los niveles ytipos de prueba aportan evidencia complementaria. Sus resultados ybloqueos se distinguen de las actividades únicamente preparadas.',14:'La automatización conserva reportes por corrida yactualiza el informe; la validación humana mantiene instrumentos yresultados separados.',15:'La matriz permite recorrer desde una obligación hasta sus pruebas,resultados,defectos yresponsable,yvolver desde una evidencia hacia su origen.',16:'El registro distingue hallazgos confirmados,candidatos automáticos yproblemas del entorno para evitar conclusiones que excedan la evidencia.',18:'Los valores se calculan a partir de reportes yformularios; su interpretación conserva denominadores,umbrales ymediciones pendientes.',19:'La estimación de deuda prioriza problemas únicos ydeclara el costo supuesto,el alcance yla incertidumbre del cálculo.',20:'Los riesgos explican la prioridad de ejecución ylas condiciones necesarias para reducir la exposición después de esta auditoría.',21:'La recomendación integra resultados,defectos yvacíos de validación; una cobertura alta de diseño no sustituye pruebas concluyentes.',22:'Las conclusiones se limitan a la línea base yla evidencia disponible; las recomendaciones ordenan las acciones posteriores.',23:'La asignación conserva las especialidades yla responsabilidad por requerimiento,sin atribuir ejecución personal no confirmada.',25:'Los anexos reúnen fuentes editables,reportes,instrumentos yevidencias auténticas; las reservas pendientes permanecen identificadas.'}
        report.para(intros.get(number,introductions.get(number,'Se presentan los elementos verificables correspondientes a este capítulo.')))
        for sub,(subtitle,text) in enumerate(sections,1):report.heading(f'{number}.{sub}. {subtitle}',2);report.para(text)
        if number==1:
            report.table('Datos de identificación',['Dato','Valor'],[
                ['Población meta','Personas organizadoras y espectadoras; perfiles inferidos de los procesos, sin estudio demográfico'],['Línea base','789565ea61bae6a84cc8d9ae3be871f601f4a2d1'],['Rama de auditoría','qa-auditoria-integral'],['Origen remoto','https://github.com/Dan1el-M/QA-Proyecto'],['RF documentados / seleccionados',f"9 / {summary['rf_selected']}"],['RNF explícitos normalizados / seleccionados',f"3 / {summary['rnf_selected']} (incluye 3 derivados)"],['Perfiles implementados','Sin perfiles diferenciados ni autenticación identificada']],[2.1,4.4])
        elif number==4:
            report.csvtable('Inventario_Requerimientos.csv','Inventario funcional y no funcional',['id','descripcion','procedencia','seleccionado'],['ID','Requerimiento','Origen','Selección'],[.7,3.2,1.3,1.3])
        elif number==5:
            report.csvtable('Alcance.csv','Alcance por requerimiento',['requerimiento','funcionalidad','nivel'],['ID','Funcionalidad y justificación de inclusión','Niveles'],[.7,3.6,2.2])
            report.csvtable('Exclusiones.csv','Exclusiones y riesgo residual',['elemento','motivo','riesgo_residual','aceptacion'],['Elemento','Motivo técnico','Riesgo','Justificación'],[1.4,1.7,1.6,1.8])
        elif number==6:
            report.orientation(True)
            titles=['Arquitectura existente','Componentes existentes','Entidades y relaciones','Flujo de registro de marcador','Estrategia de pruebas propuesta','Gestión de defectos','Automatización e integración continua propuesta','Relación entre modelo,GQM,pruebas ymétricas']
            for i,figtitle in enumerate(titles,1):
                if i>1:d.add_page_break()
                report.figure(i,figtitle,DOCS/f'diagramas/Figura_{i:03}.png','Elaboración a partir de archivos reales y del diseño de QA; fuente específica en la imagen.')
            report.orientation(False)
        elif number==7:
            report.csvtable('Modelo_Calidad.csv','Características seleccionadas,prioridad yevidencia',['caracteristica','proposito','prioridad','requerimientos','metricas'],['Característica','Propósito','Prioridad','Requerimientos','Métricas'],[1.25,2.05,.8,1.2,1.2])
            report.csvtable('GQM.csv','Objetivos y preguntas GQM',['objetivo_id','pregunta_id','pregunta','metricas'],['Objetivo','Pregunta','Texto','Métricas'],[.8,1.1,3.3,1.3])
            for g in {q['objetivo_id']:q['objetivo'] for q in design['gqm']}.items():report.para(g[0]+': '+g[1])
            results={m['id']:m for m in rows('Resultados_Metricas.csv')}
            for metric in design['metrics']:
                report.heading(metric['id']+'. '+metric['nombre'],3)
                labels={'id':'Identificador','nombre':'Nombre','caracteristica':'Característica ISO/IEC 25010:2023','objetivo':'Objetivo','preguntas':'Preguntas GQM','formula':'Fórmula','variables':'Definición de variables','unidad':'Unidad','escala':'Escala de medición','herramienta':'Herramienta','metodo':'Método de recolección','frecuencia':'Frecuencia','justificacion':'Justificación de selección','umbral_general':'Umbral general','total':'Aceptación total','parcial':'Aceptación parcial','rechazo':'Rechazo','decision':'Decisión asociada','responsable':'Responsable asignado','fuente':'Fuente de datos','alcance':'Alcance','exclusiones':'Exclusiones','limitaciones':'Limitaciones','resultado':'Resultado obtenido','estado':'Estado de evaluación','interpretacion':'Interpretación','evidencia':'Evidencia'}
                details=rows('Fichas_Metricas.csv')
                expanded=next((r for r in details if r['id']==metric['id']),metric)
                pairs=[(labels.get(key,key),value) for key,value in expanded.items()]+[(labels[key],results[metric['id']][key]) for key in ['resultado','estado','interpretacion','evidencia']]
                report.table('Ficha '+metric['id'],['Campo','Especificación'],pairs,[1.8,4.7])
        elif number==8:
            report.table('Cronograma planificado antes de la entrega',['Período','Actividad prevista','Criterio de cierre'],[
                ['25 noviembre','Fuentes,línea base,diseño y preparación','Oráculos congelados y ambiente identificado'],['26–27 noviembre','Ejecución técnica y clasificación','Reportes auténticos y defectos trazados'],['27–28 noviembre','Sesiones humanas y revisión manual','Participación real y formularios confirmados'],['29 noviembre','Integración,regeneración y revisión','Consistencia de métricas y figuras'],['30 noviembre','Revisión académica y entrega','Cumplimiento verificado sin pendientes obligatorios']],[1.1,2.7,2.7])
        elif number==9:
            executions=json.loads((ROOT/'qa/reports/executions.json').read_text(encoding='utf-8'))
            latest={r['name']:r for r in executions}
            report.table('Estado de ejecución de herramientas',['Trabajo','Código','Evidencia original'],[[k,str(v.get('exit_code')),v.get('log','') or v.get('reason','')] for k,v in latest.items()],[1.4,.6,4.5])
        elif number==11:
            report.csvtable('Revision_Requerimientos.csv','Lista de cotejo y propuestas de revisión',['requerimiento','hallazgo','propuesta'],['RF','Deficiencia de especificación','Propuesta a ratificar'],[.6,2.2,3.7])
            report.figure(11,'Métodos con mayor complejidad',DOCS/'diagramas/Figura_011.png','Reporte AST Prism conservado por corrida.','Ejecutar --only static.')
        elif number==12:
            for fig,title2,filename,cmd in [(12,'Resultado de pruebas unitarias','Figura_012.png','--only unit'),(13,'Resultado de integración','Figura_013.png','--only integration'),(14,'Evidencia de recorrido E2E','Figura_014.png','--only e2e'),(15,'P95 por escenario y carga','Figura_015.png','--only performance --load'),(16,'Verificaciones de seguridad','Figura_016.png','--only security'),(17,'Evaluación de accesibilidad','Figura_017.png','--only accessibility'),(18,'Aceptación con personas externas','Figura_018.png','importar qa/acceptance/resultados.csv'),(19,'Tiempos de usabilidad reales','Figura_019.png','importar qa/usability/resultados.csv'),(20,'Inspección formal confirmada','Figura_020.png','importar qa/static/inspeccion.json')]:
                command='python qa/scripts/import_human.py '+cmd.removeprefix('importar ') if cmd.startswith('importar ') else 'bash qa/scripts/run_all.sh '+cmd
                report.figure(fig,title2,DOCS/'diagramas'/filename,'Reportes originales o formularios confirmados.',f'Desde Entregables: {command}. Para actividades humanas, realizar primero la sesión y completar el instrumento. Guardar evidencia en qa/evidence; consultar PENDIENTES_EVIDENCIAS.md.')
        elif number==13:
            for case in rows('Casos_de_Prueba.csv'):
                report.heading(case['id']+'. '+case['nombre'],3)
                data=[['Objetivo y requerimiento',case['objetivo']+'; '+case['requerimiento']],['Tipo,nivel,técnica y prioridad',case['tipo']+'; '+case['nivel']+'; '+case['tecnica']+'; '+case['prioridad']],['Característica y responsable',case['caracteristica']+'; '+case['responsable']],['Precondiciones y datos',case['precondiciones']+'\nDatos: '+case['datos']],['Pasos / función',case['pasos']+'\n'+case['funcion']],['Resultado esperado',case['esperado']],['Resultado obtenido y estado',case['estado']+'; '+case['obtenido'][:1700]],['Evidencia y defecto',case['evidencia']+'\nDefecto: '+(compact_defects(case['defecto']) or 'Sin asociación confirmada')],['Postcondiciones y métrica',case['postcondiciones']+'; '+case['metrica']],['Implementación y ejecución',case['implementacion']+'\n'+case['comando']],['Fecha,ambiente y versión',(case['fecha'] or 'Sin ejecución confirmada')+'; '+case['ambiente']+'; '+case['version']]]
                report.table('Caso '+case['id'],['Campo','Detalle'],data,[1.7,4.8])
        elif number==14:
            report.figure(24,'Ejecución remota de GitHub Actions',ROOT/'qa/evidence/Figura_024_CI.png','GitHub Actions del repositorio; ejecución sujeta a publicación del equipo.','Después de publicar por decisión del equipo,ejecutar workflow_dispatch y conservar captura auténtica Figura_024_CI.png.')
        elif number==15:
            report.orientation(True)
            trace=rows('Matriz_Trazabilidad.csv')
            report.para('Los rangos de defectos incluyen todos los identificadores entre sus extremos. El CSV conserva cada vínculo individual y el registro distingue candidatos de hallazgos confirmados.')
            report.table('Matriz integral bidireccional',['RF/RNF','Característica','Caso','Tipo / nivel','Automatizada','Resultado','Defecto','Responsable'],[[compact_defects(r[k]) if k=='defecto' else r[k] for k in ['requerimiento','caracteristica','caso','tipo_nivel','prueba_automatizada','resultado','defecto','responsable']] for r in trace],[.65,1.05,.7,1.3,1.1,.85,.75,1.6],size=10)
            report.orientation(False)
        elif number==16:
            all_defects=rows('Registro_Defectos.csv')
            for defect in [r for r in all_defects if r['tipo'] not in ['Anomalía automática candidata','Dependencia vulnerable candidata']]:
                report.heading(defect['id']+'. '+defect['titulo'],3)
                report.para(f"{defect['tipo']}; {defect['confirmacion']}; severidad {defect['severidad']}; prioridad propuesta {defect['prioridad']}; estado {defect['estado']}.")
                report.para(defect['descripcion']);report.para('Reproducción: '+defect['pasos'])
                report.para('Esperado: '+defect['esperado']+' Actual: '+defect['actual'])
                report.para('Evidencia: '+defect['evidencia']+'. Requerimiento: '+defect['requerimiento']+'. Responsable: '+defect['responsable'])
                report.para('Impacto y recomendación: '+defect['recomendacion'])
            candidates=[r for r in all_defects if r['tipo'] in ['Anomalía automática candidata','Dependencia vulnerable candidata']]
            if candidates:
                report.table('Candidatos de herramientas pendientes de clasificación',['ID','Observación','Ubicación / evidencia','Estado'],[[r['id'],r['titulo'],r['archivo']+':'+str(r['linea']),r['estado']] for r in candidates],[.6,2.1,2.5,1.3])
                report.para('Los campos completos de reproducción,impacto,oráculo,evidencia,responsable yrecomendación se conservan en Registro_Defectos.csv. Hallazgos_Herramientas.csv conserva cada observación individual,agrupada sin duplicar defectos funcionales.')
            report.figure(10,'Hallazgos por severidad',DOCS/'diagramas/Figura_010.png','Registro_Defectos.csv; clasificación de candidatos explícita en el registro.')
        elif number==17:
            report.table('Resumen del catálogo y resultados',['Indicador','Cantidad'],[[k,v] for k,v in [('Diseñados',summary['designed']),('Implementados',summary['implemented']),('Automatizados',summary['automated']),('Concluyentes',summary['conclusive']),*summary['states'].items(),('RF con evidencia aprobada',summary['rf_with_passed_evidence'])]],[4.5,2])
            for group,label in [('by_level','nivel'),('by_characteristic','característica'),('by_owner','responsable'),('by_requirement','requerimiento')]:
                report.table('Resultados por '+label,[label,'Aprobado','Fallido','Bloqueado','No ejecutado'],[[k,*[v.get(s,0) for s in ['Aprobado','Fallido','Bloqueado','No ejecutado']]] for k,v in summary[group].items()],[2.9,.9,.9,.9,.9])
            report.figure(9,'Estados reales del catálogo',DOCS/'diagramas/Figura_009.png','qa/reports/summary.json; incluye bloqueos y actividades no ejecutadas.')
        elif number==18:
            report.csvtable('Resultados_Metricas.csv','Resultados de las trece métricas',['id','resultado','estado','interpretacion'],['Métrica','Valor','Evaluación','Interpretación'],[.7,.9,1.2,3.7])
        elif number==19:
            report.csvtable('Deuda_Tecnica.csv','Inventario priorizado de deuda',['id','defecto','descripcion','minutos','prioridad'],['ID','Hallazgo','Descripción','Minutos estimados','Prioridad'],[.6,.7,3.2,1,1])
        elif number==20:
            report.orientation(True)
            report.csvtable('Matriz_Riesgos.csv','Exposición,controles y tratamiento de riesgos',['id','descripcion','probabilidad','impacto','exposicion','nivel','controles','tratamiento'],['ID','Riesgo','P','I','P×I','Nivel','Control existente','Tratamiento'],[.6,1.6,.3,.3,.4,.7,1.8,3.3])
            report.orientation(False)
        elif number==21:
            report.para('Recomendación actual: '+summary['release']+'.')
            report.para(f"El registro contiene {summary['defects_confirmed']} hallazgos confirmados con procedencia explícita y {summary['security_candidates']} candidatos de seguridad. Hay {summary['metrics_pending']} métricas sin medición suficiente. La revisión humana y los resultados técnicos pendientes deben completarse antes de una decisión definitiva favorable.")
        elif number==23:
            report.table('Asignación consolidada',['Integrante','RF','RNF'],[[J,'RF-03,RF-04','RNF-01'],[V,'RF-01,RF-02','RNF-02'],[C,'RF-05..RF-09','RNF-03,RNF-04']],[3.5,1.5,1.5])
        elif number==24:
            def reference_key(value):
                match=re.match(r'^(.*?)\.\s*\(([^)]+)\)',value)
                return (match.group(1).casefold(),match.group(2)) if match else (value.casefold(),'')
            for reference in sorted(content['references'],key=reference_key):
                reference=clean(reference);p=report.para();p.alignment=WD_ALIGN_PARAGRAPH.LEFT
                match=re.match(r'^(.*?\)\.\s*)(.*?)(\s*\[.*|\.\s+https?://.*|$)',reference)
                if reference.startswith(('Proyecto 4 de POO:','Arquitectura del proyecto')):
                    title,rest=reference.split(' (s. f.).',1)
                    p.add_run(title).italic=True;p.add_run(' (s. f.).'+rest)
                elif match:
                    p.add_run(match.group(1));p.add_run(match.group(2)).italic=True;p.add_run(match.group(3))
                else:p.add_run(reference)
                p.paragraph_format.left_indent=Inches(.5);p.paragraph_format.first_line_indent=Inches(-.5)
        elif number==25:
            for fig,title2,basename in [(21,'Pantalla principal del producto','pantalla_selecciones.png'),(22,'Calendario y tabla de posiciones','pantalla_calendario.png'),(23,'Podio del torneo','pantalla_podio.png')]:
                files=sorted((ROOT/'qa/reports/runs').glob('*/'+basename))
                path=files[-1] if files else ROOT/'qa/evidence'/f'Figura_{fig:03}.png'
                report.figure(fig,title2,path,'Captura auténtica de la instancia local con datos sintéticos.','Ejecutar E2E o abrir la ruta local y guardar el archivo con el nombre establecido en qa/evidence.')
            report.orientation(True)
            report.rendering_annex=True
            for fig,(title2,path,source,pending) in sorted(report.deferred.items()):report.figure(fig,title2,path,source,pending)
            report.csvtable('Inventario_Evidencias.csv','Inventario de evidencia disponible',['id','caso','herramienta','ruta'],['ID','Caso','Herramienta','Ruta'],[.7,.9,1.3,3.6])
    target=DOCS/'Informe_Final_QA_Mundial.docx'
    # Remove inherited paragraph rules, including any rule from the default Title style.
    for element in [d.element,d.styles.element]:
        for border in element.xpath('.//w:pBdr'):border.getparent().remove(border)
    if target.exists():
        backup=ROOT/'qa/reports/backups';backup.mkdir(parents=True,exist_ok=True)
        shutil.copy2(target,backup/(datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.docx'))
    d.save(target)
    (DOCS/'Manifest_Figuras.json').write_text(json.dumps(report.manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Word generated:',target,';',len(d.paragraphs),'paragraphs;',len(d.tables),'tables')


if __name__=='__main__':main()
