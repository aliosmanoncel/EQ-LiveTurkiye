// Birim testi (2026-10-18): b(t) sınıf renkleri (btClassOf) ve AMR istatistiksel destek düzeyi (amrSupport).
// Fonksiyonlar index.html'den okunur. Denetlenen iddialar:
//   1. Tam üç sınıf vardır; eşikler 0,7 ve 1,4'tür (uygulamanın b-değeri haritasıyla aynı).
//   2. Pencere yalnızca %95 aralığının (b ± err) tamamı bir sınıftaysa sınıflanır; sınırı kesen aralık null (renksiz) döner.
//   3. AMR destek düzeyi önceden tanımlı p eşiklerine göre üç düzeydir: ≤ 0,01 güçlü, ≤ 0,05 sınırlı, aksi halde yetersiz.
// Kullanım (depo kökünde): node scripts/test_class_levels.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const cst = src.match(/^const BT_CLASS = [^\n]*$/m); if (!cst) throw new Error('BT_CLASS bulunamadı');
const ctx = {}; vm.createContext(ctx);
vm.runInContext([cst[0].replace('const ', 'var '), fn('btClassOf'), fn('amrSupport'), 'globalThis.__x = { btClassOf, amrSupport, BT_CLASS };'].join('\n'), ctx);
const X = ctx.__x; let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log('FAIL', m); } };
ok(X.BT_CLASS.lo === 0.7 && X.BT_CLASS.hi === 1.4 && Object.keys(X.BT_CLASS.col).length === 3, 'üç sınıf, eşikler 0,7 / 1,4');
const C = [[0.5, 0.1, 'low'], [0.6, 0.11, null], [1.0, 0.2, 'mid'], [0.85, 0.15, 'mid'], [0.8, 0.15, null], [1.3, 0.11, null], [1.7, 0.2, 'high'], [1.6, 0.12, 'high'], [1.5, 0.1, null], [1.0, NaN, null]];
C.push([0.7, 0, 'mid'], [1.4, 0, 'mid'], [0.69, 0, 'low'], [1.41, 0, 'high'], [0.8, 0.1, 'mid'], [1.3, 0.1, 'mid'], [0.6, 0.1, null], [1.5, 0.1, null],
  [1.0, -0.1, null], [1.0, Infinity, null], [NaN, 0.1, null], [undefined, 0.1, null], [0.5, null, null]);   // sınırlar (0,7 ve 1,4 tipik), sıfır genişlik, geçersiz
C.forEach(([b, e, k]) => ok(X.btClassOf(b, e) === k, `b = ${b} ± ${e} → ${k} (bulunan ${X.btClassOf(b, e)})`));
// rastgele: sınıflanan her pencerenin aralığı tamamen sınıf içinde
let s = 7; const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
for (let i = 0; i < 5000; i++) { const b = 0.3 + 1.6 * r(), e = 0.02 + 0.4 * r(), k = X.btClassOf(b, e);
  const E = 1e-9, inside = k === 'low' ? b + e < 0.7 - E : k === 'mid' ? b - e >= 0.7 - E && b + e <= 1.4 + E : k === 'high' ? b - e > 1.4 + E : !(b + e < 0.7 - E || (b - e >= 0.7 - E && b + e <= 1.4 + E) || b - e > 1.4 + E);
  if (!inside) { ok(false, `rastgele b=${b} e=${e} → ${k}`); break; } }
pass++;
ok(X.amrSupport(0.005).k === 'strong' && X.amrSupport(0.01).k === 'strong', 'p ≤ 0,01 → güçlü');
ok(X.amrSupport(0.011).k === 'limited' && X.amrSupport(0.05).k === 'limited', '0,01 < p ≤ 0,05 → sınırlı');
ok(X.amrSupport(0.0501).k === 'insufficient' && X.amrSupport(0.9).k === 'insufficient', 'p > 0,05 → yetersiz');
ok(X.amrSupport(NaN) === null, 'p yoksa düzey yok');
console.log(`${fail ? '!! FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
