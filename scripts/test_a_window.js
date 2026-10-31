// Birim testleri: a(t) — pencere olay hızı (Öncel & Wilson 2007, Eş. 3: N = n/T = 10^a) (2026-10-31).
// Fonksiyonlar index.html'den okunur: aWinFields, aChi2Q, aWinValue, aPearson, aSeriesFrom.
// Denetimler:
//   1. χ² nicelikleri (Wilson–Hilferty) kesin değerlere karşı (seri ile hesaplanan düzenli eksik gama).
//   2. Sabit hızlı Poisson süreci: a ≈ log₁₀ λ (yanlılık), %95 aralık kapsaması (örtüşmeyen pencereler).
//   3. Hız iki katına çıkınca a'daki sıçrama ≈ log₁₀ 2 = 0,301.
//   4. a_GR = a + b·Mc kimliği; sabit n'de a_GR ile b'nin ilişkisi (hız sabitken bile güçlü korelasyon) — a_GR neden ayrı gösterge değil.
//   5. b–a korelasyonu: H0 altında (sabit hız, sabit b) örtüşmeyen pencerelerle p < 0,05 oranı ≈ %5; örtüşen pencerelerin r dağılımı daha geniş.
//   6. Tamlık basamakları: Mc'si karışık pencere işaretlenir, a hesaplanmaz.
//   8. Öz-ilişki düzeltmesi (Bartlett n_eff): analitik değer; bağımsız AR(1) çiftlerinde ham ve düzeltilmiş testin hata oranı.
//   7. Kümelenme (artçı benzeri): %95 aralık Poisson varsayımına dayanır; kümelenmiş süreçte uzun dönem hızı kapsama oranı düşer (ölçülür).
// Kullanım (depo kökünde): node scripts/test_a_window.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const ctx = {}; vm.createContext(ctx);
vm.runInContext(['aWinFields', 'aChi2Q', 'aWinValue', 'aPearson', 'aSeriesFrom', 'aLag1', 'aNeffTest'].map(fn).join('\n'), ctx);
const X = ctx;
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
// Tohumlu üreteç (mulberry32)
const rng = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const Y = 365.25 * 864e5;
// Sentetik katalog: zaman (yıl) üstel bekleme, büyüklük G–R (Mc − ΔM/2'den üstel, ΔM = 0,1'e yuvarlanmış)
function katalog(rnd, segs, b, Mc) {   // segs: [[süre yıl, λ/yıl], ...]
  const ev = []; let t0 = 0; const beta = b * Math.LN10;
  for (const [d, lam] of segs) { let t = t0; for (;;) { t += -Math.log(1 - rnd()) / lam; if (t >= t0 + d) break; const m = Math.round((Mc - 0.05 - Math.log(1 - rnd()) / beta) * 10) / 10; ev.push({ t: t * Y, m: Math.max(Mc, m), mc: Mc }); } t0 += d; }
  return ev;
}
// b(t) serisi (aynı pencereleme: n ardışık olay, adım; Aki–Utsu b; zaman damgası ortalama)
function seri(ev, n, step, Mc) {
  const out = [];
  for (let i = 0; i + n <= ev.length; i += step) { const w = ev.slice(i, i + n), mm = w.reduce((a, e) => a + e.m, 0) / n;
    out.push({ t: w.reduce((a, e) => a + e.t, 0) / n, b: Math.LOG10E / (mm - Mc + 0.05), t0: w[0].t, t1: w[n - 1].t, span: w[n - 1].t - w[0].t, ...X.aWinFields(w) }); }
  return out;
}

