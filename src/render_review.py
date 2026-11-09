"""Rasterize the PDF brief, Excel dashboard print and actual PowerPoint PDF export."""
import pymupdf
from PIL import Image, ImageDraw
from data_collection import ROOT
def render():
    qa=ROOT/'.qa';qa.mkdir(exist_ok=True)
    for file,stem in [(qa/'pitch_book.pdf','slide'),(ROOT/'output/CEAT_Valuation_Summary.pdf','summary'),(qa/'dashboard.pdf','dashboard')]:
        d=pymupdf.open(file);thumbs=[]
        for i,p in enumerate(d,1):
            pix=p.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False)
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.save(qa/f'{stem}-{i:02}.png')
            if stem=='slide':
                im.thumbnail((610,345));thumbs.append(im)
        for j in range(0,len(thumbs),6):
            montage=Image.new('RGB',(1244,1095),'#cad3d5')
            for k,im in enumerate(thumbs[j:j+6]):montage.paste(im,(8+(k%2)*619,8+(k//2)*361))
            montage.save(qa/f'slides-{j+1:02}.jpg',quality=90)
if __name__=='__main__':render()

