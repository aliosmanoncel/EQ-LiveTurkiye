// Birim testleri: G-R fit aralığı [M_min, M_max) (2026-09-29).
// Fonksiyonlar ve renderGutenbergRichterCS'in sınıflama/fit bloğu doğrudan index.html'den okunur; kopya tutulmaz.
// "Eski yol" karşılaştırması için HEAD (git) sürümündeki aynı blok da okunur: fit kapalıyken sonuç birebir aynı olmalı.
// Kullanım (depo kökünde): node scripts/test_fit_range.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), cp = require('child_process');
const load = f => fs.readFileSync(f, 'utf8').replace(/\r\n/g, '\n');
const src = load(process.argv[2] || path.join(__dirname, '..', 'index.html'));
let srcOld = null; try { srcOld = cp.execSync('git show HEAD:index.html', { cwd: path.join(__dirname, '..'), maxBuffer: 1 << 26 }).toString().replace(/\r\n/g, '\n'); } catch (e) {}
const cutS = (S, a, b) => { const i = S.indexOf(a), j = S.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return S.slice(i, j); };

function mkCtx(S) {
  const inputs = {}; const ctx = { __inputs: inputs, document: { getElementById: id => ({ value: inputs[id] ?? '' }) } }; vm.createContext(ctx);
  vm.runInContext(S.match(/^const CS_QC = \{[^\n]*\};$/m)[0].replace('const CS_QC', 'var CS_QC'), ctx);
  vm.runInContext(cutS(S, 'function computeMc(evList)', '// Aki (1965) MLE b-değeri'), ctx);
  vm.runInContext(cutS(S, 'function bConfidence95(b, n)', '// Kayan pencere b-değeri'), ctx);
  vm.runInContext('var regionRect=null, regionWindowStart=null, regionWindowEnd=null, regionCapped=false, regionOrderUsed=null;', ctx);
  vm.runInContext(cutS(S, 'let csEnabled = false;', 'let lastGrFit = null;').replace('let csEnabled', 'var csEnabled').replace('let csSteps', 'var csSteps'), ctx);
  if (S.includes('function csBvalueTimeSeries(cs, fit)')) vm.runInContext(cutS(S, 'function csBvalueTimeSeries(cs, fit)', '// ── Fit aralığı arayüzü'), ctx);
  else vm.runInContext(cutS(S, 'function csBvalueTimeSeries(cs)', '// GR — basamaklı tamlık'), ctx);   // HEAD (eski imza)
  // Sınıflama + Weichert (renderGutenbergRichterCS, birebir kaynak): "Kesik birikimli eğri" yorumuna kadar
  const blk = cutS(S, '  const idx = m => Math.floor((m + 1e-9) / DM);', '  // Kesik birikimli eğri');
  vm.runInContext(`function __fit(items, cs, DM) {\n${blk}\n return { wf, m0, rate0: typeof rate0Best !== 'undefined' ? rate0Best : (wf ? wf.rate0 : null), clsBest,
    fitOn: typeof fitOn !== 'undefined' ? fitOn : false, fitNote: typeof fitNote !== 'undefined' ? fitNote : '', wfAll: typeof wfAll !== 'undefined' ? wfAll : null,
    mTopFit: typeof mTopFit !== 'undefined' ? mTopFit : null }; }`, ctx);
  return ctx;
}
const X = mkCtx(src), O = srcOld ? mkCtx(srcOld) : null;
const run = (C, code) => vm.runInContext(code, C);

let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else fail++; console.log((c ? '  ok  ' : '  !!  ') + msg); };
const YR = 365.25 * 864e5, D = s => Date.parse(s + 'T00:00:00Z'), T_END = D('2026-09-29');
const stats = a => { const m = a.reduce((x, y) => x + y, 0) / a.length; return { m, sd: Math.sqrt(a.reduce((x, y) => x + (y - m) ** 2, 0) / Math.max(1, a.length - 1)) }; };
const mulberry32 = run(X, 'mulberry32');
function erf(x) { const s = Math.sign(x); x = Math.abs(x); const t = 1 / (1 + 0.3275911 * x);
  return s * (1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x)); }
