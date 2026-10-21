/* ===== Interfaz ===== */
const $ = s => document.querySelector(s), esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const fmt = (x, d = 1) => (x * 100).toLocaleString('es-ES', { minimumFractionDigits: d, maximumFractionDigits: d }) + '%';
const nf = (x, d = 0) => Number(x).toLocaleString('es-ES', { minimumFractionDigits: d, maximumFractionDigits: d });
const PN = D.parties, PNAME = {}; PN.forEach(p => PNAME[p.k] = p.name); PNAME.BLANCO = 'En blanco';
const dshort = s => new Date(s + 'T12:00:00Z').toLocaleDateString('es-ES', { day: 'numeric', month: 'short', timeZone: 'UTC' });
const st = { polls: seedPolls(), o: { ...DEFAULTS }, sel: '28', tab: 'resumen', party: 'PP', pmode: 'seats', psort: 'gap', series: new Set(['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS']), A: null, S: null };
const LS = 'pop29n-' + D.ver;
function load() { try { const s = JSON.parse(localStorage.getItem(LS)); if (s && s.polls && s.o) { st.polls = s.polls; Object.assign(st.o, s.o, { ref: DEFAULTS.ref }) } } catch (e) { } }
function save() { try { localStorage.setItem(LS, JSON.stringify({ polls: st.polls, o: st.o })) } catch (e) { } }

let timer = null;
function schedule(ms = 120) { clearTimeout(timer); $('#pill').textContent = 'Recalculando'; timer = setTimeout(() => { compute(); save() }, ms) }

function compute() {
  const A = aggregate(st.polls, st.o); st.A = A;
  if (!A) { $('#headline').textContent = 'Marca al menos una encuesta con datos completos'; $('#sub').textContent = ''; $('#pill').textContent = 'Sin datos'; return }
  st.S = simulate(A.T, st.o, A.Tsep);
  renderAll();
}
function renderAll() {
  const { A, S } = st; if (!A || !S) return;
  head(); votes(); chips(); chart(); seats(); groups(); provPage(); partyPage(); weights(); micro();
  $('#pill').textContent = 'Poll of polls · ' + new Date(st.o.ref + 'T12:00:00Z').toLocaleDateString('es-ES', { day: 'numeric', month: 'long', timeZone: 'UTC' });
}
function seatsInt() { return lr(st.S.seats.map(x => x.mean), 350) }
const FACNAME = 'Frente Amplio + confluencias', FACI = () => FACK.map(k => KI[k]);
const grp = () => !!st.o.group;
const dnm = i => (grp() && i === KI.SUMAR) ? FACNAME : PN[i].name;
const dk = k => (grp() && k === 'SUMAR') ? FACNAME : PNAME[k];
function view() {            // datos de la portada: con las confluencias agrupadas en la casilla de Frente Amplio, o tal cual
  const { A, S } = st, T = Array.from(A.T), sh = S.share.map(x => ({ ...x })), se = S.seats.map(x => ({ ...x })), rng = { ...A.rng };
  if (grp()) {
    const F = FACI(), z = { mean: 0, lo: 0, hi: 0, med: 0 };
    T[KI.SUMAR] = F.reduce((a, i) => a + A.T[i], 0); sh[KI.SUMAR] = { ...S.facShare }; se[KI.SUMAR] = { ...S.facSeats };
    F.forEach(i => { if (i !== KI.SUMAR) { T[i] = 0; sh[i] = { ...z }; se[i] = { ...z } } });
    const xs = A.act.map(r => facMain(r.vec, st.o, A.adel)); rng.SUMAR = [Math.min(...xs), Math.max(...xs)];
  }
  return { T, sh, se, rng, si: lr(se.map(x => x.mean), 350) };
}

function head() {
  const { A, S } = st, V = view(), si = V.si;
  const order = si.map((v, i) => i).sort((a, b) => V.se[b].mean - V.se[a].mean), a = order[0], b = order[1];
  $('#headline').textContent = `La media de encuestas da al ${dnm(a)} ${si[a]} escaños, ${si[a] - si[b]} más que ${KEYS[b] === 'PSOE' ? 'al ' : 'a '}${dnm(b)}`;
  const g = S.groups.find(x => x.id === 'pp_vox_der'), gs = S.groups.find(x => x.id === 'psoe_socios');
  const pt = p => p > 0.99 ? 'más del 99 %' : p < 0.01 ? 'menos del 1 %' : Math.round(p * 100) + ' %';
  const nm = A.act.filter(r => r.p.src === 'micro').length;
  $('#sub').innerHTML = `Media de <b>${A.act.length}</b> encuestas${nm ? ` (${nm} recalculadas desde microdatos)` : ''}, equivalentes a <b>${nf(A.nEff, 0)}</b> con el mismo peso. PP, Vox y derecha suman <b>${Math.round(g.mean)}</b> escaños y llegan a 176 en <b>${pt(g.p176)}</b> de las simulaciones; PSOE, Frente Amplio y socios, <b>${Math.round(gs.mean)}</b> y <b>${pt(gs.p176)}</b>. No es una predicción.`;
}

function votes() {
  const { A } = st, V = view(), S = { share: V.sh }, b = D.nat2023, mx = 0.4;
  const idx = PN.map((p, i) => i).filter(i => V.T[i] > 0.0005 || b[i] > 0.0005).sort((x, y) => V.T[y] - V.T[x]);
  $('#votes').innerHTML = idx.map(i => {
    const k = KEYS[i], m = S.share[i].mean, mg = (S.share[i].hi - S.share[i].lo) / 2, r = V.rng[k];
    const rg = r ? `<span class="rgw" style="left:${r[0] / mx * 100}%;width:${(r[1] - r[0]) / mx * 100}%"></span>` : '';
    return `<div class="prow"><div class="top"><span class="nm"><span class="sw" style="background:var(--c-${k})"></span>${esc(dnm(i))}</span><span class="pc">${fmt(V.T[i])}</span><span class="mg">±${nf(mg * 100, 1)}</span></div>
    <div class="bar"><i style="width:${V.T[i] / mx * 100}%;background:var(--c-${k})"></i>${rg}<s style="left:${b[i] / mx * 100}%"></s></div>
    <div class="ft">${r ? `Encuestas ${fmt(r[0])} a ${fmt(r[1])} · ` : ''}2023: ${fmt(b[i])}</div></div>`;
  }).join('');
}

