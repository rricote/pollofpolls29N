"""Construye la lista de encuestas: Brújula 29N (JSON de datos abiertos), electografica.com (histórico), prensa y agregadores.
Cada fila: id, name 'Casa / Medio', date (fin de campo), n, v (% por partido), q (calidad), include, src, note."""
import csv, re, json, os
W = os.path.dirname(os.path.abspath(__file__)) + '/'
CAN = {  # nombre canónico de la casa (lo que va antes de «/» identifica la casa para el efecto casa)
 'sociometrica': 'SocioMétrica / El Español', 'socio': 'SocioMétrica / El Español',
 'nc report': 'NC Report / La Razón', 'hamalgama metrica': 'Hamalgama Métrica / Vozpópuli', 'gad3': 'GAD3 / ABC',
 'target point': 'Target Point / El Debate', '40db': '40dB / El País-SER', 'sigma dos': 'Sigma Dos / El Mundo',
 'dym': 'DYM / 20minutos', 'gesop': 'GESOP / El Periódico', 'invymark': 'InvyMark / laSexta', 'celeste-tel': 'Celeste-Tel / Onda Cero',
 'em-analytics': 'EM-Analytics / Electomanía', 'data10': 'Data10 / OKdiario', 'ateneo del dato': 'Ateneo del Dato / elDiario.es',
 'cluster17': 'Cluster17 / Agenda Pública', 'opina 360': 'Opina 360 / Telecinco-Antena 3', 'ipsos': 'Ipsos / La Vanguardia',
 'winston': 'Winston / Artículo14', 'imop insights': 'IMOP Insights / El Confidencial'}
import unicodedata
def norm(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()
def canon(casa):
    c = norm(casa)
    for k, v in CAN.items():
        if c.startswith(norm(k)): return v
    return casa
KEYMAP = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'VOX', 'FA': 'SUMAR', 'SUMAR': 'SUMAR', 'PODEMOS': 'PODEMOS', 'SALF': 'SALF', 'ADELANTE': 'ADELANTE',
          'ERC': 'ERC', 'JUNTS': 'JUNTS', 'BILDU': 'BILDU', 'PNV': 'PNV', 'BNG': 'BNG', 'CC': 'CC', 'UPN': 'UPN'}
polls = []
def add(casa, date, n, vals, q=1.0, inc=True, note='', src='pub'):
    name = canon(casa)
    v = {KEYMAP[k]: round(float(x) / 100, 5) for k, x in vals.items() if x not in (None, '') and k in KEYMAP}
    pid = re.sub(r'[^a-z0-9]', '', norm(name.split('/')[0]))[:8] + date.replace('-', '')[2:]
    base = pid; i = 2
    while any(p['id'] == pid for p in polls): pid = f'{base}_{i}'; i += 1
    polls.append({'id': pid, 'name': name, 'date': date, 'n': int(n) if n else 1000, 'v': v, 'q': q, 'include': inc, 'src': src, 'note': note})
def V(pp, ps, vx, fa, po, sa=None, **k):
    d = {'PP': pp, 'PSOE': ps, 'VOX': vx, 'FA': fa, 'PODEMOS': po}
    if sa is not None: d['SALF'] = sa
    d.update(k); return d
