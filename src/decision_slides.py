"""Editable decision pages; injected into the existing 18-slide book."""
from committee import *
def place(pos,kit):
    base,table,stat,note,txt=kit
    if pos==2:
        s=base('External funding is the gate for the next tranche' if outcome().startswith('FINANCE') else action().split('.')[0], 'Capital allocation decision','CEAT Oct 14 results pp16–20; Oct 15 call pp3–4,13–14; Funding Decision, Normalized DCF, Peer Diagnostics.',action())
        stat(s,.64,1.9,3.87,cv(F,'G4'),'Self-funded / on time',f"Proposed {cv(FI,'B5')}. The first cash-floor breach occurs in {v(F,'B4')}.")
        stat(s,4.68,1.9,3.87,cv(F,'C4'),'Peak on-time bridge',f"Stress cash before funding falls to {cv(F,'E7')}. Floor: {cv(FI,'B4')}.")
        stat(s,8.73,1.9,3.87,price(v(ND,'B36')),'Normalized DCF / share',f"Close ₹3,545.80. FY26 EBITDA quartiles {price(v(VS,'B6'))}–{price(v(VS,'D6'))}.")
        table(s,.64,4.6,12.0,1.0,['Decision','Later schedule: peak bridge','Term-funded trough','Additional funded-stress bridge'],[[outcome(),cv(F,'C5'),cv(F,'E6'),cv(F,'C8')]],size=13)
    if pos==3:
        s=base('When cash falls below the release threshold','Quarterly funding | 18 months','Funding Decision and linked cases, Q3 FY27 through Q4 FY28. Analyst funding terms and floor.',external())
        table(s,.58,1.9,12.12,2.88,HEAD,funding_table(),ratios=[1.05,1.15,1,1,1.2,1,1],size=12)
        txt(s,.66,5.02,12,.86,'¹ First quarter below the cash floor after planned funding.  ² Peak gross loans exclude lease liabilities. The balancing bridge is a funding requirement. Negative unassisted cash quantifies the shortfall before that facility.',13)
    if pos==13:
        s=base('Which operating assumptions fund the recovery','Quarterly drivers | FY27–FY31','H1 FY27 results pp16–18 and note 6; October call pp3–4,13–14; FY26 note 52. All scenario assumptions editable.',f"Core expansion and maintenance require {cv(AF,'F34')} in FY31. The discretionary tranche earns no explicit sales benefit.")
        table(s,.65,1.92,12.0,2.58,['On-time operating case','FY27E','FY28E','FY29E','FY30E','FY31E'],metric_rows(AF,[('Group sales · ₹ cr',4,n),('EBITDA margin',35,pct),('Group net profit · ₹ cr',12,n),('Closing cash · ₹ cr',16,n)],'BCDEF'),size=13)
        note(s,.68,4.75,5.7,'Legacy tyre business','Indexed units constrained by capacity. Realization reflects lagged material recovery and a modeled OHT mix shift.')
        note(s,6.63,4.75,5.75,'Acquired off-highway business','Approximate CAMSO from end-customer billing, FX and a recognition factor. Separate audited group unit prices are unavailable.')
    if pos==14:
        s=base(f"Normalized DCF gives {price(v(ND,'B36'))} per share",'Intrinsic valuation','Normalized DCF rows 24–54, 62–64. On-time forecast; group claims at 30 Sep; dated November stub.',market())
        table(s,.66,1.9,6.0,3.89,['Cash flow bridge','₹ crore'],[[x,cv(ND,'B'+str(i))] for x,i in [('FY32 operating NOPAT',27),('Required reinvestment',29),('Continuing cash flow',30),('PV of explicit quarters',31),('PV of continuing value',32),('Net claims',34)]],ratios=[1.65,1],size=13)
        note(s,7.02,1.98,5.2,'Reinvestment in perpetuity',f"Growth of {percent(ND,'B25')} at {percent(ND,'B26')} incremental ROIC requires reinvesting {percent(ND,'B28')} of NOPAT.")
        note(s,7.02,3.43,5.2,'Why the reference model was lower',f"{price(v(ND,'B48'))} reference DCF. New explicit cash flows add ₹{num(ND,'B62')} per share; revised continuing value adds ₹{num(ND,'B63')}.")
        txt(s,7.02,4.95,5.2,.80,f"Stock beta {v(WA,'B8'):.2f}. Peer-relevered beta {v(PD,'B19'):.2f} implies {percent(PD,'B20')} WACC and {price(v(ND,'H26'))} per share.",13)
    if pos==15:
        s=base('What the market price requires of operations','Market-implied operating case','Reference DCF rows 33–38; Normalized DCF rows 37–51. NSE close ₹3,545.80 on 6 November 2026.',f"FY26 EBITDA peer band {price(v(VS,'B6'))}–{price(v(VS,'D6'))}. Two-peer September LTM is a separate cross-check.")
        table(s,.68,1.96,11.97,2.4,['FY31 operating test','Base margin','Required margin','Base UFCF','Required UFCF'],[['Reference terminal-only test','12.5%',percent(ND,'B51'),cv(ND,'B49'),cv(ND,'B50')],['Revised, phased operating case',percent(ND,'B38'),percent(ND,'B42'),cv(ND,'B37'),cv(ND,'B43')]],ratios=[1.7,1,1.05,1,1.1],size=14)
        note(s,.72,4.82,5.65,'Reference test','Earlier cash flows stay fixed. The required terminal cash flow is converted to a margin at the same sales, capex and working capital.')
        note(s,6.62,4.82,5.58,'Revised test','Income rises with the phased margin improvement. The terminal year funds growth at the same incremental return.')
    if pos==17:
        s=base('Conditions for signing the next equipment order','Investment committee gates','15 October call; AR26 note 20 and note 42; modeled quarter-end payments. Analyst release criteria.',action())
        for idx,(title,body) in enumerate([
            ('Secure the base program',f"Delaying the optional spend still requires {cv(F,'C5')} of peak bridge. Confirm maturity dates, renewal documentation and lender commitments."),
            ('Test cash before each installment',f"Maintain {cv(FI,'B4')} each quarter and use actual 13-week liquidity before ordering. Reapprove if rubber inflates above the 3–3.5% Q3 outlook."),
            ('Reserve the CAMSO payment',f"Q2 FY29 includes the US$44m trademark at assumed FX. Track inventory settlements against modeled turnover; payment dates remain unverified.")]):
            note(s,.72,1.90+1.39*idx,11.75,title,body)
    if pos==18:
        s=base('Decision record and primary evidence','Investment committee close','Independent public-information portfolio project | valuation as of 6 November 2026.',short())
        note(s,.7,1.88,5.6,'Liquidity',external())
        note(s,.7,3.5,5.6,'Equity value',dcf_story())
        table(s,6.65,1.92,5.92,3.94,['Evidence','Location'],[['H1 group statements','Oct 14, pp16–20'],['Capex, billing, trademark','Oct 15 call, pp3–4, 13–14'],['Debt, contracts, CAMSO','FY26 notes 20, 42, 52'],['Peers and market inputs','Lineage; data/sources.csv'],['Calculation and controls','Funding Decision; validation.md']],ratios=[1,1.2],size=12)

