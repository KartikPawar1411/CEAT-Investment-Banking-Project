"""Refresh the fixed public documents, prices and weekly benchmark sample."""
import csv
import datetime as dt
import io
import pathlib
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
BASE = 'https://www.ceat.com/content/dam/ceat/pdf/'
NSE = 'https://nsearchives.nseindia.com/'
DOCS = {
    'AR26.pdf': BASE+'CEATIntegratedAnnualReport2526Re.pdf',
    'AR24.pdf': BASE+'Annual_Reports/CEAT-Limited-Integrated-Annual-Report-FY24.pdf',
    'AR23.pdf': BASE+'Annual_Reports/CEAT-Limited-Integrated-Annual-Report-FY23.pdf',
    'H1FY27.pdf': BASE+'CEATBMOutcomeOct142026signed.pdf',
    'H1presentation.pdf': BASE+'invpresentation.pdf',
    'FY26presentation.pdf': BASE+'CEATInvestorPresentationQ4FY26.pdf',
    'H1transcript.pdf': 'https://www.ceat.com/content/dam/ceat/ceat-revemp/financial-performance/call-transcripts/2026-10-15-ceat-q2fy27-earnings-call-transcript-vF.pdf',
}
for name, ident in {'JK26':'161601_26052026210520','MRF26':'156064_07052026183232','APOLLO26':'157532_14052026171627','APOLLOH127':'209419_04112026164438','JKH127':'203720_23102026201519'}.items():
    DOCS[name+'.html']=NSE+'corporate/ixbrl/INTEGRATED_FILING_INDAS_'+ident+'_iXBRL_WEB.html'

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read()

def document(item):
    name,url=item
    if (RAW/name).exists(): return
    data=fetch(url)
    if name.endswith('.pdf') and not data.startswith(b'%PDF'): raise ValueError(name)
    (RAW/name).write_bytes(data)
    print(name,len(data),flush=True)

def market(day):
    for back in range(6):
        trade=day-dt.timedelta(days=back)
        url=NSE+'products/content/sec_bhavdata_full_'+trade.strftime('%d%m%Y')+'.csv'
        try:
            data=fetch(url).decode('utf-8-sig')
            rows=[]
            for row in csv.DictReader(io.StringIO(data), skipinitialspace=True):
                if row['SYMBOL'].strip() in ('CEATLTD','JKTYRE','MRF','APOLLOTYRE','BALKRISIND','TVSSRICHAK','NIFTYBEES') and row['SERIES'].strip()=='EQ':
                    rows.append([trade.isoformat(),row['SYMBOL'].strip(),row['CLOSE_PRICE'].strip(),url])
            if len(rows)>=2: return rows
        except (OSError,KeyError,UnicodeError): pass
    return []

if __name__=='__main__':
    RAW.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(document,DOCS.items()))
        end=dt.date(2026,11,6)
        dates=[end-dt.timedelta(days=7*i) for i in range(53)]
        rows=sorted(row for result in pool.map(market,dates) for row in result)
    if not any(r[0]==end.isoformat() and r[1]=='CEATLTD' for r in rows): raise ValueError('Missing valuation-day print')
    with (RAW/'market.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['date','symbol','close','source']);w.writerows(rows)
    print('Market rows',len(rows))
