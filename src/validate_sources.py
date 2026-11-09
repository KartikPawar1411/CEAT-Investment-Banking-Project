"""Fail before model generation if the cutoff dataset or critical primary ties change."""
import csv
import hashlib
import json
import re
from datetime import date
from lxml import html
from openpyxl import load_workbook
from data_collection import ROOT,RAW
from lineage import records,page_numbers

def validate():
    checks=[]
    def ok(name,value):
        if not value:raise ValueError('Source validation: '+name)
        checks.append(name)
    f=ROOT/'data/processed'
    manifest=records(ROOT/'data/archive_hashes.csv')
    for row in manifest:
        ok(row['archive']+' SHA-256',hashlib.sha256((RAW/row['archive']).read_bytes()).hexdigest()==row['sha256'])
    a=json.loads((f/'assumptions.json').read_text());ok('as of',a['as_of']=='2026-11-06')
    panel=records(RAW/'market.csv')
    for sym in ['CEATLTD','MRF','APOLLOTYRE','JKTYRE','NIFTYBEES']:
        rows=[r for r in panel if r['symbol']==sym];days={r['date'] for r in rows}
        ok(sym+' price coverage',len(rows)==len(days)==53 and max(days)==a['as_of'] and all(float(r['close'])>0 for r in rows))
    erp=load_workbook(RAW/'ERPJuly26.xlsx',read_only=True,data_only=True)['ERPs by country']
    for addr,k in [('D73','credit_spread'),('E73','erp')]:ok(k,abs(erp[addr].value-a[k])<1e-12)
    labels={'revenue':'revenue from operations','pbt_before_exceptional':'total profit before exceptional items and tax','other_income':'other income','interest':'finance costs','da':'depreciation, depletion and amortisation expense','parent_pat':'profit or loss, attributable to owners of parent'}
    for r in records(f/'peers.csv'):
        ident=r['source'].split()[0];file=RAW/(ident+'.html')
        if ident=='MRFJune':
            amounts=[8415.50,649.69,195.06,88.33,447.67,495.35] if r['period']=='Q1FY27' else [7675.64,671.83,128.59,98.41,428.78,501.82]
            ok('MRF June p8 consolidated signed comparator '+r['period'],[float(r[k]) for k in labels]==amounts);continue
        if not file.exists():
            ok('JK H1 restated EBITDA inputs',[float(r[k]) for k in labels]==[7880.25,507.05,35.93,222.33,230.06,390.35]);continue
        rows=html.parse(str(file)).xpath('//tr')
        for k,label in labels.items():
            if ident=='MRF26' and k=='parent_pat':
                ok('MRF attributable income',r[k] in page_numbers('MRFAR.pdf',149));continue
            numbers=[]
            for tr in rows:
                heads=tr.xpath('./th');cells=tr.xpath('./td')
                if not heads or not cells:continue
                title= ' '.join(' '.join(x.itertext()).lower() for x in heads)
                title=' '.join(title.split())
                if label not in title:continue
                last=cells[-1].text_content().strip().replace(',','')
                if re.fullmatch(r'-?\d+(\.\d+)?',last):numbers.append(float(last)/100)
            ok(ident+' '+k,any(abs(x-float(r[k]))<.0001 for x in numbers))
    hist={r['metric']:r for r in records(f/'ceat_statements.csv')}
    import pymupdf
    for period,doc,p1,p2,mult in [('FY26','AR26.pdf',138,139,100),('FY25','AR26.pdf',138,139,100),('FY24','AR24.pdf',122,123,100),('FY23','AR23.pdf',126,127,100),('FY22','AR23.pdf',126,127,100),('H1FY27','H1FY27.pdf',17,18,1)]:
        for k in ['Cash','LT borrowings','ST borrowings','LT lease','ST lease','Capex','CFO','Cash interest','Lease cash']:
            pg=p2 if k in ['Capex','CFO','Cash interest','Lease cash'] else p1
            x=str(int(round(float(hist[k][period])*mult)))
            ok(period+' '+k+' amount on cited page',x in page_numbers(doc,pg))
    for doc,pg,raw in [('AR26.pdf',169,'178512'),('AR26.pdf',176,'42065'),('AR26.pdf',139,'112046')]:ok(f'{doc} p{pg} {raw}',raw in page_numbers(doc,pg))
    for r in ['FY25','FY26','H1FY27']:
        wc,borr={'FY25':((118274-147367)/100,(28247+35000-33302)/100),'FY26':((196575-202690)/100,(41644+105000-38398)/100),'H1FY27':(367-832,941+198-303)}[r]
        ok(r+' WC cash components',abs(wc-float(hist['WC cash impact'][r]))<1e-6);ok(r+' borrowing components',abs(borr-float(hist['Net debt raised'][r]))<1e-6)
    for r,wc,net,scale in [('FY22',63887-71248,21852+51622-5551,100),('FY23',116781-94675,745+15487-16640,100),
                           ('FY24',188222-161478,9142-55523,100),('H1FY26',933-888,393+800-178,1)]:
        ok(r+' working capital components',abs(wc/scale-float(hist['WC cash impact'][r]))<1e-6)
        ok(r+' net financing components',abs(net/scale-float(hist['Net debt raised'][r]))<1e-6)
    ok('AR23 p126 two annual tax lines',(6989+186)/100==float(hist['Tax']['FY23']) and (3627-1197)/100==float(hist['Tax']['FY22']))
    ok('H1 p16 inventory expense visual tie',float(hist['Inventory expense']['H1FY27'])==-365)
    return checks
if __name__=='__main__':print(len(validate()),'source checks passed.')




