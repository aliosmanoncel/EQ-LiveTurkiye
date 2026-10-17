// Birim testleri: ΔS/Δt ayrıştırması (2026-10-17).
// Fonksiyonlar doğrudan index.html'den okunur (BEN_DEC_NB, benGexp, benDecompose, mulberry32); kopya tutulmaz.
// Bütün kataloglar YAPAY veridir, fiziksel yorum için kullanılmaz. Denetlenen iddialar (yazılım doğruluğu):
//   1. g(b): kesilmiş G–R altında E[10^(0,75M)] — sayısal integrasyonla aynı; b = 0,75 limitinde sürekli; b < 0,75'te sonlu.
//   2. Özdeşlik: her aralıkta toplam = sayı + b + artık (log10), kayan nokta hassasiyetinde.
//   3. Sayı terimi: olay hızı ikinci yarıda iki katına çıkınca terim ≈ log10(2) farkı verir; b sabitken b terimi ≈ 0.
//   4. b terimi: b ikinci yarıda düşünce terim log10[g(b2)/g(b_ref)] yönünde pozitif olur; n < NB aralıklarda b_ref kullanılır.
//   5. Artığın ortalaması, büyük örneklemde 0'a yakındır (beklenen değer doğru kurulmuş).
// Kullanım (depo kökünde): node scripts/test_ben_decomp.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const nb = src.match(/^const BEN_DEC_NB = [^\n]*$/m); if (!nb) throw new Error('BEN_DEC_NB');
const ctx = {}; vm.createContext(ctx);
vm.runInContext(nb[0].replace('const ', 'var ') + '\n' + ['benGexp', 'benDecompose', 'mulberry32'].map(fn).join('\n') + '\nglobalThis.__x = { benGexp, benDecompose, mulberry32, BEN_DEC_NB };', ctx);
const X = ctx.__x, YR = 31557600000;
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };

// ── 1. g(b) ─────────────────────────────────────────────────────────
const num = (b, mc, mx) => { const B = b * Math.LN10, n = 200000, h = (mx - mc) / n; let s = 0, z = 0;
  for (let i = 0; i < n; i++) { const M = mc + (i + 0.5) * h, f = Math.exp(-B * (M - mc)); s += f * Math.pow(10, 0.75 * M); z += f; } return s / z; };
for (const [b, mc, mx] of [[1, 2, 7], [0.9, 1.95, 6.55], [0.75, 2, 7], [0.6, 2, 7], [1.3, 3, 8]]) {
  const a = X.benGexp(b, mc, mx), q = num(b, mc, mx); ok(Math.abs(a / q - 1) < 1e-6, `g(${b},${mc},${mx}) analitik ${a} vs sayısal ${q}`); }
ok(Math.abs(X.benGexp(0.75 + 1e-7, 2, 7) / X.benGexp(0.75, 2, 7) - 1) < 1e-5, 'b = 0,75 limitinde süreklilik');
ok(X.benGexp(0.75, 2, 2) === null && X.benGexp(0, 2, 7) === null, 'geçersiz girdide null');

// ── Sentetik katalog üreteci (ΔM = 0,1, eşik 2,0) ───────────────────
const rnd = X.mulberry32(20261017), t0 = Date.UTC(2000, 0, 1), t1 = Date.UTC(2020, 0, 1), mid = (t0 + t1) / 2;
const gr = (b) => Math.round((1.95 - Math.log10(1 - rnd()) / b) * 10) / 10;
const make = (n1, b1, n2, b2) => { const ev = [];
  for (let i = 0; i < n1; i++) ev.push({ t: t0 + rnd() * (mid - t0), m: gr(b1) });
  for (let i = 0; i < n2; i++) ev.push({ t: mid + rnd() * (t1 - mid), m: gr(b2) });
  return ev.filter(e => e.m >= 2).sort((a, b) => a.t - b.t); };
const halves = (D, key) => { const A = D.bins.filter(b => b.n && b.t1 <= mid), B = D.bins.filter(b => b.n && b.t0 >= mid), av = a => a.reduce((s, b) => s + b[key], 0) / a.length; return [av(A), av(B)]; };

// ── 2–3. Özdeşlik ve sayı terimi ────────────────────────────────────
{ const D = X.benDecompose(make(4000, 1, 8000, 1), t0, t1, YR, 2);
  ok(D && D.bins.length === 20, `20 yıllık aralık: ${D && D.bins.length}`);
  ok(D.bins.filter(b => b.n).every(b => Math.abs(b.tot - (b.cnt + b.bt + b.res)) < 1e-12), 'toplam = sayı + b + artık');
  const [c1, c2] = halves(D, 'cnt'); ok(Math.abs((c2 - c1) - Math.log10(2)) < 0.03, `sayı terimi farkı ${(c2 - c1).toFixed(3)} ≈ log10(2) = 0,301`);
  const [b1, b2] = halves(D, 'bt'); ok(Math.abs(b1) < 0.08 && Math.abs(b2) < 0.08, `b sabit → b terimi ≈ 0: ${b1.toFixed(3)}, ${b2.toFixed(3)}`);
  ok(D.bins.filter(b => b.n).every(b => b.bOwn), 'her aralıkta n ≥ NB → kendi b'); }

// ── 4. b terimi ─────────────────────────────────────────────────────
{ const D = X.benDecompose(make(6000, 1.1, 6000, 0.8), t0, t1, YR, 2);
  const [b1, b2] = halves(D, 'bt'), [c1, c2] = halves(D, 'cnt');
  ok(b2 > b1 + 0.15, `b düşünce b terimi artar: ${b1.toFixed(3)} → ${b2.toFixed(3)}`);
  ok(Math.abs(c2 - c1) < 0.05, `olay hızı sabit → sayı terimi farkı ≈ 0: ${(c2 - c1).toFixed(3)}`);
  const exp = Math.log10(X.benGexp(0.8, D.mc, D.mx) / X.benGexp(1.1, D.mc, D.mx));
  ok(Math.abs((b2 - b1) - exp) < 0.12, `b terimi farkı ${(b2 - b1).toFixed(3)} ≈ log10[g(0,8)/g(1,1)] = ${exp.toFixed(3)}`);
  const S = X.benDecompose(make(250, 1, 250, 1), t0, t1, YR, 2);   // aralık başına ~25 olay < NB
  ok(S.bins.filter(b => b.n).every(b => !b.bOwn && b.bt === 0), 'n < NB aralıklarda b_ref kullanılır, b terimi 0');
  ok(X.benDecompose(make(20, 1, 20, 1), t0, t1, YR, 2) === null, `toplam N < ${X.BEN_DEC_NB} → null`); }

// ── 5. Artık ortalaması ─────────────────────────────────────────────
{ const r = []; for (let k = 0; k < 20; k++) { const D = X.benDecompose(make(10000, 1.2, 10000, 1.2), t0, t1, YR, 2); D.bins.forEach(b => b.n && r.push(Math.pow(10, b.res))); }
  const m = r.reduce((s, v) => s + v, 0) / r.length; ok(Math.abs(m - 1) < 0.05, `gözlenen/beklenen ortalaması ${m.toFixed(3)} ≈ 1`);
  console.log(`Artık kontrolü: 400 aralık, gözlenen/beklenen ortalaması = ${m.toFixed(3)}`); }

console.log(`${fail ? '!! FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`);
process.exit(fail ? 1 : 0);
