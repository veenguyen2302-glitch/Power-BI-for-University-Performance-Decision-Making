#!/usr/bin/env python3
"""Independent CSV checks and descriptive insights (stdlib only)."""
from __future__ import annotations
import csv,json,statistics,math,sys
from collections import Counter,defaultdict
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; VALID=ROOT/'validation'; ANAL=ROOT/'analysis'
VALID.mkdir(exist_ok=True);ANAL.mkdir(exist_ok=True)

def load(name):
    with (DATA/(name+'.csv')).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows,headers=None):
    if not rows:return
    with (ANAL/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=headers or list(rows[0]));w.writeheader();w.writerows(rows)
def num(v):return float(v) if v not in ('',None) else None
def avg(xs):
    xs=[x for x in xs if x is not None]
    return sum(xs)/len(xs) if xs else None
def pp(v):return round(100*v,2) if v is not None else None
def rnd(v):return round(v,2) if v is not None else None

students=load('DimStudent');programs=load('DimProgram');faculties=load('DimFaculty')
courses=load('DimCourse');terms=load('DimTerm');enroll=load('FactEnrollment')
snapshots=load('FactStudentTerm');support=load('FactSupportCase')
by_sid={r['Student_ID']:r for r in students};by_pid={r['Program_ID']:r for r in programs}
by_fid={r['Faculty_ID']:r for r in faculties};by_cid={r['Course_ID']:r for r in courses}
by_tid={r['Term_ID']:r for r in terms};by_stk={r['StudentTermKey']:r for r in snapshots}
term_order={r['Term_ID']:int(r['Term_Order']) for r in terms}
GP={'HD':4,'D':3,'C':2,'P':1,'F':0};PAS={'HD','D','C','P'}
checks=[]
def check(name,condition,detail=''):
    checks.append(dict(Check=name,Status=('PASS' if condition else 'FAIL'),Details=detail))
check('Exactly 500 unique students',len(students)==500 and len(by_sid)==500,str(len(students)))
for t,rows,key in [('Faculty',faculties,'Faculty_ID'),('Program',programs,'Program_ID'),('Course',courses,'Course_ID'),('Term',terms,'Term_ID'),('Enrollment',enroll,'Enrollment_ID'),('StudentTerm',snapshots,'StudentTermKey'),('SupportCase',support,'Support_ID')]:
    check('Unique '+key,len(rows)==len({r[key] for r in rows}),f'{len(rows)} records')
check('Enrollment Student-Course-Term unique',len(enroll)==len({(r['Student_ID'],r['Course_ID'],r['Term_ID']) for r in enroll}),str(len(enroll)))
check('Student ID FK',all(e['Student_ID'] in by_sid for e in enroll))
check('Course ID FK',all(e['Course_ID'] in by_cid for e in enroll))
check('Term ID FK',all(e['Term_ID'] in by_tid for e in enroll))
check('Program Faculty FKs',all(p['Faculty_ID'] in by_fid for p in programs))
check('Course Faculty FKs',all(c['Faculty_ID'] in by_fid for c in courses))
check('Student Program FK',all(s['Program_ID'] in by_pid for s in students))
check('Student Entry Term FK',all(s['Entry_Term_ID'] in by_tid for s in students))
check('FactStudentTerm FKs',all(r['Student_ID'] in by_sid and r['Term_ID'] in by_tid for r in snapshots))
check('Support StudentTerm FK',all(s['StudentTermKey'] in by_stk for s in support))
check('Enrol StudentTerm correct',all(e['StudentTermKey']==f"{e['Student_ID']}|{e['Term_ID']}" and e['StudentTermKey'] in by_stk for e in enroll))
check('Snapshot StudentTerm correct',all(st['StudentTermKey']==f"{st['Student_ID']}|{st['Term_ID']}" for st in snapshots))
check('Term chronological ordering',all(date.fromisoformat(t['Start_Date'])<date.fromisoformat(t['Census_Date'])<date.fromisoformat(t['End_Date'])<date.fromisoformat(t['Result_Release_Date']) for t in terms))
check('Student not enrolled before entry',all(term_order[e['Term_ID']]>=term_order[by_sid[e['Student_ID']]['Entry_Term_ID']] for e in enroll))
check('Student entry date matches term',all(s['Entry_Date']==by_tid[s['Entry_Term_ID']]['Start_Date'] for s in students))
check('Student status domain',all(s['Latest_Study_Status'] in ('Continuing','Paused','Exited') for s in students))
check('Study load domain',all(s['Study_Load'] in ('Full-time','Part-time') for s in students))
check('Scholarship domain',all(s['Scholarship_Type'] in ('None','Merit','Access') for s in students))
check('No out-of-range source metrics',all(0<=float(e['Attendance_Pct'])<=100 and 0<=float(e['Week4_Attendance_Pct'])<=100 and 0<=float(e['Study_Hours_Per_Week'])<=28 for e in enroll))
check('Grade and enrollment status consistent',all((e['Enrollment_Status']=='Completed' and e['Final_Grade'] in GP and e['Final_Mark'] and e['Grade_Points']!='' and e['Result_Release_Date']!='') or
                       (e['Enrollment_Status']=='Withdrawn' and e['Final_Grade']=='W' and e['Final_Mark']=='' and e['Grade_Points']=='' and e['Result_Release_Date']=='') or
                       (e['Enrollment_Status']=='Incomplete' and e['Final_Grade']=='I' and e['Final_Mark']=='' and e['Grade_Points']=='' and e['Result_Release_Date']=='') for e in enroll))
