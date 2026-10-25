// Birim testleri: seçilebilir b(t) pencere boyutu (2026-10-25).
// Fonksiyonlar index.html'den okunur (computeBvalue, aralık bloğu, bWinStart, bWinTime, computeBvalueTimeSeries, btDefaultStep, btWinNote).
// Denetlenen iddialar:
//   1. Varsayılan (BT_WIN_N = 100) ile açıkça nWin = 100 aynı seriyi verir; ?btn yoksa BT_WIN_N = 100.
//   2. nWin = 50 / 30 / 20'de her pencere tam nWin olaydır; pencere sayısı ⌊(N − nWin)/adım⌋ + 1; her b, aynı olaylardan
//      computeBvalue ile birebirdir; aralık alanları (lo, hi, ciM) doludur.
//   3. Adım varsayılanı N/10 (100 → 10, 50 → 5, 30 → 3, 20 → 2); ?btn yalnız 100/50/30/20 kabul eder.
//   4. Uyarı metni N = 100'de boş, N < 100'de dolu; N = 20 "keşif" olarak etiketlenir.
// Kullanım (depo kökünde): node scripts/test_bt_window.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const block = () => { const i = src.indexOf('\nfunction bConfidence95('), j = src.indexOf('// Kayan pencere b-değeri', i); return src.slice(i + 1, j); };
const opts = src.match(/^const BT_WIN_OPTS = [^\n]*$/m)[0], winN = src.slice(src.indexOf('let BT_WIN_N = '), src.indexOf('\nfunction btDefaultStep('));
const mk = search => { const ctx = { URLSearchParams, location: { search }, localStorage: { getItem: () => null } }; vm.createContext(ctx);
  vm.runInContext(['var bTimeAnchor = "mean";', opts.replace('const ', 'var '), winN.replace('let ', 'var '), ...['btDefaultStep', 'btWinNote', 'computeBvalue', 'bWinStart', 'bWinTime', 'computeBvalueTimeSeries'].map(fn), block(),
    'globalThis.__x = { computeBvalue, computeBvalueTimeSeries, btDefaultStep, btWinNote, get N() { return BT_WIN_N; }, set N(v) { BT_WIN_N = v; } };'].join('\n'), ctx);
  return ctx.__x; };
const X = mk('');
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };

// YAPAY katalog: b = 1, M ≥ 2,0, ΔM = 0,1, 400 olay, 2015–2025
let s = 4242; const rnd = () => (s = (s * 48271) % 2147483647) / 2147483647;
const T0 = Date.parse('2015-01-01'), T1 = Date.parse('2025-01-01');
const ev = Array.from({ length: 400 }, () => ({ time: new Date(T0 + rnd() * (T1 - T0)), mag: +(2.0 + Math.floor(-Math.log(1 - rnd()) / Math.LN10 / 0.1) * 0.1).toFixed(1) }));
const Mc = 2.0;

ok(X.N === 100 && mk('?btn=50').N === 50 && mk('?btn=40').N === 100 && mk('?btn=20').N === 20, `URL: varsayılan ${X.N}; ?btn=50 → 50; ?btn=40 (geçersiz) → 100; ?btn=20 → 20`);
{ const a = X.computeBvalueTimeSeries(ev, Mc, 10, 0.1), b = X.computeBvalueTimeSeries(ev, Mc, 10, 0.1, 100);
  ok(JSON.stringify(a) === JSON.stringify(b) && a.series.length === Math.floor((400 - 100) / 10) + 1, `varsayılan = nWin 100 (${a.series.length} pencere)`); }
for (const [n, st] of [[100, 10], [50, 5], [30, 3], [20, 2]]) {
  X.N = n; ok(X.btDefaultStep() === st, `N = ${n} → adım ${X.btDefaultStep()}`);
  const r = X.computeBvalueTimeSeries(ev, Mc, st, 0.1), sorted = ev.slice().sort((p, q) => p.time - q.time);
  const expN = Math.floor((400 - n) / st) + 1; let same = true, filled = true;
  r.series.forEach((q, k) => { const w = sorted.slice(k * st, k * st + n).map(e => e.mag), b = X.computeBvalue(w, Mc, 0.1); same = same && Math.abs(q.b - b) < 1e-12; filled = filled && Number.isFinite(q.lo) && q.hi > q.lo && !!q.ciM; });
  ok(r.series.length === expN && same && filled, `N = ${n}: ${r.series.length} pencere (beklenen ${expN}); b'ler computeBvalue ile birebir; aralık alanları dolu`);
}
X.N = 100; ok(X.btWinNote() === '' && X.btWinNote(true) === '', 'N = 100: uyarı yok');
X.N = 30; ok(/N = 30/.test(X.btWinNote()) && !/keşif/.test(X.btWinNote()), 'N = 30: uyarı var, keşif etiketi yok');
X.N = 20; ok(/keşif/.test(X.btWinNote()) && /exploratory/.test(X.btWinNote(true)), 'N = 20: keşif amaçlı olarak etiketlenir');
{ X.N = 50; const small = ev.slice(0, 60); ok(X.computeBvalueTimeSeries(small, Mc, 5, 0.1).series.length > 0 && X.computeBvalueTimeSeries(small, Mc, 10, 0.1, 100).series.length === 0,
    '60 olay: N = 100 ile b(t) yok, N = 50 ile var'); }

console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
