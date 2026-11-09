"""Comparative underwriting, terminal economics and market-implied operations."""
from expansion_model import *
from openpyxl.styles import Border, Side
from openpyxl.chart import LineChart, Reference
from copy import copy

def annual(wb):
    w=sheet(wb,'FY Forecast','Consolidated forecast | on-time operating perimeter',['₹ crore unless indicated']+[f'FY{y}E' for y in range(27,32)])
    # FY27 uses signed H1 actuals for the full statements. Financing and noncore
    # historical items are preserved as reported rather than extrapolated.
    rows=[('Sales',12,'H5'),('Operating EBITDA',16,'H12'),('Depreciation',17,'H13'),('Operating EBIT',18,'H14'),('Finance cost',19,'H15'),('Other income + JV – exceptional',None,'special'),('Profit before tax',20,'H19'),('Income tax',21,'H20'),('Group net profit',22,'H21'),('Operating cash flow',39,'cf5'),('Investing cash flow',40,'cf7'),('Financing cash flow',43,'cf8'),('Cash, year end',44,None),('Borrowings',48,None),('Lease liabilities',49,None),('Net operating fixed assets',50,None),('Inventory',23,None),('Receivables',24,None),('Other assets',51,None),('Assets',52,None),('Trade payables',25,None),('Other liabilities',53,None),('Equity incl NCI',54,None),('Liabilities and equity',55,None),('Balance residual',56,None),('Maintenance, forecast only',28,None),('Core expansion, forecast only',29,None),('Discretionary, forecast only',30,None),('Trademark, forecast only',31,None),('H1 FY27 capex unallocated',None,'cap'),('Total cash investment incl trademark',None,None),('EBITDA margin',None,None),('Operating NOPAT at normal tax',None,None),('Forecast-quarter UFCF incl ROU',59,None),('Net reinvestment, forecast quarters',72,None)]
    for y,(lo,hi) in enumerate([(3,4),(5,8),(9,12),(13,16),(17,20)]):
        a=L(y+2)
        for r,(title,n,act) in enumerate(rows,4):
            w.cell(r,1,title);src="'On time'!"
            if r in range(16,29):ex=src+L(hi)+str(n)
            elif n:ex=f'SUM({src}{L(lo)}{n}:{L(hi)}{n})'
            else:ex='0'
            if y==0 and act:
                if act=='special':ex+='+'+IS+'H16+'+IS+'H17-'+IS+'H18'
                elif act=='cap':ex+='+'+CF+'H6'
                elif act.startswith('cf'):ex+='+'+CF+'H'+act[2:]
                else:ex+='+'+IS+act
            if r==34:ex=f'SUM({a}29:{a}33)'
            if r==35:ex=f'{a}5/{a}4'
            if r==36:ex=f'{a}7*(1-{TAX})'
            setcell(w,r,y+2,'='+ex,PCT if r==35 else NUM)
    w['A41']='FY27 full-year IS/CF includes historical H1 at reported precision. UFCF and reinvestment rows only include forecast quarters. The other three cases have full statements on their quarterly sheets.'
