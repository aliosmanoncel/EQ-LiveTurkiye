// Birim testleri: karma büyüklük çözünürlüğünde ortak sınıflama (2026-10-25; RAPOR §16).
// Fonksiyonlar index.html'den okunur (bGridRound, bGridOffCount, bGridVals, bGridList, Mc zinciri, computeBvalue, aralık bloğu).
// Denetlenen iddialar:
//   1. Yuvarlama, Mc'nin kullandığı sınıflamayla (computeMcSrc: Math.round(m·10)/10) birebir aynıdır; yarım değerler (x,x5) dahil.
//   2. Izgaradaki veride ve ?bgrid=ham kipinde hiçbir değer değişmez (aynı dizi nesnesi döner).
//   3. bGridList yalnız kullanılan büyüklüğü (mw ?? mag) değiştirir, ham değeri _mRaw'da korur; diğer alanlara dokunmaz.
//   4. Gerçek ISC pencereleri (data/eq_historical.json): Mc yuvarlamadan önce ve sonra aynıdır (Mc ve b aynı kümeyle tutarlı);
//      b ve %95 aralık RAPOR §16.3 ile aynı (1900–1970: 0,561, N = 464, T–M; 1971–1997: 0,720, N = 4855, T–M); ?bgrid=ham'da eski değerler.
//   5. Ön işleme aralık kipinden bağımsızdır: ?bci=normal'de de aynı yuvarlanmış küme kullanılır (yalnız aralık yöntemi değişir).
// Kullanım (depo kökünde): node scripts/test_b_grid.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const root = path.join(__dirname, '..');
const src = fs.readFileSync(process.argv[2] || path.join(root, 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
const gridDecl = src.match(/^let B_GRID_MODE = [^\n]*$/m)[0];
const mk = search => { const ctx = { URLSearchParams, location: { search } }; vm.createContext(ctx);
  vm.runInContext([gridDecl.replace('let ', 'var '), 'var tmGridInfo = null;', ...['bGridRound', 'bGridOffCount', 'bGridVals', 'bGridList'].map(fn),
    cut('const MC_DM = 0.1;', '// Aki (1965) MLE b-değeri').replace('const MC_DM', 'var MC_DM'), cut('function computeBvalue(', '// Aki (1965) MLE için %95'),
    cut('function bConfidence95(b, n)', '// Kayan pencere b-değeri'),
    'globalThis.__x = { bGridRound, bGridVals, bGridList, computeMc, computeBvalue, bCiFields, get mode() { return B_GRID_MODE; }, get ci() { return B_CI_METHOD; } };'].join('\n'), ctx);
  return ctx.__x; };
const X = mk(''), H = mk('?bgrid=ham'), NB = mk('?bci=normal');
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };

ok(X.mode === 'sinif' && H.mode === 'ham', `kip: varsayılan ${X.mode}, ?bgrid=ham → ${H.mode}`);
// 1. computeMcSrc sınıflamasıyla birebir (0,01 adımlı bütün değerler 2,00–8,00)
{ let same = true, bad = null; for (let k = 200; k <= 800; k++) { const m = +(k / 100).toFixed(2), a = X.bGridRound(m, 0, 0.1), b = +(Math.round(m * 10) / 10).toFixed(1);
    if (a !== b) { same = false; bad = [m, a, b]; break; } }
  ok(same, `yuvarlama = computeMcSrc sınıflaması (601 değer, yarım değerler dahil)${bad ? ' ilk fark ' + bad : ''}`);
  ok(X.bGridRound(4.75, 0, 0.1) === 4.8 && X.bGridRound(4.74, 0, 0.1) === 4.7 && X.bGridRound(4.65, 0, 0.1) === 4.7, 'yarım değer yukarı: 4,75 → 4,8; 4,74 → 4,7; 4,65 → 4,7'); }
// 2. ızgarada ve ham kipte değişmez
{ const v = [3.0, 3.1, 4.7, 5.5, 6.2]; ok(X.bGridVals(v).vals === v && X.bGridVals(v).nOff === 0, 'ızgaradaki veri: aynı dizi, nOff = 0');
  const w = [3.0, 3.13, 4.7]; ok(H.bGridVals(w).vals === w && X.bGridVals(w).nOff === 1 && X.bGridVals(w).vals.join() === '3,3.1,4.7', 'karma veri: varsayılanda yuvarlanır, ?bgrid=ham\'da değişmez');
  const z = [2.093, 2.186, 2.279]; ok(X.bGridVals(z, 2.0, 0.093).nOff === 0, 'eşlenmiş ızgara (a = 2,0, ΔM = 0,093): ızgaradaki değerler değişmez'); }
// 3. bGridList alanları
{ const L = [{ id: 'a', mag: 4.76, mw: null, mtype: 'mb' }, { id: 'b', mag: 5.1, mw: 5.33, mtype: 'MS' }, { id: 'c', mag: 4.7, mtype: 'md' }], g = X.bGridList(L);
  ok(g.nOff === 2 && g.list[0].mag === 4.8 && g.list[0]._mRaw === 4.76 && g.list[1].mw === 5.3 && g.list[1].mag === 5.1 && g.list[1]._mRaw === 5.33 && g.list[2] === L[2] && g.list[0].mtype === 'mb' && L[0].mag === 4.76,
    'bGridList: kullanılan büyüklük yuvarlanır, ham değer _mRaw\'da, ızgaradaki olay aynı nesne, girdi değişmez'); }
// 4–5. gerçek ISC pencereleri
const cat = JSON.parse(fs.readFileSync(path.join(root, 'data', 'eq_historical.json'), 'utf8')).events;
const EXP = { '1900–1970': { b: 0.561, n: 464, bH: 0.526, nH: 430 }, '1971–1997': { b: 0.720, n: 4855, bH: 0.718, nH: 4808 } };
for (const [y0, y1] of [[1900, 1970], [1971, 1997]]) {
  const key = `${y0}–${y1}`, ev = cat.filter(e => e.src === 'ISC' && +e.time.slice(0, 4) >= y0 && +e.time.slice(0, 4) <= y1 && (e.mag || 0) > 0)
    .map(e => ({ time: new Date(e.time), mag: e.mag, mw: e.mw || e.mag, mtype: e.mtype }));
  const run = Z => { const g = Z.bGridList(ev), Mc0 = Z.computeMc(ev), Mc1 = Z.computeMc(g.list), mags = g.list.map(e => e.mw ?? e.mag), sub = mags.filter(m => m >= Mc1 - 1e-9);
    const b = Z.computeBvalue(mags, Mc1, 0.1), ci = Z.bCiFields(b, sub.length, sub.map(m => m - Mc1), 0.1); return { Mc0, Mc1, b, n: sub.length, ci, nOff: g.nOff }; };
  const r = run(X), h = run(H), nb = run(NB), e = EXP[key];
  ok(r.Mc0 === r.Mc1 && r.nOff > 0, `${key}: Mc yuvarlamadan önce ve sonra aynı (${r.Mc0}); ${r.nOff} ızgara dışı değer`);
  ok(Math.abs(r.b - e.b) < 5e-4 && r.n === e.n && r.ci.ciM === 'tm', `${key}: b = ${r.b.toFixed(3)} (beklenen ${e.b}), N = ${r.n}, aralık ${r.ci.ciM}`);
  ok(Math.abs(h.b - e.bH) < 5e-4 && h.n === e.nH && h.ci.ciM === 'chi2', `${key}, ?bgrid=ham: eski b = ${h.b.toFixed(3)}, N = ${h.n}, χ²`);
  ok(nb.b === r.b && nb.n === r.n && nb.ci.ciM === 'normal', `${key}, ?bci=normal: aynı yuvarlanmış küme (b = ${nb.b.toFixed(3)}, N = ${nb.n}), yalnız aralık yöntemi normal`);
}

console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
