// Birim testleri: G-R model–gözlem denetimi (Patch 1 + Patch 1b + Patch 2, 2026-09-28).
// Fonksiyonlar doğrudan index.html'den okunur (weichertFit … grConsistency); kopya tutulmaz.
// Kullanım (depo kökünde): node scripts/test_gr_consistency.js [index.html]
// Metodoloji: seismo-report/eqlive-turkey-methodology.html — Tablo 8s, Tablo 8t, bootstrap yordamı.
// Referans değerler (logΓ, χ² üst kuyruk) scipy 1.15.3 ile üretilip aşağıya gömülmüştür.
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const a = src.indexOf('function weichertFit(bins)'), b = src.indexOf('let lastGrFit = null;');
if (a < 0 || b < 0 || b < a) throw new Error('index.html içinde weichertFit … grConsistency bloğu bulunamadı');
const ctx = {}; vm.createContext(ctx);
const csq = src.match(/^const CS_QC = \{[^\n]*\};$/m); if (!csq) throw new Error('CS_QC bulunamadı');
vm.runInContext(csq[0].replace('const CS_QC', 'var CS_QC'), ctx);   // posterQcSummary için (index.html'den)
vm.runInContext(src.slice(a, b) + '\n;globalThis.__x = { weichertFit, poissonBounds1sd, GR_QC, mulberry32, logGamma, poissonSample, chi2Sf, weichertExpected, poissonDeviance, grGofPoisson, grRProfile, grConsistency, fmtPboot, posterQcSummary, posterFitItems };', ctx);
const X = ctx.__x;
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };
const near = (x, y, tol) => Math.abs(x - y) <= tol * Math.max(1, Math.abs(y));

// ── 1. PRNG (mulberry32): tekrarlanabilirlik ─────────────────────────
{ const r1 = X.mulberry32(20260928), r2 = X.mulberry32(20260928), r3 = X.mulberry32(20260929);
  const s1 = Array.from({ length: 1000 }, r1), s2 = Array.from({ length: 1000 }, r2), s3 = Array.from({ length: 1000 }, r3);
  ok(s1.every((v, i) => v === s2[i]), 'PRNG aynı tohum aynı dizi');
  ok(s1.some((v, i) => v !== s3[i]), 'PRNG farklı tohum farklı dizi');
  ok(s1.every(v => v >= 0 && v < 1), 'PRNG [0,1)');
  const m = s1.reduce((p, v) => p + v, 0) / s1.length; ok(Math.abs(m - 0.5) < 0.03, 'PRNG ortalama ' + m);
  console.log('PRNG mulberry32(20260928) ilk 3:', s1.slice(0, 3).map(v => v.toFixed(10)).join(', ')); }

// ── 2. logΓ ve χ² üst kuyruk (scipy referansı) ───────────────────────
const LG = [[0.3, 1.0957979948180756], [1, 0.0], [1.5, -0.12078223763524526], [2.5, 0.2846828704729192], [5, 3.1780538303479458], [10.5, 13.940625219403763], [50, 144.56574394634487], [171.3, 708.1149470389971], [1000.25, 5906.9472682711175]];
LG.forEach(([x, y]) => ok(Math.abs(X.logGamma(x) - y) < 1e-9 * Math.max(1, Math.abs(y)), `logGamma(${x}) ${X.logGamma(x)} vs ${y}`));
const CS = [[0.5, 1, 0.47950012218695337], [3.84, 1, 0.05004352124870519], [10, 5, 0.07523524614651217], [40, 30, 0.10486428110798468], [55.76, 40, 0.04998592624419688], [120, 80, 0.0025481923036133444], [300, 250, 0.016518273157868715], [2000, 1900, 0.054206673889018606], [1, 10, 0.9998278843700441], [5000, 60, 0.0]];
CS.forEach(([x, df, p]) => ok(Math.abs(X.chi2Sf(x, df) - p) < 1e-8 + 1e-6 * p, `chi2Sf(${x},${df}) ${X.chi2Sf(x, df)} vs ${p}`));

