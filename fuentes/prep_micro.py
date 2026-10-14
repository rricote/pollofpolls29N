"""Estimaciones desde microdatos (CIS 3577, 40dB flash octubre, CEO 1169) para el poll of polls.
Variantes por encuesta:
  A = bruto: intención directa + simpatía entre quienes mencionan partido, pesos publicados.
  B = reponderado por recuerdo de voto 2023 (con ponderación suave por probabilidad de votar).
  C = B + imputación de los indecisos según su recuerdo de voto (a media intensidad).
"""
import pandas as pd, numpy as np, json, re, sys, warnings
warnings.filterwarnings('ignore')
W = '/tmp/claude-0/-home-claude/eea0bbaf-2db4-5718-a729-17707b9905cb/scratchpad/'
SIM = W + 'sim/'
UP = '/mnt/user-data/uploads/Simulador elecciones/Encuestas/'
KEYS = ['PP','PSOE','VOX','SUMAR','PODEMOS','SALF','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','OTROS','BLANCO']
MAIN = ['PP','PSOE','VOX','SUMAR','PODEMOS','SALF']

# ---------- resultados 2023 (provincia / CCAA) ----------
cm = {5:'PP',2:'PSOE',6:'VOX',10:'SUMAR',50:'ERC',57:'JUNTS',71:'BILDU',75:'PNV',65:'BNG',31:'CC',74:'UPN'}
v = pd.read_csv(SIM+'data/votos_mun_2023.csv', dtype={'id':str}); v['prov'] = v.id.str[:2]
v['p'] = v.cod_nac.map(cm).fillna('OTROS')
pv = pd.read_csv(SIM+'data/provincias.csv', dtype={'ccaa':str,'prov':str}).set_index('prov')
PROV2CCAA = {'01':'16','02':'08','03':'10','04':'01','05':'07','06':'11','07':'04','08':'09','09':'07','10':'11','11':'01','12':'10','13':'08','14':'01','15':'12','16':'08','17':'09','18':'01','19':'08','20':'16','21':'01','22':'02','23':'01','24':'07','25':'09','26':'17','27':'12','28':'13','29':'01','30':'14','31':'15','32':'12','33':'03','34':'07','35':'05','36':'12','37':'07','38':'05','39':'06','40':'07','41':'01','42':'07','43':'09','44':'02','45':'08','46':'10','47':'07','48':'16','49':'07','50':'02','51':'18','52':'19'}
pv['ccaa'] = pv.index.map(PROV2CCAA)
pt = v.pivot_table(index='prov', columns='p', values='votos', aggfunc='sum', fill_value=0)
for k in KEYS:
    if k not in pt: pt[k] = 0
pt['BLANCO'] = pv.blancos
pt = pt[KEYS]
pt['ccaa'] = pv.ccaa
pv['valid'] = pv.votos_cand + pv.blancos
pv['emit'] = pv.valid + pv.nulos
reg = pt.groupby('ccaa')[KEYS].sum()
regmeta = pv.groupby('ccaa')[['censo','blancos','nulos','emit','valid']].sum()
# recall targets (cuota del censo) por CCAA para el reponderado
def targets(rows):  # rows: ccaa list
    r = reg.loc[rows].sum(); m = regmeta.loc[rows].sum()
    t = {k: r[k]/m.censo for k in KEYS if k != 'BLANCO'}
    t['BN'] = (m.blancos + m.nulos)/m.censo
    t['ABST'] = 1 - m.emit/m.censo
    return t
b_reg = reg.div(reg.sum(axis=1), axis=0)      # cuotas 2023 sobre votos válidos por CCAA
b_nat = pt[KEYS].sum()/pt[KEYS].sum().sum()

