# Faculty Academic Performance & Student Support

**Aurora University · Enhanced Synthetic Case Study (V2) · Power BI + Python**

> **Decision question:** Which courses show concerning academic outcomes, what evidence supports that concern, and what should an academic leader investigate before acting?

**Why it matters.** A university can have an acceptable overall pass rate while specific courses have more failures. Faculty managers need a reliable, comparable view of academic outcomes — including the denominator behind each rate — before allocating tutoring capacity or asking for an assessment review. This is a simulated decision-support design, **not** a commissioned university engagement.

## 01 · Executive snapshot

| Students | Courses | Teaching terms | Graded attempts | Passing attempts | Overall pass rate |
|---:|---:|---:|---:|---:|---:|
| **500** | 44 | 6 | **5,742** | **4,501** | **78.39%** |

The data model contains **6,061 enrolment attempts** (including 177 withdrawals and 142 incompletes), mean graded course mark **63.40/100**, and mean attendance **74.47%** across *all* enrolment attempts. Rates are based on **course attempts**, not unique students; repeat attempts count separately.

### Dashboard showcase — design concept

![Aurora Faculty dashboard visual design concept with five KPI cards, course-level outcomes, trends and management insight panels](assets/dashboard-design-concept.png)

**Visual design concept (AI-generated, not an exported Power BI report).** This image demonstrates the intended layout and decision narrative; some rendered chart details and labels may differ from the underlying data. **For accurate, independently recomputed figures, use the charts and counts in the sections below.** The real Power BI Service dashboard is still in progress ([view WIP editing screenshot](assets/actual-power-bi-wip.png)); no validated `.pbix` or final report export is claimed.

## 02 · Four findings that shape management decisions

### Course outcomes — investigate the gap, not just the ranking

![Ten lowest course pass rates in V2, filtered to at least 50 eligible results](assets/lowest-course-pass-rates.svg)

**Finding:** Fundamentals of Physics (**64.58%, N=144**), Database Fundamentals (**64.77%, N=264**), Principles of Marketing (**66.67%, N=180**) and Business Law (**67.05%, N=173**) all fall below the overall **78.39%** rate. Among these four, Database Fundamentals combines a low share of passes with the largest eligible result count.

**Interpretation → next question:** Are these results recurring across terms, and do grading design, prerequisites or student composition warrant examination? The low pass rate is a **review signal**, not proof of ineffective teaching.

### Grade composition — distinguish failed results from lower passes

![Grade counts and proportional composition for the four review courses](assets/priority-course-grade-mix.svg)

**Finding:** Database Fundamentals has **93 F grades among 264** graded attempts; Fundamentals of Physics has **51 F grades among 144**. Both imply over one-third of graded results failed. Read the grade mix alongside denominators, not as independent evidence of course difficulty.

### Trend — observe change, without attributing an intervention

![Course-attempt pass rate across the six generated academic terms](assets/pass-rate-term-trend.svg)

**Finding:** The overall rate moves from **76.43% (2024-T1, N=454)** to **80.02% (2026-T2, N=1,306)**. Later terms have more results and potentially different student/course composition; the comparison does **not** establish a causal improvement.

### Engagement — association is useful for triage, not diagnosis

![Passing share by attendance band, source-generated results](assets/attendance-band-comparison.svg)

**Finding:** Attempts below **60% attendance** have a **48.43%** pass share (N=1,016); those at **85–100%** have **96.56%** (N=1,539). The synthetic generator builds related engagement and outcome signals into the data; this is **not** independent proof that higher attendance causes success.

## 03 · Evidence → decision → monitoring

| Evidence | Manager's investigation | Possible next action | How to monitor |
|---|---|---|---|
| Low pass rate with substantial eligible N | Compare grade mix and recurrence by term | Review course assessments and prerequisites with teaching staff | Course pass rate and graded counts next term |
| High F share in a selected course | Examine assessment components and engagement | Consider a targeted support pilot, subject to faculty review | Future grade mix and participation, with comparable cohorts |
| Attendance-associated outcome gap | Check who is underserved and what support is accessible | Review opt-in outreach and teaching-support access | Take-up, later attendance, subsequent results |

**No intervention has been implemented or shown to improve results.** A future evaluation needs a defined baseline, an owner, stable reporting rules and a suitable comparison.

## 04 · How it was built — inspectable evidence

- **Source and governance:** nine synthetic dimension/fact [CSV tables](data/) with [data dictionary](technical/data-dictionary.csv); generated by a [fixed-seed Python script](scripts/generate_faculty_v2.py).
- **Model:** [entity relationships, data grain and Power BI field bindings](technical/data-model.md). Student-term GPA stays separate from course marks; support activity is student-term level.
- **Measures:** [DAX definitions](technical/faculty-measures.dax) with explicit HD/D/C/P/F eligibility and a grade-count measure that preserves legend filtering.
- **Validation:** [reconciled KPIs, 39 integrity checks, Power BI test plan and caveats](technical/validation.md), and [machine-readable metric evidence](technical/verified-metrics.json).
- **Reproduction:** run [generator](scripts/generate_faculty_v2.py), then [validator](scripts/validate_and_analyse.py); charts provided as source-grounded SVG assets.

**Portfolio boundary:** the original MIS781 coursework, the older repository demonstration and this enhanced V2 are separate versions. V2 figures should not be represented as historical university statistics or as verified impact. The actual Power BI report is still being styled and tested; no downloadable, validated V2 PBIX is claimed.

[← Repository overview](../README.md)
