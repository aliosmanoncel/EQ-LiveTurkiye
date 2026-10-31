// Öz-denetim (2026-11-01): analiz.js'deki istatistik fonksiyonları bilinen değerlere ve kaba kuvvet hesaplara karşı.
// Kullanım (depo kökünde): node analysis/poisson_donem/oz_denetim.js
'use strict';
const A = require('./analiz.js');
let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
const near = (a, b, t) => Math.abs(a - b) <= t;
// χ² üst kuyruk: tablolar (χ²₀,₉₅(1) = 3,8415; χ²₀,₉₅(13) = 22,362; χ²₀,₉₉(6) = 16,812)
ok(near(A.chi2Sf(3.8415, 1), 0.05, 1e-4) && near(A.chi2Sf(22.362, 13), 0.05, 1e-4) && near(A.chi2Sf(16.812, 6), 0.01, 1e-4), 'χ² üst kuyruk tablo değerleriyle aynı (sd 1, 13, 6)');
// Poisson CDF: P(X ≤ 3 | 2) = e⁻²(1 + 2 + 2 + 4/3) = 0,857123
ok(near(A.poisCdf(3, 2), 0.857123, 1e-6), 'Poisson CDF P(X ≤ 3 | μ = 2) = 0,857123');
// Kesin binom iki yönlü: kaba kuvvetle (k = 7, n = 20, q = 0,5) ve (k = 30, n = 50, q = 0,3)
const brute = (k, n, q) => { const C = (n, k) => { let r = 1; for (let i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; }; const pm = j => C(n, j) * q ** j * (1 - q) ** (n - j); const p0 = pm(k); let s = 0; for (let j = 0; j <= n; j++) if (pm(j) <= p0 * (1 + 1e-9)) s += pm(j); return Math.min(1, s); };
ok(near(A.binom2(7, 20, 0.5), brute(7, 20, 0.5), 1e-10) && near(A.binom2(30, 50, 0.3), brute(30, 50, 0.3), 1e-10), `kesin binom iki yönlü p kaba kuvvetle aynı (${A.binom2(7, 20, 0.5).toFixed(6)}; ${A.binom2(30, 50, 0.3).toExponential(3)})`);
// Clopper–Pearson: k = 5, n = 20 → [0,0866, 0,4910] (tablo)
const cp = A.betaInvCP(5, 20, 0.05); ok(near(cp[0], 0.0866, 2e-4) && near(cp[1], 0.4910, 2e-4), `Clopper–Pearson k = 5, n = 20: [${cp[0].toFixed(4)}, ${cp[1].toFixed(4)}] (tablo 0,0866–0,4910)`);
// Poisson regresyonu: kusursuz üstel veri → eğim kesin bulunur
const t = [0, 1, 2, 3, 4, 5, 6], x = t.map(v => Math.round(100 * Math.exp(0.1 * v))), r = A.poisReg(t, x);
ok(near(r.b, 0.1, 0.005), `log-doğrusal Poisson regresyonu eğimi ${r.b.toFixed(4)} (gerçek 0,1; yuvarlama payı)`);
// Dağılım testi: sabit sayılar → var/ort 0; Poisson benzetimi → yaklaşık 1
const ev = []; for (let y = 2000; y < 2010; y++) for (let i = 0; i < 50; i++) ev.push({ t: Date.UTC(y, 0, 1) + i * 864e5 * 7, m: 4.5 });
const d0 = A.dagilim(ev, 2000, 2009, 4.0, 'm'); ok(d0.oran === 0 && d0.n === 10 && d0.ort === 50, 'dağılım: her yıl 50 olay → var/ort 0, n 10');
console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