def peers(wb):
    w=sheet(wb,'Peer Diagnostics','Peer risk, operating comparability and leave-one-out pricing',['FY26 consolidated','Market beta','Debt / equity¹','Asset beta','FY26 growth','EBITDA margin','EBIT / assets²','Debt / EBITDA¹','EV / EBITDA','Pre-ex PBT + I + DA','Other income removed','Comparable EBITDA','FY26 assets','Balance date¹','Business mix'])
    mp=wb['Market Prices']
    for k in range(3):
        x=L(9+k);src=L(6+k);mp[x+'4']='Weekly return '+['MRF','Apollo','JK'][k]
        for r in range(6,58):setcell(mp,r,k+9,f'={src}{r}/{src}{r-1}-1',PCT)
    for k,(co,assets,bd,mix) in enumerate([('MRF',31953.51,'Mar 26','Indian replacement and OEM; broad domestic product mix.'),('Apollo',29239.717,'Sep 26','India and Europe; European passenger tyres.'),('JK Tyre',15995.86,'Sep 26','India and Mexico; commercial vehicle exposure.'),('CEAT',None,'Sep 26','Domestic two-wheelers and passenger; acquired OHT and tracks.')]):
        r=k+4;t=k+5;p="'Industry & Peers'!";m="'Market Prices'!"
        w.cell(r,1,co);x=L(k+9)
        forms={2:WA+'B8' if k==3 else f'SLOPE({m}{x}6:{x}57,{m}E6:E57)',3:f'{TC}E{t}/{TC}D{t}',4:f'B{r}/(1+(1-{TAX})*C{r})',5:f'{TC}R{t}',6:f'{TC}S{t}',7:f'{TC}L{t}/M{r}',8:f'{TC}E{t}/{TC}K{t}',9:f'{TC}O{t}',10:f'SUM({p}D{t},{p}F{t},{p}G{t})' if k<3 else IS+'F12+'+IS+'F16',11:f'{p}E{t}' if k<3 else IS+'F16',12:f'J{r}-K{r}'}
        for j,ex in forms.items():setcell(w,r,j,'='+ex,PCT if j in [3,5,6,7] else NUM)
        setcell(w,r,13,assets if assets else '='+BS+'F5');w.cell(r,14,bd);w.cell(r,15,mix)
    w.column_dimensions['O'].width=65
    w['A9']='¹ Market close 6 Nov; debt as at balance date, including leases. ² EBIT / closing FY26 assets. Three-peer FY26 median avoids overweighting market caps.'
    w['A10']='CEAT management EBITDA adds JV share; here EBITDA excludes other income, JV and exceptional items. JK FY26 PBDIT 2089 includes 57.63 other income.'
    w['A11']='MRF / Apollo use pre-exceptional PBT + finance + D&A less non-operating income. No unsupported adjustments to tyre mix or IFRS leases.'
    w['A13']='Excluded peer';w['B13']='Median EV / EBITDA';w['C13']='Implied ₹ / share'
    for i,co in enumerate(['MRF','Apollo','JK Tyre'],14):
        w.cell(i,1,co);others=[f'I{r}' for r in range(4,7) if r!=i-10]
        setcell(w,i,2,'=AVERAGE('+','.join(others)+')');setcell(w,i,3,f'=(B{i}*{TC}K8-{BS}H31)/{TC}C8')
    for r,k,ex in [(18,'Median asset beta','MEDIAN(D4:D6)'),(19,'Relevered at CEAT market D/E',f'B18*(1+(1-{TAX})*C7)'),(20,'Peer-beta WACC',f'({WA}B7+B19*{WA}B9)*{WA}B16+{WA}B13*{WA}B17')]:
        w.cell(r,1,k);setcell(w,r,2,'='+ex,PCT if r==20 else NUM)
    w['A22']='September LTM set: Apollo and JK only. MRF June LTM is separate. Trading Comps rows 9–12 and 24–30 show timing explicitly.'
