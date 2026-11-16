"""Sixth funding case: the tranche funded by a non-convertible debenture. Adds two sheets and edits none."""
from datetime import date
from openpyxl.styles import Font, PatternFill, Alignment
from expansion_model import sheet, setcell, scenario, I, IS, L, PCT, NUM
from ncd_pricing import load_comparables, load_inputs, verified, manual

CASE = 'NCD'
PRICING = 'NCD Pricing'
Q = "'" + CASE + "'!"
P = "'" + PRICING + "'!"
POINTS = '0.00'
BPS = '0'
TIMES = '0.0"x"'
SLOTS = range(4, 14)  # comparable rows; spare slots take manual entries
# Fixed addresses, shared with the slide, the verifier and the tests.
ROW = {'rating': 16, 'rating2': 17, 'y3': 20, 'y5': 21, 'size': 25, 'tenor': 26, 'coupon': 27,
       'interest': 31, 'ebitda': 32, 'ebit': 33, 'cover': 34, 'ebit_cover': 35, 'net_debt': 36, 'leverage': 37,
       'low_pre': 38, 'low_funded': 39, 'floor': 40, 'headroom': 41, 'bridge': 42,
       'on_time': 45, 'external': 46, 'ncd': 47, 'ncd_rate': 50, 'loan_rate': 51, 'premium': 52,
       'decision': 55, 'pre_low': 56, 'result': 57, 'reading': 58, 'controls': 61}
PERIODS = [('Q3 FY27', 'C', 'C'), ('Q4 FY27', 'D', 'D'), ('FY27E', 'C', 'D'), ('FY28E', 'E', 'H'), ('FY29E', 'I', 'L')]
HISTORY = {16: 'H12', 18: 'H14', 19: 'H15'}  # H1 FY27 actuals completing FY27, as in FY Forecast


def band(w, r, heads):
    for c, text in enumerate(heads, 1):
        z = w.cell(r, c, text)
        z.fill = PatternFill('solid', fgColor='18394B')
        z.font = Font(name='Calibri', bold=True, color='FFFFFF', size=10)
        z.alignment = Alignment(wrap_text=True, vertical='center')
    w.row_dimensions[r].height = 34


def case_sheet(wb):
    """Same engine as the other cases. Only the term draw, its redemption and its coupon differ from On time."""
    scenario(wb, CASE)
    w = wb[CASE]
    size, tenor, coupon = P + '$B$%d' % ROW['size'], P + '$B$%d' % ROW['tenor'], P + '$B$%d' % ROW['coupon']
    for k in range(18):
        a, p = L(k + 3), L(k + 2)
        setcell(w, 36, k + 3, '=' + size if k == 0 else '=0')
        setcell(w, 37, k + 3, f'=IF({tenor}*4={k},{p}46,0)')
        setcell(w, 19, k + 3, f"=(({p}45+{p}49)*{I}$B$26+{p}47*{I}$B$27+({p}46+{a}36)*{coupon})/4")
    w['A79'] = ('NCD case: issue drawn at the start of Q3 FY27, fixed annual coupon accrued quarterly, bullet '
                'redemption at the selected tenor. Operations, capex and the tranche schedule equal On time.')


