"""Write the repository landing page from the same cached results as the publications.

Every figure comes from the recalculated workbook, the validation report and the data registers. CI regenerates this
file and fails if it differs from the committed README, so the landing page cannot drift from the model.
"""
import csv
import re
from committee import *
from ncd_case import PRICING as NP, ROW
import ncd_pricing

REPO = 'KartikPawar1411/CEAT-Investment-Banking-Project'


def rows(path):
    with (ROOT / path).open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def checks():
    """Check counts as written by the verification steps into reports/validation.md."""
    text = publish_path('reports/validation.md').read_text(encoding='utf-8')
    grab = lambda pattern: re.search(pattern, text, re.M).group(1)  # noqa: E731
    return {'qc': grab(r'^(\d[\d,]*) checks passed, including'), 'formulas': grab(r'including ([\d,]+) cached Excel formulas'),
            'sheets': grab(r'formulas across (\d+) sheets'), 'source': grab(r'(\d[\d,]*) source checks'),
            'model': grab(r'and (\d[\d,]*) integrated model checks'), 'ncd': grab(r'## NCD funding case\s+(\d[\d,]*) checks passed')}


def threshold():
    with publish_path('reports/decision_threshold_test.csv').open(encoding='utf-8-sig') as f:
        return list(csv.reader(f))[1:]


