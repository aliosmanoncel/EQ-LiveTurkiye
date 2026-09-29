// Denetim testi: basamaklı tamlık + Weichert (1980) zinciri, uçtan uca (2026-09-29).
// Olay listesi → csBuild (basamak ataması, Mc altı eleme, dönemler) → sınıflama (n_i, T_i)
// → weichertFit. Fonksiyonlar ve renderGutenbergRichterCS'in sınıflama bloğu doğrudan
// index.html'den okunur; kopya tutulmaz. index.html DEĞİŞTİRİLMEZ.
// Kullanım (depo kökünde): node scripts/test_weichert_chain.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };

const ctx = { document: { getElementById: () => ({ value: '' }) } }; vm.createContext(ctx);
vm.runInContext(src.match(/^const CS_QC = \{[^\n]*\};$/m)[0].replace('const CS_QC', 'var CS_QC'), ctx);
vm.runInContext(cut('function computeMc(evList)', '// Aki (1965) MLE b-değeri'), ctx);
vm.runInContext('var regionRect=null, regionWindowStart=null, regionWindowEnd=null, regionCapped=false, regionOrderUsed=null;', ctx);
vm.runInContext(cut('let csEnabled = false;', 'let lastGrFit = null;').replace('let csEnabled', 'var csEnabled').replace('let csSteps', 'var csSteps'), ctx);
// renderGutenbergRichterCS içindeki sınıflama bloğu (n_i, T_i, sınıf merkezleri) — birebir kaynak
const binBlock = cut('  const idx = m => Math.floor((m + 1e-9) / DM);', '  const wf = weichertFit(clsBest);');
vm.runInContext(`function __classify(items, cs, DM) {\n${binBlock}\n return { bins, clsBest, counts, kMin, kMax }; }`, ctx);
const run = code => vm.runInContext(code, ctx);

let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } console.log((c ? '  ok  ' : '  !!  ') + msg); };
const YR = 365.25 * 864e5, D = s => Date.parse(s + 'T00:00:00Z');

// Kullanıcının ekrandaki basamakları (2026-09-29 ekran görüntüsü)
const USER_STEPS = [{ start: '1999-01-01', mc: 3.5 }, { start: '2005-07-01', mc: 2.2 }, { start: '2014-01-01', mc: 2.1 }, { start: '2023-09-18', mc: 0.0 }];
const T_END = D('2026-09-29');
function setSteps(steps, win) {
  ctx.csSteps = steps.map(s => ({ ...s })); ctx.csEnabled = true;
  if (win) { ctx.regionRect = {}; ctx.regionWindowStart = new Date(win[0]); ctx.regionWindowEnd = new Date(win[1]); }
  else { ctx.regionRect = null; ctx.regionWindowStart = ctx.regionWindowEnd = null; }
}
const ev = (t, m, extra) => ({ time: new Date(t), mag: m, ...(extra || {}) });
function chain(evs, DM = 0.1) {
  ctx.__ev = evs; const cs = run('csBuild(__ev)'); ctx.__cs = cs;
  const c = run(`__classify(__cs.kept, __cs, ${DM})`); ctx.__cls = c.clsBest;
  const wf = run('weichertFit(__cls)'); return { cs, ...c, wf };
}

// ── 1. T_i: basamaklar → sınıf başına gözlem süresi (elle hesaba karşı) ──
console.log('\n1. T_i (kullanıcı basamakları, pencere 1999-01-01 → 2026-09-29)');
{ setSteps(USER_STEPS, [D('1999-01-01'), T_END]);
  const steps = run('csValidSteps()'); ctx.__st = steps; const P = run(`csPeriods(__st, ${D('1999-01-01')}, ${T_END})`); ctx.__P = P;
  const Ty = m => run(`csObsYears(${m}, __P)`);
  const exp = { 0.0: (T_END - D('2023-09-18')) / YR, 2.1: (T_END - D('2014-01-01')) / YR, 2.2: (T_END - D('2005-07-01')) / YR, 3.5: (T_END - D('1999-01-01')) / YR };
  for (const [m, T] of [[0.0, exp[0]], [2.0, exp[0]], [2.1, exp[2.1]], [2.2, exp[2.2]], [3.4, exp[2.2]], [3.5, exp[3.5]], [5.0, exp[3.5]]])
    ok(Math.abs(Ty(m) - T) < 1e-9, `T(${m.toFixed(1)}) = ${Ty(m).toFixed(3)} yıl (beklenen ${T.toFixed(3)})`);
  ok(Math.abs((D('2000-01-01') - D('1999-01-01')) / YR - 365 / 365.25) < 1e-12, 'yıl/gün dönüşümü: 1 yıl = 365.25 gün (Julian)'); }

