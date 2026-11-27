"""Build output/CEAT_Deal_Tearsheet.pdf: a one-page landscape deal tearsheet.

Every figure is read from the recalculated workbook (output/CEAT_Financial_Valuation_Model.xlsx) through the same
helpers the deck, brief and report use (src/results.py, src/committee.py), plus the dated NCD market-input register
(data/ncd_market_inputs.csv) for source dates. Nothing is typed in.

It complements the A4 investment-committee brief (output/CEAT_Valuation_Summary.pdf): the brief argues the decision in
prose; this page puts the funding, valuation and debt-pricing evidence side by side with charts.
"""
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
os.environ.setdefault('PYTHONUTF8', '1')

from reportlab.graphics.shapes import Drawing, Line, Rect, String  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import inch  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

from committee import AF, F, FI, ND, PD, TC, VS, DC, action, cash, outcome, pct, price, v  # noqa: E402
from ncd_case import PRICING as NP, ROW  # noqa: E402
import ncd_pricing  # noqa: E402

OUT = ROOT / 'output' / 'CEAT_Deal_Tearsheet.pdf'


def font_pair():
    """Calibri on Windows (as the brief), otherwise DejaVu Sans (ships with matplotlib); both carry the rupee sign."""
    env = os.environ.get('CEAT_FONT_REGULAR'), os.environ.get('CEAT_FONT_BOLD')
    if all(env):
        return env
    if Path('C:/Windows/Fonts/calibri.ttf').exists():
        return 'C:/Windows/Fonts/calibri.ttf', 'C:/Windows/Fonts/calibrib.ttf'
    import matplotlib
    ttf = Path(matplotlib.__file__).parent / 'mpl-data' / 'fonts' / 'ttf'
    return str(ttf / 'DejaVuSans.ttf'), str(ttf / 'DejaVuSans-Bold.ttf')


REG, BOLD = font_pair()
pdfmetrics.registerFont(TTFont('Body', REG))
pdfmetrics.registerFont(TTFont('Bold', BOLD))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')

NAVY, TEAL, GREY, PALE, MINT, RED, GOLD, SLATE = (colors.HexColor(h) for h in (
    '#15354A', '#167D76', '#526A76', '#E9F1F2', '#9AD1C7', '#A23B2A', '#A57439', '#8A97A8'))
RULE = colors.HexColor('#D3DEE0')
base = ParagraphStyle('b', fontName='Body', fontSize=8.2, leading=10.1, textColor=colors.HexColor('#1C2B33'))
small = ParagraphStyle('s', parent=base, fontSize=6.8, leading=8.2, textColor=GREY)
head = ParagraphStyle('h', parent=base, fontName='Bold', fontSize=9.6, leading=11.6, textColor=NAVY, spaceAfter=2)
W, H = landscape(A4)
M = 0.38 * inch
GUTTER = 0.2 * inch
COLW = (W - 2 * M - 2 * GUTTER) / 3

# ---- every figure, read once from the workbook -------------------------------------------------------------
INPUTS = ncd_pricing.load_inputs()
CASES = [v(F, f'A{r}') for r in range(4, 9)]
CLOSE = v(TC, 'B8')
CLOSE_TXT = f'₹{CLOSE:,.2f}'
FLOOR = v(FI, 'B4')
TRANCHE = v(FI, 'B5')
QUARTERS = [v(F, c + '21') for c in 'BCDEFG']
PATHS = {v(F, f'A{r}').replace(' unassisted', ''): [v(F, f'{c}{r}') for c in 'BCDEFG'] for r in range(22, 26)}
SENS = [v(ND, f'H{r}') for r in range(25, 33)]
METHODS = [(v(VS, f'A{r}').replace('FY26 ', ''), v(VS, f'B{r}'), v(VS, f'C{r}'), v(VS, f'D{r}')) for r in range(5, 9)]


def mult(x):
    return f'{x:.1f}x'


def bp(x):
    return f'{x:,.0f} bp'


def rate(x):
    return f'{x:.2f}%'


def when(cell):
    x = v(NP, cell)
    return f'{x:%d %b %Y}'.lstrip('0') if isinstance(x, date) else str(x)


def kv(rows, w0=1.2 * inch):
    tbl = Table([[Paragraph(a, base), Paragraph(b, base)] for a, b in rows], colWidths=[w0, COLW - w0])
    tbl.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, -1), 0.3, RULE),
                             ('LEFTPADDING', (0, 0), (-1, -1), 2), ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                             ('TOPPADDING', (0, 0), (-1, -1), 1.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                             ('FONTNAME', (0, 0), (0, -1), 'Bold')]))
    return tbl