def pricing_sheet(wb):
    rows, inputs = load_comparables(), load_inputs()
    w = sheet(wb, PRICING, 'NCD funding case | comparable issues, indicative coupon and credit metrics',
              ['Comparable NCD issue', 'Rating', 'Agency', 'Issue date', 'Tenor, years', 'Size, ₹ cr', 'Coupon, %',
               'Matched G-sec, %', 'Spread, bps', 'Source date', 'Primary source', 'Notes'])
    w['A2'] = ('Blue = sourced input   •   Blank = not verified from a primary source; enter by hand, then copy '
               'the spread formula down   •   Sources and retrieval dates in data/comparable_ncd_issues.csv')
    if len(rows) > len(SLOTS):
        raise ValueError('More comparable rows than slots on the NCD Pricing sheet')
    for r, row in zip(SLOTS, verified(rows) + manual(rows)):
        w.cell(r, 1, row['issuer'])
        w.cell(r, 2, row['credit_rating'] or None)
        w.cell(r, 3, row['rating_agency'] or None)
        for c, key, fmt in [(4, 'issue_date', 'dd mmm yy'), (10, 'source_date', 'dd mmm yy')]:
            if row[key]:
                setcell(w, r, c, date.fromisoformat(row[key]), fmt)
        for c, key, fmt in [(5, 'tenor_years', '0'), (6, 'issue_size_inr_cr', NUM), (7, 'coupon_pct', POINTS),
                            (8, 'benchmark_gsec_yield_pct', POINTS)]:
            if row[key] is not None:
                setcell(w, r, c, row[key], fmt)
        if row in verified(rows):
            setcell(w, r, 9, f'=(G{r}-H{r})*100', BPS)
        link = w.cell(r, 11, 'Open filing')
        link.hyperlink = row['source_url']
        link.font = Font(name='Calibri', size=11, color='234A9A', underline='single')
        w.cell(r, 12, row['notes'])
    band(w, 15, ['CEAT long-term rating', 'Rating', 'Date', 'Document', 'Source'])
    for r, key, label in [(ROW['rating'], 'ceat_rating_latest', 'Latest rating rationale'),
                          (ROW['rating2'], 'ceat_rating_second', 'Second agency')]:
        item = inputs[key]
        w.cell(r, 1, label)
        w.cell(r, 2, item['value'])
        setcell(w, r, 3, date.fromisoformat(item['as_of']), 'dd mmm yy')
        w.cell(r, 4, item['source'])
        link = w.cell(r, 5, 'Open')
        link.hyperlink = item['source_url']
    span = f'$I${SLOTS[0]}:$I${SLOTS[-1]}'
    tenors = f'$E${SLOTS[0]}:$E${SLOTS[-1]}'
    as_of = date.fromisoformat(inputs['gsec_zero_5y_current']['as_of'])
    band(w, 19, [f'Indicative coupon | CCIL zero-coupon G-sec, {as_of:%d %b %Y}', 'Benchmark, %', 'Spread low, bps',
                 'Spread high, bps', 'Coupon low, %', 'Coupon high, %', 'Comparables used', 'All-sample low, %',
                 'All-sample high, %'])
    for r, tenor in [(ROW['y3'], 3), (ROW['y5'], 5)]:
        other = f'((({tenors}<>{tenor})+({span}=""))>0)'  # SUMPRODUCT forces array evaluation in every Excel version
        w.cell(r, 1, f'{tenor}-year NCD')
        setcell(w, r, 2, float(inputs[f'gsec_zero_{tenor}y_current']['value']), POINTS)
        setcell(w, r, 3, f'=SUMPRODUCT(MIN({span}+1E9*{other}))', BPS)
        setcell(w, r, 4, f'=SUMPRODUCT(MAX({span}-1E9*{other}))', BPS)
        setcell(w, r, 5, f'=B{r}+C{r}/100', POINTS)
        setcell(w, r, 6, f'=B{r}+D{r}/100', POINTS)
        setcell(w, r, 7, f'=COUNTIFS({tenors},{tenor},{span},"<>")', '0')
        setcell(w, r, 8, f'=B{r}+MIN({span})/100', POINTS)
        setcell(w, r, 9, f'=B{r}+MAX({span})/100', POINTS)
    w['A22'] = ('Coupon = current matched-tenor benchmark + lowest / highest spread at issue among same-tenor '
                'comparables. All-sample columns apply the full spread range. No rating-notch or new-issue premium added.')
    band(w, 24, ['NCD case terms', 'Value', 'Basis'])
    for r, label, val, fmt, basis in [
            (ROW['size'], 'Issue size, ₹ crore', "='Funding Inputs'!B5", NUM, 'Sized to the discretionary tranche.'),
            (ROW['tenor'], 'Tenor selected, years', int(float(inputs['case_tenor_years']['value'])), '0',
             'Analyst choice; 3 or 5. Five matches CEAT Series 4 and avoids refinancing inside the forecast.'),
            (ROW['coupon'], 'Coupon used', f"=IF(B{ROW['tenor']}=3,F{ROW['y3']},F{ROW['y5']})/100", '0.00%',
             'Upper end of the same-tenor indicative range. Fixed, paid annually, accrued quarterly.')]:
        w.cell(r, 1, label)
        setcell(w, r, 2, val, fmt)
        w.cell(r, 3, basis)
    w['A28'] = 'Unsecured bullet issue drawn at the start of Q3 FY27. No arranger fee, stamp duty or listing cost modeled.'
    band(w, 30, ['NCD case | credit metrics, ₹ crore'] + [name for name, _, _ in PERIODS])
    labels = {'interest': 'Interest cost', 'ebitda': 'Operating EBITDA', 'ebit': 'Operating EBIT',
              'cover': 'EBITDA / interest', 'ebit_cover': 'EBIT / interest',
              'net_debt': 'Net debt incl. leases, period end', 'leverage': 'Net debt / EBITDA¹',
              'low_pre': 'Minimum cash before bridge', 'low_funded': 'Minimum funded cash', 'floor': 'Cash floor',
              'headroom': 'Pre-bridge headroom / (gap) to floor', 'bridge': 'Bridge outstanding, period end'}
    for key, label in labels.items():
        w.cell(ROW[key], 1, label)
    for c, (name, lo, hi) in enumerate(PERIODS, 2):
        x = L(c)

        def flow(row):
            return f'SUM({Q}{lo}{row}:{hi}{row})' + (f'+{IS}{HISTORY[row]}' if name == 'FY27E' else '')
        annual = '*4' if lo == hi else ''
        cells = {'interest': flow(19), 'ebitda': flow(16), 'ebit': flow(18),
                 'cover': f"{x}{ROW['ebitda']}/{x}{ROW['interest']}",
                 'ebit_cover': f"{x}{ROW['ebit']}/{x}{ROW['interest']}",
                 'net_debt': f'{Q}{hi}48+{Q}{hi}49-{Q}{hi}44',
                 'leverage': f"{x}{ROW['net_debt']}/({x}{ROW['ebitda']}{annual})",
                 'low_pre': f'MIN({Q}{lo}61:{hi}61)', 'low_funded': f'MIN({Q}{lo}44:{hi}44)',
                 'floor': f'{I}$B$4', 'headroom': f"{x}{ROW['low_pre']}-{x}{ROW['floor']}", 'bridge': f'{Q}{hi}47'}
        for key, formula in cells.items():
            setcell(w, ROW[key], c, '=' + formula, TIMES if key in ('cover', 'ebit_cover', 'leverage') else NUM)
    w['A43'] = ('¹ Quarter columns annualise that quarter’s EBITDA (×4). FY27E adds reported H1 FY27 to the two '
                'forecast quarters. Cash minimums cover forecast quarter-ends only; September opened at ₹32cr.')
    band(w, 44, ['Case comparison | 18 months to Mar 2028', 'First floor breach', 'Peak bridge', 'Pre-bridge low',
                 'Peak gross loans', 'FY28 interest', 'FY28 EBITDA / interest', 'FY28 net debt / EBITDA'])
    for key, name, label in [('on_time', 'On time', 'On time (no term issue)'),
                             ('external', 'External', 'External (₹550cr illustrative term issue)'),
                             ('ncd', CASE, 'NCD (this case)')]:
        r, q = ROW[key], "'" + name + "'!"
        w.cell(r, 1, label)
        setcell(w, r, 2, f'=IFERROR(INDEX({q}C3:H3,1,MATCH(1,{q}C65:H65,0)),"None")', 'General')
        for c, formula, fmt in [(3, f'MAX({q}C47:H47)', NUM), (4, f'MIN({q}C61:H61)', NUM),
                                (5, f'MAX({q}C48:H48)', NUM), (6, f'SUM({q}E19:H19)', NUM),
                                (7, f'SUM({q}E16:H16)/SUM({q}E19:H19)', TIMES),
                                (8, f'({q}H48+{q}H49-{q}H44)/SUM({q}E16:H16)', TIMES)]:
            setcell(w, r, c, '=' + formula, fmt)
    band(w, 49, ['NCD versus bank term loan', 'Rate low, %', 'Rate high, %', 'Annual interest low',
                 'Annual interest high', 'Basis'])
    r, size = ROW['ncd_rate'], f"$B${ROW['size']}"
    w.cell(r, 1, 'NCD, selected tenor (fixed, bullet, unsecured)')
    setcell(w, r, 2, f"=IF(B{ROW['tenor']}=3,E{ROW['y3']},E{ROW['y5']})", POINTS)
    setcell(w, r, 3, f"=IF(B{ROW['tenor']}=3,F{ROW['y3']},F{ROW['y5']})", POINTS)
    w.cell(r, 6, 'Indicative range above.')
    r = ROW['loan_rate']
    w.cell(r, 1, 'Bank term loan, as reported (floating, amortising, secured)')
    setcell(w, r, 2, float(inputs['term_loan_rate_low']['value']), POINTS)
    setcell(w, r, 3, float(inputs['term_loan_rate_high']['value']), POINTS)
    w.cell(r, 6, 'AR26 consolidated note 20, PDF p157: floating 7.15–7.8% p.a. at 31 Mar 2026. Not a current quote.')
    for r in (ROW['ncd_rate'], ROW['loan_rate']):
        setcell(w, r, 4, f'=B{r}/100*{size}')
        setcell(w, r, 5, f'=C{r}/100*{size}')
    r = ROW['premium']
    w.cell(r, 1, 'NCD premium over loan: narrowest / widest, bps and ₹ crore a year')
    setcell(w, r, 2, f"=(B{ROW['ncd_rate']}-C{ROW['loan_rate']})*100", BPS)
    setcell(w, r, 3, f"=(C{ROW['ncd_rate']}-B{ROW['loan_rate']})*100", BPS)
    setcell(w, r, 4, f'=B{r}/10000*{size}')
    setcell(w, r, 5, f'=C{r}/10000*{size}')
    w.cell(r, 6, 'Narrowest = NCD low less loan high. Widest = NCD high less loan low.')
    band(w, 54, ['Consistency with the existing recommendation', 'Value', 'Reading'])
    for key, label, formula, reading in [
            ('decision', 'Existing release decision', "'Funding Decision'!B10", 'Unchanged; read from Funding Decision.'),
            ('pre_low', 'NCD case pre-bridge low, ₹ crore', f"D{ROW['ncd']}", 'Lowest quarter-end cash through Mar 2028 before any balancing facility.'),
            ('result', 'NCD case against the floor', f"IF(B{ROW['pre_low']}>={I}$B$4-0.001,\"CLEARS FLOOR\",\"GAP REMAINS\")", 'Tests the NCD alone, without a bridge.'),
            ('reading', 'Against the existing decision', f"IF(AND(B{ROW['result']}=\"CLEARS FLOOR\",B{ROW['decision']}=\"DEFER / RESIZE FUNDING\"),\"CONTRADICTS\",\"CONSISTENT\")", 'A contradiction must be escalated; this sheet never rewrites the decision.')]:
        w.cell(ROW[key], 1, label)
        setcell(w, ROW[key], 2, '=' + formula, NUM if key == 'pre_low' else 'General')
        w.cell(ROW[key], 3, reading)
    band(w, 60, ['Controls', 'Residual', 'Tolerance', 'Status'])
    controls = [(f'NCD | {name}', f'MAX(MAX({Q}C{row}:T{row}),-MIN({Q}C{row}:T{row}))')
                for row, name in [(56, 'balance sheet'), (57, 'cash movement'), (58, 'borrowing movement')]]
    controls.append(('NCD operations equal On time (sales to EBIT)', f"SUMPRODUCT(ABS({Q}C12:T18-'On time'!C12:T18))"))
    for r, (label, formula) in enumerate(controls, ROW['controls']):
        w.cell(r, 1, label)
        setcell(w, r, 2, '=' + formula)
        setcell(w, r, 3, .00001, '0.00000')
        setcell(w, r, 4, f'=IF(ABS(B{r})<C{r},"PASS","FAIL")', 'General')
    w['A67'] = ('Benchmark is the CCIL Nelson-Siegel-Svensson zero-coupon G-sec rate at the issue tenor on the allotment '
                'date; coupons are annual-pay. Spreads are therefore approximate and comparable only with each other.')
    w['A68'] = ('Agency leverage tests use wider debt definitions (acceptances, dealer deposits, bill discounting) and are '
                'not reproduced here. Net debt above is borrowings plus leases less cash.')
    w.column_dimensions['A'].width = 52
    for col, width in zip('BCDEFGHIJKL', [19, 17, 17, 17, 17, 17, 17, 17, 14, 16, 90]):
        w.column_dimensions[col].width = width


def add_ncd(wb):
    case_sheet(wb)
    pricing_sheet(wb)