# ---------- utilidades ----------
def kish(w): w = np.asarray(w, float); return (w.sum()**2/(w**2).sum()) if w.sum() > 0 else 0
def rake(df, region_col, wcol, rec_col, tgt_by_region, cap=(0.35, 3.0)):
    """Reponderación por recuerdo, dentro de cada región. Solo ajusta categorías de recuerdo conocidas."""
    out = df[wcol].copy().astype(float)
    for rg, idx in df.groupby(region_col).groups.items():
        sub = df.loc[idx]; t = tgt_by_region[rg]
        known = sub[rec_col].isin(list(t.keys()))
        if known.sum() < 5: continue
        tot = sub.loc[known, wcol].sum()
        tt = {k: t[k] for k in t}; ts = sum(tt.values()); tt = {k: x/ts for k, x in tt.items()}
        samp = sub.loc[known].groupby(rec_col)[wcol].sum()/tot
        f = {}
        for k in tt:
            s = samp.get(k, 0)
            f[k] = np.clip(tt[k]/s, *cap) if s > 0 else 1.0
        fac = sub.loc[known, rec_col].map(f)
        new = sub.loc[known, wcol]*fac
        new *= tot/new.sum()
        out.loc[new.index] = new
    return out

def shares(df, w, vote_col, unc_col=None, rec_col=None, impute=0.0, keys=KEYS):
    """cuota de voto válido por partido. df[vote_col] = clave de partido, 'UND' (indeciso imputable) o None (excluido)."""
    ww = pd.Series(w, index=df.index)
    dec = df[vote_col].isin(keys)
    s = ww[dec].groupby(df.loc[dec, vote_col]).sum().reindex(keys, fill_value=0.0)
    if impute > 0:
        und = df[vote_col] == 'UND'
        for r, idx in df[und].groupby(rec_col).groups.items():
            if r not in keys: continue
            ref = df[dec & (df[rec_col] == r)]
            if len(ref) < 15: continue
            rs = ww[ref.index].groupby(ref[vote_col]).sum()
            rs = rs/rs.sum()
            s = s.add(rs.reindex(keys, fill_value=0.0)*ww[idx].sum()*impute, fill_value=0)
    return s/s.sum(), kish(ww[dec])

# ---------- CIS 3577 ----------
cis = pd.read_csv(UP+'CIS 3577/3577_num.csv', sep=';', encoding='utf-8-sig', low_memory=False)
cis.columns = [c.split(':')[0] for c in cis.columns]
cis = cis.copy()
cis_party = {1:'PSOE',2:'PP',3:'VOX',21:'SUMAR',8:'PODEMOS',28:'SALF',901:'ERC',902:'JUNTS',1602:'BILDU',1601:'PNV',
             1201:'BNG',503:'CC',1501:'UPN',6:'OTROS',101:'OTROS',8995:'OTROS',8996:'BLANCO',29:'COAL'}
def cis_vote(r):
    a = r.INTENCIONGR
    if a in cis_party: return cis_party[a]
    if a in (9998, 9999):
        s = r.SIMPATIAR
        if s in cis_party: return cis_party[s]
        return 'UND'
    s = r.SIMPATIAR
    if a == 9997 and s in cis_party: return cis_party[s]   # ninguno de forma directa, simpatiza con partido
    return None
cis['vote'] = cis.apply(cis_vote, axis=1)
# coalición de izquierdas (29) -> reparto proporcional Sumar / Podemos
coal = cis.vote == 'COAL'
cis.loc[coal, 'vote'] = np.where(np.random.default_rng(1).random(coal.sum()) < 0.67, 'SUMAR', 'PODEMOS')
rec_map = {1:'PSOE',2:'PP',3:'VOX',21:'SUMAR',901:'ERC',902:'JUNTS',1602:'BILDU',1601:'PNV',1201:'BNG',503:'CC',1501:'UPN',
           6:'OTROS',8995:'OTROS',8996:'BN',9977:'BN',9997:'ABST'}
cis['rec'] = cis.RECUERDO.map(rec_map).fillna('NA')
cis['prop'] = cis.PROBVOTO.map(lambda x: 0.5 if x in (98, 99) else x/10)
cis['reg'] = cis.CCAA.astype(int).map(lambda x: f'{x:02d}')
cis['w0'] = cis.PESO.astype(str).str.replace(',','.').astype(float)
tg = {r: targets([r]) for r in reg.index}
cis['wB'] = rake(cis, 'reg', 'w0', 'rec', tg)
cis['wBp'] = cis.wB*cis.prop
cis['wAp'] = cis.w0

