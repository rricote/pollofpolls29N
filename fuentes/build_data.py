import json
W = '/tmp/claude-0/-home-claude/eea0bbaf-2db4-5718-a729-17707b9905cb/scratchpad/'
D = json.load(open(W+'data.json'))
M = json.load(open(W+'work/micro.json'))
KEYS = M['keys']

REGN = {'01':'Andalucía','02':'Aragón','03':'Asturias','04':'Illes Balears','05':'Canarias','06':'Cantabria','07':'Castilla y León',
        '08':'Castilla-La Mancha','09':'Cataluña','10':'Comunitat Valenciana','11':'Extremadura','12':'Galicia','13':'Madrid',
        '14':'Murcia','15':'Navarra','16':'País Vasco','17':'La Rioja','18':'Ceuta','19':'Melilla'}
prov = []
for p in D['prov']:
    mp = M['prov'][p['id']]
    prov.append({'id': p['id'], 'name': p['name'], 'seats': p['seats'], 'ccaa': mp['ccaa'], 'valid': mp['valid'], 'sh': mp['sh']})
assert sum(p['seats'] for p in prov) == 350

def micro(k):
    m = M[k]; o = {'id': m['id'], 'n': m['n'], 'field': m['field'], 'nA': round(m['nA'], 1), 'nB': round(m['nB'], 1),
                   'A': [m['A'][x] for x in KEYS], 'B': [m['B'][x] for x in KEYS], 'C': [m['C'][x] for x in KEYS]}
    for e in ('B_unitaria', 'A_unitaria'):
        if e in m: o[e] = [m[e][x] for x in KEYS]
    if 'bonus_unidad' in m: o['bonus'] = round(m['bonus_unidad'], 3)
    if 'trans' in m: o['trans'] = m['trans']
    return o

fac = {rg: {p: {'f': x['f'], 'sd': x['sd'], 'raw': x['raw'], 'se': x['se']} for p, x in r.items()} for rg, r in M['factores_regionales'].items()}

# Encuestas publicadas (porcentajes). Fuente de la tabla: agregadores de encuestas 29N (Brújula 29N, elecciones29noviembre.com) y prensa; ver 'note'.
def P(i, name, date, n, pp, psoe, vox, sumar, podemos, salf=None, q=1.0, inc=True, note=''):
    v = {'PP': pp, 'PSOE': psoe, 'VOX': vox, 'SUMAR': sumar, 'PODEMOS': podemos}
    if salf is not None: v['SALF'] = salf
    return {'id': i, 'name': name, 'date': date, 'n': n, 'v': v, 'q': q, 'include': inc, 'src': 'pub', 'note': note}
polls = [
 P('sm1011', 'SocioMétrica / El Español', '2026-10-11', 1000, 32.6, 26.2, 18.8, 4.9, 2.8, note='Fecha según agregador; campo no confirmado'),
 P('tp1009', 'Target Point / El Debate', '2026-10-09', 1002, 32.0, 25.9, 18.7, 6.9, 3.4),
 P('invy1009', 'InvyMark / laSexta', '2026-10-09', 1200, 32.8, 28.0, 18.8, 6.3, 3.2, q=0.6, note='Una sola fuente; muestra y campo sin confirmar'),
 P('gad1008', 'GAD3 / ABC', '2026-10-08', 1077, 31.4, 26.4, 18.2, 7.4, 2.3, note='Una sola fuente (agregador)'),
 P('ges1008', 'GESOP / El Periódico', '2026-10-08', 1000, 28.7, 26.1, 18.9, 8.0, 2.6, q=0.6, note='Mezcla escenarios (Sumar en escenario Frente Amplio, Podemos por separado); PP según agregador'),
 P('ham1008', 'Hamalgama Métrica / Vozpópuli', '2026-10-08', 1000, 33.4, 25.3, 19.6, 5.4, 3.3),
 P('d401008', '40dB / El País-SER (publicada)', '2026-10-08', 800, 31.9, 28.1, 18.9, 5.3, 2.3, salf=1.8, inc=False, note='Sustituida por el cálculo desde los microdatos de la misma encuesta; actívala para usar el dato publicado'),
 P('dym1007', 'DYM / 20minutos', '2026-10-07', 1011, 34.0, 28.2, 18.2, 3.6, 2.6, note='Podemos 2,6 (Brújula) o 3,6 (otro agregador)'),
 P('imop1007', 'IMOP Insights / El Confidencial', '2026-10-07', 900, 30.4, 26.5, 19.0, 7.6, 2.3),
 P('nc1006', 'NC Report / La Razón', '2026-10-06', 1000, 34.1, 25.0, 18.2, 5.3, 3.9),
 P('em1003', 'EM-Analytics / Electomanía', '2026-10-03', 8171, 31.3, 26.9, 19.4, 5.2, 3.4, note='Sumar 5,2 (Brújula) o 6,3 (otro agregador)'),
 P('sm1003', 'SocioMétrica / El Español', '2026-10-03', 1000, 33.4, 26.5, 18.1, 5.3, 3.1),
 P('d101002', 'Data10 / OKDiario', '2026-10-02', 1000, 34.0, 26.1, 18.6, 5.2, 4.3),
 P('sig1001', 'Sigma Dos / El Mundo', '2026-10-01', 2116, 32.6, 25.6, 18.3, 6.6, 3.3, note='Campo 22 sep-1 oct'),
 P('win1001', 'Winston / Artículo14', '2026-10-01', 1201, 31.3, 24.9, 19.1, 6.8, 3.9),
 P('ate1001', 'Ateneo del Dato / elDiario.es', '2026-10-01', 1500, 33.2, 27.5, 19.2, 7.0, 3.3),
 P('sig1011', 'Sigma Dos / El Mundo (11-oct)', '2026-10-11', 1500, 31.9, 25.3, 19.1, 7.6, 3.1, q=0.6, note='Datos de prensa; muestra no indicada (1.500 supuesta)'),
 P('d40928', '40dB / El País-SER (25-28 sep)', '2026-09-28', 2000, 31.6, 27.4, 18.4, 5.6, 2.7),
 P('sm926', 'SocioMétrica / El Español', '2026-09-26', 1200, 33.9, 25.7, 18.0, 5.7, 3.3),
 P('em925', 'EM-Analytics / Electomanía', '2026-09-25', 1104, 32.3, 25.3, 18.8, 6.5, 3.8),
 P('cel921', 'Celeste-Tel / Onda Cero', '2026-09-21', 1100, 33.9, 25.4, 17.8, 6.4, 3.3),
 P('dym921', 'DYM / 20minutos', '2026-09-21', 1017, 34.7, 26.3, 17.3, 4.5, 3.7),
 P('invy911', 'InvyMark / laSexta', '2026-09-11', 1200, 33.7, 26.8, 18.6, 6.1, 3.3),
]
# convertir a fracciones
for p in polls:
    p['v'] = {k: round(x/100, 5) for k, x in p['v'].items()}

out = {
 'keys': KEYS,
 'parties': D['parties'],
 'prov': prov,
 'seats2023': D['base']['seats'],
 'nat2023': [M['b_nat'][k] for k in KEYS],
 'regn': REGN,
 'fac': fac, 'tau': M['tau'], 'nreg': M['n_reg'],
 'micro': {'cis': micro('cis'), 'd40': micro('d40'), 'ceo': micro('ceo')},
 'grupos': D['grupos'],
 'polls': polls,
}
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open(W+'work/data.js', 'w').write('const D=' + s + ';\n')
open(W+'work/data.json', 'w').write(s)
print(len(s))
