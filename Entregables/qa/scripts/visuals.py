"""Editable diagrams and charts derived from real source/report records."""
import csv,json,math
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from design import ROOT,DOCS

FONT=Path('C:/Windows/Fonts/arial.ttf')
BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)


def graph(number,title,nodes,edges,source,node_width=440,node_height=145):
    out=DOCS/'diagramas';out.mkdir(exist_ok=True)
    image=Image.new('RGB',(1700,1020),'white');d=ImageDraw.Draw(image)
    d.text((50,25),title,font=font(35,True),fill='black')
    positions={}
    for key,label,x,y in nodes:
        box=(x,y,x+node_width,y+node_height);positions[key]=box
    for a,b,label in edges:
        aa,bb=positions[a],positions[b]
        if aa[1]==bb[1]:start=(aa[2],(aa[1]+aa[3])/2);end=(bb[0],(bb[1]+bb[3])/2)
        else:start=((aa[0]+aa[2])/2,aa[3]);end=((bb[0]+bb[2])/2,bb[1])
        d.line([start,end],fill='#555555',width=4)
        angle=math.atan2(end[1]-start[1],end[0]-start[0]);arrow=[end,(end[0]-15*math.cos(angle-.4),end[1]-15*math.sin(angle-.4)),(end[0]-15*math.cos(angle+.4),end[1]-15*math.sin(angle+.4))]
        d.polygon(arrow,fill='#555555')
        if label:d.text(((start[0]+end[0])/2+5,(start[1]+end[1])/2-30),label,font=font(21),fill='black')
    for key,label,x,y in nodes:
        d.rounded_rectangle(positions[key],radius=12,fill='#F2F4F6',outline='#444444',width=3)
        lines=label.split('\n');size=32
        while size>14 and (max(d.textlength(t,font=font(size,True)) for t in lines)>node_width-40 or len(lines)*round(size*1.15)>node_height-28):size-=1
        line_height=round(size*1.15);yy=y+(node_height-len(lines)*line_height)/2
        for text in lines:
            width=d.textlength(text,font=font(size,True));d.text((x+(node_width-width)/2,yy),text,font=font(size,True),fill='black');yy+=line_height
    d.text((50,950),'Fuente: '+source,font=font(21),fill='#333333')
    base=out/f'Figura_{number:03}'
    image.save(str(base)+'.png')
    spec={'title':title,'nodes':nodes,'edges':edges,'source':source}
    base.with_suffix('.json').write_text(json.dumps(spec,indent=2,ensure_ascii=False),encoding='utf-8')
    dot='digraph G { rankdir=TB; node [shape=box];\n'
    for key,label,_,_ in nodes:dot+=f'{key} [label={json.dumps(label,ensure_ascii=False)}];\n'
    for a,b,label in edges:dot+=f'{a} -> {b} [label={json.dumps(label,ensure_ascii=False)}];\n'
    base.with_suffix('.dot').write_text(dot+'}\n',encoding='utf-8')


def bars(number,title,values,source):
    out=DOCS/'diagramas';out.mkdir(exist_ok=True)
    im=Image.new('RGB',(1700,850),'white');d=ImageDraw.Draw(im);d.text((45,25),title,font=font(35,True),fill='black')
    maxv=max(values.values(),default=1) or 1
    for i,(label,value) in enumerate(values.items()):
        y=110+i*min(100,600/max(1,len(values)))
        label=str(label);size=32
        while size>20 and d.textlength(label,font=font(size))>650:size-=1
        if d.textlength(label,font=font(size))>650:
            lines=['']
            for char in label:
                if d.textlength(lines[-1]+char,font=font(size))>650:lines.append('')
                lines[-1]+=char
            for row,text in enumerate(lines):d.text((45,y+row*(size+3)),text,font=font(size),fill='black')
        else:d.text((45,y+4),label,font=font(size),fill='black')
        x=720;width=value/maxv*800
        d.rectangle((x,y,x+width,y+40),fill='#516477')
        d.text((x+width+12,y+3),str(round(value,2)),font=font(25,True),fill='black')
    d.text((45,795),'Fuente: '+source,font=font(20),fill='#333333');im.save(out/f'Figura_{number:03}.png')
    (out/f'Figura_{number:03}.json').write_text(json.dumps({'title':title,'values':values,'source':source},indent=2,ensure_ascii=False),encoding='utf-8')