def micro_variants(df, wA, wB, vote_col='vote', rec_col='rec'):
    A, nA = shares(df, wA, vote_col)
    B, nB = shares(df, wB, vote_col)
    C, nC = shares(df, wB, vote_col, rec_col=rec_col, impute=0.5)
    return A, B, C, nA, nB, nC

A, B, C, nA, nB, nC = micro_variants(cis, cis.wAp, cis.wBp)
print('CIS A', (A*100).round(1).to_dict()); print('CIS B', (B*100).round(1).to_dict()); print('CIS C', (C*100).round(1).to_dict())
res = {'cis': {'id':'CIS 3577','n':int(len(cis)),'field':'2026-09-02','nA':nA,'nB':nB,
               'A':A.round(5).to_dict(),'B':B.round(5).to_dict(),'C':C.round(5).to_dict()}}

# regional shares (variant B) CIS
cis_reg = {}
for rg, sub in cis.groupby('reg'):
    s, ne = shares(sub, sub.wBp, 'vote')
    cis_reg[rg] = (s, ne, len(sub))

# transiciones (recuerdo -> voto, variante B) para tabla de fidelidad
dec = cis[cis.vote.isin(KEYS) & cis.rec.isin(['PP','PSOE','VOX','SUMAR','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN'])]
tr = (dec.groupby(['rec','vote']).wBp.sum().unstack(fill_value=0))
tr = tr.div(tr.sum(axis=1), axis=0)
res['cis']['trans'] = {r: tr.loc[r].round(4).to_dict() for r in tr.index}

# ---------- 40dB flash octubre ----------
d4 = pd.read_excel(UP+'2026_10_08_barometro_40db/03_Datos_octubre_2026_flash.xlsx')
def p4(x):
    x = str(x)
    pm = [('PSOE','PSOE'),('PP (','PP'),('Vox','VOX'),('Sumar','SUMAR'),('Podemos','PODEMOS'),('Se acabó','SALF'),('ERC','ERC'),
          ('JxCAT','JUNTS'),('EAJ','PNV'),('Bildu','BILDU'),('Coalición Canaria','CC'),('BNG','BNG'),('UPN','UPN'),
          ('CUP','OTROS'),('Adelante','OTROS'),('España Vaciada','OTROS'),('UPL','OTROS'),('Nueva Canarias','OTROS'),('Otro','OTROS'),
          ('Votaría en blanco','BLANCO')]
    for a, b in pm:
        if x.startswith(a) or (a == 'Bildu' and 'Bildu' in x): return b
    return None
def vote4(r, c1='p2', c2='p3'):
    a = p4(r[c1])
    if a: return a
    s = str(r[c1])
    if s.startswith('No lo sé') or s.startswith('Prefiero'):
        b = p4(r[c2]) if c2 else None
        if b and b != 'BLANCO': return b
        return 'UND'
    return None   # no votaría / nulo
d4['vote'] = d4.apply(vote4, axis=1)
def rec4(x):
    x = str(x); m = p4(x)
    if m in ('PP','PSOE','VOX','SUMAR','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN'): return m
    if m in ('OTROS','PODEMOS'): return 'OTROS' if m == 'OTROS' else 'SUMAR'
    if x.startswith('Voté en blanco') or x.startswith('Voté nulo'): return 'BN'
    if x.startswith('No voté'): return 'ABST'
    return 'NA'
d4['rec'] = d4.p9.map(rec4)
d4['prop'] = d4.p1.map(lambda x: 0.5 if str(x).startswith('No lo') else float(re.match(r'\d+', str(x)).group())/10)
ccaa_names = {'Andalucía':'01','Aragón':'02','Asturias, Principado de':'03','Balears, Illes':'04','Canarias':'05','Cantabria':'06',
              'Castilla y León':'07','Castilla - La Mancha':'08','Cataluña':'09','Comunitat Valenciana':'10','Extremadura':'11',
              'Galicia':'12','Madrid, Comunidad de':'13','Murcia, Región de':'14','Navarra, Comunidad Foral de':'15',
              'País Vasco':'16','Rioja, La':'17'}