function chips() {
  $('#chips').innerHTML = PN.filter(p => !['OTROS'].includes(p.k) && st.A.T[KI[p.k]] > 0 && !(grp() && FACK.includes(p.k) && p.k !== 'SUMAR')).map(p => `<button type="button" class="chip" data-k="${p.k}" aria-pressed="${st.series.has(p.k)}" style="--c:var(--c-${p.k})"><i></i>${esc(dk(p.k))}</button>`).join('');
  $('#chips').querySelectorAll('.chip').forEach(c => c.onclick = () => { const k = c.dataset.k; if (st.series.has(k)) { if (st.series.size > 1) st.series.delete(k) } else st.series.add(k); chips(); chart() });
}
function pval(r, k, o) { if (grp() && k === 'SUMAR') return facMain(r.vec, o, st.A.adel); if (k === 'SUMAR' || k === 'PODEMOS') return chartMain(r.vec, o)[k]; return r.vec[KI[k]] }
function chart() {
  const svg = $('#chart'), { A } = st, V = view(), S = { share: V.sh }, o = st.o, keys = [...st.series].filter(k => V.T[KI[k]] > 0 && !(grp() && FACK.includes(k) && k !== 'SUMAR'));
  const narrow = svg.parentElement.clientWidth < 560, W = narrow ? 480 : 640, H = narrow ? 400 : 560, m = { l: 40, r: narrow ? 14 : 150, t: 14, b: 30 };
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const CHW = 100, act = A.act.filter(r => dayNum(r.p.date) >= dayNum(o.ref) - CHW), ds = act.map(r => dayNum(r.p.date)), d0 = Math.min(...ds, dayNum(o.ref) - 20) - 1, d1 = dayNum(o.ref) + 1;
  const vals = []; keys.forEach(k => { act.forEach(r => { const x = pval(r, k, o); if (isFinite(x)) vals.push(x) }); vals.push(S.share[KI[k]].lo, S.share[KI[k]].hi) });
  let y0 = Math.floor((Math.min(...vals) - 0.004) * 50) / 50, y1 = Math.ceil((Math.max(...vals) + 0.006) * 50) / 50;
  const step = (y1 - y0) > 0.3 ? 0.1 : (y1 - y0) > 0.12 ? 0.05 : 0.02; y0 = Math.max(0, Math.floor(y0 / step) * step); y1 = Math.ceil(y1 / step) * step;
  const X = d => m.l + (d - d0) / (d1 - d0) * (W - m.l - m.r), Y = v => H - m.b - (v - y0) / (y1 - y0) * (H - m.t - m.b);
  let s = '';
  for (let v = y0; v <= y1 + 1e-9; v += step) s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--rule)"/><text x="${m.l - 7}" y="${Y(v) + 4}" text-anchor="end" font-size="11" fill="var(--muted)">${Math.round(v * 100)}%</text>`;
  const ticks = []; { const stp = (d1 - d0) > 60 ? 14 : 7; let first = Math.ceil(d0); while (new Date(first * MS).getUTCDay() !== 1) first++; for (let d = first; d <= d1; d += stp) ticks.push(d) }
  ticks.forEach(d => s += `<text x="${X(d)}" y="${H - m.b + 18}" text-anchor="middle" font-size="11" fill="var(--muted)">${new Date(d * MS).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', timeZone: 'UTC' })}</text>`);
  const labs = [];
  keys.forEach(k => {
    const i = KI[k], col = `var(--c-${k})`, tr = [];
    for (let d = d0; d <= d1 + 0.01; d += 0.5) { let sw = 0, sv = 0; act.forEach(r => { const x = pval(r, k, o); if (!isFinite(x)) return; const z = (dayNum(r.p.date) - d) / 9, w = r.p.q * Math.sqrt(Math.min(pollNeff(r.p, o), 2500)) * Math.exp(-z * z / 2); sw += w; sv += w * x }); if (sw > 3) tr.push(`${X(d).toFixed(1)},${Y(sv / sw).toFixed(1)}`) }
    if (tr.length > 1) s += `<polyline points="${tr.join(' ')}" fill="none" stroke="${col}" stroke-width="2.4" stroke-linejoin="round" opacity=".9"/>`;
    act.forEach(r => { const pv = pval(r, k, o); if (!isFinite(pv)) return; const rad = Math.min(8, 2.6 + 5 * Math.sqrt(r.share * A.act.length) / 2), x = X(dayNum(r.p.date)), y = Y(pv);
      const tip = `<title>${esc(r.p.name)} · ${dshort(r.p.date)}: ${fmt(pval(r, k, o))}</title>`;
      s += r.p.src === 'micro' ? `<rect x="${x - rad}" y="${y - rad}" width="${rad * 2}" height="${rad * 2}" fill="${col}" fill-opacity=".35" stroke="${col}" stroke-width="1.5">${tip}</rect>` : `<circle cx="${x}" cy="${y}" r="${rad}" fill="${col}" fill-opacity=".3" stroke="${col}" stroke-width="1.3">${tip}</circle>` });
    const lo = S.share[i].lo, hi = S.share[i].hi, x = X(d1);
    s += `<line x1="${x}" x2="${x}" y1="${Y(hi)}" y2="${Y(lo)}" stroke="${col}" stroke-width="3" opacity=".45"/><circle cx="${x}" cy="${Y(V.T[i])}" r="4.2" fill="${col}" stroke="var(--surface)" stroke-width="1.5"/>`;
    labs.push({ y: Y(V.T[i]), k, v: V.T[i] });
  });
  if (!narrow) {
    const L = labs.sort((a, b) => a.y - b.y); for (let n = 1; n < L.length; n++) if (L[n].y - L[n - 1].y < 14) L[n].y = L[n - 1].y + 14;
    const tx = W - m.r + 12; L.forEach(o => s += `<text x="${tx}" y="${o.y + 4}" font-size="11.5" font-weight="600" fill="var(--c-${o.k})">${esc(dk(o.k))} ${nf(o.v * 100, 1)}%</text>`);
  }
  svg.innerHTML = s;
}

