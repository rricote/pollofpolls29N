import json,re,glob,os
R='/mnt/user-data/uploads/Simulador elecciones/Web autonomicas/data/'
def js(p):
    s=open(p,encoding='utf-8').read()
    i=s.index(']={')+2
    return json.loads(s[i:].rstrip().rstrip(';'))
def load():
    out={}
    for reg in sorted(os.listdir(R)):
        d=R+reg
        if not os.path.isdir(d): continue
        parties=[p[0] for p in js(d+'/parties.json.js')['parties']]
        for f in sorted(glob.glob(d+'/20*.json.js')):
            if f.endswith('parties.json.js'): continue
            e=os.path.basename(f)[:10]
            if e<'2019': continue
            j=js(f)
            out[(reg,e)]={'parties':parties,'tot':j['tot'],'v':j['v'],'s':j.get('s',{}),'prov':j.get('prov',[])}
    return out
if __name__=='__main__':
    o=load()
    for k,v in o.items():
        pn=sorted(((vv,v['parties'][int(i)]) for i,vv in v['v'].items()),reverse=True)[:9]
        print(k,len(v['prov']),[(n,round(x/sum(v['v'].values())*100,1)) for x,n in pn])