def main():
    graph(1,'Arquitectura existente: solicitud y persistencia',[
      ('browser','Navegador\nHTML y formularios',600,115),('routes','Rutas Rails\nconfig/routes.rb',600,330),
      ('mvc','Controladores y vistas\napp/controllers, app/views',80,555),('business','Modelos y servicios\napp/models, app/services',1120,555),('db','SQLite: cuatro tablas\ngrupo, selección, partido, torneo',600,780)],
      [('browser','routes','HTTP'),('routes','mvc','acción'),('mvc','business','consulta / escritura'),('business','db','Active Record')], 'config/routes.rb; config/database.yml; app/')
    graph(2,'Componentes existentes del negocio',[
      ('controllers','Controladores de resultados\ny fases',490,115),
      ('services','ActualizarEstadisticasSeleccion\nCalcularGanadorPartido\nDeterminarClasificados\nSiguienteRonda',490,400),
      ('classes','Grupo, Seleccion, Partido\ny Torneo',490,720)], [('controllers','services',''),('services','classes','')], 'app/controllers/; app/services/; app/models/',node_width=720,node_height=180)
    graph(3,'Relaciones persistidas del sistema',[
      ('t','torneos\netapa_actual; podio opcional',600,120),('g','grupos\nletra única; torneo opcional',80,420),('m','partidos\nmarcador; equipos; ganador',1120,420),('s','selecciones\ngrupo; puntos; GF; GC; DG',600,750)],
      [('t','g','1 : N'),('t','m','1 : N'),('g','s','1 : N'),('m','s','local / visitante / ganador'),('g','m','1 : N')], 'db/schema.rb; claves foráneas reales')
    graph(4,'Proceso existente: registro de marcador de grupo',[
      ('f','Formulario de calendario\nmarcadores de dos equipos',600,115),('c','PartidosGrupoController\nconversión to_i',600,330),('p','Partido#registrar_resultado!\nvalidación y guardado',600,545),('s','after_save\nrecálculo de estadísticas',600,760)],
      [('f','c','PATCH'),('c','p','2 marcadores'),('p','s','si finalizado y fase_grupos')], 'calendario.html.erb; partidos_grupo_controller.rb; partido.rb')
    graph(5,'Estrategia de QA propuesta',[
      ('risk','Requerimientos y riesgos\noráculos congelados',600,115),('static','Revisión estática\nrequerimientos y código',80,400),('native','Minitest\nunidad e integración',600,400),('browser','Playwright, axe y k6\nsistema y no funcionales',1120,400),('human','Aceptación, usabilidad\ne inspección humana',600,730)],
      [('risk','static',''),('risk','native',''),('risk','browser',''),('native','human','validación complementaria')], 'qa/data/design.json; propuesta de auditoría')
    graph(6,'Proceso de gestión de defectos',[
      ('detect','Detectar y preservar\nreporte, captura o traza',600,115),('triage','Reproducir y clasificar\nseveridad y prioridad',600,330),('record','Registrar y vincular\nRF, caso, evidencia',600,545),('decision','Evaluar riesgo y liberación\ncorrección fuera de auditoría',600,760)],
      [('detect','triage',''),('triage','record','sin duplicar'),('record','decision','')], 'Registro_Defectos.csv; flujo de QA')
    graph(7,'Automatización local e integración continua propuesta',[
      ('entry','run_all.sh\nprerrequisitos y aislamiento',600,115),('jobs','Estática, Minitest\ny navegador local',80,410),('logs','Reportes por corrida\ncódigos de salida y fallos',1120,410),('final','Métricas y trazabilidad\nWord y verificación final',600,740)],
      [('entry','jobs',''),('jobs','logs',''),('logs','final','evidencia auténtica')], 'Entregables/qa/scripts/run_all.py; .github/workflows/qa.yml')
    graph(8,'Modelo de calidad y cadena de evidencia',[
      ('iso','Cinco características\nISO/IEC 25010:2023',600,115),('gqm','Cinco objetivos GQM\ny quince preguntas',600,330),('test','Requerimientos y casos\noráculos y responsables',80,590),('metrics','Trece métricas\numbrales internos',1120,590),('evidence','Reportes y evidencias\ninterpretación y decisión',600,790)],
      [('iso','gqm',''),('gqm','test',''),('gqm','metrics',''),('test','evidence',''),('metrics','evidence','')], 'GQM.csv; Fichas_Metricas.csv; Matriz_Trazabilidad.csv')
    summary=json.loads((ROOT/'qa/reports/summary.json').read_text(encoding='utf-8'))
    bars(9,'Estados reales del catálogo',summary['states'],'qa/reports/summary.json; no equivale a pruebas aprobadas')
    defects=list(csv.DictReader((DOCS/'Registro_Defectos.csv').open(encoding='utf-8-sig')))
    bars(10,'Hallazgos registrados por severidad',dict(Counter(d['severidad'] for d in defects)),'docs/Registro_Defectos.csv; candidatos diferenciados en registro')
    complexity=sorted((ROOT/'qa/reports/runs').glob('*/complexity.json'))
    if complexity:
        data=json.loads(complexity[-1].read_text(encoding='utf-8'))
        if data['count']:
            top=sorted(data['methods'],key=lambda r:r['complexity'],reverse=True)[:6]
            bars(11,'Métodos con mayor complejidad ciclomática',{r['class']+'#'+r['method']:r['complexity'] for r in top},str(complexity[-1].relative_to(ROOT)))


if __name__=='__main__':main()
