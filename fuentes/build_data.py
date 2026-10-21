import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, HERE)
import polls_build
W = HERE + '../'            # carpeta con data.json base (partidos, grupos, escaños 2023)
D = json.load(open(HERE + 'base.json')) if os.path.exists(HERE + 'base.json') else json.load(open(W + 'data.json'))
M = json.load(open(HERE + 'micro.json'))
OLD = M['keys']                       # 16 claves del preprocesado: ..., UPN, ADELANTE, OTROS, BLANCO
KEYS = OLD[:14] + ['COMPROMIS', 'UPC'] + OLD[14:]   # nueva configuración de candidaturas (18)
assert KEYS[13] == 'ADELANTE' and KEYS[-2:] == ['OTROS', 'BLANCO'] and len(KEYS) == 18
def ex(arr):                          # inserta COMPROMIS y UPC (0) antes de OTROS
    a = list(arr); return a[:14] + [0.0, 0.0] + a[14:]
def exd(d):                           # dict por clave -> lista en el orden nuevo
    return [d.get(k, 0.0) for k in KEYS]

REGN = {'01':'Andalucía','02':'Aragón','03':'Asturias','04':'Illes Balears','05':'Canarias','06':'Cantabria','07':'Castilla y León',
        '08':'Castilla-La Mancha','09':'Cataluña','10':'Comunitat Valenciana','11':'Extremadura','12':'Galicia','13':'Madrid',
        '14':'Murcia','15':'Navarra','16':'País Vasco','17':'La Rioja','18':'Ceuta','19':'Melilla'}
prov = []
for p in D['prov']:
    mp = M['prov'][p['id']]
    prov.append({'id': p['id'], 'name': p['name'], 'seats': p['seats'], 'ccaa': mp['ccaa'], 'valid': mp['valid'], 'sh': ex(mp['sh'])})
# Adelante Andalucía concurrió en 2023 solo en Cádiz (9.064 votos, 1,42 %), por separado de Sumar; antes iba en 'otros'
ADEL23 = 0.0142
for p in prov:
    if p['id'] == '11':
        p['sh'][KEYS.index('ADELANTE')] = ADEL23; p['sh'][KEYS.index('OTROS')] -= ADEL23
assert sum(p['seats'] for p in prov) == 350

def micro(k):
    m = M[k]; o = {'id': m['id'], 'n': m['n'], 'field': m['field'], 'nA': round(m['nA'], 1), 'nB': round(m['nB'], 1),
                   'A': exd(m['A']), 'B': exd(m['B']), 'C': exd(m['C'])}
    for e in ('B_unitaria', 'A_unitaria'):
        if e in m: o[e] = exd(m[e])
    if 'bonus_unidad' in m: o['bonus'] = round(m['bonus_unidad'], 3)
    if 'trans' in m: o['trans'] = m['trans']
    return o

fac = {rg: {p: {'f': x['f'], 'sd': x['sd'], 'raw': x['raw'], 'se': x['se']} for p, x in r.items()} for rg, r in M['factores_regionales'].items()}

# --- nueva configuración de candidaturas ---
# Reparto regional del voto de Podemos: media de CIS/40dB encogida hacia el reparto del voto Sumar 2023 (la muestra de Podemos por comunidad es corta)
sum23 = {}
tot = sum(M['b_reg'][rg]['SUMAR'] * sum(p['valid'] for p in prov if p['ccaa'] == rg) for rg in REGN)
for rg in REGN: sum23[rg] = M['b_reg'][rg]['SUMAR'] * sum(p['valid'] for p in prov if p['ccaa'] == rg) / tot
SHR = 0.5
fpod = {rg: round(SHR * M['loc']['PODEMOS'][rg] + (1 - SHR) * sum23[rg], 5) for rg in REGN}
KC = 0.85                             # parte del espacio ex-Sumar de la Comunitat Valenciana que va en Compromís-Front Valencià
cfg = {
  'fPod': {'cat': fpod['09'], 'cv': fpod['10'], 'can': fpod['05']},   # Podemos integrado en ERC, Compromís y Unidad del Pueblo Canario
  'wFA': {'cv': round(sum23['10'] * KC, 5), 'can': round(sum23['05'], 5)},  # parte del voto FA(ex-Sumar) que pasa a Compromís y a UPC
  'kc': KC,
  'regPodemosCoal': ['09', '10', '05'],
  'andAdelante': round((M['adelante_and']['cis'] * M['adelante_and']['n_cis'] + M['adelante_and']['d40'] * M['adelante_and']['n_d40']) / (M['adelante_and']['n_cis'] + M['adelante_and']['n_d40']), 5),
  'locPodemos': M['loc']['PODEMOS'], 'locPodemosCIS': M['loc']['PODEMOS_cis'], 'locPodemos40': M['loc']['PODEMOS_d40'], 'sumar23': {k: round(v, 5) for k, v in sum23.items()},
  'shr': SHR,
}

