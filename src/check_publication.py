"""Test financed decision data and the written recommendation in all three publications."""
import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from pptx import Presentation
from pypdf import PdfReader
from openpyxl import load_workbook
from committee import *
from verify_expansion import verify
from validate_sources import validate
def doc_texts(path):
    report=(path/'reports/CEAT_Investment_Banking_Research_Report.md').read_text(encoding='utf-8')
    pdf=PdfReader(path/'output/CEAT_Valuation_Summary.pdf')
    assert len(pdf.pages)==1
    deck=Presentation(path/'output/CEAT_Investment_Banking_Pitch_Book.pptx')
    shapes=[p for s in deck.slides for p in s.shapes]
    slides=' '.join(sh.text if sh.has_text_frame else ' '.join(c.text for row in sh.table.rows for c in row.cells) if sh.has_table else '' for sh in shapes)
    return [report,pdf.pages[0].extract_text(),slides]
def compare(path,book):
    sh=book[F];nd=book[ND]
    for text in doc_texts(path):
        for figure in [sh['B10'].value,n(sh['C4'].value),n(sh['C5'].value),n(sh['C8'].value),n(nd['B36'].value),n(book[FI]['B5'].value)]:
            assert figure in text,(figure,path)
    return [book[FI]['B5'].value,sh['B10'].value,sh['C4'].value,sh['E6'].value,nd['B36'].value]
def run():
    results=[compare(ROOT,book)]
    probe=ROOT/'.qa/threshold.xlsx'
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        target=Path(tmp);(target/'output').mkdir();(target/'reports').mkdir()
        for s in ['powerpoint_generator.py','pdf_summary.py','research_report.py']:
            subprocess.run([sys.executable,str(ROOT/'src'/s)],env={**os.environ,'CEAT_CHECK_MODEL':str(probe),'CEAT_CHECK_OUTPUT':str(target)},check=True)
        alt=load_workbook(probe,data_only=True);results.append(compare(target,alt))
        assert results[0][1]!=results[1][1] and results[0][2]!=results[1][2]
        assert action() in doc_texts(ROOT)[0] and action() not in doc_texts(target)[0]
    with (ROOT/'reports/decision_threshold_test.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['Tranche (₹ cr)','Written decision in deck, PDF and report','Peak on-time bridge (₹ cr)','Term-funded pre-bridge low (₹ cr)','DCF per share']);w.writerows(results)
    with (ROOT/'reports/validation.md').open('a',encoding='utf-8') as f:
        f.write(f'\n## Expansion underwriting\n\n{len(validate())} source checks and {verify()} integrated model checks passed. Tested all five quarterly cases through FY31, annual consolidation, first gaps, cash and debt roll-forwards, the normalized terminal year, eight valuation sensitivity cases, the market-clearing reverse case and the legacy-to-new value bridge.\n\n')
        for row in results:f.write(f'- Tranche ₹{n(row[0])} crore: **{row[1]}**, peak on-time bridge ₹{n(row[2])} crore; normalized DCF ₹{n(row[4])}/share. The workbook, deck, brief and report agree.\n')
    print('Cross-document and capex threshold test passed.')
if __name__=='__main__':run()

