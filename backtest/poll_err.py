import numpy as np,datetime as dt,collections
from polls_hist import *
ES={'2023':(P2023,'2023-07-23',(31.7,33.1,12.4,12.3,None)),'2019n':(P2019N,'2019-11-10',(28.0,20.8,15.1,12.9,6.8)),'2019a':(P2019A,'2019-04-28',(28.7,16.7,10.3,14.3,15.9))}
names=['PSOE','PP','VOX','IZQ','CS']
allz=[]
print('Error de la media de encuestas finales (puntos, estimada - real), sin efectos casa')
for k,(P,d,res) in ES.items():
    d0=dt.date.fromisoformat(d); byh=collections.defaultdict(list)
    for r in P: byh[r[1]].append(((d0-dt.date.fromisoformat(r[0])).days,r))
    line=[]
    for i in range(5):
        if res[i] is None: continue
        num=den=0
        for h,l in byh.items():
            ws=[(0.5**(a/14),r[3+i]) for a,r in l if r[3+i] is not None]
            if not ws: continue
            m=sum(w*v for w,v in ws)/sum(w for w,v in ws); n=max(r[2] for a,r in l); wt=np.sqrt(min(n,2500)); num+=wt*m; den+=wt
        e=num/den; allz.append((e-res[i],res[i],names[i],k)); line.append('%s %.1f vs %.1f (%+.1f)'%(names[i],e,res[i],e-res[i]))
    print(' ',k,'; '.join(line))
z=np.array([e/np.sqrt(t) for e,t,_,_ in allz])
print('sdSys implícito (rms de error/raíz(voto %%)) = %.2f; el modelo usa 0,28; n=%d'%(np.sqrt(np.mean(z**2)),len(z)))
print('error absoluto medio %.2f pts; sesgo medio PP %+.1f, PSOE %+.1f, Vox %+.1f, Izq %+.1f'%(np.mean([abs(e) for e,_,_,_ in allz]),*[np.mean([e for e,_,n,_ in allz if n==p]) for p in ('PP','PSOE','VOX','IZQ')]))