const stepFn = steps => t => { let mc = null; for (const s of steps) if (t >= D(s.start)) mc = s.mc; return mc; };
// Sentetik olaylar: sürekli üstel (b), yumuşak algılama eşiği; isteğe bağlı 0,1 yuvarlama
function synth({ seed, b = 1.0, rate0 = 20000, trueMc, sigma = 0.1, round = false, t0 = D('1999-01-01'), t1 = T_END }) {
  const rnd = mulberry32(seed), beta = b * Math.LN10, n = Math.round(rate0 * (t1 - t0) / YR), out = [];
  for (let i = 0; i < n; i++) {
    const t = t0 + rnd() * (t1 - t0); let m = -Math.log(1 - rnd()) / beta;
    const mc = trueMc(t); if (mc !== null && rnd() > 0.5 * (1 + erf((m - mc + 2 * sigma) / sigma / Math.SQRT2))) continue;
    if (round) m = Math.round(m * 10) / 10;
    out.push({ time: new Date(t), mag: m });
  }
  return out;
}
function fitWith(C, steps, evs, DM = 0.1, fmin = '', fmax = '') {
  C.csSteps = steps.map(s => ({ ...s })); C.csEnabled = true; C.regionRect = {}; C.regionWindowStart = new Date(D('1999-01-01')); C.regionWindowEnd = new Date(T_END);
  C.__inputs.grFitMin = fmin; C.__inputs.grFitMax = fmax;
  C.__ev = evs; C.__cs = run(C, 'csBuild(__ev)');
  return run(C, `__fit(__cs.kept, __cs, ${DM})`);
}
const TRUE_STEPS = [{ start: '1999-01-01', mc: 3.5 }, { start: '2005-07-01', mc: 3.1 }, { start: '2014-01-01', mc: 2.5 }, { start: '2023-09-18', mc: 1.9 }];
const USER_STEPS = [{ start: '1999-01-01', mc: 3.5 }, { start: '2005-07-01', mc: 2.2 }, { start: '2014-01-01', mc: 2.1 }, { start: '2023-09-18', mc: 0.0 }];

// ── 1. Izgara ve aralık denetimi ──
console.log('\n1. grFitRangeCheck');
{ const F = run(X, 'grFitRangeCheck');
  ok(!F(null, null, 0.1).on && !F(null, null, 0.1).err, 'boş → kapalı, uyarı yok (eski hesap)');
  ok(F(3.0, 5.5, 0.1).on && F(3.0, null, 0.1).on && F(null, 5.0, 0.1).on, 'ızgaradaki değerler → açık (tek taraflı da)');
  const e1 = F(2.95, null, 0.1); ok(!e1.on && /ızgarasında değil/.test(e1.err) && /UYGULANMADI/.test(e1.err), 'M_min = 2.95, ΔM = 0.1 → uygulanmaz, açık uyarı: ' + e1.err);
  const e2 = F(2.1, null, 0.2); ok(!e2.on && /2\.1/.test(e2.err), 'M_min = 2.1, ΔM = 0.2 → ızgara dışı (denetim testi 6 riski)');
  ok(!F(3.0, 3.1, 0.1).on && /2·ΔM/.test(F(3.0, 3.1, 0.1).err), 'M_max − M_min < 2·ΔM → uygulanmaz');
  ok(F(0.3, 0.7, 0.1).on, 'kayan nokta: 0.3/0.1 ızgarada sayılır'); }

