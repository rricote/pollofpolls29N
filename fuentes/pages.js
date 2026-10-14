/* ---- mapa genérico ---- */
const PI = {}; D.prov.forEach((p, j) => PI[p.id] = j);
function drawMap(target, cfg) {
  let h = '', selp = '';
  const attrs = (id, j) => `data-id="${id}" tabindex="0" role="button" aria-label="${esc(cfg.aria(id, j))}"`;
  Object.keys(MAP.paths).forEach(id => { const j = PI[id]; if (j === undefined) return; const [c, op] = cfg.fill(id, j);
    const p = `<path ${attrs(id, j)} class="${id === cfg.sel ? 'sel' : ''}" d="${MAP.paths[id]}" style="fill:${c};fill-opacity:${op.toFixed(2)}"><title>${esc(cfg.title(id, j))}</title></path>`;
    if (id === cfg.sel) selp = p; else h += p });
  let sqs = ''; Object.keys(MAP.sq).forEach(id => { const j = PI[id]; if (j === undefined) return; const [c, op] = cfg.fill(id, j), [x, y, s] = MAP.sq[id], l = cfg.label(id, j);
    sqs += `<rect ${attrs(id, j)} class="sqr${id === cfg.sel ? ' sel' : ''}" x="${x}" y="${y}" width="${s}" height="${s}" rx="4" style="fill:${c};fill-opacity:${op.toFixed(2)}"><title>${esc(cfg.title(id, j))}</title></rect>${l ? `<text class="ml ${cfg.dark(id, j) ? 'dk' : 'lt'} ${cfg.small ? 'sm' : ''}" x="${x + s / 2}" y="${y + s / 2}">${l}</text>` : ''}` });
  let tx = ''; Object.keys(MAP.lab).forEach(id => { const j = PI[id]; if (j === undefined) return; const l = cfg.label(id, j); if (l) tx += `<text class="ml ${cfg.dark(id, j) ? 'dk' : 'lt'} ${cfg.small ? 'sm' : ''}" x="${MAP.lab[id][0]}" y="${MAP.lab[id][1]}">${l}</text>` });
  const b = MAP.box;
  $(target).innerHTML = `<svg class="mapsvg" viewBox="0 0 ${MAP.w} ${MAP.h}" role="group" aria-label="${esc(cfg.group)}">${h}${selp}${tx}${sqs}<rect class="bx" x="${b[0]}" y="${b[1]}" width="${b[2] - b[0]}" height="${b[3] - b[1]}" rx="6"/><text class="bt" x="${b[0] + 8}" y="${b[1] + 16}">Canarias</text></svg>`;
  $(target).querySelectorAll('[data-id]').forEach(el => { const go = () => cfg.pick(el.dataset.id); el.onclick = go; el.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go() } } });
}
const pts = x => (x >= 0 ? '+' : '−') + nf(Math.abs(x) * 100, 1);
const mark = (k, w) => `<span class="sw" style="background:var(--c-${k})"></span>`;
function present(j, k) { return D.prov[j].sh[k] > 0 || ((k === KI.PODEMOS || k === KI.SALF) && st.A.T[k] > 0) }
const NC = {};
function need(j, k) {
  const key = j + '_' + k; if (NC[key]) return NC[key];
  const { S } = st, row = S.centShare[j], seats = D.prov[j].seats, c = S.cent[j][k], share = row[k], ok = present(j, k) && st.A.T[k] > 0;
  const r = { ok, c, share, seats };
  if (ok) { r.n1 = needShare(row, k, seats, 1); r.nx = c + 1 <= seats ? needShare(row, k, seats, c + 1) : null; r.hs = histStats(S.hist[j][k], S.N) }
  return NC[key] = r;
}

