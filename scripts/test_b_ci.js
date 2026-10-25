// Birim testleri: b-değeri %95 güven aralığı yöntemleri (2026-10-25).
// Fonksiyonlar doğrudan index.html'den okunur (bConfidence95 … bCiMethodTxt bloğu, btClassOf); kopya tutulmaz.
// Gerekçe ve Monte Carlo doğrulaması: analysis/b_guven_araligi/RAPOR.md.
// Denetlenen iddialar:
//   1. χ² uçları (Utsu 1966; Shi & Bolt 1982) ve Tinti & Mulargia (1987) Eş. 19–21 uçları, scipy ile üretilmiş
//      referans değerlerle (analysis/b_guven_araligi/bci.py) 1e-9 göreli hata içinde aynıdır; r = 0 → üst uç sonsuz.
//   2. Yöntem seçimi (2026-10-25, RAPOR §12): bütün büyüklükler ΔM ızgarasında → T–M (b̂'ye bağlı eşik yok); ızgara dışı
//      ya da fark dizisi yok → χ². N'ye bağlı geçiş yoktur (aynı veri N = 49 ve N = 50'de aynı yöntemle hesaplanır).
//   3. 'normal' kipte (?bci=normal) alanlar eski ±1,96·b/√N hesabıyla birebir aynıdır; metin biçimi " ± 0.12" kalır.
//   4. btClassOf asimetrik uçları kullanır; bCiDiffSig 'normal'de eski formülü, aksi hâlde karşıya bakan kolları kullanır.
//   5. Tohumlu küçük kapsama denetimi: ΔM = 0,1'de χ² nominal kapsar; ΔM = 0,5, b = 1,5'te χ² düşer, T–M nominal kalır.
// Kullanım (depo kökünde): node scripts/test_b_ci.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const block = () => { const i = src.indexOf('\nfunction bConfidence95('), j = src.indexOf('// Kayan pencere b-değeri', i);
  if (i < 0 || j < 0) throw new Error('bulunamadı: aralık bloğu'); return src.slice(i + 1, j); };
const cls = src.match(/^const BT_CLASS = [^\n]*$/m);
const mk = search => { const ctx = { URLSearchParams }; vm.createContext(ctx);
  vm.runInContext(`var location = { search: ${JSON.stringify(search)} };\n` + (cls ? cls[0].replace('const ', 'var ') + '\n' : 'var BT_CLASS = { lo: 0.7, hi: 1.4 };\n')
    + fn('computeBvalue') + '\n' + fn('btClassOf') + '\n' + block()
    + '\nglobalThis.__x = { computeBvalue, bConfidence95, bCiChi2, bCiTintiMulargia, bCiFields, bCiFromSym, bCiTxt, bCiDiffSig, bUtsuP, btClassOf, method: () => B_CI_METHOD };', ctx);
  return ctx.__x; };
const X = mk(''), N0 = mk('?bci=normal');
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };
const rel = (a, b) => Math.abs(a - b) / Math.abs(b);

// 1. Referans değerler (scipy 1.18.1, analysis/b_guven_araligi/bci.py ile 2026-10-25'te üretildi)
const REF = { chi2: [[10, 1.0, 0.4795388696132433, 1.7084803451419166], [25, 0.8, 0.5177178191305385, 1.1427231230001027], [49, 1.2, 0.8877666060937748, 1.558555988133729],
  [100, 1.0, 0.8136399125092314, 1.2052894775315546], [1000, 0.9, 0.8450757165669257, 0.956629036102399]],
  tm: [[10, 30, 0.1, 0.5894337307816516, 2.1699847556568943], [20, 0, 0.1, 7.735716015605731, null], [49, 20, 0.5, 0.7711017741778478, 1.443467737667454],
  [100, 110, 0.1, 2.269613066219847, 3.4077334924461335], [4, 1, 0.5, 0.28966709952763353, 4.40001517532392]] };
