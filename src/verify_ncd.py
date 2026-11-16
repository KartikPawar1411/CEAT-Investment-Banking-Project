"""Rebuild the NCD case and its pricing outside the workbook formulas, then compare."""
import math
from results import *
from committee import F, FI
from ncd_case import CASE, PRICING as NP, ROW, PERIODS, SLOTS, HISTORY
import ncd_pricing as np_


def verify():
    count = 0

    def eq(x, y, what=''):
        nonlocal count
        assert math.isclose(x, y, abs_tol=1e-6, rel_tol=1e-9), (what, x, y)
        count += 1

    def ok(test, what):
        nonlocal count
        assert test, what
        count += 1

    def p(col, key):
        return v(NP, col + str(ROW[key]))

    # 1. Comparable table and indicative coupons against the CSV and the pure functions.
    rows, inputs = np_.load_comparables(), np_.load_inputs()
    good = np_.verified(rows)
    for r, row in zip(SLOTS, good):
        ok(v(NP, f'A{r}') == row['issuer'], 'comparable order')
        eq(v(NP, f'G{r}'), row['coupon_pct'], 'coupon')
        eq(v(NP, f'H{r}'), row['benchmark_gsec_yield_pct'], 'benchmark')
        eq(v(NP, f'I{r}'), np_.spread_bps(row['coupon_pct'], row['benchmark_gsec_yield_pct']), 'spread')
        eq(row['spread_bps'], np_.spread_bps(row['coupon_pct'], row['benchmark_gsec_yield_pct']), 'CSV spread')
    for r in list(SLOTS)[len(good):]:
        ok(all(v(NP, f'{c}{r}') is None for c in 'GHI'), 'unverified rows stay blank')
    summary = np_.pricing_summary(rows, inputs)
    for key, tenor in [('y3', 3), ('y5', 5)]:
        s = summary[tenor]
        eq(p('B', key), s['benchmark']); eq(p('C', key), min(s['spreads'])); eq(p('D', key), max(s['spreads']))
        eq(p('E', key), s['coupon'][0]); eq(p('F', key), s['coupon'][1]); eq(p('G', key), len(s['spreads']))
        eq(p('H', key), s['coupon_all'][0]); eq(p('I', key), s['coupon_all'][1])
    tenor, coupon, size = p('B', 'tenor'), p('B', 'coupon'), p('B', 'size')
    ok(tenor in (3, 5), 'tenor is 3 or 5')
    eq(coupon, summary[int(tenor)]['coupon'][1] / 100, 'coupon used'); eq(size, v(FI, 'B5'), 'issue size')

    # 2. The integrated case: financing identities, and operations identical to On time.
    def q(r, c):
        return v(CASE, c + str(r))
    floor, tax = v(FI, 'B4'), v(AS, 'B11')
    prior = {'cash': v(BS, 'H15'), 'debt': v(BS, 'H23'), 'bridge': 0, 'term': 0}
    unassisted = prior['cash']
    for k in range(18):
        c, b = get_column_letter(k + 3), get_column_letter(k + 2)

        def g(r):
            return q(r, c)
        for r in list(range(5, 19)) + list(range(23, 36)) + [38, 40]:
            eq(g(r), v('On time', c + str(r)), f'operating row {r}')
        eq(g(36), size if k == 0 else 0, 'draw'); eq(g(37), prior['term'] if tenor * 4 == k else 0, 'redemption')
        eq(g(19), ((q(45, b) + q(49, b)) * v(FI, 'B26') + prior['bridge'] * v(FI, 'B27') + (prior['term'] + g(36)) * coupon) / 4, 'interest')
        eq(g(12) - sum(g(r) for r in [13, 14, 15, 17, 19, 21]), g(22), 'net income')
        eq(prior['cash'] + g(39) + g(40) + g(43), g(44), 'cash roll')
        eq(prior['debt'] + g(36) + g(42) - g(34) - g(35) - g(37), g(48), 'debt roll')
        eq(g(44) + g(23) + g(24) + g(50) + g(51), g(25) + g(48) + g(49) + g(53) + g(54), 'balance sheet')
        saved = prior['bridge'] * v(FI, 'B27') / 4
        unassisted += g(39) + g(40) + g(43) - g(42) + saved - (max(0, g(20) + saved) - max(0, g(20))) * tax
        eq(unassisted, g(61), 'cash before bridge')
        ok(g(44) >= floor - 1e-7 and g(47) >= -1e-7, 'funded cash holds the floor')
        prior = {'cash': g(44), 'debt': g(48), 'bridge': g(47), 'term': g(46)}

    # 3. Coverage, leverage and cash metrics from the pure functions.
    for col, (name, lo, hi) in zip('BCDEF', PERIODS):
        span = [get_column_letter(i) for i in range(column_index(lo), column_index(hi) + 1)]

        def flow(r):
            return sum(q(r, c) for c in span) + (v(IS, HISTORY[r]) if name == 'FY27E' else 0)
        eq(p(col, 'interest'), flow(19)); eq(p(col, 'ebitda'), flow(16)); eq(p(col, 'ebit'), flow(18))
        eq(p(col, 'cover'), np_.interest_coverage(flow(16), flow(19)), 'EBITDA cover')
        eq(p(col, 'ebit_cover'), np_.interest_coverage(flow(18), flow(19)), 'EBIT cover')
        eq(p(col, 'net_debt'), np_.net_debt(q(48, hi), q(49, hi), q(44, hi)))
        eq(p(col, 'leverage'), np_.net_debt_to_ebitda(q(48, hi), q(49, hi), q(44, hi), flow(16), 4 if lo == hi else 1), 'leverage')
        eq(p(col, 'low_pre'), min(q(61, c) for c in span)); eq(p(col, 'low_funded'), min(q(44, c) for c in span))
        eq(p(col, 'headroom'), min(q(61, c) for c in span) - floor); eq(p(col, 'bridge'), q(47, hi))

    # 4. Comparison rows tie to the unchanged Funding Decision sheet; term-loan arithmetic.
    for key, fr in [('on_time', 4), ('external', 6)]:
        ok(p('B', key) == v(F, f'B{fr}'), 'first breach'); eq(p('C', key), v(F, f'C{fr}')); eq(p('D', key), v(F, f'E{fr}')); eq(p('E', key), v(F, f'H{fr}'))
    window = 'CDEFGH'
    eq(p('C', 'ncd'), max(q(47, c) for c in window)); eq(p('D', 'ncd'), min(q(61, c) for c in window)); eq(p('E', 'ncd'), max(q(48, c) for c in window))
    low, high = summary[int(tenor)]['coupon']
    loan = (np_.value(inputs, 'term_loan_rate_low'), np_.value(inputs, 'term_loan_rate_high'))
    eq(p('B', 'ncd_rate'), low); eq(p('C', 'ncd_rate'), high); eq(p('B', 'loan_rate'), loan[0]); eq(p('C', 'loan_rate'), loan[1])
    eq(p('B', 'premium'), (low - loan[1]) * 100); eq(p('C', 'premium'), (high - loan[0]) * 100)
    eq(p('D', 'ncd_rate'), low / 100 * size); eq(p('E', 'loan_rate'), loan[1] / 100 * size)
    eq(p('D', 'premium'), (low - loan[1]) / 100 * size); eq(p('E', 'premium'), (high - loan[0]) / 100 * size)

    # 5. The existing decision is read, never written; a contradiction stops the build.
    ok(p('B', 'decision') == v(F, 'B10'), 'decision is read from Funding Decision')
    ok(p('B', 'result') == ('CLEARS FLOOR' if p('B', 'pre_low') >= floor - .001 else 'GAP REMAINS'), 'floor test')
    ok(p('B', 'reading') == 'CONSISTENT', 'NCD case contradicts the existing recommendation: report to the user and stop')
    for r in range(ROW['controls'], ROW['controls'] + 4):
        ok(v(NP, f'D{r}') == 'PASS', f'NCD control {r}')
    return count


def column_index(letter):
    from openpyxl.utils import column_index_from_string
    return column_index_from_string(letter)


if __name__ == '__main__':
    total = verify()
    report = ROOT / 'reports/validation.md'
    if report.exists() and 'CEAT_CHECK_MODEL' not in os.environ:
        with report.open('a', encoding='utf-8') as f:
            f.write(f"\n## NCD funding case\n\n{total} checks passed. Rebuilt the comparable spreads and indicative coupons from data/comparable_ncd_issues.csv, "
                    f"the sixth case's interest, cash, debt and balance-sheet roll-forwards through FY31, and its coverage and leverage metrics. "
                    f"Operations equal the On time case in every quarter. NCD case against the floor: **{v(NP, 'B' + str(ROW['result']))}**; "
                    f"against the existing decision: **{v(NP, 'B' + str(ROW['reading']))}**.\n")
    print(total, 'NCD case checks passed.')
