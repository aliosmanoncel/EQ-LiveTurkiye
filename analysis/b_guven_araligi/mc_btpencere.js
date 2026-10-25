// b(t) pencere boyutu (N = 100/50/30/20) Monte Carlo — üretim kodu (computeBvalueTimeSeries, bCiFields, btClassOf, bUtsuP; kopya yok).
// İdeal G–R, büyüklükler 0,1 ızgarasında, 600 olay (M ≥ Mc), adım N/10, zaman damgası ortalama.
// S0 durağan b = 1: pencere kapsaması, b̂/b, sınıflama şeridinde yanlış "düşük"/"yüksek" pencere oranı ve en az birini içeren seri oranı,
//    ilk ve son pencere (örtüşmeyen, bağımsız) Utsu P < 0,05 oranı (yanlış alarm).
// S1/S2: ilk 300 olay b = 1,0, son 300 olay b = 0,8 (S1) ya da 0,6 (S2): değişim sonrası tamamen yeni dönemdeki pencerelerin
//    "düşük b" (aralığın tamamı < 0,7) sınıflanma oranı ve ilk–son pencere Utsu P < 0,05 oranı (saptama gücü).
'use strict';
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); return src.slice(i, j); };
global.location = { search: '' };
(0, eval)(['var bTimeAnchor = "mean";', src.match(/^const BT_CLASS = [^\n]*$/m)[0].replace('const ', 'var '), 'var BT_WIN_N = 100;',
  ...['computeBvalue', 'bWinStart', 'bWinTime', 'computeBvalueTimeSeries', 'btClassOf'].map(fn), cut('function bConfidence95(b, n)', '// Kayan pencere b-değeri'),
  'global.__x = { computeBvalueTimeSeries, btClassOf, bUtsuP };'].join('\n'));
const X = global.__x, REPS = +(process.argv[2] || 2000), SEED = +(process.argv[3] || 20261027); let s = SEED;
const rnd = () => (s = (s * 48271) % 2147483647) / 2147483647, Mc = 3.0, T0 = Date.parse('2010-01-01'), DAY = 864e5;
const mag = b => +(Mc + Math.floor(-Math.log(1 - rnd()) / (b * Math.LN10) / 0.1) * 0.1).toFixed(1);
const cat = (b1, b2) => Array.from({ length: 600 }, (_, k) => ({ time: new Date(T0 + k * DAY), mag: mag(k < 300 ? b1 : b2) }));
const out = [], t0 = Date.now();
for (const N of [100, 50, 30, 20]) for (const [sc, b2] of [['S0', 1.0], ['S1', 0.8], ['S2', 0.6]]) {
  const st = Math.max(1, Math.round(N / 10)); let cov = 0, nw = 0, bsum = 0, falseW = 0, serAny = 0, lowPost = 0, nPost = 0, utsu = 0;
  for (let r = 0; r < REPS; r++) {
    const ser = X.computeBvalueTimeSeries(cat(1.0, b2), Mc, st, 0.1, N).series; let any = false;
    for (const q of ser) { const t1 = q.t1 ?? q.t, t0w = q.t0 ?? q.t, k = X.btClassOf(q.b, q.err, q.lo, q.hi);
      const pre = (t1 - T0) / DAY < 300 - 1e-6, post = (t0w - T0) / DAY >= 300 - 1e-6;   // tamamen değişim öncesi / sonrası pencere
      if (sc === 'S0' || pre) { const bt = 1.0; nw++; cov += q.lo <= bt && bt <= q.hi; bsum += q.b / bt; if (k === 'low' || k === 'high') { falseW++; any = true; } }
      if (sc !== 'S0' && post) { nPost++; lowPost += k === 'low'; } }
    serAny += any; const f = ser[0], l = ser[ser.length - 1]; utsu += X.bUtsuP(f.b, N, l.b, N) < 0.05;
  }
  out.push({ N, adim: st, senaryo: sc, b_sonra: b2, pencere_kapsama: cov / nw, bhat_oran: bsum / nw, yanlis_sinif_pencere: falseW / nw, yanlis_sinif_seri: serAny / REPS,
    dusuk_sinif_sonra: nPost ? lowPost / nPost : null, utsu_ilk_son: utsu / REPS });
}
fs.writeFileSync(path.join(__dirname, 'out', 'mc_btpencere.json'), JSON.stringify({ meta: { tekrar: REPS, tohum: SEED, olay: 600, Mc, sure_s: (Date.now() - t0) / 1000 }, sonuc: out }, null, 1));
for (const r of out) console.log(`N=${String(r.N).padStart(3)} ${r.senaryo} (b sonra ${r.b_sonra}) | kapsama ${r.pencere_kapsama.toFixed(3)} b̂/b ${r.bhat_oran.toFixed(3)} | yanlış sınıf pencere %${(100 * r.yanlis_sinif_pencere).toFixed(1)} seri %${(100 * r.yanlis_sinif_seri).toFixed(0)} | sonrası "düşük" ${r.dusuk_sinif_sonra === null ? '—' : '%' + (100 * r.dusuk_sinif_sonra).toFixed(0)} | Utsu ilk–son P<0,05 %${(100 * r.utsu_ilk_son).toFixed(1)}`);
console.log('süre', (Date.now() - t0) / 1000, 's');
