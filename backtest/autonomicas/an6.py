import json,math,numpy as np,sys
sys.path.insert(0,'.')
from eu import eu
H={k:{p['id']:p for p in v} for k,v in json.load(open('hist.json')).items()}
E24=json.load(open('eu24.json')); E19=eu('eu_07201905'); json.dump(E19,open('eu19.json','w'))
def sh(d,g,t): return d['votes'].get(g,0)/d['valid'] if 'votes' in d else d['v'].get(g,0)/d['valid']
def run(label,base,tgt,eus,gs=('PP','PSOE','VOX')):
    # base/tgt/eus dict pid->entry ; y = x_tgt - x_base ; z = x_eu - x_base (within region)
    ccs=set(e['ccaa'] for e in base.values())
    for g in gs:
        L=[]
        for cc in ccs:
            ps=[p for p in base if base[p]['ccaa']==cc and p in eus and sh(base[p],g,0)>.01 and sh(tgt[p],g,0)>.01 and sh(eus[p],g,0)>.01]
            if len(ps)<2: continue
            def reg(d): return sum(sh(d[p],g,0)*d[p]['valid'] for p in ps)/sum(d[p]['valid'] for p in ps)
            rb,rt,re_=reg(base),reg(tgt),reg(eus)
            for p in ps:
                xb=math.log(sh(base[p],g,0)/rb); L.append((cc,xb,math.log(sh(tgt[p],g,0)/rt)-xb,math.log(sh(eus[p],g,0)/re_)-xb))
        a=np.array([x[1:] for x in L]); cs=[x[0] for x in L]; lev,y,z=a.T
        def loo(X):
            err=[]
            for c in set(cs):
                tr=[i for i,q in enumerate(cs) if q!=c];te=[i for i,q in enumerate(cs) if q==c]
                b=np.linalg.lstsq(X[tr],y[tr],rcond=None)[0] if X.shape[1] else np.zeros(0)
                err+=list((y[te]-X[te]@b)**2)
            return np.sqrt(np.mean(err))
        b=np.linalg.lstsq(np.c_[z],y,rcond=None)[0]
        print(label,g,len(y),'corr(z,y)=%.2f w=%.2f  rmse none %.3f | z %.3f | z+lev %.3f'%(np.corrcoef(z,y)[0,1],b[0],np.sqrt((y**2).mean()),loo(np.c_[z]),loo(np.c_[z,lev])))
run('EU19: gen 19abr -> gen 19nov',H['201904'],H['201911'],E19)
run('EU24: gen 19nov -> gen 23   ',H['201911'],H['202307'],E24)
run('EU24: gen 23 -> (EU24 as target itself)',H['202307'],E24,E24) if False else None
