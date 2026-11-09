import json,numpy as np,itertools
H=json.load(open('hist.json'))
G=['PP','PSOE','VOX','CS','UPYD','IZQ','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','OTROS','BLANCO']
GI={g:i for i,g in enumerate(G)}
TAGS=['201111','201512','201606','201904','201911','202307']
def mat(tag):
    E=H[tag]; S=np.zeros((52,len(G))); SW=np.zeros((52,len(G))); w=np.zeros(52); seats=np.zeros(52,int); cc=[];ids=[]
    for i,e in enumerate(E):
        v=np.array([e['votes'].get(g,0) for g in G],float); S[i]=v/v.sum(); w[i]=e['valid']; seats[i]=e['seats']
        SW[i]=[e['sw'].get(g,0) for g in G]; cc.append(e['ccaa']); ids.append(e['id'])
    return dict(S=S,SW=SW,w=w,seats=seats,cc=np.array(cc),ids=ids)
D={t:mat(t) for t in TAGS}
assert all(D[t]['ids']==D['202307']['ids'] for t in TAGS)
CC=D['202307']['cc']; regs=sorted(set(CC))
def dhondt(S,seats,thr=0.03):
    out=np.zeros_like(S)
    for p in range(S.shape[0]):
        s=S[p].copy(); s[GI['BLANCO']]=S[p][GI['BLANCO']]
        ok=(s>=thr); ok[GI['BLANCO']]=False
        q=[]
        for g in range(len(G)):
            if ok[g]:
                for d in range(1,seats[p]+1): q.append((s[g]/d,g))
        q.sort(reverse=True)
        for _,g in q[:seats[p]]: out[p,g]+=1
    return out
def rake(base,w,target,iters=60):
    X=base.copy()
    for _ in range(iters):
        nat=(X*w[:,None]).sum(0)/w.sum()
        f=np.where(nat>0,target/np.maximum(nat,1e-12),1.0); X=X*f[None,:]
        X=X/X.sum(1,keepdims=True)
    return X
def regional(X,w,trueS,wB,lam,iters=8):
    if lam==0: return X
    tg={}
    for r in regs:
        m=CC==r; ww=wB[m]
        pred=(X[m]*ww[:,None]).sum(0)/ww.sum(); tru=(trueS[m]*ww[:,None]).sum(0)/ww.sum()
        tg[r]=lam*tru+(1-lam)*pred
    for _ in range(iters):
        for r in regs:
            m=CC==r; ww=wB[m]
            pred=(X[m]*ww[:,None]).sum(0)/ww.sum()
            f=np.where(pred>0,tg[r]/np.maximum(pred,1e-12),1.0); X[m]=X[m]*f[None,:]
        X=X/X.sum(1,keepdims=True)
    return X
def predict(A,B,prev,par,lam,hist=None):
    """par: dict g->(gamma,delta,theta)"""
    SA=D[A]['S'];SB=D[B]['S'];eps=1e-4
    base=np.zeros_like(SA)
    for g,i in GI.items():
        ga,de,th=par.get(g,(1.0,0.0,0.0)) if not isinstance(par,tuple) else par
        la=np.log(np.maximum(SA[:,i],eps))
        tr=(la-np.log(np.maximum(D[prev]['S'][:,i],eps))) if prev else 0*la
        hl=0*la
        if hist is not None and th!=0:
            hl=np.log(np.maximum(hist[:,i],eps))-la
        base[:,i]=np.where(SA[:,i]>0,np.exp(ga*la+de*tr+th*hl),0)
    # nacional verdadero de B (ponderado por voto de A como el modelo)
    w=D[A]['w']; wB=D[B]['w']
    target=(SB*wB[:,None]).sum(0)/wB.sum()
    # partidos sin base en A pero con voto en B: se reparte plano para no perderlo
    for i in range(len(G)):
        if base[:,i].sum()==0 and target[i]>0: base[:,i]=1.0
    X=base/base.sum(1,keepdims=True)
    X=rake(X,w,target)
    X=regional(X,w,SB,wB,lam)
    X=rake(X,w,target,20)
    return X
def metrics(A,B,X,main=('PP','PSOE','VOX','CS','IZQ')):
    SB=D[B]['S'];wB=D[B]['w']
    err={g:(np.abs(X[:,GI[g]]-SB[:,GI[g]])*wB).sum()/wB.sum() for g in G}
    # error medio ponderado por el peso nacional de cada partido
    nat=(SB*wB[:,None]).sum(0)/wB.sum()
    sc=sum(err[g]*nat[GI[g]] for g in main if nat[GI[g]]>0.03)/sum(nat[GI[g]] for g in main if nat[GI[g]]>0.03)
    pred=dhondt(X,D[B]['seats']); act=D[B]['SW']; orc=dhondt(SB,D[B]['seats'])
    seat_prov=np.abs(pred-orc).sum()/2          # escaños mal asignados respecto al D'Hondt de los datos reales
    seat_real=np.abs(pred-act).sum()/2
    nat_seat=np.abs(pred.sum(0)-act.sum(0)).sum()/2
    return dict(share=sc,err=err,seat_prov=seat_prov,seat_real=seat_real,floor=np.abs(orc-act).sum()/2,nat_seat=nat_seat,pred=pred.sum(0),act=act.sum(0))
TRANS=[('201512','201606','201111'),('201606','201904','201512'),('201904','201911','201606'),('201911','202307','201904'),('201606','201911','201512'),('201512','201904','201111')]