ok(X.method() === 'chi2' && N0.method() === 'normal', `kip: varsayılan ${X.method()}, ?bci=normal → ${N0.method()}`);
REF.chi2.forEach(([n, b, lo, hi]) => { const c = X.bCiChi2(b, n); ok(rel(c.lo, lo) < 1e-9 && rel(c.hi, hi) < 1e-9, `χ² N = ${n}, b = ${b}: ${c.lo.toFixed(6)}–${c.hi.toFixed(6)} (ref ${lo.toFixed(6)}–${hi.toFixed(6)})`); });
REF.tm.forEach(([n, r, dm, lo, hi]) => { const t = X.bCiTintiMulargia(n, r, dm);
  ok(rel(t.lo, lo) < 1e-9 && (hi === null ? t.hi === Infinity : rel(t.hi, hi) < 1e-9), `T–M N = ${n}, r = ${r}, ΔM = ${dm}: ${t.lo.toFixed(6)}–${t.hi} (ref ${lo.toFixed(6)}–${hi === null ? '∞' : hi.toFixed(6)})`); });
{ const c = X.bCiChi2(1, 10); ok(c.hi - 1 > 1 - c.lo, `χ² asimetrik: üst kol ${(c.hi - 1).toFixed(3)} > alt kol ${(1 - c.lo).toFixed(3)} (N = 10)`); }

// 2. Yöntem seçimi
const grid = (b, n, dm, seed) => { let s = seed; const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
  return Array.from({ length: n }, () => Math.floor(-Math.log(1 - r()) / (b * Math.LN10) / dm) * dm); };   // (m − Mc), ızgarada
{ const ex = grid(1.0, 60, 0.1, 7), b = Math.LOG10E / (ex.reduce((a, v) => a + v, 0) / ex.length + 0.05), f = X.bCiFields(b, ex.length, ex, 0.1);
  ok(f.ciM === 'tm', `ΔM = 0,1, b̂ = ${b.toFixed(2)} (ızgarada, düşük β̂ΔM) → ${f.ciM}`);
  const o = X.bCiFields(b, ex.length, ex.map(v => v + 0.0371), 0.1); ok(o.ciM === 'chi2' && Math.abs(o.lo - X.bCiChi2(b, ex.length).lo) < 1e-15, `ızgara dışı → ${o.ciM}`); }
{ const ex = grid(2.8, 60, 0.1, 11), b = Math.LOG10E / (ex.reduce((a, v) => a + v, 0) / ex.length + 0.05), f = X.bCiFields(b, ex.length, ex, 0.1);
  ok(b * Math.LN10 * 0.1 > 0.5 && f.ciM === 'tm' && Number.isFinite(f.lo), `ΔM = 0,1, b̂ = ${b.toFixed(2)} (β̂ΔM = ${(b * Math.LN10 * 0.1).toFixed(2)}) → ${f.ciM}`);
  const off = ex.map((v, i) => v + (i === 3 ? 0.013 : 0)), g = X.bCiFields(b, ex.length, off, 0.1); ok(g.ciM === 'chi2', `ızgara dışı büyüklük → ${g.ciM} (T–M r tam sayı ister)`);
  ok(X.bCiFields(b, ex.length, null, 0.1).ciM === 'chi2' && X.bCiFields(b, ex.length + 1, ex, 0.1).ciM === 'chi2', 'fark dizisi yok ya da N ile uyuşmuyor → χ²'); }
{ const ex = grid(1.5, 50, 0.5, 5), b = Math.LOG10E / (ex.reduce((a, v) => a + v, 0) / 50 + 0.25), f = X.bCiFields(b, 50, ex, 0.5);
  ok(f.ciM === 'tm', `ΔM = 0,5, b̂ = ${b.toFixed(2)} → ${f.ciM}`); }
{ const ex = grid(1.0, 50, 0.1, 3), a = ex.slice(0, 49), A = X.bCiFields(1.0, 49, a, 0.1), B = X.bCiFields(1.0, 50, ex, 0.1);
  ok(A.ciM === B.ciM && A.ciM === 'tm', `N = 49 ve N = 50 aynı yöntem (${A.ciM}/${B.ciM}); 50'de geçiş yok`); }
{ const t = X.bCiFields(2.5, 20, Array(20).fill(0), 0.1); ok(t.ciM === 'tm' && t.hi === Infinity && t.err === Infinity && X.bCiTxt({ b: 2.5, ...t }).endsWith('–∞]'), `r = 0 → üst uç sınırsız, metin "${X.bCiTxt({ b: 2.5, ...t })}"`); }
ok(X.bCiFields(null, 30).lo === null && X.bCiFields(1, 0).err === null, 'b yok ya da N = 0 → aralık yok');