console.log('\n1. χ² nicelikleri');
{ // kesin: P(k/2, x/2) = p, düzenli eksik gama serisiyle ikiye bölme
  const lgam = x => { const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]; let y = x, t = x + 5.5; t -= (x + 0.5) * Math.log(t); let s = 1.000000000190015; for (const v of c) s += v / ++y; return -t + Math.log(2.5066282746310005 * s / x); };
  const P = (a, x) => { let ap = a, sum = 1 / a, d = sum; for (let i = 0; i < 5000; i++) { ap++; d *= x / ap; sum += d; if (d < sum * 1e-16) break; } return sum * Math.exp(-x + a * Math.log(x) - lgam(a)); };
  const Q = (p, k) => { let lo = 0, hi = 10 * k; for (let i = 0; i < 200; i++) { const m = (lo + hi) / 2; if (P(k / 2, m / 2) < p) lo = m; else hi = m; } return (lo + hi) / 2; };
  let worst = 0; for (const n of [20, 50, 100, 200]) for (const p of [0.025, 0.975]) { const k = 2 * (n - 1), e = Q(p, k), a = X.aChi2Q(p, k); worst = Math.max(worst, Math.abs(a / e - 1)); }
  ok(worst < 2e-3, `Wilson–Hilferty χ² nicelikleri (n = 20–200, p = 0,025 ve 0,975): en büyük göreli hata ${worst.toExponential(1)} (log₁₀'da < 0,001)`); }

console.log('\n2. Sabit hız (λ = 20/yıl, b = 1, Mc = 3, 300 yıl; n = 100)');
{ const lam = 20, rnd = rng(11), R = 40; let cov = 0, tot = 0, bias = 0;
  for (let r = 0; r < R; r++) { const s = seri(katalog(rnd, [[300, lam]], 1, 3), 100, 100, 3), a = X.aSeriesFrom(s, 100, 3, null);
    a.forEach(q => { tot++; bias += q.a - Math.log10(lam); if (q.lo <= Math.log10(lam) && Math.log10(lam) <= q.hi) cov++; }); }
  const se = Math.sqrt(0.95 * 0.05 / tot);
  console.log(`     ${R} sentetik katalog (tohum 11), toplam ${tot} örtüşmeyen pencere (adım = n = 100): ortalama a − log₁₀λ = ${(bias / tot).toFixed(4)} (n/T tanımının beklenen yanlılığı log₁₀(100/99) = 0,0044); kapsama %${(100 * cov / tot).toFixed(1)} (± %${(196 * se).toFixed(1)})`);
  ok(Math.abs(bias / tot - Math.log10(100 / 99)) < 0.01, 'a yansız (n/T tanımının küçük yanlılığı dışında)');
  ok(Math.abs(cov / tot - 0.95) < 2.6 * se, '%95 aralık nominal kapsamada'); }

console.log('\n3. Hız değişimi (100 yıl λ = 10, sonra 100 yıl λ = 20)');
{ const rnd = rng(12), s = seri(katalog(rnd, [[100, 10], [100, 20]], 1, 3), 100, 10, 3), a = X.aSeriesFrom(s, 100, 3, null);
  const once = a.filter(q => q.t / Y < 90), sonra = a.filter(q => q.t / Y > 110), m = v => v.reduce((x, q) => x + q.a, 0) / v.length;
  const d = m(sonra) - m(once); ok(Math.abs(d - Math.log10(2)) < 0.05, `a sıçraması ${d.toFixed(3)} ≈ log₁₀ 2 = 0,301`); }

console.log('\n4. a_GR = a + b·Mc ve b ile bağı (sabit hız)');
{ const rnd = rng(13), s = seri(katalog(rnd, [[400, 20]], 1, 3), 100, 10, 3), a = X.aSeriesFrom(s, 100, 3, null);
  ok(a.every(q => Math.abs(q.aGR - (q.a + q.b * 3)) < 1e-12), 'a_GR = a + b·Mc kimliği');
  const rGR = X.aPearson(a.map(q => q.b), a.map(q => q.aGR)), rA = X.aPearson(a.map(q => q.b), a.map(q => q.a));
  console.log(`     sabit hızda (b ve hız gerçekte sabit): r(b, a_GR) = ${rGR.r.toFixed(2)}, r(b, a) = ${rA.r.toFixed(2)}`);
  ok(rGR.r > 0.9 && Math.abs(rA.r) < 0.3, 'a_GR, b ile yapısal olarak bağlı (r > 0,9); a = log₁₀(n/T) bağlı değil — panelde a_GR ayrı gösterge olarak çizilmez'); }