d4['reg'] = d4.ccaa.map(ccaa_names)
assert d4.reg.notna().all()
d4['w0'] = d4.ponde.astype(float)
# En 40dB no hay Ceuta/Melilla; reponderamos con objetivos de las 17 CCAA
d4['wB'] = rake(d4, 'reg', 'w0', 'rec', tg)
d4['wBp'] = d4.wB*d4.prop
d4['wAp'] = d4.w0
A4, B4, C4, nA4, nB4, nC4 = micro_variants(d4, d4.wAp, d4.wBp)
print('40dB A', (A4*100).round(1).to_dict()); print('40dB B', (B4*100).round(1).to_dict()); print('40dB C', (C4*100).round(1).to_dict())
res['d40'] = {'id':'40dB flash (microdatos)','n':int(len(d4)),'field':'2026-10-08','nA':nA4,'nB':nB4,
              'A':A4.round(5).to_dict(),'B':B4.round(5).to_dict(),'C':C4.round(5).to_dict()}
# escenario unitario (p5/p6)
def vote5(r):
    a = str(r['p5'])
    if a.startswith('Sumar/Frente Amplio + Podemos'): return 'SUMAR'
    return vote4(r, 'p5', 'p6')
d4['vote_u'] = d4.apply(vote5, axis=1)
Bu, _ = shares(d4, d4.wBp, 'vote_u')
res['d40']['B_unitaria'] = Bu.round(5).to_dict()
Au, _ = shares(d4, d4.wAp, 'vote_u')
res['d40']['A_unitaria'] = Au.round(5).to_dict()
print('40dB unitaria B', (Bu*100).round(1).to_dict())
res['d40']['bonus_unidad'] = float(Bu['SUMAR']/(B4['SUMAR']+B4['PODEMOS']))
print('bonus unidad', res['d40']['bonus_unidad'])
tr4 = (d4[d4.vote.isin(KEYS) & d4.rec.isin(['PP','PSOE','VOX','SUMAR','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN'])]
       .groupby(['rec','vote']).wBp.sum().unstack(fill_value=0))
tr4 = tr4.div(tr4.sum(axis=1), axis=0)
res['d40']['trans'] = {r: tr4.loc[r].round(4).to_dict() for r in tr4.index}

# ---------- CEO 1169 (Cataluña) ----------
ce = pd.read_csv(UP+'ceo_1169/REO1169_microdades_anonimitzades.csv', sep=';', encoding='latin-1', low_memory=False)
cv = {'PSC/PSOE':'PSOE','PP':'PP','VOX':'VOX','Sumar - En Comú Podem':'SUMAR','Podemos':'PODEMOS','ERC':'ERC','Junts per Catalunya':'JUNTS',
      'CUP':'OTROS','PACMA':'OTROS','Ciutadans/Ciudadanos':'OTROS','Aliança catalana':'OTROS','Altres partits':'OTROS','En blanc':'BLANCO'}
def vce(x):
    x = str(x).strip()
    if x in cv: return cv[x]
    if x in ('No ho sap', 'No contesta'): return 'UND'
    return None
ce['vote'] = ce.INT_CONGRES_VOT.map(vce)
rc = {'PSC-PSOE':'PSOE','PP':'PP','VOX':'VOX','Sumar - En Comú Podem':'SUMAR','ERC':'ERC','Junts per Catalunya':'JUNTS','CUP':'OTROS',
      'Altres':'OTROS','En blanc':'BN','Nul':'BN','No va votar':'ABST'}
