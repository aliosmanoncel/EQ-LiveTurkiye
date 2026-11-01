// Birim testleri (2026-11-01): bölge karşılaştırmasında Poisson aşılma olasılığı (cmpProbBoot, cmpProbAt, cmpProb, cmpProbWarn, cmpPc).
// Fonksiyonlar index.html'den okunur (kopya tutulmaz). Plan: analysis/poisson_olasilik/PLAN_olasilik_modulu.md §2 tutarlılık testleri (a)–(d).
// Denetimler:
//   (a) P(≥6; t) = 1 − e^(−t/tr6): tablodaki tekrarlanma süresi (cmpStats) ile aynı λ.
//   (b) Tablo hücresi ile eğri noktası aynı (aynı fonksiyon ve çekilişler).
//   (c) Bootstrap: aynı tohumla tek (M, t) için G–R panelindeki grPoissonBootSimple ile birebir aynı %95 sınırları.
//   (d) Monotonluk: P, M arttıkça azalır, t arttıkça artar; band P'yi içerir.
//   (e) Sentetik katalog: bilinen λ0 ve b = 1 ile %95 bandının kapsaması ≈ %95 (birkaç (M, t)).
//   (f) Uyarılar ve biçim: GK74 açık/kapalı/bilinmiyor, tür geçişi, mb doygunluğu, ekstrapolasyon; yüzde biçimi.
//   (g) Yayın şekli: eğri noktaları tablo hücreleriyle aynı; eğri bölgenin Mc'sinden başlar; Mmax üstü ekstrapolasyon; süreler 10/25/50/100;
//       SVG boyutu (çift sütun 493 pt, tek sütun 241 pt), eksen başlıkları, lejant; altyazı (B, tohum, 'not an earthquake forecast').
//   (h) Aşama 2: bant etiketi '±1σ' içermez; ekstrapolasyon sınıfı Tr/T (≤ 1, ≤ exK, > exK), sınır büyüklükleri kapalı biçimle tutarlı,
//       Marmara benzeri örnek (Tr(≥7)/T ≈ 10,1) 'yuksek'; uyarı, tablo işaretleri, şekil (Tr = T çizgisi, Tr > 10T zemini), altyazı, CSV sütunları.
//   (a') Doymamış değerde tutarlılık: P(≥7; 10 yıl) = 1 − e^(−10·λ(≥7)), %0–100 arasında.
// Kullanım (depo kökünde): node scripts/test_cmp_prob.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const line = re => { const m = src.match(re); if (!m) throw new Error('bulunamadı: ' + re); return m[0].replace(/^const /, 'var '); };
const ctx = { document: { getElementById: () => ({ value: '1e4' }) }, B_CI_METHOD: 'normal', B_GRID_MODE: 'sinif' }; vm.createContext(ctx);   // B_GRID_MODE: uygulamanın varsayılanı (URL ?bgrid=ham yoksa)
vm.runInContext([line(/^const GR_POIS = [^\n]*$/m), line(/^const GR_QC = [^\n]*$/m), line(/^const CMP_PROB = [^\n]*$/m), line(/^const CMP_MAX = [^\n]*$/m),
  ...['mulberry32', 'logGamma', 'poissonSample', 'bGridRound', 'bGridVals', 'computeBvalue', 'bConfidence95', 'bCiFields', 'grPoissonP', 'grLambdaSimple', 'grPctl',
      'bGridOffCount', 'grPoissonBootSimple', 'cmpStats', 'cmpProbBoot', 'cmpProbAt', 'cmpProb', 'cmpProbWarn', 'cmpProbExtrap', 'cmpProbMk', 'cmpTr', 'cmpTrT', 'cmpPc', 'cmpRng', 'cmpProbCurves', 'cmpProbFigRange', 'cmpProbFigSvg', 'cmpProbBTxt', 'cmpProbFigCaption'].map(fn), line(/^const CMP_FIG = [^\n]*$/m), line(/^const CMP_EX = \{[\s\S]*?\} \};$/m), 'var cmpProbFigRangeV = { lo: 4, hi: 8 };', "var cmpProbFigBand = '95';"].join('\n').replace(/^var CMP_PROB = (.*), cmpProbCache = new Map\(\);$/m, 'var CMP_PROB = $1; var cmpProbCache = new Map();'), ctx);
