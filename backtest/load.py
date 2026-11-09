import collections
def rd(p): return [l for l in open(p,encoding='latin-1').read().split('\n') if l.strip()]
def election(tag):
    yymm=tag[2:]; d=f'02{tag}_MESA'
    cands={}
    for l in rd(f'{d}/0302{yymm}.DAT'):
        cands[l[8:14]]=dict(sig=l[14:64].strip(),name=l[64:214].strip(),c_prov=l[214:220],c_aut=l[220:226],c_nat=l[226:232])
    meta={}
    for l in rd(f'{d}/0702{yymm}.DAT'):
        p=l[9:11]+l[11:13]
        meta[p]=dict(name=l[14:64].strip(),raw=l)
    votes=collections.defaultdict(dict); seats=collections.defaultdict(dict)
    for l in rd(f'{d}/0802{yymm}.DAT'):
        p=l[9:11]+l[11:13]; votes[p][l[14:20]]=int(l[20:28]); seats[p][l[14:20]]=int(l[28:33])
    return cands,meta,votes,seats
