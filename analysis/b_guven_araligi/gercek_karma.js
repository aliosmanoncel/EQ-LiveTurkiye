// ISC tarihsel pencerelerinde (1900–1970, 1971–1997) bugünkü hesap ile ortak 0,1 sınıfına yuvarlamanın karşılaştırılması.
// Üretim kodu (computeMc, computeBvalue, computeBvalueTimeSeries, bCiFields). Uygulamadaki pencere seçimi: src = ISC, yıl aralığı,
// kullanılan büyüklük mw || mag (dönüşüm kapalı). Mc her iki durumda da computeMc ile (0,1 sınıflarında; yuvarlamadan bağımsız).
'use strict';
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); return src.slice(i, j); };
global.location = { search: '' };
(0, eval)(['var bTimeAnchor = "mean"; var BT_WIN_N = 100;', cut('const MC_DM = 0.1;', '// Aki (1965) MLE b-değeri').replace('const MC_DM', 'var MC_DM'),
  ...['computeBvalue', 'bWinStart', 'bWinTime', 'computeBvalueTimeSeries'].map(fn), cut('function bConfidence95(b, n)', '// Kayan pencere b-değeri'),
  'global.__x = { computeMc, computeBvalue, computeBvalueTimeSeries, bCiFields, bCiTxt };'].join('\n'));
const X = global.__x;
const cat = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'data', 'eq_historical.json'), 'utf8')).events;
const r01 = x => +(Math.round(x * 10 + 1e-9) / 10).toFixed(1);
const res = [];
for (const [y0, y1] of [[1900, 1970], [1971, 1997]]) {
  const ev = cat.filter(e => e.src === 'ISC' && +e.time.slice(0, 4) >= y0 && +e.time.slice(0, 4) <= y1 && (e.mag || 0) > 0)
    .map(e => ({ time: new Date(e.time), mag: e.mag, mw: e.mw || e.mag }));
  const Mc = X.computeMc(ev), row = { donem: `${y0}–${y1}`, Mc, N_toplam: ev.length };
  for (const [k, conv] of [['bugun', m => m], ['yuvarla', r01]]) {
    const L = ev.map(e => ({ ...e, mw: conv(e.mw) })), mags = L.map(e => e.mw), sub = mags.filter(m => m >= Mc - 1e-9);
    const b = X.computeBvalue(mags, Mc, 0.1), ci = X.bCiFields(b, sub.length, sub.map(m => m - Mc), 0.1);
    const bt = X.computeBvalueTimeSeries(L, Mc, 10, 0.1, 100).series;
    row[k] = { N: sub.length, b: +b.toFixed(3), aralik: X.bCiTxt({ b, ...ci }).trim(), yontem: ci.ciM, bt_pencere: bt.length,
      bt_ort: bt.length ? +(bt.reduce((a, q) => a + q.b, 0) / bt.length).toFixed(3) : null, bt_yontem: [...new Set(bt.map(q => q.ciM))].join('/') };
  }
  res.push(row);
}
fs.writeFileSync(path.join(__dirname, 'out', 'gercek_karma.json'), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1));