/* ---- página de provincias ---- */
function provPage() {
  const { S } = st;
  for (const k in NC) delete NC[k];
  $('#provSel').innerHTML = D.prov.slice().sort((a, b) => a.name.localeCompare(b.name, 'es')).map(p => `<option value="${p.id}" ${p.id === st.sel ? 'selected' : ''}>${esc(p.name)} (${p.seats})</option>`).join('');
  const win = j => { const s = S.cent[j], sh = S.centShare[j]; let b = 0; for (let i = 1; i < NPAR; i++) if (s[i] > s[b] || (s[i] === s[b] && sh[i] > sh[b])) b = i; return b };
  drawMap('#tiles', { sel: st.sel, group: 'Mapa de provincias', small: false,
    fill: (id, j) => { const w = win(j); return [`var(--c-${KEYS[w]})`, 0.42 + 0.58 * S.winCnt[j][w]] }, label: id => ABBR[id], dark: () => false,
    aria: (id, j) => `${D.prov[j].name}, ${PN[win(j)].name} lidera`, title: (id, j) => `${D.prov[j].name} · ${PN[win(j)].name} · ${Math.round(S.winCnt[j][win(j)] * 100)} %`,
    pick: id => { st.sel = id; provPage() } });
  const used = new Set(D.prov.map((p, j) => win(j)));
  $('#mleg').innerHTML = [...used].map(i => `<span><i style="background:var(--c-${KEYS[i]})"></i>${esc(PN[i].name)}</span>`).join('') + '<span>Más pálido = más disputada</span>';
  detail();
}
function detail() {
  const { S } = st, j = PI[st.sel], p = D.prov[j]; if (j === undefined) return;
  const row = S.centShare[j], base = p.sh, N = S.N;
  const ks = []; for (let k = 0; k < NPAR; k++) { const r = need(j, k); if (r.ok && (r.c > 0 || row[k] >= 0.01 || r.hs.p1 >= 0.02)) ks.push(k) }
  ks.sort((a, b) => row[b] - row[a]);
  const q = quotients(row, p.seats), lastW = q.filter(x => x.won).slice(-1)[0], firstO = q.find(x => !x.won);
  const qmax = q[0].q;
  const thr = Math.max(0.03, 1 / (p.seats + 1));
  $('#pd').innerHTML = `<h3>${esc(p.name)}</h3><div class="meta">${p.seats} ${p.seats === 1 ? 'escaño' : 'escaños'} · ${esc(D.regn[p.ccaa])} · ${nf(p.valid / 1e6, 2)} M de votos válidos en 2023</div>
  <div class="kpis"><div><b>${fmt(Math.max(0.03, 1 / (p.seats + 1)), 1)}</b><span>voto aproximado para sacar un escaño (el 3 % legal o 1/(escaños+1), el mayor)</span></div>
  <div><b>${esc(PN[lastW.k].name)}</b><span>se lleva el último escaño con un cociente de ${fmt(lastW.q)}</span></div>
  <div><b>${firstO ? esc(PN[firstO.k].name) : '–'}</b><span>primero fuera${firstO ? `, con ${fmt(firstO.q)}` : ''}</span></div></div>
  <div class="tw"><table class="pt mt prt"><thead><tr><th>Partido</th><th>2023</th><th>Voto est.</th><th>Escaños</th><th>Rango 90 %</th><th>Prob. ≥1</th><th>Necesita para el 1.º</th><th>Necesita para otro más</th></tr></thead><tbody>
  ${ks.map(k => { const r = need(j, k), d1 = r.share - r.n1, dn = r.nx === null ? null : r.nx - r.share, vot = d => Math.round(Math.abs(d) * p.valid / 100) * 100;
    return `<tr><td><button type="button" class="lk" data-party="${KEYS[k]}">${mark(KEYS[k])}${esc(PN[k].name)}</button></td><td class="num">${fmt(base[k])}</td><td class="num"><b>${fmt(row[k])}</b></td><td class="num s2">${r.c}</td><td class="num">${r.hs.lo}–${r.hs.hi}</td><td class="num">${r.hs.p1 >= 0.995 ? '>99 %' : r.hs.p1 < 0.005 ? '<1 %' : Math.round(r.hs.p1 * 100) + ' %'}</td>
    <td class="num need" title="Con el resto de partidos escalados en proporción">${fmt(r.n1)} <small class="${d1 >= 0 ? 'up' : 'dn'}">${pts(d1)}</small></td>
    <td class="num need" ${dn !== null ? `title="Unos ${nf(vot(dn))} votos más, aproximado con la participación de 2023"` : ''}>${dn === null ? '–' : `${fmt(r.nx)} <small class="dn">+${nf(dn * 100, 1)}</small>`}</td></tr>` }).join('')}
  </tbody></table></div>
  <p class="note" style="margin:10px 0 0">«Necesita» es el voto que tendría que sacar el partido en la provincia para llevarse ese escaño, con el resto de partidos escalados en proporción. La cifra pequeña es la distancia en puntos desde su voto estimado (verde si ya lo supera, rojo si le falta). Probabilidades y rangos salen de las ${nf(N)} simulaciones.</p>
  <h4 class="sh">Cómo se reparten los escaños</h4>
  <p class="note">Método D'Hondt: cada partido por encima del 3 % divide su voto entre 1, 2, 3…; los ${p.seats} cocientes más altos se llevan un escaño. En azul oscuro, los que ganan escaño; en trazo punteado, los dos primeros que se quedan fuera.</p>
  <div class="qs">${q.map(x => `<div class="qr ${x.won ? 'won' : 'out'}"><span class="qn">${x.n}</span><span class="qp">${mark(KEYS[x.k])}${esc(PN[x.k].name)} <small>÷${x.d}</small></span><span class="qb"><i style="width:${x.q / qmax * 100}%;background:var(--c-${KEYS[x.k]})"></i></span><span class="qv">${fmt(x.q)}</span></div>`).join('')}</div>`;
  $('#pd').querySelectorAll('[data-party]').forEach(b => b.onclick = () => { st.party = b.dataset.party; setTab('partidos') });
  const sel = $('#provSel'); if (sel) sel.value = st.sel;
}

