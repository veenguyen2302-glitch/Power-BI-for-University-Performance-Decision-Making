# Publishing and migration guide — review before upload

## Publish exactly what is new

This package is an **additive portfolio proposal**, not a repository modification. The GitHub connection used for the review was read-only; **nothing has been pushed or deleted**.

1. **Upload `faculty/` intact** to the repository root (GitHub → Add file → Upload files; preserve subfolder paths). All links in `faculty/README.md` are relative.
2. **Replace root `README.md` only after reviewing it**. This replacement is shorter and points to the existing workstreams without claiming their results were updated.
3. Keep all existing `docs/`, `site/`, `data/`, `sql/`, `test/`, `dashboards/` and numbered `.md` files **as they are** for now. They contain the **original/older demo**, not V2; do not silently replace them with V2 numbers.
4. After the Faculty report is fully formatted and checked in Power BI Service, replace `faculty/assets/actual-power-bi-wip.png` with a **real, final Power BI screenshot** and revise the caption. Do not use the AI-generated presentation concept as a Power BI execution screenshot.
5. Before publicising a PBIX, inspect embedded data, credentials, source paths and distribution rights. No `.pbix` is included here.

## Existing repository — planned disposition (no deletion performed)

| Existing path | Status for this publication | Why |
|---|---|---|
| `README.md` | **Replace after review** with delivered concise landing page | Current root README reads as a publication note, rather than a recruiter-facing overview |
| `01-business-understanding.md` and `02-stakeholder-requirements.md` | **Retain as legacy**, later consolidate | Original three-dashboard scenario and proposed (not interviewed) requirements |
| `03-data-model-and-quality.md` | **Retain as legacy; do not reuse for V2** | Contains obsolete demo schema and some stale visual-aggregation interpretation |
| `04-analytical-findings.md` | **Retain as legacy; do not cite as V2** | Contains 650-student older demo and original coursework figures |
| `05-dashboard-design.md` | **Retain for other workstreams; later audit labels** | Figure captions/screenshots are swapped and older warnings need reconciliation |
| `06-decisions-and-interventions.md` to `10-recruitment-story.md` | **Retain as legacy**, later consolidate into compact workstream pages | Useful decision logic, but overly long and some examples assume different data |
| `data/students.csv`, `data/student_results.csv`, `data/work_orders.csv`, `data/departments.csv` | **Keep unchanged** | Older synthetic demo; not the 500-student V2 dataset |
| `dashboards/`, `docs/`, `site/`, `sql/`, `test/` | **Keep unchanged** | Other original project material or demonstration functionality |
| New `faculty/` directory | **Add** | Self-contained verified V2 case study without contaminating legacy datasets |

## Three separate evidence layers

- **Original MIS781**: initial coursework and PBIX files; **not** this package's data source.
- **Older GitHub demonstration**: 650 student records; maintained for provenance, separate from V2.
- **Enhanced Faculty V2**: 500 students, 6,061 attempts, 78.39% attempt-level pass rate; sourced exclusively from `faculty/data/`.

## Quick publish QA

- Check that the root README links to `faculty/README.md`.
- Open the Faculty README on GitHub and confirm all 5 PNG/SVG assets display.
- Check all CSVs and scripts are in matching relative paths.
- Verify actual Power BI outputs before substituting a final dashboard screenshot.
- Make a separate later migration for Facilities and Admissions; don't present them as V2.

*This guide is for the repository owner; it may be omitted from the public repository after uploading.*