// ── 3. Poisson örnekleme (Knuth μ<10, PTRS μ≥10): ortalama, varyans, dağılım ──
{ const rnd = X.mulberry32(12345), n = 100000;
  for (const mu of [0.3, 2, 9.99, 10, 15, 50, 300, 2000]) {
    let s = 0, s2 = 0; const cnt = new Map();
    for (let i = 0; i < n; i++) { const k = X.poissonSample(mu, rnd); s += k; s2 += k * k; cnt.set(k, (cnt.get(k) || 0) + 1); }
    const m = s / n, v = s2 / n - m * m;
    ok(Math.abs(m - mu) < 5 * Math.sqrt(mu / n), `Poisson μ=${mu} ortalama ${m.toFixed(4)}`);
    ok(Math.abs(v / mu - 1) < 0.03, `Poisson μ=${mu} varyans/μ ${(v / mu).toFixed(4)}`);
    if (mu <= 300) { // pmf ile ki-kare uyumu (beklenen ≥ 5 hücreler, uçlar birleştirilir)
      const pmf = k => Math.exp(-mu + k * Math.log(mu) - X.logGamma(k + 1));
      const lo = Math.max(0, Math.floor(mu - 5 * Math.sqrt(mu))), hi = Math.ceil(mu + 5 * Math.sqrt(mu) + 5);
      let chi = 0, dof = -1, eAcc = 0, oAcc = 0;
      let eLow = 0, oLow = 0; for (let k = 0; k < lo; k++) { eLow += n * pmf(k); oLow += cnt.get(k) || 0; }
      eAcc = eLow; oAcc = oLow;
      for (let k = lo; k <= hi; k++) { eAcc += n * pmf(k); oAcc += cnt.get(k) || 0; if (eAcc >= 5) { chi += (oAcc - eAcc) ** 2 / eAcc; dof++; eAcc = 0; oAcc = 0; } }
      let oHi = 0; cnt.forEach((c, k) => { if (k > hi) oHi += c; }); const eHi = n - [...Array(hi + 1).keys()].reduce((p, k) => p + n * pmf(k), 0);
      if (eHi + eAcc >= 5) { chi += (oHi + oAcc - eHi - eAcc) ** 2 / (eHi + eAcc); dof++; }
      const p = X.chi2Sf(chi, dof); ok(p > 0.001, `Poisson μ=${mu} dağılım uyumu p=${p.toFixed(4)} (sd=${dof})`);
    }
  } }

// ── 4. Poisson sapması ───────────────────────────────────────────────
ok(Math.abs(X.poissonDeviance([3, 5, 0], [3, 5, 0.0])) < 1e-12, 'D(n=μ) = 0');
ok(near(X.poissonDeviance([0, 2], [1, 1]), 2 * ((0 - (0 - 1)) + (2 * Math.log(2) - (2 - 1))), 1e-12), 'D elle hesapla eşit');