parties = [
 {'k': 'PP', 'name': 'PP', 'color': '#1d84ce'}, {'k': 'PSOE', 'name': 'PSOE', 'color': '#e30613'}, {'k': 'VOX', 'name': 'Vox', 'color': '#5bb85d'},
 {'k': 'SUMAR', 'name': 'Frente Amplio', 'color': '#e6007e'}, {'k': 'PODEMOS', 'name': 'Podemos', 'color': '#7b3f98'},
 {'k': 'SALF', 'name': 'Se Acabó la Fiesta', 'color': '#d4a017'}, {'k': 'ERC', 'name': 'ERC', 'color': '#f7a600'},
 {'k': 'JUNTS', 'name': 'Junts', 'color': '#00c3b2'}, {'k': 'BILDU', 'name': 'EH Bildu', 'color': '#b5cf18'}, {'k': 'PNV', 'name': 'PNV', 'color': '#008c45'},
 {'k': 'BNG', 'name': 'BNG', 'color': '#6fb5e0'}, {'k': 'CC', 'name': 'CC', 'color': '#f4c20d'}, {'k': 'UPN', 'name': 'UPN', 'color': '#a02c2c'},
 {'k': 'ADELANTE', 'name': 'Adelante Andalucía', 'color': '#1f9d55'}, {'k': 'COMPROMIS', 'name': 'Compromís-Front Valencià', 'color': '#e4572e'},
 {'k': 'UPC', 'name': 'Unidad del Pueblo Canario', 'color': '#2a6f97'}, {'k': 'OTROS', 'name': 'Otros', 'color': '#8c8c8c'}]
LEFT = ['PSOE', 'SUMAR', 'PODEMOS', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'ADELANTE', 'COMPROMIS', 'UPC']
LEFT_SJ = [k for k in LEFT if k != 'JUNTS']
grupos = [
 {'id': 'pp', 'label': 'PP', 'parties': ['PP']}, {'id': 'pp_vox', 'label': 'PP + Vox', 'parties': ['PP', 'VOX']},
 {'id': 'pp_vox_der', 'label': 'PP + Vox + derecha', 'parties': ['PP', 'VOX', 'UPN', 'CC', 'SALF']},
 {'id': 'pp_vox_der_j', 'label': 'PP + Vox + derecha + Junts', 'parties': ['PP', 'VOX', 'UPN', 'CC', 'SALF', 'JUNTS']},
 {'id': 'psoe_socios', 'label': 'PSOE + Frente Amplio + socios de investidura', 'parties': LEFT},
 {'id': 'psoe_socios_sj', 'label': 'PSOE + Frente Amplio + socios sin Junts', 'parties': LEFT_SJ},
 {'id': 'psoe_sumar', 'label': 'PSOE + Frente Amplio', 'parties': ['PSOE', 'SUMAR']}, {'id': 'psoe', 'label': 'Solo PSOE', 'parties': ['PSOE']}]

nat23 = exd(M['b_nat']); _v = sum(p['valid'] for p in prov); _c = next(p['valid'] for p in prov if p['id'] == '11')
_x = ADEL23 * _c / _v; nat23[KEYS.index('ADELANTE')] += _x; nat23[KEYS.index('OTROS')] -= _x
s23 = D['base']['seats']; seats2023 = s23[:13] + [0, 0, 0] + s23[13:]
out = {
 'keys': KEYS, 'parties': parties, 'prov': prov, 'seats2023': seats2023,
 'nat2023': nat23, 'regn': REGN, 'fac': fac, 'tau': M['tau'], 'nreg': M['n_reg'],
 'micro': {'cis': micro('cis'), 'd40': micro('d40'), 'ceo': micro('ceo')},
 'grupos': grupos, 'cfg': cfg, 'polls': polls_build.polls,
 'cat2023': exd(M['b_reg']['09']),
 'ver': '3',
}
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open(HERE + 'data.js', 'w', encoding='utf-8').write('const D=' + s + ';\n')
open(HERE + 'data_v2.json', 'w', encoding='utf-8').write(s)
print(len(s), cfg['fPod'], cfg['wFA'], cfg['andAdelante'])
