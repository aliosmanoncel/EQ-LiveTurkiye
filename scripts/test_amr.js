// Birim testleri: AMR geriye dönük testi (2026-10-17).
// Fonksiyonlar doğrudan index.html'den okunur (AMR_* sabitleri, amrFitQ, amrGrid, amrSynthPoisson, amrSynthCluster,
// amrPvalue, mulberry32); kopya tutulmaz. Bütün kataloglar YAPAY veridir, fiziksel yorum için kullanılmaz.
// Denetlenen iddialar:
//   1. q ölçütü: tam güç yasası (0 < m < 1, hızlanan) q ≪ 1 ve m'yi geri bulur; doğrusal birikim q ≈ 1; yavaşlayan
//      birikim hızlanma sayılmaz (k < 0 koşulu).
//   2. Izgara: t_f ve sonrası olaylar dışarıda; n < 20 hücre geçersiz; katalog başlangıcından önceki hücre geçersiz.
//   3. Sentetik üreticiler: olay sayısı, büyüklük ve uzaklık korunur; zamanlar pencerede; küme içi zaman farkları
//      (döngüsel sarma modülünde) korunur.
//   4. p = (1 + #{T_sim ≤ T_obs}) / (N + 1).
//   5. Kalibrasyon: gerçekten Poisson olan kataloglarda Poisson sıfırı altında p yaklaşık düzgün (yanlış pozitif oranı
//      nominal düzeyi belirgin aşmaz); hızlanan sentetik katalogda p küçük.
// Kullanım (depo kökünde): node scripts/test_amr.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => {
  const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j);
};
const consts = ['AMR_M_GRID', 'AMR_PROTOS', 'AMR_Y_GRID', 'AMR_NMIN'].map(c => { const m = src.match(new RegExp('^const ' + c + ' = [^\\n]*$', 'm')); if (!m) throw new Error(c); return m[0].replace(/^const /, 'var '); });
// 2026-10-18: R ızgarası protokole bağlı (AMR-P1 ≤ 300 km, AMR-P2 ≤ 500 km); AMR_PROTO ortam değişkeniyle seçilir
consts.push(`var AMR_R_GRID = AMR_PROTOS['${process.env.AMR_PROTO || 'AMR-P2'}'];`);
const ctx = {}; vm.createContext(ctx);
vm.runInContext([...new Set(consts)].join('\n') + '\n' + ['amrFitQ', 'amrGrid', 'amrSynthPoisson', 'amrSynthCluster', 'amrDropCheck', 'amrPvalue', 'mulberry32'].map(fn).join('\n') +
  '\nglobalThis.__x = { amrFitQ, amrGrid, amrSynthPoisson, amrSynthCluster, amrDropCheck, amrPvalue, mulberry32, AMR_R_GRID, AMR_Y_GRID, AMR_NMIN, AMR_YR };', ctx);
const X = ctx.__x, YR = X.AMR_YR;
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };

// ── 1. q ölçütü ─────────────────────────────────────────────────────
{ const tf = 2020, ts = Float64Array.from({ length: 60 }, (_, i) => 2000 + i * 19.5 / 59);
  const pw = Float64Array.from(ts, t => 10 - 3 * Math.pow(tf - t, 0.3));
  const r = X.amrFitQ(ts, pw, tf); ok(r && r.q < 0.05 && r.m === 0.3, `tam güç yasası: q=${r && r.q} m=${r && r.m}`);
  const ln = Float64Array.from(ts, t => 2 + 0.5 * (t - 2000) + 0.05 * Math.sin(37 * t));
  const l = X.amrFitQ(ts, ln, tf); ok(l && l.q > 0.9, `doğrusal: q=${l && l.q}`);
  const dec = Float64Array.from(ts, t => 10 * (1 - Math.exp(-(t - 2000) / 3)));   // yavaşlayan birikim
  const d = X.amrFitQ(ts, dec, tf); ok(d && d.q > 0.9, `yavaşlayan birikim hızlanma sayılmamalı: q=${d && d.q}`);
  // İşaret koşulu: S = K + k(t_f − t)^m, 0 < m < 1. k < 0 → dS/dt = −k·m·(t_f − t)^(m−1) > 0 ve t → t_f iken artar (hızlanma);
  // k > 0 azalan S verir ve reddedilmelidir. Seçilen her uyumda k < 0 olmalı ve uyumun eğimi pozitif, artan olmalı.
  const neg = Float64Array.from(ts, t => 10 + 3 * Math.pow(tf - t, 0.3));   // k = +3: azalan S
  const nr = X.amrFitQ(ts, neg, tf); ok(nr && nr.q >= 0.99, `k > 0 (azalan S) reddedilmeli: q=${nr && nr.q} m=${nr && nr.m}`);
  ok(r.k < 0, `seçilen uyumda k < 0: ${r.k}`);
  const rate = t => -r.k * r.m * Math.pow(tf - t, r.m - 1);
  ok(rate(2000) > 0 && rate(2019) > rate(2010) && rate(2010) > rate(2000), 'uyumun eğimi pozitif ve t_f\'ye yaklaştıkça artar');
  ok(Math.abs((r.K + r.k * Math.pow(0, r.m)) - 10) < 0.05, `t = t_f'de S = K sonlu: K=${r.K}`); }

