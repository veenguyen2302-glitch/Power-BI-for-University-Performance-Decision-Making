#!/usr/bin/env python3
"""Reproducible Aurora University Faculty V2 synthetic dataset.

Standard-library-only. All people, offerings and outcomes are fictional.
Run: python scripts/generate_faculty_v2.py
The CSV files in ../data/ are regenerated deterministically using SEED.
"""
from __future__ import annotations
import csv, json, math, random, statistics
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'; OUT.mkdir(parents=True,exist_ok=True)
SEED=20261113
R=random.Random(SEED)
STUDENT_COUNT=500
GRADE_POINTS={'HD':4,'D':3,'C':2,'P':1,'F':0}
TERMS=[
    ('2024-T1',2024,'T1',date(2024,3,4),date(2024,3,29),date(2024,6,14),date(2024,6,28)),
    ('2024-T2',2024,'T2',date(2024,7,15),date(2024,8,9),date(2024,10,25),date(2024,11,8)),
    ('2025-T1',2025,'T1',date(2025,3,3),date(2025,3,28),date(2025,6,13),date(2025,6,27)),
    ('2025-T2',2025,'T2',date(2025,7,14),date(2025,8,8),date(2025,10,24),date(2025,11,7)),
    ('2026-T1',2026,'T1',date(2026,3,2),date(2026,3,27),date(2026,6,12),date(2026,6,26)),
    ('2026-T2',2026,'T2',date(2026,7,13),date(2026,8,7),date(2026,10,23),date(2026,11,6)),
]
FACULTIES=[
    {'Faculty_ID':'FAC-BUS','Faculty_Name':'Business and Law'},
    {'Faculty_ID':'FAC-CMP','Faculty_Name':'Computing and Data'},
    {'Faculty_ID':'FAC-SCI','Faculty_Name':'Science and Engineering'},
]
PROGRAMS=[
    ('PRG-COM','Bachelor of Commerce','FAC-BUS'),
    ('PRG-BAN','Bachelor of Business Analytics','FAC-BUS'),
    ('PRG-IT','Bachelor of Information Technology','FAC-CMP'),
    ('PRG-DS','Bachelor of Data Science','FAC-CMP'),
    ('PRG-ENG','Bachelor of Engineering Studies','FAC-SCI'),
    ('PRG-ENV','Bachelor of Environmental Science','FAC-SCI'),
]
PROGRAMS=[dict(Program_ID=i,Program_Name=n,Faculty_ID=f,Nominal_Full_Time_Terms=6) for i,n,f in PROGRAMS]
# Grade rules are a custom fictional 4-point policy, NOT a claim about any actual university.
COURSE_LIST=[
 ('BUS101','Accounting','FAC-BUS',1),('BUS102','Principles of Marketing','FAC-BUS',1),
 ('BUS103','Economics','FAC-BUS',1),('BUS104','Business Law','FAC-BUS',1),
 ('BUS105','Management Principles','FAC-BUS',1),('BUS106','Statistics','FAC-BUS',1),
 ('BUS201','Finance','FAC-BUS',2),('BUS202','Financial Reporting','FAC-BUS',2),
 ('BUS203','Consumer Behaviour','FAC-BUS',2),('BUS204','Marketing Analytics','FAC-BUS',2),
 ('BUS205','Business Ethics','FAC-BUS',2),('BUS206','Operations Management','FAC-BUS',2),
 ('BUS301','Corporate Finance','FAC-BUS',3),('BUS302','Strategic Management','FAC-BUS',3),
 ('BUS303','Decision Modelling','FAC-BUS',3),('BUS304','Business Research','FAC-BUS',3),
 ('CMP101','Programming','FAC-CMP',1),('CMP102','Computing Fundamentals','FAC-CMP',1),
 ('CMP103','Database Fundamentals','FAC-CMP',1),('CMP104','Web Systems','FAC-CMP',1),
 ('CMP201','Data Visualisation','FAC-CMP',2),('CMP202','Database Design','FAC-CMP',2),
 ('CMP203','Software Development','FAC-CMP',2),('CMP204','Cybersecurity','FAC-CMP',2),
 ('CMP205','Systems Analysis','FAC-CMP',2),('CMP206','Probability and Statistics','FAC-CMP',2),
 ('CMP301','Predictive Analytics','FAC-CMP',3),('CMP302','Data Engineering','FAC-CMP',3),
 ('CMP303','Applied AI','FAC-CMP',3),('CMP304','Cloud Systems','FAC-CMP',3),
 ('SCI101','Engineering Mathematics','FAC-SCI',1),('SCI102','Fundamentals of Physics','FAC-SCI',1),
 ('SCI103','Environmental Systems','FAC-SCI',1),('SCI104','Statistics for Science','FAC-SCI',1),
 ('SCI201','Environmental Chemistry','FAC-SCI',2),('SCI202','Research Methods','FAC-SCI',2),
 ('SCI203','Earth Systems','FAC-SCI',2),('SCI204','Systems Design','FAC-SCI',2),
 ('SCI205','Sustainability Policy','FAC-SCI',2),('SCI206','Project Management','FAC-SCI',2),
 ('SCI301','Operations Research','FAC-SCI',3),('SCI302','Environmental Impact Assessment','FAC-SCI',3),
 ('SCI303','Applied Laboratory Skills','FAC-SCI',3),('SCI304','Engineering Project','FAC-SCI',3),
]
COURSES=[dict(Course_ID=i,Course_Name=n,Faculty_ID=f,Course_Level=l,Credit_Points=6)
         for i,n,f,l in COURSE_LIST]
