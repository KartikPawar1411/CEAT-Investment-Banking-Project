"""Integrated quarterly underwriting, amounts in INR crore. All forward assumptions are editable."""
import calendar
from datetime import date
from openpyxl.utils import get_column_letter as L
from openpyxl.styles import Font, PatternFill, Alignment
from data_collection import ROOT

I="'Funding Inputs'!"
BS="'Historical Balance Sheet'!"
IS="'Historical Income Statement'!"
CF="'Historical Cash Flow'!"
TC="'Trading Comps'!"
WA="'WACC'!"
DC="'DCF Model'!"
TAX="'Sources & Assumptions'!$B$11"
CASES=['On time','Delay','External','Stress']
PCT='0.0%;(0.0%);0.0%'
NUM='#,##0.0;(#,##0.0);0.0'
def sheet(wb,name,title,heads):
    w=wb.create_sheet(name)
    w.append([title]);w.append([]);w.append(heads)
    w.freeze_panes='B4';w.sheet_view.showGridLines=False
    for c in w[3]:
        c.fill=PatternFill('solid',fgColor='18394B');c.font=Font(name='Calibri',bold=True,color='FFFFFF',size=10)
        c.alignment=Alignment(wrap_text=True,vertical='center')
    w.row_dimensions[3].height=34;w.column_dimensions['A'].width=39
    w['A1'].font=Font(name='Calibri',size=17,bold=True,color='11675F');w.row_dimensions[1].height=30
    for j in range(2,len(heads)+1):w.column_dimensions[L(j)].width=16
    return w
def setcell(w,r,c,val,fmt=NUM):
    z=w.cell(r,c,val);z.number_format=fmt
    z.font=Font(name='Calibri',size=11,color=('177063' if '!' in str(val) else '253549') if str(val).startswith('=') else '234A9A')
