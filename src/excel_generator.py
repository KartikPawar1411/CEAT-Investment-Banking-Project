"""Create the editable valuation workbook from the point-in-time input archive."""
import csv
import datetime as dt
import json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as col
from openpyxl.chart import LineChart, BarChart, Reference
from data_collection import ROOT, RAW
from source_register import write_sources
P=ROOT/'data/processed'
OUT=ROOT/'output/CEAT_Financial_Valuation_Model.xlsx'
A=json.loads((P/'assumptions.json').read_text())
def records(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
facts={r['metric']:r for r in records(P/'ceat_statements.csv')}
periods=['FY22','FY23','FY24','FY25','FY26','Q2FY27','H1FY27','H1FY26']
S=['Cover & Dashboard','Sources & Assumptions','Historical Income Statement','Historical Balance Sheet','Historical Cash Flow','Financial Ratios','Industry & Peers','Trading Comps','Relative Valuation','Revenue Forecast','DCF Model','WACC','Sensitivity Analysis','Valuation Summary','Scenario Analysis','Operating Sensitivities','Market Prices','Model Checks','Historical Charts']
D,AS,IS,BS,CF,RA,PE,TC,RV,RF,DC,WA,SE,VS,SC,OS,MP,QC,CH=S
N='#,##0.0;(#,##0.0);–'; INT='#,##0;(#,##0);–'; PC='0.0%;(0.0%);–'; X='0.00"x"'; DATE='dd mmm yyyy'
wb=Workbook();wb.remove(wb.active)
def sheet(name,sub):
    w=wb.create_sheet(name);w.sheet_view.showGridLines=False;w.freeze_panes='B5'
    w['A1']=name;w['A2']=sub;w.sheet_properties.pageSetUpPr.fitToPage=True
    w.column_dimensions['A'].width=39;w.row_dimensions[1].height=33;w.row_dimensions[2].height=32
    for i in range(2,18):w.column_dimensions[col(i)].width=16
    w.sheet_properties.tabColor='157B76' if name in [D,DC,VS] else '19364C'
    return w
def lab(w,r,t):w.cell(r,1,t)
def put(w,r,c,v,fmt=N):
    p=w.cell(r,c,v);p.number_format=fmt;return p
def row(w,r,items,start=1):
    for c,v in enumerate(items,start):
        if v is not None:w.cell(r,c,v)
def header(w,n,items):
    row(w,n,items)
    for c in range(1,len(items)+1):
        p=w.cell(n,c);p.fill=PatternFill('solid',fgColor='17364B');p.font=Font(name='Calibri',size=10,bold=True,color='FFFFFF');p.alignment=Alignment(vertical='center',wrap_text=True)
    w.row_dimensions[n].height=34
def ref(s,addr):return "'"+s+"'!"+addr
def link(w,r,c,s,addr,fmt=N):put(w,r,c,'='+ref(s,addr),fmt)
def historical(w,r,label,key=None):
    lab(w,r,label)
    for c,p in enumerate(periods,2):
        val=facts[key or label][p]
        if val:put(w,r,c,float(val))
def formula(w,r,label,expression,cols=range(2,10),fmt=N):
    lab(w,r,label)
    for c in cols:put(w,r,c,'='+expression(col(c),c),fmt)
def sub(w,r,text):
    lab(w,r,text)
    w.cell(r,1).font=Font(name='Calibri',bold=True,color='177975',size=11)
for n,t in zip(S,[
 '6 November 2026  |  Consolidated  |  INR crore unless indicated','Blue = editable input   •   Green = cross-sheet formula   •   Black = same-sheet calculation',
 'FY ends 31 March. Q2 and half-year figures are independently rounded to whole crore.','Current assets include disposal groups held for sale. Debt includes lease obligations where indicated.',
 'Positive capex, interest and lease payments are outflow magnitudes.','Annual returns use average opening and closing capital. H1 growth compares like periods.',
 'FY26 primary peer set. Interim observations support a separate September LTM comparison.','Spot equity prices, latest available balance sheets and period-specific earnings.',
 'Inclusive quartiles of meaningful multiples. Equity multiples apply to attributable profit.','FY27 starts from H1 actuals. The first growth and margin inputs refer to H2 only.',
 'End-year discounting. FY27 retains the post-valuation share of H2 operating cash flow.','Nominal INR. Market equity and book value of borrowings plus leases as a proxy for market debt.',
 'INR per listed share. Change one assumption set at a time.','INR per listed share. Peer quartiles and DCF operating cases have different meanings.',
 'Bear and bull vary operating assumptions, discount rate and terminal growth together.','Full driver-by-driver recalculation. Each block represents a scenario or grid coordinate.',
 'NSE EQ unadjusted closes. Market proxy is NIFTYBEES. Price returns exclude dividends.','Zero residuals expected, subject to the disclosed filing precision.','Editable charts. Annual consolidated, INR crore or percent as indicated.']):sheet(n,t)
w=wb[AS]; header(w,4,['Financial inputs','Value','Basis / source'])
inputs=[('Valuation date',dt.date(2026,11,6),'NSE close, strictly as of this date'),('Listed shares, count',A['shares_issued'],'SHP; includes 138,229 employee trust shares, issued basis for all equity outputs'),('Government yield',A['sovereign_yield'],'CCIL, 9–10 year on 6 Nov'),('Sovereign default spread',A['credit_spread'],'ERP, rating-based India, July'),('India equity risk premium',A['erp'],'ERP, total country premium'),('Marginal cost of debt',A['debt_cost'],'Upper end of FY26 INR bank loan range 7.15–7.80%; marginal proxy'),('Normalized corporate tax',A['tax'],'Indian domestic concessional rate inclusive of surcharge and cess'),('Perpetual nominal growth',A['terminal_growth'],'Mature INR growth assumption, below final explicit growth; no market share gain in perpetuity')]
for r,(k,v,note) in enumerate(inputs,5):
    row(w,r,[k,v,note]);w.cell(r,2).number_format=DATE if r==5 else INT if r==6 else PC
header(w,15,['FY27 first column = H2 growth/margin','FY27E','FY28E','FY29E','FY30E','FY31E'])
for i,(k,l) in enumerate([('growth','Revenue growth'),('margin','Operating EBITDA margin'),('da','D&A / revenue'),('capex','Capex: FY27 INR cr, later % revenue'),('nwc','Closing trade working capital / revenue')],16):
    lab(w,i,l)
    for j,v in enumerate(A[k],2):put(w,i,j,v,N if i==19 and j==2 else PC)
header(w,23,['FY21 opening values','INR crore','AR22, consolidated balance sheet and P&L p114'])
for r,(k,v) in enumerate(A['opening'].items(),24):row(w,r,[k,v])
header(w,38,['Source ID','Issuer','Document','Link to original','Published / available','Period','Data / locator','Retrieved','Verification'])
for r,values in enumerate(write_sources(),39):
    row(w,r,values);p=w.cell(r,4);p.hyperlink=values[3];p.value='Open original'
for c,width in {'B':23,'C':65,'D':21,'E':39,'F':23,'G':58,'H':18,'I':48}.items():w.column_dimensions[c].width=width
w=wb[MP];header(w,4,['Session','CEATLTD','NIFTYBEES','CEAT return','ETF return','MRF','APOLLOTYRE','JKTYRE'])
bydate={}
for record in records(RAW/'market.csv'):bydate.setdefault(record['date'],{})[record['symbol']]=float(record['close'])
for r,(day,prices) in enumerate(sorted(bydate.items()),5):
    put(w,r,1,dt.date.fromisoformat(day),DATE)
    for c,key in [(2,'CEATLTD'),(3,'NIFTYBEES'),(6,'MRF'),(7,'APOLLOTYRE'),(8,'JKTYRE')]:put(w,r,c,prices[key])
    if r>5:
        for c,base in [(4,'B'),(5,'C')]:put(w,r,c,f'={base}{r}/{base}{r-1}-1',PC)
last=w.max_row
for name in [IS,BS,CF,RA]:header(wb[name],4,['INR crore unless indicated']+periods)
w=wb[IS]
for r,key in [(5,'Revenue'),(6,'Materials'),(7,'Purchases'),(8,'Inventory expense'),(10,'Employee'),(11,'Other opex'),(13,'DA'),(15,'Interest'),(16,'Other income'),(17,'JV'),(18,'Exceptional'),(20,'Tax'),(21,'Group PAT'),(22,'Parent PAT')]:historical(w,r,key)
for r,t,f in [(9,'Material cost incl. inventory','SUM(@6:@8)'),(12,'Operating EBITDA','@5-@9-@10-@11'),(14,'Operating EBIT','@12-@13'),(19,'PBT incl. share of associates / JVs','@14-@15+@16+@17-@18'),(23,'PAT reconciliation residual','@19-@20-@21')]:formula(w,r,t,lambda a,c,f=f:f.replace('@',a))
w=wb[BS]
for r,key in [(5,'Assets'),(6,'Total equity'),(7,'NCI'),(8,'Current assets incl held for sale'),(9,'Current liabilities'),(10,'Non-current liabilities'),(11,'Inventory'),(12,'Receivables'),(13,'Payables MSME'),(14,'Payables others'),(15,'Cash'),(16,'LT borrowings'),(17,'ST borrowings'),(18,'LT lease'),(19,'ST lease'),(20,'PPE'),(21,'JV assets'),(22,'Investments')]:historical(w,r,key)
bcols=[2,3,4,5,6,8]
for r,t,f in [(23,'Gross borrowings','@16+@17'),(24,'Lease liabilities','@18+@19'),(25,'Gross debt including leases','@23+@24'),(26,'Net debt incl. leases','@25-@15'),(27,'Trade operating working capital','@11+@12-@13-@14'),(28,'Invested capital','@6+@26-@21-@22'),(29,'Parent equity','@6-@7'),(30,'Balance sheet reconciliation','@5-@6-@9-@10'),(31,'EV less equity bridge','@26+@7-@21-@22')]:formula(w,r,t,lambda a,c,f=f:f.replace('@',a),bcols)
w=wb[CF]
for r,key in enumerate(['CFO','Capex','CFI','CFF','Cash interest','Lease cash','Net debt raised','WC cash impact','Opening cash','Closing cash'],5):historical(w,r,key)
for r,t,f in [(15,'Cash after capex','@5-@6'),(16,'FCFE proxy incl. net borrowing','@15-@9-@10+@11'),(17,'Cash-flow reconciliation','@13+@5+@7+@8-@14')]:formula(w,r,t,lambda a,c,f=f:f.replace('@',a),[2,3,4,5,6,8,9])
w=wb[RA]; labels=['Revenue growth','Operating EBITDA margin','EBIT margin','Net margin (group PAT)','Current ratio','Borrowings / equity','ROE on average parent equity','ROIC on average invested capital','Net debt / operating EBITDA','Capex / sales','Cash after capex','UFCF proxy (trade WC definition)','Trade WC / revenue']
for i,t in enumerate(labels,5):lab(w,i,t)
for c in range(2,10):
    a=col(c);prev=col(c-1);ip=lambda r:ref(IS,a+str(r));bp=lambda r:ref(BS,a+str(r));cp=lambda r:ref(CF,a+str(r))
    prevrev=ref(AS,'B24') if c==2 else ref(IS,prev+'5')
    if c in [2,3,4,5,6,8]:put(w,5,c,'='+ip(5)+'/'+(ref(IS,'I5') if c==8 else prevrev)+'-1',PC)
    for r,metric in [(6,12),(7,14),(8,21)]:put(w,r,c,'='+ip(metric)+'/'+ip(5),PC)
    if c in bcols:
        for r,num,den in [(9,8,9),(10,23,6)]:put(w,r,c,'='+bp(num)+'/'+bp(den),X)
        put(w,17,c,'='+bp(27)+'/'+(ip(5) if c<7 else '('+ip(5)+'*2)'),PC)
    if c!=7:
        put(w,14,c,'='+cp(6)+'/'+ip(5),PC);link(w,15,c,CF,a+'15')
    if c<=6:
        prev_eq=ref(AS,'B25') if c==2 else ref(BS,prev+'29')
        prev_ic='('+ref(AS,'B26')+'+'+ref(AS,'B27')+'+'+ref(AS,'B28')+'-'+ref(AS,'B29')+'-'+ref(AS,'B30')+'-'+ref(AS,'B31')+')' if c==2 else ref(BS,prev+'28')
        prev_wc='('+ref(AS,'B32')+'+'+ref(AS,'B33')+'-'+ref(AS,'B34')+')' if c==2 else ref(BS,prev+'27')
        put(w,11,c,'='+ip(22)+'/AVERAGE('+bp(29)+','+prev_eq+')',PC)
        put(w,12,c,'='+ip(14)+'*(1-'+ref(AS,'B11')+')/AVERAGE('+bp(28)+','+prev_ic+')',PC)
        put(w,13,c,'='+bp(26)+'/'+ip(12),X)
        put(w,16,c,'='+ip(14)+'*(1-'+ref(AS,'B11')+')+'+ip(13)+'-'+cp(6)+'-('+bp(27)+'-'+prev_wc+')')
lab(w,20,'FY22–FY26 revenue CAGR');put(w,20,2,'=('+ref(IS,'F5')+'/'+ref(IS,'B5')+')^(1/4)-1',PC)
w=wb[PE];header(w,4,['Company','Period','Revenue','Pre-ex. PBT¹','Other income','Finance cost','D&A','Parent PAT','EBIT','EBITDA','Margin','Source'])
for r,p in enumerate(records(P/'peers.csv'),5):
    row(w,r,[p['symbol'],p['period']]+[float(p[k]) for k in ['revenue','pbt_before_exceptional','other_income','interest','da','parent_pat']])
    put(w,r,9,f'=D{r}-E{r}+F{r}');put(w,r,10,f'=I{r}+G{r}');put(w,r,11,f'=J{r}/C{r}',PC);w.cell(r,12,p['source'])
header(w,14,['Market bridge','Issued shares','Borrowings','Lease debt','Cash','NCI','Investments / JV','Eligible deposits','FY25 sales','Balance date','Source'])
for r,p in enumerate(records(P/'peer_bridge.csv'),15):row(w,r,[p['symbol']]+[float(p[k]) for k in ['shares','borrowings','leases','cash','nci','investments','eligible_deposits','prior_revenue']]+[p['balance_date'],p['source']])
lab(w,21,'¹ Before exceptional items, tax and equity-accounted profit. Non-operating income excluded from EBIT.')
header(w,24,['Operating scope','Measure','H1 FY27 share','Perimeter'])
for r,(k,v) in enumerate(zip(['Replacement','OEM','Exports','Truck & bus','Two/three-wheelers','Passenger car / UV','Off-highway','LCV / other'],[.5,.3,.2,.27,.28,.23,.16,.06]),25):row(w,r,['Channel' if r<28 else 'Product',k,v,'Standalone revenue; MIX p7']);w.cell(r,3).number_format=PC
header(w,35,['Customer geography','FY26 revenue','Share','Perimeter'])
for r,(k,v) in enumerate([('India',12168.44),('Outside India',3311.07)],36):row(w,r,[k,v,f'=B{r}/SUM(B36:B37)','Consolidated customer contracts; excludes other operating revenue']);w.cell(r,3).number_format=PC
for j in ['K','L']:w.column_dimensions[j].width=37
w=wb[TC];header(w,4,['Company / period','Price ₹','Shares crore','Market cap','Debt incl. leases','NCI','Cash + deposits','Investments','Enterprise value','Revenue','EBITDA','EBIT','Parent profit','EV / sales','EV / EBITDA','EV / EBIT','P/E','Growth','Margin'])
for r,co in enumerate(['MRF','APOLLOTYRE','JKTYRE','CEATLTD','APOLLOTYRE','JKTYRE','CEATLTD'],5):
    ltm=r>=9;row(w,r,[co+(' · Sep LTM' if ltm else ' · FY26')]);v={'MRF':'F','APOLLOTYRE':'G','JKTYRE':'H','CEATLTD':'B'}[co];link(w,r,2,MP,v+str(last))
    if co!='CEATLTD':
        k={'MRF':15,'APOLLOTYRE':16,'JKTYRE':17}[co];pr={'MRF':5,'APOLLOTYRE':6,'JKTYRE':7}[co]
        pp=lambda a:ref(PE,a+str(k))
        put(w,r,3,'='+pp('B')+'/10000000');put(w,r,5,'='+pp('C')+'+'+pp('D'));put(w,r,6,'='+pp('F'));put(w,r,7,'='+pp('E')+'+'+pp('H'));put(w,r,8,'='+pp('G'))
        for ci,s in [(10,'C'),(11,'J'),(12,'I'),(13,'H')]:
            expr=ref(PE,s+str(pr))
            if ltm:
                cur,old=(9,8) if co=='APOLLOTYRE' else (11,10);expr+='+'+ref(PE,s+str(cur))+'-'+ref(PE,s+str(old))
            put(w,r,ci,'='+expr)
        if not ltm:put(w,r,18,f'=J{r}/'+pp('I')+'-1',PC)
    else:
        put(w,r,3,'='+ref(AS,'B6')+'/10000000');link(w,r,5,BS,'H25');link(w,r,6,BS,'H7');link(w,r,7,BS,'H15');put(w,r,8,'='+ref(BS,'H21')+'+'+ref(BS,'H22'))
        for ci,s in [(10,5),(11,12),(12,14),(13,22)]:
            expr=ref(IS,'F'+str(s))
            if ltm:expr+='+'+ref(IS,'H'+str(s))+'-'+ref(IS,'I'+str(s))
            put(w,r,ci,'='+expr)
        if not ltm:link(w,r,18,RA,'F5',PC)
    put(w,r,4,f'=B{r}*C{r}');put(w,r,9,f'=D{r}+E{r}+F{r}-G{r}-H{r}')
    for ci,num,den in [(14,'I','J'),(15,'I','K'),(16,'I','L'),(17,'D','M')]:put(w,r,ci,f'=IF({den}{r}>0,{num}{r}/{den}{r},"NM")',X)
    put(w,r,19,f'=K{r}/J{r}',PC)
for base,lo,hi,ce in [(14,5,7,8),(24,9,10,11)]:
    header(w,base,['September LTM · 2 peers' if base==24 else 'FY26 · 3 peers','EV / revenue','EV / EBITDA','EV / EBIT','P/E'])
    for i,label in enumerate(['Minimum','25th percentile','Median','Mean','75th percentile','Maximum','CEAT vs median'],1):
        lab(w,base+i,label)
        for j,o in enumerate('NOPQ',2):
            rng=f'{o}{lo}:{o}{hi}';f=[f'MIN({rng})',f'PERCENTILE({rng},0.25)',f'MEDIAN({rng})',f'AVERAGE({rng})',f'PERCENTILE({rng},0.75)',f'MAX({rng})',f'{o}{ce}/{col(j)}{base+3}-1'][i-1]
            put(w,base+i,j,f'=IF(COUNT({rng})=0,"NM",{f})',PC if i==7 else X)
w=wb[RV];header(w,4,['Method','Target metric','P25','Median','P75','Median EV','Median equity','Low ₹/sh','Median ₹/sh','High ₹/sh','vs close'])
for r in range(5,13):
    i=(r-5)%4;ltm=r>=9;base=24 if ltm else 14;tr=11 if ltm else 8;label=['EV / revenue','EV / EBITDA','EV / EBIT','P/E'][i];lab(w,r,label+(' · Sep LTM' if ltm else ' · FY26'));link(w,r,2,TC,'JKLM'[i]+str(tr))
    for c,idx in [(3,2),(4,3),(5,5)]:link(w,r,c,TC,col(2+i)+str(base+idx),X)
    br=ref(BS,'H31');shares=ref(TC,'C8')
    if i<3:put(w,r,6,f'=B{r}*D{r}');put(w,r,7,f'=F{r}-{br}')
    else:put(w,r,7,f'=B{r}*D{r}');put(w,r,6,f'=G{r}+{br}')
    for c,o in [(8,'C'),(9,'D'),(10,'E')]:put(w,r,c,'=('+f'B{r}*{o}{r}'+('' if i==3 else '-'+br)+')/'+shares)
    put(w,r,11,f'=I{r}/'+ref(TC,'B8')+'-1',PC)
w=wb[WA];header(w,4,['Nominal INR capital costs','Value','Method'])
for r,(l,f,fmt,note) in enumerate([
 ('G-sec yield',ref(AS,'B7'),PC,'CCIL on valuation date'),('Sovereign spread',ref(AS,'B8'),PC,'India rating-based spread'),('Default-adjusted risk-free rate','B5-B6',PC,'Local sovereign yield less credit spread'),('Levered equity beta','SLOPE('+ref(MP,'D6:D'+str(last))+','+ref(MP,'E6:E'+str(last))+')',X,'52 weekly close-to-close price returns, NIFTYBEES proxy'),('India total ERP',ref(AS,'B9'),PC,'Includes country risk'),('Cost of equity','B7+B8*B9',PC,'CAPM'),('Pretax cost of debt',ref(AS,'B10'),PC,'FY26 disclosed bank rate range, upper bound'),('Tax rate',ref(AS,'B11'),PC,'Normalized domestic rate'),('After-tax debt cost','B11*(1-B12)',PC,'Tax shield at normalized rate'),('Market equity',ref(TC,'D8'),N,'NSE close × listed shares'),('Gross debt',ref(BS,'H25'),N,'September borrowings and leases, book proxy'),('Equity weight','B14/(B14+B15)',PC,'Market equity weight'),('Debt weight','1-B16',PC,'Gross debt weight'),('WACC','B10*B16+B13*B17',PC,'Base nominal INR discount rate'),('Beta R-squared','RSQ('+ref(MP,'D6:D'+str(last))+','+ref(MP,'E6:E'+str(last))+')',PC,'Weekly proxy regression fit')],5):
    lab(w,r,l);put(w,r,2,'='+f,fmt);w.cell(r,3,note)
w.column_dimensions['C'].width=62
w=wb[RF];header(w,4,['Revenue forecast','FY27E','FY28E','FY29E','FY30E','FY31E'])
for c in range(2,7):
    a=col(c);p=col(c-1)
    for r,l in [(5,'H2 or annual growth input'),(6,'Prior comparable sales'),(7,'H2 / annual projected sales'),(8,'H1 actual included'),(9,'Full-year sales'),(10,'Full-year sales growth')]:lab(w,r,l)
    link(w,5,c,AS,a+'16',PC);put(w,6,c,'='+ (ref(IS,'F5')+'-'+ref(IS,'I5') if c==2 else p+'9'))
    put(w,7,c,f'={a}6*(1+{a}5)');put(w,8,c,'='+ref(IS,'H5') if c==2 else '=0');put(w,9,c,f'={a}7+{a}8');put(w,10,c,f'={a}9/'+(ref(IS,'F5') if c==2 else p+'9')+'-1',PC)
w=wb[DC];header(w,4,['Five-year UFCF, INR crore','FY27E','FY28E','FY29E','FY30E','FY31E'])
dc_labels=['Full-year revenue','Full-year EBITDA','EBITDA margin','D&A','EBIT','Tax rate','NOPAT','Cash capex','Closing trade NWC','Change in trade NWC','Full-year UFCF','H2 / annual UFCF before stub','FY27 remaining share of H2','Eligible future UFCF','Year end','Years from valuation','Discount factor','PV of future UFCF']
for r,l in enumerate(dc_labels,5):lab(w,r,l)
for c in range(2,7):
    a=col(c);p=col(c-1)
    link(w,5,c,RF,a+'9');f=[(6,(ref(IS,'H12')+'+'+ref(RF,'B7')+'*'+ref(AS,'B17') if c==2 else a+'5*'+ref(AS,a+'17'))),(7,a+'6/'+a+'5'),(8,a+'5*'+ref(AS,a+'18')),(9,a+'6-'+a+'8'),(10,ref(AS,'B11')),(11,a+'9*(1-'+a+'10)'),(12,ref(AS,a+'19') if c==2 else a+'5*'+ref(AS,a+'19')),(13,a+'5*'+ref(AS,a+'20')),(14,a+'13-'+(ref(BS,'F27') if c==2 else p+'13')),(15,f'{a}11+{a}8-{a}12-{a}14'),(16,('('+a+'9-'+ref(IS,'H14')+')*(1-'+a+'10)+'+a+'8-'+ref(IS,'H13')+'-('+a+'12-'+ref(CF,'H6')+')-('+a+'13-'+ref(BS,'H27')+')') if c==2 else a+'15'),(17,('('+a+'19-'+ref(AS,'B5')+')/('+a+'19-DATE(2026,9,30))') if c==2 else '1'),(18,a+'16*'+a+'17'),(19,'DATE('+str(2025+c)+',3,31)'),(20,'('+a+'19-'+ref(AS,'B5')+')/365'),(21,'1/(1+'+ref(WA,'B18')+')^'+a+'20'),(22,a+'18*'+a+'21')]
    for r,expr in f:put(w,r,c,'='+expr,PC if r in [7,10,17,21] else DATE if r==19 else N)
for r,l,expr,fmt in [(25,'PV explicit forecasts','SUM(B22:F22)',N),(26,'Perpetual growth',ref(AS,'B12'),PC),(27,'Terminal value at FY31 end','IF('+ref(WA,'B18')+'>B26,F15*(1+B26)/('+ref(WA,'B18')+'-B26),"NM")',N),(28,'PV of terminal value','IF(ISNUMBER(B27),B27*F21,"NM")',N),(29,'Enterprise value','IF(ISNUMBER(B28),B25+B28,"NM")',N),(30,'EV less equity bridge',ref(BS,'H31'),N),(31,'Equity value','IF(ISNUMBER(B29),B29-B30,"NM")',N),(32,'Listed shares (crore)',ref(TC,'C8'),N),(33,'Value per listed share','IF(ISNUMBER(B31),B31/B32,"NM")',N),(34,'Upside / downside','IF(ISNUMBER(B33),B33/'+ref(TC,'B8')+'-1,"NM")',PC),(35,'Terminal PV / EV','IF(ISNUMBER(B29),B28/B29,"NM")',PC)]:
    lab(w,r,l);put(w,r,2,'='+expr,fmt)
from workbook_schedules import finish
finish(globals())