function seats() {
  const V = view(), S = { seats: V.se }, si = V.si, b = D.seats2023;
  const seq = ['PODEMOS', 'SUMAR', 'UPC', 'COMPROMIS', 'ADELANTE', 'BILDU', 'BNG', 'ERC', 'PSOE', 'JUNTS', 'PNV', 'CC', 'PP', 'UPN', 'SALF', 'VOX'].map(k => KI[k]);
  const list = []; seq.forEach(i => { for (let n = 0; n < si[i]; n++) list.push(i) });
  const rows = 9, cx = 200, cy = 200, r0 = 82, R = 190, radii = [...Array(rows)].map((_, k) => r0 + (R - r0) * k / (rows - 1)), sr = radii.reduce((a, b) => a + b, 0);
  let cnt = radii.map(r => Math.round(350 * r / sr)); cnt[rows - 1] += 350 - cnt.reduce((a, b) => a + b, 0);
  const pts = []; radii.forEach((r, k) => { for (let j = 0; j < cnt[k]; j++) pts.push([Math.PI - Math.PI * (cnt[k] === 1 ? .5 : j / (cnt[k] - 1)), r]) });
  pts.sort((p, q) => q[0] - p[0] || p[1] - q[1]);
  $('#hemi').innerHTML = pts.map((p, n) => { const i = list[n]; return i === undefined ? '' : `<circle cx="${(cx + p[1] * Math.cos(p[0])).toFixed(1)}" cy="${(cy - p[1] * Math.sin(p[0])).toFixed(1)}" r="4.5" fill="var(--c-${KEYS[i]})"/>` }).join('');
  const idx = PN.map((p, i) => i).filter(i => i < NPAR && (si[i] > 0 || b[i] > 0 || S.seats[i].hi > 0)).sort((a, c) => S.seats[c].mean - S.seats[a].mean);
  $('#tbl tbody').innerHTML = idx.map(i => { const d = si[i] - b[i];
    return `<tr data-k="${KEYS[i]}" class="clk" title="Ver el detalle del partido"><td><span class="sw" style="background:var(--c-${KEYS[i]})"></span>${esc(dnm(i))}</td><td class="s">${si[i]}</td><td class="r">${S.seats[i].lo}–${S.seats[i].hi}</td><td class="d">${d > 0 ? '+' : d < 0 ? '−' : ''}${Math.abs(d) || '='}</td></tr>` }).join('');
}
function groups() {
  const { S } = st, V = view(), si = V.si, VW = 700, X0 = 2, SC = (VW - 4) / 350, xs = n => X0 + n * SC;
  $('#groups').innerHTML = S.groups.map(g => {
    const segs = [...new Set(g.parties.map(k => KI[k]))].filter(i => i !== undefined && si[i] > 0).map(i => ({ i, n: si[i] })).sort((a, b) => b.n - a.n);
    const tot = segs.reduce((a, x) => a + x.n, 0); let x = 0, rects = '', labels = ''; const rowEnd = [-1e9, -1e9];
    segs.forEach(sg => { const w = sg.n * SC, x1 = xs(x); rects += `<rect x="${x1.toFixed(1)}" y="40" width="${Math.max(w, 0.8).toFixed(1)}" height="26" fill="var(--c-${KEYS[sg.i]})" stroke="var(--surface)" stroke-width="1"><title>${esc(dnm(sg.i))}: ${sg.n}</title></rect>`;
      const big = w >= 34, fs = big ? 15 : 11, tw = String(sg.n).length * fs * 0.62, cxm = x1 + w / 2; let r = 0;
      if (cxm - tw / 2 < rowEnd[0] + 2) r = 1; if (r === 1 && cxm - tw / 2 < rowEnd[1] + 2) r = 2;
      const y = r === 0 ? 34 : r === 1 ? 21 : 8; if (r < 2) rowEnd[r] = cxm + tw / 2;
      labels += `<text x="${cxm.toFixed(1)}" y="${y}" text-anchor="middle" font-size="${fs}" font-weight="${big ? 700 : 600}" fill="var(--c-${KEYS[sg.i]})" stroke="var(--surface)" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round">${sg.n}</text>`; x += sg.n });
    const mx = xs(176), mark = `<line x1="${mx}" x2="${mx}" y1="4" y2="68" stroke="var(--ink)" stroke-width="1.5"/><text x="${mx + 5}" y="9" font-size="10.5" font-weight="600" fill="var(--ink)" letter-spacing=".04em">176 MAYORÍA ABSOLUTA</text>`;
    const p = g.p176, pt = p > 0.99 ? 'más del 99 %' : p < 0.01 ? 'menos del 1 %' : Math.round(p * 100) + ' %';
    return `<div class="grow"><div><div class="gt">${esc(g.label)}</div><div class="gs"><b>${tot}</b> escaños · rango 90 %: ${g.lo}–${g.hi} · llega a 176 en <b>${pt}</b></div></div>
    <svg class="gsvg" viewBox="0 0 ${VW} 70" role="img" aria-label="${esc(g.label)}: ${tot} escaños"><rect x="${X0}" y="40" width="${(350 * SC).toFixed(1)}" height="26" fill="var(--track)"/>${rects}${mark}${labels}</svg></div>` }).join('');
}