def inputs(wb):
    w=sheet(wb,'Funding Inputs','Underwriting assumptions | 6 November 2026',['Input / decision variable','Value','Evidence, interpretation and timing'])
    w.column_dimensions['C'].width=115
    rows=[
    ('Minimum quarter-end cash',100,'Analyst liquidity floor. September cash was 32. This is a decision threshold, not a covenant.'),
    ('Discretionary tranche',300,'Analyst proposal incremental to core FY27 budget. Two equal payments. No contracted revenue or savings assumed.'),
    ('FY27 standalone capex',1400,'CALL p13, management FY27 estimate.'),
    ('CAMSO upstream equipment midpoint',125,'CALL p13, midpoint of management range 100–150; outside standalone capex.'),
    ('Maintenance per quarter',150,'Analyst allocation within total core capex; based on FY26 depreciation and capex.'),
    ('Core expansion per quarter after FY27',115,'Analyst continuing core scope. Specific September contract phasing undisclosed.'),
    ('FX, INR per USD',90,'Analyst translation assumption for trademark and dollar end-customer billing.'),
    ('CAMSO monthly end billing, USD m',10,'CALL pp3–4, indicative size; excludes distributor-to-consolidated timing conversion.'),
    ('Estimated recognition factor',.75,'Analyst fraction of gross end-customer billing attributed to consolidated sales, not the 85% customer transition statistic.'),
    ('Quarterly core unit demand growth',.018,'Analyst 1.8% QoQ (~7.4% annual). CALL p5 attributes ~40% of 26.2% group Q2 YoY sales growth to volume (~10.5 growth points); group includes CAMSO.'),
    ('Starting core utilization',.85,'Analyst proxy for legacy sites, separate from Sri Lanka utilization below 50%, CALL pp3–4.'),
    ('Quarterly capacity growth',.016,'Analyst effective output ramp from core program; proposed tranche earns no incremental forecast sales.'),
    ('Quarterly underlying core price uplift',.002,'Analyst underlying price movement before commodity recovery and separate OHT mix effect.'),
    ('Q3 sequential basket shock',.0325,'CALL p13, midpoint of management 3–3.5% Q3 guidance. Prior quarter +8–9%.'),
    ('Subsequent quarterly basket inflation',.004,'Analyst composite materials escalation. Rubber-only share undisclosed.'),
    ('Lagged cost recovery',.75,'Analyst price recovery after one quarter; call differentiates replacement and OEM resets.'),
    ('Stress incremental basket shock',.08,'Analyst additional one-time step in Q3 input price level; persists and changes subsequent pricing.'),
    ('CAMSO growth, first two quarters',.10,'Analyst QoQ ramp, informed by 20–25% H2/H1 volume outlook; not equivalent to disclosed revenues.'),
    ('CAMSO growth thereafter',.017,'Analyst growth per quarter.'),
    ('Mature collection days',38,'Analyst convergence over six quarters from September balances on Q2 sales.'),
    ('Mature inventory days',72,'Analyst convergence from September inventory on Q2 material expense.'),
    ('Mature payable days',108,'Analyst convergence from September trade payables on Q2 material expense.'),
    ('Blended existing borrowing rate',.085,'Analyst effective cash rate; FY26 note 20 domestic floating loans 7.15–7.8%, scope differs.'),
    ('Incremental bridge rate',.105,'Illustrative variable funding; capacity and terms are unverified.'),
    ('Planned external term proceeds',550,'Illustrative beginning Q3 FY27 issue; bullet in Q4 FY31. No lender indication.'),
    ('External term rate',.095,'Analyst illustrative fixed rate. No fees assumed.'),
    ('Stress rollover shortfall',.10,'Analyst one-time nonrenewal of residual short/other borrowings in Q4 FY27.'),
    ('Other opex variable share',.65,'Analyst split of Q2 other operating expenses; remaining cost and payroll rise quarterly.'),
    ('Quarterly fixed cost inflation',.012,'Analyst payroll/fixed overhead inflation.'),
    ('Lease principal paid / replaced per q',25,'Analyst equal principal and noncash renewals; RoU depreciation included in total D&A.'),
    ('Normalized terminal ROIC',.14,'Analyst return on incremental capital. Reinvestment = next-year NOPAT × growth / ROIC.'),
    ('Annual dividend cash',140,'Analyst recurring payout in September, AR26 note 19 FY26 proposed 141.58.'),
    ('Trademark commitment, USD m',44,'H1 p20 note 6, call p13–14: end of August 2028. Capitalized in Q2 FY29.'),
    ('Baseline Q2 basket change',.085,'CALL pp3–4: 8–9% sequential raw-material inflation. Price carryover Q3 modeled at recovery fraction.'),
    ('Quarterly composite depreciation rate',.0205,'Analyst rate on opening PPE, CWIP, intangibles and ROU pooled. Includes replacement ROU depreciation.'),
    ('Gross operating plant, Sep',9453,'H1 p17: PPE 7779 + CWIP 931 + ROU 310 + intangible 394 + under-development intangible 39.'),
    ('Stress recovery fraction',.40,'Analyst recovery of previous quarterly input escalation, replacing base recovery.'),
    ('Inventory commitment, USD m (memo)',44,'H1 p20 approx.; settlement timing and remaining balance unknown. Normal turnover included in inventory days.'),
    ]
    for r,(k,v,note) in enumerate(rows,4):
        w.cell(r,1,k);setcell(w,r,2,v,PCT if r in [12,13,14,15,16,17,18,19,20,21,22,26,27,29,30,31,32,34,37,38,40] else NUM);w.cell(r,3,note)
    # Disclosed March current maturities take precedence over gross face-value schedule.
    w.cell(44,1,'Repayments by FY | ₹ crore');year=[2027,2028,2029,2030,2031]
    for j,y in enumerate(year,2):w.cell(44,j,y)
    for r,(name,carrying,current,weights) in enumerate([
        ('Kotak',131.92,47.97,[16,12,0,0]),('Bank of Baroda I',321.56,139.73,[20,20,0,0]),
        ('Bank of Baroda II',320,60,[31,39,4,0]),('State Bank',400,42.11,[10.53,10.53,10.53,10.53]),
        ('Axis',400,30,[13.75,15,18.75,20])],45):
        w.cell(r,1,name);w.cell(r,2,current);w.cell(r,7,carrying)
        rem=[28,40,74,89.47,92.5][r-45]
        for c,weight in enumerate(weights,3):w.cell(r,c,f'=($G{r}-$B{r})*{weight}/{rem}')
    w['G44']='March carrying incl current';w['A51']='AR26 note 20 pp157–158. Current portion per table; allocate remaining carrying value pro rata to disclosed future weights. FY27 H2 assumes half-year already repaid.'
    w['A52']='₹250cr Series 4 due 30 Dec 2030; FY27 Sep ₹150cr Series 3 matures before opening balance. Other debt assumed rolled. No undrawn revolver in base liquidity.'
    for c in 'DEFG':w.column_dimensions[c].width=21
    for r,(label,val,desc) in enumerate([
        ('Base OHT sales mix proxy',"='Industry & Peers'!C31",'Standalone product mix as proxy for core; acquired CAMSO independently modeled.'),
        ('OHT relative realization',1.60,'Analyst price per equivalent unit; other core products indexed at 1.00.'),
        ('FY31 OHT unit share increase',.03,'Analyst increase over 18 quarters. Opening unit share inferred from reported sales mix and assumed relative price.')],55):
        w.cell(r,1,label);setcell(w,r,2,val,NUM if r==56 else PCT);w.cell(r,3,desc)
