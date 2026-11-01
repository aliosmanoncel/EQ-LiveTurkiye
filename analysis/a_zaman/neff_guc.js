// Düzeltilmiş b–a korelasyon testinin gücü (2026-10-31): ortak yenilikli iki AR(1) serisi; index.html'deki aPearson, aLag1, aNeffTest kullanılır.
// Kullanım (depo kökünde): node analysis/a_zaman/neff_guc.js
const fs = require('fs'), vm = require('vm'), src = fs.readFileSync('index.html', 'utf8');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const X = {}; vm.createContext(X); vm.runInContext(['aPearson', 'aLag1', 'aNeffTest'].map(fn).join('\n'), X);
const rng = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const rnd = rng(33), g = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
// Gerçek korelasyon c: ortak yenilik e_ortak ile iki AR(1) serisi (aynı φ); süreçler arası korelasyon = c
const cift = (n, f, c) => { const x = [], y = []; let px = 0, py = 0; for (let i = 0; i < n + 50; i++) { const e = g(), u = g(), v = g(); px = f * px + Math.sqrt(c) * e + Math.sqrt(1 - c) * u; py = f * py + Math.sqrt(c) * e + Math.sqrt(1 - c) * v; if (i >= 50) { x.push(px); y.push(py); } } return [x, y]; };
for (const [n, f] of [[13, 0.5], [22, 0.5], [22, 0.8], [50, 0.8]]) for (const c of [0.5, 0.8]) { let ham = 0, duz = 0; const R = 3000;
  for (let i = 0; i < R; i++) { const [x, y] = cift(n, f, c), seg = [x.map((v, j) => ({ a: v, b: y[j] }))], r = X.aPearson(x, y), ra = X.aLag1(seg, q => q.a), rb = X.aLag1(seg, q => q.b), t = X.aNeffTest(r.r, n, ra ? ra.r : null, rb ? rb.r : null);
    if (r.p < 0.05) ham++; if (t.p !== null && t.p < 0.05) duz++; }
  console.log(`n = ${n}, φ = ${f}, gerçek korelasyon ${c}: güç ham %${(100 * ham / R).toFixed(1)}, düzeltilmiş %${(100 * duz / R).toFixed(1)}`); }
