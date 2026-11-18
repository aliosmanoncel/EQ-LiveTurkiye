// core.mjs — Ana Şok Öncesi Sismisite Oranı Testi (Pre-mainshock Seismicity Rate Test)
// Sürüm: pmsr-core-0.1.0 (2026-11-18) — DENEME, feature/premainshock-rate-test dalı
//
// Yöntem kaynağı: Azad Khan, Werner, Biggs ve Fagereng (2025), JGR Solid Earth 130(7),
// e2024JB030733 — Bölüm 2 (ana şok seçimi: Fixed, Mag-Dep, Combined), Type A ve
// Empirical Seismicity Rate (ESR) tanımları; Mc: b-değeri kararlılığı (Cao ve Gao, 2002;
// Woessner ve Wiemer, 2005), Aki-Utsu b ve Shi-Bolt belirsizliği.
// Bu dosya makaledeki yöntem tanımından bağımsız yazılmıştır; GPLv3 lisanslı `statseis`
// paketinden satır aktarımı yoktur. `statseis` yalnızca depo dışında referans (test
// kâhini) olarak kullanılmıştır — bkz. analysis/2026-11-18_pmsr_scsn_reproduction/.
//
// Katalogdan bağımsızdır: girdi { id, t (s, UTC epoch), lat, lon, m } dizisi.
// Tek büyüklük türü varsayılır; dönüştürülmüş/karışık büyüklükler kullanıcının sorumluluğundadır.

export const PMSR_VERSION = 'pmsr-core-0.1.0';

export const DEFAULTS = Object.freeze({
  mainshockMin: 4.0,      // ana şok adayı eşiği
  fixedRadiusKm: 10,      // Fixed: daha büyük olay arama yarıçapı
  fixedDays: 365,         // Fixed: geriye bakış süresi
  mdR0: 20, mdCR: 5,      // Mag-Dep: R(M) = R0 + cR·L(M), L = 10^((M−4,38)/1,49)
  mdT0: 50, mdCT: 25,     // Mag-Dep: T(M) = T0 + cT·(M − mainshockMin)
  radiusKm: 10,           // öncü/kalibrasyon yarıçapı
  windowDays: 20,         // öncü penceresi
  calibDays: 365,         // kalibrasyon: calibDays → windowDays gün önce
  stepPerDay: 100,        // kayan pencere adımı = 0,01 gün
  alpha: 0.01,            // anlamlılık eşiği (99. persentil)
  typeAMin: 3.0,          // Type A büyüklük eşiği (Mc kesmesiz)
  mcR0: 10, mcStep: 5, mcRmax: 50, mcMinN: 275, // yerel Mc yarıçap genişletme
  mbin: 0.1, mbsDM: 0.4,  // Mc (MBS) parametreleri
  mcCausal: false,        // true: Mc yalnız ana şok öncesi veriden
});

const DAY = 86400;
const RAD = Math.PI / 180;

export function haversineKm(lat1, lon1, lat2, lon2) {
  const p1 = lat1 * RAD, p2 = lat2 * RAD;
  const a = Math.sin((p2 - p1) / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin((lon2 - lon1) * RAD / 2) ** 2;
  return 2 * 6371 * Math.asin(Math.sqrt(a));
}

// WGS84 elipsoidi üzerinde jeodezik uzaklık (Vincenty 1975, ters problem), km.
// Yerel Mc yarıçapı bu uzaklıkla ölçülür (referans uygulamayla aynı elipsoit).
export function geodesicKm(lat1, lon1, lat2, lon2) {
  const a = 6378137, f = 1 / 298.257223563, b = a * (1 - f);
  const L = (lon2 - lon1) * RAD;
  const U1 = Math.atan((1 - f) * Math.tan(lat1 * RAD)), U2 = Math.atan((1 - f) * Math.tan(lat2 * RAD));
  const sU1 = Math.sin(U1), cU1 = Math.cos(U1), sU2 = Math.sin(U2), cU2 = Math.cos(U2);
  let lam = L, it = 0, sS, cS, sig, sA, c2A, c2Sm;
  do {
    const sL = Math.sin(lam), cL = Math.cos(lam);
    sS = Math.sqrt((cU2 * sL) ** 2 + (cU1 * sU2 - sU1 * cU2 * cL) ** 2);
    if (sS === 0) return 0;
    cS = sU1 * sU2 + cU1 * cU2 * cL;
    sig = Math.atan2(sS, cS);
    sA = cU1 * cU2 * sL / sS;
    c2A = 1 - sA * sA;
    c2Sm = c2A !== 0 ? cS - 2 * sU1 * sU2 / c2A : 0;
    const C = f / 16 * c2A * (4 + f * (4 - 3 * c2A));
    const prev = lam;
    lam = L + (1 - C) * f * sA * (sig + C * sS * (c2Sm + C * cS * (-1 + 2 * c2Sm * c2Sm)));
    if (Math.abs(lam - prev) < 1e-12) break;
  } while (++it < 200);
  const u2 = c2A * (a * a - b * b) / (b * b);
  const A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)));
  const B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)));
  const dS = B * sS * (c2Sm + B / 4 * (cS * (-1 + 2 * c2Sm * c2Sm) - B / 6 * c2Sm * (-3 + 4 * sS * sS) * (-3 + 4 * c2Sm * c2Sm)));
  return b * A * (sig - dS) / 1000;
}

