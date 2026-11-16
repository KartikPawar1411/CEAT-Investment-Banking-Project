"""Slide 19: the NCD funding case. Appended after the close so slides 1–18 keep their content and numbers."""
from committee import *
from ncd_case import PRICING as NP, ROW, PERIODS


def p(col, key):
    return v(NP, col + str(ROW[key]))


def verdict():
    floor, low = cv(FI, 'B4'), cash(p('B', 'pre_low'))
    if p('B', 'reading') != 'CONSISTENT':
        return f"The NCD case clears the {floor} floor on its own and contradicts the existing decision, {outcome()}. Escalate before relying on either."
    if p('B', 'result') == 'CLEARS FLOOR':
        return f"The NCD keeps quarter-end cash at or above the {floor} floor without a bridge. The existing decision, {outcome()}, stands."
    return f"The NCD narrows the gap but does not close it: cash before a bridge still falls to {low} against the {floor} floor. The existing decision, {outcome()}, stands."


def coupon_range(key):
    return f"{p('E', key):.2f}–{p('F', key):.2f}%"


def place_ncd(kit):
    base, table, stat, note, txt = kit
    s = base(f"A {cash(p('B', 'size'))} NCD prices near {coupon_range('y5')} and still needs a {cash(p('C', 'ncd'))} bridge",
             'Debt capital markets | sixth funding case',
             'NCD Pricing and NCD sheets; data/comparable_ncd_issues.csv (issuer filings); India Ratings 3 Jul 2026; CCIL zero-coupon rates 12 Nov 2026; AR26 note 20.',
             verdict())
    for x, key, years in [(.64, 'y5', 5), (4.68, 'y3', 3)]:
        stat(s, x, 1.9, 3.87, coupon_range(key), f'{years}-year indicative coupon',
             f"{years}-year G-sec {p('B', key):.2f}% plus {p('C', key):.0f}–{p('D', key):.0f} bp from {p('G', key):.0f} same-tenor issues. CEAT: {p('B', 'rating')}.")
    stat(s, 8.73, 1.9, 3.87, f"{p('B', 'premium'):.0f}–{p('C', 'premium'):.0f} bp", 'NCD cost over bank loans',
         f"Reported loans float at {p('B', 'loan_rate'):.2f}–{p('C', 'loan_rate'):.2f}% (Mar 2026). On-time peak bridge {cash(p('C', 'on_time'))}.")
    cols = 'BCDEF'
    rows = [['Interest cost · ₹ cr'] + [n(p(c, 'interest')) for c in cols],
            ['EBITDA / interest'] + [mult(p(c, 'cover')) for c in cols],
            ['Net debt / EBITDA¹'] + [mult(p(c, 'leverage')) for c in cols],
            ['Cash before bridge · ₹ cr'] + [n(p(c, 'low_pre')).replace('-', '−') for c in cols]]
    table(s, .64, 4.28, 12.0, 1.56, [f"NCD case, {p('B', 'tenor'):.0f}-year at {p('B', 'coupon'):.2%}"] + [name for name, _, _ in PERIODS],
          rows, ratios=[1.9, 1, 1, 1, 1, 1], size=12)
    txt(s, .66, 5.90, 12, .26, '¹ Net debt includes leases. Quarter columns annualise that quarter’s EBITDA. Floor: ' + cv(FI, 'B4') + '.', 10)