/* ---- página de partidos ---- */
function partyPage() {
  const { S, A } = st, k = KI[st.party], key = KEYS[k];
  $('#pchips').innerHTML = PN.filter(p => PN.indexOf(p) < NPAR && (A.T[KI[p.k]] > 0)).sort((a, b) => S.seats[KI[b.k]].mean - S.seats[KI[a.k]].mean).map(p => `<button type="button" class="chip" data-k="${p.k}" aria-pressed="${p.k === st.party}" style="--c:var(--c-${p.k})"><i></i>${esc(p.name)} <small>${Math.round(S.seats[KI[p.k]].mean)}</small></button>`).join('');
  $('#pchips').querySelectorAll('.chip').forEach(c => c.onclick = () => { st.party = c.dataset.k; partyPage() });
  const si = seatsInt(), rows = [];
  for (let j = 0; j < NJ; j++) rows.push({ j, p: D.prov[j], r: need(j, k) });
  const con = rows.filter(x => x.r.c > 0).length, play = rows.filter(x => x.r.ok && x.r.hs.p1 >= 0.05 && x.r.hs.p1 < 0.95).length, ex = rows.filter(x => x.r.ok).length;
  const sh = S.share[k], sm = S.seats[k], seatsC = rows.reduce((a, x) => a + x.r.c, 0);
  $('#pk').innerHTML = `<div><b style="color:var(--c-${key})">${fmt(A.T[k])}</b><span>voto nacional estimado, entre ${fmt(sh.lo)} y ${fmt(sh.hi)}</span></div>
  <div><b>${si[k]}</b><span>escaños en la media de simulaciones, entre ${sm.lo} y ${sm.hi}</span></div>
  <div><b>${con}</b><span>provincias con escaño en el escenario central${ex < NJ ? ` de ${ex} donde se presenta` : ''}</span></div>
  <div><b>${play}</b><span>provincias en juego, con entre un 5 y un 95 % de probabilidad de escaño</span></div>`;
  const mode = st.pmode, maxS = Math.max(1, ...rows.map(x => x.r.c));
  const gap = x => x.r.ok ? x.r.share - x.r.n1 : -1;
  const fill = (id, j) => { const r = need(j, k); if (!r.ok) return ['var(--track)', 0.35];
    if (mode === 'seats') return r.c > 0 ? [`var(--c-${key})`, 0.32 + 0.68 * Math.sqrt(r.c / maxS)] : ['var(--track)', 1];
    const g = r.share - r.n1; return g >= 0 ? [`var(--c-${key})`, 0.92] : [`var(--c-${key})`, Math.max(0.08, 0.55 + g / 0.1 * 0.5)] };
  const label = (id, j) => { const r = need(j, k); if (!r.ok) return ''; if (mode === 'seats') return r.c > 0 ? String(r.c) : ''; return nf(r.n1 * 100, r.n1 * 100 >= 10 ? 0 : 1) };
  const dark = (id, j) => { const r = need(j, k); if (!r.ok) return true; if (mode === 'seats') return r.c === 0; return (r.share - r.n1) < -0.03 };
  drawMap('#pmap', { sel: null, group: `Mapa de escaños de ${PN[k].name} por provincia`, small: mode !== 'seats', fill, label, dark,
    aria: (id, j) => `${D.prov[j].name}: ${need(j, k).c} escaños`, title: (id, j) => { const r = need(j, k); return r.ok ? `${D.prov[j].name} · ${r.c} escaños · voto ${fmt(r.share)} · necesita ${fmt(r.n1)} para el primero` : `${D.prov[j].name} · no se presenta` },
    pick: id => { st.sel = id; setTab('provincias') } });
  $('#pmt').textContent = mode === 'seats' ? `Dónde saca escaño ${key === 'PP' || key === 'VOX' ? 'el' : 'el'} ${PN[k].name}`.replace('el PSOE', 'el PSOE') : `Voto que necesita ${PN[k].name} para su primer escaño`;
  $('#pmn').textContent = mode === 'seats' ? `El número es el escaño que consigue en el escenario central, ${seatsC} en total (la media de simulaciones da ${si[k]}). Más oscuro, más escaños. Pulsa una provincia para ver su detalle.` : 'El número es el % de voto provincial que haría falta para su primer escaño. Sólido: ya lo supera. Más claro: le falta voto, y cuanto más pálido, más lejos está.';
  $('#pleg').innerHTML = mode === 'seats' ? `<span><i style="background:var(--c-${key})"></i>Con escaño</span><span><i style="background:var(--track)"></i>Sin escaño o no se presenta</span>` : `<span><i style="background:var(--c-${key})"></i>Ya supera el mínimo</span><span><i style="background:var(--c-${key});opacity:.25"></i>Por debajo</span><span><i style="background:var(--track)"></i>No se presenta</span>`;
  // tabla
  const ord = st.psort, pr = rows.filter(x => x.r.ok);
  pr.sort((a, b) => ord === 'seats' ? (b.r.c - a.r.c || gap(b) - gap(a)) : ord === 'name' ? a.p.name.localeCompare(b.p.name, 'es') : gap(b) - gap(a));
  $('#psort').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', b.dataset.s === ord));
  $('#ptab').innerHTML = `<thead><tr><th>Provincia</th><th>Escaños</th><th>Voto est.</th><th>Necesita para el 1.º</th><th>Diferencia</th><th>Prob. ≥1</th></tr></thead><tbody>${pr.map(x => { const r = x.r, g = r.share - r.n1;
    return `<tr><td><button type="button" class="lk" data-prov="${x.p.id}">${esc(x.p.name)}</button> <small class="mut">${x.p.seats}</small></td><td class="num s2">${r.c || '·'}</td><td class="num">${fmt(r.share)}</td><td class="num">${fmt(r.n1)}</td><td class="num ${g >= 0 ? 'up' : 'dn'}">${pts(g)}</td><td class="num">${r.hs.p1 >= 0.995 ? '>99 %' : r.hs.p1 < 0.005 ? '<1 %' : Math.round(r.hs.p1 * 100) + ' %'}</td></tr>` }).join('')}</tbody>`;
  $('#ptab').querySelectorAll('[data-prov]').forEach(b => b.onclick = () => { st.sel = b.dataset.prov; setTab('provincias') });
  $('#pnote').textContent = ex < NJ ? `${PN[k].name} no aparece en las ${NJ - ex} provincias donde no se presentó en 2023.` : '';
}