def build():
    c = checks()
    close = v(TC, 'B8')
    close_txt = f'₹{close:,.2f}'
    dcf = v(ND, 'B36')
    ncd = ROW['ncd']
    sources, register, comps = rows('data/sources.csv'), rows('data/processed/input_register.csv'), ncd_pricing.verified(ncd_pricing.load_comparables())
    alt = [r for r in threshold() if r[1] != outcome()]
    alt_line = (f" At a {cash(float(alt[0][0]))} tranche the same generators write **{alt[0][1]}** in the deck, brief and report, "
                f"so the wording is driven by the model.") if alt else ''
    sens = [v(ND, f'H{r}') for r in range(25, 33)]
    text = f"""# CEAT Limited | Expansion financing and valuation

[![tests](https://github.com/{REPO}/actions/workflows/tests.yml/badge.svg)](https://github.com/{REPO}/actions/workflows/tests.yml)
![sources](https://img.shields.io/badge/sources-{len(sources)}_dated%2C_{len(register)}_traced_inputs-15354A)
![checks](https://img.shields.io/badge/independent_checks-{sum(int(c[k].replace(',', '')) for k in ('qc', 'source', 'model', 'ncd')):,}-167D76)
![scope](https://img.shields.io/badge/valuation_date-6_Nov_2026-526A76)

**Can CEAT Limited (NSE: CEATLTD) pay for a {cash(v(FI, 'B5'))} capacity tranche on schedule without breaking its cash floor? A quarterly three-statement model built from CEAT's filings says no.**

**Result: {outcome()}.** {action()}
- **{cash(v(F, 'G4'))} of the {cash(v(FI, 'B5'))} tranche** can be paid on time from internal cash. The on-time schedule first breaches the {cash(v(FI, 'B4'))} cash floor in **{v(F, 'B4')}** and needs **{cash(v(F, 'C4'))}** of peak bridge borrowing.
- A {cash(v(NP, 'B25'))} five-year NCD prices at an indicative **{v(NP, 'E21'):.2f}–{v(NP, 'F21'):.2f}%**. It cuts the peak bridge to {cash(v(NP, f'C{ncd}'))} but does not close the gap.
- The normalized DCF gives **{price(dcf)} per share** against the {close_txt} close. The close requires a **{percent(ND, 'B42')} FY31 EBITDA margin**, against {percent(ND, 'B38')} in the base case.

[![Tearsheet](docs/img/tearsheet.png)](output/CEAT_Deal_Tearsheet.pdf)
<sub>One-page deal tearsheet. Click it for the PDF.</sub>

| Open | What it is |
|---|---|
| [**Tearsheet**](output/CEAT_Deal_Tearsheet.pdf) | One landscape page: recommendation, six funding cases, cash path, valuation range, implied margin, NCD pricing |
| [**Investment brief**](output/CEAT_Valuation_Summary.pdf) | One A4 page for the investment committee: the decision argued in prose, five funding cases, release conditions |
| [**Excel model**](output/CEAT_Financial_Valuation_Model.xlsx) | {c['sheets']} sheets, every output a live formula. Start at Cover & Dashboard, then Funding Decision; edit the blue cells in Funding Inputs |
| [**Pitch book**](output/CEAT_Investment_Banking_Pitch_Book.pptx) ([PDF](output/CEAT_Investment_Banking_Pitch_Book.pdf)) | 19 slides. Slides 2–3: decision and capital requirement. Slides 13–15: operating case vs the market. Slide 19: NCD case |
| [**Research report**](reports/CEAT_Investment_Banking_Research_Report.md) | Company and sector evidence, forecast economics, peer and intrinsic valuation, risks and references |
| [**NCD funding case**](docs/ncd_case.md) | Sixth funding case: a five-year NCD for the {cash(v(NP, 'B25'))} tranche, priced from {len(comps)} AA/AA+ tyre-sector issues |
| [**Input lineage**](data/processed/input_register.csv) · [**sources**](data/sources.csv) | {len(register)} inputs traced to filing, page, reporting unit and conversion; {len(sources)} dated sources |
| [**Validation**](reports/validation.md) · [**threshold test**](reports/decision_threshold_test.csv) | Independent checks, and a separately recalculated decision at a different tranche size |

## The decision in 30 seconds

| | |
|---|---:|
| Proposed tranche / self-funded on schedule | {cash(v(FI, 'B5'))} / **{cash(v(F, 'G4'))}** |
| Cash floor / first quarter below it | {cash(v(FI, 'B4'))} / {v(F, 'B4')} |
| Peak bridge: on time / delayed / funded stress | **{cash(v(F, 'C4'))}** / {cash(v(F, 'C5'))} / {cash(v(F, 'C8'))} |
| Cash before a bridge, lowest quarter: on time / stress | {cash(v(F, 'E4'))} / {cash(v(F, 'E7'))} |
| Illustrative {cash(v(FI, 'B28'))} term issue: lowest quarter-end cash | {cash(v(F, 'E6'))} |
| NCD case: coupon / peak bridge | {v(NP, 'B27') * 100:.2f}% / {cash(v(NP, f'C{ncd}'))} |
| Normalized DCF vs close | **{price(dcf)}** vs {close_txt} ({(dcf / close - 1) * 100:+.1f}%) |
| DCF sensitivity range (8 tests) | {price(min(sens))}–{price(max(sens))} |
| FY26 peer EV/EBITDA, P25–P75 per share | {price(v(VS, 'B6'))}–{price(v(VS, 'D6'))} (median {mult(v(TC, 'C17'))}) |
| FY31 EBITDA margin: base / implied by the close | {percent(ND, 'B38')} / **{percent(ND, 'B42')}** |
| WACC / perpetual growth / terminal ROIC | {percent(ND, 'B24')} / {percent(ND, 'B25')} / {percent(ND, 'B26')} |

## What the numbers show

1. **The plan is not self-funding on schedule.** Cash before any bridge falls to {cash(v(F, 'E4'))} on the on-time schedule. In stress it falls to {cash(v(F, 'E7'))}. {cash(v(F, 'G4'))} of the {cash(v(FI, 'B5'))} tranche can be paid on its dates while holding the {cash(v(FI, 'B4'))} floor.
2. **Delay alone does not fix it.** Moving the two payments back four quarters cuts the peak bridge to {cash(v(F, 'C5'))}, but the core plan still breaches the floor in {v(F, 'B5')}.
3. **Debt narrows the gap but does not close it.** {external()} The NCD case cuts the peak bridge from {cash(v(NP, 'C45'))} to {cash(v(NP, f'C{ncd}'))}. Cash before a bridge still reaches {cash(v(NP, f'D{ncd}'))}, so the decision stands.
4. **The market is pricing a better margin than the base case.** The DCF sits {abs(dcf / close - 1) * 100:.1f}% {'below' if dcf < close else 'above'} the close. Recovering the close needs {v(ND, 'B41') * 10000:,.0f} bp of extra FY31 EBITDA margin, phased in, on the same sales and reinvestment path.

![Decision](docs/img/decision.png)

<details>
<summary><b>Funding cases, valuation, market-implied margin, NCD case and history</b></summary>

![Funding cases](docs/img/funding-cases.png)
![Relative valuation](docs/img/relative-valuation.png)
![DCF](docs/img/dcf.png)
![Market-implied operating case](docs/img/market-implied.png)
![NCD case](docs/img/ncd-case.png)
![EBITDA and margin](docs/img/chart-ebitda.png)
![Operating cash flow and capex](docs/img/chart-cash_capex.png)

</details>

## Capital decision

{markdown_table(HEAD, funding_table())}

First gap is the first modeled quarter-end below the {cv(FI, 'B4')} analyst floor after any planned issuance. Peak loans exclude lease liabilities. Affordable is the portion of the proposed tranche that can be paid on its specified schedule while preserving the floor through March 2028. A balancing facility covers deficits in the integrated statements; its availability is unverified. View the unassisted cash path alongside financed cash. September opens at ₹32cr and intra-quarter liquidity is unknown.

FY27 standalone capex guidance was ₹1,400cr plus ₹100–150cr for CAMSO upstream equipment. The midpoint leaves ₹723cr of core spending in H2 after ₹802cr in H1. The proposed tranche is incremental. FY26 note 42 reported ₹1,785.12cr of March capital contracts. The September contracted balance and payment schedule are unknown. The core expansion bucket is an analyst planning allocation. The model includes the separate US$44m trademark in Q2 FY29. Inventory timing remains a working-capital risk.

## Valuation

{dcf_story()} {market()} FY26 EBITDA quartiles imply {price(v(VS, 'B6'))}–{price(v(VS, 'D6'))}. {legacy()} Peer-beta WACC gives {price(v(ND, 'H26'))} per share. Forecast returns depend on input-cost recovery, utilization, mix and continuing capital efficiency.

## Built to be checked

- **Frozen primary evidence.** The issuer and market archive in `data/raw` is pinned by SHA-256. {c['source']} source checks confirm the hashes, the cutoff date, the price panels and that material filed values appear on the cited pages. {len(register)} inputs are traced in the [input register](data/processed/input_register.csv) to document, page, reporting unit and conversion.
- **Independent reconstructions.** Each model is rebuilt in Python, outside the workbook formulas, and compared:
  - {c['qc']} quality-control checks across {c['formulas']} cached Excel formulas, including statement ties, beta and WACC;
  - {c['model']} integrated checks on all five quarterly cases through FY31: cash and debt roll-forwards, first gaps, the terminal year, the eight DCF sensitivities and the reverse DCF;
  - {c['ncd']} checks on the NCD case and its pricing.
- **The written decision moves with the model.** The deck, brief and report must quote the same decision and figures as the workbook. A separate Excel copy is recalculated at a different tranche size and republished.{alt_line}
- **Tests on every push** (GitHub Actions, Linux). CI runs:
  - the pytest suite (NCD spread and coverage arithmetic, sourced comparables, workbook vs independent rebuild);
  - the source validation and both independent reconstructions against the committed workbook;
  - a rebuild of this README, which fails if any figure here has drifted from the model;
  - a rebuild of the tearsheet, which must stay one page.
- **Stated limits.** The tranche, cash floor, bridge and financing terms are analyst assumptions, not company covenants. Unverified figures stay blank, never zero; see the model conventions below.

## Rebuild

Use 64-bit Windows, desktop Microsoft Excel and PowerPoint registered for COM automation, PowerShell and Python 3.12+.

```powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File build.ps1
```

`build.ps1` runs the whole pipeline:

1. `build.py --render` builds in a staging folder. It:
   - verifies the archived evidence;
   - builds the workbook and recalculates it in Excel;
   - runs the independent checks;
   - generates the charts, deck, brief, report and this README;
   - exports the deck to PDF through PowerPoint;
   - publishes only if every check passes. A failed build leaves the prior outputs intact.
2. `build_tearsheet.py` builds the tearsheet from the published workbook.
3. `scripts/export_images.ps1` exports the README images.
4. The tests run.

ReportLab uses installed Calibri regular and bold fonts by default. Set CEAT_FONT_REGULAR and CEAT_FONT_BOLD to absolute paths to Unicode TTF alternatives when needed; the tearsheet falls back to DejaVu Sans. Close open copies of the files before publishing.

For a presentation-only rebuild, use `build.py --publish-only --render` after a full build. This requires the cached baseline workbook and .qa/threshold.xlsx from the same full build. To persist new assumptions through a full rebuild, change src/expansion_model.py. Manual edits made in Excel recalculate the linked scenarios and dashboard; a full rebuild restores the source-controlled assumptions. The snapshot date is fixed. Refreshing a source or changing the cutoff requires a new evidence review and an explicit update to data/archive_hashes.csv.

## Model conventions

- Five integrated cases run quarterly from December 2026 through March 2031. A sixth, the NCD case, runs on the same engine. FY Forecast aggregates the on-time statements and combines FY27 with reported H1. Rows 37–38 show forecast-period flows. Other assets and liabilities are fixed at opening residuals. No balancing plug is used.
- The core volume index and OHT relative realization are analyst proxies. September standalone product mix anchors core equivalent-unit shares. CAMSO end-customer billing is scaled separately. Acquired FY26 product revenue of ₹420.65cr supports a directional ex-CAMSO comparison. Group physical volumes, audited segment profit and individual plant returns are unavailable.
- Existing borrowing costs accrue on opening debt, planned term proceeds accrue from draw, and a balancing draw accrues interest from the next quarter. Projected short-term renewals and term funding are assumptions. Gross term balances, reported current maturities and disclosed repayment weights are reconciled in Funding Inputs. Leases are debt in the EV and new ROU assets are capital investment in UFCF.
- The original DCF and original scenario/sensitivity schedules are labeled reference. Normalized DCF contains the revised calculation, value bridge, peer-beta sensitivity and market-implied margin path. Trading Comps distinguishes the three FY26 peers, two aligned September LTM peers and MRF's June LTM observation.
- data/raw holds the frozen issuer and market archive. CCIL's yield is transcribed in the dated source register; its original daily web table is not archived. Some older filing dispatch days remain unverified. The inventory commitment has no disclosed September unpaid balance. Analyst debt terms, minimum cash and stress triggers are not company covenants.

## Repository layout

```
build.ps1            one-command rebuild (pipeline, tearsheet, images, tests)
build.py             staged, validated build of the model and publications
build_tearsheet.py   one-page deal tearsheet from the recalculated workbook
src/                 evidence checks, workbook, cases, DCF, NCD case, deck, brief, report, verifiers, README
data/                raw archive (hash-pinned), processed inputs, input register, NCD comparables and market inputs
tests/               test_ncd_case.py
output/              Excel model, pitch book (.pptx, .pdf), investment brief, tearsheet
reports/             research report, validation results, decision threshold test
docs/                ncd_case.md (NCD write-up), img/ (README images)
charts/              historical charts used in the deck and report
scripts/             export_images.ps1
```

Independent public-information analyst portfolio project.
"""
    publish_path('README.md').write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    build()
