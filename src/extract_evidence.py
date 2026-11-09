"""Flatten statement pages for audit. All page numbers are PDF page indices starting at one."""
from pathlib import Path
from pypdf import PdfReader
from lxml import html
import re
from data_collection import ROOT, RAW

if __name__=='__main__':
    out=ROOT/'data/processed/extracts';out.mkdir(parents=True,exist_ok=True)
    for path in RAW.glob('*.html'):
        doc=html.fromstring(path.read_bytes())
        rows=[' | '.join(' '.join(cell.text_content().split()) for cell in row.xpath('./td|./th')) for row in doc.xpath('//tr')]
        (out/(path.stem+'.txt')).write_text('\n'.join(rows), encoding='utf-8')
    for path in RAW.glob('*.pdf'):
        file=out/(path.stem+'.txt')
        if file.exists():continue
        pages=[]
        for n,page in enumerate(PdfReader(path).pages,1):
            try:
                page_text=page.extract_text(extraction_mode='layout', layout_mode_space_vertically=False) or ''
            except Exception as err:
                page_text=f'[Text extraction unavailable: {type(err).__name__}]'
            pages.append(f'\n=== PDF PAGE {n} ===\n'+page_text)
        file.write_text('\n'.join(pages),encoding='utf-8')

