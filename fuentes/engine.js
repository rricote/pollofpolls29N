/* ===== Motor del poll of polls ===== */
const KEYS = D.keys, NK = KEYS.length, KI = {};
KEYS.forEach((k, i) => KI[k] = i);
const NPAR = 16;                       // partidos que compiten por escaño (0..15); 16 = OTROS, 17 = BLANCO
const MAIN5 = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS'];
let UNITY_R = 0;
/* parte del Frente Amplio restante que vive en comunidades donde Podemos ya va dentro de otras listas (Cataluña, C. Valenciana, Canarias): ahí la unidad no aplica y no hay bonus */
let _CS = null;
function coalShare() {
  if (_CS !== null) return _CS;
  const C = D.cfg; let a = 0, b = 0;
  D.prov.forEach(p => { const w = p.valid * p.sh[KI.SUMAR] * (p.ccaa === '05' ? 0 : p.ccaa === '10' ? 1 - C.kc : 1); b += w; if (C.regPodemosCoal.includes(p.ccaa)) a += w });
  return _CS = b > 0 ? a / b : 0;
}
const FACK = ['SUMAR', 'COMPROMIS', 'UPC', 'ADELANTE'];   // Frente Amplio + confluencias
const BLOCK = ['ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'UPN'];
const NATIVE = KEYS.map((k, i) => i);
const MS = 864e5;
const dayNum = s => Date.parse(s + 'T12:00:00Z') / MS;

function mulberry(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; } }
function normal(r) { let u = 0, v = 0; while (u === 0) u = r(); v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

/* ---- vector de cada encuesta ---- */
function pollVec(p, o) {
  if (p.src === 'micro') return D.micro[p.mk][o.variant].slice();
  const v = new Array(NK).fill(NaN);
  for (const k in p.v) { const x = +p.v[k]; if (isFinite(x) && p.v[k] !== '' && p.v[k] !== null) v[KI[k]] = x; }
  return MAIN5.every(k => isFinite(v[KI[k]])) ? v : null;
}
function pollNeff(p, o) {
  if (p.src === 'micro') return D.micro[p.mk][o.variant === 'A' ? 'nA' : 'nB'];
  return Math.max(1, +p.n || 0) / 1.4;
}
function pollWeight(p, o) {
  const age = Math.max(0, dayNum(o.ref) - dayNum(p.date));
  return (+p.q || 0) * Math.sqrt(Math.min(pollNeff(p, o), 2500)) * Math.pow(0.5, age / o.half);
}

/* ---- efecto casa: desviación media de cada encuestadora respecto al consenso del resto en la misma fecha, encogida (bayesiana) y centrada ---- */
const houseKey = p => p.src === 'micro' ? null : String(p.name || '').split(/\s*[\/(]/)[0].normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase() || null;
const HOUSE_TAU = 0.06;   // dispersión relativa a priori de los efectos casa (6 % del % de cada partido)
const HOUSE_BW = 16;      // ventana (días) con la que se construye el consenso en la fecha de cada encuesta
function houseEffects(act, o) {
  const pub = act.filter(r => r.hk), groups = {};
  pub.forEach(r => (groups[r.hk] = groups[r.hk] || []).push(r));
  const out = {}, names = Object.keys(groups);
  if (names.length < 3) return out;
  const dn = r => dayNum(r.p.date), qn = r => (+r.p.q || 0) * Math.sqrt(Math.min(pollNeff(r.p, o), 2500));
  names.forEach(h => {
    const mine = groups[h], oth = pub.filter(r => r.hk !== h);
    const acc = {}, raw = {}, he = {}; let Wm = 0, ne = 0, used = 0;
    MAIN5.forEach(k => acc[k] = { s: 0, w: 0, v: 0 });
    mine.forEach(r => {
      let sw = 0; const cs = new Array(MAIN5.length).fill(0);
      oth.forEach(x => { const z = (dn(x) - dn(r)) / HOUSE_BW, w = qn(x) * Math.exp(-z * z / 2); if (w < 1e-9) return; sw += w; MAIN5.forEach((k, i) => cs[i] += w * x.vec[KI[k]]) });
      if (sw < 1.5 * qn(r)) return;               // sin consenso suficiente en esa fecha
      const wr = qn(r); used++; Wm += wr; ne += pollNeff(r.p, o);
      MAIN5.forEach((k, i) => { const cons = cs[i] / sw, a = acc[k]; a.s += wr * (r.vec[KI[k]] - cons); a.w += wr; a.v += wr * cons });
    });
    if (!used) return;
    MAIN5.forEach(k => {
      const a = acc[k], d = a.s / a.w, cons = a.v / a.w, pq = cons * (1 - cons), nv = pq / ne + pq / 4000, tv = Math.pow(HOUSE_TAU * cons, 2);
      raw[k] = d; he[k] = d * tv / (tv + nv);
    });
    out[h] = { name: mine[0].p.name.split(/\s*[\/(]/)[0].trim(), n: mine.length, used, W: Wm, he, raw };
  });
  const ks = Object.keys(out); if (ks.length < 3) return {};
  // centrar: la media simple de los efectos entre encuestadoras es cero (cada casa cuenta igual; el sesgo medio del sector no se puede medir sin un resultado real)
  MAIN5.forEach(k => { const m = ks.reduce((a, h) => a + out[h].he[k], 0) / ks.length; ks.forEach(h => out[h].he[k] -= m) });
  return out;
}

/* ---- agregación: media ponderada de encuestas ---- */
function aggregate(polls, o) {
  const rows = [], b = D.nat2023;
  let W = 0; const m5 = new Array(5).fill(0); let sS = 0, sW = 0;
  polls.forEach(p => {
    const r = { p, vec: null, w: 0, ok: false };
    rows.push(r);
    if (!p.include || p.regional) return;
    const v = pollVec(p, o); if (!v) return;
    r.vec = v; r.w = pollWeight(p, o); r.ok = r.w > 0; r.hk = houseKey(p);
  });
  const act = rows.filter(r => r.ok);
  if (!act.length) return null;
  const HE = o.house > 0 ? houseEffects(act, o) : {};
  act.forEach(r => { r.raw = r.vec; r.he = null; const h = HE[r.hk]; if (h) { r.vec = r.vec.slice(); r.he = h.he; MAIN5.forEach(k => r.vec[KI[k]] -= o.house * h.he[k]) } });
  act.forEach(r => { W += r.w; MAIN5.forEach((k, i) => m5[i] += r.w * r.vec[KI[k]]); if (isFinite(r.vec[KI.SALF])) { sS += r.w * r.vec[KI.SALF]; sW += r.w } });
  for (let i = 0; i < 5; i++) m5[i] /= W;
  const salf = sW > 0 ? sS / sW : 0.017;
  // Adelante Andalucía: media de las encuestas que la miden (los microdatos siempre la recogen)
  let aS = 0, aW = 0; act.forEach(r => { const x = r.vec[KI.ADELANTE]; if (isFinite(x)) { aS += r.w * x; aW += r.w } });
  const adel = aW > 0 ? aS / aW : 0.008;
  let Rb = 0;
  act.forEach(r => { const s5 = MAIN5.reduce((a, k) => a + r.vec[KI[k]], 0); const sl = isFinite(r.vec[KI.SALF]) ? r.vec[KI.SALF] : salf; const ad = isFinite(r.vec[KI.ADELANTE]) ? r.vec[KI.ADELANTE] : adel; Rb += r.w * (1 - s5 - sl - ad) });
  Rb /= W;
  // reparto del resto: bloque regional (cambios relativos desde microdatos), blancos y otros
  const bi = BLOCK.map(k => KI[k]), bB = bi.reduce((a, i) => a + b[i], 0);
  const mr = act.filter(r => r.p.src === 'micro'); let pooled = bi.map(() => 0), pw = 0;
  mr.forEach(r => { const s = bi.reduce((a, i) => a + r.vec[i], 0); if (s > 0) { bi.forEach((i, n) => pooled[n] += r.w * r.vec[i] / s); pw += r.w } });
  const rho = bi.map((i, n) => { if (!pw || o.lam <= 0) return 1; const ratio = (pooled[n] / pw) / (b[i] / bB); return Math.pow(Math.min(3, Math.max(0.3, ratio)), o.lam) });
  const q = bi.map((i, n) => b[i] * rho[n]), qs = q.reduce((a, x) => a + x, 0);
  let block = bB * (1 + o.blockShift), blank = b[KI.BLANCO], oth = Rb - block - blank;
  if (oth < 0.005) { const need = 0.005 - oth, f = (block + blank - need) / (block + blank); block *= f; blank *= f; oth = 0.005 }
  const T = new Array(NK).fill(0);
  MAIN5.forEach((k, i) => T[KI[k]] = m5[i]); T[KI.SALF] = salf; T[KI.ADELANTE] = adel;
  bi.forEach((i, n) => T[i] = block * q[n] / qs);
  T[KI.OTROS] = oth; T[KI.BLANCO] = blank;
  // nueva configuración de candidaturas: Podemos va dentro de ERC (Cataluña), Compromís-Front Valencià (C. Valenciana) y
  // Unidad del Pueblo Canario (Canarias); el espacio ex-Sumar también va en esas dos últimas. Fuera de ahí, Podemos y Frente Amplio por separado.
  const C = D.cfg, fa = T[KI.SUMAR], pod = T[KI.PODEMOS], tr = C.wFA.cv + C.wFA.can;
  T[KI.COMPROMIS] = fa * C.wFA.cv + pod * C.fPod.cv; T[KI.UPC] = fa * C.wFA.can + pod * C.fPod.can;
  T[KI.ERC] += pod * C.fPod.cat; T[KI.SUMAR] = fa * (1 - tr); T[KI.PODEMOS] = pod * (1 - C.fPod.cat - C.fPod.cv - C.fPod.can);
  const tf = { podCat: pod * C.fPod.cat, podCV: pod * C.fPod.cv, podCan: pod * C.fPod.can, faCV: fa * C.wFA.cv, faCan: fa * C.wFA.can };
  const Tsep = T.slice(); { const ts = Tsep.reduce((a, x) => a + x, 0); for (let i = 0; i < NK; i++) Tsep[i] /= ts }
  UNITY_R = T[KI.SUMAR] > 0 ? T[KI.PODEMOS] / T[KI.SUMAR] : 0;   // peso del Podemos propio frente a Frente Amplio, para repartir la lista unitaria en provincias
  if (o.unity) {
    // las listas donde Podemos/ex-Sumar ya van integrados (ERC, Compromís, UPC) no se ven afectadas por la unidad
    const FIX = [KI.ERC, KI.COMPROMIS, KI.UPC], fx = FIX.reduce((a, i) => a + T[i], 0);
    const S = T[KI.SUMAR] + T[KI.PODEMOS], Sc = T[KI.SUMAR] * coalShare(), nS = Math.min(0.3, Sc + (S - Sc) * o.bonus), f = (1 - nS - fx) / (1 - S - fx);
    for (let i = 0; i < NK; i++) if (!FIX.includes(i)) T[i] *= f; T[KI.SUMAR] = nS; T[KI.PODEMOS] = 0;
  }
  const tot = T.reduce((a, x) => a + x, 0); for (let i = 0; i < NK; i++) T[i] /= tot;
  // dispersión entre encuestas por partido
  const rng = {}; ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS'].forEach(k => { const xs = act.map(r => r.vec[KI[k]]); rng[k] = [Math.min(...xs), Math.max(...xs)] });
  const nEff = W * W / act.reduce((a, r) => a + r.w * r.w, 0);
  rows.forEach(r => r.share = r.ok ? r.w / W : 0);
  return { T, Tsep, rows, act, rng, HE, tf, adel, nEff, salf, Rb, rho: Object.fromEntries(BLOCK.map((k, n) => [k, rho[n]])), W };
}

/* ---- reparto a provincias: swing proporcional sobre 2023 con ajuste regional y calibrado a los objetivos nacionales ---- */
const NJ = D.prov.length, VV = D.prov.map(p => p.valid), VT = VV.reduce((a, x) => a + x, 0);
function facFor(ccaa, k, o) {
  const f = D.fac[ccaa]; if (!f) return { m: 1, sd: 0.06 };
  let e = f[KEYS[k]]; if (!e && (k === KI.PODEMOS || k === KI.COMPROMIS || k === KI.UPC)) e = f.SUMAR;
  if (!e) return { m: 1, sd: 0.06 };
  return { m: Math.pow(e.f, o.regInt), sd: e.sd };
}
function baseMatrix(o, Tsep) {
  if (o.unity && Tsep) {      // lista unitaria: se parte del reparto provincial por separado (ya calibrado) y solo se funden FA y Podemos donde Podemos concurre aparte, con el bonus allí
    const so = baseMatrix({ ...o, unity: false }); rake(so.S0, Tsep, 16);
    D.prov.forEach((p, j) => { if (!D.cfg.regPodemosCoal.includes(p.ccaa)) { so.S0[j][KI.SUMAR] = (so.S0[j][KI.SUMAR] + so.S0[j][KI.PODEMOS]) * o.bonus; so.S0[j][KI.PODEMOS] = 0 } });
    return so;
  }
  const S0 = [], SD = [];
  D.prov.forEach(p => {
    const row = p.sh.slice(), sd = new Array(NK).fill(0.06), sum = p.sh[KI.SUMAR], C = D.cfg;
    row[KI.PODEMOS] = C.regPodemosCoal.includes(p.ccaa) ? 0 : sum; row[KI.SALF] = p.sh[KI.VOX];
    if (p.ccaa === '10') { row[KI.COMPROMIS] = sum * C.kc; row[KI.SUMAR] = sum * (1 - C.kc) }
    if (p.ccaa === '05') { row[KI.UPC] = sum; row[KI.SUMAR] = 0 }
    if (p.ccaa === '01') row[KI.ADELANTE] = C.andAdelante;
    for (let k = 0; k < NPAR; k++) { if (row[k] <= 0) continue; const f = facFor(p.ccaa, k, o); row[k] *= f.m; sd[k] = f.sd * o.regInt }
    S0.push(row); SD.push(sd);
  });
  return { S0, SD };
}
function rake(S, T, iters) {
  for (let it = 0; it < iters; it++) {
    for (let k = 0; k < NK; k++) {
      if (T[k] <= 0) { for (let j = 0; j < NJ; j++) S[j][k] = 0; continue }
      let m = 0; for (let j = 0; j < NJ; j++) m += VV[j] * S[j][k]; m /= VT;
      if (m > 0) { const f = T[k] / m; for (let j = 0; j < NJ; j++) S[j][k] *= f }
    }
    for (let j = 0; j < NJ; j++) { let s = 0; for (let k = 0; k < NK; k++) s += S[j][k]; for (let k = 0; k < NK; k++) S[j][k] /= s }
  }
}
function dhondt(s, seats, out) {
  out.fill(0);
  const el = []; for (let k = 0; k < NPAR; k++) if (s[k] >= 0.03) el.push(k);
  for (let n = 0; n < seats; n++) {
    let best = -1, bq = -1;
    for (const k of el) { const q = s[k] / (out[k] + 1); if (q > bq) { bq = q; best = k } }
    if (best < 0) break; out[best]++;
  }
}
function natShare(S) { const t = new Array(NK).fill(0); for (let j = 0; j < NJ; j++) for (let k = 0; k < NK; k++) t[k] += VV[j] * S[j][k]; return t.map(x => x / VT) }

/* ---- simulación ---- */
const GRP = D.grupos;
function pct(sorted, p) { const i = (sorted.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return sorted[lo] + (sorted[hi] - sorted[lo]) * (i - lo) }
function simulate(T, o, Tsep) {
  const { S0, SD } = baseMatrix(o, Tsep);
  const out = new Int16Array(NPAR);
  // escenario central
  const Sc = S0.map(r => r.slice()); rake(Sc, T, 16);
  const cent = Sc.map((s, j) => { dhondt(s, D.prov[j].seats, out); return Array.from(out) });
  // simulaciones
  const R = mulberry(2911), N = o.nsim;
  const seatSim = Array.from({ length: NPAR }, () => new Int16Array(N));
  const shSim = Array.from({ length: NK }, () => new Float32Array(N));
  const grpSim = GRP.map(() => new Int16Array(N));
  const facSeatSim = new Int16Array(N), facShSim = new Float32Array(N), FAC = FACK.map(k => KI[k]);
  const winCnt = Array.from({ length: NJ }, () => new Float32Array(NPAR));
  const seatMean = Array.from({ length: NJ }, () => new Float32Array(NPAR));
  const shMean = Array.from({ length: NJ }, () => new Float32Array(NK));
  const hist = D.prov.map(p => Array.from({ length: NPAR }, () => new Uint32Array(p.seats + 1)));
  const nreg = {}; D.prov.forEach((p, j) => (nreg[p.ccaa] = nreg[p.ccaa] || []).push(j));
  for (let n = 0; n < N; n++) {
    const Tn = T.map((t, k) => { if (t <= 0) return 0; if (k === KI.BLANCO) return t; const sig = k === KI.OTROS ? 0.15 : o.sdSys / Math.sqrt(t * 100); return t * Math.exp(sig * normal(R) - sig * sig / 2) });
    const ts = Tn.reduce((a, x) => a + x, 0); for (let k = 0; k < NK; k++) Tn[k] /= ts;
    const S = S0.map(r => r.slice()); rake(S, Tn, 12);
    for (const c in nreg) { const eps = new Array(NK); for (let k = 0; k < NK; k++) eps[k] = normal(R); nreg[c].forEach(j => { for (let k = 0; k < NPAR; k++) if (S[j][k] > 0) { const sd = SD[j][k]; S[j][k] *= Math.exp(sd * eps[k] - sd * sd / 2) } }) }
    for (let j = 0; j < NJ; j++) {
      let s = 0; for (let k = 0; k < NPAR; k++) if (S[j][k] > 0) S[j][k] *= Math.exp(o.sdProv * normal(R) - o.sdProv * o.sdProv / 2);
      for (let k = 0; k < NK; k++) s += S[j][k]; for (let k = 0; k < NK; k++) S[j][k] /= s;
    }
    const tot = new Int16Array(NPAR);
    for (let j = 0; j < NJ; j++) {
      dhondt(S[j], D.prov[j].seats, out);
      let w = 0, bs = -1; for (let k = 0; k < NPAR; k++) { tot[k] += out[k]; seatMean[j][k] += out[k]; hist[j][k][out[k]]++; if (out[k] > bs || (out[k] === bs && S[j][k] > S[j][w])) { bs = out[k]; w = k } }
      winCnt[j][w]++;
      for (let k = 0; k < NK; k++) shMean[j][k] += S[j][k];
    }
    for (let k = 0; k < NPAR; k++) seatSim[k][n] = tot[k];
    const ns = natShare(S); for (let k = 0; k < NK; k++) shSim[k][n] = ns[k];
    facSeatSim[n] = FAC.reduce((a, i) => a + tot[i], 0); facShSim[n] = FAC.reduce((a, i) => a + ns[i], 0);
    GRP.forEach((g, i) => { let s = 0; g.parties.forEach(k => s += tot[KI[k]]); grpSim[i][n] = s });
  }
  const sum = (arr, p) => { const a = Float64Array.from(arr).sort(); return pct(a, p) };
  const seats = [], share = [];
  for (let k = 0; k < NPAR; k++) { const a = Float64Array.from(seatSim[k]).sort(); const mean = a.reduce((x, y) => x + y, 0) / N; seats.push({ mean, lo: Math.round(pct(a, .05)), hi: Math.round(pct(a, .95)), med: Math.round(pct(a, .5)) }) }
  for (let k = 0; k < NK; k++) { const a = Float64Array.from(shSim[k]).sort(); share.push({ mean: a.reduce((x, y) => x + y, 0) / N, lo: pct(a, .05), hi: pct(a, .95) }) }
  const groups = GRP.map((g, i) => { const a = Float64Array.from(grpSim[i]).sort(); let c = 0; for (let n = 0; n < N; n++) if (grpSim[i][n] >= 176) c++; return { id: g.id, label: g.label, parties: g.parties, mean: a.reduce((x, y) => x + y, 0) / N, lo: Math.round(pct(a, .05)), hi: Math.round(pct(a, .95)), p176: c / N } });
  for (let j = 0; j < NJ; j++) { for (let k = 0; k < NPAR; k++) { winCnt[j][k] /= N; seatMean[j][k] /= N } for (let k = 0; k < NK; k++) shMean[j][k] /= N }
  const fs = Float64Array.from(facSeatSim).sort(), fh = Float64Array.from(facShSim).sort();
  const facSeats = { mean: fs.reduce((x, y) => x + y, 0) / N, lo: Math.round(pct(fs, .05)), hi: Math.round(pct(fs, .95)), med: Math.round(pct(fs, .5)) }, facShare = { mean: fh.reduce((x, y) => x + y, 0) / N, lo: pct(fh, .05), hi: pct(fh, .95) };
  return { facSeats, facShare, cent, centShare: Sc, seats, share, groups, winCnt, seatMean, shMean, hist, N };
}
function lr(vals, total) { const fl = vals.map(Math.floor); let r = total - fl.reduce((a, b) => a + b, 0); vals.map((v, i) => [v - fl[i], i]).sort((a, b) => b[0] - a[0]).slice(0, r).forEach(([, i]) => fl[i]++); return fl }

function seedPolls() {
  const ps = D.polls.map(p => ({ ...p, v: { ...p.v } }));
  ps.push({ id: 'cis3577', name: 'CIS 3577 (microdatos)', date: '2026-09-03', n: D.micro.cis.n, v: {}, q: 1, include: true, src: 'micro', mk: 'cis', note: 'Barómetro de septiembre; reponderado por recuerdo de voto 2023' });
  ps.push({ id: 'd40flash', name: '40dB flash (microdatos)', date: '2026-10-08', n: D.micro.d40.n, v: {}, q: 1, include: true, src: 'micro', mk: 'd40', note: 'Flash 7-8 oct; sin Ceuta y Melilla' });
  ps.push({ id: 'ceo1169', name: 'CEO 1169 (solo Cataluña)', date: '2026-09-16', n: D.micro.ceo.n, v: {}, q: 1, include: false, src: 'micro', mk: 'ceo', regional: true, note: 'No entra en la media nacional: refuerza los factores de Cataluña' });
  return ps;
}
const DEFAULTS = { half: 14, variant: 'B', regInt: 1, unity: false, bonus: D.micro.d40.bonus, nsim: 1000, sdSys: 0.28, sdProv: 0.05, lam: 0.35, house: 1, group: true, blockShift: 0, ref: '2026-10-21' };

/* ---- voto necesario para escaño (D'Hondt, resto de partidos escalados en proporción) ---- */
const _out = new Int16Array(NPAR);
function seatsAt(row, k, x, seats) {
  const rest = 1 - row[k], f = rest > 0 ? (1 - x) / rest : 0, t = new Array(NK);
  for (let i = 0; i < NK; i++) t[i] = i === k ? x : row[i] * f;
  dhondt(t, seats, _out); return _out[k];
}
function needShare(row, k, seats, target) {
  if (target < 1 || target > seats) return null;
  if (seatsAt(row, k, 0.999, seats) < target) return null;
  let lo = 0, hi = 0.999;
  for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (seatsAt(row, k, mid, seats) >= target) hi = mid; else lo = mid }
  return hi;
}
function quotients(row, seats) {
  const q = [];
  for (let k = 0; k < NPAR; k++) if (row[k] >= 0.03) for (let d = 1; d <= seats + 1; d++) q.push({ k, d, q: row[k] / d });
  q.sort((a, b) => b.q - a.q);
  return q.slice(0, seats + 3).map((x, i) => ({ ...x, n: i + 1, won: i < seats }));
}
function histStats(h, N) {
  let c = 0, lo = null, hi = null, mean = 0;
  for (let s = 0; s < h.length; s++) { mean += s * h[s]; c += h[s]; if (lo === null && c >= 0.05 * N) lo = s; if (hi === null && c >= 0.95 * N) hi = s }
  return { lo, hi, mean: mean / N, p1: 1 - h[0] / N };
}

/* ---- barrera efectiva: voto mínimo que necesitaría un partido nuevo para sacar un escaño en la provincia (los demás se reducen en proporción) ---- */
function effThreshold(row, seats, noLegal) {
  const win = x => {
    const f = (1 - x), q = [];
    for (let k = 0; k < NPAR; k++) { const s = row[k] * f; if (s >= 0.03) for (let d = 1; d <= seats; d++) q.push(s / d) }
    q.sort((a, b) => b - a);
    const last = q.length >= seats ? q[seats - 1] : 0;
    return (noLegal || x >= 0.03) && x > last;
  };
  let lo = 0.0, hi = 1; if (!win(0.999)) return null;
  for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (win(mid)) hi = mid; else lo = mid }
  return hi;
}

/* ---- valores de Frente Amplio y Podemos en el gráfico: misma conversión que la media (candidaturas regionales y escenario unitario) ---- */
function chartMain(vec, o) {
  const c = D.cfg; let fa = vec[KI.SUMAR] * (1 - c.wFA.cv - c.wFA.can), po = vec[KI.PODEMOS] * (1 - c.fPod.cat - c.fPod.cv - c.fPod.can);
  if (o.unity) { const sc = fa * coalShare(); fa = Math.min(0.3, sc + (fa + po - sc) * o.bonus); po = 0 }
  return { SUMAR: fa, PODEMOS: po };
}

/* ---- Frente Amplio + confluencias de una encuesta: FA + Podemos propio + Adelante (Compromís y UPC son trozos de FA/Podemos; el Podemos de ERC queda fuera) ---- */
function facMain(vec, o, adel) {
  let s = vec[KI.SUMAR];
  if (o.unity) { const c = D.cfg, sc = s * coalShare(), po = vec[KI.PODEMOS] * (1 - c.fPod.cat - c.fPod.cv - c.fPod.can); s = Math.min(0.3, sc + (s + po - sc) * o.bonus) }
  const ad = isFinite(vec[KI.ADELANTE]) ? vec[KI.ADELANTE] : adel;
  return s + ad;
}