BR = 'Brújula 29N (datos abiertos)'
# --- Brújula 29N, encuestas.json (14-oct-2026): fecha = fin de campo ---
add('GAD3 / ABC', '2026-10-08', 1077, V(31.4, 26.4, 18.2, 7.4, 2.3, 1.8, ERC=2.6, JUNTS=1.5, BILDU=1.5, PNV=1.0, BNG=0.9, CC=0.4, UPN=0.1), note=BR)
add('GESOP / El Periódico', '2026-10-08', 1000, V(28.7, 26.1, 18.9, 8.0, 2.6, 2.0, ERC=2.5, JUNTS=1.9), q=0.6, note=BR + '. Mezcla escenarios (FA y Podemos por separado según la casa); PP aportado solo por agregadores')
add('SocioMétrica / El Español', '2026-10-11', 1000, V(32.6, 26.2, 18.8, 4.9, 2.8, 2.1, ERC=2.0, JUNTS=1.5, BILDU=1.3, PNV=0.8, BNG=0.9, CC=0.5, UPN=0.2, ADELANTE=0.9), note=BR + '. FA 5,8 en otros agregadores')
add('EM-Analytics / Electomanía', '2026-10-03', 8171, V(31.3, 26.9, 19.4, 5.2, 3.4, 1.7, ERC=2.0, JUNTS=1.1, BILDU=1.4, PNV=1.1, BNG=1.0, CC=0.3, UPN=0.2), note=BR + '. Panel online autoseleccionado')
add('Data10 / OKdiario', '2026-10-02', 1000, V(34.0, 26.1, 18.6, 5.2, 4.3, 1.4, ERC=1.9, JUNTS=1.5, BILDU=1.4, PNV=0.8, BNG=1.0, CC=0.3, UPN=0.2), note=BR)
add('SocioMétrica / El Español', '2026-10-03', 1000, V(33.4, 26.5, 18.1, 5.3, 3.1, 2.2, ERC=2.2, JUNTS=1.2, BILDU=1.3, PNV=1.0, BNG=0.9, CC=0.6, UPN=0.2), note=BR)
add('Sigma Dos / El Mundo', '2026-10-01', 2116, V(32.6, 25.6, 18.3, 6.6, 3.3, None, ERC=2.5, JUNTS=1.1, BILDU=1.3, PNV=1.0, BNG=0.9, CC=0.5, UPN=0.2), note=BR + '. Campo 22 sep-1 oct')
add('Winston / Artículo14', '2026-10-01', 1201, V(31.3, 24.9, 19.1, 6.8, 3.9), note=BR)
add('Ateneo del Dato / elDiario.es', '2026-10-01', 1500, V(33.2, 27.5, 19.2, 7.0, 3.3), note=BR)
add('40dB / El País-SER', '2026-09-28', 2000, V(31.6, 27.4, 18.4, 5.6, 2.7, 2.0), note=BR)
add('SocioMétrica / El Español', '2026-09-26', 1200, V(33.9, 25.7, 18.0, 5.7, 3.3, 2.0, ERC=2.0, JUNTS=1.2, BILDU=1.4, PNV=0.9, BNG=1.0, CC=0.6, UPN=0.2), note=BR)
add('DYM / 20minutos', '2026-09-21', 1017, V(34.7, 26.3, 17.3, 4.5, 3.7, 1.0), note=BR + '. Campo 16-21 sep')
add('Target Point / El Debate', '2026-09-10', 1012, V(31.5, 25.6, 18.9, 6.9, 2.8, 2.5), note=BR)
add('Hamalgama Métrica / Vozpópuli', '2026-09-08', 1000, V(33.6, 25.1, 19.3, 5.6, 3.8, 1.6, ERC=1.9, JUNTS=1.4, BILDU=1.3, PNV=0.9, BNG=0.8, CC=0.5, UPN=0.2), note=BR)
add('GAD3 / ABC', '2026-09-03', 1010, V(31.1, 26.1, 19.2, 7.0, 3.1, 1.5, ERC=2.3, JUNTS=1.2, BILDU=1.5, PNV=0.9, BNG=0.9, CC=0.3, UPN=0.2), note=BR)
add('NC Report / La Razón', '2026-09-03', 1000, V(34.4, 24.9, 18.3, 5.7, 3.4, None, ERC=2.0, JUNTS=1.6, BILDU=1.4, PNV=1.0, BNG=0.8, CC=0.4, UPN=0.2), note=BR)
add('40dB / El País-SER', '2026-09-02', 2000, V(32.4, 27.6, 17.8, 5.7, 2.8, 2.2), note=BR + '. Campo 31 ago-2 sep')
add('GESOP / El Periódico', '2026-07-09', 1001, V(29.4, 26.5, 17.8, 7.7, 4.0, 2.0, ERC=2.3, JUNTS=1.0), note=BR)
add('NC Report / La Razón', '2026-10-06', 1000, V(34.1, 25.0, 18.2, 5.3, 3.9, None, ERC=1.8, JUNTS=2.9, BILDU=1.4, PNV=0.9, BNG=0.7, CC=0.4, UPN=0.2), note=BR)
add('DYM / 20minutos', '2026-10-07', 1011, V(34.0, 28.2, 18.2, 3.6, 2.6, 0.5), note=BR + '. Podemos 2,6 (Brújula) o 3,6 (otro agregador)')
add('40dB / El País-SER', '2026-10-08', 800, V(31.9, 28.1, 18.9, 5.3, 2.3, 1.8), inc=False, note=BR + '. Sustituida por el cálculo desde los microdatos de la misma encuesta; actívala para usar el dato publicado')
add('IMOP Insights / El Confidencial', '2026-10-07', 900, V(30.4, 26.5, 19.0, 7.6, 2.3, 1.9, ERC=2.2, JUNTS=1.1, BILDU=1.3, PNV=0.9, BNG=1.1, CC=0.6, UPN=0.2), note=BR)
add('Hamalgama Métrica / Vozpópuli', '2026-10-08', 1000, V(33.4, 25.3, 19.6, 5.4, 3.3, 1.8, ERC=1.9, JUNTS=1.7, BILDU=1.3, PNV=0.9, BNG=0.8, CC=0.5, UPN=0.2), note=BR)
add('Target Point / El Debate', '2026-10-09', 1002, V(32.0, 25.9, 18.7, 6.9, 3.4, 1.3), note=BR)
# --- prensa / agregadores (ya usadas en la versión anterior) ---
add('InvyMark / laSexta', '2026-10-09', 1200, V(32.8, 28.0, 18.8, 6.3, 3.2), q=0.6, note='Una sola fuente; muestra y campo sin confirmar')
add('InvyMark / laSexta', '2026-09-11', 1200, V(33.7, 26.8, 18.6, 6.1, 3.3), q=0.8, note='Agregadores; muestra supuesta')
add('Celeste-Tel / Onda Cero', '2026-09-21', 1100, V(33.9, 25.4, 17.8, 6.4, 3.3), q=0.8, note='Agregadores; electografica solo recoge una de septiembre de 2025, revisar')
add('EM-Analytics / Electomanía', '2026-09-25', 1104, V(32.3, 25.3, 18.8, 6.5, 3.8), note='Agregadores (Brújula 29N)')
# --- nuevas hasta el 21-oct ---
add('EM-Analytics / Electomanía', '2026-10-17', 3141, V(31.8, 27.1, 18.9, 4.9, 2.0, 1.7, JUNTS=1.2, BILDU=1.4, PNV=1.0, BNG=1.0, CC=0.3, ERC=2.1, ADELANTE=1.1), note='Fuente primaria (ElectoPanel, 15-17 oct); ERC y SALF solo de agregador')
add('Sigma Dos / El Mundo', '2026-10-14', 3007, V(31.5, 25.3, 19.5, 7.2, 2.8, None, ERC=2.5, JUNTS=1.2, BILDU=1.2, PNV=0.9, BNG=0.8, CC=0.5, UPN=0.2, ADELANTE=0.8), note='Campo 1-14 oct, publicada el 19. Agregadores (electografica y electomanía). Sustituye a la entrega parcial del 11-oct (PP 31,9 / PSOE 25,3 / Vox 19,1 / FA 7,6), que comparte entrevistas')
# --- histórico: electografica.com (agregador) ---
def have(name, date): return any(p['name'] == canon(name) and p['date'] == date for p in polls)
SKIP = set()
for f, drop in (('polls_histA.csv', set()), ('polls_histB.csv', set()), ('polls_histC.csv', {('Data10', '2026-02-10'), ('EM-Analytics', '2026-07-15'), ('EM-Analytics', '2026-07-01'), ('EM-Analytics', '2026-06-30')})):
    for r in csv.DictReader(open(W + f, encoding='utf-8')):
        d = r['campo_fin'] or r['campo_ini']
        if not d or (r['casa'], d) in drop: continue
        if (r['casa'], r['campo_ini']) in drop: continue
        if have(r['casa'], d): continue
        if d >= '2026-09-01' and canon(r['casa']) in {p['name'] for p in polls if p['date'] >= '2026-09-01'}:
            # evitar duplicados con tolerancia de fechas (campo vs publicación)
            if any(p['name'] == canon(r['casa']) and abs((int(p['date'][8:]) + 30 * int(p['date'][5:7])) - (int(d[8:]) + 30 * int(d[5:7]))) <= 3 for p in polls if p['date'][:4] == d[:4]): continue
        vals = {k: r[k] for k in ('PP', 'PSOE', 'VOX', 'FA', 'PODEMOS', 'SALF', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'UPN', 'ADELANTE') if r.get(k, '') != ''}
        if 'SALF' in vals and float(vals['SALF']) == 0 and r['casa'].startswith(('Sigma', 'NC')): vals.pop('SALF')
        if r['casa'] == 'EM-Analytics' and d == '2026-09-03': vals.pop('ADELANTE', None)
        if not all(k in vals for k in ('PP', 'PSOE', 'VOX', 'FA', 'PODEMOS')): continue
        add(r['casa'], d, r['n'], vals, q=0.85, note='electografica.com (agregador, sin contrastar con la fuente primaria)' + (('. ' + r['nota']) if r.get('nota') else ''))
polls.sort(key=lambda p: p['date'], reverse=True)
if __name__ == '__main__':
    from collections import Counter
    c = Counter(canon(p['name']).split('/')[0].strip() for p in polls if p['include'])
    print(len(polls), dict(c.most_common()))
    print(sum(1 for p in polls if p['date'] >= '2026-09-01'))