/* ---- pestañas ---- */
const TABS = ['resumen', 'provincias', 'partidos', 'encuestas'];
function setTab(t, quiet) {
  if (!TABS.includes(t)) t = 'resumen'; st.tab = t;
  TABS.forEach(x => { const on = x === t, b = $('#tab-' + x); $('#p-' + x).hidden = !on; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1 });
  if (t === 'provincias') detail(); if (t === 'resumen' && st.A && st.S) chart();
  if (!quiet) { try { history.replaceState(null, '', '#' + t) } catch (e) { try { location.hash = t } catch (e2) { } } window.scrollTo({ top: 0 }) }
}
function bindPages() {
  TABS.forEach(t => { const b = $('#tab-' + t); b.onclick = () => setTab(t); b.onkeydown = e => { const i = TABS.indexOf(t); if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); const n = TABS[(i + (e.key === 'ArrowRight' ? 1 : TABS.length - 1)) % TABS.length]; setTab(n); $('#tab-' + n).focus() } } });
  $('#provSel').onchange = e => { st.sel = e.target.value; provPage() };
  document.querySelectorAll('input[name=pm]').forEach(r => r.onchange = () => { st.pmode = $('#pm1').checked ? 'need' : 'seats'; partyPage() });
  $('#psort').querySelectorAll('button').forEach(b => b.onclick = () => { st.psort = b.dataset.s; partyPage() });
  $('#tbl').addEventListener('click', e => { const r = e.target.closest('tr[data-k]'); if (r) { st.party = r.dataset.k; setTab('partidos') } });
}
