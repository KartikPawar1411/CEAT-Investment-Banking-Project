# NCD funding case

Sixth funding case for the ₹300cr discretionary tranche: a non-convertible debenture instead of the bridge. Research date 13 November 2026. The model's valuation date (6 November 2026) and the five existing cases are unchanged.

## Result

| | 3-year | 5-year |
|---|---|---|
| CCIL zero-coupon G-sec, 12 Nov 2026 | 6.71% | 6.95% |
| Same-tenor comparable spread | 114–130 bp (2 issues) | 96–113 bp (2 issues) |
| Indicative coupon | 7.85–8.01% | 7.91–8.08% |
| Full-sample cross-check (96–130 bp) | 7.67–8.01% | 7.91–8.25% |

The case uses a 5-year bullet at 8.08%, the top of the same-tenor range.

| NCD case, ₹ crore | Q3 FY27 | Q4 FY27 | FY27E | FY28E | FY29E |
|---|---|---|---|---|---|
| Interest cost | 92 | 92 | 417 | 364 | 317 |
| EBITDA / interest | 6.1x | 7.1x | 4.9x | 8.0x | 10.6x |
| EBIT / interest | 4.0x | 5.0x | 3.0x | 5.7x | 7.9x |
| Net debt / EBITDA | 1.9x | 1.7x | 2.1x | 1.3x | 0.9x |
| Minimum cash before bridge | 51 | −153 | −153 | −100 | 39 |
| Gap to the ₹100cr floor | −49 | −253 | −253 | −200 | −61 |
| Bridge outstanding, period end | 49 | 254 | 254 | 0 | 0 |

Quarter leverage annualises that quarter's EBITDA. FY27E adds reported H1 FY27 to the two forecast quarters. The first breach is Q3 FY27; the bridge balance peaks one quarter later, in Q4 FY27.

The NCD cuts the peak bridge from ₹551cr (On time) to ₹254cr but does not remove it. That agrees with the existing decision, DEFER / RESIZE FUNDING, which this work does not alter.

## Method

1. **Rating.** India Ratings affirmed CEAT's NCDs and bank facilities at IND AA/Positive on 3 July 2026 (latest rationale found). CARE reaffirmed CARE AA; Positive on 8 January 2026.
2. **Comparables.** Fixed-coupon, plain NCDs allotted between 13 Nov 2025 and 13 Nov 2026 by non-financial Indian corporates rated AA or AA+. Coupon, tenor and dates were read from each issuer's exchange filing.
3. **Benchmark.** CCIL's Nelson-Siegel-Svensson zero-coupon G-sec rate at the issue tenor on the allotment date, from CCIL's Zero Rates page. Spread = coupon − benchmark.
4. **Indicative coupon.** Current benchmark plus the lowest and highest same-tenor spread. No notch or new-issue premium is added.
5. **Case.** `src/ncd_case.py` runs the same quarterly engine as the other cases. Only three rows differ from On time: the ₹300cr draw in Q3 FY27, its redemption, and its coupon. A control proves sales to EBIT equal On time in every quarter.
6. **Term loan.** CEAT's reported rupee term-loan range, FY26 annual report consolidated note 20: floating 7.15–7.8% at 31 March 2026.

## Comparables and exclusions

Five rows from three issuers were verified, against a target of five to eight.

| Issue | Rating | Date | Tenor | Coupon | G-sec | Spread |
|---|---|---|---|---|---|---|
| CEAT Series 4 | CARE AA; Positive | 30 Dec 2025 | 5y | 7.20% | 6.24% | 96 bp |
| Balkrishna Series I | CARE AA+; Stable | 23 Mar 2026 | 3y | 7.20% | 6.06% | 114 bp |
| Balkrishna Series II | CARE AA+; Stable | 23 Mar 2026 | 4y | 7.38% | 6.25% | 113 bp |
| Balkrishna Series III | CARE AA+; Stable | 23 Mar 2026 | 5y | 7.55% | 6.42% | 113 bp |
| Apollo Tyres (secured) | IND AA+/Stable | 30 Sep 2026 | 3y | 7.81% | 6.51% | 130 bp |

URLs and dates are in `data/comparable_ncd_issues.csv` and `data/ncd_market_inputs.csv`.

