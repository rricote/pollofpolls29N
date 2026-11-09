import json,math
from load_reg import load
reg=load()
H={k:{p['id']:p for p in v} for k,v in json.load(open('/tmp/claude-0/-home-claude/eea0bbaf-2db4-5718-a729-17707b9905cb/scratchpad/el/hist.json')).items()}
NATB={'PP':0.309,'PSOE':0.268,'VOX':0.191}   # media de encuestas actual (referencia nacional de las autonómicas 2025-26)
G={'PP':['PP'],'PSOE':['PSOE'],'VOX':['Vox']}
W={'PP':0.30,'PSOE':0.20,'VOX':0.0}
cases=[('01','andalucia','2022-06-19','2026-05-17','201911'),('02','aragon','2023-05-28','2026-02-08','202307'),('07','castilla-y-leon','2022-02-13','2026-03-15','201911'),('11','extremadura','2023-05-28','2025-12-21','202307')]
def nat(k,g): return sum(p['votes'].get(g,0) for p in H[k].values())/sum(p['valid'] for p in H[k].values())
def tot(key,g):
    v=reg[key];P=v['parties'];return sum(x for i,x in v['v'].items() if P[int(i)] in G[g])/(sum(v['v'].values())+v['tot']['bl'])
out={}
for cc,r,a,b,nk in cases:
    provs=[p['c'] for p in reg[(r,b)]['prov']]; row={}
    for g in G:
        base=sum(H['202307'][p]['votes'].get(g,0) for p in provs)/sum(H['202307'][p]['valid'] for p in provs)
        x23=math.log(base/nat('202307',g)); xB=math.log(tot((r,b),g)/NATB[g]); xA=math.log(tot((r,a),g)/nat(nk,g))
        z=xB-x23; dreg=xB-xA; zc=(z+dreg)/2
        row[g]={'z':round(z,3),'dreg':round(dreg,3),'zc':round(zc,3),'m':round(W[g]*zc,4)}
    out[cc]=row; print(r,row)
json.dump(out,open('reg_prior.json','w'))