// ── 2. Sınırlar: [başlangıç, sonraki) yarı-açık; m = Mc dahil; son dönem tEnd dahil ──
console.log('\n2. Zaman ve büyüklük sınırları');
{ setSteps(USER_STEPS, [D('1999-01-01'), T_END]);
  const evs = [
    ev(D('2005-07-01'), 2.2),              // basamak 2'nin tam başı, m = Mc → tutulmalı (Mc 2.2)
    ev(D('2005-07-01') - 1, 2.2),          // 1 ms önce → basamak 1 (Mc 3.5) → atılmalı
    ev(D('2014-01-01'), 2.1),              // basamak 3 başı, m = Mc → tutulmalı
    ev(D('2014-01-01'), 2.0999),           // Mc'nin hemen altı → atılmalı
    ev(T_END, 0.5),                        // tEnd anı, son basamak → tutulmalı
    ev(D('1998-12-31'), 4.0),              // ilk basamaktan önce → atılmalı
    ev(D('2010-01-01'), 5.0), ev(D('2020-01-01'), 3.0), ev(D('2024-01-01'), 1.0), ev(D('2025-01-01'), 1.2)];
  const r = chain(evs);
  const keptKey = new Set(r.cs.kept.map(k => k.t + '|' + k.m));
  ok(keptKey.has(D('2005-07-01') + '|2.2'), 'basamak başındaki olay yeni basamağa atanıyor, m = Mc dahil');
  ok(!keptKey.has((D('2005-07-01') - 1) + '|2.2'), 'basamak başından 1 ms önceki olay eski basamağa (Mc 3.5) atanıp atılıyor');
  ok(keptKey.has(D('2014-01-01') + '|2.1') && !keptKey.has(D('2014-01-01') + '|2.0999'), 'Mc sınırı: 2.1 tutulur, 2.0999 atılır');
  ok(keptKey.has(T_END + '|0.5'), 'tEnd anındaki olay tutulur');
  ok(r.cs.kept.length + r.cs.nExcluded === evs.length, `olay korunumu: tutulan ${r.cs.kept.length} + atılan ${r.cs.nExcluded} = ${evs.length} (çift sayım yok)`);
  const nBins = r.bins.reduce((a, b) => a + b.n, 0);
  ok(nBins === r.cs.kept.length, `Σ n_i (${nBins}) = tutulan olay sayısı (${r.cs.kept.length})`);
  // m = Mc olan olay, T'si o basamağı içeren sınıfa mı düşüyor? (n ve T aynı sınıf tanımını kullanmalı)
  const binOf = m => r.bins.find(b => b.m === +(Math.floor((m + 1e-9) / 0.1) * 0.1).toFixed(2));
  ok(Math.abs(binOf(2.1).T - (T_END - D('2014-01-01')) / YR) < 1e-9, 'm=2.1 sınıfının T\'si basamak 3–4 süresi (n ile T tutarlı)'); }

// ── 3. Pay/payda aynı sınıf kümesi; boş sınıflar olabilirlikte ──
console.log('\n3. Olabilirlik: sınıf kümesi');
{ const wSrc = cut('function weichertFit(bins)', '// Sabit β için');
  ok(/const B = bins\.filter\(b => b\.T > 0\);/.test(wSrc) && !/bins\.forEach/.test(wSrc), 'weichertFit: pay (Σn m) ve payda (ΣT e^{-βm}) aynı B kümesi üzerinden');
  // Davranış testi (kaynak metnine bağlı değil): araya boş sınıf düşen katalogda n = 0 sınıfı olabilirliğe giriyor mu?
  setSteps([{ start: '1999-01-01', mc: 2.0 }], [D('1999-01-01'), T_END]);
  const e0 = []; for (let i = 0; i < 12; i++) { e0.push(ev(D('2010-01-01') + i * 864e5, 2.0)); e0.push(ev(D('2011-01-01') + i * 864e5, 2.4)); }
  const r0 = chain(e0), gaps = r0.clsBest.filter(c => c.n === 0).map(c => (c.m - 0.05).toFixed(1));
  ok(gaps.join(',') === '2.1,2.2,2.3', 'classesTo: kMin…kMax arası BOŞ sınıflar da (n=0) katılıyor (Weichert 1980 gereği): ' + gaps.join(',')); }

