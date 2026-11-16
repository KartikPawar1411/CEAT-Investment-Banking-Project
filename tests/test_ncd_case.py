"""Tests for the NCD spread and coverage calculations.

Run from the project root:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
The workbook tests need a built model (build.py) and are skipped without one.
"""
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import ncd_pricing as ncd  # noqa: E402

AS_OF = date(2026, 11, 13)
MODEL = ROOT / 'output/CEAT_Financial_Valuation_Model.xlsx'


class Spread(unittest.TestCase):
    def test_spread_is_coupon_less_benchmark_in_basis_points(self):
        self.assertEqual(ncd.spread_bps(7.20, 6.24), 96.0)
        self.assertEqual(ncd.spread_bps(7.81, 6.51), 130.0)

    def test_spread_can_be_negative_and_is_rounded_to_a_tenth(self):
        self.assertEqual(ncd.spread_bps(6.00, 6.25), -25.0)
        self.assertEqual(ncd.spread_bps(7.383, 6.25), 113.3)

    def test_indicative_coupon_adds_lowest_and_highest_spread(self):
        self.assertEqual(ncd.indicative_coupon(6.95, [96.0, 113.0]), (7.91, 8.08))
        self.assertEqual(ncd.indicative_coupon(6.71, [130.0, 114.0]), (7.85, 8.01))

    def test_indicative_coupon_refuses_an_empty_sample(self):
        with self.assertRaises(ValueError):
            ncd.indicative_coupon(6.95, [])

    def test_unverified_rows_are_excluded_not_zero_filled(self):
        rows = [{'coupon_pct': 7.2, 'benchmark_gsec_yield_pct': 6.24, 'tenor_years': 5.0},
                {'coupon_pct': None, 'benchmark_gsec_yield_pct': None, 'tenor_years': None},
                {'coupon_pct': 7.5, 'benchmark_gsec_yield_pct': None, 'tenor_years': 2.0}]
        self.assertEqual(ncd.spreads(rows), [96.0])
        self.assertEqual(len(ncd.manual(rows)), 2)
        self.assertIsNone(ncd.number('  '))


class Coverage(unittest.TestCase):
    def test_interest_coverage(self):
        self.assertAlmostEqual(ncd.interest_coverage(600, 100), 6.0)
        self.assertAlmostEqual(ncd.interest_coverage(457, 86.4), 5.2893518, places=6)

    def test_interest_coverage_needs_positive_interest(self):
        for bad in (0, -5):
            with self.assertRaises(ValueError):
                ncd.interest_coverage(600, bad)

    def test_net_debt_includes_leases_and_nets_cash(self):
        self.assertEqual(ncd.net_debt(4000, 219, 100), 4119)

    def test_leverage_annual_and_annualised_quarter(self):
        self.assertAlmostEqual(ncd.net_debt_to_ebitda(4000, 200, 100, 2050), 2.0)
        self.assertAlmostEqual(ncd.net_debt_to_ebitda(4000, 200, 100, 512.5, periods_per_year=4), 2.0)

    def test_leverage_needs_positive_ebitda(self):
        with self.assertRaises(ValueError):
            ncd.net_debt_to_ebitda(4000, 200, 100, 0)


class ComparableData(unittest.TestCase):
    def setUp(self):
        self.rows = ncd.load_comparables()

    def test_columns_are_exactly_as_specified(self):
        with ncd.COMPARABLES.open(encoding='utf-8-sig') as f:
            self.assertEqual(f.readline().strip().split(','), ncd.COLUMNS)

    def test_stored_spread_equals_coupon_less_benchmark(self):
        good = ncd.verified(self.rows)
        self.assertGreaterEqual(len(good), 1)
        for row in good:
            self.assertEqual(row['spread_bps'], ncd.spread_bps(row['coupon_pct'], row['benchmark_gsec_yield_pct']), row['issuer'])

    def test_verified_rows_are_sourced_dated_and_in_the_aa_band(self):
        for row in ncd.verified(self.rows):
            self.assertTrue(row['source_url'].startswith('https://'), row['issuer'])
            self.assertTrue(row['rating_agency'] and row['source_date'], row['issuer'])
            self.assertIn('AA', row['credit_rating'])
            self.assertNotIn('AAA', row['credit_rating'])
            issued = date.fromisoformat(row['issue_date'])
            self.assertTrue(date(AS_OF.year - 1, AS_OF.month, AS_OF.day) <= issued <= AS_OF, row['issuer'])

    def test_manual_rows_carry_no_numbers_and_say_where_to_look(self):
        for row in ncd.manual(self.rows):
            for key in ['tenor_years', 'issue_size_inr_cr', 'coupon_pct', 'benchmark_gsec_yield_pct', 'spread_bps']:
                self.assertIsNone(row[key], row['issuer'])
            self.assertTrue(row['notes'].startswith('NEEDS MANUAL ENTRY'))
            self.assertTrue(row['source_url'].startswith('https://'))

    def test_market_inputs_are_sourced(self):
        inputs = ncd.load_inputs()
        for key in ['ceat_rating_latest', 'gsec_zero_3y_current', 'gsec_zero_5y_current', 'term_loan_rate_low', 'term_loan_rate_high']:
            self.assertTrue(inputs[key]['source_url'].startswith('https://'), key)
            date.fromisoformat(inputs[key]['as_of'])
        self.assertLess(ncd.value(inputs, 'term_loan_rate_low'), ncd.value(inputs, 'term_loan_rate_high'))

    def test_pricing_summary_matches_hand_arithmetic(self):
        s = ncd.pricing_summary(self.rows)
        for tenor in (3, 5):
            low, high = s[tenor]['coupon']
            self.assertAlmostEqual(low, s[tenor]['benchmark'] + min(s[tenor]['spreads']) / 100)
            self.assertAlmostEqual(high, s[tenor]['benchmark'] + max(s[tenor]['spreads']) / 100)
            self.assertLessEqual(low, high)


def built():
    if not MODEL.exists():
        return False
    from openpyxl import load_workbook
    book = load_workbook(MODEL, read_only=True)
    names = book.sheetnames
    book.close()
    return 'NCD Pricing' in names


@unittest.skipUnless(built(), 'Build the workbook first: build.py')
class Workbook(unittest.TestCase):
    def test_workbook_agrees_with_independent_reconstruction(self):
        import verify_ncd
        self.assertGreater(verify_ncd.verify(), 500)

    def test_existing_five_cases_and_decision_are_still_in_place(self):
        import results
        self.assertEqual([results.v('Funding Decision', f'A{r}') for r in range(4, 9)],
                         ['On time', 'Delay', 'External', 'Stress', 'Funded stress'])
        self.assertIsNone(results.v('Funding Decision', 'A9'))
        self.assertEqual(results.v('NCD Pricing', 'B55'), results.v('Funding Decision', 'B10'))


if __name__ == '__main__':
    unittest.main()
