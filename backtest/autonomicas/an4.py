exec(open('an1.py').read().split("pairs=[")[0])
import numpy as np
pairs=[('aragon','2019-05-26','2023-05-28'),('castilla-la-mancha','2019-05-26','2023-05-28'),('comunidad-valenciana','2019-04-28','2023-05-28'),('extremadura','2019-05-26','2023-05-28'),('canarias','2019-05-26','2023-05-28'),('castilla-y-leon','2019-05-26','2022-02-13'),('galicia','2020-07-12','2024-02-18'),('pais-vasco','2020-07-12','2024-04-21'),('cataluna','2021-02-14','2024-05-12')]
rows=[]
for r,a,b in pairs:
    A,tA=regshares((r,a)); B,tB=regshares((r,b)); provs=list(A)
    vs19={q['id']:q['valid'] for q in H['201911']}; vs23={q['id']:q['valid'] for q in H['202307']}
    for g in G:
        r19=sum(g19[q][0][g]*vs19[q] for q in provs)/sum(vs19[q] for q in provs)
        r23=sum(g23[q][0][g]*vs23[q] for q in provs)/sum(vs23[q] for q in provs)
        for p in provs:
            if min(A[p][g],B[p][g],g19[p][0][g],g23[p][0][g])<=0.005: continue
            x19=math.log(g19[p][0][g]/r19);x23=math.log(g23[p][0][g]/r23)
            xA=math.log(A[p][g]/tA[g]);xB=math.log(B[p][g]/tB[g])
            rows.append((r,g,x19,x23,xA,xB))
def fit(X,y): return np.linalg.lstsq(X,y,rcond=None)[0]
for g in G:
    d=[q for q in rows if q[1]==g]; a=np.array([q[2:] for q in d]); regs=[q[0] for q in d]
    x19,x23,xA,xB=a.T; y=x23-x19
    feats={'none':np.zeros((len(y),1)),'z=xB-x19':(xB-x19)[:,None],'dreg':(xB-xA)[:,None],'dreg+lev':np.c_[xB-xA,x19],'z+lev':np.c_[xB-x19,x19],'lev':x19[:,None]}
    out=[]
    for n,X in feats.items():
        err=[]
        for r in set(regs):
            tr=np.array([i for i,q in enumerate(regs) if q!=r]);te=np.array([i for i,q in enumerate(regs) if q==r])
            b=fit(X[tr],y[tr]) if n!='none' else np.zeros(1); err+=list((y[te]-X[te]@b)**2)
        b=fit(X,y) if n!='none' else [0]
        out.append('%s %.3f %s'%(n,np.sqrt(np.mean(err)),np.round(b,2)))
    print(g,len(y),' | '.join(out))
