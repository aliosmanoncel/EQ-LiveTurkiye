// Birim testleri: b(t) uyarlamalı gösterim adımı ve zaman damgası (2026-10-17).
// Fonksiyonlar doğrudan index.html'den okunur (bWinStart, bWinTime, btAdaptive, computeBvalue, bConfidence95,
// computeBvalueTimeSeries); kopya tutulmaz.
// Denetlenen iddialar:
//   1. Seyreltme yalnızca gösterimi etkiler: gösterilen her pencere hesaplanan bir pencerenin AYNISIDIR,
//      son pencere korunur, özet istatistikler (b ort., b son, ±%95) tam seriden hesaplanır ve değişmez.
//   2. Eşik ve hedef: > 500 pencerede etkinleşir, gösterilen pencere sayısı ≈ 200; ≤ 500 pencerede seri aynen döner.
//   3. Zaman damgası (ortalama / ortanca / son) yalnızca noktanın yatay yerini değiştirir: aynı pencerenin b ve
//      ±%95 değeri üç seçenekte birebir aynıdır; ortalama zaman pencerenin ilk ve son olayı arasındadır.
// Kullanım (depo kökünde): node scripts/test_bt_adaptive.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => {   // üst düzey "function name(" bloğunu, bir sonraki üst düzey satıra kadar keser
  const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j);
};
const cst = src.match(/^const BT_ADAPT_MAX = [^\n]*$/m); if (!cst) throw new Error('BT_ADAPT_MAX bulunamadı');
const ciBlock = () => {   // 2026-10-25: b güven aralığı bloğu (bConfidence95 … bCiMethodTxt); BCI=normal ortam değişkeni eski ±1,96·b/√N kipini seçer
  const i = src.indexOf('\nfunction bConfidence95('), j = src.indexOf('// Kayan pencere b-değeri', i); if (i < 0 || j < 0) throw new Error('bulunamadı: aralık bloğu');
  return src.slice(i + 1, j) + (process.env.BCI && src.includes('let B_CI_METHOD') ? `\nB_CI_METHOD = '${process.env.BCI}';` : ''); };
const ctx = {}; vm.createContext(ctx);
vm.runInContext(['var bTimeAnchor = "mean";', cst[0].replace('const ', 'var '),
  ...['bWinStart', 'bWinTime', 'btAdaptive', 'computeBvalue', 'computeBvalueTimeSeries'].map(fn), ciBlock(),
  'globalThis.__x = { bWinStart, bWinTime, btAdaptive, computeBvalueTimeSeries, setA: a => { bTimeAnchor = a; } };'].join('\n'), ctx);
const X = ctx.__x;
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };

// Sentetik katalog: G-R b = 1 (M ≥ 1,5, ΔM = 0,1), 2000–2026; %12'si 3 günlük yoğun kümede (testere görünümü)
// YAPAY VERİ: gerçek bir katalog değildir, fiziksel yorum için kullanılmaz. Küme (1 Haziran 2020) testere görünümünü üretmek
// için yerleştirildi. 17 Ekim 2026 ekran görüntülerindeki 2015–2016 b = 0,7 dönemi de bu üretecin bir türevinde yapay olarak eklendi.
function catalog(n, seed) {
  let s = seed; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const t0 = Date.UTC(2000, 0, 1), t1 = Date.UTC(2026, 0, 1), tc = Date.UTC(2020, 5, 1), ev = [];
  for (let i = 0; i < n; i++) {
    const t = i < 0.12 * n ? tc + rnd() * 3 * 864e5 : t0 + rnd() * (t1 - t0);
    ev.push({ time: new Date(t), mag: Math.round((1.5 - Math.log10(1 - rnd())) * 10) / 10 });
  }
  return ev;
}
const MC = 1.5, avg = a => a.reduce((p, c) => p + c.b, 0) / a.length;

