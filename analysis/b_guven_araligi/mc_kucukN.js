// Küçük örneklem (N < 50) test grubu — üretim kodu (index.html computeBvalue, bCiFields), kopya yok.
// A) Tek örneklem: kapsama (T–M, üretim kuralı) ve eski normal yaklaşım; iki yönlü kaçırma; göreli genişlik; b̂ yanlılığı.
// B) İki bağımsız örneklem (ör. iki dönem ya da iki bölge, her biri N olay): b farkının ayırt edilme olasılığı
//    (i) iki %95 T–M aralığının örtüşmemesi, (ii) Utsu (1992) testi P < 0,05 [dA = −2N ln N + 2N₁ ln(N₁ + N₂b₁/b₂)
//    + 2N₂ ln(N₁b₂/b₁ + N₂) − 2, P ≈ exp(−dA/2 − 2)]; b₁ = b₂'de yanlış alarm oranı.
// İdeal G–R (tam tamlık, hatasız büyüklük, bağımsız olaylar); büyüklükler ΔM ızgarasında. Kullanım: node mc_kucukN.js [tekrar] [tohum]
'use strict';
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
global.location = { search: '' };
(0, eval)(cut('function computeBvalue(', '// Aki (1965) MLE için %95') + cut('function bConfidence95(b, n)', '// Kayan pencere b-değeri')
  + '\nglobal.__x = { computeBvalue, bCiFields, bConfidence95 };');
const X = global.__x, REPS = +(process.argv[2] || 20000), SEED = +(process.argv[3] || 20261026); let s = SEED;
const rnd = () => (s = (s * 48271) % 2147483647) / 2147483647, Mc = 3.0;
const sample = (b, N, dm) => { const beta = b * Math.LN10; return Array.from({ length: N }, () => +(Mc + Math.floor(-Math.log(1 - rnd()) / beta / dm) * dm).toFixed(3)); };
const est = (m, dm) => { const bh = X.computeBvalue(m, Mc, dm); return bh === null ? null : { b: bh, ...X.bCiFields(bh, m.length, m.map(v => v - Mc), dm) }; };
const utsuP = (b1, n1, b2, n2) => { const n = n1 + n2, dA = -2 * n * Math.log(n) + 2 * n1 * Math.log(n1 + n2 * b1 / b2) + 2 * n2 * Math.log(n1 * b2 / b1 + n2) - 2; return Math.exp(-dA / 2 - 2); };
const med = a => { const q = a.slice().sort((x, y) => x - y); return q[Math.floor(q.length / 2)]; };
const NS = [10, 15, 20, 25, 30, 40, 49], A = [], B = [], t0 = Date.now();
for (const dm of [0.1, 0.2]) for (const b of [0.7, 1.0, 1.3, 1.6]) for (const N of NS) {
  let cov = 0, lo = 0, hi = 0, covN = 0, hiN = 0, inf = 0; const w = [], bb = [];
  for (let r = 0; r < REPS; r++) { const e = est(sample(b, N, dm), dm); bb.push(e.b);
    cov += e.lo <= b && b <= e.hi; lo += b < e.lo; hi += b > e.hi; inf += e.hi === Infinity; if (Number.isFinite(e.hi)) w.push((e.hi - e.lo) / b);
    const en = X.bConfidence95(e.b, N); covN += e.b - en <= b && b <= e.b + en; hiN += b > e.b + en; }
  A.push({ dM: dm, b, N, kapsama: cov / REPS, altta: lo / REPS, ustte: hi / REPS, ust_sonsuz: inf / REPS, gorece_genislik_ortanca: med(w),
    bhat_ort_oran: bb.reduce((a, v) => a + v, 0) / REPS / b, normal_kapsama: covN / REPS, normal_ustte: hiN / REPS });
}
const R2 = Math.round(REPS / 4);
for (const N of NS) for (const b2 of [1.0, 0.8, 0.7, 0.5, 1.3]) {
  let ovl = 0, ut = 0;
  for (let r = 0; r < R2; r++) { const e1 = est(sample(1.0, N, 0.1), 0.1), e2 = est(sample(b2, N, 0.1), 0.1);
    ovl += e1.hi < e2.lo || e2.hi < e1.lo; ut += utsuP(e1.b, N, e2.b, N) < 0.05; }
  B.push({ N, b1: 1.0, b2, araliklar_ortusmez: ovl / R2, utsu_P_lt_005: ut / R2 });
}
fs.writeFileSync(path.join(__dirname, 'out', 'mc_kucukN.json'), JSON.stringify({ meta: { tekrar: REPS, tekrar_iki_ornek: R2, tohum: SEED, Mc, sure_s: (Date.now() - t0) / 1000, kaynak: 'index.html computeBvalue + bCiFields' }, tek: A, iki: B }, null, 1));
console.log('süre', (Date.now() - t0) / 1000, 's');
