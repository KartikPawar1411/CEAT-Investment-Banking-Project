# CEAT Limited | Expansion financing and valuation

**6 November 2026 · India · INR crore unless indicated**

**DEFER / RESIZE FUNDING · ₹0cr of ₹300cr self-funded.** Defer the tranche. The proposed term funding is insufficient; resize the program or secure more capital. The on-time schedule first breaches the ₹100cr cash floor in Q3 FY27. Peak bridge borrowing is ₹551cr. The illustrative ₹550cr term issue leaves ₹86cr at the base trough. Under funded stress, the plan needs another ₹1,252cr of peak bridge capacity.

| Open | Review |
|---|---|
| [One-page investment brief](output/CEAT_Valuation_Summary.pdf) | Recommendation, five funding cases and valuation |
| [Editable Excel model](output/CEAT_Financial_Valuation_Model.xlsx) | Start at Cover & Dashboard, then Funding Decision. Edit blue assumption cells in Funding Inputs. |
| [Investment banking pitch book](output/CEAT_Investment_Banking_Pitch_Book.pptx) | Slides 2–3 show the decision, capital requirement and conditions for release. Slides 13–15 reconcile the operating case with the market. |
| [Research report](reports/CEAT_Investment_Banking_Research_Report.md) | Company and sector evidence, forecast economics, peer and intrinsic valuations, risks and references |
| [Input lineage](data/processed/input_register.csv) · [original sources](data/sources.csv) | Filed measures, reporting units, conversion, dates and source locators |
| [Validation results](reports/validation.md) · [capex threshold test](reports/decision_threshold_test.csv) | Independent checks and a separately recalculated, republished decision |
| [NCD funding case](docs/ncd_case.md) | Sixth funding case: a five-year NCD for the ₹300cr tranche at an indicative 8.08% (113 bp over the 5-year G-sec), from five AA/AA+ tyre-sector issues. It cuts the peak bridge from ₹551cr to ₹254cr but does not remove it, so the decision is unchanged. |

## Capital decision

| Case | First gap¹ | Peak bridge | Peak loans² | Cash pre-bridge | Funded low | Affordable |
| --- | --- | --- | --- | --- | --- | --- |
| On time | Q3 FY27 | ₹551cr | ₹4,237cr | −₹444cr | ₹100cr | ₹0cr |
| Delay | Q3 FY27 | ₹248cr | ₹3,960cr | −₹144cr | ₹100cr | ₹0cr |
| External | Q4 FY27 | ₹14cr | ₹4,316cr | ₹86cr | ₹100cr | ₹286cr |
| Stress | Q3 FY27 | ₹1,792cr | ₹4,915cr | −₹1,572cr | ₹100cr | ₹0cr |
| Funded stress | Q4 FY27 | ₹1,252cr | ₹4,925cr | −₹1,084cr | ₹100cr | ₹0cr |

First gap is the first modeled quarter-end below the ₹100cr analyst floor after any planned issuance. Peak loans exclude lease liabilities. Affordable is the portion of the proposed tranche that can be paid on its specified schedule while preserving the floor through March 2028. A balancing facility covers deficits in the integrated statements; its availability is unverified. View the unassisted cash path alongside financed cash. September opens at ₹32cr and intra-quarter liquidity is unknown.

FY27 standalone capex guidance was ₹1,400cr plus ₹100–150cr for CAMSO upstream equipment. The midpoint leaves ₹723cr of core spending in H2 after ₹802cr in H1. The proposed tranche is incremental. FY26 note 42 reported ₹1,785.12cr of March capital contracts. The September contracted balance and payment schedule are unknown. The core expansion bucket is an analyst planning allocation. The model includes the separate US$44m trademark in Q2 FY29. Inventory timing remains a working-capital risk.

## Valuation