def valuation(wb):
    w=sheet(wb,'Normalized DCF','Value of operating cash flow | quarterly discounting',['Quarter','Time, years','Eligible fraction','Sales','EBITDA','EBIT','Net reinvestment','Eligible UFCF','PV of UFCF','Uplift ramp','UFCF / 1pt uplift','Market EBITDA','Market EBIT','Market UFCF¹'])
    for k,(_,tag) in enumerate(calendar_data(),4):
        c=L(k-1);q="'On time'!"+c;w.cell(k,1,tag)
        values={2:f'({q}4-\'Sources & Assumptions\'!$B$5)/365',3:f'({q}4-\'Sources & Assumptions\'!$B$5)/({q}4-\'On time\'!B4)' if k==4 else '1',
        4:q+'12',5:q+'16',6:q+'18',7:q+'72',8:f'C{k}*({q}59)',9:f'H{k}/(1+$B$24)^B{k}',
        10:f'MIN(1,({k}-4)/14)',11:f'C{k}*D{k}*J{k}*0.01*(1-{TAX})',12:f'E{k}+D{k}*J{k}*$B$41',13:f'F{k}+D{k}*J{k}*$B$41',14:f'C{k}*(M{k}*(1-{TAX})-G{k})'}
        for j,e in values.items():setcell(w,k,j,'='+e,PCT if j in [3,10] else NUM)
    formulas=[
    ('Stock-beta WACC',WA+'B18'),('Perpetual nominal growth',"'Sources & Assumptions'!B12"),('Terminal incremental ROIC',I+'B34'),
    ('FY32 normalized NOPAT',"'FY Forecast'!F36*(1+B25)"),('Terminal reinvestment rate','B25/B26'),('FY32 required reinvestment','B27*B28'),('FY32 terminal UFCF','B27-B29'),
    ('PV of explicit UFCF','SUM(I4:I21)'),('PV of terminal UFCF','B30/(B24-B25)/(1+B24)^B21'),('Enterprise value','B31+B32'),('Net claims',BS+'H31'),('Issued shares, crore',TC+'C8'),
    ('Normalized value, ₹ / share','(B33-B34)/B35'),('FY31 base UFCF',"'FY Forecast'!F37"),('FY31 base operating margin',"'FY Forecast'!F35"),
    ('PV per +1pt FY31 margin, with ramp',f'SUMPRODUCT(K4:K21,1/(1+B24)^B4:B21)+SUM(D18:D21)*0.01*(1-{TAX})*(1+B25)*(1-B28)/(B24-B25)/(1+B24)^B21'),
    ('Market EV',TC+'I8'),('Required margin uplift','(B40-B33)/B39*0.01'),('Required FY31 EBITDA margin','B38+B41'),('FY31 required UFCF','SUM(N18:N21)'),
    ('Market FY32 NOPAT',f'SUM(M18:M21)*(1-{TAX})*(1+B25)'),('Market FY32 reinvestment','B44*B28'),('Market FY32 UFCF','B44-B45'),
    ('Market case, implied price','(SUMPRODUCT(N4:N21,1/(1+B24)^B4:B21)+B46/(B24-B25)/(1+B24)^B21-B34)/B35'),
    ('Original model value',DC+'B33'),('Original model FY31 UFCF',DC+'F15'),('Original reverse FY31 UFCF',DC+'B37'),
    ('Legacy margin needed, fixed capex/WC',f'{DC}F7+(B50-B49)/({DC}F5*(1-{TAX}))'),
    ('FY32 market implied sales',"SUM(D18:D21)*(1+B25)"),('FY32 market implied capital base','B44/B26'),('FY32 base implied capital base','B27/B26')]
    for r,(nm,ex) in enumerate(formulas,24):
        w.cell(r,1,nm);setcell(w,r,2,'='+ex,PCT if r in [24,25,26,28,38,41,42,51] else NUM)
    for j,nm in enumerate(['Test','WACC','g','ROIC','₹ per share'],4):w.cell(24,j,nm)
    for r,(lab,cost,g,roic) in enumerate([('Base','B24','B25','B26'),('Peer beta',"'Peer Diagnostics'!B20",'B25','B26'),('WACC −100 bp','B24-0.01','B25','B26'),('WACC +100 bp','B24+0.01','B25','B26'),('Growth −50 bp','B24','B25-0.005','B26'),('Growth +50 bp','B24','B25+0.005','B26'),('ROIC −300 bp','B24','B25','B26-0.03'),('ROIC +300 bp','B24','B25','B26+0.03')],25):
        w.cell(r,4,lab)
        for j,ex in enumerate([cost,g,roic],5):setcell(w,r,j,'='+ex,PCT)
        ex=f'(SUMPRODUCT(H4:H21,1/(1+E{r})^B4:B21)+\'FY Forecast\'!F36*(1+F{r})*(1-F{r}/G{r})/(E{r}-F{r})/(1+E{r})^B21-B34)/B35'
        setcell(w,r,8,'='+ex)
    w['A56']='¹ Operating case holds sales, explicit reinvestment and tax rate fixed; higher unit margins are phased to 100% of required uplift across all FY31 quarters.'
    w['A57']='Positive growth requires continuing capital. Implied FY32 capital base = NOPAT / normalized ROIC; this is a steady-state return assumption, not reported capital.'
    w['A61']='Original → revised equity bridge per share'
    w['A62']='Change in PV of explicit cash flows';setcell(w,62,2,'=(B31-'+DC+'B25)/B35')
    w['A63']='Change in PV of continuing value';setcell(w,63,2,'=(B32-'+DC+'B28)/B35')
    w['A64']='Reconstructed normalized value';setcell(w,64,2,'=B48+B62+B63')
    w['A58']='November-to-December stub prorates Q3 UFCF evenly (no November balance sheet). Trademark included once in FY29 investments; no additional acquisition debt claim.'
    w['A59']='DCF assumes prospective tranche spent on time with no quantified capacity benefit. Lease additions are treated as capital investment; overall claims include lease debt.'
