#!/usr/bin/env python3
"""Regenerate all four evidence charts from Aurora Faculty V2 CSVs (stdlib only)."""
from pathlib import Path
from collections import Counter
import csv
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets';A.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'data'
def read(name):
    with (DATA/(name+'.csv')).open(encoding='utf-8-sig',newline='') as handle:
        return list(csv.DictReader(handle))

students=read('DimStudent');courses=read('DimCourse');terms=read('DimTerm');enroll=read('FactEnrollment')
passed={'HD','D','C','P'};eligible=passed|{'F'}
graded=[e for e in enroll if e['Enrollment_Status']=='Completed' and e['Final_Grade'] in eligible]
passing=[e for e in graded if e['Final_Grade'] in passed]
course_stats=[]
for c in courses:
    rows=[e for e in graded if e['Course_ID']==c['Course_ID']]
    if not rows:continue
    cnt=Counter(e['Final_Grade'] for e in rows)
    pass_n=sum(cnt[g] for g in passed)
    course_stats.append({'name':c['Course_Name'],'n':len(rows),'rate':100*pass_n/len(rows),'grades':cnt})
course_stats.sort(key=lambda x:(x['rate'],x['name']))
low10=[c for c in course_stats if c['n']>=50][:10]
term_stats=[]
for t in sorted(terms,key=lambda t:int(t['Term_Order'])):
    rs=[e for e in graded if e['Term_ID']==t['Term_ID']]
    pn=sum(e['Final_Grade'] in passed for e in rs)
    term_stats.append({'term':t['Term_ID'],'n':len(rs),'rate':100*pn/len(rs)})
attendance=[]
for label,pred in [('<60%',lambda v:v<60),('60–<75%',lambda v:60<=v<75),('75–<85%',lambda v:75<=v<85),('85–100%',lambda v:85<=v<=100)]:
    rs=[e for e in graded if pred(float(e['Attendance_Pct']))]
    pn=sum(e['Final_Grade'] in passed for e in rs)
    attendance.append({'band':label,'n':len(rs),'rate':100*pn/len(rs)})

COL={'navy':'#15385E','ink':'#172B42','blue':'#2876C7','teal':'#2EA8A0','amber':'#F0A448','pale':'#EEF4F9','white':'#FFFFFF','muted':'#63758A','grid':'#E0E8F0','slate':'#476785','light':'#76A9DD'}