def grid(rows, widths, highlight=None):
    data = [[Paragraph(f'<b>{c}</b>' if i == 0 or j == 0 else c, base) for j, c in enumerate(r)] for i, r in enumerate(rows)]
    tbl = Table(data, colWidths=widths)
    st = [('BACKGROUND', (0, 0), (-1, 0), PALE), ('LINEBELOW', (0, 0), (-1, -1), 0.3, RULE),
          ('LEFTPADDING', (0, 0), (-1, -1), 2), ('RIGHTPADDING', (0, 0), (-1, -1), 2),
          ('TOPPADDING', (0, 0), (-1, -1), 1.3), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.3), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
    if highlight is not None:
        st.append(('BACKGROUND', (0, highlight), (-1, highlight), colors.HexColor('#E3F0EE')))
    tbl.setStyle(TableStyle(st))
    return tbl


def cash_path(width, height=2.05 * inch):
    """Quarter-end cash before any balancing facility, by case, against the analyst floor (Funding Decision rows 21-26)."""
    d = Drawing(width, height)
    d.add(String(0, height - 9, f'Quarter-end cash before a bridge vs the {cash(FLOOR)} floor (₹ crore)',
                 fontName='Bold', fontSize=7.6, fillColor=NAVY))
    x0, x1, y0, y1 = 30, width - 6, 22, height - 26
    lo = min(min(p) for p in PATHS.values())
    hi = max(max(max(p) for p in PATHS.values()), FLOOR)
    step = 500
    lo_t, hi_t = (int(lo // step) * step), (int(-(-hi // step)) * step)
    ys = lambda val: y0 + (val - lo_t) / (hi_t - lo_t) * (y1 - y0)  # noqa: E731
    xs = lambda i: x0 + 8 + i * (x1 - x0 - 16) / (len(QUARTERS) - 1)  # noqa: E731
    for t in range(lo_t, hi_t + 1, step):
        d.add(Line(x0, ys(t), x1, ys(t), strokeColor=RULE, strokeWidth=0.3))
        d.add(String(x0 - 3, ys(t) - 2.2, f'{t:,.0f}'.replace('-', '−'), fontName='Body', fontSize=5.8, fillColor=GREY, textAnchor='end'))
    d.add(Line(x0, ys(FLOOR), x1, ys(FLOOR), strokeColor=RED, strokeWidth=0.8, strokeDashArray=[2, 2]))
    for i, q in enumerate(QUARTERS):
        d.add(String(xs(i), y0 - 9, q, fontName='Body', fontSize=5.8, fillColor=GREY, textAnchor='middle'))
    palette = {'On time': NAVY, 'Delay': SLATE, 'External': TEAL, 'Stress': GOLD}
    for name, path in PATHS.items():
        for i in range(len(path) - 1):
            d.add(Line(xs(i), ys(path[i]), xs(i + 1), ys(path[i + 1]), strokeColor=palette[name], strokeWidth=1.4))
        for i, val in enumerate(path):
            d.add(Rect(xs(i) - 1.3, ys(val) - 1.3, 2.6, 2.6, fillColor=palette[name], strokeColor=None))
    lx = x0
    for name, col in list(palette.items()) + [(f'Floor {cash(FLOOR)}', RED)]:
        d.add(Rect(lx, 1.5, 7, 3, fillColor=col, strokeColor=None))
        d.add(String(lx + 9, 1, name, fontName='Body', fontSize=6, fillColor=GREY))
        lx += 11 + pdfmetrics.stringWidth(name, 'Body', 6) + 8
    return d


def football(width, height=1.95 * inch):
    """Per-share value ranges: FY26 peer quartiles by multiple and the normalized DCF sensitivity span, vs the close."""
    rows = [(f'{m} (P25–P75)', lo, mid, hi, SLATE) for m, lo, mid, hi in METHODS]
    rows.append(('Normalized DCF (8 tests)', min(SENS), v(ND, 'B36'), max(SENS), TEAL))
    d = Drawing(width, height)
    d.add(String(0, height - 9, f'Value per share (₹) vs the {CLOSE_TXT} close; tick = central',
                 fontName='Bold', fontSize=7.6, fillColor=NAVY))
    x0, x1, top, bottom = 92, width - 22, height - 22, 16
    step = 500
    lo_t = int(min(r[1] for r in rows) // step) * step
    hi_t = int(-(-max(r[3] for r in rows) // step)) * step
    xs = lambda val: x0 + (val - lo_t) / (hi_t - lo_t) * (x1 - x0)  # noqa: E731
    for t in range(lo_t, hi_t + 1, step):
        d.add(Line(xs(t), bottom, xs(t), top + 4, strokeColor=RULE, strokeWidth=0.3))
        d.add(String(xs(t), bottom - 8, f'{t:,.0f}', fontName='Body', fontSize=5.8, fillColor=GREY, textAnchor='middle'))
    band = (top - bottom) / len(rows)
    for i, (label, lo, mid, hi, col) in enumerate(rows):
        yc = top - band * (i + 0.5)
        d.add(String(x0 - 4, yc - 2.3, label, fontName='Body', fontSize=6.3, fillColor=colors.HexColor('#1C2B33'), textAnchor='end'))
        d.add(Rect(xs(lo), yc - band * 0.3, xs(hi) - xs(lo), band * 0.6, fillColor=col, strokeColor=None))
        d.add(Line(xs(mid), yc - band * 0.38, xs(mid), yc + band * 0.38, strokeColor=colors.white, strokeWidth=1.2))
        d.add(String(xs(lo) - 2, yc - 2.2, f'{lo:,.0f}', fontName='Body', fontSize=5.6, fillColor=GREY, textAnchor='end'))
        d.add(String(xs(hi) + 2, yc - 2.2, f'{hi:,.0f}', fontName='Body', fontSize=5.6, fillColor=GREY))
    d.add(Line(xs(CLOSE), bottom, xs(CLOSE), top + 4, strokeColor=RED, strokeWidth=0.9, strokeDashArray=[2, 2]))
    return d


def fit(canvas, x, y, text, font, size, width):
    """Draw text at the largest size up to `size` that fits `width` (fonts differ in width across platforms)."""
    while size > 5 and canvas.stringWidth(text, font, size) > width:
        size -= 0.25
    canvas.setFont(font, size)
    canvas.drawString(x, y, text)


def header(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 0.8 * inch, W, 0.8 * inch, stroke=0, fill=1)
    stats = [(outcome(), 'recommendation'), (cash(v(F, 'C4')), 'peak on-time bridge'),
             (price(v(ND, 'B36')), 'normalized DCF / share')]
    x = W - M
    for big, lab in reversed(stats):
        canvas.setFont('Bold', 13.5)
        canvas.setFillColor(colors.white)
        wbig = max(canvas.stringWidth(big, 'Bold', 13.5), canvas.stringWidth(lab, 'Body', 7))
        canvas.drawRightString(x, H - 0.42 * inch, big)
        canvas.setFont('Body', 7)
        canvas.setFillColor(MINT)
        canvas.drawRightString(x, H - 0.6 * inch, lab)
        x -= wbig + 0.28 * inch
    room = x - M
    canvas.setFillColor(colors.white)
    fit(canvas, M, H - 0.42 * inch, 'CEAT Limited (NSE: CEATLTD)  |  Expansion financing tearsheet', 'Bold', 16.5, room)
    canvas.setFillColor(MINT)
    fit(canvas, M, H - 0.62 * inch, f'Valuation date 6 November 2026  |  consolidated, INR crore unless indicated  |  '
        f'{cash(TRANCHE)} discretionary capacity tranche  |  close {CLOSE_TXT}', 'Body', 8.4, room)
    canvas.setFillColor(GREY)
    fit(canvas, M, 0.3 * inch, 'Sources: CEAT FY26 annual report (notes 20, 42, 52), 14 Oct H1 results, 15 Oct call; NSE closes 6 Nov 2026; '
        f'MRF, Apollo and JK filings; CCIL zero-coupon curve {date.fromisoformat(INPUTS["gsec_zero_5y_current"]["as_of"]):%d %b %Y}; '
        f'India Ratings {when("C16")}; comparable NCD exchange filings; July 2026 ERP.', 'Body', 6.1, W - 2 * M)
    fit(canvas, M, 0.18 * inch, 'Every figure is read from the recalculated workbook (output/CEAT_Financial_Valuation_Model.xlsx). '
        'Tranche, cash floor, bridge and financing terms are analyst assumptions, not company covenants. '
        'Independent public-information analysis.', 'Body', 6.1, W - 2 * M)
    canvas.restoreState()


def col1():
    out = [Paragraph('Recommendation', head),
           Paragraph(f'<font name="Bold" color="#167D76">{outcome()}.</font> {action()} '
                     f'{cash(v(F, "G4"))} of the {cash(TRANCHE)} tranche can be paid on time from internal cash.', base),
           Spacer(1, 4), kv([
               ('Cash floor', f'{cash(FLOOR)} at every quarter-end (analyst floor)'),
               ('First breach', f'{v(F, "B4")} on the on-time schedule'),
               ('Peak funding gap', f'<b>{cash(v(F, "C4"))}</b> of bridge borrowing on time; cash falls to '
                                    f'{cash(v(F, "E4"))} before it'),
               ('Downside', f'Stress cash before a bridge falls to {cash(v(F, "E7"))}; funded stress still needs '
                            f'{cash(v(F, "C8"))} of bridge'),
           ], w0=0.95 * inch)]
    rows = [['Case', 'First gap', 'Peak bridge', 'Pre-bridge low', 'Peak loans']]
    for r in range(4, 9):
        rows.append([v(F, f'A{r}'), v(F, f'B{r}'), cash(v(F, f'C{r}')), cash(v(F, f'E{r}')), cash(v(F, f'H{r}'))])
    n = ROW['ncd']
    rows.append([f'NCD {cash(v(NP, "B25"))}', v(NP, f'B{n}'), cash(v(NP, f'C{n}')), cash(v(NP, f'D{n}')), cash(v(NP, f'E{n}'))])
    out += [Spacer(1, 5), Paragraph('Funding cases, 18 months to March 2028', head),
            grid(rows, [0.8 * inch] + [(COLW - 0.8 * inch) / 4] * 4, highlight=1),
            Paragraph(f'Pre-bridge low = lowest quarter-end cash before a balancing facility. Peak loans exclude leases. External '
                      f'adds an illustrative {cash(v(FI, "B28"))} term issue; the sixth (NCD) case funds the tranche with a '
                      f'5-year debenture.', small),
            Spacer(1, 4), cash_path(COLW)]
    return out


def col2():
    tc = [('MRF', 5), ('Apollo', 6), ('JK Tyre', 7), ('CEAT', 8)]
    out = [Paragraph('Valuation', head), football(COLW), Spacer(1, 3),
           grid([['FY26 method', 'P25', 'Median', 'P75', 'Median vs close']] +
                [[m, f'{lo:,.0f}', f'{mid:,.0f}', f'{hi:,.0f}', f'{(mid / CLOSE - 1) * 100:+.1f}%'] for m, lo, mid, hi in METHODS],
                [0.85 * inch] + [(COLW - 0.85 * inch) / 4] * 4),
           Spacer(1, 5), Paragraph('Normalized DCF', head), kv([
               ('Per share', f'<b>{price(v(ND, "B36"))}</b> vs {CLOSE_TXT} close ({(v(ND, "B36") / CLOSE - 1) * 100:+.1f}%)'),
               ('Inputs', f'WACC {pct(v(ND, "B24"))} (stock beta {v("WACC", "B8"):.2f}); growth {pct(v(ND, "B25"))}; '
                          f'terminal incremental ROIC {pct(v(ND, "B26"))}'),
               ('EV → equity', f'EV {cash(v(ND, "B33"))} less {cash(v(ND, "B34"))} net claims; '
                               f'{v(ND, "B32") / v(ND, "B33") * 100:.0f}% of EV is terminal value'),
               ('Sensitivity', f'{price(min(SENS))}–{price(max(SENS))} across ±100 bp WACC, ±50 bp growth, ±300 bp ROIC; '
                               f'peer-beta WACC {pct(v(PD, "B20"))} gives {price(v(ND, "H26"))}'),
               ('Reference DCF', f'{price(v(ND, "B48"))} on the original annual model (kept for comparison)'),
           ], w0=0.8 * inch),
           Spacer(1, 5), Paragraph('Trading comps, FY26', head),
           grid([['', 'EV / sales', 'EV / EBITDA', 'EV / EBIT', 'P/E']] +
                [[nm, mult(v(TC, f'N{r}')), mult(v(TC, f'O{r}')), mult(v(TC, f'P{r}')), mult(v(TC, f'Q{r}'))] for nm, r in tc] +
                [['Peer median', mult(v(TC, 'B17')), mult(v(TC, 'C17')), mult(v(TC, 'D17')), mult(v(TC, 'E17'))]],
                [0.8 * inch] + [(COLW - 0.8 * inch) / 4] * 4, highlight=4)]
    return out


def col3():
    n = ROW['ncd']
    out = [Paragraph('What the close requires', head), kv([
        ('Implied FY31 margin', f'<b>{pct(v(ND, "B42"))}</b> FY31 EBITDA margin vs {pct(v(ND, "B38"))} in the base case: '
                                f'{v(ND, "B41") * 10000:,.0f} bp of uplift phased through FY31 recovers {price(v(ND, "B47"))}'),
        ('FY31 UFCF', f'{cash(v(ND, "B43"))} required vs {cash(v(ND, "B37"))} modeled; FY32 reinvestment {cash(v(ND, "B45"))}'),
        ('Reference test', f'Original model needs {pct(v(ND, "B51"))} vs its {pct(v(DC, "F7"))} base '
                           f'({cash(v(ND, "B50"))} vs {cash(v(ND, "B49"))} FY31 UFCF)'),
    ], w0=0.95 * inch)]
    out += [Spacer(1, 5), Paragraph('NCD pricing: sixth funding case', head), grid([
        ['Tenor', 'CCIL G-sec', 'Comparable spread', 'Indicative coupon'],
        ['3-year', rate(v(NP, 'B20')), f'{v(NP, "C20"):,.0f}–{bp(v(NP, "D20"))} ({v(NP, "G20")})', f'{rate(v(NP, "E20"))}–{rate(v(NP, "F20"))}'],
        ['5-year', rate(v(NP, 'B21')), f'{v(NP, "C21"):,.0f}–{bp(v(NP, "D21"))} ({v(NP, "G21")})', f'{rate(v(NP, "E21"))}–{rate(v(NP, "F21"))}'],
    ], [0.55 * inch, 0.7 * inch, 1.1 * inch, COLW - 2.35 * inch], highlight=2),
        Paragraph(f'CEAT rated {v(NP, "B16")} (India Ratings, {when("C16")}). Spreads from {len(ncd_pricing.verified(ncd_pricing.load_comparables()))} '
                  f'AA/AA+ tyre-sector NCD issues over the CCIL zero-coupon curve; count of same-tenor issues in brackets.', small),
        Spacer(1, 3), kv([
            ('Case terms', f'{cash(v(NP, "B25"))}, {v(NP, "B26")}-year unsecured bullet at <b>{v(NP, "B27") * 100:.2f}%</b>, '
                           f'the top of the same-tenor range'),
            ('vs bank loans', f'Reported term loans float at {rate(v(NP, "B51"))}–{rate(v(NP, "C51"))}; the NCD costs '
                              f'{v(NP, "B52"):,.0f}–{bp(v(NP, "C52"))} more (₹{v(NP, "D52"):.1f}–{v(NP, "E52"):.1f}cr a year)'),
            ('Effect', f'Peak bridge falls from {cash(v(NP, "C45"))} to <b>{cash(v(NP, f"C{n}"))}</b>; cash before a bridge still '
                       f'reaches {cash(v(NP, f"D{n}"))} against the {cash(FLOOR)} floor'),
            ('Credit', f'FY28 EBITDA / interest {mult(v(NP, f"G{n}"))}; net debt / EBITDA {mult(v(NP, f"H{n}"))}'),
            ('Reading', f'{v(NP, "B57")}: {v(NP, "B58").lower()} with {v(NP, "B55")}'),
        ], w0=0.85 * inch)]
    img = ROOT / 'charts' / '06_cash_capex.png'
    iw = COLW
    out += [Spacer(1, 4), Image(str(img), width=iw, height=iw * 4.5 / 8.5)]
    return out


def build():
    OUT.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=M, rightMargin=M, topMargin=0.94 * inch,
                            bottomMargin=0.44 * inch, title='CEAT Limited | Expansion financing tearsheet',
                            author='Kartik Pawar', subject='One-page deal tearsheet generated from the recalculated model')
    layout = Table([[col1(), col2(), col3()]], colWidths=[COLW, COLW, COLW])
    layout.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('LEFTPADDING', (1, 0), (2, 0), GUTTER),
                                ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    doc.build([layout], onFirstPage=header)
    print(f'wrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    build()