def decision(wb):
    w=sheet(wb,'Funding Decision','Expansion committee | 18 months to March 2028',['Scenario','First floor breach¹','Peak bridge','Peak new debt²','Unassisted low','Funded low','Affordable tranche³','Peak gross loans','First new financing','Headroom / (gap)'])
    for r,s in enumerate(CASES+['Funded stress'],4):
        q="'"+s+"'!";w.cell(r,1,s)
        f={2:f'IFERROR(INDEX({q}C3:H3,1,MATCH(1,{q}C65:H65,0)),"None")',3:f'MAX({q}C47:H47)',4:f'MAX({q}C71:H71)',5:f'MIN({q}C61:H61)',6:f'MIN({q}C44:H44)',7:f'MIN({I}B5,{q}C64:H64)',8:f'MAX({q}C48:H48)',9:('"Q3 FY27"' if s in ['External','Funded stress'] else f'B{r}'),10:f'E{r}-{I}B4'}
        for j,ex in f.items():setcell(w,r,j,'='+ex)
    w['A10']='Release decision';setcell(w,10,2,f'=IF(AND(G4>={I}B5-0.01,G7>={I}B5-0.01),"RELEASE",IF(AND(G4>={I}B5-0.01,G7<{I}B5-0.01),"CONDITIONAL",IF(G5>={I}B5-0.01,"DELAY",IF(G6>={I}B5-0.01,"FINANCE BEFORE RELEASE","DEFER / RESIZE FUNDING"))))','General')
    w['A11']='¹ First cash below analyst floor, after any planned term issuance and before a balancing facility. Initial September cash excluded from forecast trough.'
    w['A12']='² Bridge plus illustrative external term proceeds outstanding. Peak gross loans excludes leases. Funded low assumes every required bridge draw is available.'
    w['A13']='³ Maximum of proposed amount supportable at its scheduled half-payments, keeping floor in every modeled quarter. Includes planned term capital in External only.'
    w['A14']='Conditional = base covers requested amount, stress fails. Delay = later schedule covers it. If both fail, require fully funded term capacity or resize the plan.'
    w['A15']='Scope: through Mar 2028. Review again before trademark in Sep 2028. A conservative liquidity review also tests unsettled inventory and intraperiod lows.'
    w.column_dimensions['A'].width=30;w.column_dimensions['B'].width=23
    w['A18']='Maximum affordable before request cap'
    for j,s in enumerate(CASES,2):
        w.cell(17,j,s);setcell(w,18,j,"=MIN('"+s+"'!C64:H64)")
    for i,n in enumerate(['Quarter ends','On time unassisted','Delay unassisted','External unassisted','Stress unassisted','Cash floor'],21):
        w.cell(i,1,n)
        for k,(_,tag) in enumerate(calendar_data()[:6],2):
            ex=tag if i==21 else '='+I+'B4' if i==26 else "='"+CASES[i-22]+"'!"+L(k+1)+'61'
            setcell(w,i,k,ex)
    graph=LineChart();graph.title='Quarter-end cash before a balancing facility';graph.y_axis.title='₹ crore'
    graph.add_data(Reference(w,min_col=1,max_col=7,min_row=22,max_row=26),titles_from_data=True,from_rows=True);graph.set_categories(Reference(w,min_col=2,max_col=7,min_row=21));graph.width=24;graph.height=10;w.add_chart(graph,'A29')