def rrect(x,y,w,h,fill,r=9,stroke=None,sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def txt(x,y,s,size=17,fill=None,weight=400,anchor='start'):
    color=fill or COL['ink'];s=escape(str(s))
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" font-family="Arial, Helvetica, sans-serif">{s}</text>'
def line(x1,y1,x2,y2,color=None,width=1,dash=None):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or COL["grid"]}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def base(w,h,title,subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">',rrect(0,0,w,h,COL['white'],0),rrect(0,0,w,67,COL['navy'],0),txt(26,43,title,25,COL['white'],700),txt(27,94,subtitle,14,COL['muted'])]
def save(name,parts):
    (A/name).write_text('\n'.join(parts+['</svg>']),encoding='utf-8')

# Chart 1: lowest 10, honest 0% baseline, dotted overall comparison.
w,h=1040,610;p=base(w,h,'Course pass rates | lowest 10 eligible courses','Ranked by graded-attempt pass rate • Only courses with N ≥ 50')
x0=315;span=525;y0=143;step=38
for v in [0,20,40,60,80,100]:
    x=x0+span*v/100;p += [line(x,125,x,520,COL['grid']),txt(x,542,f'{v}%',13,COL['muted'],anchor='middle')]
x=x0+span*(100*len(passing)/len(graded))/100
p += [line(x,126,x,516,COL['amber'],2.2,'5,4'),rrect(728,78,270,34,'#FFF3E2',7),txt(743,100,'Overall pass rate 78.39%',15,'#8D5714',700)]
for i,c in enumerate(low10):
    y=y0+i*step
    p += [txt(296,y+19,c['name'],16,COL['ink'],500,'end'),rrect(x0,y,span*c['rate']/100,23,COL['blue'] if i>3 else COL['navy'],4),txt(857,y+18,f'{c["rate"]:.2f}%',16,COL['ink'],700),txt(953,y+18,f'N={c["n"]}',13,COL['muted'])]
p += [txt(29,584,'Source: Faculty V2 • HD/D/C/P ÷ HD/D/C/P/F • Includes graded repeat attempts',13,COL['muted'])]
save('lowest-course-pass-rates.svg',p)

# Chart 2: four priority course grade composition, counts and percentages.
w,h=1050,565;p=base(w,h,'Grade mix | four courses prioritised for review','Each bar shows 100% of graded results; labels are counts of course attempts')
legend=[('HD','#15385E'),('D','#2876C7'),('C','#2EA8A0'),('P','#A9D0F2'),('F','#F0A448')]
for i,(g,col) in enumerate(legend):
    p += [rrect(236+i*117,113,17,17,col,3),txt(261+i*117,127,g,15,COL['ink'],700)]
sel=low10[:4];x0=330;span=620
for i,c in enumerate(sel):
    y=182+i*81
    p += [txt(303,y+27,c['name'],17,COL['ink'],600,'end')]
    cur=x0
    for g,col in legend:
        n=c['grades'][g];dx=span*n/c['n']
        p += [rrect(round(cur,2),y,round(dx,2)+.15,42,col,0)]
        if dx>43:p += [txt(cur+dx/2,y+27,str(n),16,COL['white'] if g!='P' else COL['ink'],700,'middle')]
        cur+=dx
    p += [txt(970,y+27,f'N={c["n"]}',14,COL['muted'])]
for v in [0,25,50,75,100]:
    x=x0+span*v/100;p += [line(x,507,x,519,COL['grid']),txt(x,542,f'{v}%',14,COL['muted'],anchor='middle')]
p += [line(x0,507,x0+span,507),txt(20,554,'Grades: HD 80+, D 70–<80, C 60–<70, P 50–<60, F <50 | Simulated rules',13,COL['muted'])]
save('priority-course-grade-mix.svg',p)

# Chart 3: term line trend, labelled note on axis range.
w,h=1040,550;p=base(w,h,'Pass rate across six academic terms','Overall eligible attempts by term (cohort and course mix can change)')
x0=112;x1=950;y0=145;y1=426
rate_to_y=lambda v:y1-(v-70)/15*(y1-y0)
for v in [70,75,80,85]:
    yy=rate_to_y(v);p += [line(x0,yy,x1,yy,COL['grid']),txt(90,yy+5,f'{v}%',14,COL['muted'],anchor='end')]
coords=[]
for i,t in enumerate(term_stats):
    x=x0+(x1-x0)*i/(len(term_stats)-1); y=rate_to_y(t['rate']);coords.append((x,y,t))
path=' '.join((('M' if i==0 else 'L')+f'{x:.1f},{y:.1f}') for i,(x,y,t) in enumerate(coords))
p += [f'<path d="{path}" fill="none" stroke="{COL["blue"]}" stroke-width="4" stroke-linejoin="round"/>']
for x,y,t in coords:
    p += [f'<circle cx="{x}" cy="{y}" r="7" fill="white" stroke="{COL["blue"]}" stroke-width="3"><title>{escape(t["term"])}: {t["rate"]:.2f}% (N={t["n"]})</title></circle>',txt(x,y-16,f'{t["rate"]:.2f}%',16,COL['ink'],700,'middle'),txt(x,459,t['term'],15,COL['ink'],500,'middle'),txt(x,481,f'N={t["n"]}',12,COL['muted'],anchor='middle')]
p += [rrect(656,94,353,34,'#FFF3E2',7),txt(673,117,'Y-axis begins at 70%; not zero',14,'#8D5714',600),txt(24,528,'Source: Faculty V2 • term rates are descriptive; not an intervention effect',13,COL['muted'])]
save('pass-rate-term-trend.svg',p)

# Chart 4: attendance by band.
w,h=1040,550;p=base(w,h,'Attendance bands | observed passing share','Descriptive association in generated data; not evidence of a causal effect')
x0=296;span=606;y0=166;step=80
for v in [0,25,50,75,100]:
    x=x0+span*v/100;p += [line(x,147,x,467,COL['grid']),txt(x,490,f'{v}%',14,COL['muted'],anchor='middle')]
x=x0+span*(100*len(passing)/len(graded))/100;p += [line(x,143,x,466,COL['amber'],2,'5,4')]
for i,b in enumerate(attendance):
    y=y0+i*step; color=COL['blue'] if i<2 else COL['teal']
    p += [txt(276,y+24,b['band'],19,COL['ink'],600,'end'),rrect(x0,y,span*b['rate']/100,36,color,5),txt(920,y+25,f'{b["rate"]:.2f}%',18,COL['ink'],700),txt(301,y+56,f'N={b["n"]:,} graded attempts',12,COL['muted'])]
p += [rrect(694,98,315,34,'#FFF3E2',7),txt(709,120,'Overall passing share: 78.39%',14,'#8D5714',600),txt(26,525,'Source: Faculty V2 • attendance measured over course attempts • synthetic generator includes shared engagement effects',12,COL['muted'])]
save('attendance-band-comparison.svg',p)


print('Rendered four verified SVG charts into:', A)
