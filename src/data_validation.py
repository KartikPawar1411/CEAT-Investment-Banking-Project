"""Audit the published workbook against independent Python calculations and output files."""
import csv
import datetime as dt
import json
import math
import re
import zipfile
from statistics import covariance,variance
from pathlib import Path
from openpyxl import load_workbook
from pptx import Presentation
from pypdf import PdfReader
from results import *
def run():
    checks=[]
    def check(name,ok):
        if not ok:raise AssertionError(name)
        checks.append(name)
    def close(name,a,b,tol=1e-6):check(name,math.isclose(a,b,rel_tol=1e-9,abs_tol=tol))
    a=json.loads((ROOT/'data/processed/assumptions.json').read_text())
    with (ROOT/'data/processed/ceat_statements.csv').open() as f:history={r['metric']:r for r in csv.DictReader(f)}
    def h(metric,period):return float(history[metric][period])
    def ebitda(p):return h('Revenue',p)-sum(h(k,p) for k in ['Materials','Purchases','Inventory expense','Employee','Other opex'])
    def wc(p):return h('Inventory',p)+h('Receivables',p)-h('Payables MSME',p)-h('Payables others',p)
    for j,p in enumerate(['FY22','FY23','FY24','FY25','FY26']):
        c='BCDEF'[j]
        close(p+' assets = liabilities and equity',h('Assets',p),h('Total equity',p)+h('Current liabilities',p)+h('Non-current liabilities',p),.015)
        close(p+' EBITDA, independently summed costs',ebitda(p),v(IS,c+'12'))
        close(p+' group PAT tie',ebitda(p)-h('DA',p)-h('Interest',p)+h('Other income',p)+h('JV',p)-h('Exceptional',p)-h('Tax',p),h('Group PAT',p),.015)
        close(p+' CFO/CFI/CFF bridge',h('Closing cash',p),h('Opening cash',p)+h('CFO',p)+h('CFI',p)+h('CFF',p),.015)
    with (ROOT/'data/raw/market.csv').open() as f:market=list(csv.DictReader(f))
    check('All market observation dates fall on or before cutoff',all(r['date']<=a['as_of'] for r in market))
    pr={r['symbol']:float(r['close']) for r in market if r['date']==a['as_of']}
    dates=sorted({r['date'] for r in market});check('53 paired weekly closes',len(dates)==53)
    ret={}
    for symbol in ['CEATLTD','NIFTYBEES']:
        rows=sorted((r['date'],float(r['close'])) for r in market if r['symbol']==symbol)
        ret[symbol]=[y[1]/x[1]-1 for x,y in zip(rows,rows[1:])]
    beta=covariance(ret['CEATLTD'],ret['NIFTYBEES'])/variance(ret['NIFTYBEES']);close('Independent OLS beta',beta,v(WA,'B8'))
    shares=a['shares_issued']/1e7;eq=pr['CEATLTD']*shares
    debt=sum(h(k,'H1FY27') for k in ['LT borrowings','ST borrowings','LT lease','ST lease'])
    bridge=debt+h('NCI','H1FY27')-h('Cash','H1FY27')-h('JV assets','H1FY27')-h('Investments','H1FY27')
    rate=(eq*(a['sovereign_yield']-a['credit_spread']+beta*a['erp'])+debt*a['debt_cost']*(1-a['tax']))/(eq+debt)
    close('Independent CAPM and WACC',rate,v(WA,'B18'));close('Spot capitalization',eq,v(TC,'D8'));close('Enterprise to equity bridge',bridge,v(DC,'B30'))
    check('Normalized DCF spread positive',rate>a['terminal_growth'])
    with (ROOT/'data/processed/peer_bridge.csv').open() as f:peers=list(csv.DictReader(f))
    for i,p in enumerate(peers,5):
        market_eq=float(p['shares'])*pr[p['symbol']]/1e7
        enterprise=market_eq+sum(float(p[k]) for k in ['borrowings','leases','nci'])-sum(float(p[k]) for k in ['cash','investments','eligible_deposits'])
        close(p['symbol']+' spot market cap',market_eq,v(TC,'D'+str(i)));close(p['symbol']+' spot EV',enterprise,v(TC,'I'+str(i)))
    for r in [5,6,7,8,9,10,11,12]:
        for numerator,den,which in [('I','J','N'),('I','K','O'),('I','L','P'),('D','M','Q')]:
            close('Trading ratio '+which+str(r),v(TC,numerator+str(r))/v(TC,den+str(r)),v(TC,which+str(r)))
    def calculate(growth_delta=0,margin_delta=0,rate_delta=0,terminal_delta=0):
        rev=h('Revenue','FY26');nwc=wc('FY26');cash=[];powers=[];cost=rate+rate_delta;g=a['terminal_growth']+terminal_delta
        for i in range(5):
            if i==0:
                h2=(rev-h('Revenue','H1FY26'))*(1+a['growth'][0]+growth_delta)
                rev=h('Revenue','H1FY27')+h2;eb=ebitda('H1FY27')+h2*(a['margin'][0]+margin_delta)
            else:
                rev*=1+a['growth'][i]+growth_delta;eb=rev*(a['margin'][i]+margin_delta)
            dep=rev*a['da'][i];cap=a['capex'][i] if i==0 else rev*a['capex'][i];nw=rev*a['nwc'][i]
            u=(eb-dep)*(1-a['tax'])+dep-cap-nw+nwc;nwc=nw
            if i==0:
                h1dep=h('DA','H1FY27')
                h1u=(ebitda('H1FY27')-h1dep)*(1-a['tax'])+h1dep-h('Capex','H1FY27')-wc('H1FY27')+wc('FY26')
                u=(u-h1u)*145/182
            cash.append(u);powers.append((dt.date(2027+i,3,31)-dt.date.fromisoformat(a['as_of'])).days/365)
        disc=[flow/(1+cost)**t for flow,t in zip(cash,powers)]
        tv=cash[-1]*(1+g)/(cost-g)/(1+cost)**powers[-1]
        return (sum(disc)+tv-bridge)/shares
    close('Base DCF reconstructed from raw inputs',calculate(),v(DC,'B33'))
    for i,(k,shock) in enumerate(a['risk_cases'].items(),5):close(k+' independent scenario',calculate(*shock),v(SC,'F'+str(i)))
    for ir in range(5):
        for jc in range(5):
            close(f'WACC/g grid {ir+1},{jc+1}',calculate(rate_delta=(ir-2)*.01,terminal_delta=(jc-2)*.005),v(SE,'BCDEF'[jc]+str(6+ir)))
            close(f'Growth/margin grid {ir+1},{jc+1}',calculate((ir-2)*.02,(jc-2)*.01),v(SE,'BCDEF'[jc]+str(16+ir)))
    formula_book=load_workbook(MODEL,read_only=False)
    formula_count=sum(cell.data_type=='f' for sh in formula_book for rr in sh for cell in rr)
    check('Formula caches populated, no Excel errors',all(book[sh.title][cell.coordinate].value is not None and book[sh.title][cell.coordinate].data_type!='e' for sh in formula_book for rr in sh for cell in rr if cell.data_type=='f'))
    check('All model checks pass',all(v('Model Checks','D'+str(i))=='PASS' for i in range(5,17)))
    ppt=Presentation(ROOT/'output/CEAT_Investment_Banking_Pitch_Book.pptx')
    check('Pitch book has 19 slides',len(ppt.slides)==19)
    report=(ROOT/'reports/CEAT_Investment_Banking_Research_Report.md').read_text(encoding='utf-8')
    check('Research report has 18 requested sections',len(re.findall(r'^## \d+\.',report,re.M))==18)
    pdf=PdfReader(ROOT/'output/CEAT_Valuation_Summary.pdf');check('Summary is one page',len(pdf.pages)==1)
    pdf_text=pdf.pages[0].extract_text();all_text=' '.join(shape.text if shape.has_text_frame else ' '.join(c.text for row in shape.table.rows for c in row.cells) if shape.has_table else '' for slide in ppt.slides for shape in slide.shapes)
    for figure in [n(v(DC,'B33')),n(v(VS,'B6')),n(v(VS,'D6')),'3,545.80']:
        check('Core figure '+figure+' in all published documents',all(figure in x for x in [report,all_text,pdf_text]))
    check('All eight requested chart files',len(list((ROOT/'charts').glob('0*.png')))==8)
    report_lines=['# Valuation quality control','',f'{len(checks)} checks passed, including {formula_count:,} cached Excel formulas across {len(book.sheetnames)} sheets.','',f'Independent reference DCF: INR {calculate():,.2f} per listed share. Independent WACC: {rate:.6%}.','']
    report_lines+=['- '+name for name in checks]
    (ROOT/'reports/validation.md').write_text('\n'.join(report_lines)+'\n',encoding='utf-8')
    print(report_lines[2],report_lines[4])
if __name__=='__main__':run()