check('Grade matches published simulated threshold',all(e['Final_Grade']==('HD' if float(e['Final_Mark'])>=80 else 'D' if float(e['Final_Mark'])>=70 else 'C' if float(e['Final_Mark'])>=60 else 'P' if float(e['Final_Mark'])>=50 else 'F') for e in enroll if e['Enrollment_Status']=='Completed'))
check('Grade points match mapping',all(float(e['Grade_Points'])==GP[e['Final_Grade']] for e in enroll if e['Final_Grade'] in GP))
hist=defaultdict(list)
for e in sorted(enroll,key=lambda e:(e['Student_ID'],e['Course_ID'],term_order[e['Term_ID']])):
    hist[(e['Student_ID'],e['Course_ID'])].append(e)
att_err=[];bad_repeats=[]
for key,rows in hist.items():
    for idx,e in enumerate(rows):
        if int(e['Attempt_No'])!=idx+1:att_err.append(e['Enrollment_ID'])
        if idx and rows[idx-1]['Final_Grade'] not in ('F','I','W'):bad_repeats.append(e['Enrollment_ID'])
check('Attempt_No is sequential',not att_err,str(len(att_err))+' errors')
check('Retakes only after F/W/I',not bad_repeats,str(len(bad_repeats))+' errors')
check('Retake capped at 3 attempts',all(len(v)<=3 for v in hist.values()))
check('Support offer max one per student-term',len(support)==len({r['StudentTermKey'] for r in support}))
support_dates_ok=True
for u in support:
    snap=by_stk[u['StudentTermKey']];t=by_tid[snap['Term_ID']]
    offer=date.fromisoformat(u['Referral_Date'])
    if not (date.fromisoformat(t['Start_Date']) < offer < date.fromisoformat(t['End_Date'])):support_dates_ok=False
    count=int(u['Sessions_Attended'])
    if u['Support_Status'] in ('Completed','Partially attended') and count<1:support_dates_ok=False
    if u['Support_Status'] in ('Declined','Did not attend') and count!=0:support_dates_ok=False
    if count:
        first=date.fromisoformat(u['First_Session_Date']);follow=date.fromisoformat(u['Follow_Up_Date'])
        if not (offer<=first<=follow<=date.fromisoformat(t['End_Date'])):support_dates_ok=False
    elif u['First_Session_Date'] or u['Follow_Up_Date']:support_dates_ok=False
check('Support temporal logic, activity and statuses',support_dates_ok)