// ── 2. Normalizasyon: λ(≥M_min) ≠ λ[M_min, M_max) ──
console.log('\n2. Normalizasyon (beklenen sayımlar, gürültüsüz)');
{ const W = run(X, 'weichertFit'), G = run(X, 'grRateAboveMin');
  const beta = Math.LN10, lam3 = 50, DM = 0.1;   // gerçek: λ(≥3.0) = 50/yıl, b = 1
  const cls = (lo, hi, T, mx) => { const a = []; for (let k = Math.round(lo / DM); k < Math.round(hi / DM); k++) { const m = k * DM;
      const F = M => mx === undefined ? Math.exp(-beta * (M - 3)) : (M >= mx ? 0 : (Math.exp(-beta * (M - 3)) - Math.exp(-beta * (mx - 3))) / (1 - Math.exp(-beta * (mx - 3))));
      a.push({ m: m + DM / 2, lo: m, n: T * lam3 * (F(m) - F(m + DM)), T }); } return a; };
  const c1 = cls(3.0, 4.0, 20), w1 = W(c1), g1 = G(w1.rate0, w1.beta, 3.0, 4.0, null);
  console.log(`     fit [3.0, 4.0): b̂ = ${w1.b.toFixed(4)}; λ_aralık = ${w1.rate0.toFixed(3)}; λ(≥3.0) = ${g1.toFixed(3)} (gerçek 50; aralık oranı gerçeğin ${(w1.rate0 / 50).toFixed(3)} katı)`);
  ok(Math.abs(w1.b - 1) < 1e-3, 'kesik pencerede b tam geri üretiliyor');
  ok(Math.abs(g1 - 50) / 50 < 0.005, 'λ(≥M_min) = λ_aralık / (1 − e^{−β(M_max−M_min)}) gerçek oranı veriyor');
  ok(Math.abs(w1.rate0 / 50 - 0.9) < 0.005, 'λ_aralık ayrı raporlanıyor (b = 1, 1 birim pencere → %90)');
  const c2 = cls(3.0, 4.0, 20, 5.0), w2 = W(c2), g2 = G(w2.rate0, w2.beta, 3.0, 4.0, 5.0);
  ok(Math.abs(g2 - 50) / 50 < 0.005, `Mx = 5.0 kesik modelde λ(≥3.0) = ${g2.toFixed(3)} (gerçek 50)`);
  const c3 = cls(3.0, 5.0, 20, 5.0), w3 = W(c3); ok(Math.abs(G(w3.rate0, w3.beta, 3.0, 5.0, 5.0) - w3.rate0) < 1e-9, 'mTop = Mx → λ(≥m0) = λ_aralık (eski Mx davranışı korunur)');
  // Gürültülü topluluk: yansızlık
  const rnd = mulberry32(99), P = run(X, 'poissonSample'), bs = [], gs = [];
  for (let r = 0; r < 300; r++) { const s = c1.map(c => ({ ...c, n: P(c.n, rnd) })), w = W(s); if (!w) continue; bs.push(w.b); gs.push(G(w.rate0, w.beta, 3.0, 4.0, null)); }
  const sb = stats(bs), sg = stats(gs);
  console.log(`     Poisson topluluğu (300): b̂ = ${sb.m.toFixed(3)} ± ${sb.sd.toFixed(3)}; λ̂(≥3.0) = ${sg.m.toFixed(2)} ± ${sg.sd.toFixed(2)}`);
  ok(Math.abs(sb.m - 1) < 0.02 && Math.abs(sg.m - 50) / 50 < 0.02, 'gürültüde b ve λ(≥M_min) yansız'); }

// ── 3. Eski yol: fit kapalıyken HEAD ile birebir aynı ──
console.log('\n3. Fit kapalı → eski sonuçla birebir eşitlik (HEAD index.html)');
if (!O) ok(false, 'HEAD okunamadı (git yok?)');
else for (const [nm, steps, DM, extra] of [['kullanıcı basamakları, ΔM 0.1', USER_STEPS, 0.1, {}], ['doğru basamaklar, ΔM 0.2', TRUE_STEPS, 0.2, {}], ['Mx = 6.0', USER_STEPS, 0.1, { grMx: '6.0' }]]) {
  const evs = synth({ seed: 2024, trueMc: stepFn(TRUE_STEPS), round: true });
  Object.assign(X.__inputs, extra); Object.assign(O.__inputs, extra);
  const a = fitWith(X, steps, evs, DM), b = fitWith(O, steps, evs, DM);
  X.__inputs.grMx = ''; O.__inputs.grMx = '';
  ok(!a.fitOn && a.wf.b === b.wf.b && a.wf.sigma === b.wf.sigma && a.rate0 === b.rate0 && a.m0 === b.m0 && a.wf.N === b.wf.N,
    `${nm}: b ${a.wf.b.toFixed(6)} = ${b.wf.b.toFixed(6)}, λ ${a.rate0.toFixed(4)} = ${b.rate0.toFixed(4)}, N ${a.wf.N}`);
}

