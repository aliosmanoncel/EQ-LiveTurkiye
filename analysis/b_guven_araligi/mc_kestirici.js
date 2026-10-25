// Nokta kestiricisi karşılaştırması: Aki–Utsu (EQ-Live, computeBvalue) ve Tinti & Mulargia (1987) gruplanmış en çok olabilirlik.
// Gruplanmış büyüklükte k = (m − Mc)/ΔM sınıf indeksleri geometrik dağılır, P(k) = (1 − p)p^k, p = e^{−βΔM}. z̄ = ortalama k.
//   Aki–Utsu:  β̂_U = 1 / (ΔM (z̄ + 1/2))               (Utsu 1966 ΔM/2 düzeltmesi)
//   T&M MLE:   p̂ = z̄ / (1 + z̄)  →  β̂_TM = ln(1 + 1/z̄) / ΔM   (z̄ = 0'da tanımsız: bütün olaylar en küçük sınıfta)
// b = β·log10(e). İdeal G–R, büyüklükler ızgarada. Ölçütler: ortalama b̂/b (yanlılık), göreli RMSE, iki kestirici arasındaki
// ortalama mutlak fark, tanımsız (z̄ = 0) oranı. Gerçek kataloglarda da iki kestirici karşılaştırılır. Kullanım: node mc_kestirici.js
'use strict';
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); return src.slice(i, j); };
global.location = { search: '' };
(0, eval)(cut('function computeBvalue(', '// Aki (1965) MLE için %95') + '\nglobal.__x = { computeBvalue };');
const X = global.__x, L10 = Math.LOG10E; let s = 20261030;
const rnd = () => (s = (s * 48271) % 2147483647) / 2147483647;
const bTM = (zbar, dm) => zbar > 0 ? Math.log(1 + 1 / zbar) / dm * L10 : Infinity;
const out = [];
for (const dm of [0.1, 0.2]) for (const b of [0.7, 1.0, 1.5, 2.5]) for (const N of [10, 20, 50, 100, 500, 5000]) {
  const R = N >= 5000 ? 800 : 4000, beta = b * Math.LN10; let sU = 0, sT = 0, qU = 0, qT = 0, dAbs = 0, und = 0, nOk = 0;
  for (let r = 0; r < R; r++) {
    let sum = 0; const mags = new Array(N);
    for (let k = 0; k < N; k++) { const c = Math.floor(-Math.log(1 - rnd()) / beta / dm); sum += c; mags[k] = +(3 + c * dm).toFixed(3); }
    const z = sum / N, u = X.computeBvalue(mags, 3, dm), t = bTM(z, dm);
    if (!Number.isFinite(t)) { und++; continue; }
    nOk++; sU += u / b; sT += t / b; qU += (u / b - 1) ** 2; qT += (t / b - 1) ** 2; dAbs += Math.abs(t - u) / b;
  }
  out.push({ dM: dm, b, N, betaDM: +(beta * dm).toFixed(3), aki_utsu_bhat_b: sU / nOk, tm_bhat_b: sT / nOk, aki_utsu_rmse: Math.sqrt(qU / nOk), tm_rmse: Math.sqrt(qT / nOk), ort_fark_gorece: dAbs / nOk, tanimsiz: und / R });
}
// gerçek kataloglar (dönüşüm yok; karma çözünürlükte ortak 0,1 sınıfı, RAPOR §16)
const real = []; const r01 = x => +(Math.round(x * 10 + 1e-9) / 10).toFixed(1);
const hist = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'data', 'eq_historical.json'), 'utf8')).events;
const sets = [['ISC 1900–1970', hist.filter(e => e.src === 'ISC' && +e.time.slice(0, 4) <= 1970), 4.7], ['ISC 1971–1997', hist.filter(e => e.src === 'ISC' && +e.time.slice(0, 4) >= 1971 && +e.time.slice(0, 4) <= 1997), 3.7],
  ['EMSC 1998–', hist.filter(e => e.src === 'EMSC'), null]];
for (const [nm, ev, Mc0] of sets) {
  const m = ev.map(e => r01(e.mw || e.mag)).filter(v => v > 0), Mc = Mc0 ?? (() => { const c = {}; m.forEach(v => c[v.toFixed(1)] = (c[v.toFixed(1)] || 0) + 1); return +(+Object.entries(c).sort((a, b) => b[1] - a[1])[0][0] + 0.2).toFixed(1); })();
  const sub = m.filter(v => v >= Mc - 1e-9), z = sub.reduce((a, v) => a + Math.round((v - Mc) / 0.1), 0) / sub.length;
  real.push({ katalog: nm, Mc, N: sub.length, aki_utsu: +X.computeBvalue(m, Mc, 0.1).toFixed(4), tm: +bTM(z, 0.1).toFixed(4) });
}
fs.writeFileSync(path.join(__dirname, 'out', 'mc_kestirici.json'), JSON.stringify({ meta: { tohum: 20261030, kaynak: 'index.html computeBvalue' }, sonuc: out, gercek: real }, null, 1));
for (const o of out) if (o.dM === 0.1 || o.b <= 1.5) console.log(`ΔM=${o.dM} b=${o.b} βΔM=${o.betaDM.toFixed(2)} N=${String(o.N).padStart(4)} | Aki–Utsu b̂/b ${o.aki_utsu_bhat_b.toFixed(3)} RMSE ${o.aki_utsu_rmse.toFixed(3)} | T&M ${o.tm_bhat_b.toFixed(3)} RMSE ${o.tm_rmse.toFixed(3)} | |fark|/b ${(100 * o.ort_fark_gorece).toFixed(2)}% | tanımsız ${(100 * o.tanimsiz).toFixed(1)}%`);
console.log(JSON.stringify(real, null, 1));
