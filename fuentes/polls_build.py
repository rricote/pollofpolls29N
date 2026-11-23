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
add('SocioMétrica / El Español', '2026-10-11', 1000, V(32.6, 26.2, 18.8, 5.8, 2.8, 2.1, ERC=2.0, JUNTS=1.5, BILDU=1.3, PNV=0.8, BNG=0.9, CC=0.5, UPN=0.2, ADELANTE=0.9), note=BR + '. FA 5,8 en otros agregadores')
add('EM-Analytics / Electomanía', '2026-10-03', 8171, V(31.3, 26.9, 19.4, 6.3, 3.4, 1.7, ERC=2.0, JUNTS=1.1, BILDU=1.4, PNV=1.1, BNG=1.0, CC=0.3, UPN=0.2), note=BR + '. Panel online autoseleccionado')
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
add('EM-Analytics / Electomanía', '2026-10-17', 3141, V(31.8, 27.1, 18.9, 6.2, 2.0, 1.7, JUNTS=1.2, BILDU=1.4, PNV=1.0, BNG=1.0, CC=0.3, ERC=2.1, ADELANTE=1.1), note='Fuente primaria (ElectoPanel, 15-17 oct); ERC y SALF solo de agregador')
add('Sigma Dos / El Mundo', '2026-10-14', 3007, V(31.5, 25.3, 19.5, 8.1, 2.8, None, ERC=2.5, JUNTS=1.2, BILDU=1.2, PNV=0.9, BNG=0.8, CC=0.5, UPN=0.2, ADELANTE=0.8), note='Campo 1-14 oct, publicada el 19. Agregadores (electografica y electomanía). Sustituye a la entrega parcial del 11-oct (PP 31,9 / PSOE 25,3 / Vox 19,1 / FA 7,6), que comparte entrevistas')
# --- nuevas 22-oct a 5-nov: fuentes electografica.com (agregador fiable), eleccionesenespana.es y prensa ---
# «Frente Amplio» = FA + Compromís-FV + UPC (el espacio ex-Sumar completo); en las filas anteriores de Brújula se corrigió así donde la fuente lo permitía
FAN = 'FA incluye Compromís-FV y UPC'
add('IMOP Insights / El Confidencial', '2026-10-16', 1000, V(28.5, 27.1, 20.0, 8.9, 1.9, 1.2, ERC=2.2, JUNTS=1.2, BILDU=1.3, PNV=1.0), note='Campo 13-16 oct. ' + FAN)
add('Sigma Dos / El Mundo', '2026-10-22', 3122, V(30.6, 26.1, 19.9, 8.2, 2.8, None, ERC=2.5, JUNTS=1.2, BILDU=1.2, PNV=0.9, CC=0.4), q=0.7, note='Campo 8-22 oct, publicada el 26; comparte entrevistas con la de 1-14 oct. ' + FAN)
add('Ateneo del Dato / elDiario.es', '2026-10-22', 1500, V(31.1, 27.6, 19.8, 6.8, 2.7), q=0.8, note='Campo 20-22 oct. Muestra no indicada (se supone 1.500 como la anterior)')
add('Winston / Artículo14', '2026-10-23', 1200, {'PP': 29.4, 'PSOE': 27.1, 'VOX': 19.2, 'FA': 5.6}, inc=False, note='Campo 21-23 oct. No publica Podemos, no puede entrar en la media')
add('EM-Analytics / Electomanía', '2026-10-23', 4309, V(30.9, 26.7, 19.0, 7.0, 1.7, None, ERC=2.2, JUNTS=1.3, BILDU=1.4, PNV=1.0), q=0.85, note='ElectoPanel 17-23 oct. Panel online. Comparte parte del campo con el del 15-17 oct')
add('NC Report / La Razón', '2026-10-24', 1000, V(33.1, 25.8, 19.0, 6.6, 2.6, None, ERC=2.0, JUNTS=1.8, BILDU=1.4, PNV=0.9, ADELANTE=1.3), note='Campo 22-24 oct. ' + FAN)
add('More in Common', '2026-10-25', 2210, V(28.3, 27.6, 20.8, 7.8, 2.6, 2.4), note='Campo 21-25 oct, panel online (Pulso electoral). ' + FAN)
add('SocioMétrica / El Español', '2026-10-25', 3223, V(32.4, 27.0, 18.6, 6.1, 1.8, 2.4, ERC=2.6, JUNTS=1.7, BILDU=1.3, PNV=0.8, BNG=0.9, CC=0.4, ADELANTE=1.2), q=0.6, note='Campo acumulado 1 sep-25 oct (panel online); FA 4,9 + Compromís 0,9 + UPC 0,3. Comparte entrevistas con las demás de SocioMétrica')
add('Sondaxe / La Voz de Galicia', '2026-10-28', 1200, V(29.2, 26.9, 19.2, 7.2, 2.0, 2.4, ERC=2.6, JUNTS=1.3, BILDU=1.4, PNV=0.9, BNG=0.9, CC=0.3, ADELANTE=2.0), note='Campo 26-28 oct. ' + FAN)
add('Hamalgama Métrica / Vozpópuli', '2026-10-28', 1000, V(32.4, 26.4, 19.9, 5.4, 2.2, 1.8, ERC=1.9, JUNTS=1.7, BILDU=1.3, PNV=0.9, BNG=0.8, CC=0.0, UPN=0.2, ADELANTE=1.1), note='Campo 22-28 oct. ' + FAN)
add('NC Report / La Razón', '2026-10-29', 1000, V(33.0, 25.6, 19.3, 6.9, 2.4, None, ERC=2.0, JUNTS=1.8, BILDU=1.4, PNV=0.9, BNG=0.8, CC=0.4, ADELANTE=1.2), note='Campo 26-29 oct. ' + FAN)
add('Target Point / El Debate', '2026-10-30', 1024, V(31.8, 25.5, 19.9, 6.6, 2.4, 2.6), note='Campo 28-30 oct. ' + FAN)
add('EM-Analytics / Electomanía', '2026-10-30', 1527, V(31.5, 25.8, 19.2, 6.2, 1.7, None, ERC=2.2, JUNTS=1.2, BILDU=1.4, PNV=0.9), q=0.85, note='ElectoPanel 28-30 oct (publicado el 1 nov). Panel online')
add('Sigma Dos / El Mundo', '2026-10-30', 2505, V(31.1, 24.6, 19.3, 8.4, 1.9, None, ERC=3.0, JUNTS=1.1, BILDU=1.3, PNV=0.9, BNG=1.0, CC=0.4, UPN=0.2, ADELANTE=1.4), note='Campo 29-30 oct (tras el accidente de Urda), publicada el 1 nov; FA 7,1 + Compromís 0,9 + UPC 0,4')
add('SocioMétrica / El Español', '2026-11-01', 4893, V(32.7, 26.6, 19.1, 6.1, 1.7, 2.5, ERC=2.5, JUNTS=1.4, BILDU=1.4, PNV=0.8), q=0.6, note='Campo acumulado 1 sep-1 nov. FA 5,2-6,1 según la fuente (se usa 6,1). Comparte entrevistas con las demás de SocioMétrica')
add('The Objective (sondeo interno de Vox)', '2026-10-27', 1500, V(28.1, 29.6, 20.2, 6.2, 1.9), q=0.3, inc=False, note='Sondeo interno de Vox filtrado; Vox lo ha desmentido. No es una encuesta publicada: desactivada')
# --- nuevas 6-9 nov: electografica.com, eleccionesenespana.es, prensa ---
add('Celeste-Tel / Onda Cero', '2026-11-03', 1100, V(31.8, 25.7, 19.2, 8.0, 1.9, 1.6, ERC=2.2, JUNTS=1.5, BILDU=1.4, PNV=0.9, BNG=0.8, CC=0.5, UPN=0.0, ADELANTE=1.2), note='Campo 29 oct-3 nov, publicada el 6 nov; FA 6,8 + Compromís 1,2 (UPC no desglosada)')
add('Sondaxe / La Voz de Galicia', '2026-11-04', 1200, V(29.7, 27.3, 18.6, 7.1, 2.2, 1.6, ERC=2.9, JUNTS=1.4, BILDU=1.5, PNV=0.7, BNG=0.9, CC=0.5, ADELANTE=2.3), note='Campo 2-4 nov, publicada el 8 nov. ' + FAN)
add('Ateneo del Dato / elDiario.es', '2026-11-05', 2000, V(31.5, 28.6, 18.6, 6.1, 1.5), q=0.8, note='Campo 2-5 nov, publicada el 8 nov. Solo datos de los cinco primeros partidos. ' + FAN)
add('IMOP Insights / El Confidencial', '2026-11-06', 1000, V(29.8, 25.9, 19.9, 8.1, 1.2, 1.7, ERC=2.6, JUNTS=1.2, BILDU=1.6, PNV=0.7, BNG=1.3, CC=0.5, ADELANTE=1.8), note='Campo 2-6 nov, publicada el 8 nov. ' + FAN)
add('EM-Analytics / Electomanía', '2026-11-06', 1860, V(31.1, 25.3, 19.2, 7.6, 1.8), q=0.85, note='ElectoPanel 6 nov (panel online). Solo cinco primeros partidos. ' + FAN)
add('SW Demoscopia / La Séptima', '2026-11-06', 4500, V(28.8, 30.8, 17.2, 7.7, 1.8, 2.1, ERC=2.5, JUNTS=1.2, BILDU=1.3, PNV=0.8, BNG=0.9, CC=0.4, ADELANTE=1.5), q=0.8, inc=False, note='Tracking diario móvil 26 oct-6 nov (telefónica); comparte entrevistas con sus entregas anteriores, solo se usa la última. Casa nueva y atípica (PSOE primero). ' + FAN)
# --- nuevas 9-13 nov: electografica.com, mapaelectoral.es, politicheck.es, prensa ---
add('GAD3 / ABC', '2026-11-05', 1502, V(31.9, 25.9, 18.6, 7.5, 1.4, 1.3, ERC=2.7, JUNTS=1.4, BILDU=1.5, PNV=0.9, BNG=0.9, CC=0.4, UPN=0.0, ADELANTE=1.6), note='Campo 3-5 nov (CATI), publicada el 9 nov; FA 5,7 + Compromís-FV 1,5 + UPC 0,3')
add('NC Report / La Razón', '2026-11-05', 1000, V(32.6, 25.6, 19.3, 6.9, 2.4, 0.0, ERC=2.0, JUNTS=1.8, BILDU=1.4, PNV=0.9, BNG=0.8, CC=0.4, UPN=0.4, ADELANTE=1.2), note='Campo 2-5 nov, publicada el 9 nov. ' + FAN + '; PP 32,6 + UPN-PP 0,4')
add('Data10 / OKdiario', '2026-11-03', 1500, V(32.4, 24.7, 19.8, 6.9, 3.1, 1.5, ERC=2.3, JUNTS=1.5, BILDU=1.3, PNV=0.7, BNG=1.0, CC=0.4, UPN=0.3, ADELANTE=1.3), note='Campo 2-3 nov, publicada el 9 nov (la nota y la tabla difieren: PP 32,7 o 32,4; se usa la tabla). ' + FAN)
add('DYM / 20minutos', '2026-11-06', 1025, V(33.1, 27.3, 18.6, 5.6, 1.9, 0.4), note='Campo 4-6 nov (CAWI), publicada el 10 nov. Solo seis partidos')
add('Sigma Dos / El Mundo', '2026-11-06', 4172, V(31.0, 25.2, 19.4, 8.1, 1.6, 0.0, ERC=2.9, JUNTS=1.2, BILDU=1.3, PNV=0.9, BNG=1.0, CC=0.4, UPN=0.2, ADELANTE=1.6), q=0.6, note='Campo 30 oct-6 nov, publicada el 8 nov; FA 6,5 + Compromís-FV 1,2 + UPC 0,4. Comparte entrevistas con la entrega del 11 nov, de ahí la calidad reducida')
add('Sigma Dos / El Mundo', '2026-11-11', 3120, V(30.8, 25.3, 19.6, 7.3, 1.4, 0.0, ERC=2.9, JUNTS=1.2, BILDU=1.3, PNV=0.9, BNG=1.0, CC=0.4, UPN=0.2, ADELANTE=2.0), inc=False, note='Campo 3-11 nov (CATI + CAWI), publicada el 12-13 nov; FA 5,8 + Compromís-FV 1,1 + UPC 0,4. Sustituida por la entrega del 15 nov')
add('SocioMétrica / El Español', '2026-11-08', 5460, V(32.0, 27.7, 18.9, 5.9, 1.2, 2.2, ERC=1.6, JUNTS=1.4, BILDU=1.6, PNV=0.8, ADELANTE=1.7), q=0.6, inc=False, note='Campo acumulado desde 1 sep, publicada el 8 nov (cierre no publicado). Comparte entrevistas con las demás SocioMétrica. Sustituida por la entrega del 15 nov')
add('SW Demoscopia / La Séptima', '2026-11-12', 6500, V(28.4, 31.5, 17.2, 7.3, 1.7, 2.0, ADELANTE=1.4), q=0.8, inc=False, note='Tracking diario móvil, entrega del 12 nov (publicada el 13 nov). La web solo da PP, PSOE, Vox y FA; Podemos, SALF y Adelante son de la entrega del 11 nov. n de la entrega del 11 nov (6.500). Solo se usa la última entrega porque comparten entrevistas. Sustituida por la entrega del 15 nov')
add('40dB / El País-SER', '2026-11-12', 1000, V(31.5, 29.4, 18.8, 5.1, 1.3), inc=False, note='Tracking diario, campo 10-12 nov, publicada el 13 nov. FA 3,5 + otras coaliciones de izquierda (Compromís-FV, UPC, Ara Més) 1,6. Solo cinco partidos. Es una encuesta distinta de la preelectoral I (2-4 nov), que entra por sus microdatos. Sustituida por la entrega del 16 nov (tracking acumulado)')
add('40dB / El País-SER', '2026-11-04', 2000, V(31.9, 29.9, 18.0, 5.0, 1.2, 2.0), inc=False, note='Preelectoral I (2-4 nov), publicada el 9 nov. FA 3,4 + Compromís-FV 1,1 + UPC 0,3 + Ara Més 0,2. Sustituida por el cálculo desde los microdatos de la misma encuesta; actívala para usar el dato publicado')
add('CIS / preelectoral (macroencuesta)', '2026-10-30', 45074, V(25.5, 33.3, 18.4, 6.9, 1.1, 1.4, ADELANTE=1.5), q=0.5, inc=False, note='Macroencuesta preelectoral del CIS (campo 7-30 oct, 45.074 entrevistas), publicada el 12 nov. Estimación del propio CIS (la web del CIS da FA 4,7; el 6,9 agrupa Compromís, UPC y Ara Más). Sin microdatos todavía: no entra en la media, como las filas publicadas de los barómetros. Actívala para probar')
add('Reestimación CIS preelectoral (Ateneo del Dato)', '2026-10-30', 45074, V(27.6, 30.1, 21.7, 6.3, 1.1, 1.7, ERC=3.0, JUNTS=1.1, BILDU=1.6, PNV=0.9, BNG=0.9), q=0.8, inc=False, note='Ateneo del Dato reestima la macroencuesta preelectoral del CIS (campo 7-30 oct, 45.074 entrevistas) con el método de transferencias: corrige el desequilibrio de recuerdo de voto 2023 y reparte indecisos y abstención. Publicada por elDiario.es el 13 nov. Mientras no haya microdatos del CIS sustituye a la fila del propio CIS (desactivada). Escaños de Ateneo: PSOE 124, PP 110, Vox 77, FA 7, ERC 13. Otros 3,9 %' + '. Sustituida por los microdatos del CIS 3584 (fila propia)')
# --- nuevas 13-16 nov ---
add('40dB / El País-SER', '2026-11-16', 2500, V(31.5, 30.3, 18.0, 5.4, 1.1), inc=False, note='Tracking diario acumulado, entrega del 16 nov. FA 3,7 + otras coaliciones de izquierda 1,7. Solo cinco partidos. Muestra y campo no publicados (se supone 2.500: las entregas del 13, 14 y 15 nov traían 1.000, 1.500 y 2.000). Sustituida por los microdatos del tracking diario (fila propia de microdatos); actívala para usar el dato publicado')
add('SW Demoscopia / La Séptima', '2026-11-15', 8500, V(28.4, 31.7, 16.9, 7.3, 1.7, 2.0, ADELANTE=1.5), q=0.8, inc=False, note='Tracking diario móvil, entrega del 15 nov (muestra 8.500). Solo se usa la última entrega porque comparten entrevistas' + '. Sustituida por la entrega del 16 nov')
add('Sigma Dos / El Mundo', '2026-11-15', 5370, V(31.0, 25.6, 19.7, 7.2, 1.4, None, ADELANTE=1.9), inc=False, note='Entrega del 15 nov (muestra 5.370), acumulada desde la del 11 nov; SALF no publicada. Sustituye a la del 11 nov' + '. Sustituida por la entrega del 16 nov')
add('SocioMétrica / El Español', '2026-11-15', 5923, V(31.6, 27.8, 19.1, 4.7, 1.2, 2.2, ADELANTE=1.6), q=0.6, inc=False, note='Entrega del 15 nov (muestra 5.923), acumulada desde el 1 sep. FA 4,7 según el agregador: no se sabe si incluye Compromís y UPC (las entregas anteriores daban 5,9-6,1 con ellos). Comparte entrevistas con las demás SocioMétrica' + '. Sustituida por la entrega del 21 nov')
add('EM-Analytics / Electomanía', '2026-11-15', 2617, V(30.7, 26.7, 19.0, 7.6, 1.4, 2.1, ADELANTE=1.4), q=0.85, inc=False, note='ElectoPanel 15 nov (panel online, muestra 2.617). Comparte entrevistas con las entregas diarias del 12-14 nov: solo se usa la última' + '. Sustituida por la entrega del 16 nov')
add('YouGov / Ara', '2026-11-14', 1221, V(29.6, 25.9, 20.3, 9.2, 1.8, None, ADELANTE=1.8), note='Publicada el 14 nov. Vox 20,3 según Mapa Electoral (otro agregador da 20,0). Campo no indicado. FA 9,2 (el valor más alto de todas las casas)')
add('Sondaxe / La Voz de Galicia', '2026-11-15', 1000, V(30.8, 26.4, 18.2, 6.4, 2.2, 1.6, ADELANTE=2.3), inc=False, note='Publicada el 15 nov. Campo no indicado. ' + FAN + '. Sustituida por la entrega del 16 nov')
add('Winston / Artículo14', '2026-11-13', 1501, V(31.1, 26.4, 18.7, 8.4, 1.6, 2.5, ADELANTE=1.95), note='Publicada el 13 nov. Campo no indicado')
add('NC Report / La Razón', '2026-11-12', 1000, V(32.1, 26.1, 19.0, 7.6, 1.5, None, ERC=1.9, JUNTS=1.6, BILDU=1.4, PNV=0.8, BNG=1.0, CC=0.4, UPN=0.4, ADELANTE=1.8), note='Campo 6-12 nov, publicada el 13-16 nov. Muestra no indicada (se supone 1.000); SALF no publicada')
add('IMOP Insights / El Confidencial', '2026-11-13', 1000, V(31.5, 26.9, 19.0, 6.9, 0.9, 1.6, ERC=2.9, BILDU=1.7, BNG=1.3, ADELANTE=2.2), note='Cuarta oleada, campo 10-13 nov, publicada el 16 nov. Muestra no indicada (se supone 1.000). FA incluye Compromís-FV (7 + 4 escaños)')
# --- nuevas 16 nov ---
add('40dB / El País-SER', '2026-11-16', 2000, V(31.8, 30.6, 17.5, 5.4, 1.1, 1.6), inc=False, note='Tracking diario, entrega del 17 nov (campo 12-16 nov, 2.000 entrevistas). FA 3,7 + otras coaliciones 1,7. Sustituida por los microdatos del tracking (fila propia); actívala para usar el dato publicado')
add('SW Demoscopia / La Séptima', '2026-11-16', 9000, V(28.6, 31.8, 16.8, 7.4, 1.7, 2.0, ADELANTE=1.5), q=0.8, inc=False, note='Tracking diario móvil, entrega del 16 nov (muestra 9.000). Solo se usa la última entrega porque comparten entrevistas' + '. Sustituida por la entrega del 17 nov')
add('Sigma Dos / El Mundo', '2026-11-16', 3002, V(30.8, 26.1, 19.8, 8.3, 1.4, None, ADELANTE=1.8), inc=False, note='Entrega del 16 nov (muestra 3.002, ventana móvil); SALF no publicada. Sustituye a la del 15 nov' + '. Sustituida por la entrega del 17 nov')
add('EM-Analytics / Electomanía', '2026-11-16', 3294, V(30.5, 26.9, 18.9, 7.7, 1.2, 2.2, ADELANTE=1.5), q=0.85, inc=False, note='ElectoPanel 16 nov (panel online, muestra 3.294). Comparte entrevistas con las entregas diarias anteriores: solo se usa la última' + '. Sustituida por la entrega del 17 nov')
add('Sondaxe / La Voz de Galicia', '2026-11-16', 1000, V(30.2, 26.7, 17.6, 6.5, 2.2, None, ADELANTE=1.8), inc=False, note='Publicada el 16 nov. Campo no indicado; SALF no publicada. Sustituye a la del 15 nov' + '. Sustituida por la entrega del 17 nov')
add('Target Point / El Debate', '2026-11-16', 1013, V(30.6, 27.0, 18.7, 7.3, 1.6, 2.1, ADELANTE=1.9), note='Publicada el 16 nov. Campo no indicado')
add('Data10 / OKdiario', '2026-11-16', 1500, V(31.7, 25.5, 20.4, 6.7, 2.1, 1.5, ADELANTE=1.7), inc=False, note='Publicada el 16 nov. Campo no indicado' + '. Sustituida por la entrega del 19 nov')
add('InvyMark / laSexta', '2026-11-16', 1000, {'PP': 32.2, 'PSOE': 28.2, 'VOX': 19.1, 'FA': 6.4}, inc=False, note='Publicada el 16 nov. No publica Podemos (no puede entrar en la media); muestra no indicada. Casa dudosa en entregas anteriores')
# --- nuevas 17-18 nov ---
add('40dB / El País-SER', '2026-11-17', 2000, V(32.2, 30.7, 17.0, 5.2, 1.2, 1.7), inc=False, note='Tracking diario, entrega del 18 nov (campo 13-17 nov, 2.000 entrevistas). FA 3,5 + otras coaliciones 1,7. Sustituida por los microdatos del tracking (fila propia); actívala para usar el dato publicado')
add('SW Demoscopia / La Séptima', '2026-11-17', 9500, V(29.1, 31.9, 16.5, 7.3, 1.7, 2.0, ADELANTE=1.5), q=0.8, inc=False, note='Tracking diario móvil, entrega del 17 nov (muestra 9.500). La web solo da PP, PSOE, Vox y FA; Podemos, SALF y Adelante son de la entrega del 16 nov. Solo se usa la última entrega porque comparten entrevistas' + '. Sustituida por la entrega del 18 nov')
add('Sigma Dos / El Mundo', '2026-11-17', 3759, V(30.7, 26.4, 19.8, 6.7, 1.2, None, ADELANTE=1.8), inc=False, note='Entrega del 17 nov (muestra 3.759, ventana móvil); SALF no publicada. Sustituye a la del 16 nov' + '. Sustituida por la entrega del 18 nov')
add('EM-Analytics / Electomanía', '2026-11-17', 4446, V(30.8, 27.0, 18.8, 7.7, 1.3, 2.2, ADELANTE=1.5), q=0.85, inc=False, note='ElectoPanel 17 nov (panel online, muestra 4.446). Comparte entrevistas con las entregas diarias anteriores: solo se usa la última' + '. Sustituida por la entrega del 18 nov')
add('Sondaxe / La Voz de Galicia', '2026-11-17', 1000, V(29.7, 26.7, 18.0, 7.7, 2.1, 3.0, ADELANTE=1.6), inc=False, note='Publicada el 17 nov (la fuente enlaza una ruta del 16 nov: la fecha puede variar un día). Campo no indicado. Sustituye a la del 16 nov' + '. Sustituida por la entrega del 18 nov')
# --- nuevas 18 nov ---
add('SW Demoscopia / La Séptima', '2026-11-18', 10000, V(29.1, 31.9, 16.4, 7.3, 1.6, 2.0, ADELANTE=1.6), q=0.8, inc=False, note='Tracking diario móvil, entrega del 18 nov (muestra 10.000). Solo se usa la última entrega porque comparten entrevistas' + '. Sustituida por la entrega del 20 nov')
add('Sigma Dos / El Mundo', '2026-11-18', 4511, V(30.7, 26.7, 19.7, 8.7, 0.8, None, ADELANTE=1.7), inc=False, note='Entrega del 18 nov (muestra 4.511, ventana móvil); SALF no publicada. Sustituye a la del 17 nov' + '. Sustituida por la entrega del 19 nov')
add('EM-Analytics / Electomanía', '2026-11-18', 4927, V(30.8, 27.0, 18.9, 7.7, 1.3, 2.2, ADELANTE=1.6), q=0.85, inc=False, note='ElectoPanel 18 nov (panel online, muestra 4.927). Comparte entrevistas con las entregas diarias anteriores: solo se usa la última' + '. Sustituida por la entrega del 19 nov')
add('Sondaxe / La Voz de Galicia', '2026-11-18', 1000, V(28.5, 27.8, 19.6, 7.1, 1.0, 2.7, ADELANTE=1.3), inc=False, note='Publicada el 18 nov (el agregador lista dos entregas ese día; se usa la primera: 29,0 / 27,0 / 19,4 / 7,5 en la segunda, que apunta a una noticia del 17). Campo no indicado. Sustituye a la del 17 nov' + '. Sustituida por la entrega del 19 nov')
# --- nuevas 19 nov ---
add('Sigma Dos / El Mundo', '2026-11-19', 4491, V(31.0, 27.1, 19.4, 8.9, 0.8, None, ADELANTE=1.7), inc=False, note='Entrega del 19 nov (muestra 4.491, ventana móvil); SALF no publicada. Sustituye a la del 18 nov' + '. Sustituida por la entrega del 20 nov')
add('EM-Analytics / Electomanía', '2026-11-19', 5704, V(30.4, 27.6, 18.7, 7.4, 1.1, 2.4, ADELANTE=1.6), q=0.85, inc=False, note='ElectoPanel 19 nov (panel online, muestra 5.704). Comparte entrevistas con las entregas diarias anteriores: solo se usa la última' + '. Sustituida por la entrega del 20 nov')
add('Sondaxe / La Voz de Galicia', '2026-11-19', 1000, V(28.5, 27.8, 19.6, 7.4, 1.0, 2.7, ADELANTE=1.3), inc=False, note='Publicada el 19 nov. Campo no indicado. Sustituye a la del 18 nov' + '. Sustituida por la entrega del 20 nov')
add('Data10 / OKdiario', '2026-11-19', 2600, V(31.5, 26.9, 19.4, 6.5, 2.1, 1.5, ADELANTE=1.7), inc=False, note='Publicada el 19 nov (muestra acumulada 2.600; el 18 nov fue 2.300: 31,6 / 26,5 / 19,4 / 6,7). Campo no indicado. Sustituye a las entregas del 16 y 18 nov' + '. Sustituida por la entrega del 20 nov')
add('Public First / Politico', '2026-11-19', 2454, V(29.5, 27.2, 19.6, 5.9, 2.2, 2.0, ADELANTE=1.8), q=0.85, note='Publicada el 19 nov. Campo no indicado; casa nueva en la media. La fuente la repite como "PF Global" (n=1.375) con cifras idénticas: se cuenta una sola vez')
add('PF Global / Politico', '2026-11-19', 1375, V(29.5, 27.2, 19.6, 5.9, 2.2, 2.0, ADELANTE=1.8), q=0.85, inc=False, note='Cifras idénticas a Public First / Politico (misma publicación duplicada en el agregador): no se cuenta dos veces')
add('Metroscopia / laSexta', '2026-11-19', 1000, {'PP': 30.0, 'PSOE': 30.0, 'VOX': 19.0}, inc=False, note='Publicada el 19 nov. Solo PP, PSOE y Vox (sin Frente Amplio ni Podemos): no puede entrar en la media; muestra no indicada')
add('40dB / El País-SER', '2026-11-19', 2000, V(32.4, 30.4, 17.2, 3.7, 1.2, 1.7), inc=False, note='Tracking diario "día 7", publicado el 19 nov (n=2.000). FA 3,7 + otras coaliciones 1,7 (Sumar 5,4 según el agregador). Sustituida por los microdatos del tracking (fila propia)')
add('40dB / El País-SER', '2026-11-19', 2000, V(32.2, 30.2, 17.6, 3.6, 1.1, 1.7), inc=False, note='Tracking diario "día 8", publicado el 19 nov (n=2.000; Sumar 5,3 según el agregador). Sustituida por los microdatos del tracking (fila propia)')
# --- nuevas 20 nov ---
add('SW Demoscopia / La Séptima', '2026-11-19', 10500, V(29.2, 31.8, 16.4, 7.3, 1.6, 2.0, ADELANTE=1.6), q=0.8, inc=False, note='Tracking diario móvil, entrega del 19 nov (muestra 10.500; Adelante de la del 18). Sustituida por la entrega del 20 nov')
add('SW Demoscopia / La Séptima', '2026-11-20', 11000, V(29.6, 32.1, 16.3, 6.9, 1.6, 2.0, ADELANTE=1.6), q=0.8, inc=False, note='Tracking diario móvil, entrega del 20 nov (muestra 11.000). La web solo da PP, PSOE, Vox y FA; Podemos 1,6, SALF 2,0 y Adelante 1,6 son de la entrega del 19 nov. Solo se usa la última entrega porque comparten entrevistas' + '. Sustituida por la entrega del 21 nov')
add('Sigma Dos / El Mundo', '2026-11-20', 4561, V(31.2, 27.6, 18.9, 8.9, 0.8, None, ADELANTE=1.7), inc=False, note='Entrega del 20 nov (muestra 4.561, ventana móvil); SALF no publicada. Sustituye a la del 19 nov' + '. Sustituida por la entrega del 21 nov')
add('EM-Analytics / Electomanía', '2026-11-20', 6559, V(31.0, 27.6, 18.2, 7.6, 0.9, 2.3, ADELANTE=1.6), q=0.85, inc=False, note='ElectoPanel 20 nov (panel online, muestra 6.559). Comparte entrevistas con las entregas diarias anteriores: solo se usa la última' + '. Sustituida por la entrega del 21 nov')
add('Sondaxe / La Voz de Galicia', '2026-11-20', 1000, V(29.3, 27.8, 19.7, 6.9, 0.9, None, ADELANTE=1.6), inc=False, note='Entrega del 20 nov según Mapa Electoral (el artículo enlazado es del 19: puede ser una sola entrega listada dos veces con cifras distintas). Campo no indicado; SALF no publicada. Sustituye a la del 19 nov' + '. Sustituida por la entrega del 21 nov')
add('Data10 / OKdiario', '2026-11-20', 750, V(32.5, 26.5, 18.8, 6.8, 2.1, 1.5, ADELANTE=1.7), inc=False, note='Publicada el 20 nov. Mapa Electoral da n=750 (la del 19 fue 2.600 acumulada: la muestra puede estar mal). Campo no indicado. Sustituye a la del 19 nov' + '. Sustituida por la entrega del 21 nov')
add('More in Common', '2026-11-20', 2315, V(28.9, 28.0, 19.8, 7.1, 1.7, 2.3), q=0.85, note='Publicada el 20 nov (el agregador no indica el medio). Campo no indicado; Adelante no publicada')
add('40dB / El País-SER', '2026-11-20', 2000, V(31.9, 31.2, 17.1, 5.5, 1.1, 1.5), inc=False, note='Tracking diario "día 9", publicado el 20 nov (n=2.000). Es el mismo dato que los microdatos del día 9 (ya incluidos en la fila de microdatos del tracking)')
add('40dB / El País-SER', '2026-11-21', 2000, V(31.9, 31.6, 16.9, 5.3, 1.0, 1.4), inc=False, note='Tracking diario "día 10", publicado el 21 nov (campo 17-21 nov, ventana móvil; n=2.000 supuesta). FA 3,6 + otras coaliciones 1,7. Comparte 1.500 entrevistas con los microdatos del tracking (días 7-9): no se suma a ellos; actívala solo si desactivas la fila de microdatos. Los microdatos del día 10 ya están en la fila del tracking')
# --- nuevas 21 nov ---
add('SocioMétrica / El Español', '2026-11-21', 6842, V(31.8, 28.5, 18.8, 5.9, 1.0, 2.2, ADELANTE=1.6), q=0.6, inc=False, note='Entrega del 21 nov (muestra 6.842), acumulada. FA 5,9 (con Compromís y UPC). El agregador enlaza una ruta del 15 nov: la fecha puede variar. Comparte entrevistas con las demás de SocioMétrica. Sustituye a la del 15 nov' + '. Sustituida por la entrega del 22 nov')
add('EM-Analytics / Electomanía', '2026-11-21', 7109, V(31.0, 27.9, 18.5, 7.3, 0.9, 2.1, ADELANTE=1.6), q=0.85, inc=False, note='ElectoPanel 21 nov (panel online, muestra 7.109). Comparte entrevistas con las entregas diarias anteriores: solo se usa la última' + '. Sustituida por la entrega del 22 nov')
add('Sigma Dos / El Mundo', '2026-11-21', 4511, V(31.5, 28.0, 18.3, 7.1, 0.7, None, ADELANTE=1.6), inc=False, note='Entrega del 21 nov (muestra 4.511, ventana móvil); SALF no publicada. Sustituye a la del 20 nov' + '. Sustituida por la entrega del 22 nov')
add('SW Demoscopia / La Séptima', '2026-11-21', 11500, V(29.7, 32.5, 15.9, 6.8, 1.6, 2.0, ADELANTE=1.6), q=0.8, inc=False, note='Tracking diario móvil, entrega del 21 nov (muestra 11.500). Podemos, SALF y Adelante de entregas anteriores. Solo se usa la última entrega porque comparten entrevistas' + '. Sustituida por la entrega del 22 nov')
add('Data10 / OKdiario', '2026-11-21', 3000, V(32.3, 26.5, 19.9, 6.7, 2.1, 1.5, ADELANTE=1.7), inc=False, note='Publicada el 21 nov (muestra 3.000; la del 20 dio 750, que parecía errónea). Campo no indicado. Sustituye a la del 20 nov' + '. Sustituida por la entrega del 22 nov')
add('Sondaxe / La Voz de Galicia', '2026-11-21', 1000, V(29.5, 27.9, 19.8, 6.8, 0.9, None, ADELANTE=1.4), inc=False, note='Entrega del 21 nov. Podemos no publicado en la fuente: se mantiene el 0,9 de la entrega anterior; SALF no publicada. Campo no indicado. Sustituye a la del 20 nov' + '. Sustituida por la entrega del 22 nov')
# --- nuevas 22-23 nov ---
add('SocioMétrica / El Español', '2026-11-22', 7266, V(31.7, 28.7, 18.4, 5.9, 1.0, 2.2, ADELANTE=1.7), q=0.6, note='Entrega del 22 nov (muestra 7.266), acumulada. Comparte entrevistas con las demás de SocioMétrica. Sustituye a la del 21 nov')
add('EM-Analytics / Electomanía', '2026-11-22', 7982, V(31.2, 28.4, 18.3, 7.6, 0.92, 2.10, ADELANTE=1.74), q=0.85, note='ElectoPanel 22 nov (panel online, muestra 7.982). Comparte entrevistas con las entregas diarias anteriores: solo se usa la última')
add('Sigma Dos / El Mundo', '2026-11-22', 4616, V(31.7, 28.3, 17.9, 7.2, 0.7, None, ADELANTE=1.6), note='Entrega del 22 nov (muestra 4.616, ventana móvil); SALF no publicada y Adelante de la entrega anterior. Sustituye a la del 21 nov')
add('SW Demoscopia / La Séptima', '2026-11-22', 12000, V(29.9, 32.5, 15.8, 6.8, 1.6, 2.0, ADELANTE=1.6), q=0.8, note='Tracking diario móvil, entrega del 22 nov (muestra 12.000). Podemos, SALF y Adelante de entregas anteriores. Solo se usa la última entrega porque comparten entrevistas')
add('Data10 / OKdiario', '2026-11-22', 3000, V(32.1, 27.0, 19.0, 6.6, 2.1, 1.5, ADELANTE=1.7), note='Publicada el 22 nov (muestra 3.000). Campo no indicado. Sustituye a la del 21 nov')
add('Sondaxe / La Voz de Galicia', '2026-11-22', 1000, V(31.1, 28.2, 17.3, 7.4, 1.5, 1.7, ADELANTE=1.7), note='Entrega del 22 nov (la fuente cita una imagen de X; el agregador lista otra entrada del 22 con 30,0 / 27,7 / 18,8 / 8,1, que parece reciclar la del 21: no se usa). Campo no indicado. Sustituye a la del 21 nov')
add('Ipsos / La Vanguardia', '2026-11-22', 1999, V(30.3, 29.8, 17.9, 5.8, 1.1, 1.9, ADELANTE=2.14), note='Publicada el 22 nov. Campo no indicado; FA 5,8 (agrupación con Compromís y UPC no confirmada)')
add('Hamalgama Métrica / Vozpópuli', '2026-11-22', 1000, V(31.8, 25.4, 20.6, 6.5, 1.2, 1.7, ADELANTE=1.53), q=0.85, note='Publicada el 22 nov. Campo no indicado. Escaños de la fuente atípicos (Vox 80, PSOE 98)')
add('Winston / Artículo14', '2026-11-22', 1482, V(31.1, 28.2, 17.7, 6.4, 1.6, 2.6), note='Publicada el 22 nov. Campo no indicado; Adelante no publicada')
add('GAD3 / ABC', '2026-11-19', 1501, V(31.1, 28.4, 18.1, 8.0, 1.1, 1.3, ERC=2.6, JUNTS=1.1, BILDU=1.6, PNV=1.0, BNG=0.9, CC=0.3, ADELANTE=1.93), note='Campo 16-19 nov, publicada el 22 nov. FA 8,0 según Mapa Electoral (con Compromís y UPC; Comparavoto da FA 5,8 + Compromís 1,5)')
add('DYM / 20minutos', '2026-11-22', 1010, V(33.0, 28.0, 18.0, 6.9, 1.3, 0.4), note='Publicada el 22 nov. Campo no indicado; SALF 0,4 según la fuente')
add('40dB / El País-SER', '2026-11-23', 7500, V(31.8, 30.9, 17.3, 5.7, 1.1), inc=False, note='Encuesta final de 40dB publicada por El País el 23 nov: 7.500 entrevistas (2.000 del segundo barómetro preelectoral, 18-20 nov, más 5.500 del tracking diario, 10-21 nov), campo 10-21 nov, error ±1,1 %. Escaños: PP 130 (con 2 de UPN), PSOE 124, Vox 57, izquierdas 9, otros 30. Se solapa con los microdatos del tracking (ya incluidos), por eso no se suma; actívala solo si desactivas la fila de microdatos. Faltan los microdatos del barómetro de 18-20 nov')
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
