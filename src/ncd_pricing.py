"""NCD pricing arithmetic. Pure functions over the sourced CSVs; no workbook required."""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'
COMPARABLES = DATA / 'comparable_ncd_issues.csv'
INPUTS = DATA / 'ncd_market_inputs.csv'
COLUMNS = ['issuer', 'credit_rating', 'rating_agency', 'issue_date', 'tenor_years', 'issue_size_inr_cr', 'coupon_pct',
           'benchmark_gsec_yield_pct', 'spread_bps', 'source_url', 'source_date', 'notes']


def number(text):
    """Blank stays blank: an unverified figure is None, never zero."""
    text = str(text).strip()
    return float(text) if text else None


def spread_bps(coupon_pct, benchmark_pct):
    """Coupon less matched-tenor government yield, in basis points."""
    return round((coupon_pct - benchmark_pct) * 100, 1)


def load_comparables(path=COMPARABLES):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in ['tenor_years', 'issue_size_inr_cr', 'coupon_pct', 'benchmark_gsec_yield_pct', 'spread_bps']:
            row[key] = number(row[key])
    return rows


def verified(rows):
    """Rows usable for pricing: coupon, benchmark and tenor were all read from a primary source."""
    return [r for r in rows if None not in (r['coupon_pct'], r['benchmark_gsec_yield_pct'], r['tenor_years'])]


def manual(rows):
    return [r for r in rows if r not in verified(rows)]


def spreads(rows, tenor=None):
    return [spread_bps(r['coupon_pct'], r['benchmark_gsec_yield_pct']) for r in verified(rows)
            if tenor is None or r['tenor_years'] == tenor]


def indicative_coupon(benchmark_pct, spread_list):
    """Current benchmark plus the lowest and highest observed comparable spread. Returns (low %, high %)."""
    if not spread_list:
        raise ValueError('No verified comparable spread for this tenor')
    return (round(benchmark_pct + min(spread_list) / 100, 4), round(benchmark_pct + max(spread_list) / 100, 4))


def load_inputs(path=INPUTS):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return {r['key']: r for r in csv.DictReader(f)}


def value(inputs, key):
    return float(inputs[key]['value'])


def interest_coverage(earnings, interest):
    """Earnings (EBITDA or EBIT) divided by interest expense for the same period."""
    if interest <= 0:
        raise ValueError('Interest must be positive')
    return earnings / interest


def net_debt(borrowings, leases, cash):
    return borrowings + leases - cash


def net_debt_to_ebitda(borrowings, leases, cash, ebitda, periods_per_year=1):
    """Period-end net debt including leases over EBITDA. Pass periods_per_year=4 to annualise one quarter."""
    if ebitda <= 0:
        raise ValueError('EBITDA must be positive')
    return net_debt(borrowings, leases, cash) / (ebitda * periods_per_year)


def pricing_summary(rows=None, inputs=None):
    """Everything the workbook derives, recomputed here so the two can be compared."""
    rows = load_comparables() if rows is None else rows
    inputs = load_inputs() if inputs is None else inputs
    out = {'count': len(verified(rows)), 'manual': len(manual(rows)), 'all': spreads(rows)}
    for tenor in (3, 5):
        bench = value(inputs, f'gsec_zero_{tenor}y_current')
        out[tenor] = {'benchmark': bench, 'spreads': spreads(rows, tenor),
                      'coupon': indicative_coupon(bench, spreads(rows, tenor)),
                      'coupon_all': indicative_coupon(bench, spreads(rows))}
    return out