# Independently reconstruct cumulative and term GPA in chronological order.
enroll_by_term=defaultdict(list)
for e in enroll:enroll_by_term[e['StudentTermKey']].append(e)
snap_by_student=defaultdict(list)
for s in snapshots:snap_by_student[s['Student_ID']].append(s)
snap_err=[]; risk_err=[]; term_counts_err=[]
for sid,records in snap_by_student.items():
    accumulated=[];prev_gpa=None;prev_att=None;prev_fail=0
    for idx,s in enumerate(sorted(records,key=lambda a:term_order[a['Term_ID']])):
        eligible=[e for e in enroll_by_term[s['StudentTermKey']] if e['Final_Grade'] in GP]
        passnum=sum(e['Final_Grade'] in PAS for e in eligible)
        fails=sum(e['Final_Grade']=='F' for e in eligible)
        weighted=[(int(by_cid[e['Course_ID']]['Credit_Points']), GP[e['Final_Grade']]) for e in eligible]
        expected_t=round(sum(cp*gp for cp,gp in weighted)/sum(cp for cp,gp in weighted),2) if weighted else None
        expected_prior=round(sum(cp*gp for cp,gp in accumulated)/sum(cp for cp,gp in accumulated),2) if accumulated else None
        expected_risk=('No prior results' if not accumulated else
            'High' if (prev_gpa is not None and prev_gpa<1.7) or (prev_att is not None and prev_att<55) or prev_fail>=2 else
            'Moderate' if (prev_gpa is not None and prev_gpa<2.5) or (prev_att is not None and prev_att<70) or prev_fail>=1 else 'Low')
        if s['Risk_Band_At_Term_Start']!=expected_risk:risk_err.append(s['StudentTermKey'])
        if len(eligible)!=int(s['Term_Graded_Results']) or passnum!=int(s['Term_Passing_Results']) or fails!=int(s['Term_Failed_Results']):term_counts_err.append(s['StudentTermKey'])
        if s['Prior_Graded_Results']!=str(len(accumulated)):term_counts_err.append(s['StudentTermKey']+' prior count')
        accumulated+=weighted
        expected_cum=round(sum(cp*gp for cp,gp in accumulated)/sum(cp for cp,gp in accumulated),2) if accumulated else None
        def close(raw,expected):
            return (raw=='' and expected is None) or (raw!='' and expected is not None and abs(float(raw)-expected)<0.011)
        if not all([close(s['Term_GPA'],expected_t),close(s['Cumulative_GPA_End'],expected_cum),
                    close(s['Prior_Cumulative_GPA'],expected_prior),close(s['Prior_Term_GPA'],prev_gpa),
                    close(s['Prior_Term_Attendance_Pct'],prev_att),
                    s['Prior_Term_Failed_Results']==str(prev_fail)]):snap_err.append(s['StudentTermKey'])
        if int(s['Cumulative_Graded_Results'])!=len(accumulated) or int(s['Cumulative_Graded_Credit_Points'])!=sum(cp for cp,gp in accumulated):snap_err.append(s['StudentTermKey']+' credits')
        prev_gpa=expected_t;prev_att=round(avg([num(e['Attendance_Pct']) for e in enroll_by_term[s['StudentTermKey']]]),2)
        prev_fail=fails
check('Term and cumulative GPA reconcile independently',not snap_err,str(len(snap_err))+' errors')
check('Prior-term risk has no future/result leakage',not risk_err,str(len(risk_err))+' errors')
check('Term result counts reconcile',not term_counts_err,str(len(term_counts_err))+' errors')
check('No invalid GPA',all((not s['Term_GPA'] or 0<=float(s['Term_GPA'])<=4) and (not s['Cumulative_GPA_End'] or 0<=float(s['Cumulative_GPA_End'])<=4) for s in snapshots))

report=dict(dataset='Aurora Faculty V2 — 500 fully synthetic students',checks=checks,
            passed=sum(c['Status']=='PASS' for c in checks),failed=sum(c['Status']=='FAIL' for c in checks),
            notes=['A PASS validates simulated integrity against documented rules, not real-world representativeness.',
                   'No observed treatment effect is claimed; support participation is non-random.',
                   'Course grades and pass rates exclude W and I and include graded retake attempts.',
                   'All original academic data remain unchanged.'])