// ── Sentetik katalog yardımcıları ────────────────────────────────────
const DM = 0.1;
// Basamaklı tamlık: M < 2.0 yalnızca son Ty1 yıl, M ≥ 2.0 tüm Ty2 yıl; sınıf merkezleri m + DM/2
function mkClasses(beta, rate0, m0, mTop, Tof) {
  const c = []; for (let m = m0; m < mTop - 1e-9; m = +(m + DM).toFixed(2)) c.push({ lo: m, m: +(m + DM / 2).toFixed(3), T: Tof(m) });
  // gerçek beklenen: T·[λ(≥lo) − λ(≥lo+DM)], λ(≥M) = rate0 e^{-β(M−m0)}
  c.forEach(x => { x.mu = x.T * rate0 * (Math.exp(-beta * (x.lo - m0)) - Math.exp(-beta * (x.lo + DM - m0))); }); return c;
}
function simClasses(C, rnd, muf) { return C.map(x => ({ m: x.m, lo: x.lo, T: x.T, n: X.poissonSample(muf ? muf(x) : x.mu, rnd) })); }
function toBins(C) { // renderGutenbergRichterCS ile aynı: alt sınır, rate, cumRate, cumN, cumLo/cumHi
  const bins = C.map(x => ({ m: x.lo, n: x.n, T: x.T, rate: x.T > 0 ? x.n / x.T : 0 }));
  let run = 0, runN = 0; for (let i = bins.length - 1; i >= 0; i--) { run += bins[i].rate; bins[i].cumRate = run; runN += bins[i].n; bins[i].cumN = runN; }
  for (let i = 0; i < bins.length; i++) { const tail = bins.slice(i).filter(b => b.n > 0 && b.T > 0); if (!tail.length) continue;
    const Nc = tail.reduce((a, b) => a + b.n, 0), Ts = tail.map(b => b.T), eqT = Math.max(...Ts) - Math.min(...Ts) < 1e-6;
    if (eqT) { const [lo, hi] = X.poissonBounds1sd(Nc); bins[i].cumLo = lo / Ts[0]; bins[i].cumHi = hi / Ts[0]; bins[i].errSrc = 'Poisson (eşit T)'; }
    else { const sd = Math.sqrt(tail.reduce((a, b) => a + b.n / (b.T * b.T), 0)); bins[i].cumLo = Math.max(bins[i].cumRate - sd, 0); bins[i].cumHi = bins[i].cumRate + sd; bins[i].errSrc = 'σ² = Σn/T²'; } }
  return bins;
}
const Tstep = m => (m < 2.0 - 1e-9 ? 3 : 15);

// ── 5. Katman (1): uyum testi — tekrarlanabilirlik, kalibrasyon, güç ──
{ const beta = Math.LN10, C = mkClasses(beta, 300, 1.0, 5.0, Tstep), rnd = X.mulberry32(777);
  const obs = simClasses(C, rnd), wf = X.weichertFit(obs);
  const g1 = X.grGofPoisson(obs, wf), g2 = X.grGofPoisson(obs, wf);
  ok(g1.ok && g1.pBoot === g2.pBoot && g1.D === g2.D, 'GoF aynı tohum → aynı p_boot');
  ok(g1.B === 999 && g1.seed === 20260928 && g1.df === g1.K - 2, 'GoF B=999, tohum 20260928, sd=K−2');
  ok(g1.pBoot >= 1 / 1000 && g1.pBoot <= 1, 'p_boot aralığı');
  const g3 = X.grGofPoisson(obs, wf, { seed: 1 }); ok(g3.pBoot !== g1.pBoot || g3.D === g1.D, 'farklı tohum çalışıyor');
  // Kalibrasyon: doğru modelden 200 katalog, B = 199 → p_boot < 0.05 oranı ≈ 0.05
  let rej = 0; const R = 200;
  for (let r = 0; r < R; r++) { const o = simClasses(C, rnd), f = X.weichertFit(o); const g = X.grGofPoisson(o, f, { B: 199, seed: 1000 + r }); if (g.pBoot < 0.05) rej++; }
  const rate = rej / R; console.log(`Kalibrasyon (H0 doğru, ${R} katalog, B=199): p_boot<0.05 oranı = ${rate.toFixed(3)}`);
  ok(rate > 0.01 && rate < 0.11, 'GoF kalibrasyonu ≈ α');
  // Güç: M < 2.0 sınıflarında eksik kayıt (yalnızca %35 algılanmış) → modelden sapma
  let rejA = 0; for (let r = 0; r < 50; r++) { const o = simClasses(C, rnd, x => x.lo < 2.0 - 1e-9 ? 0.35 * x.mu : x.mu), f = X.weichertFit(o); if (X.grGofPoisson(o, f, { B: 199, seed: 5000 + r }).pBoot < 0.05) rejA++; }
  console.log(`Güç (M<2.0 eksik kayıt %65, 50 katalog): red oranı = ${(rejA / 50).toFixed(2)}`);
  ok(rejA / 50 > 0.8, 'GoF eksik kayıtta reddediyor');
  // Mref bağımsızlığı: grGofPoisson M_ref almıyor
  ok(X.grGofPoisson.length === 3, 'grGofPoisson imzası M_ref içermiyor'); }

