// Birleşik seçim kuralının Monte Carlo kapsama testi (üretim kodu: index.html bCiFields, kopya yok).
// Kural veriye bağlıdır (β̂·ΔM > 0,5 ve ızgarada → T–M, aksi hâlde χ²); bu test seçimin kendisinin kapsamayı bozup bozmadığını ölçer.
// İdeal G–R örneklemleri: (m − Mc) = ΔM·⌊Üstel(β)/ΔM⌋ (sınıf merkezleri ızgarada). Kullanım: node mc_secim.js [tekrar=4000] [tohum=20261025]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const i = src.indexOf('\nfunction bConfidence95('), j = src.indexOf('// Kayan pencere b-değeri', i);
const ctx = { URLSearchParams, location: { search: '' } }; vm.createContext(ctx);
vm.runInContext(src.slice(i + 1, j) + '\nglobalThis.__x = { bCiFields, bCiChi2, bCiTintiMulargia };', ctx);
const X = ctx.__x, REPS = +(process.argv[2] || 4000); let s = +(process.argv[3] || 20261025);
const rnd = () => (s = (s * 48271) % 2147483647) / 2147483647;
const NS = [10, 20, 49, 100, 500];
const CASES = [[0.1, [0.7, 1.0, 1.5, 2.0, 2.1, 2.2, 2.3, 2.5, 3.0]], [0.2, [0.7, 1.0, 1.1, 1.2, 1.5]], [0.3, [0.7, 1.0]], [0.5, [0.5, 0.7, 1.0, 1.5]]];
const wil = (k, n) => { const p = k / n, z = 1.96, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [c - h, c + h]; };
const out = [], t0 = Date.now();
for (const [dm, bs] of CASES) for (const b of bs) for (const N of NS) {
  const beta = b * Math.LN10; let cC = 0, cK = 0, cT = 0, nT = 0, lowK = 0, upK = 0, inf = 0, wK = 0;
  for (let r = 0; r < REPS; r++) {
    const ex = new Array(N); let sum = 0;
    for (let k = 0; k < N; k++) { const v = Math.floor(-Math.log(1 - rnd()) / beta / dm) * dm; ex[k] = v; sum += v; }
    const bh = Math.LOG10E / (sum / N + dm / 2), f = X.bCiFields(bh, N, ex, dm), q = X.bCiChi2(bh, N), t = X.bCiTintiMulargia(N, Math.round(sum / dm), dm);
    cK += f.lo <= b && b <= f.hi; lowK += b < f.lo; upK += b > f.hi; nT += f.ciM === 'tm'; inf += f.hi === Infinity;
    if (Number.isFinite(f.hi)) wK += (f.hi - f.lo) / b;
    cC += q.lo <= b && b <= q.hi; cT += t.lo <= b && b <= t.hi;
  }
  const [wl, wu] = wil(cK, REPS);
  out.push({ dM: dm, b, N, betaDM: +(beta * dm).toFixed(3), birlesik: cK / REPS, birlesik_mc95: [+wl.toFixed(4), +wu.toFixed(4)], altta: lowK / REPS, ustte: upK / REPS,
    tm_orani: nT / REPS, ust_sonsuz: inf / REPS, gorece_genislik: wK / Math.max(1, REPS - inf), yalniz_chi2: cC / REPS, yalniz_tm: cT / REPS });
}
fs.mkdirSync(path.join(__dirname, 'out'), { recursive: true });
fs.writeFileSync(path.join(__dirname, 'out', 'mc_secim.json'), JSON.stringify({ meta: { tekrar: REPS, tohum: +(process.argv[3] || 20261025), sure_s: (Date.now() - t0) / 1000, kaynak: 'index.html bCiFields' }, sonuc: out }, null, 1));
for (const r of out) console.log(`ΔM=${r.dM} b=${r.b} N=${String(r.N).padStart(4)} βΔM=${r.betaDM.toFixed(2)} | birleşik ${r.birlesik.toFixed(3)} (${(r.altta * 100).toFixed(1)}/${(r.ustte * 100).toFixed(1)}) TM %${(r.tm_orani * 100).toFixed(0)} ∞ %${(r.ust_sonsuz * 100).toFixed(1)} | χ² ${r.yalniz_chi2.toFixed(3)} TM ${r.yalniz_tm.toFixed(3)}`);
console.log('süre', (Date.now() - t0) / 1000, 's');