// 3. 'normal' kip: eski hesapla birebir
{ let same = true; for (const [b, n] of [[1, 10], [0.83, 37], [1.27, 100], [0.61, 4321]]) { const f = N0.bCiFields(b, n, null, 0.1), e = 1.96 * b / Math.sqrt(n);
    same = same && f.err === e && f.lo === b - e && f.hi === b + e && f.ciM === 'normal' && N0.bCiTxt({ b, ...f }) === ' ± ' + e.toFixed(2); }
  ok(same, "normal kip: err, lo, hi ve metin eski ±1,96·b/√N ile birebir"); }
{ const ex = grid(2.8, 60, 0.1, 11); ok(N0.bCiFields(2.6, 60, ex, 0.1).ciM === 'normal', "normal kipte T–M koşulu sağlansa da eski hesap"); }
{ const f = X.bCiFromSym(1.1, 0.2); ok(f.ciM === 'fisher' && f.lo === 1.1 - 0.2 && X.bCiTxt({ b: 1.1, ...f }) === ' ± 0.20', 'çift kesik (Fisher) aralık simetrik kalır, metin ±'); }

// 4. Sınıflama ve anlamlılık
ok(X.btClassOf(1.0, 0.2) === N0.btClassOf(1.0, 0.2) && X.btClassOf(1.0, 0.2) === 'mid', 'btClassOf(b, err) eski çağrıyla aynı');
ok(X.btClassOf(1.0, 0.25, 0.75, 1.45) === null && X.btClassOf(1.0, 0.25, 0.75, 1.39) === 'mid', 'btClassOf asimetrik uçları kullanır (hi = 1,45 → belirsiz; 1,39 → tipik)');
ok(X.btClassOf(1.6, Infinity, 1.45, Infinity) === 'high' && X.btClassOf(1.0, Infinity, 0.6, Infinity) === null, 'sınırsız üst uç: alt uç > 1,4 ise yüksek, aksi hâlde belirsiz');
{ const a = { b: 1.3, err: 0.2, ciM: 'normal' }, c = { b: 0.9, err: 0.15, ciM: 'normal' }; ok(X.bCiDiffSig(a, c) === (Math.abs(a.b - c.b) > Math.sqrt(a.err ** 2 + c.err ** 2)), 'bCiDiffSig normal: eski formül'); }
{ const u = { b: 1.3, lo: 1.1, hi: 1.6, err: 0.25, ciM: 'chi2' }, d = { b: 0.9, lo: 0.75, hi: 1.12, err: 0.185, ciM: 'chi2' };
  ok(X.bCiDiffSig(u, d) === (0.4 > Math.sqrt(0.2 ** 2 + 0.22 ** 2)), 'bCiDiffSig asimetrik: büyüğün alt kolu ve küçüğün üst kolu'); }

