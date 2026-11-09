"""Access the recalculated workbook as the single publishing source."""
import csv
import os
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from data_collection import ROOT
MODEL=ROOT/'output/CEAT_Financial_Valuation_Model.xlsx'
MODEL=Path(os.environ.get('CEAT_CHECK_MODEL',str(MODEL)))
def publish_path(relative):
    return Path(os.environ.get('CEAT_CHECK_OUTPUT',str(ROOT)))/relative
book=load_workbook(MODEL,data_only=True,read_only=False)
IS='Historical Income Statement';BS='Historical Balance Sheet';CF='Historical Cash Flow';RA='Financial Ratios';TC='Trading Comps';RV='Relative Valuation';DC='DCF Model';WA='WACC';VS='Valuation Summary';SC='Scenario Analysis';SE='Sensitivity Analysis';PE='Industry & Peers';D='Cover & Dashboard';AS='Sources & Assumptions';MP='Market Prices'
def v(sheet,addr):return book[sheet][addr].value
def series(sheet,r,columns='BCDEF'):return [v(sheet,c+str(r)) for c in columns]
def n(x):return f'{x:,.0f}'
def one(x):return f'{x:,.1f}'
def pct(x):return f'{x:.1%}'
def mult(x):return f'{x:.1f}x'
def price(x):return '₹'+n(x)
def source_rows():
    with (ROOT/'data/sources.csv').open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def metric_rows(sheet,items,columns):
    return [[label]+[fmt(x) if x is not None else '—' for x in series(sheet,r,columns)] for label,r,fmt in items]
def markdown_table(labels,rows):
    return '\n'.join(['| '+' | '.join(labels)+' |','| '+' | '.join('---' for _ in labels)+' |']+['| '+' | '.join(str(x) for x in rr)+' |' for rr in rows])
assert isinstance(v(DC,'B33'),(float,int)), 'Recalculate in Excel or LibreOffice before publishing.'