console.log('\n5. b–a korelasyonunun geçerliliği (H0: sabit hız, sabit b; 300 katalog)');
{ const rnd = rng(14), R = 300; let rejInd = 0, nInd = 0; const rOv = [], rIn = [];
  for (let r = 0; r < R; r++) { const s = seri(katalog(rnd, [[120, 20]], 1, 3), 100, 10, 3), a = X.aSeriesFrom(s, 100, 3, null);
    const ind = a.filter((q, i) => i % 10 === 0), pi = X.aPearson(ind.map(q => q.b), ind.map(q => q.a)), po = X.aPearson(a.map(q => q.b), a.map(q => q.a));
    if (pi) { nInd++; if (pi.p < 0.05) rejInd++; rIn.push(pi.r); } if (po) rOv.push(po.r); }
  const sd = v => { const m = v.reduce((a, x) => a + x, 0) / v.length; return Math.sqrt(v.reduce((a, x) => a + (x - m) ** 2, 0) / (v.length - 1)); };
  // Örtüşen pencerelerle Fisher p'si kullanılsaydı: aynı r, ~10 kat fazla "n" ile
  let rejOv = 0; for (const r of rOv) { const n = 230, z = Math.atanh(r) * Math.sqrt(n - 3); if (Math.abs(z) > 1.96) rejOv++; }
  console.log(`     örtüşmeyen pencereler (≈ 23): p < 0,05 oranı %${(100 * rejInd / nInd).toFixed(1)}; örtüşen pencereler bağımsızmış gibi sayılsaydı: %${(100 * rejOv / rOv.length).toFixed(1)}`);
  ok(rejInd / nInd < 0.09, 'örtüşmeyen pencerelerle test boyutu nominale yakın (≤ %9)');
  ok(rejOv / rOv.length > 2 * rejInd / nInd, 'örtüşen pencereleri bağımsız saymak sahte anlamlılık üretir — panelde örtüşen r için p verilmez'); }

console.log('\n6. Tamlık basamakları: karışık Mc penceresi');
{ const w = [{ t: 0, mc: 4.5 }, { t: 1, mc: 4.5 }, { t: 2, mc: 4.0 }], f = X.aWinFields(w);
  ok(f.mcLo === 4.0 && f.mcHi === 4.5 && f.w0 === 0 && f.w1 === 2, 'aWinFields: pencere sınırları ve Mc aralığı');
  const s = [{ t: 1, b: 1, w0: 0, w1: Y, mcLo: 4.5, mcHi: 4.5 }, { t: 2, b: 1, w0: 0, w1: Y, mcLo: 4.0, mcHi: 4.5 }], a = X.aSeriesFrom(s, 100, null, {});
  ok(a[0].mc === 4.5 && !a[0].mixed && a[1].mixed && a[1].mc === null && a[1].aGR === null, 'tek Mc penceresi çizilir; karışık pencere işaretlenir, a_GR hesaplanmaz'); }

console.log('\n7. Kümelenme: %95 aralığın Poisson varsayımı (uzun dönem hızı λ = 20/yıl, 300 yıl, 40 katalog)');
{ // Ana olaylar Poisson (μ), her birinin K ~ Poisson(m) artçısı, gecikme üstel (ortalama 0,02 yıl ≈ 7 gün). Uzun dönem hızı λ = μ(1 + m).
  const kume = (rnd, mu, m, d) => { const ev = []; const pois = l => { let k = 0, p = Math.exp(-l), c = p, u = rnd(); while (u > c) { k++; p *= l / k; c += p; } return k; };
    let t = 0; for (;;) { t += -Math.log(1 - rnd()) / mu; if (t >= d) break; ev.push(t); const K = pois(m); for (let j = 0; j < K; j++) { const ta = t - 0.02 * Math.log(1 - rnd()); if (ta < d) ev.push(ta); } }
    return ev.sort((a, b) => a - b).map(x => ({ t: x * Y, m: 3 + Math.round(-Math.log(1 - rnd()) / Math.LN10 * 10) / 10, mc: 3 })); };
  const out = [];
  for (const [ad, mu, m] of [['kümelenmesiz (m = 0)', 20, 0], ['orta (m = 1)', 10, 1], ['güçlü (m = 4)', 4, 4]]) {
    const rnd = rng(15), lam = mu * (1 + m); let cov = 0, tot = 0;
    for (let r = 0; r < 40; r++) X.aSeriesFrom(seri(kume(rnd, mu, m, 300), 100, 100, 3), 100, 3, null).forEach(q => { tot++; if (q.lo <= Math.log10(lam) && Math.log10(lam) <= q.hi) cov++; });
    out.push([ad, cov / tot, tot]); }
  console.log(`     uzun dönem λ'yı kapsama: ${out.map(([a, c, n]) => `${a} %${(100 * c).toFixed(1)} (${n} pencere)`).join('; ')}`);
  ok(Math.abs(out[0][1] - 0.95) < 0.02 && out[1][1] < out[0][1] - 0.05 && out[2][1] < out[1][1], 'kümelenme arttıkça kapsama düşer: aralık yalnız Poisson (bağımsız olay) varsayımında %95; artçılar ayıklanmadıysa dar kalır'); }

