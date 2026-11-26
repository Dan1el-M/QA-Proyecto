"""Render native page images and preserve a reviewable page inventory."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from pypdf import PdfReader
from design import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--raster',action='store_true');args=parser.parse_args()
    base=ROOT/'qa/reports/document-render';pdf=base/'Informe_Final_QA_Mundial.pdf';out=base/'final';out.mkdir(exist_ok=True)
    previous={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in out.glob('page-*.png')}
    if args.raster:
        poppler=Path(sys.executable).parent.parent/'native/poppler/Library/bin/pdftoppm.exe'
        subprocess.run([str(poppler),'-r','100','-png',str(pdf),str(out/'page')],check=True)
    reader=PdfReader(pdf);pages=[]
    for i,page in enumerate(reader.pages,1):
        text=page.extract_text() or ''
        pages.append(dict(page=i,characters=len(text),width=float(page.mediabox.width),height=float(page.mediabox.height),start=text[:100],blank=len(text.strip())<10))
    digits=len(str(len(pages)))
    pngs=[out/f'page-{i:0{digits}d}.png' for i in range(1,len(pages)+1)]
    if not all(path.is_file() for path in pngs):raise RuntimeError('Missing current PDF page images')
    boards=[];f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
    for offset in range(0,len(pngs),4):
        canvas=Image.new('RGB',(2200,2264),'#DDDDDD');draw=ImageDraw.Draw(canvas)
        for index,path in enumerate(pngs[offset:offset+4]):
            x=index%2*1100;y=index//2*1132
            draw.text((x+10,y+3),f'Página {offset+index+1} — imagen nativa,100dpi',fill='black',font=f)
            with Image.open(path) as image:canvas.paste(image,(x,y+32))
        target=out/f'board-{offset//4+1:02}.png';canvas.save(target);boards.append(dict(board=target.name,pages=list(range(offset+1,min(offset+5,len(pngs)+1)))))
    hashes={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in pngs}
    changed=[i for i,path in enumerate(pngs,1) if previous.get(path.name)!=hashes[path.name]]
    report={'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':pages,'blank_pages':[p['page'] for p in pages if p['blank']],'boards':boards,'raster_dpi':100,'png_sha256':hashes,'changed_since_previous_raster':changed,'note':'Boards preserve every source page at its native pixel size; no resampling.'}
    (base/'page-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Pages:',len(pages),'; native images:',len(pngs),'; boards:',len(boards),'; blanks:',report['blank_pages'])


if __name__=='__main__':main()