(VALID/'Data_Quality_Report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
with (VALID/'Data_Quality_Report.md').open('w',encoding='utf-8') as f:
    f.write('# Aurora Faculty V2 — Data Quality Report\n\n')
    f.write(f"**Tests:** {report['passed']} passed; {report['failed']} failed. **Scope:** generated synthetic data only.\n\n")
    f.write('| Validation | Status | Detail |\n|---|---|---|\n')
    for c in checks:f.write(f"| {c['Check']} | {c['Status']} | {c['Details']} |\n")
    f.write('\n'+ '\n'.join('- '+n for n in report['notes'])+'\n')
print('QA',report['passed'],'PASS',report['failed'],'FAIL')
if report['failed']:
    print('FAILED', [c for c in checks if c['Status']=='FAIL']);sys.exit(1)

# Recompute all descriptive metrics independently from emitted CSVs.
passrows=[e for e in enroll if e['Final_Grade'] in GP]
passnum=sum(e['Final_Grade'] in PAS for e in passrows)
coursegroups=defaultdict(list); termgroups=defaultdict(list); attendee=defaultdict(list);prep=defaultdict(list)
for e in enroll:
    coursegroups[e['Course_ID']].append(e)
    termgroups[e['Term_ID']].append(e)
    if e['Final_Grade'] in GP:
        a=num(e['Attendance_Pct'])
        band=('<60%' if a<60 else '60–<75%' if a<75 else '75–<85%' if a<85 else '85–100%')
        attendee[band].append(e)
        prep[e['Exam_Preparation']].append(e)

def calc(rows):
    eligible=[e for e in rows if e['Final_Grade'] in GP]
    passing=sum(e['Final_Grade'] in PAS for e in eligible)
    return dict(Enrollment_Rows=len(rows),Unique_Students=len({e['Student_ID'] for e in rows}),
                Graded_Results=len(eligible),Passing_Results=passing,
                Failed_Results=sum(e['Final_Grade']=='F' for e in eligible),
                Pass_Rate_Pct=pp(passing/len(eligible)) if eligible else None,
                Avg_Course_Mark=rnd(avg([num(e['Final_Mark']) for e in eligible])),
                Avg_Attendance_Pct=rnd(avg([num(e['Attendance_Pct']) for e in rows])),
                Avg_Study_Hours_Per_Week=rnd(avg([num(e['Study_Hours_Per_Week']) for e in rows])),
                Mean_Grade_Points=rnd(avg([GP[e['Final_Grade']] for e in eligible])))

course_metrics=[]
for cid,rows in coursegroups.items():
    c=by_cid[cid];record=dict(Course_ID=cid,Course_Name=c['Course_Name'],Faculty=by_fid[c['Faculty_ID']]['Faculty_Name'],
                                Course_Level=c['Course_Level']);record.update(calc(rows))
    course_metrics.append(record)
course_metrics.sort(key=lambda x:(x['Pass_Rate_Pct'],x['Course_Name']))
write('course_metrics.csv',course_metrics)
term_metrics=[]
for tid,rows in termgroups.items():
    d=dict(Term_ID=tid,Term_Order=term_order[tid]);d.update(calc(rows));term_metrics.append(d)
term_metrics.sort(key=lambda x:x['Term_Order']);write('term_metrics.csv',term_metrics)
attendance_metrics=[]
for label in ['<60%','60–<75%','75–<85%','85–100%']:
    d=dict(Attendance_Band=label);d.update(calc(attendee[label]));attendance_metrics.append(d)
write('attendance_band_metrics.csv',attendance_metrics)
prep_metrics=[]
for label in ['Early','Regular','Last minute','None']:
    d=dict(Exam_Preparation=label);d.update(calc(prep[label]));prep_metrics.append(d)
write('exam_preparation_metrics.csv',prep_metrics)

# Follow-up: next ADJACENT term ONLY, not just the next observed record; no causal estimate.
support_by_stk={s['StudentTermKey']:s for s in support}
term_by_student=defaultdict(dict)
for s in snapshots:term_by_student[s['Student_ID']][term_order[s['Term_ID']]]=s
support_outcomes=[]
for snap in snapshots:
    j=term_order[snap['Term_ID']]
    if j>=6:continue
    fut=term_by_student[snap['Student_ID']].get(j+1)
    if not fut or snap['Term_GPA']=='' or fut['Term_GPA']=='':continue
    sup=support_by_stk.get(snap['StudentTermKey'])
    participation='Participated' if sup and int(sup['Sessions_Attended'])>0 else 'Not participated'
    support_outcomes.append(dict(StudentTermKey=snap['StudentTermKey'],Term_ID=snap['Term_ID'],
        Risk_Band_At_Term_Start=snap['Risk_Band_At_Term_Start'],
        Support_Participation=participation,Term_GPA=num(snap['Term_GPA']),
        Next_Term_GPA=num(fut['Term_GPA']),Next_Term_GPA_Change=round(num(fut['Term_GPA'])-num(snap['Term_GPA']),2)))
# One row per eligible student-term, next consecutive term only. Derived/analytical fact.
with (DATA/'FactSupportFollowup.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(support_outcomes[0]));w.writeheader();w.writerows(support_outcomes)
print('FactSupportFollowup.csv:',len(support_outcomes),'records')
followup_groups=defaultdict(list)
for x in support_outcomes:followup_groups[(x['Risk_Band_At_Term_Start'],x['Support_Participation'])].append(x)
followup_metrics=[]
for (risk,participation),xs in sorted(followup_groups.items()):
    followup_metrics.append(dict(Risk_Band_At_Term_Start=risk,Support_Participation=participation,
        Eligible_Adjacent_Term_Students=len(xs),Avg_Current_Term_GPA=rnd(avg([x['Term_GPA'] for x in xs])),
        Avg_Next_Term_GPA=rnd(avg([x['Next_Term_GPA'] for x in xs])),
        Avg_Next_Term_GPA_Change=rnd(avg([x['Next_Term_GPA_Change'] for x in xs]))))
write('support_follow_up_metrics.csv',followup_metrics)

# Snapshot KPI values only at all-time/term level; cumulative GPA from latest snapshot per student.
latest_snap=[max(a,key=lambda r:term_order[r['Term_ID']]) for a in snap_by_student.values()]
latest_valid=[s for s in latest_snap if s['Cumulative_GPA_End']!='']
all_calc=calc(enroll)
all_calc.update(Students=len(students),Courses=len(courses),Student_Term_Records=len(snapshots),
    Support_Offers=len(support),Support_Participants=sum(int(s['Sessions_Attended'])>0 for s in support),
    Avg_Latest_Student_Cumulative_GPA=rnd(avg([float(s['Cumulative_GPA_End']) for s in latest_valid])),
    Withdrawal_Rows=sum(e['Enrollment_Status']=='Withdrawn' for e in enroll),
    Incomplete_Rows=sum(e['Enrollment_Status']=='Incomplete' for e in enroll),
    At_Risk_Student_Term_Records=sum(s['Risk_Band_At_Term_Start'] in ('High','Moderate') for s in snapshots))
meta=dict(overall=all_calc,grade_mix=dict(Counter(e['Final_Grade'] for e in enroll)),
          lowest_courses_min_50=[r for r in course_metrics if r['Graded_Results']>=50][:7],
          highest_courses_min_50=sorted([r for r in course_metrics if r['Graded_Results']>=50],key=lambda x:x['Pass_Rate_Pct'],reverse=True)[:5],
          term_metrics=term_metrics,attendance=attendance_metrics,exam_prep=prep_metrics,
          support_follow_up=followup_metrics)
(ANAL/'reproducible_kpis.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('SUMMARY',json.dumps(all_calc,ensure_ascii=False))
print('LOW',[(x['Course_Name'],x['Pass_Rate_Pct'],x['Graded_Results']) for x in meta['lowest_courses_min_50'][:5]])
print('ATTENDANCE',[(x['Attendance_Band'],x['Pass_Rate_Pct'],x['Graded_Results']) for x in attendance_metrics])
