// Birim testleri: Poisson aşılma olasılığı ve tekrarlanma süresi (2026-10-27).
// Fonksiyonlar index.html'den okunur (kopya tutulmaz): grPoissonP, grLambdaSimple, grLambdaWeichert, grPoissonBootSimple,
// grPoissonBootWeichert, grHalfSplitTest ve dayandıkları computeBvalue, weichertFit, weichertExpected, poissonSample, mulberry32, logGamma.
// Denetimler:
//   1. Analitik: P(t) = 1 − e^(−λt), Tr = 1/λ; küçük λ'da sayısal doğruluk (expm1).
//   2. Tutarlılık: tek Mc λ(≥M) = paneldeki G–R doğrusu 10^(a − bM)/T (a = log10 N(≥Mc) + b·Mc); Weichert λ = panel eğrisi (curveFn), kesik/kesilmesiz.
//   3. Sentetik katalog (tek Mc): bilinen λ0 ve b = 1 → λ(≥6) ve P(50 yıl) yansız geri üretilir; bootstrap %95 aralığı kapsaması ≈ %95.
//   4. Sentetik katalog (Weichert, değişken tamlık): aynı denetimler.
//   5. Tamlık denetimi (binom, tek yönlü): kesin değer ve iki senaryo.
// Kullanım (depo kökünde): node scripts/test_poisson_prob.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const line = re => { const m = src.match(re); if (!m) throw new Error('bulunamadı: ' + re); return m[0].replace(/^const /, 'var '); };
const ctx = {}; vm.createContext(ctx);
vm.runInContext([line(/^const GR_QC = [^\n]*$/m), line(/^const GR_POIS = [^\n]*$/m), line(/^const LANCZOS_C = \[[\s\S]*?\];$/m),
  ...['mulberry32', 'logGamma', 'poissonSample', 'bGridRound', 'computeBvalue', 'weichertFit', 'weichertExpected',
      'grPoissonP', 'grLambdaSimple', 'grLambdaWeichert', 'grPctl', 'grPoissonBootSimple', 'grPoissonBootWeichert', 'grHalfSplitTest'].map(fn)].join('\n'), ctx);
const X = ctx;
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
const near = (a, b, tol) => Math.abs(a - b) <= tol;

console.log('\n1. Analitik');
ok(near(X.grPoissonP(0.01, 50), 1 - Math.exp(-0.5), 1e-15), `λ = 0,01/yıl, t = 50 → P = ${X.grPoissonP(0.01, 50).toFixed(6)} (1 − e^−0,5 = 0,393469)`);
ok(near(X.grPoissonP(1e-12, 50), 5e-11, 1e-20), `çok küçük λ (1e-12): P = ${X.grPoissonP(1e-12, 50)} ≈ λt = 5e-11 (expm1 doğruluğu)`);
ok(X.grPoissonP(0, 50) === 0 && X.grPoissonP(null, 50) === null && X.grPoissonP(0.1, 0) === null, 'λ = 0 → P = 0; geçersiz girdi → null');
ok(near(X.grPoissonP(0.02, 1 / 0.02), 1 - Math.exp(-1), 1e-15), 't = Tr → P = 1 − e⁻¹ = 0,632 (Tr içinde olma olasılığı %63, kesinlik değil)');

console.log('\n2. Panelle tutarlılık');
{ const n = 120, T = 40, b = 0.9, Mc = 3.5, a = Math.log10(n) + b * Mc;
  const maxRel = Math.max(...[3.5, 4, 5, 6, 7, 8].map(M => Math.abs(X.grLambdaSimple(n, T, b, Mc, M) / (Math.pow(10, a - b * M) / T) - 1)));
  ok(maxRel < 1e-12, `tek Mc: λ(≥M) = 10^(a − bM)/T, panel a = log10 N(≥Mc) + b·Mc (en büyük göreli fark ${maxRel.toExponential(1)})`);
  ok(near(X.grLambdaSimple(n, T, b, Mc, Mc), n / T, 1e-12), 'tek Mc: λ(≥Mc) = N(≥Mc)/T');
  const curveFn = (rate0, beta, m0, mx) => m => mx === null ? rate0 * Math.exp(-beta * (m - m0))
    : (m >= mx ? 0 : rate0 * (Math.exp(-beta * (m - m0)) - Math.exp(-beta * (mx - m0))) / (1 - Math.exp(-beta * (mx - m0))));   // renderGutenbergRichterCS ile birebir
  let d = 0; for (const mx of [null, 7.5]) for (const M of [3, 4.2, 5, 6.5, 7, 7.49, 7.5, 8]) { const u = X.grLambdaWeichert(2.3, 2.1, 3.0, M, mx), v = curveFn(2.3, 2.1, 3.0, mx)(M); d = Math.max(d, Math.abs(u - v)); }
  ok(d === 0, `Weichert: λ(≥M) panel eğrisiyle (curveFn) birebir, kesilmesiz ve Mx = 7,5 kesik (fark ${d})`);
  ok(X.grLambdaWeichert(2.3, 2.1, 3.0, 7.5, 7.5) === 0 && X.grLambdaWeichert(2.3, 2.1, 3.0, 7.4, 7.5) > 0, 'kesik G–R: M ≥ Mx → λ = 0; Mx altında pozitif'); }