// ── 4. Fit penceresi, eksik düşük sınıfları dışlayınca b'yi geri üretiyor ──
console.log('\n4. Gerçek Mc 3.5/3.1/2.5/1.9, girilen 3.5/2.2/2.1/0.0 (ekrandaki), fit [M_min, —)');
{ const R = { all: [], f25: [], f32: [], f35: [] }, L = [];
  for (let r = 0; r < 20; r++) {
    const evs = synth({ seed: 700 + r, trueMc: stepFn(TRUE_STEPS) });
    const a = fitWith(X, USER_STEPS, evs); R.all.push(a.wf.b);
    const f25 = fitWith(X, USER_STEPS, evs, 0.1, '2.5'); R.f25.push(f25.wf.b);
    const f32 = fitWith(X, USER_STEPS, evs, 0.1, '3.2'); R.f32.push(f32.wf.b);
    const f35 = fitWith(X, USER_STEPS, evs, 0.1, '3.5'); R.f35.push(f35.wf.b);
    L.push(f32.rate0 * Math.exp(-f32.wf.beta * (4.0 - f32.m0)));
  }
  const s = k => stats(R[k]);
  console.log(`     tüm sınıflar b̂ = ${s('all').m.toFixed(3)}; M_min 2.5: ${s('f25').m.toFixed(3)}; 3.2: ${s('f32').m.toFixed(3)} ± ${s('f32').sd.toFixed(3)}; 3.5: ${s('f35').m.toFixed(3)} ± ${s('f35').sd.toFixed(3)} (gerçek 1.0)`);
  const lam4 = 20000 * Math.pow(10, -4.0); console.log(`     λ̂(≥4.0), M_min 3.2 fitinden: ${stats(L).m.toFixed(3)} (gerçek ${lam4.toFixed(3)})`);
  ok(s('all').m < 0.8, 'tüm sınıflar: aşağı yanlı (eski sonuç, karşılaştırma satırı)');
  ok(Math.abs(s('f32').m - 1) < 0.05 && Math.abs(s('f35').m - 1) < 0.06, 'gerçek tamlığın üstündeki fit penceresi b\'yi yansız geri üretiyor');
  ok(s('f25').m < s('f32').m, 'eksik bölgeye inen M_min (2.5) hâlâ yanlı → tarama bunu göstermeli');
  ok(Math.abs(stats(L).m / lam4 - 1) < 0.06, 'fit penceresinden λ(≥4.0) yansız (normalizasyon + T_i)'); }

// ── 5. M_max: üst kesilme ve boş sınıflar ──
console.log('\n5. M_max');
{ const evs = synth({ seed: 31, trueMc: stepFn(TRUE_STEPS) });
  const f = fitWith(X, TRUE_STEPS, evs, 0.1, '3.5', '4.5'), top = Math.max(...f.clsBest.map(c => c.lo));
  ok(Math.abs(top - 4.4) < 1e-9 && Math.min(...f.clsBest.map(c => c.lo)) === 3.5, `sınıflar [3.5, 4.5): alt 3.5, üst sınıf alt sınırı ${top.toFixed(1)}; mTopFit = ${f.mTopFit}`);
  ok(f.clsBest.every(c => c.lo >= 3.5 - 1e-9 && c.lo < 4.5 - 1e-9), 'aralık dışı sınıf olabilirliğe girmiyor');
  const g = fitWith(X, TRUE_STEPS, evs, 0.1, '3.5', '9.0'); const empt = g.clsBest.filter(c => c.n === 0 && c.lo > 6).length;
  ok(empt > 0 && g.mTopFit === 9, `M_max gözlenen en büyük sınıfın üstündeyse aradaki BOŞ sınıflar (${empt}) koşullu olabilirliğe giriyor`);
  const h = fitWith(X, TRUE_STEPS, evs, 0.1, '2.95'); ok(!h.fitOn && /UYGULANMADI/.test(h.fitNote), 'ızgara dışı M_min → fit kapalı + uyarı (sessiz yuvarlama yok)'); }

