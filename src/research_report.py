"""Publish the interview research memo with linked source evidence and model tables."""
from results import *
def build():
    sources={r['ID']:r for r in source_rows()}
    def cites(*ids):return ' '.join('['+k+']('+sources[k]['Original URL']+')' for k in ids)
    def table(sheet,items,cols,labels):return markdown_table(['INR crore unless noted']+labels,metric_rows(sheet,items,cols))
    fy=['FY22','FY23','FY24','FY25','FY26'];c=price(v(TC,'B8'));pv=v(DC,'B33');lo,mid,hi=series(VS,6,'BCD')
    rr=markdown_table(['Method','P25 / bear','Median / base','P75 / bull','Mid vs close'],[[v(VS,'A'+str(r)),*[price(x) for x in series(VS,r,'BCD')],pct(v(VS,'E'+str(r)))] for r in range(5,10)])
    comps=markdown_table(['Company / period','Revenue','EBITDA','EBIT','Parent PAT','EV/sales','EV/EBITDA','EV/EBIT','P/E'],[[v(TC,'A'+str(r)),*[n(x) for x in series(TC,r,'JKLM')],*[mult(x) for x in series(TC,r,'NOPQ')]] for r in range(5,12)])
    bridges=markdown_table(['Company','NSE close ₹','Shares cr','Mkt cap','Debt incl leases','NCI','Cash + deposits','Investments','EV'],[[v(TC,'A'+str(r)).split(' ·')[0],f'{v(TC,"B"+str(r)):,.2f}',f'{v(TC,"C"+str(r)):.7f}',*[one(x) for x in series(TC,r,'DEFGHI')]] for r in range(5,9)])
    sens=markdown_table(['WACC / g']+[pct(x) for x in series(SE,5)],[[pct(v(SE,'A'+str(r)))]+[n(x) for x in series(SE,r)] for r in range(6,11)])
    op=markdown_table(['Growth Δ / margin Δ']+[pct(x) for x in series(SE,15)],[[pct(v(SE,'A'+str(r)))]+[n(x) for x in series(SE,r)] for r in range(16,21)])
    cases=markdown_table(['Case','Growth Δ','Margin Δ','WACC Δ','Terminal g Δ','₹/share','vs close'],[[v(SC,'A'+str(r)),*[pct(x) for x in series(SC,r,'BCDE')],price(v(SC,'F'+str(r))),pct(v(SC,'G'+str(r)))] for r in range(5,8)])
    matrix=markdown_table(['Option','Value','Fit','Capital efficiency','Execution ease','Risk control','Speed','LT growth','Weighted / 5'],[[v(PE,'A'+str(r)),*[str(int(x)) for x in series(PE,r,'BCDEFGH')],f'{v(PE,"I"+str(r)):.2f}'] for r in range(42,47)])
    t=f"""# CEAT Limited — Strategic Advisory, Corporate Valuation & Growth Opportunities

**Investment Banking Pitch Book | Valuation as of 6 November 2026**  
NSE CEATLTD · BSE 500878 · Automobile Components / Tyres and Rubber Manufacturing · India. Financial amounts are consolidated INR crore unless specified. FY26 means 1 April 2025 to 31 March 2026. Per-share values are INR. Independent academic simulation prepared in November 2026.

## 1. Executive summary

## 2. Company background

CEAT began manufacturing in India in 1958 as CEAT Tyres of India Limited and adopted its present name in 1990. Today the RPG Group company sells passenger car and utility vehicle tyres, two- and three-wheeler tyres, truck and bus tyres, light commercial tyres, and off-highway tyres and tracks. Manufacturing and brand-led replacement distribution connect it to end users. OEM relationships create original-fitment volume and a route to subsequent replacement purchases. {cites('AR23','AR26','MIX')}

The FY26 accounts include ₹1,120.46 crore of business-combination cash outflow, separate from organic capex. CAMSO added a Sri Lankan manufacturing footprint and off-highway tracks and construction tyres. Management reported less than 50% utilization at the Sri Lankan facility in October. Transitioning upstream equipment and retaining overseas customers are earlier priorities than buying another asset. {cites('AR26','CALL')}

## 3. Business model

**Reported operating profile.** CEAT disclosed 50+ OEM relationships and 61,000+ touchpoints. A touchpoint is broader than a dedicated dealership. The standalone H1 channel split was replacement 50%, OEM 30% and exports 20%. The product split was two/three-wheelers 28%, truck/bus 27%, passenger car/utility vehicles 23%, off-highway 16% and LCV/other 6%. These are two distinct views of the same standalone revenue. Adding the two distributions would double count sales. {cites('MIX')}

**Geographic exposure.** FY26 consolidated revenue from contracts with customers was ₹15,479.51 crore, including ₹12,168.44 crore in India and ₹3,311.07 crore outside India ({pct(v(PE,'C37'))}). FY25 outside-India revenue was ₹2,458.40 crore on ₹13,020.70 crore of contracts. Other operating revenue accounts for the difference to group revenue from operations. Market and product mixes are standalone disclosures, and a consolidated product-profit split was unavailable. {cites('AR26')}

**Capital and control.** The September pattern shows 40,450,092 issued shares. Promoters held 47.29%, the public 52.37% and the employee trust 0.34%. Within public holdings, domestic institutions held 23.26% of the company and foreign institutions 13.41%. The market-cap and valuation denominator uses all listed shares. Excluding 138,229 trust shares would increase per-share value by approximately 0.34%. {cites('SHP')}

## 4. Industry analysis

| Evidence | Period and scope | Advisory implication |
|---|---|---|
| Estimated tyre-industry turnover of about ₹1,00,000 crore | ATMA FY25 estimate. Exact first publication day unverified. | Provides scale. Global consolidated issuer sales cannot be divided by this domestic base to infer market shares. |
| Tyre exports rose from ₹25,057 crore to ₹27,312 crore | FY25–FY26, IBEF on 4 Jun 2026 citing ATMA | Export franchises diversify volume, with freight, import barriers and currency movements affecting net realization. |
| Domestic passenger, commercial and two-wheeler sales grew 7.9%, 12.6% and 10.7% | SIAM on 14 Apr 2026. FY26 levels of 46.43 lakh, 10.80 lakh and 2.17 crore vehicles | OEM demand tracks production plans. The installed fleet creates later replacement demand driven by mileage, loading, tyre life and retreading. |
| Seven-company sample revenue rose 15.4% in Q1 FY27 | ICRA, 30 Sep 2026 | Realization increases can lift revenue even as raw material costs erode contribution. |
| Domestic tyre volume demand forecast to grow 5–7% and operating margins to fall about 200 bp | ICRA FY27 outlook, published 30 Sep 2026 | Sector forecast provides a volume anchor. CEAT revenue also reflects price, mix and the acquisition perimeter. |

{cites('ATMA','EXPORT','SIAM','ICRA')}

Natural rubber drives carcass and tread costs. Synthetic rubber, carbon black and other petrochemical inputs transmit crude-price changes. Inventory residence time and OEM reset schedules can delay price recovery. In Q2 management estimated another 8–9% sequential raw-material cost increase. Replacement channels can reprice quicker, although local competitors and dealer inventory constrain pass-through. A weaker rupee raises import costs and changes the INR value of export receipts. The net hedge depends on currency, procurement timing and contractual terms. {cites('CALL','AR26')}

Infrastructure activity and freight utilization affect commercial replacements and off-highway demand. Plant tooling, curing presses, homologation, channel credit and distribution density raise entry costs. Imports supplied less than 5% of demand in ICRA’s September review despite 22% year-on-year import-volume growth in Q1. GST rationalisation supported demand in the second half of FY26 according to CEAT. Rubber sourcing, waste-tyre producer responsibility and energy efficiency also affect manufacturing economics. A verified domestic concentration ratio and consistent industry-wide utilization rate were unavailable. {cites('ICRA','AR26','MRFAR')}

## 5. Historical financial performance

{table(IS,[('Revenue',5,n),('Material cost incl. inventories',9,n),('Employee expense',10,n),('Other operating expense',11,n),('Operating EBITDA',12,n),('D&A',13,n),('Operating EBIT',14,n),('Finance cost',15,n),('Other income',16,n),('JV / associate profit',17,n),('Exceptional charges',18,n),('PBT incl. JV',19,n),('Tax',20,n),('Group PAT',21,n),('Attributable PAT',22,n)],'BCDEF',fy)}

**Analyst reconciliation.** Operating EBITDA equals sales less material consumption, purchases, inventory expense, staff cost and other operating expense. Operating EBIT deducts D&A. PBT on the model's comparable basis adds other income and JV earnings and deducts interest and exceptional charges. Group PAT includes minority earnings. P/E and ROE use owner-attributable profit. Management includes JV earnings in its presentation EBITDA, explaining most of the difference between its 13.2% FY26 margin and our {pct(v(RA,'F6'))}. Both DCF cash flows and EV multiples exclude equity-accounted earnings, so the equity bridge restores the carrying value of the JV. {cites('AR23','AR24','AR26','MIX')}

{table(IS,[('Revenue',5,n),('Operating EBITDA',12,n),('D&A',13,n),('EBIT',14,n),('Finance cost',15,n),('Group PAT',21,n),('Attributable PAT',22,n)],'GHI',['Q2 FY27','H1 FY27','H1 FY26'])}

Q2 reported ₹4,762 crore of sales against ₹3,773 crore a year earlier, while group PAT fell to ₹112 crore from ₹186 crore. H1's lower gross margin and higher finance and depreciation costs reduced parent earnings despite higher volumes and price realizations. October disclosures round amounts to whole crore; the comparative H1 line items can therefore differ from total PAT by ₹1 crore. {cites('H1','MIX','CALL')}

{table(BS,[('Assets',5,n),('Total equity',6,n),('Current assets incl. held for sale',8,n),('Current liabilities',9,n),('Non-current liabilities',10,n),('Inventory',11,n),('Trade receivables',12,n),('Cash equivalents',15,n),('PPE',20,n),('Borrowings',23,n),('Leases',24,n),('Net debt incl. leases',26,n),('Trade NWC',27,n)],'BCDEFH',fy+['Sep 26'])}

Net debt reached ₹4,033 crore at September versus ₹{n(v(BS,'F26'))} crore in March. Inventory rose by approximately ₹814 crore in six months. Reported cash was ₹32 crore. A current ratio below 1 reflects heavy trading-credit and short-term funding dependence. Cash alone understates available liquidity when committed lines exist, but undrawn facilities and covenant headroom require lender confirmation. {cites('AR26','H1')}

{table(CF,[('Operating cash flow',5,n),('Capex',6,n),('Investing cash flow',7,n),('Financing cash flow',8,n),('Cash interest paid',9,n),('Lease cash paid',10,n),('Net new borrowings',11,n),('WC cash contribution',12,n),('Cash after capex',15,n),('FCFE proxy incl. net borrowing',16,n)],'BCDEFH',fy+['H1 FY27'])}

CFO is the filed operating cash flow. CEAT classifies interest paid in financing. Cash after capex is CFO less cash purchases of PPE/intangibles, including CWIP and capital advances. The FCFE proxy also subtracts financing-classified cash interest and lease payments and adds net new borrowings. It measures debt-supported equity cash flow before acquisitions and shareholder distributions. Historical UFCF is independently reconstructed from operating EBIT, normalized tax, D&A, cash capex and changes in trade NWC. This narrower trade-NWC calculation excludes several operating balances in the statutory cash-flow statement. {cites('AR23','AR24','AR26','H1')}

## 6. Financial ratio analysis

{table(RA,[('Revenue growth',5,pct),('EBITDA margin',6,pct),('EBIT margin',7,pct),('Net margin',8,pct),('Current ratio',9,mult),('Borrowings / equity',10,mult),('ROE',11,pct),('ROIC',12,pct),('Net debt / EBITDA',13,mult),('Capex / sales',14,pct),('Historical UFCF proxy',16,n)],'BCDEF',fy)}

ROE divides parent PAT by the average opening and closing parent equity. ROIC divides normalized after-tax operating EBIT by average invested capital. Invested capital equals group equity plus borrowings and leases, less cash, JV interests and other investments. The first-year averages use March 2021 balances. The FY24 increase in returns followed a recovery in operating margin despite modest sales growth. FY26 ROIC of {pct(v(RA,'F12'))} only modestly exceeded the valuation-date WACC of {pct(v(WA,'B18'))}; the comparison is indicative because acquisition capital was deployed during the year. Measured FY26 growth includes the CAMSO purchase. {cites('AR22','AR23','AR24','AR26')}

## 7. Competitive landscape

MRF and Apollo each sold roughly twice CEAT's FY26 revenue. Their broader manufacturing footprints and volumes influence procurement scale, product development and fixed-cost absorption. MRF also carries a substantial investment portfolio. Apollo has a European business and FY26 restructuring and tax items. JK Tyre is closest on consolidated revenue and has truck/bus and Mexican exposure. CEAT's two-wheeler and replacement channels offer distribution reach, while CAMSO extends the business into tracks with different customers and utilization risks. Comparing EV/sales without controlling for margins would reward scale independently of cash generation. {cites('MRFAR','APFY','JKH1report','AR26','MIX')}

## 8. Peer selection methodology

| Initial peer | Treatment | Economic reason |
|---|---|---|
| MRF (NSE MRF) | FY26 set | Broad tyres, domestic brand and replacement presence. Larger scale and financial assets require a careful EV bridge. September LTM unavailable by cutoff. |
| Apollo Tyres (NSE APOLLOTYRE) | FY26 and September LTM | Overlapping replacement/OEM lines, with European manufacturing, restructuring charges and a one-off FY26 tax benefit. |
| JK Tyre & Industries (NSE JKTYRE) | FY26 and September LTM | Similar scale, truck/bus exposure and higher leverage. Restated prior-period H1 for the amalgamation. |
| Balkrishna Industries (NSE BALKRISIND) | Specialty reference only | Export-led off-highway economics resemble one CEAT growth business better than CEAT as a whole. |
| TVS Srichakra (NSE TVSSRICHAK) | Product / acquisition screen | Smaller business concentrated in two-wheeler and off-highway tyres, with different customer mix and utilization. |
| Goodyear India (BSE 500168) | Product reference only | Farm tyre exposure and multinational parent relationships limit comparability to the diversified consolidated business. |

Each selected company uses FY26 operating metrics in the primary set. September LTM is a second, two-company cross-check. MRF's June trailing period is excluded from that cross-section. A three-name median can move materially when any single observation changes. {cites('MRF26','APOLLO26','JK26','TVS')}

## 9. Comparable company valuation

{bridges}

EV = listed equity capitalization + borrowings + lease obligations + reported NCI − cash equivalents − eligible deposits − identified non-operating investments. Book values proxy claim and investment fair values. MRF uses the March balance sheet; other bridges use September. MRF includes ₹1,867.02 crore of 3–12 month deposits and excludes unclaimed dividends and restricted CSR balances. For the other issuers, bank accounts outside cash equivalents are retained where availability could not be established. JK Tyre's reported negative NCI is carried at book value. Enterprise values are calculated on 6 November; balance-sheet dates are proxies for the valuation date. {cites('MRFAR','APOLLOH127','JKH1report','H1','NSE 2026-11-06')}

{comps}

MRF’s separately dated June LTM revenue was ₹{n(v(TC,'J12'))} crore and operating EBITDA was ₹{n(v(TC,'K12'))} crore. Its June LTM EV/EBITDA was {mult(v(TC,'O12'))}. It carries zero weight in the September LTM statistics. {cites('MRFJune','MRFAR')}

LTM = audited FY26 + H1 FY27 − H1 FY26, using like-for-like consolidated earnings. Operating EBITDA for the peers equals pre-exceptional profit before equity-accounted earnings and tax, less other income, plus gross finance cost and D&A. P/E uses net profit attributable to owners, retaining tax and exceptional effects. MRF's primary annual report resolves an unpopulated ownership-attribution field in the exchange table. Its parent PAT differs from consolidated profit by less than ₹0.02 crore. {cites('MRFAR','APOLLO26','APOLLOH126','APOLLOH127','JKFYreport','JKH1report')}

{markdown_table(['FY26 sample','EV/sales','EV/EBITDA','EV/EBIT','P/E'],[[v(TC,'A'+str(r))]+[mult(x) for x in series(TC,r,'BCDE')] for r in range(15,21)])}

Applying the median EV/EBITDA multiple of {mult(v(TC,'C17'))} to CEAT operating EBITDA of ₹{n(v(IS,'F12'))} crore produces ₹{n(v(RV,'F6'))} crore of enterprise value. Subtracting the ₹{n(v(BS,'H31'))} crore net bridge yields ₹{n(v(RV,'G6'))} crore of equity, or {price(mid)} per listed share. CEAT's own FY26 EV/EBITDA is {pct(v(TC,'C21'))} above the peer median. Depreciation makes the EBIT method more sensitive to the age of assets and acquisition amortization. P/E incorporates differences in financing, taxes and exceptional charges. The same-method September LTM median is {price(v(RV,'I10'))} per share with two peers.

## 10. DCF valuation

## 11. WACC methodology

## 12. Sensitivity and scenario analysis

## 13. Valuation synthesis

## 14. Strategic alternatives

**A · Staged organic expansion.** Complete already-committed Nagpur two-wheeler and Chennai truck/bus and passenger radial investments. Management reported roughly ₹120 crore-plus of quarterly spending at Nagpur and about ₹280 crore at Chennai. Allocate further tooling to confirmed OEM nominations and replacement cohorts with positive incremental contribution. Test realized contribution, yields and receivable days before approving subsequent tranches. The upside is throughput on an existing channel; the risk is inventory accumulation before pricing recovers. {cites('CALL','MIX')}

**B · Hypothetical acquisition screens.** TVS Srichakra's two-wheeler and off-highway capacity offers product fit, but overlaps CEAT's organic investments. Its FY26 annual report describes ₹220 crore of additional approved capacity spend at Madurai. Test whether an alliance, plant-level agreement or asset acquisition could access a distinctive product or customer more cheaply than enterprise control. Indag Rubber's pre-cured tread and retreading materials offer a different route to fleet lifecycle service. Diligence should test casing quality, warranty risk, repeat fleet revenue, maintenance capex, customer concentration and promoter willingness. Public disclosures establish business fit alone. Buyer interest, seller availability, control premiums, deal values and synergies are unverified. Debt-financed control is difficult to support while H1 cash after capex is negative. A minority investment or milestone-based consideration could limit initial funding, subject to diligence and negotiated rights. {cites('TVS','INDAG','H1')}

**C · Financing alternatives.** An illustrative ₹1,000 crore program equals {pct(1000/v(TC,'D8'))} of CEAT's spot equity value. At 7.8%, all-debt funding adds ₹78 crore of annual pretax interest and about ₹58 crore after normalized tax. Gross debt rises from ₹4,065 crore to ₹5,065 crore before repayment. Issuing equity at the ₹3,545.80 reference price would create {1000/v(TC,'B8'):.3f} crore shares and {pct(1000/(v(TC,'D8')+1000))} post-issue dilution before fees and discounts. Internal funding preserves ownership but temporarily demands working-capital release or deferred capex. A convertible can defer cash interest or equity issuance in return for option value, covenants and potential dilution. Pricing and feasibility require lender or investor terms.

**D · Partnership / JV.** Pilot an overseas distributor for CAMSO tracks using minimum offtake, service obligations and capped support for inventory. A manufacturing or technology JV can share tooling and local homologation, but exclusivity, intellectual-property rights and channel conflict need contractual limits. Measure partner sell-through and warranty claims before expanding territory. CEAT already accounts for Sri Lankan joint ventures, providing experience with shared governance. {cites('AR26','CALL')}

**E · Strategic merger or sale.** A buyer could spread R&D and distribution expense over a larger base or use CEAT's Indian network. Industrial logic alone does not establish a control premium. Promoter consent, customer retention, competition review, pricing of minority interests and governance would drive executable value. Set the standalone DCF and trading benchmarks before discussing any potential offer. No buyer, mandate or negotiations are assumed.

## 15. Recommended strategic direction

## 16. Transaction and execution risks

| Risk | Early indicator | Proposed response |
|---|---|---|
| Rubber and crude costs outrun pricing | Contribution per kg, inventory carrying cost, OEM reset lag | Reset contract prices where possible and limit speculative inventory. |
| Volume or utilization disappoints | Orders versus rated capacity, dealer sell-through, CAMSO uptime | Stage tooling and use pilot agreements before capacity commitments. |
| Foreign exchange or export restrictions | Unhedged procurement and collections by currency, cross-border lead times | Match funding and purchase currency; model landed cost by market. |
| Debt service and refinancing | Short maturities, quarterly cash after capex, floating-rate reset | Pre-agree liquidity and test headroom before any binding acquisition. |
| Integration or product quality | First-pass yield, returns, technical approvals and warranty claims | Assign technical owners and escalate failures before volume ramps. |
| Valuation and control | WACC–g spread, implied terminal UFCF, synergies after integration cost | Test downside financing and independent standalone valuation before any premium. |

## 17. Limitations

## 18. References

The source register includes original URLs, financial periods, filing dates or availability evidence, retrieval date, and audit notes. The archived NSE panel includes an original file link for each observation. Cash-market prices use CLOSE_PRICE, EQ series. Excel sheet and row labels match the calculation tables in this memo.

"""
    for s in sources.values():
        if s['ID'].startswith('NSE ') and s['ID']!='NSE 2026-11-06':continue
        t+=f"- **{s['ID']}** · {s['Source']} · {s['Publication date / evidence']} · {s['Data retrieved']}. [{s['Document']}]({s['Original URL']})\n"
    t+='\n### Supporting figures\n\n'
    for path in sorted((ROOT/'charts').glob('0*.png')):t+=f'![{path.stem[3:].replace("_"," ")}](../charts/{path.name})\n\n'
    from committee import report
    publish_path('reports/CEAT_Investment_Banking_Research_Report.md').write_text(report(t),encoding='utf-8')
if __name__=='__main__':build()

