/* ===== Motor del poll of polls ===== */
const KEYS = D.keys, NK = KEYS.length, KI = {};
KEYS.forEach((k, i) => KI[k] = i);
const NPAR = 13;                       // partidos que compiten por escaño (0..12); 13 = OTROS, 14 = BLANCO
const MAIN5 = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS'];
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

/* ---- efecto casa: desviación media de cada encuestadora respecto al consenso del resto, encogida (bayesiana) y centrada ---- */
const houseKey = p => p.src === 'micro' ? null : String(p.name || '').split(/\s*[\/(]/)[0].normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase() || null;
const HOUSE_TAU = 0.06;   // dispersión relativa a priori de los efectos casa (6 % del % de cada partido)
function houseEffects(act, o) {
  const pub = act.filter(r => r.hk), groups = {};
  pub.forEach(r => (groups[r.hk] = groups[r.hk] || []).push(r));
  const out = {}, names = Object.keys(groups);
  if (names.length < 3) return out;
  names.forEach(h => {
    const mine = groups[h], oth = pub.filter(r => r.hk !== h), Wo = oth.reduce((a, r) => a + r.w, 0), Wm = mine.reduce((a, r) => a + r.w, 0);
    const ne = mine.reduce((a, r) => a + pollNeff(r.p, o), 0), no = oth.reduce((a, r) => a + pollNeff(r.p, o), 0);
    const he = {}, raw = {};
    MAIN5.forEach(k => {
      const i = KI[k], cons = oth.reduce((a, r) => a + r.w * r.vec[i], 0) / Wo, own = mine.reduce((a, r) => a + r.w * r.vec[i], 0) / Wm;
      const d = own - cons, pq = cons * (1 - cons), nv = pq / ne + pq / no, tv = Math.pow(HOUSE_TAU * cons, 2);
      raw[k] = d; he[k] = d * tv / (tv + nv);
    });
    out[h] = { name: mine[0].p.name.split(/\s*[\/(]/)[0].trim(), n: mine.length, W: Wm, he, raw };
  });
  // centrar: la media simple de los efectos entre encuestadoras es cero (cada casa cuenta igual; el sesgo medio del sector no se puede medir sin un resultado real)
  MAIN5.forEach(k => { const m = names.reduce((a, h) => a + out[h].he[k], 0) / names.length; names.forEach(h => out[h].he[k] -= m) });
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
  let Rb = 0;
  act.forEach(r => { const s5 = MAIN5.reduce((a, k) => a + r.vec[KI[k]], 0); const sl = isFinite(r.vec[KI.SALF]) ? r.vec[KI.SALF] : salf; Rb += r.w * (1 - s5 - sl) });
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
  MAIN5.forEach((k, i) => T[KI[k]] = m5[i]); T[KI.SALF] = salf;
  bi.forEach((i, n) => T[i] = block * q[n] / qs);
  T[KI.OTROS] = oth; T[KI.BLANCO] = blank;
  if (o.unity) {
    const S = T[KI.SUMAR] + T[KI.PODEMOS], nS = Math.min(0.3, S * o.bonus), f = (1 - nS) / (1 - S);
    for (let i = 0; i < NK; i++) T[i] *= f; T[KI.SUMAR] = nS; T[KI.PODEMOS] = 0;
  }
  const tot = T.reduce((a, x) => a + x, 0); for (let i = 0; i < NK; i++) T[i] /= tot;
  // dispersión entre encuestas por partido
  const rng = {}; ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS'].forEach(k => { const xs = act.map(r => r.vec[KI[k]]); rng[k] = [Math.min(...xs), Math.max(...xs)] });
  const nEff = W * W / act.reduce((a, r) => a + r.w * r.w, 0);
  rows.forEach(r => r.share = r.ok ? r.w / W : 0);
  return { T, rows, act, rng, HE, nEff, salf, Rb, rho: Object.fromEntries(BLOCK.map((k, n) => [k, rho[n]])), W };
}

/* ---- reparto a provincias: swing proporcional sobre 2023 con ajuste regional y calibrado a los objetivos nacionales ---- */
const NJ = D.prov.length, VV = D.prov.map(p => p.valid), VT = VV.reduce((a, x) => a + x, 0);
function facFor(ccaa, k, o) {
  const f = D.fac[ccaa]; if (!f) return { m: 1, sd: 0.06 };
  let e = f[KEYS[k]]; if (!e && k === KI.PODEMOS) e = f.SUMAR;
  if (!e) return { m: 1, sd: 0.06 };
  return { m: Math.pow(e.f, o.regInt), sd: e.sd };
}
function baseMatrix(o) {
  const S0 = [], SD = [];
  D.prov.forEach(p => {
    const row = p.sh.slice(), sd = new Array(NK).fill(0.06);
    row[KI.PODEMOS] = p.sh[KI.SUMAR]; row[KI.SALF] = p.sh[KI.VOX];
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
function simulate(T, o) {
  const { S0, SD } = baseMatrix(o);
  const out = new Int16Array(NPAR);
  // escenario central
  const Sc = S0.map(r => r.slice()); rake(Sc, T, 16);
  const cent = Sc.map((s, j) => { dhondt(s, D.prov[j].seats, out); return Array.from(out) });
  // simulaciones
  const R = mulberry(2911), N = o.nsim;
  const seatSim = Array.from({ length: NPAR }, () => new Int16Array(N));
  const shSim = Array.from({ length: NK }, () => new Float32Array(N));
  const grpSim = GRP.map(() => new Int16Array(N));
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
    GRP.forEach((g, i) => { let s = 0; g.parties.forEach(k => s += tot[KI[k]]); grpSim[i][n] = s });
  }
  const sum = (arr, p) => { const a = Float64Array.from(arr).sort(); return pct(a, p) };
  const seats = [], share = [];
  for (let k = 0; k < NPAR; k++) { const a = Float64Array.from(seatSim[k]).sort(); const mean = a.reduce((x, y) => x + y, 0) / N; seats.push({ mean, lo: pct(a, .05), hi: pct(a, .95), med: pct(a, .5) }) }
  for (let k = 0; k < NK; k++) { const a = Float64Array.from(shSim[k]).sort(); share.push({ mean: a.reduce((x, y) => x + y, 0) / N, lo: pct(a, .05), hi: pct(a, .95) }) }
  const groups = GRP.map((g, i) => { const a = Float64Array.from(grpSim[i]).sort(); let c = 0; for (let n = 0; n < N; n++) if (grpSim[i][n] >= 176) c++; return { id: g.id, label: g.label, parties: g.parties, mean: a.reduce((x, y) => x + y, 0) / N, lo: pct(a, .05), hi: pct(a, .95), p176: c / N } });
  for (let j = 0; j < NJ; j++) { for (let k = 0; k < NPAR; k++) { winCnt[j][k] /= N; seatMean[j][k] /= N } for (let k = 0; k < NK; k++) shMean[j][k] /= N }
  return { cent, centShare: Sc, seats, share, groups, winCnt, seatMean, shMean, hist, N };
}
function lr(vals, total) { const fl = vals.map(Math.floor); let r = total - fl.reduce((a, b) => a + b, 0); vals.map((v, i) => [v - fl[i], i]).sort((a, b) => b[0] - a[0]).slice(0, r).forEach(([, i]) => fl[i]++); return fl }

function seedPolls() {
  const ps = D.polls.map(p => ({ ...p, v: { ...p.v } }));
  ps.push({ id: 'cis3577', name: 'CIS 3577 (microdatos)', date: '2026-09-03', n: D.micro.cis.n, v: {}, q: 1, include: true, src: 'micro', mk: 'cis', note: 'Barómetro de septiembre; reponderado por recuerdo de voto 2023' });
  ps.push({ id: 'd40flash', name: '40dB flash (microdatos)', date: '2026-10-08', n: D.micro.d40.n, v: {}, q: 1, include: true, src: 'micro', mk: 'd40', note: 'Flash 7-8 oct; sin Ceuta y Melilla' });
  ps.push({ id: 'ceo1169', name: 'CEO 1169 (solo Cataluña)', date: '2026-09-16', n: D.micro.ceo.n, v: {}, q: 1, include: false, src: 'micro', mk: 'ceo', regional: true, note: 'No entra en la media nacional: refuerza los factores de Cataluña' });
  return ps;
}
const DEFAULTS = { half: 14, variant: 'B', regInt: 1, unity: false, bonus: D.micro.d40.bonus, nsim: 1000, sdSys: 0.28, sdProv: 0.05, lam: 0.35, house: 1, blockShift: 0, ref: '2026-10-14' };

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
