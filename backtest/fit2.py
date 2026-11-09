from fit import *
FE=['PP','PSOE','VOX','CS','IZQ']
CONS=[('201512','201606'),('201606','201904'),('201904','201911'),('201911','202307')]
def feats(A,own):
    S=D[A]['S'];w=D[A]['w']
    cols=[np.log(np.maximum(S[:,GI[own]],1e-4))]+[S[:,GI[f]] for f in FE if f!=own]
    X=np.stack(cols,1); mu=(X*w[:,None]).sum(0)/w.sum(); return X-mu
def design(g,trs):
    Xs=[];ys=[];ws=[]
    for A,B in trs:
        SA=D[A]['S'][:,GI[g]];SB=D[B]['S'][:,GI[g]]
        if (SA*D[A]['w']).sum()/D[A]['w'].sum()<0.02 or (SB*D[B]['w']).sum()/D[B]['w'].sum()<0.02: continue
        m=(SA>0.005)&(SB>0.005)
        y=np.log(SB[m]/SA[m]); w=D[A]['w'][m]; y=y-(y*w).sum()/w.sum()
        X=feats(A,g)[m]; X=X-(X*w[:,None]).sum(0)/w.sum()
        Xs.append(X);ys.append(y);ws.append(w/w.sum())
    if not Xs: return None
    return np.vstack(Xs),np.concatenate(ys),np.concatenate(ws)
def fitridge(trs,lam,parties=BIG,cols=None):
    beta={}
    for g in parties:
        d=design(g,trs)
        if d is None: continue
        X,y,w=d
        if cols is not None: X=X[:,cols]
        A_=X.T@(X*w[:,None])+lam*np.eye(X.shape[1])*w.sum(); b=np.linalg.solve(A_,X.T@(y*w))
        beta[g]=b
    return beta
def predict_lin(A,B,beta,lamreg,cols=None):
    SA=D[A]['S'];SB=D[B]['S'];w=D[A]['w'];wB=D[B]['w']
    base=SA.copy()
    for g,b in beta.items():
        X=feats(A,g); X=X if cols is None else X[:,cols]
        base[:,GI[g]]=SA[:,GI[g]]*np.exp(X@b)
    target=(SB*wB[:,None]).sum(0)/wB.sum()
    for i in range(len(G)):
        if base[:,i].sum()==0 and target[i]>0: base[:,i]=1.0
    X=rake(base/base.sum(1,keepdims=True),w,target); X=regional(X,w,SB,wB,lamreg); return rake(X,w,target,20)
if __name__=='__main__':
    for lamR in (0,0.6):
        base=[];
        for A,B in CONS+[('201606','201911'),('201512','201904')]:
            X=predict(A,B,None,(1,0,0),lamR); m=metrics(A,B,X); base.append((m['share'],m['seat_real']))
        print('lamR',lamR,'base',np.round(np.array(base).mean(0),4))
        for rl in (0.001,0.01,0.05,0.2,1.0):
            r=[]
            for i,(A,B) in enumerate(CONS+[('201606','201911'),('201512','201904')]):
                train=[t for t in CONS if t!=(A,B) and not (i>=4 and False)]
                if i>=4: train=[t for t in CONS if not (t[0]>=A and t[1]<=B)]  # sin episodios solapados
                beta=fitridge(train,rl)
                X=predict_lin(A,B,beta,lamR); m=metrics(A,B,X); r.append((m['share'],m['seat_real']))
            print('  ridge',rl,np.round(np.array(r).mean(0),4),[round(x[0],4) for x in r])