/* ---- tabla de encuestas ---- */
function pollRow(p) {
  const o = st.o, micro = p.src === 'micro', vec = pollVec(p, o), ok = !!vec;
  const cell = k => { const x = micro ? D.micro[p.mk][o.variant][KI[k]] : p.v[k];
    const sh = (x === undefined || x === null || x === '' || isNaN(x)) ? '' : nf(x * 100, 1);
    return micro ? `<td class="num ro">${p.regional ? '' : sh}</td>` : `<td><input class="in num" inputmode="decimal" data-id="${p.id}" data-k="${k}" value="${sh}" aria-label="${esc(p.name)} ${PNAME[k]}"></td>` };
  const note = p.note ? `<span class="pn">${esc(p.note)}</span>` : '';
  const warn = micro ? '' : `<span class="pn warn" ${ok ? 'hidden' : ''}>Faltan PP, PSOE, Vox, Frente Amplio o Podemos</span>`;
  return `<tr data-id="${p.id}" class="${p.include && ok ? '' : 'off'}"><td class="c"><input type="checkbox" data-id="${p.id}" data-f="include" ${p.include ? 'checked' : ''} ${p.regional ? 'disabled' : ''} aria-label="Usar ${esc(p.name)}"></td>
  <td class="nm2">${micro ? `<span class="mu" title="Recalculada desde microdatos">μ</span>` : `<input class="in txt" data-id="${p.id}" data-f="name" value="${esc(p.name)}" aria-label="Nombre">`}${micro ? esc(p.name) : ''}${note}${warn}</td>
  <td><input class="in" type="date" data-id="${p.id}" data-f="date" value="${p.date}" aria-label="Fecha ${esc(p.name)}"></td>
  <td>${micro ? `<span class="num ro">${nf(p.n)}</span>` : `<input class="in num" inputmode="numeric" data-id="${p.id}" data-f="n" value="${p.n}" aria-label="Muestra ${esc(p.name)}">`}</td>
  ${['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS', 'SALF', 'ADELANTE'].map(cell).join('')}
  <td><input class="in num q" inputmode="decimal" data-id="${p.id}" data-f="q" value="${String(p.q).replace('.', ',')}" aria-label="Calidad ${esc(p.name)}"></td>
  <td class="num pw" id="w-${p.id}">–</td>
  <td class="c">${micro ? '' : `<button type="button" class="x" data-del="${p.id}" aria-label="Quitar ${esc(p.name)}">×</button>`}</td></tr>`;
}
function renderTable() {
  const sorted = st.polls.slice().sort((a, b) => b.date.localeCompare(a.date));
  $('#pt tbody').innerHTML = sorted.map(pollRow).join('');
}
function houseTable() {
  const { A } = st, o = st.o, HE = A.HE || {}, hs = Object.values(HE).sort((a, b) => b.W - a.W), cols = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS'];
  const pts = x => { const t = nf(Math.abs(x) * 100, 1); return (Math.abs(x) * 100 < 0.05 ? '' : x > 0 ? '+' : '−') + t };
  $('#hnote').textContent = hs.length ? `Cuánto se desvía cada encuestadora de la media del resto, en puntos, encogido hacia cero según cuántas entregas y qué muestra tiene (con pocas encuestas el dato es sobre todo ruido) y centrado para que la suma entre encuestadoras sea cero (el sesgo común de todo el sector no se puede medir sin un resultado real). Se resta de sus datos antes de promediar${o.house < 1 ? ` con intensidad ${nf(o.house * 100, 0)} %` : ''}. Solo usa las encuestas publicadas; no mide el cambio de opinión en el tiempo, así que una casa que solo publicó hace semanas puede parecer más sesgada de lo que es.` : 'Hacen falta al menos tres encuestadoras activas para estimar efectos casa.';
  let h = `<thead><tr><th>Encuestadora</th><th>Encuestas</th>${cols.map(k => `<th>${esc(PNAME[k])}</th>`).join('')}</tr></thead><tbody>`;
  hs.forEach(x => { h += `<tr><td>${esc(x.name)}</td><td class="num">${x.n}</td>${cols.map(k => { const v = x.he[k]; return `<td class="num" title="Desviación bruta ${pts(x.raw[k])}">${pts(v)}</td>` }).join('')}</tr>` });
  $('#hft').innerHTML = hs.length ? h + '</tbody>' : '';
}
function weights() {
  const { A } = st; houseTable();
  A.rows.forEach(r => { const el = document.getElementById('w-' + r.p.id); if (el) el.textContent = r.ok ? nf(r.share * 100, 1) + '%' : '–'; const tr = el && el.closest('tr'); if (tr) { tr.classList.toggle('off', !r.ok); const w = tr.querySelector('.warn'); if (w) w.hidden = !!pollVec(r.p, st.o) } });
  $('#ptnote').textContent = `Peso = calidad × raíz de la muestra efectiva × 0,5^(días desde el trabajo de campo / ${st.o.half}). El CEO solo alimenta los factores de Cataluña.`;
}
$('#pt').addEventListener('input', e => {
  const t = e.target, id = t.dataset.id; if (!id) return; const p = st.polls.find(x => x.id === id); if (!p) return;
  const num = s => { const x = parseFloat(String(s).replace(',', '.')); return isFinite(x) ? x : NaN };
  if (t.dataset.k) { const x = num(t.value); if (isNaN(x)) delete p.v[t.dataset.k]; else p.v[t.dataset.k] = x / 100 }
  else if (t.dataset.f === 'n') p.n = Math.max(0, num(t.value) || 0);
  else if (t.dataset.f === 'q') p.q = Math.max(0, isNaN(num(t.value)) ? 0 : num(t.value));
  else if (t.dataset.f === 'name') p.name = t.value;
  else if (t.dataset.f === 'date') { if (t.value) p.date = t.value }
  schedule(350);
});
$('#pt').addEventListener('change', e => {
  const t = e.target, id = t.dataset.id; if (!id) return; const p = st.polls.find(x => x.id === id); if (!p) return;
  if (t.dataset.f === 'include') { p.include = t.checked; schedule(60) }
});
$('#pt').addEventListener('click', e => { const d = e.target.closest('[data-del]'); if (!d) return; st.polls = st.polls.filter(p => p.id !== d.dataset.del); renderTable(); schedule(30) });
$('#addp').onclick = () => { st.polls.unshift({ id: 'u' + Date.now(), name: 'Nueva encuesta', date: st.o.ref, n: 1000, v: {}, q: 1, include: false, src: 'pub', note: '' }); renderTable(); const f = $('#pt tbody tr input.txt'); if (f) { f.focus(); f.select() } schedule(30) };
$('#reset').onclick = () => { try { localStorage.removeItem(LS) } catch (e) { } st.polls = seedPolls(); st.o = { ...DEFAULTS }; sync(); renderTable(); schedule(30) };

/* ---- controles ---- */
function sync() {
  const o = st.o; $('#half').value = o.half; $('#halfv').textContent = o.half + ' d'; $('#variant').value = o.variant;
  $('#regInt').value = Math.round(o.regInt * 100); $('#regv').textContent = Math.round(o.regInt * 100) + '%';
  $('#g1').checked = !!o.group; $('#g0').checked = !o.group; $('#u0').checked = !o.unity; $('#u1').checked = !!o.unity; $('#nsim').value = String(o.nsim);
  $('#sdSys').value = o.sdSys; $('#sdSysv').textContent = nf(o.sdSys, 2); $('#sdProv').value = o.sdProv; $('#sdProvv').textContent = nf(o.sdProv * 100, 0) + '%';
  $('#house').value = o.house; $('#housev').textContent = o.house >= 1 ? 'Total' : o.house <= 0 ? 'Apagada' : nf(o.house * 100, 0) + ' %'; $('#lam').value = o.lam; $('#lamv').textContent = nf(o.lam, 2); $('#bonus').value = o.bonus; $('#bonusv').textContent = '×' + nf(o.bonus, 2); $('#bonusF').hidden = !o.unity;
}
function bind() {
  const o = st.o;
  $('#half').oninput = e => { o.half = +e.target.value; sync(); schedule() };
  $('#variant').onchange = e => { o.variant = e.target.value; renderTable(); schedule(30) };
  $('#regInt').oninput = e => { o.regInt = +e.target.value / 100; sync(); schedule() };
  document.querySelectorAll('input[name=grp]').forEach(r => r.onchange = () => { o.group = $('#g1').checked; sync(); renderAll(); save() });
  document.querySelectorAll('input[name=unity]').forEach(r => r.onchange = () => { o.unity = $('#u1').checked; sync(); schedule(30) });
  $('#nsim').onchange = e => { o.nsim = +e.target.value; schedule(30) };
  $('#sdSys').oninput = e => { o.sdSys = +e.target.value; sync(); schedule() };
  $('#sdProv').oninput = e => { o.sdProv = +e.target.value; sync(); schedule() };
  $('#house').oninput = e => { o.house = +e.target.value; sync(); schedule() };
  $('#lam').oninput = e => { o.lam = +e.target.value; sync(); schedule() };
  $('#bonus').oninput = e => { o.bonus = +e.target.value; sync(); schedule() };
}