// Sentetik katalog üretici: Mc − ΔM/2'den üstel büyüklükler, ΔM'e yuvarlanmış (Aki–Utsu varsayımı)
function synthSimple(rnd, lam0, T, b, Mc, dm) {
  const n = X.poissonSample(lam0 * T, rnd), beta = b * Math.LN10, m = [];
  for (let i = 0; i < n; i++) m.push(X.bGridRound(Mc - dm / 2 - Math.log(1 - rnd()) / beta, Mc, dm));
  return m;
}
console.log('\n3. Sentetik katalog — tek Mc (λ0 = 2/yıl, M ≥ 3,0; b = 1; T = 60 yıl; ΔM = 0,1)');
{ const lam0 = 2, T = 60, b = 1, Mc = 3.0, dm = 0.1, M = 6.0, t = 50;
  // Gerçek λ(≥6): sürekli büyüklük Mc − ΔM/2'den başlar; sınıf ≥ 6,0 ⇔ sürekli ≥ 5,95
  const lamTrue = lam0 * Math.pow(10, -b * (M - dm / 2 - (Mc - dm / 2))), pTrue = 1 - Math.exp(-lamTrue * t);
  const rnd = (() => { const r = X.mulberry32(777); return r; })();
  const R = 200, est = [], pe = []; let cov = 0, covP = 0;
  for (let r = 0; r < R; r++) {
    const mg = synthSimple(rnd, lam0, T, b, Mc, dm), n = mg.length, bh = X.computeBvalue(mg, Mc, dm);
    const lam = X.grLambdaSimple(n, T, bh, Mc, M), ci = X.grPoissonBootSimple(n, T, bh, Mc, dm, M, t, { B: 400, seed: 1000 + r });
    est.push(Math.log10(lam)); pe.push(X.grPoissonP(lam, t));
    if (ci.lamLo <= lamTrue && lamTrue <= ci.lamHi) cov++; if (ci.pLo <= pTrue && pTrue <= ci.pHi) covP++;
  }
  const mLog = est.reduce((a, v) => a + v, 0) / R, mP = pe.reduce((a, v) => a + v, 0) / R;
  console.log(`     gerçek λ(≥6) = ${lamTrue.toExponential(3)}/yıl, P(50) = ${pTrue.toFixed(4)}; kestirim: ortalama log10 λ = ${mLog.toFixed(3)} (gerçek ${Math.log10(lamTrue).toFixed(3)}), ortalama P = ${mP.toFixed(4)}`);
  console.log(`     bootstrap %95 kapsaması (${R} katalog): λ ${(100 * cov / R).toFixed(1)}%, P ${(100 * covP / R).toFixed(1)}%`);
  ok(Math.abs(mLog - Math.log10(lamTrue)) < 0.05, 'λ(≥6) log ölçekte yansız (|fark| < 0,05)');
  ok(cov / R >= 0.90 && cov / R <= 0.99 && covP / R >= 0.90 && covP / R <= 0.99, 'bootstrap aralığı nominal %95 kapsamaya yakın (%90–99)');
  // Yalnız b'nin ±1,96σ aralığı (sayım belirsizliği yok): M = 6'da (3 birim dışdeğerleme) b baskındır; Mc'de (M = 3,0) b aralığı tek noktaya çöker, yalnız sayım belirsizliği kalır.
  const M2 = 3.0, lamTrue2 = lam0 * Math.pow(10, -b * (M2 - Mc)); let covB6 = 0, covB35 = 0, covBoot35 = 0; const rnd2 = X.mulberry32(778);
  for (let r = 0; r < R; r++) {
    const mg = synthSimple(rnd2, lam0, T, b, Mc, dm), n = mg.length, bh = X.computeBvalue(mg, Mc, dm), se = bh / Math.sqrt(n);
    const bOnly = Mx => [X.grLambdaSimple(n, T, bh + 1.96 * se, Mc, Mx), X.grLambdaSimple(n, T, bh - 1.96 * se, Mc, Mx)];
    const [l6, h6] = bOnly(M), [l35, h35] = bOnly(M2);
    if (l6 <= lamTrue && lamTrue <= h6) covB6++; if (l35 <= lamTrue2 && lamTrue2 <= h35) covB35++;
    const ci = X.grPoissonBootSimple(n, T, bh, Mc, dm, M2, t, { B: 400, seed: 3000 + r }); if (ci.lamLo <= lamTrue2 && lamTrue2 <= ci.lamHi) covBoot35++;
  }
  console.log(`     yalnız b aralığı kapsaması: M ≥ 6 → ${(100 * covB6 / R).toFixed(1)}% (b baskın); M ≥ 3,0 (= Mc) → ${(100 * covB35 / R).toFixed(1)}%; ortak bootstrap M ≥ 3,0 → ${(100 * covBoot35 / R).toFixed(1)}%`);
  ok(covB35 / R < 0.85 && covBoot35 / R >= 0.90, 'Mc düzeyinde yalnız b aralığı sayım belirsizliğini kaçırır; sayım bileşenli bootstrap nominale yakın (ChatGPT notu: b aralığı tek başına yetmez)'); }

