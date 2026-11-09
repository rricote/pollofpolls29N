import json,math,numpy as np
from load_reg import load
reg=load(); M={p['id']:p for p in json.load(open('model_prov.json'))}
G={'PP':['PP'],'PSOE':['PSOE'],'VOX':['Vox']}
for r,e in [('andalucia','2026-05-17'),('aragon','2026-02-08'),('castilla-y-leon','2026-03-15'),('extremadura','2025-12-21')]:
    v=reg[(r,e)];P=v['parties']; pv={p['c']:p for p in v['prov']}
    ps=list(pv)
    for g,n in G.items():
        def rs(p): t=sum(p['v'].values())+p['bl']; return sum(x for i,x in p['v'].items() if P[int(i)] in n)/t
        w={q:M[q]['valid'] for q in ps}; W=sum(w.values())
        rm=sum(M[q]['sh'][g]*w[q] for q in ps)/W; r23=sum(M[q]['b23'][g]*w[q] for q in ps)/W; rr=sum(rs(pv[q])*w[q] for q in ps)/W
        a=[];b=[]; txt=[]
        for q in ps:
            dm=math.log(M[q]['sh'][g]/rm)-math.log(M[q]['b23'][g]/r23); dr=math.log(rs(pv[q])/rr)-math.log(M[q]['b23'][g]/r23)
            a.append(dm);b.append(dr); txt.append('%s %+.2f/%+.2f'%(M[q]['name'][:6],dm,dr))
        print(r,g,'corr %.2f'%(np.corrcoef(a,b)[0,1] if len(a)>2 else float('nan')),' model/regional within-region shift:',' '.join(txt))
