"""Complete A/AA applicability instrument. No outcome is prefilled."""
import csv,json
from design import ROOT,csvwrite

CRITERIA=[
('1.1.1','A','Inspeccionar imágenes eiconos en el árbol accesible; comprobar alternativa equivalente ymarcar decorativas.'),
('1.2.1','A','Buscar audio ovideo pregrabado sin pista complementaria; verificar alternativa. Si no existe multimedia,justificar No aplica.'),
('1.2.2','A','Si hay video pregrabado con audio,activar subtítulos ycontrastar diálogo einformación sonora; de lo contrario justificar No aplica.'),
('1.2.3','A','Si hay video pregrabado,comprobar descripción oalternativa de su información visual; justificar ausencia de multimedia.'),
('1.2.4','AA','Identificar video en directo ycomprobar subtítulos; si no hay transmisión,justificar No aplica.'),
('1.2.5','AA','En video pregrabado comprobar audiodescripción de información visual no expresada en audio; justificar ausencia.'),
('1.3.1','A','Revisar etiquetas asociadas,encabezados,relaciones de tablas ygrupos de campos mediante el árbol de accesibilidad.'),
('1.3.2','A','Desactivar estilos yleer el orden del DOM; confirmar que mantiene el significado de marcador,tabla yacciones.'),
('1.3.3','A','Leer instrucciones yerrores; comprobar que no dependan solo de forma,posición,tamaño osonido.'),
('1.3.4','AA','Alternar orientación vertical yhorizontal yverificar que no se restringe una orientación sin necesidad esencial.'),
('1.3.5','AA','Inventariar campos de datos personales; si existen,comprobar autocomplete apropiado. No confundir países del torneo con datos personales.'),
('1.4.1','A','Comprobar que estados,clasificados yerrores cuentan con texto osemántica además del color.'),
('1.4.2','A','Comprobar audio automático de más de3s ycontrol independiente; si no hay audio,documentar No aplica.'),
('1.4.3','AA','Medir pares de colores efectivos:4.5:1 en texto normal y3:1 en texto grande; registrar RGB yrazón.'),
('1.4.4','AA','Aumentar texto al200% ycomprobar funciones,campos ycontenido sin recortes.'),
('1.4.5','AA','Buscar texto convertido en imagen; comprobar alternativa de texto salvo excepciones esenciales como logotipos.'),
('1.4.10','AA','Evaluar320CSSpx ozoom400%; verificar reflujo sin doble desplazamiento,considerando excepciones de tablas bidimensionales.'),
('1.4.11','AA','Medir contraste3:1 de componentes,estados yfoco frente a colores adyacentes; justificar excepciones aplicables.'),
('1.4.12','AA','Aplicar interlineado1.5,espacio entre párrafos2em,letras0.12em ypalabras0.16em; comprobar ausencia de pérdida de contenido.'),
('1.4.13','AA','Mostrar contenido por hover yfoco; probar que se puede descartar,mantener apuntándolo yconservarlo mientras corresponde.'),
('2.1.1','A','Completar funciones con Tab,ShiftTab,Enter,Espacio yflechas,sin ratón; registrar toda función inaccesible.'),
('2.1.2','A','Entrar ysalir de modales ycontroles solo con teclado; comprobar que no existe una trampa de foco.'),
('2.1.4','A','Identificar atajos de una sola letra; si existen,comprobar desactivación,remapeo oactivación solo con foco pertinente.'),
('2.2.1','A','Identificar límites de tiempo ycomprobar desactivación,ajuste oextensión; justificar si no hay límites.'),
('2.2.2','A','Revisar movimiento,parpadeo,desplazamiento yactualización automática; comprobar pausa,detención uocultación cuando corresponda.'),
('2.3.1','A','Observar cambios visuales ycomprobar ausencia de destellos por encima del umbral; documentar elementos observados.'),
('2.4.1','A','Desde el inicio con teclado,buscar mecanismo para omitir navegación repetida yacceder al contenido principal.'),
('2.4.2','A','Revisar document.title de cada pantalla ycomprobar que describe su propósito.'),
('2.4.3','A','Recorrer todo el foco; abrir ycerrar modales ycomprobar orden lógico yretorno al control que los abrió.'),
('2.4.4','A','Revisar enlaces,iconos ysus contextos; determinar su destino con el nombre accesible.'),
('2.4.5','AA','Comprobar más de una forma de localizar páginas cuando el criterio aplica; justificar excepciones de pasos de proceso.'),
('2.4.6','AA','Revisar que encabezados yetiquetas describan tema opropósito ypermitan distinguir local yvisitante.'),
('2.4.7','AA','Navegar con teclado ycomprobar indicador de foco visible en cada control.'),
('2.4.11','AA','Con foco en cada componente,comprobar que no queda totalmente oculto por contenido creado por la página.'),
('2.5.1','A','Identificar gestos multipunto ode trayectoria; comprobar alternativa de puntero simple.'),
('2.5.2','A','En acciones de puntero,comprobar activación al soltar,opción de cancelar odeshacer,salvo excepción esencial.'),
('2.5.3','A','Comparar etiqueta visible de botones ycampos con su nombre accesible; el nombre debe incluir el texto visible.'),
('2.5.4','A','Identificar acciones por movimiento del dispositivo; comprobar alternativa de interfaz ydesactivación cuando aplique.'),
('2.5.7','AA','Si hay arrastre,comprobar alternativa de puntero simple sin arrastrar; justificar si no existe.'),
('2.5.8','AA','Medir objetivos de puntero de24×24CSSpx oespaciado equivalente; registrar excepciones justificadas.'),
('3.1.1','A','Inspeccionar html.lang ycomprobar que identifica el idioma principal del documento.'),
('3.1.2','AA','Identificar pasajes en otro idioma ysu marcado lang; considerar excepciones de nombres propios ytérminos técnicos.'),
('3.2.1','A','Recorrer controles con Tab ycomprobar que recibir foco no provoca un cambio de contexto.'),
('3.2.2','A','Modificar controles ycomprobar que no hay cambios de contexto inesperados sin aviso previo.'),
('3.2.3','AA','Comparar orden relativo de navegación repetida entre las tres pantallas.'),
('3.2.4','AA','Comparar nombres eidentificación de componentes con la misma función entre las tres pantallas.'),
('3.2.6','A','Si se repite ayuda,comparar su posición relativa entre páginas; si no existe,justificar No aplica.'),
('3.3.1','A','Intentar datos vacíos onegativos en el dataset QA; comprobar identificación textual del campo ydel error.'),
('3.3.2','A','Revisar etiquetas einstrucciones de todos los campos yrequisitos antes de enviar.'),
('3.3.3','AA','Provocar un error conocido ycomprobar sugerencia de corrección cuando se pueda proporcionar.'),
('3.3.4','AA','En cambios oborrados de datos controlables,comprobar reversión,revisión ocorrección antes de confirmar según aplique.'),
('3.3.7','A','En un mismo proceso,comprobar que no se vuelve a solicitar información ya proporcionada sin justificación.'),
('3.3.8','AA','Si existe autenticación,comprobar que no exige una prueba cognitiva sin alternativa permitida. Si no hay autenticación,justificar No aplica.'),
('4.1.2','A','Inspeccionar nombres,roles yestados de controles ymodales con árbol accesible ylector de pantalla.'),
('4.1.3','AA','Con Narrador olector de pantalla,guardar un resultado oprovocar error ycomprobar anuncio del estado sin mover innecesariamente el foco.')]


def main():
    path=ROOT/'qa/accessibility/manual.csv'
    existing=list(csv.DictReader(path.open(encoding='utf-8-sig',newline=''))) if path.exists() else []
    bykey={(r['pantalla'],r['criterio']):r for r in existing}
    output=[]
    for s in range(1,4):
        for criterion,level,procedure in CRITERIA:
            output.append(bykey.get((f'ACC-{s:03}',criterion),dict(pantalla=f'ACC-{s:03}',criterio=criterion,nivel=level,procedimiento=procedure,estado='',evidencia='',observacion='',bloqueante='',confirmado='')))
    csvwrite(path,output)
    (ROOT/'qa/accessibility/criterios.json').write_text(json.dumps({'standard':'WCAG2.2 A andAA','criteria':[c[0] for c in CRITERIA],'per_screen':len(CRITERIA),'total':len(output),'source':'https://www.w3.org/TR/WCAG22/'},indent=2),encoding='utf-8')
    print('Applicability instrument:',len(CRITERIA),'criteria per screen;',len(output),'checks; outcomes remain blank.')


if __name__=='__main__':main()