console.log('\n8. Öz-ilişki düzeltmesi (Bartlett n_eff)');
{ const t = X.aNeffTest(0.79, 22, 0.73, 0.80);
  ok(Math.abs(t.neff - 22 * (1 - 0.584) / (1 + 0.584)) < 1e-9 && Math.abs(t.p - 0.074) < 0.002, `n = 22, ρ_a = 0,73, ρ_b = 0,80, r = 0,79: n_eff = ${t.neff.toFixed(2)}, p = ${t.p.toFixed(3)} (raporla aynı: 5,8 ve ≈ 0,07)`);
  ok(X.aNeffTest(0.5, 10, -0.5, 0.6).neff === 10 && X.aNeffTest(0.65, 8, 0.6, 0.62).p === null && X.aNeffTest(0.5, 10, null, 0.5).p === null, 'ρ_a·ρ_b < 0 → n_eff = n (şişirilmez); n_eff < 5 → p verilmez; öz-ilişki yoksa p verilmez');
  const segs = [[{ a: 1 }, { a: 2 }, { a: 3 }], [{ a: 5 }, { a: 4 }, { a: 6 }, { a: 8 }]], l = X.aLag1(segs, q => q.a), l4 = X.aLag1([[{ a: 1 }, { a: 2 }, { a: 3 }], [{ a: 5 }, { a: 4 }, { a: 6 }]], q => q.a);
  ok(l && l.n === 5 && l4 === null, 'aLag1: çiftler yalnız segment içinde (2 + 3 = 5 çift); 4 çiftte hesaplanmaz');
  // Bağımsız iki AR(1) serisi (gerçek korelasyon 0): α = 0,05'te reddetme oranı
  const rnd = rng(21), g = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
  const ar = (n, f) => { const x = [g() / Math.sqrt(1 - f * f)]; for (let i = 1; i < n; i++) x.push(f * x[i - 1] + g()); return x; };
  const sonuc = [];
  for (const [n, f] of [[13, 0], [13, 0.8], [22, 0], [22, 0.8], [50, 0.8]]) { let ham = 0, duz = 0, test = 0; const R = 3000;
    for (let i = 0; i < R; i++) { const x = ar(n, f), y = ar(n, f), seg = [x.map((v, j) => ({ a: v, b: y[j] }))], r = X.aPearson(x, y);
      const ra = X.aLag1(seg, q => q.a), rb = X.aLag1(seg, q => q.b), t2 = X.aNeffTest(r.r, n, ra ? ra.r : null, rb ? rb.r : null);
      if (r.p < 0.05) ham++; if (t2.p !== null) { test++; if (t2.p < 0.05) duz++; } }
    sonuc.push([n, f, ham / R, duz / R, test / R]); }
  console.log('     bağımsız AR(1) çiftleri (3000 tekrar): ' + sonuc.map(([n, f, h, d, tt]) => `n = ${n}, φ = ${f}: ham %${(100 * h).toFixed(1)}, düzeltilmiş %${(100 * d).toFixed(1)} (test edilebilen %${(100 * tt).toFixed(0)})`).join('; '));
  ok(sonuc.every(([, , , d]) => d <= 0.065) && sonuc.filter(([, f]) => f === 0.8).every(([, , h]) => h > 0.15), 'düzeltilmiş testin hata oranı ≤ %6,5; φ = 0,8\'de ham test %15\'in üstünde sahte anlamlılık üretiyor'); }

console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
