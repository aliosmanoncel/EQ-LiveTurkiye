// Birim testi (2026-11-01): canlı sorguda analiz penceresinin sonu şimdiyi aşmaz (regionClampEnd). index.html'den okunur.
// Denetimler: geçmiş bitiş değişmez; ileri bitiş şimdiye çekilir; boş değer korunur; T ve λ = n/T üzerindeki etki (Hong Kong örneği).
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const X = {}; vm.createContext(X); vm.runInContext(fn('regionClampEnd'), X);
let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
const YIL = 365.25 * 864e5, now = new Date(Date.UTC(2026, 10, 1, 14, 0, 0));
{ const e = new Date(Date.UTC(2026, 9, 31, 20, 59, 59)); ok(+X.regionClampEnd(e, now) === +e, 'geçmiş bitiş tarihi değişmez'); }
{ const e = new Date(Date.UTC(2026, 11, 31, 20, 59, 59)); ok(+X.regionClampEnd(e, now) === +now, 'ileri bitiş tarihi (2026-12-31) şimdiye çekilir'); }
{ ok(+X.regionClampEnd(now, now) === +now, 'bitiş = şimdi → değişmez'); ok(X.regionClampEnd(null, now) === null, 'boş bitiş korunur'); }
{ // Hong Kong karşılaştırması: 1971-01-01 (yerel, UTC+3) – 2026-12-31 23:59:59 (yerel); N(≥Mc) = 1405, b = 0,98, Mc = 4,84
  const t0 = Date.UTC(1970, 11, 31, 21), eski = Date.UTC(2026, 11, 31, 20, 59, 59), yeni = +X.regionClampEnd(new Date(eski), now);
  const T0 = (eski - t0) / YIL, T1 = (yeni - t0) / YIL, l0 = 1405 / T0 * Math.pow(10, -0.98 * (6 - 4.84)), l1 = 1405 / T1 * Math.pow(10, -0.98 * (6 - 4.84));
  ok(Math.abs(T0 - 56.0) < 0.01 && T1 < T0, `Hong Kong: T ${T0.toFixed(3)} → ${T1.toFixed(3)} yıl; λ(≥6) ${l0.toFixed(4)} → ${l1.toFixed(4)} /yıl (+%${(100 * (l1 / l0 - 1)).toFixed(2)}); tekrarlanma ${(1 / l0).toFixed(3)} → ${(1 / l1).toFixed(3)} yıl`); }
{ // Kısa pencere: 2026 yılının tamamı Kasım başında sorgulanırsa
  const t0 = Date.UTC(2025, 11, 31, 21), eski = Date.UTC(2026, 11, 31, 20, 59, 59), T0 = (eski - t0) / YIL, T1 = (+X.regionClampEnd(new Date(eski), now) - t0) / YIL;
  ok(T0 / T1 > 1.15, `kısa pencere (2026 tamamı, 1 Kasım'da): T ${T0.toFixed(3)} → ${T1.toFixed(3)} yıl (eski T %${(100 * (T0 / T1 - 1)).toFixed(0)} uzun)`); }
console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