// ── 2. Izgara kuralları ─────────────────────────────────────────────
{ const tf = Date.UTC(2020, 0, 1), rnd = X.mulberry32(5);
  const ev = Array.from({ length: 400 }, () => ({ t: tf - rnd() * 20 * YR, m: 3 + rnd(), d: rnd() * 300 }));
  ev.push({ t: tf, m: 7, d: 0 }, { t: tf + 1e9, m: 5, d: 1 });   // ana şok anı ve sonrası dışarıda kalmalı
  const G = X.amrGrid(ev, tf, 3, X.AMR_R_GRID, X.AMR_Y_GRID, -Infinity);
  const c = G.cells.find(z => z.r === 300 && z.yr === 20); ok(c.n === 400, `t ≥ t_f olaylar dışarıda: n=${c.n}`);
  ok(G.cells.filter(z => z.ok).every(z => z.n >= X.AMR_NMIN), 'geçerli hücrelerde n ≥ NMIN');
  ok(G.cells.filter(z => !z.ok && z.n > 0).every(z => z.n < X.AMR_NMIN), 'n < NMIN hücreler geçersiz');
  const G2 = X.amrGrid(ev, tf, 3, X.AMR_R_GRID, X.AMR_Y_GRID, tf - 7 * YR);
  ok(G2.cells.filter(z => z.yr > 7).every(z => !z.ok), 'katalog başlangıcından önceki hücreler geçersiz');
  ok(G.T === Math.min(...G.cells.filter(z => z.ok).map(z => z.q)), 'T = en küçük q'); }

// ── 3. Sentetik üreticiler ──────────────────────────────────────────
{ const wa = 0, wb = 10 * YR, rnd = X.mulberry32(9), ev = [], cl = [];
  for (let c = 0; c < 30; c++) { const t0 = rnd() * wb, root = ev.length; for (let j = 0; j < 5; j++) { ev.push({ t: Math.min(wb - 1, t0 + j * 864e5), m: 3 + j * 0.1, d: c }); cl.push(root); } }
  const P = X.amrSynthPoisson(ev, wa, wb, rnd), K = X.amrSynthCluster(ev, cl, wa, wb, rnd);
  for (const [S, lab] of [[P, 'Poisson'], [K, 'küme']]) {
    ok(S.length === ev.length && S.every((s, i) => s.m === ev[i].m && s.d === ev[i].d), `${lab}: sayı/büyüklük/uzaklık korunur`);
    ok(S.every(s => s.t >= wa && s.t < wb), `${lab}: zamanlar pencerede`); }
  const L = wb - wa, mod = v => ((v % L) + L) % L;
  ok(ev.every((e, i) => Math.abs(mod((K[i].t - K[cl[i]].t) - (e.t - ev[cl[i]].t))) < 1e-3 || Math.abs(mod((K[i].t - K[cl[i]].t) - (e.t - ev[cl[i]].t)) - L) < 1e-3), 'küme içi zaman farkları korunur (döngüsel)'); }

// ── 4. p değeri ─────────────────────────────────────────────────────
{ const r = X.amrPvalue(0.5, [0.4, 0.6, 0.5, null, 0.9]); ok(r.n === 4 && Math.abs(r.p - 3 / 5) < 1e-12, `p formülü ${r.p}`);
  ok(X.amrPvalue(0.1, [0.5, 0.6, 0.7]).p === 0.25, 'gözlem hepsinden küçükse p = 1/(N+1)'); }