/* ---- mapa genérico ---- */
const PI = {}; D.prov.forEach((p, j) => PI[p.id] = j);
function drawMap(target, cfg) {
  let h = '', selp = '';
  const attrs = (id, j) => `data-id="${id}" tabindex="0" role="button" aria-label="${esc(cfg.aria(id, j))}"`;
  Object.keys(MAP.paths).forEach(id => { const j = PI[id]; if (j === undefined) return; const [c, op] = cfg.fill(id, j);
    const p = `<path ${attrs(id, j)} class="${id === cfg.sel ? 'sel' : ''}" d="${MAP.paths[id]}" style="fill:${c};fill-opacity:${op.toFixed(2)}"><title>${esc(cfg.title(id, j))}</title></path>`;
    if (id === cfg.sel) selp = p; else h += p });
  let sqs = ''; Object.keys(MAP.sq).forEach(id => { const j = PI[id]; if (j === undefined) return; const [c, op] = cfg.fill(id, j), [x, y, s] = MAP.sq[id], l = cfg.label(id, j);
    sqs += `<rect ${attrs(id, j)} class="sqr${id === cfg.sel ? ' sel' : ''}" x="${x}" y="${y}" width="${s}" height="${s}" rx="4" style="fill:${c};fill-opacity:${op.toFixed(2)}"><title>${esc(cfg.title(id, j))}</title></rect>${l ? `<text class="ml ${cfg.dark(id, j) ? 'dk' : 'lt'} ${cfg.cls || ''}" x="${x + s / 2}" y="${y + s / 2}">${l}</text>` : ''}` });
  let tx = ''; Object.keys(MAP.lab).forEach(id => { const j = PI[id]; if (j === undefined) return; const l = cfg.label(id, j); if (l) tx += `<text class="ml ${cfg.dark(id, j) ? 'dk' : 'lt'} ${cfg.cls || ''}" x="${MAP.lab[id][0]}" y="${MAP.lab[id][1]}">${l}</text>` });
  const b = MAP.box;
  $(target).innerHTML = `<svg class="mapsvg" viewBox="0 0 ${MAP.w} ${MAP.h}" role="group" aria-label="${esc(cfg.group)}">${h}${selp}${tx}${sqs}<rect class="bx" x="${b[0]}" y="${b[1]}" width="${b[2] - b[0]}" height="${b[3] - b[1]}" rx="6"/><text class="bt" x="${b[0] + 8}" y="${b[1] + 16}">Canarias</text></svg>`;
  $(target).querySelectorAll('[data-id]').forEach(el => { const go = () => cfg.pick(el.dataset.id); el.onclick = go; el.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go() } } });
}
const pts = x => { const t = nf(Math.abs(x) * 100, 1); return (Math.abs(x) * 100 < 0.05 ? '' : x > 0 ? '+' : '−') + t };
const mark = (k, w) => `<span class="sw" style="background:var(--c-${k})"></span>`;
function present(j, k) {
  const p = D.prov[j], C = D.cfg, K = KEYS[k];
  if (K === 'PODEMOS') return st.A.T[k] > 0 && !C.regPodemosCoal.includes(p.ccaa);   // en Cataluña, C. Valenciana y Canarias va dentro de otras listas
  if (K === 'SUMAR') return p.ccaa !== '05' && p.sh[k] > 0;                           // en Canarias, dentro de Unidad del Pueblo Canario
  if (K === 'ADELANTE') return p.ccaa === '01';
  if (K === 'COMPROMIS') return p.ccaa === '10';
  if (K === 'UPC') return p.ccaa === '05';
  return p.sh[k] > 0 || (K === 'SALF' && st.A.T[k] > 0);
}
const NC = {};
function need(j, k) {
  const key = j + '_' + k; if (NC[key]) return NC[key];
  const { S } = st, row = S.centShare[j], seats = D.prov[j].seats, c = S.cent[j][k], share = row[k], ok = present(j, k) && st.A.T[k] > 0;
  const r = { ok, c, share, seats };
  if (ok) { r.n1 = needShare(row, k, seats, 1); r.nx = c + 1 <= seats ? needShare(row, k, seats, c + 1) : null; r.hs = histStats(S.hist[j][k], S.N) }
  return NC[key] = r;
}

function thrChart() {
  const { S } = st, svg = $('#thr'); if (!svg) return;
  const L = D.prov.map((p, j) => ({ p, j, e: effThreshold(S.centShare[j], p.seats, true) })).filter(x => x.e !== null && x.p.id !== '51' && x.p.id !== '52').map(x => ({ ...x, v: x.e }));
  L.sort((a, b) => a.v - b.v || b.p.seats - a.p.seats);
  const SHORT = { 'Santa Cruz de Tenerife': 'S.C. Tenerife', 'Castelló/Castellón': 'Castelló', 'Alacant/Alicante': 'Alicante', 'València/Valencia': 'València', 'Araba/Álava': 'Araba', 'Illes Balears': 'Baleares' }, nm = p => SHORT[p.name] || p.name;
  const n = L.length, W = Math.max(900, n * 26 + 66), H = 410, m = { l: 56, r: 10, t: 44, b: 96 };
  const top = Math.ceil(Math.max(...L.map(x => x.v)) * 20) / 20, Y = v => H - m.b - v / top * (H - m.t - m.b), bw = (W - m.l - m.r) / n;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.style.minWidth = W + 'px'; svg.style.width = '100%';
  let s = '';
  const st1 = top > 0.3 ? 0.1 : 0.05;
  for (let v = 0; v <= top + 1e-9; v += st1) s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--rule)"/><text x="${m.l - 7}" y="${Y(v) + 4}" text-anchor="end" font-size="11" fill="var(--muted)">${Math.round(v * 100)}%</text>`;
  L.forEach((x, i) => {
    const cx = m.l + bw * (i + .5), h = Y(0) - Y(x.v), sel = x.p.id === st.sel, atFloor = x.e <= 0.03;
    s += `<g data-id="${x.p.id}" class="thrb" tabindex="0" role="button" aria-label="${esc(x.p.name)}: ${x.p.seats} escaños, barrera efectiva ${fmt(x.v)}"><title>${esc(x.p.name)} · ${x.p.seats} escaños · barrera efectiva ${fmt(x.v)}${atFloor ? ' (manda el 3 % legal)' : ''}</title>
      <rect x="${cx - bw * .36}" y="${Y(x.v)}" width="${bw * .72}" height="${h}" rx="2" fill="${atFloor ? 'var(--faint)' : 'var(--focus)'}" fill-opacity="${sel ? 1 : .72}"${sel ? ' stroke="var(--ink)" stroke-width="1.5"' : ''}/>
      <rect x="${cx - bw / 2}" y="${m.t - 16}" width="${bw}" height="${H - m.t - m.b + 16 + 90}" fill="transparent"/>
      <text x="${cx}" y="${m.t - 20}" text-anchor="middle" font-size="12.5" font-weight="700" fill="var(--ink)">${x.p.seats}</text><text x="${cx}" y="${Y(x.v) - 5}" text-anchor="middle" font-size="10" fill="var(--ink)" stroke="var(--surface)" stroke-width="3" paint-order="stroke" pointer-events="none">${nf(x.v * 100, 1)}</text>
      <text transform="translate(${cx + 4},${H - m.b + 10}) rotate(-60)" text-anchor="end" font-size="11" fill="var(--muted)">${esc(nm(x.p))}</text></g>`;
  });
  s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(0.03)}" y2="${Y(0.03)}" stroke="var(--ink)" stroke-width="1.4" stroke-dasharray="2 4" stroke-linecap="round" pointer-events="none"/><text x="${W - m.r}" y="${Y(0.03) - 5}" text-anchor="end" font-size="10.5" fill="var(--ink)" pointer-events="none">Umbral legal 3 %</text><text x="${m.l - 7}" y="${m.t - 22}" text-anchor="end" font-size="10.5" fill="var(--muted)">Escaños</text>`;
  svg.innerHTML = s;
  svg.querySelectorAll('.thrb').forEach(g => { const go = () => { st.sel = g.dataset.id; provPage(); window.scrollTo({ top: 0 }) }; g.onclick = go; g.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go() } } });
}