// ── 1–2. Seyreltme: alt küme, son pencere, özetler, eşik ─────────────
for (const [n, step] of [[600, 1], [700, 10], [5000, 10], [18000, 10], [18000, 1], [2000, 1]]) {
  for (const a of ['mean', 'mid', 'end']) {
    X.setA(a);
    const { series, N } = X.computeBvalueTimeSeries(catalog(n, 11), MC, step), AD = X.btAdaptive(series, N, step), tag = `n=${n} adım=${step} ${a}`;
    if (series.length <= 500) { ok(!AD.on && AD.ser === series && AD.step === step, `${tag}: ≤500 pencerede seri aynen dönmeli`); continue; }
    ok(AD.on, `${tag}: >500 pencerede seyreltme etkin olmalı (${series.length})`);
    ok(AD.step % step === 0 && AD.step >= step, `${tag}: gösterim adımı hesaplama adımının katı olmalı (${AD.step})`);
    ok(AD.ser.length >= 150 && AD.ser.length <= 260, `${tag}: gösterilen pencere ≈200 olmalı (${AD.ser.length})`);
    ok(AD.ser.every(p => series.includes(p)), `${tag}: gösterilen her pencere hesaplanan bir pencere olmalı`);
    ok(AD.ser[AD.ser.length - 1] === series[series.length - 1], `${tag}: son pencere korunmalı`);
    const idx = AD.ser.map(p => series.indexOf(p));
    ok(idx.every((v, k) => k === 0 || v - idx[k - 1] === AD.f), `${tag}: aralık sabit olmalı (f=${AD.f})`);
    // Özetler renderBvalueTS'teki gibi tam seriden: seyreltme çağrısı seriyi değiştirmemeli
    const snap = JSON.stringify(series); X.btAdaptive(series, N, step);
    ok(JSON.stringify(series) === snap, `${tag}: btAdaptive seriyi değiştirmemeli`);
    const again = X.computeBvalueTimeSeries(catalog(n, 11), MC, step).series;
    ok(Math.abs(avg(again) - avg(series)) < 1e-12 && again[again.length - 1].b === series[series.length - 1].b, `${tag}: b ort. / b son yeniden hesapta aynı`);
  }
}

// ── 3. Zaman damgası yalnızca yatay konumu değiştirir ───────────────
for (const [n, step] of [[3000, 1], [3000, 10], [3099, 10]]) {
  const ev = catalog(n, 23), R = {};
  for (const a of ['mean', 'mid', 'end']) { X.setA(a); R[a] = X.computeBvalueTimeSeries(ev, MC, step).series; }
  const tag = `n=${n} adım=${step}`;
  // ortalama ve ortanca aynı pencere başlangıçlarını kullanır → b ve hata birebir aynı
  ok(R.mean.length === R.mid.length && R.mean.every((p, i) => p.b === R.mid[i].b && p.err === R.mid[i].err), `${tag}: ortalama ↔ ortanca b/hata aynı`);
  // son olay seçeneği pencereleri sona hizalar; hizalama aynıysa ((N−100) % adım = 0) b birebir aynı olmalı
  const Nev = ev.filter(e => e.mag >= MC).length;
  if ((Nev - 100) % step === 0) ok(R.end.length === R.mean.length && R.end.every((p, i) => p.b === R.mean[i].b && p.err === R.mean[i].err), `${tag}: son ↔ ortalama b/hata aynı (aynı hizalama)`);
  else { // farklı hizalamada bile her 'son' penceresi, adım 1 serisinde aynı b ile bulunmalı
    X.setA('end'); const all1 = X.computeBvalueTimeSeries(ev, MC, 1).series, bset = new Set(all1.map(p => p.b));
    ok(R.end.every(p => bset.has(p.b)), `${tag}: 'son' pencereleri adım-1 pencere kümesinin elemanı`); }
  // ortalama zaman pencerenin [ilk, son] aralığında; son ≥ ortalama ve ortanca
  X.setA('mean'); const W = X.computeBvalueTimeSeries(ev, MC, step).series;
  const sorted = [...ev].filter(e => e.mag >= MC).sort((a, b) => a.time - b.time);
  ok(W.every((p, i) => { const w = sorted.slice(i * step, i * step + 100); return p.t >= +w[0].time && p.t <= +w[99].time; }), `${tag}: ortalama zaman pencere içinde`);
  ok(W.every((p, i) => { const w = sorted.slice(i * step, i * step + 100); return Math.abs(p.t - w.reduce((s, e) => s + +e.time, 0) / 100) < 1; }), `${tag}: ortalama zaman = Σt/100`);
}

console.log(`${fail ? '!! ' : ''}${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`);
process.exit(fail ? 1 : 0);