// ── 6. b(t): çift kesik Aki–Utsu ──
console.log('\n6. b(t) tahmincisi csAkiBRange + csFitItems');
{ const A = run(X, 'csAkiB'), AR = run(X, 'csAkiBRange'), FI = run(X, 'csFitItems'), rnd = mulberry32(5);
  const it = Array.from({ length: 300 }, () => { const mc = [2.0, 2.5, 3.0][Math.floor(rnd() * 3)]; return { m: +(mc + Math.round(-Math.log(1 - rnd()) / Math.LN10 * 10) / 10).toFixed(1), mc }; });
  ok(Math.abs(AR(it, null).b - A(it)) < 1e-12, 'M_max boşken csAkiBRange ≡ csAkiB (eski b(t) ile aynı)');
  const trunc = (n, lo, hi, b, r) => Array.from({ length: n }, () => { let m; do { m = Math.round((lo - 0.05 - Math.log(1 - r()) / (b * Math.LN10)) * 10) / 10; } while (m >= hi - 1e-9 || m < lo - 1e-9); return { m, mc: lo }; });
  const bs = [], zs = [], bsA = [];
  for (let k = 0; k < 400; k++) { const w = trunc(100, [2.0, 2.5][k % 2], 3.5, 1.0, rnd), r = AR(w, 3.5); if (!r) continue; bs.push(r.b); zs.push((r.b - 1) / r.se); bsA.push(A(w)); }
  const sb = stats(bs), sz = stats(zs), sa = stats(bsA);
  console.log(`     N = 100 pencere, [Mc, 3.5), b = 1: kesik b̂ = ${sb.m.toFixed(3)} (z sd ${sz.sd.toFixed(2)}); kesilmesiz Aki aynı veride ${sa.m.toFixed(3)}`);
  ok(Math.abs(sb.m - 1) < 0.04 && sz.sd > 0.8 && sz.sd < 1.25, 'kesik tahminci yansız, SE (Fisher) kalibre');
  ok(sa.m > 1.1, 'M_max\'ı yok sayan Aki yukarı yanlı → çift kesik tahminci gerekli');
  const fi = FI([{ m: 2.0, mc: 1.5 }, { m: 3.0, mc: 1.5 }, { m: 3.0, mc: 3.5 }, { m: 3.6, mc: 3.5 }, { m: 5.0, mc: 2.0 }, { m: 4.9, mc: 2.0 }], { on: true, lo: 3.0, hi: 5.0 });
  ok(JSON.stringify(fi.map(x => [x.m, x.mc])) === JSON.stringify([[3.0, 3.0], [3.6, 3.5], [4.9, 3.0]]), 'olay başına eşik max(Mc_i, M_min); M < M_max; m = M_max dışarıda');
  // b(t) serisi uçtan uca: fit kapalıyken eski seri ile birebir
  const evs = synth({ seed: 77, trueMc: stepFn(TRUE_STEPS), round: true }); fitWith(X, USER_STEPS, evs);
  const sOff = run(X, 'csBvalueTimeSeries(__cs, null)'), sOld = O ? (fitWith(O, USER_STEPS, evs), run(O, 'csBvalueTimeSeries(__cs)')) : null;
  ok(sOld && sOff.series.length === sOld.series.length && sOff.series.every((p, i) => p.b === sOld.series[i].b && p.err === sOld.series[i].err), `b(t), fit kapalı: ${sOff.series.length} pencere HEAD ile birebir`);
  const sOn = run(X, 'csBvalueTimeSeries(__cs, {on:true, lo:3.2, hi:null})');
  const mOff = stats(sOff.series.map(p => p.b)).m, mOn = stats(sOn.series.map(p => p.b)).m;
  console.log(`     b(t) ortalaması: tüm sınıflar ${mOff.toFixed(3)}, fit M ≥ 3.2 ${mOn.toFixed(3)} (gerçek 1.0; ${sOn.series.length} pencere)`);
  ok(Math.abs(mOn - 1) < 0.06 && mOff < 0.85, 'b(t) aynı fit kararını kullanınca yanlılık kalkıyor'); }