// ── Sentetik katalog üreteci ──
const mulberry32 = run('mulberry32');
function synth({ seed, b = 1.0, rate0 = 20000, m0 = 0.0, t0 = D('1999-01-01'), t1 = T_END, trueMc, sigma = 0.15, round = null, conv = null }) {
  // λ(M≥m0) = rate0 /yıl, sürekli üstel büyüklükler; algılama: q(m) = Φ((m − Mc_gerçek(t) + 2σ)/σ)
  // (Mc_gerçek'te ≈ %98 algılama; Ogata & Katsura 1993 tipi yumuşak eşik)
  const rnd = mulberry32(seed), beta = b * Math.LN10, years = (t1 - t0) / YR, n = Math.round(rate0 * years);
  const Phi = z => 0.5 * (1 + erf(z / Math.SQRT2));
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = t0 + rnd() * (t1 - t0); let m = m0 - Math.log(1 - rnd()) / beta;
    const mc = trueMc(t); if (mc !== null && rnd() > Phi((m - mc + 2 * sigma) / sigma)) continue;
    let e;
    if (round) m = Math.round(m / round) * round;
    if (conv) e = { time: new Date(t), mag: +m.toFixed(1), mw: conv(+m.toFixed(1)) }; else e = { time: new Date(t), mag: m };
    out.push(e);
  }
  return out;
}
function erf(x) { const s = Math.sign(x); x = Math.abs(x); const t = 1 / (1 + 0.3275911 * x);
  return s * (1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x)); }
const stepFn = steps => t => { let mc = null; for (const s of steps) if (t >= D(s.start)) mc = s.mc; return mc; };
const stats = a => { const m = a.reduce((x, y) => x + y, 0) / a.length; return { m, sd: Math.sqrt(a.reduce((x, y) => x + (y - m) ** 2, 0) / (a.length - 1)) }; };

// ── 4. Doğruluk: girilen basamaklar = gerçek tamlık → b geri üretiliyor mu? ──
console.log('\n4. Sentetik geri üretim (b = 1.0, 4 basamak, girilen Mc = gerçek Mc; N ≈ 1500, kullanıcı ölçeği)');
const TRUE_STEPS = [{ start: '1999-01-01', mc: 3.5 }, { start: '2005-07-01', mc: 3.1 }, { start: '2014-01-01', mc: 2.5 }, { start: '2023-09-18', mc: 1.9 }];
{ setSteps(TRUE_STEPS, [D('1999-01-01'), T_END]);
  const bs = [], zs = [];
  for (let r = 0; r < 40; r++) { const w = chain(synth({ seed: 100 + r, trueMc: stepFn(TRUE_STEPS), sigma: 0.1 })).wf; bs.push(w.b); zs.push((w.b - 1) / w.sigma); }
  const s = stats(bs), z = stats(zs);
  console.log(`     N ≈ ${chain(synth({ seed: 100, trueMc: stepFn(TRUE_STEPS), sigma: 0.1 })).cs.kept.length}`);
  console.log(`     b̂: ort ${s.m.toFixed(3)}, sd ${s.sd.toFixed(3)} (40 katalog); z=(b̂−1)/σ̂: ort ${z.m.toFixed(2)}, sd ${z.sd.toFixed(2)}`);
  ok(Math.abs(s.m - 1.0) < 0.03, 'yan (bias) < 0.03 → birleştirme + T_i + olabilirlik doğru');
  ok(z.sd > 0.7 && z.sd < 1.4, 'σ̂ kalibre (z sd ≈ 1)'); }