The normalized DCF gives ₹3,324 per share versus the ₹3,545.80 close. It assumes a 15.5% FY31 EBITDA margin, ₹2,346cr of FY31 unlevered free cash flow and 28.6% terminal reinvestment. On the revised sales and reinvestment path, a 64 bp margin uplift phased through FY31 produces a 16.2% FY31 EBITDA margin, ₹2,485cr of FY31 UFCF and ₹3,546 per share. FY32 reinvestment rises to ₹836cr. FY26 EBITDA quartiles imply ₹2,955–₹3,690. The reference DCF gives ₹1,370. Reaching the close with its explicit flows fixed requires ₹2,343cr of FY31-equivalent UFCF versus ₹1,037cr modeled. At fixed sales, D&A, capex and working capital that implies a 19.6% EBITDA margin against its 12.5% base. The reverse test changes the terminal run rate only. Peer-beta WACC gives ₹3,950 per share. Forecast returns depend on input-cost recovery, utilization, mix and continuing capital efficiency.

## Rebuild on Windows

Use 64-bit Windows, desktop Microsoft Excel and PowerPoint registered for COM automation, PowerShell, Python 3.12 and the packages in requirements.txt. ReportLab uses installed Calibri regular and bold fonts by default. Set CEAT_FONT_REGULAR and CEAT_FONT_BOLD to absolute paths to Unicode TTF alternatives when needed. Close open copies of the files before publishing.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe build.py --render
```

The normal build is offline. It verifies the archived evidence hashes, material filing values and cutoff dates, builds an editable workbook, recalculates it in Excel, and checks the financial statements and valuation before generating the publications. A separate Excel copy changes the tranche amount and regenerates the deck, report and brief. The test checks that the decision and numerical outputs change together. Only validated staged outputs are published. With --render, PowerPoint exports every slide and the PDF pages are rendered for inspection under .qa. The published pitch-book PDF is a rendering of the editable deck. The build guard leaves prior published outputs intact on validation failure.

For a presentation-only rebuild, use `build.py --publish-only --render` after a full build. This requires the cached baseline workbook and .qa/threshold.xlsx from the same full build. To persist new assumptions through a full rebuild, change src/expansion_model.py. Manual edits made in Excel recalculate the linked scenarios and dashboard; a full rebuild restores the source-controlled assumptions. The snapshot date is fixed. Refreshing a source or changing the cutoff requires a new evidence review and an explicit update to data/archive_hashes.csv.

## Model conventions

- Five integrated cases run quarterly from December 2026 through March 2031. FY Forecast aggregates the on-time statements and combines FY27 with reported H1. Rows 37–38 show forecast-period flows. Other assets and liabilities are fixed at opening residuals. No balancing plug is used.
- The core volume index and OHT relative realization are analyst proxies. September standalone product mix anchors core equivalent-unit shares. CAMSO end-customer billing is scaled separately. Acquired FY26 product revenue of ₹420.65cr supports a directional ex-CAMSO comparison. Group physical volumes, audited segment profit and individual plant returns are unavailable.
- Existing borrowing costs accrue on opening debt, planned term proceeds accrue from draw, and a balancing draw accrues interest from the next quarter. Projected short-term renewals and term funding are assumptions. Gross term balances, reported current maturities and disclosed repayment weights are reconciled in Funding Inputs. Leases are debt in the EV and new ROU assets are capital investment in UFCF.
- The original DCF and original scenario/sensitivity schedules are labeled reference. Normalized DCF contains the revised calculation, value bridge, peer-beta sensitivity and market-implied margin path. Trading Comps distinguishes the three FY26 peers, two aligned September LTM peers and MRF's June LTM observation.
- data/raw holds the frozen issuer and market archive. CCIL's yield is transcribed in the dated source register; its original daily web table is not archived. Some older filing dispatch days remain unverified. The inventory commitment has no disclosed September unpaid balance. Analyst debt terms, minimum cash and stress triggers are not company covenants.

Independent public-information analyst portfolio project.