def dashboard(wb):
    old=wb['Cover & Dashboard'];wb.remove(old)
    w=sheet(wb,'Cover & Dashboard','CEAT Limited  |  Expansion decision',['6 NOVEMBER 2026','MODEL OUTPUT','READ-THROUGH'])
    w.column_dimensions['A'].width=38;w.column_dimensions['B'].width=28;w.column_dimensions['C'].width=79
    w['A2']='INR crore for funding  ·  INR per share for valuation  ·  consolidated  ·  quarter-end cash'
    rows=[
    ('Decision',"'Funding Decision'!B10",'Release only if the planning floor survives both the base and downside cases.'),
    ('Requested tranche',I+'B5','Two equal installments; incremental to the FY27 core envelope.'),
    ('On-time affordable tranche',"'Funding Decision'!G4",'Self-funded within 18 months at scheduled payment dates.'),
    ('First unfinanced shortfall',"'Funding Decision'!B4",'Quarter-end observation, measured against the cash floor.'),
    ('Peak bridge required',"'Funding Decision'!C4",'Incremental borrowing, subject to credit availability.'),
    ('Downside cash before bridge',"'Funding Decision'!E7",'Basket shock, slower recovery and partial short-term nonrenewal.'),
    ('Delayed tranche capacity',"'Funding Decision'!G5",'First installments move from Dec 26 / Mar 27 to Dec 27 / Mar 28.'),
    ('Normalized DCF per share',"'Normalized DCF'!B36",'Quarterly cash flows; FY32 reinvestment supports perpetual growth.'),
    ('FY26 peer P25 per share',"'Valuation Summary'!B6",'Three listed tyre peers. Independent relative cross-check.'),
    ('FY26 peer P75 per share',"'Valuation Summary'!D6",'Close on 6 November 2026: ₹3,545.80.'),
    ('Projected cash floor',I+'B4','Obtain a committed facility or delay if the modeled trough misses this amount.')]
    for r,(n,expr,note) in enumerate(rows,4):
        w.cell(r,1,n);setcell(w,r,2,'='+expr);w.cell(r,3,note)
        for c in w[r][:3]:
            if r%2==0:c.fill=PatternFill('solid',fgColor='E7F1EF')
            c.alignment=Alignment(vertical='center',wrap_text=True)
        w.row_dimensions[r].height=29
    for r,(a,b) in enumerate([('Funding Decision','Quarterly scenarios and liquidity'),('Normalized DCF','Market-implied margin and sensitivity'),('Lineage','Sources, reported values and unit conversions')],16):
        w.cell(r,1,a).hyperlink="#'"+a+"'!A1";w.cell(r,3,b)
    wb.move_sheet(w,offset=-wb.index(w));wb.active=0
def upgrade(wb):
    inputs(wb)
    for name in CASES+['Funded stress']:scenario(wb,name)
    annual(wb);peers(wb);valuation(wb);decision(wb)
    qc=wb['Model Checks']
    qc['A20']='Expansion underwriting | live controls'
    controls=[]
    for case in CASES+['Funded stress']:
        for row,label in [(56,'balance sheet'),(57,'cash movement'),(58,'borrowing movement')]:
            rng=f"'{case}'!C{row}:T{row}"
            controls.append((case+' | '+label,f'MAX(MAX({rng}),-MIN({rng}))'))
    controls.extend([('New DCF: original-to-revised bridge',"'Normalized DCF'!B64-'Normalized DCF'!B36"),
        ('Reverse DCF: recovered market close',"'Normalized DCF'!B47-'Trading Comps'!B8"),
        ('New DCF: reinvestment supports growth',"'Normalized DCF'!B29*'Normalized DCF'!B26-'Normalized DCF'!B27*'Normalized DCF'!B25"),
        ('FY27 core capex vs midpoint envelope',"'FY Forecast'!B34-'FY Forecast'!B31-'Funding Inputs'!B6-'Funding Inputs'!B7")])
    for r,(label,expression) in enumerate(controls,21):
        qc.cell(r,1,label);setcell(qc,r,2,'='+expression);setcell(qc,r,3,.00001,'0.00000')
        setcell(qc,r,4,f'=IF(ABS(B{r})<C{r},"PASS","FAIL")','General')
    from lineage import register
    register(wb);dashboard(wb)
    for s in ['DCF Model','Scenario Analysis','Sensitivity Analysis','Revenue Forecast','Operating Sensitivities','Valuation Summary']:
        wb[s]['A1']='Reference model | '+s
    for idx,s in enumerate(['Funding Decision','Funding Inputs','FY Forecast','Normalized DCF','Peer Diagnostics','Lineage'],1):wb.move_sheet(s,offset=idx-wb.index(wb[s]))