// ── 6. Katman (2): log R(M) profili ve Δb ────────────────────────────
{ const b0 = 1.0, bHat = 0.8, m0 = 1.0, C = mkClasses(b0 * Math.LN10, 400, m0, 6.0, () => 15);
  C.forEach(x => { x.n = Math.round(x.mu); }); const bins = toBins(C);
  const model = M => 400 * Math.pow(10, -bHat * (M - m0)) * 1.0;
  const pr = X.grRProfile(bins, 2.0, model);
  ok(pr.ok && Math.abs(pr.deltaB - (b0 - bHat)) < 0.03, 'Δb ≈ b0 − b̂ = 0.2: ' + (pr.deltaB || 0).toFixed(3));
  ok(pr.points.every(p => p.n >= 5), 'profil ΣN ≥ 5');
  ok(pr.mFrom === 2.0, 'profil en yüksek eşikten başlar');
  const k = bins.findIndex(b => b.m >= pr.mTo + 0.05); ok(k < 0 || bins[k].cumN < 5, 'profil ΣN<5 ilk eşikte biter');
  ok(!X.grRProfile(bins, 5.8, model).ok, '<3 nokta → ok=false'); }

// ── 7. Katman (3): R(M_ref) raporu — aralığın tamamına dayalı gösterge ──
{ const m0 = 2.0, rate0 = 20000, beta = Math.LN10, C = mkClasses(beta, rate0, m0, 6.0, () => 10);
  C.forEach(x => { x.n = Math.round(x.mu); }); const bins = toBins(C);
  const truth = M => rate0 * Math.exp(-beta * (M - m0)), k5 = bins.findIndex(b => b.m >= 5 - 1e-6), obs5 = bins[k5].cumRate;
  let r = X.grConsistency(bins, m0, 5.0, 6.0, DM, truth); ok(r.level === 'ok' && r.rLo <= r.R && r.R <= r.rHi, 'uyum → ok ' + JSON.stringify([r.level, r.rLo, r.rHi]));
  r = X.grConsistency(bins, m0, 5.0, 6.0, DM, M => 16 * truth(M)); ok(r.level === 'red', '16× çok olay → red');
  r = X.grConsistency(bins, m0, 5.0, 6.0, DM, M => 5 * truth(M)); ok(r.level === 'warn', '5× → warn');
  r = X.grConsistency(bins, m0, 5.0, 6.0, DM, () => 3 * obs5); ok(r.level === 'warn', 'nokta R=3 → aralık 3\'ü aşar → warn');
  r = X.grConsistency(bins, m0, 5.0, 6.0, DM, () => obs5 / 12); ok(r.level === 'red' || r.level === 'warn', 'R=1/12 → aralığa göre');
  // Poster benzeri: 9 olay, T = 14.742, R = 12.8 → aralık 10'u kapsar → warn (tek noktada red olurdu)
  const P = [{ m: 4.5, n: 9, T: 14.742 }, { m: 4.6, n: 0, T: 14.742 }, { m: 4.7, n: 0, T: 14.742 }];
  const pb = toBins(P.map(x => ({ lo: x.m, m: x.m + 0.05, T: x.T, n: x.n }))); const lam = pb[0].cumRate;
  r = X.grConsistency(pb, 0.7, 4.5, 4.8, DM, () => 12.8 * lam);
  ok(r.level === 'warn' && Math.abs(r.rLo - 8.80) < 0.05 && Math.abs(r.rHi - 19.0) < 0.1, `poster benzeri R=12.8 → warn, aralık ${r.rLo.toFixed(2)}–${r.rHi.toFixed(2)}`);
  // Sınır durumları
  { const Cs = mkClasses(beta, 100, m0, 6.0, () => 10); Cs.forEach(x => { x.n = x.lo >= 5.5 - 1e-9 ? (x.lo < 5.8 - 1e-9 ? 1 : 0) : Math.round(x.mu); });
    const bs = toBins(Cs); r = X.grConsistency(bs, m0, 5.5, 6.0, DM, truth); ok(r.level === 'fewN' && r.nObs === 3, 'fewN'); }
  r = X.grConsistency(bins, m0, 4.95, 6.0, DM, truth); ok(r.mCmp === 5 && r.shifted, 'sınıf sınırı olmayan M_ref');
  ok(X.grConsistency(bins, m0, 6.5, 6.0, DM, truth).level === 'extrap', 'dışkestirim');
  ok(X.grConsistency(bins, m0, 1.5, 6.0, DM, truth).reason === 'below', 'alt sınır');
  ok(X.grConsistency(bins, m0, 5.95, 6.0, DM, truth).reason === 'top', 'üst sınıf');
  const b2 = bins.map(x => ({ ...x })); b2[b2.length - 1].T = 0; ok(X.grConsistency(b2, m0, 5.0, 6.0, DM, truth).reason === 'T0', 'T=0');
  // Farklı T: λ_obs = Σn/T (eski n/T_ref şişmesi yok)
  const Cd = mkClasses(beta, 20000, m0, 6.0, m => (m < 4.0 - 1e-9 ? 2 : 40)); Cd.forEach(x => { x.n = Math.round(x.mu); }); const bd = toBins(Cd);
  r = X.grConsistency(bd, m0, 3.5, 6.0, DM, truth);
  const kd = bd.findIndex(b => b.m >= 3.5 - 1e-6), old = bd.slice(kd).reduce((a2, b3) => a2 + b3.n, 0) / bd[kd].T;
  ok(Math.abs(r.R - 1) < 0.1 && r.level === 'ok', `farklı T: R=${r.R.toFixed(3)}; eski n/T_ref oranı ${(truth(3.5) / old).toFixed(3)}`); }