/* ---- página de provincias ---- */
function provPage() {
  const { S } = st;
  for (const k in NC) delete NC[k];
  $('#provSel').innerHTML = D.prov.slice().sort((a, b) => a.name.localeCompare(b.name, 'es')).map(p => `<option value="${p.id}" ${p.id === st.sel ? 'selected' : ''}>${esc(p.name)} (${p.seats})</option>`).join('');
  const win = j => { const s = S.cent[j], sh = S.centShare[j]; let b = 0; for (let i = 1; i < NPAR; i++) if (s[i] > s[b] || (s[i] === s[b] && sh[i] > sh[b])) b = i; return b };
  drawMap('#tiles', { sel: st.sel, group: 'Mapa de provincias', cls: '',
    fill: (id, j) => { const w = win(j); return [`var(--c-${KEYS[w]})`, 0.42 + 0.58 * S.winCnt[j][w]] }, label: id => ABBR[id], dark: () => false,
    aria: (id, j) => `${D.prov[j].name}, ${PN[win(j)].name} lidera`, title: (id, j) => `${D.prov[j].name} · ${PN[win(j)].name} · ${Math.round(S.winCnt[j][win(j)] * 100)} %`,
    pick: id => { st.sel = id; provPage() } });
  const used = new Set(D.prov.map((p, j) => win(j)));
  $('#mleg').innerHTML = [...used].map(i => `<span><i style="background:var(--c-${KEYS[i]})"></i>${esc(PN[i].name)}</span>`).join('') + '<span>Más pálido = más disputada</span>';
  detail(); thrChart();
}
function detail() {
  const { S } = st, j = PI[st.sel], p = D.prov[j]; if (j === undefined) return;
  const row = S.centShare[j], base = p.sh, N = S.N;
  const ks = []; for (let k = 0; k < NPAR; k++) { const r = need(j, k); if (r.ok && (r.c > 0 || row[k] >= 0.01 || r.hs.p1 >= 0.02)) ks.push(k) }
  ks.sort((a, b) => row[b] - row[a]);
  const q = quotients(row, p.seats), lastW = q.filter(x => x.won).slice(-1)[0], firstO = q.find(x => !x.won);
  const qmax = q[0].q, qshow = p.seats > 12 ? q.filter(x => x.n > p.seats - 10) : q;
  const thr = Math.max(0.03, 1 / (p.seats + 1));
  $('#pd').innerHTML = `<h3>${esc(p.name)}</h3><div class="meta">${p.seats} ${p.seats === 1 ? 'escaño' : 'escaños'} · ${esc(D.regn[p.ccaa])} · ${nf(p.valid / 1e6, 2)} M de votos válidos en 2023</div>
  <div class="kpis"><div><b>${fmt(Math.max(0.03, 1 / (p.seats + 1)), 1)}</b><span>voto aproximado para sacar un escaño (el 3 % legal o 1/(escaños+1), el mayor)</span></div>
  <div><b>${esc(PN[lastW.k].name)}</b><span>se lleva el último escaño con un cociente de ${fmt(lastW.q)}</span></div>
  <div><b>${firstO ? esc(PN[firstO.k].name) : '–'}</b><span>primero fuera${firstO ? `, con ${fmt(firstO.q)}` : ''}</span></div></div>
  <div class="tw"><table class="pt mt prt"><thead><tr><th>Partido</th><th>2023</th><th>Voto est.</th><th>Escaños</th><th>Rango 90 %</th><th>Prob. ≥1</th><th>Para el 1.º</th><th>Para otro más</th></tr></thead><tbody>
  ${ks.map(k => { const r = need(j, k), d1 = r.share - r.n1, dn = r.nx === null ? null : r.nx - r.share, vot = d => Math.round(Math.abs(d) * p.valid / 100) * 100;
    return `<tr><td><button type="button" class="lk" data-party="${KEYS[k]}">${mark(KEYS[k])}${esc(PN[k].name)}</button></td><td class="num">${fmt(base[k])}</td><td class="num"><b>${fmt(row[k])}</b></td><td class="num s2">${r.c}</td><td class="num">${r.hs.lo}–${r.hs.hi}</td><td class="num">${r.hs.p1 >= 0.995 ? '>99 %' : r.hs.p1 < 0.005 ? '<1 %' : Math.round(r.hs.p1 * 100) + ' %'}</td>
    <td class="num need" title="Con el resto de partidos escalados en proporción">${fmt(r.n1)} <small class="${d1 >= 0 ? 'gd' : 'bd'}">${pts(d1)}</small></td>
    <td class="num need" ${dn !== null ? `title="Unos ${nf(vot(dn))} votos más, aproximado con la participación de 2023"` : ''}>${dn === null ? '–' : `${fmt(r.nx)} <small class="bd">+${nf(dn * 100, 1)}</small>`}</td></tr>` }).join('')}
  </tbody></table></div>
  <p class="note" style="margin:10px 0 0">«Necesita» es el voto que tendría que sacar el partido en la provincia para llevarse ese escaño, con el resto de partidos escalados en proporción. La cifra pequeña es la distancia en puntos desde su voto estimado (verde si ya lo supera, rojo si le falta). Probabilidades y rangos salen de las ${nf(N)} simulaciones.</p>
  <h4 class="sh">Cómo se reparten los escaños</h4>
  <p class="note">Método D'Hondt: cada partido por encima del 3 % divide su voto entre 1, 2, 3…; los ${p.seats} cocientes más altos se llevan un escaño. Las barras sólidas ganan escaño; las de trazo punteado son los primeros que se quedan fuera.${p.seats > 12 ? ' Aquí se muestran solo los últimos diez escaños repartidos y los que se quedan a las puertas.' : ''}</p>
  <div class="qs">${qshow.map(x => `<div class="qr ${x.won ? 'won' : 'out'}"><span class="qn">${x.n}</span><span class="qp">${mark(KEYS[x.k])}${esc(PN[x.k].name)} <small>÷${x.d}</small></span><span class="qb"><i style="width:${x.q / qmax * 100}%;background:var(--c-${KEYS[x.k]})"></i></span><span class="qv">${fmt(x.q)}</span></div>`).join('')}</div>`;
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
    if (mode === 'seats') return r.c > 0 ? [`var(--c-${key})`, 0.32 + 0.68 * Math.sqrt(r.c / maxS)] : r.hs.p1 >= 0.25 ? [`var(--c-${key})`, 0.12 + 0.2 * r.hs.p1] : ['var(--track)', 1];
    const g = r.share - r.n1; return g >= 0 ? [`var(--c-${key})`, 0.92] : [`var(--c-${key})`, Math.max(0.08, 0.55 + g / 0.1 * 0.5)] };
  const label = (id, j) => { const r = need(j, k); if (!r.ok) return ''; if (mode === 'seats') return r.c > 0 ? String(r.c) : r.hs.p1 >= 0.25 ? Math.round(r.hs.p1 * 100) + '%' : ''; return nf(r.n1 * 100, r.n1 * 100 >= 10 ? 0 : 1) };
  const dark = (id, j) => { const r = need(j, k); if (!r.ok) return true; if (mode === 'seats') return r.c === 0; return (r.share - r.n1) < -0.03 };
  drawMap('#pmap', { sel: null, group: `Mapa de escaños de ${PN[k].name} por provincia`, cls: mode === 'seats' ? 'lg' : 'sm', fill, label, dark,
    aria: (id, j) => `${D.prov[j].name}: ${need(j, k).c} escaños`, title: (id, j) => { const r = need(j, k); return r.ok ? `${D.prov[j].name} · ${r.c} escaños · voto ${fmt(r.share)} · necesita ${fmt(r.n1)} para el primero` : `${D.prov[j].name} · no se presenta` },
    pick: id => { st.sel = id; setTab('provincias') } });
  $('#pmt').textContent = mode === 'seats' ? `Dónde saca escaño ${PN[k].name}` : `Voto que necesita ${PN[k].name} para su primer escaño`;
  $('#pmn').textContent = mode === 'seats' ? `El número es el escaño que consigue en el escenario central, ${seatsC} en total (la media de simulaciones da ${si[k]}). Más oscuro, más escaños. Un % en tono claro es una provincia sin escaño en el escenario central pero con esa probabilidad de sacarlo (por eso la media de simulaciones puede superar al escenario central). Pulsa una provincia para ver su detalle.` : 'El número es el % de voto provincial que haría falta para su primer escaño. Sólido: ya lo supera. Más claro: le falta voto, y cuanto más pálido, más lejos está.';
  $('#pleg').innerHTML = mode === 'seats' ? `<span><i style="background:var(--c-${key})"></i>Con escaño</span><span><i style="background:var(--c-${key});opacity:.25"></i>Sin escaño central, con probabilidad ≥ 25 %</span><span><i style="background:var(--track)"></i>Sin escaño o no se presenta</span>` : `<span><i style="background:var(--c-${key})"></i>Ya supera el mínimo</span><span><i style="background:var(--c-${key});opacity:.25"></i>Por debajo</span><span><i style="background:var(--track)"></i>No se presenta</span>`;
  // tabla
  const ord = st.psort, pr = rows.filter(x => x.r.ok);
  pr.sort((a, b) => ord === 'seats' ? (b.r.c - a.r.c || gap(b) - gap(a)) : ord === 'name' ? a.p.name.localeCompare(b.p.name, 'es') : gap(b) - gap(a));
  $('#psort').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', b.dataset.s === ord));
  $('#ptab').innerHTML = `<thead><tr><th>Provincia</th><th>Esc.</th><th>Voto est.</th><th title="Voto necesario para el primer escaño">Necesita</th><th title="Voto estimado menos voto necesario, en puntos">Dif.</th><th title="Probabilidad de al menos un escaño">Prob. ≥1</th></tr></thead><tbody>${pr.map(x => { const r = x.r, g = r.share - r.n1;
    return `<tr><td><button type="button" class="lk" data-prov="${x.p.id}">${esc(x.p.name)}</button> <small class="mut">${x.p.seats}</small></td><td class="num s2">${r.c || '·'}</td><td class="num">${fmt(r.share)}</td><td class="num">${fmt(r.n1)}</td><td class="num ${g >= 0 ? 'gd' : 'bd'}">${pts(g)}</td><td class="num">${r.hs.p1 >= 0.995 ? '>99 %' : r.hs.p1 < 0.005 ? '<1 %' : Math.round(r.hs.p1 * 100) + ' %'}</td></tr>` }).join('')}</tbody>`;
  $('#ptab').querySelectorAll('[data-prov]').forEach(b => b.onclick = () => { st.sel = b.dataset.prov; setTab('provincias') });
  $('#pnote').textContent = ex < NJ ? `${PN[k].name} no se presenta en las ${NJ - ex} provincias restantes.` : '';
}