**Needs manual entry** (rows are in the CSV with blank figures):

- Ashok Leyland, August 2026 issue: NSE filing `ASHOKLEYLAND_10082026192413_SEINTIMATIONNCDALLOTMENTPDF.pdf`.
- Balkrishna, second 2026 issue: NSE filing of 3 Sep 2026, or BSE announcements for scrip 502355.
- Godrej Industries, June 2026 issue: NSE WDM listing circular or the issuer's BSE announcement.
- Balkrishna per-series issue sizes (only the ₹750cr aggregate is in the filing): key information document.
- Apollo's instrument-level rating letter. The rating shown is India Ratings' statement about Apollo's debt in its CEAT release.

NSE's archive timed out on the research date, so none of these was read from a primary document. After entering coupon and benchmark, copy the spread formula down on the NCD Pricing sheet.

**Excluded:** JSW Energy, 28 Sep 2026 (7-year, benchmark-linked coupon); TVS Motor, Aug 2026 (reported as AAA); banks, NBFCs and other financial issuers.

## Limitations

- Five observations from three tyre companies; four of five are AA+, one notch above CEAT. CEAT's own December 2025 issue priced tighter than the AA+ issues that followed, so the sample shows spreads widening through 2026 rather than a clean notch premium.
- Zero-coupon benchmark against annual-pay coupons: spreads are comparable with each other, not with par-yield spreads quoted elsewhere.
- Apollo's issue is secured; CEAT's precedent is unsecured.
- The term-loan range is a March 2026 floating rate, not a current quote. The 5-year benchmark was 6.42% on 23 March and 6.95% on 12 November, so a fresh loan would likely price higher. No adjustment is made.
- No issue costs are modeled. Agency leverage tests use wider debt definitions and are not reproduced.
- The balancing bridge is assumed available, as in the other cases.

## NCD versus bank term loan

On reported numbers the NCD costs 11–93 bp more than CEAT's bank loans, or ₹0.3–2.8cr a year on ₹300cr. The loan range is seven months old and floating, so the true gap is probably at the low end. The NCD is fixed-rate, bullet and, on CEAT's own precedent, unsecured; a term loan amortises through FY27–FY28, exactly when the model is short of cash, and takes plant security. **Recommendation:** if the tranche is to be debt-funded, a 5-year NCD is the better instrument than a term loan at a small cost premium, but ₹300cr is not enough. It leaves a ₹254cr peak bridge and cash ₹253cr under the floor in Q4 FY27, so the existing DEFER / RESIZE FUNDING decision stands.

## Five interview questions

1. **Why 8.08% when CEAT issued at 7.20% eleven months ago?** The 5-year G-sec rose from 6.24% to 6.95%. CEAT's own 96 bp spread on today's benchmark gives 7.91%; the AA+ issue from March gives 113 bp and 8.08%. The case uses the higher figure.
2. **Why is an AA issuer priced off AA+ comparables?** Those are the only verified same-sector issues in the window. The data shows no notch premium, so none is invented; the limitation is stated and the case uses the top of the range.
3. **Does the NCD fix the funding gap?** No. Cash before a bridge still reaches −₹153cr in Q4 FY27 against a ₹100cr floor. The External case shows roughly ₹550cr of term money is needed, and even that leaves ₹86cr at the trough.
4. **Does it strain the rating?** FY27E net debt/EBITDA is 2.1x and EBITDA cover 4.9x, improving to 1.3x and 8.0x in FY28E. India Ratings already expects its own, wider leverage measure at 2.3–2.5x in FY27 and tests 1.75x on a sustained basis, so the NCD adds to an already stretched year without changing the trajectory.
5. **Why not the cheaper bank loan?** The reported 7.15–7.8% is a March floating rate. More important is structure: amortisation would pull repayments into the trough quarters, while a bullet NCD pushes principal beyond the forecast and fixes the rate.

## Where things are

- Workbook: sheets `NCD` (the case) and `NCD Pricing` (comparables, coupon, metrics, term-loan comparison, controls).
- Deck: slide 19.
- Code: `src/ncd_pricing.py`, `src/ncd_case.py`, `src/ncd_slide.py`, `src/verify_ncd.py`.
- Tests: `.venv\Scripts\python.exe -m unittest discover -s tests -v`.
