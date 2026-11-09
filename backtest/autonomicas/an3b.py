import json,math,numpy as np
from load_reg import load
reg=load(); H={k:{p['id']:p for p in v} for k,v in json.load(open('/tmp/claude-0/-home-claude/eea0bbaf-2db4-5718-a729-17707b9905cb/scratchpad/el/hist.json')).items()}
single={'asturias':['33'],'baleares':['07'],'cantabria':['39'],'madrid':['28'],'murcia':['30'],'la-rioja':['26'],'navarra':['31']}
G={'PP':['PP','AP'],'PSOE':['PSOE','PSC','PSE-EE'],'VOX':['Vox']}
sel=[('andalucia','2022-06-19'),('aragon','2023-05-28'),('asturias','2023-05-28'),('baleares','2023-05-28'),('canarias','2023-05-28'),('cantabria','2023-05-28'),('castilla-la-mancha','2023-05-28'),('castilla-y-leon','2022-02-13'),('cataluna','2024-05-12'),('comunidad-valenciana','2023-05-28'),('extremadura','2023-05-28'),('galicia','2024-02-18'),('madrid','2023-05-28'),('murcia','2023-05-28'),('la-rioja','2023-05-28'),('pais-vasco','2024-04-21'),('navarra','2023-05-28')]
def nat(k,g): return sum(p['votes'].get(g.replace('VOX','VOX'),0) for p in H[k].values())/sum(p['valid'] for p in H[k].values())
rows=[]
for r,e in sel:
    v=reg[(r,e)];P=v['parties']
    provs=single.get(r) or [p['c'] for p in v['prov']]
    for g,names in G.items():
        if r=='navarra' and g=='PP': continue
        rb=sum(x for i,x in v['v'].items() if P[int(i)] in names)/(sum(v['v'].values())+v['tot']['bl'])
        gr=lambda k: sum(H[k][p]['votes'].get(g,0) for p in provs)/sum(H[k][p]['valid'] for p in provs)
        if min(gr('201911'),gr('202307'),rb)<=0.01: continue
        x19=math.log(gr('201911')/nat('201911',g)); x23=math.log(gr('202307')/nat('202307',g)); xB=math.log(rb/nat('202307',g))
        rows.append((r,g,x19,x23,xB))
for g in G:
    d=[q for q in rows if q[1]==g]; a=np.array([q[2:] for q in d]); x19,x23,xB=a.T
    y=x23-x19; z=xB-x19; w=(z@y)/(z@z)
    err=[]
    for i in range(len(y)):
        m=np.arange(len(y))!=i; ww=(z[m]@y[m])/(z[m]@z[m]); err.append((y[i]-ww*z[i])**2)
    print(g,len(d),'w=%.2f corr %.2f'%(w,np.corrcoef(z,y)[0,1]),'rmse none %.3f  with regional (LOO) %.3f'%(np.sqrt((y**2).mean()),np.sqrt(np.mean(err))))

print('--- dreg (B vs previous regional A) ---')
prevA={'andalucia':None,'aragon':'2019-05-26','asturias':'2019-05-26','baleares':'2019-05-26','canarias':'2019-05-26','cantabria':'2019-05-26','castilla-la-mancha':'2019-05-26','castilla-y-leon':'2019-05-26','cataluna':'2021-02-14','comunidad-valenciana':'2019-04-28','extremadura':'2019-05-26','galicia':'2020-07-12','madrid':'2021-05-04','murcia':'2019-05-26','la-rioja':'2019-05-26','pais-vasco':'2020-07-12','navarra':'2019-05-26'}
# benchmark nat at regional A time ~ closest general: 2019-05 -> 201904 ; 2020-07/2021 -> 201911
natA={'2019-05-26':'201904','2019-04-28':'201904','2020-07-12':'201911','2021-02-14':'201911','2021-05-04':'201911'}
rows2=[]
for r,e in sel:
    a=prevA[r]
    if not a: continue
    v=reg[(r,e)];vA=reg[(r,a)];P=v['parties'];PA=vA['parties']
    provs=single.get(r) or [p['c'] for p in v['prov']]
    for g,names in G.items():
        if r=='navarra' and g=='PP': continue
        sB=sum(x for i,x in v['v'].items() if P[int(i)] in names)/(sum(v['v'].values())+v['tot']['bl'])
        sA=sum(x for i,x in vA['v'].items() if PA[int(i)] in names)/(sum(vA['v'].values())+vA['tot']['bl'])
        gr=lambda k: sum(H[k][p]['votes'].get(g,0) for p in provs)/sum(H[k][p]['valid'] for p in provs)
        if min(gr('201911'),gr('202307'),sA,sB)<=0.01: continue
        x19=math.log(gr('201911')/nat('201911',g)); x23=math.log(gr('202307')/nat('202307',g))
        xB=math.log(sB/nat('202307',g)); xA=math.log(sA/nat(natA[a],g))
        rows2.append((r,g,x19,x23,xB,xA))
for g in G:
    d=[q for q in rows2 if q[1]==g]; a=np.array([q[2:] for q in d]); x19,x23,xB,xA=a.T
    y=x23-x19
    for name,z in [('dreg=xB-xA',xB-xA),('z=xB-x19',xB-x19)]:
        w=(z@y)/(z@z); err=[]
        for i in range(len(y)):
            m=np.arange(len(y))!=i; ww=(z[m]@y[m])/(z[m]@z[m]); err.append((y[i]-ww*z[i])**2)
        print(g,name,len(d),'w=%.2f corr %.2f'%(w,np.corrcoef(z,y)[0,1]),'rmse none %.3f LOO %.3f'%(np.sqrt((y**2).mean()),np.sqrt(np.mean(err))))
print('--- combined ---')
for g in G:
    d=[q for q in rows2 if q[1]==g]; a=np.array([q[2:] for q in d]); x19,x23,xB,xA=a.T
    y=x23-x19; z=((xB-xA)+(xB-x19))/2
    w=(z@y)/(z@z); err=[]
    for i in range(len(y)):
        m=np.arange(len(y))!=i; ww=(z[m]@y[m])/(z[m]@z[m]); err.append((y[i]-ww*z[i])**2)
    # resid after
    print(g,len(d),'w=%.2f corr %.2f'%(w,np.corrcoef(z,y)[0,1]),'rmse none %.3f LOO %.3f'%(np.sqrt((y**2).mean()),np.sqrt(np.mean(err))))