// ── 5. Kalibrasyon ve güç ───────────────────────────────────────────
{ const tf = Date.UTC(2020, 0, 1), wa = tf - 20 * YR, R = X.AMR_R_GRID, Yg = X.AMR_Y_GRID;
  const mk = (rnd, n, tfun) => Array.from({ length: n }, () => ({ t: tfun(rnd), m: Math.round((3 - Math.log10(1 - rnd())) * 10) / 10, d: rnd() * 300 }));
  const pOf = (ev, rnd, nSim) => { const o = X.amrGrid(ev, tf, 3, R, Yg, -Infinity), T = [];
    for (let k = 0; k < nSim; k++) T.push(X.amrGrid(X.amrSynthPoisson(ev, wa, tf, rnd), tf, 3, R, Yg, -Infinity).T); return X.amrPvalue(o.T, T).p; };
  const rnd = X.mulberry32(20261017), ps = [];
  for (let c = 0; c < 40; c++) ps.push(pOf(mk(rnd, 300, r => wa + r() * (tf - wa)), rnd, 39));
  const fp10 = ps.filter(p => p <= 0.1).length / ps.length;
  ok(fp10 <= 0.25, `Poisson kataloglarında p ≤ 0,10 oranı ${fp10} (nominal 0,10)`);
  console.log(`Kalibrasyon: 40 Poisson kataloğu, p ≤ 0,10 oranı = ${fp10.toFixed(3)}, p ortalaması = ${(ps.reduce((a, b) => a + b, 0) / ps.length).toFixed(3)}`);
  // Hızlanan katalog: olay yoğunluğu ∝ (t_f − t)^(−0,7) → ters dönüşümle örnekleme
  const acc = mk(rnd, 300, r => tf - 20 * YR * Math.pow(r(), 1 / 0.3));
  const pa = pOf(acc, rnd, 99); ok(pa <= 0.05, `hızlanan katalogda p küçük: ${pa}`);
  console.log(`Güç: hızlanan sentetik katalog, p = ${pa.toFixed(3)}`); }

// ── 6. Tek olay / küme duyarlılığı (amrDropCheck; Guilhem vd. 2013) ──
{ const tf = Date.UTC(2020, 0, 1), rnd = X.mulberry32(31), ev = [], cl = [];
  for (let i = 0; i < 150; i++) { ev.push({ t: tf - 10 * YR + rnd() * 10 * YR, m: 3 + Math.round(rnd() * 8) / 10, d: rnd() * 90 }); cl.push(i); }
  const big = ev.length; ev.push({ t: tf - 0.4 * YR, m: 6.5, d: 10 }); cl.push(big);   // geç gelen büyük olay
  for (let j = 0; j < 60; j++) { ev.push({ t: tf - 0.4 * YR + rnd() * 0.3 * YR, m: 3 + Math.round(rnd() * 15) / 10, d: 12 }); cl.push(big); }   // artçıları
  const cell = { r: 100, yr: 10 }, D = X.amrDropCheck(ev, cl, cell, tf, 3);
  ok(D && D.big.m === 6.5 && D.nCluster === 61, `en büyük olay ve kümesi bulunur: M${D && D.big.m}, küme ${D && D.nCluster}`);
  ok(D.all.ok && D.noBig.ok && D.noCluster.ok, 'üç karşılaştırma geçerli (n ≥ NMIN)');
  ok(D.all.n === 211 && D.noBig.n === 210 && D.noCluster.n === 150, `n değerleri ${D.all.n}/${D.noBig.n}/${D.noCluster.n}`);
  ok(D.all.q < 0.7 && D.noCluster.q > D.all.q + 0.2, `geç küme q'yu düşürür; çıkarınca yükselir: ${D.all.q.toFixed(2)} → ${D.noCluster.q.toFixed(2)}`);
  const G = X.amrGrid(ev, tf, 3, [100], [10]); ok(Math.abs(G.T - D.all.q) < 1e-12, 'bütün olaylar q = ızgara hücresinin q değeri');
  // NMIN koşulu: küme çıkarılınca n < NMIN → geçersiz
  const ev2 = ev.slice(big), cl2 = cl.slice(big).map(c => c - big), D2 = X.amrDropCheck(ev2, cl2, cell, tf, 3);
  ok(D2.all.ok && !D2.noCluster.ok && D2.noCluster.q === null, `n < NMIN olunca geçersiz: n=${D2.noCluster.n}`); }

console.log(`${fail ? '!! FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`);
process.exit(fail ? 1 : 0);