def calendar_data():
    d=[]
    for i in range(18):
        month=(11+i*3)%12+1;y=2026+(11+i*3)//12
        d.append((date(y,month,calendar.monthrange(y,month)[1]),f'Q{(month//3+2)%4+1} FY{(y+(month>3))%100}'))
    return d
LABELS="""Quarter end
Core volume index
Effective capacity index
Core utilization
Input price index
Core realization index incl mix
Core sales proxy
CAMSO sales proxy
Group sales
Material expense incl inventory
Employee expense
Other operating costs
Operating EBITDA
Depreciation incl right-of-use
Operating EBIT
Interest expense
Profit before tax
Tax expense
Group net income
Inventory
Trade receivables
Trade payables
Trade working capital
Change in trade working capital
Maintenance capex
Core expansion budget
Discretionary tranche
Trademark acquisition
Lease renewals (noncash)
Lease principal
Scheduled loan / NCD maturity
Nonrenewal of other borrowings
Planned term draw
Planned term redemption
Distributions
Operating cash before financing interest
Investing cash flow
Cash before balancing facility
Balancing draw / (repayment)
Financing cash flow incl interest
Closing cash
Closing legacy borrowings
Closing planned term debt
Closing bridging debt required
Total borrowings ex lease
Closing lease obligations
Net operating fixed assets incl ROU
Other assets, held constant
Total assets
Other liabilities, held constant
Total equity incl NCI
Liabilities and equity
Balance sheet residual
Cash roll-forward residual
Debt roll-forward residual
Unlevered free cash flow
Opening cash
Pre-backstop cash, cumulative
Tranche payment weight, cumulative
No-tranche cash without backstop
Tranche capacity at quarter end
Unfunded shortfall flag
Unassisted interest tax adjustment
Net reinvestment incl trademark
Effective inventory days
Effective collection days
Effective payment days
Peak incremental financing outstanding
Total reinvestment incl noncash ROU""".splitlines()
def scenario(wb,name):
    dates=calendar_data();w=sheet(wb,name,name+' | funding and quarterly three statements',['₹ crore except indices and days','Sep opening']+[t for d,t in dates])
    for r,title in enumerate(LABELS,4):w.cell(r,1,title)
    def inp(r):return I+'$B$'+str(r)
    opening={4:date(2026,9,30),5:100,6:'=100/'+inp(14),7:'=B5/B6',8:100,9:100,11:'='+inp(11)+'*3*'+inp(10)+'/10*'+inp(12),10:'='+IS+'G5-B11',12:'='+IS+'G5',13:'='+IS+'G9',14:'='+IS+'G10',15:'='+IS+'G11',16:'='+IS+'G12',23:'='+BS+'H11',24:'='+BS+'H12',25:'='+BS+'H13+'+BS+'H14',26:'='+BS+'H27',44:'='+BS+'H15',45:'='+BS+'H23',46:0,47:0,48:'=SUM(B45:B47)',49:'='+BS+'H24',50:'='+inp(39),51:'='+BS+'H5-B44-B23-B24-B50',52:'='+BS+'H5',54:'='+BS+'H6',53:'=B52-B54-B48-B49-B25',61:'=B44',62:0,63:'=B44',66:0}
    for r,v in opening.items():setcell(w,r,2,v,'dd mmm yy' if r==4 else NUM)
    for r,title in [(80,'Core OHT equivalent units / total'),(81,'Indexed product realization at constant prices'),(82,'Discretionary capex under construction'),(83,'Memo: organic/core revenue growth, QoQ')]:w.cell(r,1,title)
    setcell(w,80,2,'='+inp(55)+'/('+inp(56)+'-('+inp(56)+'-1)*'+inp(55)+')',PCT)
    setcell(w,81,2,'=1+B80*('+inp(56)+'-1)');setcell(w,82,2,0)
    for k,(end,tag) in enumerate(dates):
        j=k+3;a=L(j);p=L(j-1);fy=(k+2)//4;yr=L(fy+2);stress=name in ['Stress','Funded stress']
        vol=inp(13);rate=inp(40 if stress else 19);fac=inp(27)
        unit_cost='$B$13/$B$12';growth=inp(17)+(('+'+inp(20)) if stress else '') if k==0 else inp(18)
        # Recover a fraction of the prior absolute change in cost per indexed unit.
        # The opening Q2 index is 100 after an 8.5% rise from its earlier level.
        lag=f'{p}8-{p}8/(1+{inp(37)})' if k==0 else f'{p}8-{L(j-2)}8'
        due='SUM('+I+'$'+yr+'$45:$'+yr+'$49)/4'+('+250' if k==16 else '')
        coll=f'$B$24/$B$12*92+MIN(1,{k+1}/6)*({inp(23)}-$B$24/$B$12*92)'
        inv=f'$B$23/$B$13*92+MIN(1,{k+1}/6)*({inp(24)}-$B$23/$B$13*92)'
        pay=f'$B$25/$B$13*92+MIN(1,{k+1}/6)*({inp(25)}-$B$25/$B$13*92)'
        # A 92-day standard quarter avoids spurious WC releases in short fiscal quarters.
        spend=k in ((4,5) if name=='Delay' else (0,1))
        F={5:f'MIN({p}5*(1+{vol}),{a}6)',6:f'{p}6*(1+{inp(15)})',7:f'{a}5/{a}6',
        8:f'{p}8*(1+{growth})',9:f'{p}9*(1+{inp(16)})+$B$9*({lag})/100*{unit_cost}*{rate}',
        10:f'$B$10*{a}5/100*{a}9/100',11:f'{p}11*(1+{inp(21 if k<2 else 22)})',12:f'SUM({a}10:{a}11)',
        13:f'$B$13*({a}5/100*$B$10/$B$12+{a}11/$B$12)*{a}8/100',
        14:f'{p}14*(1+{inp(32)})',15:f'$B$15*({inp(31)}*({a}5/100*$B$10/$B$12+{a}11/$B$12)+(1-{inp(31)})*(1+{inp(32)})^{k+1})',
        16:f'{a}12-SUM({a}13:{a}15)',17:f'{p}50*{inp(38)}',18:f'{a}16-{a}17',
        19:f'(({p}45+{p}49)*{inp(26)}+{p}47*{fac}+({p}46+{a}36)*{inp(29)})/4',
        20:f'{a}18-{a}19',21:f'MAX(0,{a}20)*{TAX}',22:f'{a}20-{a}21',
        23:f'{a}13*{a}68/92',24:f'{a}12*{a}69/92',25:f'{a}13*{a}70/92',26:f'{a}23+{a}24-{a}25',
        27:f'{a}26-{p}26',28:inp(8),29:(f'({inp(6)}+{inp(7)}-{CF}H6)/2-{a}28' if k<2 else inp(9)),
        30:inp(5)+'/2' if spend else '0',31:inp(36)+'*'+inp(10)+'/10' if k==7 else '0',
        32:inp(33),33:inp(33),34:due,35:f'($B$45-SUM({I}G45:G49)+SUM({I}B45:B49)/2-250)*{inp(30)}' if stress and k==1 else '0',
        36:inp(28) if name in ['External','Funded stress'] and k==0 else '0',37:f'{p}46' if k==17 else '0',38:inp(35) if end.month==9 else '0',
        39:f'{a}22+{a}17+{a}19-{a}27',40:f'-SUM({a}28:{a}31)',41:f'{p}44+{a}39+{a}40+{a}36-SUM({a}33:{a}35)-{a}37-{a}38-{a}19',
        42:f'MAX({inp(4)}-{a}41,-{p}47)',43:f'{a}36+{a}42-SUM({a}33:{a}35)-{a}37-{a}38-{a}19',
        44:f'{p}44+{a}39+{a}40+{a}43',45:f'{p}45-{a}34-{a}35',46:f'{p}46+{a}36-{a}37',47:f'{p}47+{a}42',
        48:f'SUM({a}45:{a}47)',49:f'{p}49+{a}32-{a}33',50:f'{p}50-{a}40+{a}32-{a}17',51:f'{p}51',
        52:f'SUM({a}23:{a}24)+{a}44+{a}50+{a}51',53:f'{p}53',54:f'{p}54+{a}22-{a}38',
        55:f'{a}25+SUM({a}48:{a}49)+{a}53+{a}54',56:f'{a}52-{a}55',57:f'{a}44-{p}44-{a}39-{a}40-{a}43',
        58:f'{a}48-{p}48-{a}42-{a}36+{a}34+{a}35+{a}37',59:f'{a}18*(1-{TAX})-{a}72',60:f'{p}44',
        61:f'{a}44-{a}47+{a}66',62:f'{p}62+'+('0.5' if spend else '0'),
        63:f'{a}61+{a}62*{inp(5)}',64:f'IF({a}62>0,MAX(0,({a}63-{inp(4)})/{a}62),IF({a}63>={inp(4)},1E9,0))',
        65:f'IF({a}61<{inp(4)}-0.001,1,0)',66:f'{p}66+{p}47*{fac}/4-(MAX(0,{a}20+{p}47*{fac}/4)-MAX(0,{a}20))*{TAX}',
        67:f'-{a}40-{a}17+{a}27',68:inv,69:coll,70:pay,71:f'{a}46+{a}47',72:f'{a}67+{a}32'}
        F[80]=f'$B$80+{inp(57)}*{k+1}/18'
        F[81]=f'1+{a}80*({inp(56)}-1)'
        F[10]+=f'*{a}81/$B$81'
        F[82]=f'{p}82+{a}30' if k<6 else '0'
        F[17]=f'({p}50-{p}82)*{inp(38)}'
        F[83]=f'{a}10/{p}10-1'
        setcell(w,4,j,end,'dd mmm yy')
        for r,ex in F.items():setcell(w,r,j,'='+ex,PCT if r in [7,62,80,83] else NUM)
    w['A75']='Opening Sep cash precedes valuation date. December is the first forecast checkpoint. Quarter-end floor does not establish intra-quarter liquidity.'
    w['A76']='Other assets / liabilities = opening reported residuals, fixed thereafter. No forecast plug. JV, other income, exceptional items and OCI forecast at zero.'
    w['A77']='Lease funding: new ROU assets and debt are noncash. UFCF deducts new lease investment because enterprise claims include lease liabilities.'
    w['A78']='Pre-backstop cash removes bridge principal and restores its after-tax interest. Tranche stays in CWIP through the decision window. No sales benefit underwritten.'