export function ruptureLengthKm(M) { return 10 ** ((M - 4.38) / 1.49); }

// ---------- Ana şok seçimi ----------
// cat: zamana göre sıralı. Döner: [{i, fixed, magdep, combined}] (M ≥ mainshockMin adaylar)
export function selectMainshocks(cat, opt = {}) {
  const o = { ...DEFAULTS, ...opt };
  const big = [];
  for (let i = 0; i < cat.length; i++) if (cat[i].m >= o.mainshockMin) big.push(i);
  const out = [];
  for (const i of big) {
    const e = cat[i];
    // Fixed: son fixedDays içinde fixedRadiusKm içinde daha büyük olay varsa dışla
    let fixed = true;
    for (let j = i - 1; j >= 0; j--) {
      const q = cat[j];
      if (e.t - q.t > o.fixedDays * DAY) break;
      if (q.m > e.m && haversineKm(e.lat, e.lon, q.lat, q.lon) <= o.fixedRadiusKm) { fixed = false; break; }
    }
    // Mag-Dep: daha büyük bir adayın R(M_L), T(M_L) penceresine düşüyorsa dışla
    let magdep = true;
    for (const k of big) {
      if (k === i) continue;
      const L = cat[k];
      if (L.m <= e.m) continue;
      const dtDays = (e.t - L.t) / DAY;
      const T = o.mdT0 + o.mdCT * (L.m - o.mainshockMin);
      if (dtDays >= T || dtDays <= -T) continue;
      if (dtDays < 0 && !o.mdIncludePreceding) continue;
      const R = o.mdR0 + o.mdCR * ruptureLengthKm(L.m);
      if (haversineKm(e.lat, e.lon, L.lat, L.lon) <= R) { magdep = false; break; }
    }
    out.push({ i, id: e.id, fixed, magdep, combined: fixed && magdep });
  }
  return out;
}

// ---------- Mc: b-değeri kararlılığı ----------
// Aday Mc değerleri 0,1'lik bölme merkezleridir; b, ham büyüklüklerden (M > Mc − Δ/2)
// Aki-Utsu ile, belirsizlik Shi ve Bolt (1982) ile hesaplanır. Mc, |b_ort − b| ≤ δb
// koşulunu sağlayan en küçük bölmedir; b_ort, Mc'den Mc + ΔM'ye kadarki bölmelerin b
// ortalamasıdır (Woessner ve Wiemer, 2005). Ortalamadaki bölmelerden biri tanımsızsa
// (≤ 1 olay) o aday geçersizdir; son ΔM/Δ + 1 bölme aday olamaz.
function akiB(mags, mc, mbin) {
  const thr = Math.round(mc * 10) / 10 - mbin / 2;
  let s = 0, n = 0;
  for (const m of mags) if (m > thr) { s += m; n++; }
  if (n < 2) return { b: NaN, db: NaN, n };
  const mean = s / n;
  const b = Math.LOG10E / (mean - (mc - mbin / 2));
  let ss = 0;
  for (const m of mags) if (m > thr) ss += (m - mean) ** 2;
  return { b, db: 2.3 * b * b * Math.sqrt(ss / (n * (n - 1))), n };
}

export function mcMBS(mags, opt = {}) {
  const o = { ...DEFAULTS, ...opt };
  const mbin = o.mbin;
  if (mags.length < 2) return NaN;
  let lo = Infinity, hi = -Infinity;
  for (const m of mags) { if (m < lo) lo = m; if (m > hi) hi = m; }
  const k0 = Math.round(lo / mbin), k1 = Math.round(hi / mbin);
  const bins = []; for (let k = k0; k <= k1; k++) bins.push(+(k * mbin).toFixed(1));
  const bv = bins.map(c => { const r = akiB(mags, c, mbin); return r.n > 1 ? r : { b: NaN, db: NaN }; });
  const nAvg = Math.round(o.mbsDM / mbin);
  for (let i = 0; i < bins.length; i++) {
    if (i >= bins.length - (nAvg + 1)) break;
    let s = 0, ok = true;
    for (let j = i; j <= i + nAvg; j++) { if (!isFinite(bv[j].b)) { ok = false; break; } s += bv[j].b; }
    if (!ok) continue;
    if (Math.abs(s / (nAvg + 1) - bv[i].b) <= bv[i].db) return bins[i];
  }
  return NaN;
}

