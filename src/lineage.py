"""Cell-level input register. Originals remain in data/raw. Derived totals are labelled."""
import csv
import json
import re
from decimal import Decimal
from functools import lru_cache
import pymupdf
from openpyxl import load_workbook
from expansion_model import ROOT,sheet

def records(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
@lru_cache(None)
def page_numbers(doc,page):
    with pymupdf.open(ROOT/'data/raw'/doc) as d:
        text=d[page-1].get_text()
    return set(re.findall(r'(?<!\d)\d+(?:\.\d+)?(?!\d)',text.replace(',','')))
def register(wb):
    data=ROOT/'data';cat={r['ID']:r for r in records(data/'sources.csv')}
    heads=['Metric','Period','Archive / source ID','Page / table','Publication / evidence date','Reported unit','Reported / component value','Conversion / treatment','Model input (cr unless noted)','Evidence status']
    out=[]
    def rec(k,p,file,loc,id,unit,raw,trans,val,status):
        out.append([k,p,file,loc,cat.get(id,{}).get('Publication date / evidence',id),unit,raw,trans,val,status])
    hist=records(data/'processed/ceat_statements.csv')
    derived={'Tax':'current + deferred and prior-year taxes','Net debt raised':'proceeds less principal repayments, incl short-term net movement','WC cash impact':'cash generated pre-tax less operating profit before working capital changes','Current assets incl held for sale':'total current assets plus assets held for sale','Cash interest':'interest paid per consolidated financing cash flows','Lease cash':'lease liability cash payments per financing cash flows'}
    for idx,row in enumerate(hist):
        k=row['metric']
        for period,s in list(row.items())[1:]:
            if not s:continue
            annual=period.startswith('FY');id={'FY22':'AR23','FY23':'AR23','FY24':'AR24','FY25':'AR26','FY26':'AR26'}.get(period,'H1')
            file=(id if annual else 'H1FY27')+'.pdf'
            pg=({'AR23':126,'AR24':122,'AR26':138}[id]+int(idx>=32) if annual else 16+(idx>=14)+(idx>=32))
            raw=abs(Decimal(s)*(100 if annual else 1));token=format(raw.normalize(),'f')
            hit=token in page_numbers(file,pg);amt=float(s)
            method=derived.get(k,'statement line')+('; lakh ÷ 100' if annual else '; whole crore')
            if k in ['Capex','Cash interest','Lease cash']:method+='; outflow magnitude'
            reported=amt*(100 if annual else 1)*(-1 if k in ['Capex','Cash interest','Lease cash'] else 1)
            components={('WC cash impact','FY26'):'196575 − 202690',('WC cash impact','FY25'):'118274 − 147367',('WC cash impact','H1FY27'):'367 − 832',
                        ('Net debt raised','FY26'):'41644 + 105000 − 38398',('Net debt raised','FY25'):'28247 + 35000 − 33302',('Net debt raised','H1FY27'):'941 + 198 − 303'}
            comp=components.get((k,period))
            additional={
                ('Net debt raised','FY22'):'21852 + 51622 − 5551',('Net debt raised','FY23'):'745 + 15487 − 16640',
                ('Net debt raised','FY24'):'9142 + 0 − 55523',('Net debt raised','H1FY26'):'393 + 800 − 178',
                ('WC cash impact','FY22'):'63887 − 71248',('WC cash impact','FY23'):'116781 − 94675',
                ('WC cash impact','FY24'):'188222 − 161478',('WC cash impact','H1FY26'):'933 − 888',
                ('Tax','FY22'):'−1197 + 3627',('Tax','FY23'):'186 + 6989'}
            comp=comp or additional.get((k,period))
            if k=='Inventory expense' and period=='H1FY27':
                rec(k,period,file,'PDF p16, H1 column (c)',id,'₹ crore',-365,'signed expense; confirmed in rendered statement',amt,'Visual tie to filing')
                continue
            rec(k,period,file,'Consolidated statements PDF p'+str(pg),id,'₹ lakh' if annual else '₹ crore',comp or (round(reported,4) if hit else 'see components / signed table'),method,amt,'Components verified' if comp else 'Magnitude on cited page' if hit else 'Calculated total or OCR requires visual tie')
    for row in records(data/'processed/peers.csv'):
        co,p=row['symbol'],row['period'];id=row['source'].split()[0]
        annual=p=='FY26';file=id+('.pdf' if id in ['JKH1report','MRFJune'] else '.html')
        for k in ['revenue','pbt_before_exceptional','other_income','interest','da','parent_pat']:
            # JK PDF comparative reports crore; NSE HTML filings display lakh.
            pdf=id in ['JKH1report','MRFJune'] or co=='MRF' and k=='parent_pat'
            val=float(row[k]);src='MRFAR.pdf' if co=='MRF' and k=='parent_pat' else file
            rec(co+' '+k,p,src,'p147 group 2426.10 less NCI 0.01; p149 parent' if src=='MRFAR.pdf' else 'p8 June quarter and comparator' if id=='MRFJune' else 'p4 restated H1 comparative' if pdf else 'Consolidated results, '+k,'MRFAR' if src=='MRFAR.pdf' else id,'₹ crore' if pdf else '₹ lakh',val if pdf else round(val*100,4),'as presented' if pdf else 'divide by 100',val,'Issuer statement')
    # Each bridge input has its own filing date; share counts and prior revenues can use different filings.
    bridge_evidence={
        'MRF': [('MRFAR','MRFAR.pdf','p146 borrowings','176.02 + 2191.03'),('MRFAR','MRFAR.pdf','p146 lease liabilities','719.26 + 120.35'),('MRFAR','MRFAR.pdf','p146 cash',304.59),('MRFAR','MRFAR.pdf','p146 noncontrolling interest',0.19),('MRFAR','MRFAR.pdf','p146 financial investments','340.96 + 3056.85'),('MRFAR','MRFAR.pdf','p174 note 10 eligible deposits',1867.02),('MRFAR','MRFAR.pdf','p148 share capital',4241143),('MRFAR','MRFAR.pdf','p147 previous-year operations revenue',28153)],
        'APOLLOTYRE':[('APOLLOH127','APOLLOH127.html','Consolidated debt: current and non-current','164270.60 + 267332.70'),('APOLLOH127','APOLLOH127.html','Other financial liabilities: lease sub-lines','86387.10 + 33316.10'),('APOLLOH127','APOLLOH127.html','Cash and equivalents on balance sheet',97331.90),('APOLLOH127','APOLLOH127.html','Consolidated equity attribution','blank; nil assumed'),('APOLLOH127','APOLLOH127.html','Equity-method, noncurrent and current investments','684.30 + 4994.40 + 0'),('APOLLOH127','APOLLOH127.html','Other bank balances excluded','1455.20 excluded'),('APSH','ApolloSH.pdf','Table I, issued equity shares',635100946),('APFY','APFY source register URL','FY26 announcement, FY25 consolidated comparator',26123)],
        'JKTYRE':[('JKH1report','JKH1report.pdf','p6 borrowings','2661.51 + 3325.28'),('JKH1report','JKH1report.pdf','p6 lease liabilities','101.15 + 36.70'),('JKH1report','JKH1report.pdf','p6 cash and equivalents',156.91),('JKH1report','JKH1report.pdf','p6 noncontrolling interest',-.66),('JKH127','JKH127.html','Equity-method, noncurrent and current investments','7880 + 2935 + 1104'),('JKH1report','JKH1report.pdf','p6 other bank balances excluded','134.21 excluded'),('JKSH','JKSH.pdf','Table I, issued equity shares',288289511),('JKFYreport','JKFYreport.pdf','p7 restated consolidated comparator',14692.92)]}
    for r in records(data/'processed/peer_bridge.csv'):
        for idx,k in enumerate(['borrowings','leases','cash','nci','investments','eligible_deposits','shares','prior_revenue']):
            ident,file,loc,value=bridge_evidence[r['symbol']][idx]
            unit='shares' if k=='shares' else '₹ lakh' if file.endswith('.html') else '₹ crore'
            rec(r['symbol']+' '+k,r['balance_date'] if k!='prior_revenue' else 'FY25',file,loc,ident,unit,value,'÷100 after aggregation' if unit=='₹ lakh' else 'add components where shown; use stated amount',float(r[k]),'Eligibility assumption' if k=='eligible_deposits' else 'Source bridge')
    for k,s,pg,raw,unit,meth,val in [
        ('FY26 CAMSO product revenue','AR26',176,42065,'₹ lakh','÷100; 7 months acquired product revenue',420.65),('Capital contracts remaining, net of advances','AR26',169,178512,'₹ lakh','÷100; March snapshot only',1785.12),
        ('FY27 standalone capex','CALL',13,1400,'₹ crore','management outlook',1400),('CAMSO upstream budget','CALL',13,'100–150','₹ crore','midpoint',125),
        ('Trademark, future payment','H1',20,44,'USD m','× assumed FX ÷ 10; Q2 FY29 per call',44),
        ('Acquisition inventory commitment','H1',20,'approx 44','USD m','turnover modeled in inventory days; pending balance unknown',44),
        ('Series 4 NCD principal','AR26',157,25000,'₹ lakh','÷100; Dec 2030 maturity',250),
        ('FY26 acquisition cash outflow','AR26',139,112046,'₹ lakh','÷100; excluded from regular cash capex',1120.46)]:
        rec(k,'FY26' if s=='AR26' else 'H1 FY27',{'AR26':'AR26.pdf','CALL':'H1transcript.pdf','H1':'H1FY27.pdf'}[s],f'PDF p{pg}',s,unit,raw,meth,val,'Reported line / guidance')
    a=json.loads((data/'processed/assumptions.json').read_text())
    for peer,ident,assets in [('MRF','MRF26',3195351),('Apollo','APOLLO26',2923971.70),('JK Tyre','JK26',1599586)]:
        rec(peer+' FY26 assets','FY26',ident+'.html','Consolidated balance sheet, Total assets',ident,'₹ lakh',assets,'÷100; denominator for EBIT / closing assets',assets/100,'Issuer statement')
    for loan,carrying,current in [('Kotak',13192,4797),('BoB I',32156,13973),('BoB II',32000,6000),('SBI',40000,4211),('Axis',40000,3000)]:
        rec(loan+' principal due within 1 year','31 Mar 2026','AR26.pdf','PDF p157 note 20, current maturities','AR26','₹ lakh',current,'÷100; half assumed paid by Sep. Balance table takes priority over gross footnote.',current/100,'Issuer statement')
        rec(loan+' total amortized cost','31 Mar 2026','AR26.pdf','PDF pp157–158 note 20, current + noncurrent','AR26','₹ lakh',carrying,'÷100; balance after current portion allocated by surviving maturity weights',carrying/100,'Carrying value, not gross face')
    for k,id,file,loc,method in [('sovereign_yield','YIELD','CCIL','6 Nov tenor 9–10 years','percent ÷ 100'),('erp','ERP','ERPJuly26.xlsx','ERPs by country!E73','decimal'),('credit_spread','ERP','ERPJuly26.xlsx','ERPs by country!D73','decimal'),('debt_cost','AR26','AR26.pdf','p157 note 20','upper end of domestic floating range'),('tax','Analyst assumption','assumptions.json','tax','normalized marginal rate'),('shares_issued','SHP','CEATSHP.pdf','Table I','count ÷ 10 million = crore shares')]:
        val=a[k];rec(k,'6 Nov valuation',file,loc,id,'shares' if k=='shares_issued' else '%' if k=='sovereign_yield' else 'decimal',val*100 if k=='sovereign_yield' else val,method,val,'Source register / assumption')
    for row in records(data/'raw/market.csv'):
        if row['symbol'] in ['CEATLTD','NIFTYBEES','MRF','APOLLOTYRE','JKTYRE']:
            rec(row['symbol']+' close',row['date'],'market.csv','NSE EQ CLOSE_PRICE','NSE '+row['date'],'₹ / share',float(row['close']),'weekly price return: current / previous − 1',float(row['close']),'URL in market.csv')
    w=sheet(wb,'Lineage','Source register | financial figures and market inputs',heads)
    for row in out:w.append(row)
    for col,width in zip('ABCDEFGHIJ',[40,17,40,38,36,24,24,65,23,40]):w.column_dimensions[col].width=width
    w.auto_filter.ref=w.dimensions
    with (data/'processed/input_register.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(heads);writer.writerows(out)