vm.runInContext(src.match(/^const LANCZOS_C = \[[\s\S]*?\];$/m)[0].replace(/^const /, 'var '), ctx);
const X = ctx; let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
const YIL = 365.25 * 864e5;
// Sentetik kayıt: T yıl, λ0 olay/yıl M ≥ Mc, b; büyüklükler 0,1 ızgarasında
function kayit(seed, T, lam0, b, Mc, extra) { const r = X.mulberry32(seed), n = X.poissonSample(lam0 * T, r), beta = b * Math.LN10, mags = [];
  for (let i = 0; i < n; i++) mags.push(X.bGridRound(Mc - 0.05 - Math.log(1 - r()) / beta, Mc, 0.1));
  return Object.assign({ name: 'S', t0: 0, t1: T * YIL, Mc, dm: 0.1, area: 1e5, cLat: 0, mags, types: { ml: n } }, extra || {}); }
{ // (a) tr6 ile tutarlılık
  const r = kayit(7, 40, 30, 1.0, 4.0), s = X.cmpStats(r), p = X.cmpProb(r, s), c = p.cell(6, 50);
  ok(Math.abs(c.lam - 1 / s.tr6) / c.lam < 1e-12 && Math.abs(c.P - (1 - Math.exp(-50 / s.tr6))) < 1e-12, `(a) λ(≥6) = 1/tr6 (${c.lam.toFixed(5)} = ${(1 / s.tr6).toFixed(5)}); P(≥6; 50 yıl) = 1 − e^(−50/tr6) = ${(100 * c.P).toFixed(2)}%`);
  // (b) aynı hücre iki kez (tablo ve eğri aynı fonksiyonu ve önbellekteki çekilişleri kullanır)
  const c2 = X.cmpProb(r, s).cell(6, 50); ok(c2.P === c.P && c2.lo === c.lo && c2.hi === c.hi && X.cmpProbBoot(s.n, s.T, s.b, r.Mc, 0.1) === p.bt, '(b) tablo hücresi = eğri noktası (aynı çekilişler, önbellek)');
  // (c) G–R panelinin bootstrap'ıyla aynı
  for (const [M, t] of [[5, 10], [6, 50], [7, 100]]) { const g = X.grPoissonBootSimple(s.n, s.T, s.b, r.Mc, 0.1, M, t), cc = p.cell(M, t);
    ok(g.B === p.bt.B && g.nFail === p.bt.nFail && Math.abs(g.pLo - cc.lo) < 1e-15 && Math.abs(g.pHi - cc.hi) < 1e-15, `(c) M ≥ ${M}, t = ${t}: %95 [${(100 * cc.lo).toFixed(3)}–${(100 * cc.hi).toFixed(3)}] = grPoissonBootSimple (B = ${g.B}, tohum ${g.seed})`); }
  // (d) monotonluk ve bandın P'yi içermesi
  let mono = true, icinde = true; for (const t of [10, 30, 50, 100]) { let prev = 2; for (let M = 4.0; M <= 8.0 + 1e-9; M += 0.1) { const q = p.cell(+M.toFixed(1), t); if (!(q.P <= prev + 1e-15)) mono = false; prev = q.P; if (!(q.lo <= q.P + 1e-12 && q.P <= q.hi + 1e-12 && q.l16 >= q.lo - 1e-12 && q.h84 <= q.hi + 1e-12)) icinde = false; } }
  for (const M of [5, 6, 7]) { let prev = -1; for (const t of [10, 30, 50, 100]) { const q = p.cell(M, t); if (!(q.P >= prev)) mono = false; prev = q.P; } }
  ok(mono, '(d) P, M arttıkça azalıyor ve t arttıkça artıyor'); ok(icinde, '(d) %95 bandı P\'yi ve %68 bandını içeriyor'); }
{ // (e) kapsama: 200 sentetik katalog, T = 30 yıl, λ0(≥4) = 20/yıl, b = 1
  const K = 200, Mc = 4.0, lam0 = 20, T = 30, hedef = [[5, 10], [6, 30], [7, 100]], say = hedef.map(() => 0);
  for (let k = 0; k < K; k++) { const r = kayit(1000 + k, T, lam0, 1.0, Mc), s = X.cmpStats(r), p = X.cmpProb(r, s);
    hedef.forEach(([M, t], j) => { const P0 = 1 - Math.exp(-lam0 * Math.pow(10, -(M - Mc)) * t), c = p.cell(M, t); if (c.lo <= P0 && P0 <= c.hi) say[j]++; }); }
  hedef.forEach(([M, t], j) => ok(say[j] / K >= 0.91 && say[j] / K <= 0.99, `(e) kapsama M ≥ ${M}, t = ${t} yıl: %${(100 * say[j] / K).toFixed(1)} (200 katalog; beklenen ≈ %95)`)); }
{ // (f) uyarılar ve biçim
  const s = { Mmax: 6.4 }, w = (o) => X.cmpProbWarn(Object.assign({ types: { ml: 10 } }, o), s);
  ok(/GK74 açık: bağımsızlık garanti değil/.test(w({ gk74: true, mcU: null, turU: null })) && /GK74 kapalı: artçılar dahil/.test(w({ gk74: false, mcU: null, turU: null })) && /GK74 durumu bilinmiyor/.test(w({})), '(f) GK74 açık / kapalı / bilinmiyor (eski kayıt)');
  ok(/büyüklük türü geçişi: MD → ML/.test(w({ gk74: true, mcU: null, turU: 'MD → ML (2010–2011)' })) && /değerlendirilemedi/.test(w({ gk74: true, mcU: null, turU: 'değerlendirilemedi' })) && /tamlık \(Mc\) uyarısı var/.test(w({ gk74: true, mcU: 'tekMc', turU: null })), '(f) tür geçişi, değerlendirilemedi ve Mc uyarısı');
  ok(/mb %77: mb doygunluğu/.test(X.cmpProbWarn({ gk74: true, mcU: null, turU: null, types: { mb: 77, mw: 23 } }, s)) && /ekstrapolasyon/.test(w({ gk74: true, mcU: null, turU: null })), '(f) mb doygunluğu (≥ %50) ve M > Mmax ekstrapolasyonu');
  ok(X.cmpPc(0.85123) === '85,1' && X.cmpPc(0.9996) === '&gt; 99,9' && X.cmpPc(0.0004) === '&lt; 0,1' && X.cmpPc(null) === '—', '(f) yüzde biçimi (85,1 / > 99,9 / < 0,1 / —)');
  ok(X.cmpProb({ Mc: null, mags: [] }, { b: null }) === null && X.cmpProb({ Mc: 4, dm: 0.1 }, { b: 1, T: 10, n: 5, Mmax: 5 }) === null, '(f) b ya da N(≥Mc) < 10 yoksa olasılık hesaplanmaz'); }
{ // (a') doymamış değer
  const r = kayit(7, 40, 30, 1.0, 4.0), s = X.cmpStats(r), c = X.cmpProb(r, s).cell(7, 10), lam7 = s.n / s.T * Math.pow(10, -s.b * 3);
  ok(c.P > 0.05 && c.P < 0.95 && Math.abs(c.P - (1 - Math.exp(-10 * lam7))) < 1e-12 && c.lo < c.P && c.P < c.hi, `(a') P(≥7; 10 yıl) = ${(100 * c.P).toFixed(2)}% [${(100 * c.lo).toFixed(2)}–${(100 * c.hi).toFixed(2)}] = 1 − e^(−10·λ(≥7)); doymamış`); }
{ // (g) yayın şekli
  const r1 = Object.assign(kayit(11, 30, 20, 1.0, 4.0), { name: 'Bölge <A>', src: 'test', gk74: true }), r2 = Object.assign(kayit(12, 30, 8, 0.9, 4.5), { name: 'B', src: 'test', gk74: false });
  X.CMP = [r1, r2]; const S = X.CMP.map(X.cmpStats), PR = X.CMP.map((r, i) => X.cmpProb(r, S[i]));
  const svg = X.cmpProbFigSvg(S, PR, { en: true }), R = X.cmpProbFigRange(), C = X.cmpProbCurves(r1, S[0], PR[0]);
  ok(/width="493pt"/.test(svg) && /viewBox="0 0 493 /.test(svg), 'çift sütun genişliği 493 pt (174 mm)');
  ok(JSON.stringify(Object.keys(C).map(Number)) === JSON.stringify([10, 25, 50, 100]) && [10, 25, 50, 100].every(t => svg.includes(`t = ${t} yr`)), 'süreler 10/25/50/100 yıl, lejantta');
  const q = C[50].find(z => Math.abs(z.M - 6) < 1e-9), cell = PR[0].cell(6, 50);
  ok(q && q.P === cell.P && q.lo === cell.lo && q.hi === cell.hi, 'eğri noktası (M 6, t 50) = tablo hücresi');
  ok(Math.abs(C[10][0].M - r1.Mc) < 1e-9 && C[10].every(z => z.M >= r1.Mc - 1e-9), `eğri bölgenin Mc'sinden (${r1.Mc}) başlıyor`);
  ok(C[10].some(z => z.ex) && C[10].filter(z => z.ex).every(z => z.M > S[0].Mmax) && /stroke-dasharray="3 2"/.test(svg) && /max,obs/.test(svg), `Mmax (${S[0].Mmax}) üstü ekstrapolasyon kesikli; Mmax işaretli`);
  ok(/Magnitude<\/text>|Magnitude, M/.test(svg) && /Probability of exceedance \(%\)/.test(svg) && /\(a\) Bölge &lt;A&gt;/.test(svg) && /\(b\) B/.test(svg), 'eksen başlıkları, panel harfleri, ad kaçışı');
  ok(R.lo === 4 && R.hi >= 8, `x aralığı ${R.lo}–${R.hi}`);
  const tr = X.cmpProbFigSvg(S, PR, { en: false }); ok(/Aşılma olasılığı \(%\)/.test(tr) && /t = 10 yıl/.test(tr), 'Türkçe sürüm');
  X.CMP = [r1]; const S1 = [S[0]], one = X.cmpProbFigSvg(S1, [PR[0]], { en: true }); ok(/width="241pt"/.test(one), 'tek bölge: tek sütun 241 pt (85 mm)');
  X.CMP = [r1, r2]; const cap = X.cmpProbFigCaption(S, PR, true), capTr = X.cmpProbFigCaption(S, PR, false);
  { const s68 = X.cmpProbFigSvg(S, PR, { en: true, band: '68' }), c68 = X.cmpProbFigCaption(S, PR, true, '68');
    const c68tr = X.cmpProbFigCaption(S, PR, false, '68'), s68tr = X.cmpProbFigSvg(S, PR, { en: false, band: '68' });
    ok(s68 !== svg && /16th–84th percentile</.test(s68) && /16\.–84\. yüzdelik</.test(s68tr) && /95% interval/.test(svg) && /16th–84th percentile range/.test(c68) && /16\.–84\. yüzdelik aralığı/.test(c68tr) && /95% intervals/.test(cap), 'bant seçeneği: %95 (varsayılan) ve 16.–84. yüzdelik; lejant ve altyazı bandı belirtiyor');
    ok(![svg, s68, s68tr, cap, c68, c68tr, capTr].some(t => /1σ|1 σ|sigma/i.test(t)), "(h) şekil ve altyazıda '±1σ' yok (bootstrap yüzdeliği σ olarak adlandırılmıyor)");
    ok(/>0\.01<\/text>/.test(svg), 'y ekseni %0,01\'e iniyor (Khodaverdian vd. 2016 gibi düşük olasılık kuyruğu)'); }
  ok(/B = 1000, seed 20261027/.test(cap) && /not an earthquake forecast/.test(cap) && /GK74 on/.test(cap) && /GK74 off/.test(cap) && /deprem tahmini değildir/.test(capTr), 'altyazı: bootstrap B ve tohum, GK74 durumu, "tahmin değildir" (EN/TR)'); }
{ // (h) ekstrapolasyon sınıfı
  const K = X.CMP_PROB.exK, e = X.cmpProbExtrap;
  ok(K === 10 && e(1 / 20, 20).exC === 'gozlem' && e(1 / 20.0001, 20).exC === 'uzatma' && e(1 / 200, 20).exC === 'uzatma' && e(1 / 200.01, 20).exC === 'yuksek' && e(0, 20).exC === null, '(h) sınıflar: Tr ≤ T gözlem, T < Tr ≤ 10T uzatma, Tr > 10T yüksek (sınırlar dahil/hariç doğru)');
  // kapalı biçim: M_k = Mc + (log N + log k)/b ⇒ Tr(≥M_k) = k·T
  let kb = true; for (const [n, T, b, Mc] of [[27346, 28.6, 1.05, 3.2], [3000, 28.7, 1.0, 3.2], [150, 10, 0.8, 4.0]]) for (const k of [1, 10]) { const M = X.cmpProbMk(n, b, Mc, k), tr = 1 / X.grLambdaSimple(n, T, b, Mc, M); if (Math.abs(tr / (k * T) - 1) > 1e-12) kb = false; }
  ok(kb, '(h) sınır büyüklükleri: Tr(≥Mc + (log₁₀N + log₁₀k)/b) = k·T (k = 1, 10; üç örnek)');
  // Marmara benzeri: T = 28,7 yıl, Tr(≥7) ≈ 290 yıl → Tr/T ≈ 10,1 → yüksek
  const T = 28.7, b = 1.0, Mc = 3.2, n = Math.round(T / 290 * Math.pow(10, b * (7 - Mc))), c = e(X.grLambdaSimple(n, T, b, Mc, 7), T);
  ok(c.exC === 'yuksek' && Math.abs(c.tr - 290) < 2, `(h) Marmara benzeri (N = ${n}, b = 1, T = 28,7): Tr(≥7) = ${c.tr.toFixed(0)} yıl, Tr/T = ${c.trT.toFixed(2)} → yüksek`);
  const r = Object.assign(kayit(7, 28.7, 0, 1.0, 3.2), { mags: Array.from({ length: n }, (_, i) => +(3.2 + (i % 30) * 0.1).toFixed(1)) }), w = X.cmpProbWarn(Object.assign(r, { gk74: true, mcU: null, turU: null }), { n, T, b, Mmax: 7.4 });
  ok(/‡ M≥7: Tr ≈ 290 yıl, T = 28,7 yıl \(Tr\/T = 10,1\) — yüksek ekstrapolasyon belirsizliği/.test(w) && /† M≥6: Tr ≈ 29 yıl/.test(w) && !/M≥5: Tr/.test(w), '(h) uyarı satırı: M≥7 ‡ (Tr/T = 10,1), M≥6 † (Tr ≈ 29 yıl), M≥5 işaretsiz');
  // şekil: Tr = T çizgisi ve Tr > 10T zemini; lejant
  const r1 = Object.assign(kayit(11, 30, 20, 1.0, 4.0), { name: 'A', src: 'test', gk74: true }); X.CMP = [r1]; const S = [X.cmpStats(r1)], PR = [X.cmpProb(r1, S[0])], svg = X.cmpProbFigSvg(S, PR, { en: true }), cap = X.cmpProbFigCaption(S, PR, true), capTr = X.cmpProbFigCaption(S, PR, false);
  const m1 = X.cmpProbMk(S[0].n, S[0].b, r1.Mc, 1), mK = X.cmpProbMk(S[0].n, S[0].b, r1.Mc, 10);
  ok(m1 > r1.Mc && mK - m1 > 0.9 && /fill-opacity="0\.06"/.test(svg) && /<tspan dy="-1\.5"> = T<\/tspan>/.test(svg) && /= T \(catalogue duration\)/.test(svg) && /&gt; 10T<\/tspan>/.test(svg) && /&gt; 10T: high extrapolation uncertainty/.test(svg), `(h) şekil: Tr = T (M ${m1.toFixed(2)}) çizgisi ve Tr > 10T (M ${mK.toFixed(2)}) gri zemin, lejantta`);
  const cT = PR[0].cell(+(m1 - 0.01).toFixed(3), 10), cU = PR[0].cell(+(m1 + 0.01).toFixed(3), 10), cY = PR[0].cell(+(mK + 0.01).toFixed(3), 10);
  ok(cT.exC === 'gozlem' && cU.exC === 'uzatma' && cY.exC === 'yuksek', '(h) hücre sınıfı şekildeki sınırlarla aynı (M_T − 0,01 gözlem, + 0,01 uzatma; M_10T + 0,01 yüksek)');
  ok(/Solid vertical line: magnitude at which the mean recurrence interval Tr = 1\/λ\(≥M\) equals the catalogue duration T/.test(cap) && /Grey area: Tr > 10T/.test(cap) && /Gri alan: Tr > 10T/.test(capTr), '(h) altyazı Tr = T ve Tr > 10T ölçütünü açıklıyor (EN/TR)'); }
console.log(`
${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
