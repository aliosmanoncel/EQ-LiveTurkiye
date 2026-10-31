// n_eff düzeltmesinin sağlamlığı (2026-10-31; ChatGPT incelemesi m. 2). index.html'deki aPearson, aLag1, aNeffTest kullanılır.
// H0: iki seri birbirinden BAĞIMSIZ (gerçek ilişki yok). α = 0,05'te ham ve düzeltilmiş testin reddetme oranı; düzeltilmiş test edilebilen oran (n_eff ≥ 5).
// Yapılar: AR(1) (φ ve n ızgarası), AR(2) (uzun bellek), MA(1) (yalnız gecikme-1), rastgele yürüyüş (durağan değil),
//          ortak yönde doğrusal eğilim + AR(1) gürültü (iki süreç bağımsız ama ikisi de eğilimli). Ayrıca kısa serilerde ρ̂'nın yanlılığı.
// Kullanım (depo kökünde): node analysis/a_zaman/neff_saglamlik.js
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const X = {}; vm.createContext(X); vm.runInContext(['aPearson', 'aLag1', 'aNeffTest'].map(fn).join('\n'), X);
const rng = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const rnd = rng(2026), g = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
const BURN = 100;
const ar1 = (n, f) => { let x = 0; const o = []; for (let i = 0; i < n + BURN; i++) { x = f * x + g(); if (i >= BURN) o.push(x); } return o; };
const ar2 = (n, f1, f2) => { let x1 = 0, x2 = 0; const o = []; for (let i = 0; i < n + BURN; i++) { const x = f1 * x1 + f2 * x2 + g(); x2 = x1; x1 = x; if (i >= BURN) o.push(x); } return o; };
const ma1 = (n, th) => { let e0 = g(); const o = []; for (let i = 0; i < n; i++) { const e = g(); o.push(e + th * e0); e0 = e; } return o; };
const rw = n => { let x = 0; const o = []; for (let i = 0; i < n; i++) { x += g(); o.push(x); } return o; };
const trend = (n, f, s) => ar1(n, f).map((v, i) => v + s * i);
const R = 2000;
function deney(gen) {
  let ham = 0, duz = 0, test = 0, rhoS = 0, rhoN = 0;
  for (let i = 0; i < R; i++) { const [x, y] = gen(), seg = [x.map((v, j) => ({ a: v, b: y[j] }))], r = X.aPearson(x, y); if (!r) continue;
    const ra = X.aLag1(seg, q => q.a), rb = X.aLag1(seg, q => q.b), t = X.aNeffTest(r.r, x.length, ra ? ra.r : null, rb ? rb.r : null);
    if (ra) { rhoS += ra.r; rhoN++; } if (r.p < 0.05) ham++; if (t.p !== null) { test++; if (t.p < 0.05) duz++; } }
  return { ham: ham / R, duz: duz / R, test: test / R, rho: rhoN ? rhoS / rhoN : null };
}
const satir = [], yaz = (yapi, par, n, r) => { satir.push({ yapi, par, n, ...r }); console.log(`${yapi.padEnd(22)} ${par.padEnd(16)} n = ${String(n).padStart(2)}: ham %${(100 * r.ham).toFixed(1).padStart(4)} | düzeltilmiş %${(100 * r.duz).toFixed(1).padStart(4)} | test edilebilen %${(100 * r.test).toFixed(0).padStart(3)} | ort. ρ̂ ${r.rho === null ? '—' : r.rho.toFixed(2)}`); };
for (const f of [0.2, 0.5, 0.8, 0.9, 0.95]) for (const n of [6, 8, 10, 13, 22, 50]) yaz('AR(1)', `φ = ${f}`, n, deney(() => [ar1(n, f), ar1(n, f)]));
for (const n of [13, 22, 50]) yaz('AR(2) uzun bellek', 'φ₁ 0,5, φ₂ 0,4', n, deney(() => [ar2(n, 0.5, 0.4), ar2(n, 0.5, 0.4)]));
for (const n of [13, 22, 50]) yaz('MA(1)', 'θ = 0,8', n, deney(() => [ma1(n, 0.8), ma1(n, 0.8)]));
for (const n of [13, 22, 50]) yaz('Rastgele yürüyüş', 'durağan değil', n, deney(() => [rw(n), rw(n)]));
for (const n of [13, 22, 50]) yaz('Ortak yönde eğilim', 'AR(1) 0,5 + eğim', n, deney(() => [trend(n, 0.5, 2 / n), trend(n, 0.5, 2 / n)]));
fs.writeFileSync(path.join(__dirname, 'neff_saglamlik.json'), JSON.stringify({ tekrar: R, alfa: 0.05, satir }, null, 1));