COURSE_BY_ID={c['Course_ID']:c for c in COURSES}
# Latent difficulty is GENERATOR-only and is not an observed analytical variable.
DIFFICULTY={c['Course_ID']:max(-7,min(7,R.gauss(0,3.3))) for c in COURSES}


def clamp(x,a,b): return min(max(x,a),b)
def choose(items,weights): return R.choices(items,weights,k=1)[0]
def grade_from_mark(mark):
    if mark>=80: return 'HD'
    if mark>=70: return 'D'
    if mark>=60: return 'C'
    if mark>=50: return 'P'
    return 'F'
def round2(x): return round(float(x),2)
def iso(x): return x.isoformat() if x is not None else ''
def write_csv(name,headers,rows):
    p=OUT/(name+'.csv')
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=headers,extrasaction='raise'); writer.writeheader()
        writer.writerows(rows)
    print(f'{p.name}: {len(rows):,} records')
    return p

# Students: one student has one major program. Enrollment rows may span multiple courses/terms.
student_rows=[]; hidden={}
entry_indices=[0,1,2,3,4,5]; entry_weights=[0.28,0.12,0.25,0.13,0.15,0.07]
program_ids=[p['Program_ID'] for p in PROGRAMS]
for no in range(1,STUDENT_COUNT+1):
    sid=f'AU-ST{no:04d}'
    pid=choose(program_ids,[0.20,0.19,0.18,0.17,0.13,0.13])
    entryidx=choose(entry_indices,entry_weights)
    study_load=choose(['Full-time','Part-time'],[0.77,0.23])
    ability=R.gauss(0,0.88)
    engagement=clamp(R.gauss(0,0.94),-2.7,2.7)
    score=round2(clamp(69+11.8*ability+R.gauss(0,8),35,98))
    if score>=74 and R.random()<0.28: scholarship='Merit'
    elif R.random()<0.13: scholarship='Access'
    else: scholarship='None'
    age=choose(list(range(17,38)),[1,8,12,15,13,10,8,6,5,4,3,2,2,2,1,1,1,1,1,1,1])
    rec=dict(Student_ID=sid,Program_ID=pid,Entry_Term_ID=TERMS[entryidx][0],
             Entry_Date=iso(TERMS[entryidx][3]),Entry_Age=age,
             Study_Load=study_load,Entry_Score=score,Scholarship_Type=scholarship,
             Latest_Study_Status='')
    student_rows.append(rec)
    hidden[sid]=dict(entry_index=entryidx,ability=ability,engagement=engagement,
                     program=pid,load=study_load,stress_bias=R.gauss(0,0.18))