// ── 8. p_boot gösterimi (Patch 2): çözünürlük alt sınırı "≤ 0.001" ─────────
ok(X.fmtPboot({ pBoot: 1 / 1000, Bok: 999 }) === '≤ 0.001', 'fmtPboot alt sınır → ≤ 0.001');
ok(X.fmtPboot({ pBoot: 0.143, Bok: 999 }) === '= 0.143', 'fmtPboot olağan değer');
ok(X.fmtPboot({ pBoot: 1 / 991, Bok: 990 }) === '≤ 0.001', 'fmtPboot başarısız tekrarlı alt sınır (B_ok = 990)');
ok(X.fmtPboot({ pBoot: 2 / 1000, Bok: 999 }) === '= 0.002', 'fmtPboot bir tekrar ≥ D → = 0.002');

// ── 9. Poster kalite kontrol özeti (Patch 2, seçenek A): yapılandırılmış, kısa, metin kazımadan ──
{ const q = { gof: { ok: true, reject: true, pBoot: 1 / 1000, Bok: 999, dPerDf: 28.097 }, profile: { ok: true, deltaB: 0.5929 }, level: 'fewN', nObs: 4, mCmp: 5 };
  const cq = { lowMc: [{ row: 1, mc: 1.8, mcData: 2.4 }, { row: 3, mc: 1.9, mcData: 2.4 }, { row: 4, mc: 0.7, mcData: 1.6 }], inv: [{}, {}, {}, {}], small: [{ row: 2, n: 33 }], short: [] };
  const s = X.posterQcSummary(q, cq);   // cq.warn YOK: özet uyarı metinlerinden kazınmıyor
  console.log('Poster özeti (poster verisi):', s, `[${s.length} karakter]`);
  for (const k of ['p_boot ≤ 0.001', 'D/sd = 28.1', 'G-R uyumsuz', 'Δb = 0.59 (b̂ düşük)', 'R(M≥5): n = 4, verilmedi',
    '3 basamak veri Mc altında (1: 1.8<2.4, 3: 1.9<2.4, 4: 0.7<1.6)', '4 dönemde oran tersinmesi', '1 basamakta <50 olay'])
    ok(s.includes(k), 'özet içerir: ' + k);
  ok(s.startsWith('**Kalite kontrol:**'), 'özet başlığı');
  ok(s.length <= 250, 'özet kısa (' + s.length + ' karakter)');
  const s2 = X.posterQcSummary({ gof: { ok: true, reject: false, pBoot: 0.143, Bok: 999, dPerDf: 1.3 }, profile: { ok: true, deltaB: -0.043 }, level: 'ok', R: 1.107, rLo: 0.876, rHi: 1.426, mCmp: 4 }, { lowMc: [], inv: [], small: [], short: [] });
  ok(s2.includes('p_boot = 0.143') && s2.includes('uyumsuzluk saptanmadı') && s2.includes('R(M≥4) = 1.11 [0.876–1.43]') && s2.includes("basamaklar veri Mc'siyle uyumlu"), 'temiz durum özeti: ' + s2);
  const s3 = X.posterQcSummary(null, { capMag: true, lowMc: [], inv: [], small: [], short: [] });
  ok(s3.includes('sorgu kesilmiş') && !s3.includes('uyum testi'), 'model–gözlem yoksa yalnızca tamlık'); }