// ── 7. Kararlılık taraması ve öneri ──
console.log('\n7. grStabilityScan + grSuggestMmin (gerçek: 3.2 altı eksik, girilen basamaklar iyimser)');
{ const evs = synth({ seed: 4242, trueMc: stepFn(TRUE_STEPS) }); const f = fitWith(X, USER_STEPS, evs);
  X.__cls = run(X, `(() => { const a = []; for (let k = Math.round(${Math.min(...f.clsBest.map(c => c.lo))} / 0.1); k <= 60; k++) { const m = +(k * 0.1).toFixed(2), T = csObsYears(m, __cs.periods); const n = __cs.kept.filter(x => Math.floor((x.m + 1e-9) / 0.1) === k).length; if (T > 0) a.push({ m: m + 0.05, lo: m, n, T }); } return a; })()`);
  const mins = []; for (let k = 15; k <= 40; k++) mins.push(+(k / 10).toFixed(1));
  const rows = run(X, 'grStabilityScan')(X.__cls, mins, null), sug = run(X, 'grSuggestMmin')(rows);
  console.log('     M_min:  ' + rows.filter((r, i) => i % 3 === 0).map(r => `${r.mMin.toFixed(1)}→${r.b !== undefined ? r.b.toFixed(2) : '—'}${r.dPerDf != null ? `(D/sd ${r.dPerDf.toFixed(1)})` : ''}`).join('  '));
  console.log(`     öneri: ${sug ? `M_min = ${sug.mMin} (b = ${sug.b.toFixed(3)}, b_ave = ${sug.bAve.toFixed(3)}, σ = ${sug.sigma.toFixed(3)}, N = ${sug.N})` : 'yok'}`);
  ok(rows.length === 26 && rows.every(r => r.b === undefined || (r.sigma > 0 && r.N > 0 && r.K >= 2)), 'tarama 1.5 → 4.0, 26 satır: b, σ, N, K, D/sd');
  ok(sug && sug.mMin >= 2.9 && sug.mMin <= 3.6, 'öneri gerçek tamlık bölgesinde (2.9–3.6)');
  const lowD = rows.find(r => Math.abs(r.mMin - 2.0) < 1e-9), hiD = rows.find(r => Math.abs(r.mMin - 3.5) < 1e-9);
  ok(lowD.dPerDf > 3 * hiD.dPerDf, `D/sd eksik bölgede yüksek (M_min 2.0: ${lowD.dPerDf.toFixed(1)}), tam bölgede düşük (3.5: ${hiD.dPerDf.toFixed(2)})`);
  const flat = mins.map(m => ({ mMin: m, b: 1 + (m < 3 ? 0.5 : 0), sigma: 0.01, N: 10 })); ok(run(X, 'grSuggestMmin')(flat) === null, 'N < 50 → öneri yok (öneri zorlanmaz)'); }

// ── 8. R profili üst sınırı ve URL ──
console.log('\n8. grRProfile(mEnd) ve URL parametreleri');
{ const P = run(X, 'grRProfile'), bins = []; for (let k = 20; k < 60; k++) bins.push({ m: k / 10, T: 10, cumN: 1000 * Math.pow(10, -(k / 10 - 2)), cumRate: 100 * Math.pow(10, -(k / 10 - 2)) });
  const a = P(bins, 3.0, M => 100 * Math.pow(10, -(M - 2))), b = P(bins, 3.0, M => 100 * Math.pow(10, -(M - 2)), 4.0);
  ok(a.mTo > 4.0 && b.mTo < 4.0 - 1e-9 && b.ok, `profil M_max'ta duruyor (${a.mTo.toFixed(1)} → ${b.mTo.toFixed(1)})`);
  ok(/\['fmin', 'grFitMin', ''\], \['fmax', 'grFitMax', ''\]/.test(src), 'URL: fmin / fmax parametreleri GR_URL_PARAMS içinde (paylaşılabilir, yeniden üretilebilir)');
  ok(/id="grFitMin"/.test(src) && /id="grFitMax"/.test(src) && /grFitSuggestApply\(\)/.test(src), 'UI: M_min, M_max alanları ve ⚙ Oto öner');
  ok(/csBvalueTimeSeries\(cs, btFit\)/.test(src) && /grFitRangeCurrent\(\)/.test(src), 'b(t) ve G-R aynı karar kaynağını okuyor (grFitRangeCurrent)'); }

console.log(`\nPASS ${pass} FAIL ${fail}`); process.exit(fail ? 1 : 0);