# Eligible elective pools: program's faculty with selected interdisciplinary options.
program_to_faculty={p['Program_ID']:p['Faculty_ID'] for p in PROGRAMS}
shared={
 'PRG-COM':['CMP101','CMP201','CMP205','SCI206','SCI202'],
 'PRG-BAN':['CMP101','CMP103','CMP201','CMP202','CMP206','CMP301','CMP302','BUS201','SCI301'],
 'PRG-IT':['BUS106','BUS205','BUS303','SCI101','SCI202','SCI301'],
 'PRG-DS':['BUS106','BUS204','BUS303','BUS201','SCI101','SCI104','SCI301'],
 'PRG-ENG':['CMP101','CMP203','CMP205','CMP303','BUS206','BUS303','BUS205'],
 'PRG-ENV':['CMP101','CMP201','BUS103','BUS106','BUS205','BUS206','SCI301'],
}
program_pools={p['Program_ID']:list(dict.fromkeys([c['Course_ID'] for c in COURSES if c['Faculty_ID']==p['Faculty_ID']]+shared[p['Program_ID']])) for p in PROGRAMS}

fact_enrol=[]; fact_term=[]; fact_support=[]; serial=0; support_serial=0
for s in student_rows:
    sid=s['Student_ID']; h=hidden[sid]
    history=defaultdict(list)
    graded_prior=[] # list of (credit_points, grade_points)
    prior_term_gpa=None; prior_term_att=None; prior_term_failed=0
    stopped=False; one_term_pause=False; last_visited=None; terms_studied=0
    engagement=h['engagement']; ability=h['ability']; entryidx=h['entry_index']
    for tix in range(entryidx,len(TERMS)):
        term=TERMS[tix]; tid,year,tl,start,census,end,release=term
        # No post-enrolment information enters the current term's START risk score.
        if stopped: break
        if tix>entryidx:
            stop_prob=0.018 + (0.022 if prior_term_gpa is not None and prior_term_gpa<1.65 else 0)
            if R.random()<stop_prob: stopped=True; break
            if not one_term_pause and R.random()<0.024:
                one_term_pause=True; continue
            one_term_pause=False
        last_visited=tix; terms_studied+=1
        student_term_key=f'{sid}|{tid}'
        if not graded_prior: start_risk='No prior results'
        elif (prior_term_gpa is not None and prior_term_gpa<1.7) or (prior_term_att is not None and prior_term_att<55) or prior_term_failed>=2:
            start_risk='High'
        elif (prior_term_gpa is not None and prior_term_gpa<2.5) or (prior_term_att is not None and prior_term_att<70) or prior_term_failed>=1:
            start_risk='Moderate'
        else: start_risk='Low'
        prior_cum=round2(sum(cp*gp for cp,gp in graded_prior)/sum(cp for cp,gp in graded_prior)) if graded_prior else None
        target=choose([3,4],[0.42,0.58]) if h['load']=='Full-time' else choose([1,2],[0.37,0.63])
        if R.random()<0.06: target=max(1,target-1)
        term_stress=R.gauss(h['stress_bias'],0.74)
        term_engagement=engagement+R.gauss(0,0.30)-0.2*term_stress
        chosen=[]
        # Only failed, withdrawn or incomplete courses may be repeated. Attempt number then increments.
        repeatable=[cid for cid,attempts in history.items() if len(attempts)<3 and attempts[-1] in ('F','W','I')]
        R.shuffle(repeatable)
        for cid in repeatable:
            if len(chosen)<target and R.random()<0.59: chosen.append(cid)
        pool=program_pools[h['program']]
        eligible=[cid for cid in pool if cid not in chosen and cid not in history]
        # Prefer foundation courses early; more advanced courses at later stages.
        R.shuffle(eligible)
        eligible.sort(key=lambda x:(abs(COURSE_BY_ID[x]['Course_Level']-min(3,1+(terms_studied-1)//2))+
                                    R.random()*0.9))
        chosen += eligible[:max(0,target-len(chosen))]
        if len(chosen)<target:
            wider=[c['Course_ID'] for c in COURSES if c['Course_ID'] not in chosen and c['Course_ID'] not in history]
            R.shuffle(wider); chosen+=wider[:target-len(chosen)]
        # Create early engagement features before deciding whom to offer support.
        preliminary=[]
        for cid in chosen:
            attendance=clamp(76+11.0*term_engagement+2.3*ability-6.1*term_stress+
                             R.gauss(0,10)+R.gauss(0,4),20,100)
            week4=clamp(attendance+R.gauss(0,9),15,100)
            hours=clamp(10.6+3.1*term_engagement+0.8*ability+0.15*DIFFICULTY[cid]-
                        1.0*term_stress+R.gauss(0,3.5),1,28)
            prep_ability=engagement+R.gauss(0,1)-0.15*term_stress
            prep=('Early' if prep_ability>1.0 else 'Regular' if prep_ability>-0.3
                  else 'Last minute' if prep_ability>-1.4 else 'None')
            preliminary.append((cid,attendance,week4,hours,prep))
        min_week4=min(x[2] for x in preliminary)
        avg_week4=statistics.mean(x[2] for x in preliminary)
        prior_fail_signal=prior_term_failed>0
        referral_prob=0.07+(0.28 if start_risk=='High' else 0.16 if start_risk=='Moderate' else 0.03)
        referral_prob += 0.18 if avg_week4<62 else 0.09 if min_week4<50 else 0
        referral_prob += 0.07 if prior_fail_signal else 0
        referred=R.random()<min(referral_prob,0.83)
        attended_sessions=0
        if referred:
            support_serial+=1
            support_type=choose(['Peer tutoring','Study planning','Academic skills workshop'],[0.44,0.31,0.25])
            reason=('Low early attendance' if avg_week4<62 else
                    'Prior failed result' if prior_fail_signal else
                    'Prior low academic results' if start_risk in ('High','Moderate') else
                    'Self-request / general support')
            referral=start+timedelta(days=25+R.randint(0,9))
            support_status=choose(['Completed','Partially attended','Declined','Did not attend'],
                                  [0.46,0.25,0.18,0.11])
            attended_sessions=(R.randint(3,5) if support_status=='Completed' else
                               R.randint(1,2) if support_status=='Partially attended' else 0)
            first_session=referral+timedelta(days=R.randint(2,9)) if attended_sessions>0 else None
            followup=(min(end,first_session+timedelta(days=R.randint(14,26))) if first_session else None)
            fact_support.append(dict(Support_ID=f'SUP{support_serial:05d}',StudentTermKey=student_term_key,
                                     Support_Type=support_type,Referral_Reason=reason,
                                     Referral_Date=iso(referral),First_Session_Date=iso(first_session),
                                     Sessions_Attended=attended_sessions,Support_Status=support_status,
                                     Follow_Up_Date=iso(followup),Follow_Up_Status=('Follow-up recorded' if followup else 'Not applicable')))
        term_mark_points=[]; term_attendance=[]; term_fail=0; term_passing=0
        for cid,att,week4,hours,prep in preliminary:
            attempt=len(history[cid])+1
            withdraw_prob=0.027+max(0,(57-att)/600)+max(0,term_stress-1.1)*0.018
            inc_prob=0.018+max(0,(63-att)/800)
            draw=R.random()
            if draw<withdraw_prob: status='Withdrawn'
            elif draw<withdraw_prob+inc_prob: status='Incomplete'
            else: status='Completed'
            if status=='Completed':
                prep_effect={'Early':3.5,'Regular':1.3,'Last minute':-1.0,'None':-3.5}[prep]
                # Simulated modest, uncertain learning-assistance effect; never proof of causal value.
                session_effect=(min(attended_sessions,4)*0.6 if attended_sessions else 0)
                raw=(63.2+8.2*ability+3.8*term_engagement+0.23*(att-74)+
                     0.5*(hours-11)+prep_effect-DIFFICULTY[cid]
                     -2.4*term_stress+1.3*(attempt-1)+session_effect+R.gauss(0,10.8))
                mark=round2(clamp(raw,8,99))
                grade=grade_from_mark(mark)
                gpoints=GRADE_POINTS[grade]
                term_mark_points.append((COURSE_BY_ID[cid]['Credit_Points'],gpoints))
                graded_prior.append((COURSE_BY_ID[cid]['Credit_Points'],gpoints))
                term_passing+=grade!='F'; term_fail+=grade=='F'
            else:
                mark=None;grade='W' if status=='Withdrawn' else 'I';gpoints=None
            serial+=1
            fact_enrol.append(dict(Enrollment_ID=f'ENR{serial:06d}',Student_ID=sid,
                    Term_ID=tid,Course_ID=cid,StudentTermKey=student_term_key,
                    Attempt_No=attempt,Enrollment_Status=status,
                    Final_Mark=mark,Final_Grade=grade,Grade_Points=gpoints,
                    Attendance_Pct=round2(att),Week4_Attendance_Pct=round2(week4),
                    Study_Hours_Per_Week=round2(hours),Exam_Preparation=prep,
                    Result_Release_Date=iso(release) if status=='Completed' else ''))
            history[cid].append(grade)
            term_attendance.append(att)
        tgpa=(round2(sum(cp*g for cp,g in term_mark_points)/sum(cp for cp,g in term_mark_points)) if term_mark_points else None)
        cgpa=(round2(sum(cp*g for cp,g in graded_prior)/sum(cp for cp,g in graded_prior)) if graded_prior else None)
        term_att=(round2(statistics.mean(term_attendance)) if term_attendance else None)
        term_grade_count=len(term_mark_points)
        fact_term.append(dict(StudentTermKey=student_term_key,Student_ID=sid,Term_ID=tid,
                 First_Observed_Term=1 if terms_studied==1 else 0,
                 Prior_Graded_Results=len(graded_prior)-term_grade_count,
                 Prior_Cumulative_GPA=prior_cum,
                 Prior_Term_GPA=prior_term_gpa,
                 Prior_Term_Attendance_Pct=prior_term_att,
                 Prior_Term_Failed_Results=prior_term_failed,
                 Risk_Band_At_Term_Start=start_risk,
                 Term_Graded_Results=term_grade_count,Term_Passing_Results=term_passing,
                 Term_Failed_Results=term_fail,
                 Term_GPA=tgpa,Cumulative_GPA_End=cgpa,
                 Term_Avg_Attendance_Pct=term_att,
                 Cumulative_Graded_Results=len(graded_prior),
                 Cumulative_Graded_Credit_Points=sum(cp for cp,gp in graded_prior)))
        prior_term_gpa=tgpa
        prior_term_att=term_att
        prior_term_failed=term_fail
        # Some persistent engagement variation, but not all students trend upwards.
        engagement=clamp(engagement+R.gauss(0,0.15),-2.8,2.8)
    s['Latest_Study_Status']=('Exited' if stopped else
                              'Paused' if last_visited is None or last_visited<len(TERMS)-1 else
                              'Continuing')

DIM_TERM=[dict(Term_ID=t[0],Academic_Year=t[1],Study_Period=t[2],Start_Date=iso(t[3]),
               Census_Date=iso(t[4]),End_Date=iso(t[5]),Result_Release_Date=iso(t[6]),Term_Order=i+1)
          for i,t in enumerate(TERMS)]
FILES={
 'DimFaculty':(list(FACULTIES[0]),FACULTIES),
 'DimProgram':(list(PROGRAMS[0]),PROGRAMS),
 'DimCourse':(list(COURSES[0]),COURSES),
 'DimTerm':(list(DIM_TERM[0]),DIM_TERM),
 'DimStudent':(list(student_rows[0]),student_rows),
 'FactEnrollment':(list(fact_enrol[0]),fact_enrol),
 'FactStudentTerm':(list(fact_term[0]),fact_term),
 'FactSupportCase':(list(fact_support[0]),fact_support),
}
for name,(cols,rows) in FILES.items():write_csv(name,cols,rows)
meta=dict(dataset='Aurora University — Faculty Academic Performance & Student Support V2',
          synthetic=True,original_coursework_data_modified=False,
          seed=SEED,students=len(student_rows),enrollments=len(fact_enrol),
          student_term_records=len(fact_term),support_offers=len(fact_support),
          graded_results=sum(row['Final_Grade'] in GRADE_POINTS for row in fact_enrol),
          passing_results=sum(row['Final_Grade'] in ('HD','D','C','P') for row in fact_enrol),
          course_count=len(COURSES),terms=len(DIM_TERM),faculties=len(FACULTIES),programs=len(PROGRAMS),
          dataset_as_of='2026-11-06',
          grade_thresholds={'HD':'80-100','D':'70-<80','C':'60-<70','P':'50-<60','F':'<50'},
          grade_points=GRADE_POINTS,
          weights={'course_credit_points':6},
          note='Artificial generator assumptions are documented; associations do not represent real students or causal effects.')
(OUT/'generation_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('META',json.dumps(meta,ensure_ascii=False))
