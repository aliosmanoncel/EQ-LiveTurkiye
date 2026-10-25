// Karma büyüklük çözünürlüğü (ISC tarihsel katalog benzeri) Monte Carlo — üretim kodu (computeBvalue, bCiFields; kopya yok).
// Gerçek büyüklük sürekli G–R (m ≥ m0 = 3,0, b ∈ {0,7; 1,0; 1,3}); her olay olasılık f ile 0,01'e, aksi hâlde 0,1'e en yakın değere
// yuvarlanarak "kaydedilir" (f = 0,56: ISC 1971–1997 b hesabına giren olayların iki ondalıklı oranı). Mc = 3,2.
// Yöntemler: (A) bugünkü: karma değerler, eşik m ≥ Mc, ΔM/2 = 0,05; aralık bCiFields (ızgara dışı → χ²)
//            (B) sürekli varsayım: aynı değerler, ΔM = 0 (Aki 1965 sürekli), χ² aralığı
//            (C) ortak 0,1 sınıfı: her değer 0,1'e en yakın değere yuvarlanır (ondalığı 5 ile biten 0,01 değerleri yukarı), sonra
//                eşik ve ΔM/2 = 0,05; aralık bCiFields (ızgarada → Tinti & Mulargia)
// Kullanım: node mc_karma.js [tekrar=4000] [tohum=20261029]
'use strict';
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); return src.slice(i, j); };
global.location = { search: '' };
(0, eval)(cut('function computeBvalue(', '// Aki (1965) MLE için %95') + cut('function bConfidence95(b, n)', '// Kayan pencere b-değeri') + '\nglobal.__x = { computeBvalue, bCiFields, bCiChi2 };');
const X = global.__x, REPS = +(process.argv[2] || 4000), SEED = +(process.argv[3] || 20261029); let s = SEED;
const rnd = () => (s = (s * 48271) % 2147483647) / 2147483647, M0 = 3.0, Mc = 3.2;
const r2 = (x, d) => Math.round(x / d + 1e-9) * d, fix = x => +x.toFixed(2);
const out = [];
for (const f of [0.0, 0.56, 1.0]) for (const b of [0.7, 1.0, 1.3]) for (const N0 of [100, 500, 3000]) {
  const beta = b * Math.LN10, acc = { A: [0, 0, 0], B: [0, 0, 0], C: [0, 0, 0] }; let nA = 0;
  for (let r = 0; r < REPS; r++) {
    // N0: M ≥ Mc olay sayısının yaklaşık değeri; m0'dan üretilir ki eşik çevresi doğru temsil edilsin
    const n = Math.round(N0 * Math.pow(10, b * (Mc - M0))), rec = [];
    for (let k = 0; k < n; k++) { const m = M0 - Math.log(1 - rnd()) / beta; rec.push(fix(rnd() < f ? r2(m, 0.01) : r2(m, 0.1))); }
    const sub = rec.filter(m => m >= Mc - 1e-9), bA = X.computeBvalue(rec, Mc, 0.1); nA += sub.length;
    const ciA = X.bCiFields(bA, sub.length, sub.map(m => m - Mc), 0.1);
    const bB = X.computeBvalue(rec, Mc, 0), ciB = X.bCiChi2(bB, sub.length);
    const rc = rec.map(m => fix(r2(m, 0.1))), subC = rc.filter(m => m >= Mc - 1e-9), bC = X.computeBvalue(rc, Mc, 0.1), ciC = X.bCiFields(bC, subC.length, subC.map(m => m - Mc), 0.1);
    for (const [k, bh, ci] of [['A', bA, ciA], ['B', bB, ciB], ['C', bC, ciC]]) { acc[k][0] += bh / b; acc[k][1] += ci.lo <= b && b <= ci.hi; acc[k][2] += b > ci.hi; }
  }
  const o = { f2: f, b, N: Math.round(nA / REPS) };
  for (const k of ['A', 'B', 'C']) { o[k + '_bhat_b'] = acc[k][0] / REPS; o[k + '_kapsama'] = acc[k][1] / REPS; o[k + '_ustte'] = acc[k][2] / REPS; }
  out.push(o);
}
fs.writeFileSync(path.join(__dirname, 'out', 'mc_karma.json'), JSON.stringify({ meta: { tekrar: REPS, tohum: SEED, m0: M0, Mc, kaynak: 'index.html' }, sonuc: out }, null, 1));
for (const o of out) console.log(`f2=${o.f2} b=${o.b} N≈${String(o.N).padStart(4)} | A bugünkü b̂/b ${o.A_bhat_b.toFixed(3)} kaps ${o.A_kapsama.toFixed(3)} | B sürekli ${o.B_bhat_b.toFixed(3)} ${o.B_kapsama.toFixed(3)} | C 0,1 sınıfı ${o.C_bhat_b.toFixed(3)} ${o.C_kapsama.toFixed(3)}`);