// ── 10. Poster Sonuçlar yerleşimi (Patch 2b — madde bütünlüğü): hiçbir madde ortasından kesilmez ──
{ const F = X.posterFitItems;
  const used = (hs, gp, r) => hs.slice(0, r.keep).reduce((a, h) => a + h + gp, 0);
  let r = F([40, 30, 20], 2, 100, 13, false); ok(r.keep === 3 && r.dropped === 0, 'hepsi sığar (96 ≤ 100)');
  r = F([40, 30, 20], 2, 95, 13, false); ok(r.keep === 2 && r.dropped === 1 && used([40, 30, 20], 2, r) + 13 <= 95, 'son madde bütün olarak çıkar, not için yer ayrılır');
  r = F([40, 30, 20], 2, 96, 13, true); ok(r.keep === 2 && r.dropped === 1, 'noteAlways: Ana mesaj notu için yer ayrılır');
  r = F([40, 30, 20], 2, 200, 13, true); ok(r.keep === 3 && r.dropped === 0, 'noteAlways ama hepsi + not sığar');
  r = F([120, 10], 2, 100, 13, false); ok(r.keep === 0 && r.dropped === 2, 'ilk madde sığmazsa kesilmez, hiç tutulmaz');
  r = F([], 2, 100, 13, false); ok(r.keep === 0 && r.dropped === 0, 'boş liste');
  r = F([50, 10, 10], 2, 70, 13, false); ok(r.keep === 1, 'sıra korunur: sonraki küçük madde öne alınmaz');
  // özellik testi: rastgele girdilerde tutulanlar + not her zaman sığar, keep + dropped = n
  const rnd = X.mulberry32(20260928); let okAll = true, cnt = 0;
  for (let it = 0; it < 2000; it++) { const n = Math.floor(rnd() * 7), hs = Array.from({ length: n }, () => 5 + Math.floor(rnd() * 80)),
      gp = rnd() < 0.5 ? 2 : 5, avail = 20 + Math.floor(rnd() * 200), nh = 13, na = rnd() < 0.3, q = F(hs, gp, avail, nh, na);
    const u = used(hs, gp, q) + ((q.dropped || na) ? nh : 0);
    if (q.keep + q.dropped !== n || u > avail && q.keep > 0) okAll = false; if (q.dropped) cnt++; }
  ok(okAll, 'özellik (2000 rastgele): tutulan maddeler + not ≤ avail, keep + dropped = n');
  ok(cnt > 100, 'özellik testi taşma durumlarını da kapsar (' + cnt + ')');
  const src2 = require('fs').readFileSync(require('path').join(__dirname, '..', 'index.html'), 'utf8');
  ok(!/wrap\(msg[^\n]*\.slice\(0, 3\)/.test(src2), 'Ana mesaj artık 3 satırda sessizce kesilmiyor'); }

console.log(`PASS ${pass} FAIL ${fail}`); process.exit(fail ? 1 : 0);