/* ---- pestañas ---- */
const TABS = ['resumen', 'provincias', 'partidos', 'encuestas'];
function setTab(t, quiet) {
  if (!TABS.includes(t)) t = 'resumen'; st.tab = t;
  TABS.forEach(x => { const on = x === t, b = $('#tab-' + x); $('#p-' + x).hidden = !on; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1 });
  if (st.A && st.S) { if (t === 'provincias') detail(); if (t === 'resumen') chart() }
  if (!quiet) { try { history.replaceState(null, '', '#' + t) } catch (e) { try { location.hash = t } catch (e2) { } } window.scrollTo({ top: 0 }) }
}
function bindPages() {
  TABS.forEach(t => { const b = $('#tab-' + t); b.onclick = () => setTab(t); b.onkeydown = e => { const i = TABS.indexOf(t); if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); const n = TABS[(i + (e.key === 'ArrowRight' ? 1 : TABS.length - 1)) % TABS.length]; setTab(n); $('#tab-' + n).focus() } } });
  $('#provSel').onchange = e => { st.sel = e.target.value; provPage() };
  document.querySelectorAll('input[name=pm]').forEach(r => r.onchange = () => { st.pmode = $('#pm1').checked ? 'need' : 'seats'; partyPage() });
  $('#psort').querySelectorAll('button').forEach(b => b.onclick = () => { st.psort = b.dataset.s; partyPage() });
  $('#tbl').addEventListener('click', e => { const r = e.target.closest('tr[data-k]'); if (r) { st.party = r.dataset.k; setTab('partidos') } });
}

