from bt import *
import itertools,sys
BIG=['PP','PSOE','VOX','CS','IZQ']
def histof(A):
    i=TAGS.index(A); return np.mean([D[t]['S'] for t in TAGS[:i+1]],axis=0)
def run(par,lams=(0,0.6),trs=TRANS):
    out=[]
    for A,B,P in trs:
        h=histof(A)
        for lam in lams:
            X=predict(A,B,P,par,lam,hist=h); m=metrics(A,B,X); out.append((m['share'],m['seat_real']))
    return np.array(out)
def P(ga,de,th,only=None):
    return {g:(ga,de,th) for g in BIG if only is None or g in only}
if __name__=='__main__':
    base=run({}); print('base',base.mean(0))
    res=[]
    for ga in (0.6,0.7,0.8,0.9,1.0,1.1,1.2):
        for de in (-0.2,0,0.2,0.4):
            for th in (-0.2,0,0.2,0.4):
                r=run(P(ga,de,th)); res.append((r[:,0].mean(),r[:,1].mean(),ga,de,th))
    res.sort()
    for x in res[:12]: print('%.4f %.1f g=%.1f d=%.1f t=%.1f'%x)