// 5. Tohumlu kapsama (küçük; ayrıntılı çalışma RAPOR.md §4–9). ±0,02 tolerans: 3000 tekrarda MC standart hatası ≈ 0,004.
const cover = (b, n, dm, reps, seed) => { let s = seed; const r = () => (s = (s * 48271) % 2147483647) / 2147483647; let c = 0, t = 0;
  for (let k = 0; k < reps; k++) { const ex = Array.from({ length: n }, () => Math.floor(-Math.log(1 - r()) / (b * Math.LN10) / dm) * dm);
    const bh = Math.LOG10E / (ex.reduce((a, v) => a + v, 0) / n + dm / 2), q = X.bCiChi2(bh, n), rr = Math.round(ex.reduce((a, v) => a + v, 0) / dm), tq = X.bCiTintiMulargia(n, rr, dm);
    c += q.lo <= b && b <= q.hi; t += tq.lo <= b && b <= tq.hi; } return [c / reps, t / reps]; };
{ const [c, t] = cover(1.0, 10, 0.1, 3000, 20261025); ok(Math.abs(c - 0.95) < 0.02 && Math.abs(t - 0.95) < 0.02, `ΔM = 0,1, b = 1, N = 10: χ² ${c.toFixed(3)}, T–M ${t.toFixed(3)}`); }
{ const [c, t] = cover(1.5, 49, 0.5, 2000, 777); ok(c < 0.85 && t >= 0.93, `ΔM = 0,5, b = 1,5, N = 49: χ² ${c.toFixed(3)} (düşer), T–M ${t.toFixed(3)} (nominal)`); }

{ let s2 = 99, cc = 0, ct = 0; const R = 300, N = 10000, b = 1.5, beta = b * Math.LN10, rr = () => (s2 = (s2 * 48271) % 2147483647) / 2147483647;
  for (let k = 0; k < R; k++) { let sum = 0; for (let i = 0; i < N; i++) sum += Math.floor(-Math.log(1 - rr()) / beta / 0.1);
    const bh = Math.LOG10E / (0.1 * (sum / N + 0.5)), q = X.bCiChi2(bh, N), t = X.bCiTintiMulargia(N, sum, 0.1); cc += q.lo <= b && b <= q.hi; ct += t.lo <= b && b <= t.hi; }
  ok(cc / R < 0.9 && ct / R > 0.92, `ΔM = 0,1, b = 1,5, N = 10 000 (${R} tekrar): χ² ${(cc / R).toFixed(3)} (büyük N'de düşer), T–M ${(ct / R).toFixed(3)}`); }

// 6. Utsu (1992) fark testi: özdeş b ve N'de dA = −2 → P = e⁻¹; simetri; küçük N kalibrasyonu (yanlış alarm ≈ %5)
ok(Math.abs(X.bUtsuP(1, 30, 1, 30) - Math.exp(-1)) < 1e-12 && Math.abs(X.bUtsuP(0.8, 25, 1.2, 40) - X.bUtsuP(1.2, 40, 0.8, 25)) < 1e-12, 'Utsu P: özdeşte e⁻¹, örneklemlerin sırasına göre simetrik');
ok(X.bUtsuP(1, 30, 1.6, 30) < X.bUtsuP(1, 30, 1.3, 30) && X.bUtsuP(1, 0, 1, 30) === null, 'Utsu P: fark büyüdükçe küçülür; N = 0 → yok');
{ let s3 = 31, fa = 0; const R = 3000, N = 30, beta = Math.LN10, rr = () => (s3 = (s3 * 48271) % 2147483647) / 2147483647;
  const bh = () => { let sum = 0; for (let i = 0; i < N; i++) sum += Math.floor(-Math.log(1 - rr()) / beta / 0.1); return Math.LOG10E / (0.1 * (sum / N + 0.5)); };
  for (let k = 0; k < R; k++) fa += X.bUtsuP(bh(), N, bh(), N) < 0.05;
  ok(Math.abs(fa / R - 0.05) < 0.015, `Utsu P < 0,05 yanlış alarm (N = 30, b₁ = b₂ = 1, ${R} çift): ${(fa / R).toFixed(3)}`); }

console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