/* ---- microdatos ---- */
function micro() {
  const mm = D.micro, o = st.o, nm = k => nf(k * 100, 1);
  const cols = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS', 'SALF', 'ADELANTE'];
  const row = (lab, v, cls) => `<tr class="${cls || ''}"><td>${lab}</td>${cols.map(k => `<td class="num">${v[k] === undefined ? '–' : nm(v[k])}</td>`).join('')}<td class="num">${v.R === undefined ? '–' : nm(v.R)}</td></tr>`;
  const vv = arr => { const v = {}; cols.forEach(k => v[k] = arr[KI[k]]); v.R = 1 - cols.reduce((a, k) => a + arr[KI[k]], 0); return v };
  const pub = (pp, ps, vx, su, po, sa) => { const v = { PP: pp / 100, PSOE: ps / 100, VOX: vx / 100 }; if (su !== undefined) { v.SUMAR = su / 100; v.PODEMOS = po / 100; v.SALF = sa / 100; v.R = 1 - (pp + ps + vx + su + po + sa) / 100 } return v };
  let h = `<thead><tr><th>Encuesta y método</th>${cols.map(k => `<th>${esc(PNAME[k])}</th>`).join('')}<th>Resto</th></tr></thead><tbody>`;
  h += `<tr class="grp"><td colspan="9">CIS 3577 · ${nf(mm.cis.n)} entrevistas</td></tr>` + row('Publicada por el CIS', pub(25.5, 31.0, 16.6)) + row('Bruta (voto + simpatía)', vv(mm.cis.A)) + row('Reponderada por recuerdo', vv(mm.cis.B), o.variant === 'B' ? 'sel' : '') + row('Reponderada + indecisos', vv(mm.cis.C), o.variant === 'C' ? 'sel' : '');
  h += `<tr class="grp"><td colspan="9">40dB flash, 7-8 oct · ${nf(mm.d40.n)} entrevistas</td></tr>` + row('Publicada por 40dB', pub(31.9, 28.1, 18.9, 5.3, 2.3, 1.8)) + row('Bruta (intención + afinidad)', vv(mm.d40.A)) + row('Reponderada por recuerdo', vv(mm.d40.B), o.variant === 'B' ? 'sel' : '') + row('Reponderada + indecisos', vv(mm.d40.C), o.variant === 'C' ? 'sel' : '');
  h += `</tbody>`; $('#mt').innerHTML = h;
  // nueva configuración de candidaturas: dónde se integra el voto de Podemos y del espacio ex-Sumar
  const C = D.cfg, tf = st.A.tf, pts = x => nf(x * 100, 1);
  const pr = [['09', 'cat', 'ERC (Cataluña)', tf.podCat], ['10', 'cv', 'Compromís-Front Valencià', tf.podCV], ['05', 'can', 'Unidad del Pueblo Canario', tf.podCan]];
  let z = `<thead><tr><th>Dónde está el voto de Podemos</th><th>CIS 3577</th><th>40dB flash</th><th>Usado</th><th>Puntos de voto en la media</th></tr></thead><tbody>`;
  z += pr.map(([rg, c, lab, pt]) => `<tr><td>Se integra en ${esc(lab)}</td><td class="num">${pts(C.locPodemosCIS[rg])} %</td><td class="num">${pts(C.locPodemos40[rg])} %</td><td class="num">${pts(C.fPod[c])} %</td><td class="num">${nf(pt * 100, 2)}</td></tr>`).join('');
  const sepU = 1 - C.fPod.cat - C.fPod.cv - C.fPod.can;
  z += `<tr class="sel"><td>Concurre por separado (resto de España)</td><td class="num">${pts(1 - pr.reduce((a, x) => a + C.locPodemosCIS[x[0]], 0))} %</td><td class="num">${pts(1 - pr.reduce((a, x) => a + C.locPodemos40[x[0]], 0))} %</td><td class="num">${pts(sepU)} %</td><td class="num">${nf(st.A.T[KI.PODEMOS] * 100, 2)}</td></tr></tbody>`;
  $('#pz').innerHTML = z;
  $('#pzn').textContent = `Porcentaje de los votantes de Podemos que viven en cada comunidad, medido en CIS y 40dB (reponderado). El valor usado mezcla a partes iguales las dos encuestas y el reparto del voto Sumar de 2023, porque la muestra de Podemos por comunidad es corta. Los votantes de Cataluña, la Comunitat Valenciana y Canarias se suman a ERC, Compromís-Front Valencià y Unidad del Pueblo Canario. El espacio ex-Sumar pasa en parte a Compromís (${pts(C.wFA.cv)} % de su voto, un ${pts(C.kc)} % del que tenía en la Comunitat Valenciana) y a Unidad del Pueblo Canario (${pts(C.wFA.can)} %), que sustituye a Frente Amplio en Canarias.`;
  // CEO + fidelidad
  const ck = ['PSOE', 'PP', 'VOX', 'SUMAR', 'ERC', 'JUNTS'];
  const crow = (lab, arr, cls) => `<tr class="${cls || ''}"><td>${lab}</td>${ck.map(k => `<td class="num">${nm(arr[KI[k]])}</td>`).join('')}</tr>`;
  const cn = `<p class="note" style="margin:14px 0 6px">Cataluña, voto al Congreso. El CEO (${nf(mm.ceo.n)} entrevistas, 1 sep a 1 oct) y el CIS refuerzan el ajuste regional de la comunidad.</p><div class="tw"><table class="pt mt"><thead><tr><th>Cataluña</th>${ck.map(k => `<th>${k === 'PSOE' ? 'PSC' : esc(PNAME[k])}</th>`).join('')}</tr></thead><tbody>${crow('Resultado de 2023', D.cat2023)}${crow('CEO bruto', mm.ceo.A)}${crow('CEO reponderado', mm.ceo.B, 'sel')}</tbody></table></div>`;
  $('#cat').innerHTML = cn;
  const tr = mm.cis.trans, order = ['PP', 'PSOE', 'VOX', 'SUMAR', 'ERC', 'JUNTS'];
  let r = `<thead><tr><th>Votó en 2023</th><th>Repite</th><th>Se va a</th></tr></thead><tbody>`;
  order.forEach(k => { const t = tr[k]; if (!t) return; const rep = t[k] || 0, oth = Object.entries(t).filter(([q, v]) => q !== k && v >= 0.012).sort((a, b) => b[1] - a[1]).slice(0, 3);
    r += `<tr><td><span class="sw" style="background:var(--c-${k})"></span>${esc(PNAME[k])}</td><td class="num">${nm(rep)}</td><td class="to">${oth.map(([q, v]) => `${esc(PNAME[q])} ${nm(v)}`).join(' · ') || '–'}</td></tr>` });
  $('#rt').innerHTML = r + '</tbody>';
  // factores regionales
  const fk = ['PP', 'PSOE', 'VOX', 'SUMAR', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC'];
  let f = `<thead><tr><th>Comunidad</th><th>Muestra CIS</th>${fk.map(k => `<th>${esc(PNAME[k])}</th>`).join('')}</tr></thead><tbody>`;
  Object.keys(D.regn).forEach(rg => { const fr = D.fac[rg] || {}, nn = D.nreg[rg];
    f += `<tr><td>${esc(D.regn[rg])}</td><td class="num">${nf(nn[0])}</td>${fk.map(k => { const e = fr[k]; if (!e) return '<td class="num">·</td>'; const m = Math.pow(e.f, o.regInt), c = m > 1.04 ? 'up' : m < 0.96 ? 'dn' : ''; return `<td class="num ${c}">${nf(m, 2)}</td>` }).join('')}</tr>` });
  $('#ft').innerHTML = f + '</tbody>';
}

load(); sync(); bind(); bindPages(); renderTable(); (function () { let t = ''; try { t = location.hash.replace('#', '') } catch (e) { } setTab(t, true) })();
window.addEventListener('resize', () => { if (st.S) chart() });
setTimeout(compute, 20);