// ── 5. Kullanıcı basamakları (iyimser Mc) ile aynı gerçek katalog ──
console.log('\n5. Sentetik: gerçek Mc = 3.5/3.1/2.5/1.9, girilen Mc = 3.5/2.2/2.1/0.0 (ekrandaki)');
{ const bs = [], shape = [];
  for (let r = 0; r < 20; r++) {
    const evs = synth({ seed: 500 + r, trueMc: stepFn(TRUE_STEPS), sigma: 0.1 });
    setSteps(USER_STEPS, [D('1999-01-01'), T_END]); const u = chain(evs); bs.push(u.wf.b);
    if (r === 0) { // yüksek eşikli alt küme (M ≥ 3.5 sınıfları) için ayrı Weichert
      ctx.__hi = u.clsBest.filter(c => c.m >= 3.5); const hi = run('weichertFit(__hi)');
      const lo = u.bins.filter(b => b.m >= 1.0 && b.m < 3.0 && b.n > 0).map(b => Math.log10(b.rate));
      shape.push({ hi: hi.b, loSlope: (lo[lo.length - 1] - lo[0]) / 2.0 }); }
  }
  const s = stats(bs);
  console.log(`     b̂ (tüm sınıflar): ort ${s.m.toFixed(3)} ± ${s.sd.toFixed(3)}; M≥3.5 alt kümesi b̂ = ${shape[0].hi.toFixed(2)}; M 1–3 sınıf oranlarının eğimi ≈ ${shape[0].loSlope.toFixed(2)} (tam katalogda −1.0)`);
  ok(s.m < 0.8, 'iyimser basamaklar b\'yi belirgin aşağı çeker (kod hatası olmadan) → ekrandaki b≈0.5 davranışı yeniden üretildi');
  ok(Math.abs(shape[0].hi - 1) < 0.15, 'M ≥ 3.5 sınıfları tek başına doğru b verir → eğim kırılması girdi kaynaklı'); }

// ── 6. Mc sınıf ızgarasında değilse / ΔM = 0.2 (gizli risk) ──
console.log('\n6. Sınıf ızgarası dışı Mc (ΔM = 0.2, Mc = 2.1)');
{ const steps = [{ start: '1999-01-01', mc: 3.5 }, { start: '2014-01-01', mc: 2.1 }];
  setSteps(steps, [D('1999-01-01'), T_END]);
  const bs = [], bs1 = [];
  for (let r = 0; r < 20; r++) { const evs = synth({ seed: 900 + r, trueMc: stepFn(steps), sigma: 0.02 }); bs.push(chain(evs, 0.2).wf.b); bs1.push(chain(evs, 0.1).wf.b); }
  const s = stats(bs), s1 = stats(bs1);
  console.log(`     b̂(ΔM=0.1) = ${s1.m.toFixed(3)}; b̂(ΔM=0.2) = ${s.m.toFixed(3)} (gerçek 1.0)`);
  ctx.__ev = synth({ seed: 901, trueMc: stepFn(steps), sigma: 0.02 }); const cs = run('csBuild(__ev)'); ctx.__cs = cs;
  const c = run('__classify(__cs.kept, __cs, 0.2)'), b20 = c.bins.find(b => b.m === 2.0);
  console.log(`     [2.0, 2.2) sınıfı: n = ${b20.n} (2.1–2.2 arası, basamak 2'den), T = ${b20.T.toFixed(2)} yıl (basamak 2 süresi DAHİL EDİLMEMİŞ)`);
  ok(Math.abs(s1.m - 1.0) < 0.03, 'ΔM = 0.1 (kullanıcı ayarı, Mc ızgarada): b yansız');
  ok(b20.n > 0 && b20.T === 0, `GİZLİ HATA (ΔM = 0.2, Mc = 2.1): [2.0, 2.2) sınıfının ${b20.n} olayı T = 0 nedeniyle olabilirlikten sessizce düşüyor; üst basamakta Mc = 2.0 olsaydı n sayılır ama T eksik kalırdı → oran şişer`); }