// Yerel Mc: yarıçap mcR0'dan mcStep adımla mcRmax'a, ≥ mcMinN olay olana dek (tüm katalog süresi)
export function localMc(cat, ev, opt = {}) {
  const o = { ...DEFAULTS, ...opt };
  // mcCausal: yalnız ana şoktan önceki olaylar (canlı/nedensel kullanım). Varsayılan: false
  // (Khan vd. gibi tüm katalog dönemi).
  const d = cat.map(q => (o.mcCausal && q.t >= ev.t) ? Infinity : geodesicKm(ev.lat, ev.lon, q.lat, q.lon));
  let r = o.mcR0, sel;
  for (;;) {
    sel = [];
    for (let j = 0; j < cat.length; j++) if (d[j] < r) sel.push(cat[j].m);
    if (sel.length >= o.mcMinN || r >= o.mcRmax) break;
    r += o.mcStep;
  }
  const enough = sel.length >= o.mcMinN;
  return { mc: enough ? mcMBS(sel, o) : NaN, n: sel.length, radiusKm: r, enough };
}

// ---------- Empirical Seismicity Rate (ESR) ----------
// daysBefore: ana şoktan önceki olayların gün cinsinden uzaklıkları (R ve Mc filtreli)
export function esr(daysBefore, opt = {}) {
  const o = { ...DEFAULTS, ...opt };
  const W = o.windowDays, C = o.calibDays, S = o.stepPerDay;
  const d = daysBefore.filter(x => x > 0 && x < C + W).sort((a, b) => a - b);
  const reg = d.filter(x => x >= W);
  const nObs = d.length - reg.length;
  const cut = Math.min(Math.floor(o.cutOffDay ?? C), C);
  const counts = [];
  // pencere başlangıçları W, W+1/S, ..., cut−W ; sayım: p < x ≤ p+W
  const ub = (arr, v) => { let a = 0, b = arr.length; while (a < b) { const m = (a + b) >> 1; if (arr[m] <= v) a = m + 1; else b = m; } return a; };
  for (let k = Math.round(W * S); k <= Math.round((cut - W) * S); k++) {
    const p = k / S;
    counts.push(ub(reg, p + W) - ub(reg, p));
  }
  let pval, q99 = NaN, maxW = NaN;
  if (counts.length === 0) pval = nObs > 0 ? 0 : 1;
  else {
    let ge = 0; for (const c of counts) if (c >= nObs) ge++;
    pval = ge / counts.length;
    const s = [...counts].sort((a, b) => a - b);
    const pos = 0.99 * (s.length - 1), f = Math.floor(pos);
    q99 = s[f] + (s[Math.min(f + 1, s.length - 1)] - s[f]) * (pos - f);
    maxW = s[s.length - 1];
  }
  return { nObs, nCalib: reg.length, nWindows: counts.length, p: pval, q99, maxWindow: maxW,
           significant: pval < o.alpha };
}

// ---------- Tek ana şok için tüm zincir ----------
export const LABELS = Object.freeze({
  sig: { tr: 'İstatistiksel olarak anlamlı artış', en: 'Statistically significant rate increase' },
  ns:  { tr: 'İstatistiksel olarak anlamlı artış bulunamadı', en: 'No statistically significant rate increase' },
  na:  { tr: 'Analiz için yeterli veri yok', en: 'Insufficient data for analysis' },
  notMain: { tr: 'Seçilen olay ana şok seçim kuralını sağlamıyor', en: 'Selected event does not satisfy the mainshock selection rule' },
});

export function analyzeEvent(cat, idx, opt = {}) {
  const o = { ...DEFAULTS, ...opt };
  const ev = cat[idx];
  const mc = localMc(cat, ev, o);
  const before = [], typeA = [];
  for (let j = 0; j < idx; j++) {
    const q = cat[j];
    const days = (ev.t - q.t) / DAY;
    if (days <= 0 || days >= o.calibDays + o.windowDays) continue;
    if (haversineKm(ev.lat, ev.lon, q.lat, q.lon) >= o.radiusKm) continue;
    if (days < o.windowDays && q.m >= o.typeAMin) typeA.push(q.id);
    if (mc.enough && q.m >= mc.mc) before.push(days);
  }
  const catStartDays = (ev.t - cat[0].t) / DAY;
  const r = mc.enough ? esr(before, { ...o, cutOffDay: Math.min(catStartDays, o.calibDays) }) : null;
  const label = !mc.enough ? 'na' : (r.significant ? 'sig' : 'ns');
  return { id: ev.id, t: ev.t, m: ev.m, lat: ev.lat, lon: ev.lon, mc, esr: r, typeA: typeA.length,
           typeAWarning: mc.enough && mc.mc > o.typeAMin, label, version: PMSR_VERSION };
}

// Varsayılandan farklı parametreleri listeler (sonuç ekranında işaretlemek için)
export function nonDefault(opt = {}) {
  return Object.keys(opt).filter(k => k in DEFAULTS && opt[k] !== DEFAULTS[k]).map(k => ({ key: k, value: opt[k], default: DEFAULTS[k] }));
}

// Wilson %95 güven aralığı
export function wilson(k, n, z = 1.959963984540054) {
  if (!n) return [NaN, NaN];
  const p = k / n, d = 1 + z * z / n, c = p + z * z / (2 * n), h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
  return [(c - h) / d, (c + h) / d];
}
