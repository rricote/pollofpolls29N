import re,json,collections
from load import *
def grp(sig,tag):
    s=sig.upper()
    if re.match(r'^(P\.?P\.?($|[-\s])|PP-|UPN-PP)',s) or s in('PP','P.P.'): return 'PP'
    if re.match(r'^(PSC|PSOE|P\.S\.O\.E|PSE-EE|PSDEG|PSIB|PSN|PSOE-NCA)',s): return 'PSOE'
    if s.startswith('VOX'): return 'VOX'
    if s in("C'S","C´S","CS") or s.startswith("C'S"): return 'CS'
    if s.startswith('UPYD'): return 'UPYD'
    if re.match(r'^(PODEMOS|EN COMÚ|ECP|EUPV|IU|I\.U\.|IUC|IULV|CHA-IU|EU-V|EUIB|ICV|MÉS|MES |SUMAR|MÁS PAÍS|M PAÍS|COMPROMÍS|COMPROMIS|EQUO|PSM-IV|SSP|EB$|ALIANZA VERDE)',s) or s=='EB' or 'EQUO' in s: return 'IZQ'
    if re.match(r'^(ERC|ESQUERRA|ERPV)',s): return 'ERC'
    if re.match(r'^(CIU|CDC|DL$|JXCAT|PDECAT|JUNTS)',s): return 'JUNTS'
    if re.match(r'^(AMAIUR|EH BILDU|BILDU)',s): return 'BILDU'
    if re.match(r'^(E\.?A\.?J|EAJ)',s): return 'PNV'
    if re.match(r'^(B\.N\.G|BNG|NÓS)',s): return 'BNG'
    if re.match(r'^(CC|CCA|NC-CCA|NC-BC)',s): return 'CC'
    if re.match(r'^(NA\+|U\.P\.N)',s): return 'UPN'
    return 'OTROS'
out={}
for tag in ['201111','201512','201606','201904','201911','202307']:
    c,m,v,s=election(tag)
    provs=sorted(p for p in v if p[2:]!='99')
    E=[]
    for p in provs:
        raw=m[p]['raw']; blank=int(raw[125:133]); seats=int(raw[149:155]); cv=int(raw[141:149])
        vt=collections.Counter(); st=collections.Counter()
        for k,x in v[p].items():
            g=grp(c[k]['sig'],tag); vt[g]+=x; st[g]+=s[p][k]
        vt['BLANCO']=blank
        E.append(dict(id=p[2:],ccaa=p[:2],name=m[p]['name'],seats=seats,valid=cv+blank,votes=dict(vt),sw=dict(st)))
    out[tag]=E
    tot=collections.Counter(); ts=collections.Counter()
    for e in E:
        for g,x in e['votes'].items(): tot[g]+=x
        for g,x in e['sw'].items(): ts[g]+=x
    T=sum(tot.values()); print(tag,sum(e['seats'] for e in E),{g:(round(100*x/T,1),ts[g]) for g,x in tot.most_common()})
json.dump(out,open('hist.json','w'))
