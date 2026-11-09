import json,math,numpy as np,sys
sys.path.insert(0,'/home/claude/reg')
from load_reg import load
reg=load()
H={k:{p['id']:p for p in v} for k,v in json.load(open('hist.json')).items()}
E19=json.load(open('eu19.json')); E24=json.load(open('eu24.json'))
G={'PP':['PP','AP'],'PSOE':['PSOE','PSC','PSE-EE'],'VOX':['Vox']}
def regsh(key):
    v=reg[key];P=v['parties'];o={}
    for p in v['prov']:
        t=sum(p['v'].values())+p['bl']; o[p['c']]={g:sum(x for i,x in p['v'].items() if P[int(i)] in n)/t for g,n in G.items()}|{'valid':t}
    return o
def sh(d,g):
    if 'votes' in d: return d['votes'].get(g,0)/d['valid']
    if 'v' in d: return d['v'].get(g,0)/d['valid']
    return d[g]
def study(label,base,tgt,srcs,regs):
    # srcs: dict name->dict pid->entry ; regs: region codes allowed (provinces) ; within-region comparison on provinces common to all
    for g in G:
        rows=[]
        for cc in set(e['ccaa'] for e in base.values()):
            ps=[p for p in base if base[p]['ccaa']==cc and all(p in s for s in srcs.values()) and p in regs and all(sh(s[p],g)>.01 for s in list(srcs.values())+[base,tgt] if p in s)]
            if len(ps)<2: continue
            def rg(d): return sum(sh(d[p],g)*d[p]['valid'] for p in ps)/sum(d[p]['valid'] for p in ps)
            xb={p:math.log(sh(base[p],g)/rg(base)) for p in ps}
            for p in ps:
                row=[cc,math.log(sh(tgt[p],g)/rg(tgt))-xb[p],xb[p]]+[math.log(sh(s[p],g)/rg(s))-xb[p] for s in srcs.values()]
                rows.append(row)
        if not rows: continue
        cs=[r[0] for r in rows]; A=np.array([r[1:] for r in rows]); y=A[:,0]; Z=A[:,2:]; lev=A[:,1]
        def loo(X):
            err=[]
            for c in set(cs):
                tr=[i for i,q in enumerate(cs) if q!=c];te=[i for i,q in enumerate(cs) if q==c]
                if not te or not tr: continue
                b=np.linalg.lstsq(X[tr],y[tr],rcond=None)[0] if X.shape[1] else np.zeros(0)
                err+=list((y[te]-X[te]@b)**2)
            return np.sqrt(np.mean(err))
        b=np.linalg.lstsq(Z,y,rcond=None)[0]
        print(label,g,len(y),'w=',np.round(b,2),'rmse none %.3f joint %.3f'%(np.sqrt((y**2).mean()),loo(Z)),'| each:',[round(loo(Z[:,[i]]),3) for i in range(Z.shape[1])])
# abr19 -> nov19 with EU19 and regionals of 2019
R19={}
for r,e in [('aragon','2019-05-26'),('castilla-la-mancha','2019-05-26'),('castilla-y-leon','2019-05-26'),('extremadura','2019-05-26'),('canarias','2019-05-26'),('comunidad-valenciana','2019-04-28')]:
    for c,d in regsh((r,e)).items(): R19[c]=d
# regional entries need ccaa/valid fields
base=H['201904'];tgt=H['201911']
R19={c:{**d} for c,d in R19.items()}
study('abr19->nov19 [EU19, regional19]',base,tgt,{'EU19':E19,'REG19':R19},set(R19))
study('abr19->nov19 [EU19 only, same provs]',base,tgt,{'EU19':E19},set(R19))
study('abr19->nov19 [regional only]',base,tgt,{'REG19':R19},set(R19))
study('abr19->nov19 [EU19 all provs]',base,tgt,{'EU19':E19},set(base))
