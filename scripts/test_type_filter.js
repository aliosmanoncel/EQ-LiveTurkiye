// Birim testleri: magnitüd tipi duyarlılık filtresi (MD / dönüştürülmemiş ML<1,7) — 2026-09-29.
// Fonksiyonlar index.html'den okunur. Kullanım (depo kökünde): node scripts/test_type_filter.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
const ctx = {}; vm.createContext(ctx);
vm.runInContext(cut('function tmIsMD(e)', 'function tmTypeFilterOpts()') + ';globalThis.X={tmIsMD,tmIsUnconvertedMLlow,tmTypeFilter};', ctx);
const X = ctx.X;
let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };

const ev = [
  { id: 1, mtype: 'MD', mag: 2.9 }, { id: 2, mtype: 'md', mag: 3.1 },
  { id: 3, mtype: 'ml', mag: 1.2 },                         // dönüştürülmemiş (mw yok)
  { id: 4, mtype: 'ML', mag: 1.6, mw: 1.6 },               // dönüştürülmemiş (mw = mag)
  { id: 5, mtype: 'ml', mag: 1.7, mw: 1.871 },             // dönüştürülmüş, sınırda: dahil kalmalı
  { id: 6, mtype: 'ml', mag: 1.5, mw: 1.685 },             // hipotetik: dönüştürülmüş ML<1,7 → ML<1,7 filtresi YAKALAMAMALI
  { id: 7, mtype: 'mw', mag: 5.3 }, { id: 8, mtype: 'mb', mag: 4.1, mw: 4.2 }, { id: 9, mtype: 'mdl', mag: 2.0 }];
const ids = r => r.list.map(e => e.id).join(',');

const d = X.tmTypeFilter(ev, { md: true, mlLow: true });
ok(d.list.length === ev.length && d.list.every((e, i) => e === ev[i]) && d.nMD === 0 && d.nMLlow === 0, 'varsayılan (ikisi dahil): liste AYNEN, aynı referanslar → mevcut yöntem (0.426) etkilenmez');
ok(X.tmTypeFilter(ev).list.length === ev.length, 'seçenek verilmezse varsayılan = dahil');
const a = X.tmTypeFilter(ev, { md: false, mlLow: true });
ok(ids(a) === '3,4,5,6,7,8,9' && a.nMD === 2, 'MD hariç: yalnız MD/md çıkar (büyük-küçük harf duyarsız), "mdl" gibi başka tip dokunulmaz');
const b = X.tmTypeFilter(ev, { md: true, mlLow: false });
ok(ids(b) === '1,2,5,6,7,8,9' && b.nMLlow === 2, 'ML<1,7 hariç: yalnız DÖNÜŞTÜRÜLMEMİŞ ML<1,7 çıkar; ML=1,7 ve dönüştürülmüş olay kalır');
const c = X.tmTypeFilter(ev, { md: false, mlLow: false });
ok(ids(c) === '5,6,7,8,9' && c.nMD + c.nMLlow + c.list.length === c.nIn, 'ikisi hariç: sayım korunumu (hariç + kalan = girdi)');
ok(ev.length === 9 && ev[0].mtype === 'MD' && ev[0].mag === 2.9 && !('removed' in ev[0]), 'girdi listesi ve olaylar DEĞİŞMEZ (silme/dönüştürme yok)');
ok(/id="tmInclMD" checked/.test(src) && /id="tmInclMLlow" checked/.test(src), 'UI: iki onay kutusu, varsayılan işaretli (dahil)');
ok(/searchParams\.set\('xmd', '1'\)/.test(src) && /searchParams\.set\('xmllow', '1'\)/.test(src) && /restoreTmTypeFilterFromURL\(\);/.test(src), 'URL: xmd / xmllow yalnız hariç tutulunca yazılır ve açılışta geri yüklenir');
ok(/const tf = tmTypeFilter\(evList, tmTypeFilterOpts\(\)\); evList = tf\.list;/.test(src) && src.indexOf('evList = tf.list') < src.indexOf('lastTmEvList = evList;'), 'filtre dönüşümden sonra, tamlık/b(t)/G-R zincirinden ÖNCE uygulanıyor');
ok(/Magnitüd tipi duyarlılık senaryosu/.test(src), 'poster: senaryo açıkken Veri ve Yöntem maddesi yazılır');
console.log(`\nPASS ${pass} FAIL ${fail}`); process.exit(fail ? 1 : 0);