ce['rec'] = ce.REC_CONGRES_VOT_CENS_R.map(rc).fillna('NA')
pm = {'Segur que aniré a votar':1.0,'Probablement aniré a votar':0.75,'Probablement no aniré a votar':0.25,'Segur que no no aniré a votar':0.0}
ce['prop'] = ce.INT_CONGRES_PART_1_4.map(pm).fillna(0.5)
ce['reg'] = '09'; ce['w0'] = ce.PONDERA.astype(float)
ce['wB'] = rake(ce, 'reg', 'w0', 'rec', {'09': tg['09']})
ce['wBp'] = ce.wB*ce.prop
Ac, Bc, Cc, nAc, nBc, nCc = micro_variants(ce, ce.w0*ce.prop, ce.wBp)
print('CEO A', (Ac*100).round(1).to_dict()); print('CEO B', (Bc*100).round(1).to_dict()); print('CEO C', (Cc*100).round(1).to_dict())
print('2023 Cat', (b_reg.loc['09']*100).round(1).to_dict())
res['ceo'] = {'id':'CEO 1169 (Cataluña)','n':int(len(ce)),'field':'2026-09-16','nA':nAc,'nB':nBc,
              'A':Ac.round(5).to_dict(),'B':Bc.round(5).to_dict(),'C':Cc.round(5).to_dict()}

# ---------- factores regionales (swing relativo respecto al nacional) ----------
# Referencia nacional: media de CIS y 40dB (variante B) para que el sesgo general de cada encuesta no se confunda con efecto regional.
nat_ref = (B*nB + B4*nB4)/(nB + nB4)
TAU = 0.18
def lnf(s_reg, ne, b_c, b_n, s_n, p):
    s = max(s_reg[p], 1e-4)
    est = np.log(s/b_c[p]) - np.log(s_n[p]/b_n[p])
    se = np.sqrt((1-s)/(s*max(ne, 1)))
    return est, se
regions = sorted(reg.index)
fac = {}
for rg in regions:
    row = {}
    s_c, ne, n = cis_reg[rg]
    for p in KEYS:
        if p in ('PODEMOS', 'SALF', 'BLANCO', 'OTROS') or b_reg.loc[rg, p] < 0.02:
            continue
        # CIS (referencia: su propio nacional)
        e1, se1 = lnf(s_c, ne, b_reg.loc[rg], b_nat, B, p)
        ests = [(e1, se1)]
        if rg == '09':       # añade CEO (referencia: nacional medio de CIS/40dB)
            e2, se2 = lnf(Bc, nBc, b_reg.loc[rg], b_nat, nat_ref, p)
            ests.append((e2, se2))
        wsum = sum(1/se**2 for e, se in ests); e = sum(e/se**2 for e, se in ests)/wsum; se = np.sqrt(1/wsum)
        w = TAU**2/(TAU**2 + se**2)
        row[p] = {'raw': round(float(e), 4), 'se': round(float(se), 4), 'f': round(float(np.exp(w*e)), 4), 'sd': round(float(np.sqrt(1/(1/TAU**2 + 1/se**2))), 4)}
    fac[rg] = row
res['factores_regionales'] = fac
res['tau'] = TAU
res['n_reg'] = {rg: [int(cis_reg[rg][2]), round(float(cis_reg[rg][1]), 1)] for rg in regions}
res['b_nat'] = b_nat.round(5).to_dict()
res['b_reg'] = {rg: b_reg.loc[rg].round(5).to_dict() for rg in regions}
# provincias: base 2023, votos válidos, ccaa
prov_out = {}
for p in pt.index:
    row = pt.loc[p, KEYS].astype(float); tot = row.sum()
    prov_out[p] = {'sh': (row/tot).round(5).tolist(), 'valid': int(tot), 'ccaa': pv.loc[p, 'ccaa']}
res['prov'] = prov_out
res['keys'] = KEYS
json.dump(res, open(W+'work/micro.json', 'w'), ensure_ascii=False)
print('regional factors CIS+CEO Catalonia:', json.dumps(fac['09']))
print({rg: {p: x['f'] for p, x in r.items() if p in ('PP','PSOE','VOX','SUMAR')} for rg, r in fac.items()})
