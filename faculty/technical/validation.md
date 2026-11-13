# Data validation and reproducibility

**Source**: all nine files in [`faculty/data/`](../data/). These are **generated synthetic records**; the original MIS781 coursework and old repository demonstration remain separate.

## Independent reconciliation (from source CSVs)

| KPI | Definition | Recomputed |
|---|---|---:|
| Students | Unique `DimStudent.Student_ID` | **500** |
| Courses / academic terms | Unique dimension keys | **44 / 6** |
| Enrolment attempts | `FactEnrollment` rows | **6,061** |
| Graded results | Completed attempts; grade HD/D/C/P/F | **5,742** |
| Passing results | Eligible HD/D/C/P attempts | **4,501** |
| Pass rate | Passing / graded | **78.39%** |
| Mean course mark | Nonblank `Final_Mark` on completed attempts | **63.40/100** |
| Mean attendance | All enrolment attempts, including W/I | **74.47%** |
| Mean study hours | All attempts | **10.29 hours/week** |
| Withdrawn / incomplete | W / I | **177 / 142** |
| Support offers / uptake | Offers with an attended session / offers | **370 / 534 = 69.29%** |

The supplied generator's QA report records **39/39 passing integrity checks** (unique IDs; FK consistency; grade thresholds; chronological order; GPA reconciliation; no future-information leakage in starting risk). The independent workbook-to-CSV metric comparison was done again for this portfolio package; the DAX itself was **not executed inside Power BI** here. The [39 check results](qa-checks.json) are included for inspection.

## Verification workflow

```bash
python faculty/scripts/generate_faculty_v2.py
python faculty/scripts/validate_and_analyse.py
```

The scripts resolve their root directory from their own locations and regenerate `faculty/data/` and `faculty/analysis/` (after creating the output folders). **Do not point them at the original MIS781 source.** Chart SVGs in `faculty/assets/` were generated independently from the packaged V2 CSVs; the included `faculty/scripts/render_charts.py` regenerates chart assets without external libraries.

### Power BI checks still required

- Import all nine V2 tables; set dimension relationships and chronologically sort `Term_ID`.
- Compare unfiltered cards against the KPI table above.
- Check Grade Count has only **HD/D/C/P/F** and totals 5,742; `[Graded Results]` must **not** be placed in a chart split by grade because it ignores the grade filter.
- Confirm a course selection changes course pass rate and *graded results* consistently; test 2026-T2 = **80.02%** and **1,306** graded attempts in the unfiltered faculty context.
- Check student-term support measures are not unintentionally filtered by teaching-course selections.
- Capture the final dashboard in Power BI **after** these steps; the enclosed screenshot is an honest work-in-progress image.

## Limitations

Synthetic data cannot substantiate true university demand, actual treatment effectiveness or operational improvements. Term-level changes may reflect shifts in course and cohort mix. Attendance and results have shared latent generator features; associations are not causal estimates. The separate follow-up table is observational and includes selection bias.

[Back to case study](../README.md) · [Model](data-model.md)