console.log('\n4. Sentetik katalog — Weichert, değişken tamlık (M ≥ 3: son 30 yıl; M ≥ 4: 80 yıl; M ≥ 5: 200 yıl; λ(≥3) = 5/yıl; b = 1)');
{ const DM = 0.1, b = 1, beta = b * Math.LN10, lam0 = 5, m0 = 3.0, M = 6.5, t = 50;
  const Tof = lo => lo >= 5 - 1e-9 ? 200 : lo >= 4 - 1e-9 ? 80 : 30;
  const lamGE = m => lam0 * Math.exp(-beta * (m - m0)), lamTrue = lamGE(M), pTrue = 1 - Math.exp(-lamTrue * t);
  const rnd = X.mulberry32(4242), R = 200; let cov = 0, covP = 0; const est = [];
  for (let r = 0; r < R; r++) {
    const cls = []; for (let k = 30; k < 80; k++) { const lo = +(k * DM).toFixed(2), T = Tof(lo); cls.push({ m: lo + DM / 2, lo, T, n: X.poissonSample(T * (lamGE(lo) - lamGE(lo + DM)), rnd) }); }
    const wf = X.weichertFit(cls); if (!wf) continue;
    const lamOf = f => X.grLambdaWeichert(f.rate0, f.beta, m0, M, null);
    const lam = lamOf(wf), ci = X.grPoissonBootWeichert(cls, wf, lamOf, t, { B: 400, seed: 5000 + r });
    est.push(Math.log10(lam)); if (ci.lamLo <= lamTrue && lamTrue <= ci.lamHi) cov++; if (ci.pLo <= pTrue && pTrue <= ci.pHi) covP++;
  }
  const mLog = est.reduce((a, v) => a + v, 0) / est.length;
  console.log(`     gerçek λ(≥6,5) = ${lamTrue.toExponential(3)}/yıl, P(50) = ${pTrue.toFixed(4)}; ortalama log10 λ = ${mLog.toFixed(3)} (gerçek ${Math.log10(lamTrue).toFixed(3)}); kapsama λ ${(100 * cov / R).toFixed(1)}%, P ${(100 * covP / R).toFixed(1)}%`);
  ok(Math.abs(mLog - Math.log10(lamTrue)) < 0.05, 'Weichert λ(≥6,5) log ölçekte yansız');
  ok(cov / R >= 0.90 && cov / R <= 0.99 && covP / R >= 0.90 && covP / R <= 0.99, 'Weichert bootstrap aralığı nominal %95 kapsamaya yakın (%90–99)'); }

console.log('\n5. Tamlık denetimi (binom, tek yönlü)');
{ const h = X.grHalfSplitTest(Array.from({ length: 10 }, (_, i) => 60 + i), 0, 100);
  ok(h.n1 === 0 && near(h.p, 1 / 1024, 1e-12), `n = 10, ilk yarıda 0 → p = ${h.p.toExponential(3)} (kesin 1/1024)`);
  const rnd = X.mulberry32(9), uni = Array.from({ length: 400 }, () => rnd() * 100), front = Array.from({ length: 400 }, () => (rnd() < 0.25 ? rnd() * 50 : 50 + rnd() * 50));
  const hu = X.grHalfSplitTest(uni, 0, 100), hf = X.grHalfSplitTest(front, 0, 100);
  ok(hu.p > 0.01 && hf.p < 1e-6, `tekdüze katalog p = ${hu.p.toFixed(3)} (uyarı yok); başı eksik katalog (ilk yarı %25) p = ${hf.p.toExponential(1)} (uyarı)`); }

console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