// ── 7. Büyüklük dönüşümü örgüsü: ML 0.1 adım → Mw = 0.93·ML + 0.29 (0.093 adım) ──
console.log('\n7. ML→Mw örgüsü (Çıvgın & Scordilis 2019 kolu) ve ΔM = 0.1 sınıflama (200 katalog × 3000 olay)');
{ const W = run('weichertFit'), rnd = mulberry32(7);
  const fit = (mags, mc) => { const c = {}; let kmin = 1e9, kmax = 0;
    mags.filter(m => m >= mc - 1e-9).forEach(m => { const k = Math.floor((m + 1e-9) / 0.1); c[k] = (c[k] || 0) + 1; kmin = Math.min(kmin, k); kmax = Math.max(kmax, k); });
    const cl = []; for (let k = kmin; k <= kmax + 20; k++) cl.push({ m: k * 0.1 + 0.05, n: c[k] || 0, T: 1 }); return W(cl).b; };
  const R = { ml: [], mw25: [], mw26: [] };
  for (let r = 0; r < 200; r++) { const ML = []; for (let i = 0; i < 3000; i++) ML.push(+(2.0 - Math.log(1 - rnd()) / Math.LN10).toFixed(1));
    const MW = ML.map(m => 0.93 * m + 0.29); R.ml.push(fit(ML, 2.5)); R.mw25.push(fit(MW, 2.5)); R.mw26.push(fit(MW, 2.6)); }
  const e = 1 / 0.93, a = stats(R.ml).m, b25 = stats(R.mw25).m, b26 = stats(R.mw26).m;
  const occ = {}; for (let k = 20; k <= 50; k++) { const mw = 0.93 * k / 10 + 0.29, kk = Math.floor((mw + 1e-9) / 0.1); (occ[kk] = occ[kk] || []).push((k / 10).toFixed(1)); }
  const dbl = Object.entries(occ).filter(([, v]) => v.length > 1).map(([k, v]) => `${(k / 10).toFixed(1)}←ML ${v.join('+')}`);
  console.log(`     b̂(ML) = ${a.toFixed(3)} (gerçek 1.0); b̂(Mw) Mc 2.5: ${b25.toFixed(3)}, Mc 2.6: ${b26.toFixed(3)} (ölçek dönüşümü beklentisi 1/0.93 = ${e.toFixed(3)})`);
  console.log(`     iki ML değeri alan Mw sınıfları (ML 2.0–5.0): ${dbl.join('; ')}`);
  ok(Math.abs(a - 1) < 0.02, 'ML ızgarasında b yansız');
  ok(b25 - e > 0 && b26 - e < 0.1, `Mw örgüsü: Mc fazına bağlı YUKARI yönlü yanlılık (+${(b25 - e).toFixed(3)} … +${(b26 - e).toFixed(3)}); yön ters, ekrandaki düşük b'yi AÇIKLAMAZ`);
  ok(dbl.length > 0, 'örgü: bazı Mw sınıfları 2 ML değeri alıyor → sınıf sayılarında sıçrama (uyum testini bir miktar şişirir)'); }

// ── 8. Küçük N: sınıf kümesi gözlenen en büyük sınıfta kesiliyor (Mx boşken) ──
console.log('\n8. Küçük örneklem: üst kesilme = gözlenen maksimum (Mx girilmemişken)');
{ const W = run('weichertFit'); const rnd = mulberry32(42);
  const trial = (N, ext) => { const bs = []; for (let r = 0; r < 300; r++) { const c = {}; let kmax = 0;
      for (let i = 0; i < N; i++) { const k = Math.floor((2 - Math.log(1 - rnd()) / Math.LN10) / 0.1 + 1e-9); c[k] = (c[k] || 0) + 1; kmax = Math.max(kmax, k); }
      const cl = []; for (let k = 20; k <= kmax + ext; k++) cl.push({ m: k * 0.1 + 0.05, n: c[k] || 0, T: 1 }); const w = W(cl); if (w) bs.push(w.b); }
    return stats(bs).m; };
  const r30 = trial(30, 0), r30x = trial(30, 30), r1000 = trial(1000, 0);
  console.log(`     N=30: b̂ ${r30.toFixed(3)} (maksta kesik) vs ${r30x.toFixed(3)} (+3 birim boş sınıf); N=1000: ${r1000.toFixed(3)}`);
  ok(r30 < 0.93 && Math.abs(r1000 - 1) < 0.03, 'küçük N\'de (≈ kayan pencere, tek basamak) b aşağı yanlı; N ≳ 300\'de ihmal edilebilir → kullanıcı kataloğunda (N=1355) b≈0.5\'i AÇIKLAMAZ'); }

console.log(`\nPASS ${pass} FAIL ${fail}`); process.exit(fail ? 1 : 0);
