// Aşama 3 doğrulaması (2026-11-01): NegBin (Gamma–Poisson) örnekleyici ile eski olay-başına örnekleyicinin dağılım karşılaştırması.
// Kanıt: NEGBIN_esdegerlik.md. Bu betik kanıtın sayısal sınamasıdır; birebir eşitlik beklenmez (rastgele sayı akışı farklı).
// Eski örnekleyici: 1f28df9 commit'indeki grPoissonBootSimple (git'ten okunur; kopya tutulmaz). Yeni: depodaki grBootDraws.
// Denetimler:
//   (1) Eski kodun bu betikteki çekiliş döngüsü 1f28df9'daki grPoissonBootSimple ile birebir aynı sonucu veriyor (kaynak doğrulaması).
//   (2) Beş senaryoda (n, b, ΔM) eski ve yeni (n*, b*) örnekleri: b* için iki örneklem KS; a*, b*, λ*(≥6), P(≥7; 50 yıl) yüzdelikleri;
//       ortalama, varyans, cov(a*, b*), corr(a*, b*), corr(n*, b*). Gürültü ölçeği: eski(tohum 1) − eski(tohum 2) farkı.
//   (3) n* verildiğinde S'nin dağılımı: eski (olay başına) ve yeni (Gamma–Poisson) kesin NegBin olasılıklarına karşı χ² uyum testi;
//       n* ∈ {12, 30, 200}, her biri 5 bağımsız tohum × 40 000 örnek; Fisher birleşik p (tek bir p'nin şansa bağlı düşüklüğüne karşı).
//   (4) Kapsama: 300 sentetik katalog (bilinen λ0, b); eski ve yeni %95 aralıklarının P(≥M; t)'yi kapsama oranı (B = 2000, ikisi de).
//   (5) Süre: B = 2000, n = 27 346 (Türkiye) — eski şema ve yeni şema.
// Kullanım (depo kökünde): node analysis/poisson_olasilik/negbin_karsilastirma.js   (≈ 9 dk; KISA=1 yalnız (1) ve (3), sonuç dosyası yazılmaz)
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), { execSync } = require('child_process');
const ROOT = path.join(__dirname, '..', '..'), ESKI = '1f28df9', KISA = process.env.KISA === '1';
const yeniSrc = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').replace(/\r\n/g, '\n'), eskiSrc = execSync(`git show ${ESKI}:index.html`, { cwd: ROOT, maxBuffer: 1 << 28 }).toString().replace(/\r\n/g, '\n');
const yukle = (src, adlar, sabit) => { const fn = n => { const i = src.indexOf('\nfunction ' + n + '('); if (i < 0) throw new Error('yok ' + n); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
  const line = re => src.match(re)[0].replace(/^const /, 'var '); const c = { B_GRID_MODE: 'sinif' }; vm.createContext(c);
  vm.runInContext([...sabit.map(line), ...adlar.map(fn)].join('\n'), c); vm.runInContext(src.match(/^const LANCZOS_C = \[[\s\S]*?\];$/m)[0].replace(/^const /, 'var '), c); return c; };
const ORT = ['mulberry32', 'logGamma', 'poissonSample', 'bGridRound', 'computeBvalue', 'grPoissonP', 'grLambdaSimple', 'grPctl'];
const N = yukle(yeniSrc, [...ORT, 'gammaSample', 'grBootDraws', 'grPoissonBootSimple'], [/^const GR_POIS = [^\n]*$/m, /^const GR_QC = [^\n]*$/m]);
const O = yukle(eskiSrc, [...ORT, 'grPoissonBootSimple'], [/^const GR_POIS = [^\n]*$/m, /^const GR_QC = [^\n]*$/m]);
// Eski şemanın çekiliş döngüsü — 1f28df9 grPoissonBootSimple / cmpProbBoot ile aynı ifadeler; (1)'de doğrulanır
function eskiDraws(n, b, Mc, dm, B, seed) { const rnd = O.mulberry32(seed), beta = b * Math.LN10, D = []; let nFail = 0;
  for (let k = 0; k < B; k++) { const ns = O.poissonSample(n, rnd); if (ns < 10) { nFail++; continue; }
    const mg = new Array(ns); for (let i = 0; i < ns; i++) mg[i] = O.bGridRound(Mc - dm / 2 - Math.log(1 - rnd()) / beta, Mc, dm);
    const bs = O.computeBvalue(mg, Mc, dm); if (!(bs > 0)) { nFail++; continue; } D.push([ns, bs]); } return { B, nFail, seed, D }; }
const yeniDraws = (n, b, Mc, dm, B, seed) => N.grBootDraws(n, b, Mc, dm, B, seed);
const R = { eski_commit: ESKI, uretim: new Date().toISOString(), node: process.version, denetim: [] }; let pass = 0, fail = 0;
const ok = (c, m) => { c ? pass++ : fail++; R.denetim.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };
// ── istatistik yardımcıları
const pct = (a, q) => O.grPctl(a, q), ort = a => a.reduce((x, y) => x + y, 0) / a.length, vr = a => { const m = ort(a); return a.reduce((x, y) => x + (y - m) ** 2, 0) / (a.length - 1); };
const kov = (a, b) => { const ma = ort(a), mb = ort(b); let s = 0; for (let i = 0; i < a.length; i++) s += (a[i] - ma) * (b[i] - mb); return s / (a.length - 1); }, kor = (a, b) => kov(a, b) / Math.sqrt(vr(a) * vr(b));
function ks2(x, y) { const a = x.slice().sort((p, q) => p - q), b = y.slice().sort((p, q) => p - q); let i = 0, j = 0, D = 0;
  while (i < a.length && j < b.length) { const v = Math.min(a[i], b[j]); while (i < a.length && a[i] <= v) i++; while (j < b.length && b[j] <= v) j++; D = Math.max(D, Math.abs(i / a.length - j / b.length)); }
  const ne = a.length * b.length / (a.length + b.length), l = (Math.sqrt(ne) + 0.12 + 0.11 / Math.sqrt(ne)) * D; let p = 0; for (let k = 1; k <= 100; k++) p += 2 * (-1) ** (k - 1) * Math.exp(-2 * k * k * l * l);
  return { D, p: Math.max(0, Math.min(1, p)) }; }   // Numerical Recipes (Press vd. 2007, §14.3.3); kesikli veride tutucu
const ozet = (D, T, Mc) => { const ns = D.map(d => d[0]), bs = D.map(d => d[1]), as = D.map(([n, b]) => Math.log10(n / T) + b * Mc), l6 = D.map(([n, b]) => N.grLambdaSimple(n, T, b, Mc, 6)), p7 = D.map(([n, b]) => N.grPoissonP(N.grLambdaSimple(n, T, b, Mc, 7), 50));
  return { ns, bs, as, l6, p7 }; };
const Q = [0.025, 0.16, 0.5, 0.84, 0.975];
// (1) kaynak doğrulaması
{ const n = 300, T = 20, b = 1.0, Mc = 4.0, dm = 0.1, B = 400, seed = 77, e = O.grPoissonBootSimple(n, T, b, Mc, dm, 6, 50, { B, seed }), d = eskiDraws(n, b, Mc, dm, B, seed);
  const P = d.D.map(([ns, bs]) => O.grPoissonP(O.grLambdaSimple(ns, T, bs, Mc, 6), 50));
  ok(e.pLo === pct(P, 0.025) && e.pHi === pct(P, 0.975) && e.nFail === d.nFail, `(1) eski çekiliş döngüsü = ${ESKI} grPoissonBootSimple (B = ${B}, tohum ${seed}; %95 [${e.pLo.toFixed(6)}, ${e.pHi.toFixed(6)}] birebir)`); }
// (2) senaryolar
const SEN = [['küçük N', 50, 1.0, 4.0, 0.1, 20000], ['Marmara benzeri', 624, 1.0, 3.2, 0.1, 20000], ['Doğu Anadolu benzeri', 5007, 0.99, 3.2, 0.1, 10000], ['Türkiye benzeri', 27346, 1.14, 3.2, 0.1, 4000], ['ΔM = 0,2, b = 0,8', 200, 0.8, 4.0, 0.2, 20000]];
R.senaryo = [];
for (const [ad, n, b, Mc, dm, K] of (KISA ? [] : SEN)) { const T = 28.7;
  const e1 = ozet(eskiDraws(n, b, Mc, dm, K, 101).D, T, Mc), e2 = ozet(eskiDraws(n, b, Mc, dm, K, 202).D, T, Mc), y = ozet(yeniDraws(n, b, Mc, dm, K, 303).D, T, Mc);
  const ksY = ks2(e1.bs, y.bs), ksE = ks2(e1.bs, e2.bs), ksA = ks2(e1.as, y.as);
  const sat = {}; for (const k of ['bs', 'as', 'l6', 'p7']) sat[k] = Q.map(q => ({ q, eski: pct(e1[k], q), eski2: pct(e2[k], q), yeni: pct(y[k], q) }));
  const mom = { b_ort: [ort(e1.bs), ort(e2.bs), ort(y.bs)], b_var: [vr(e1.bs), vr(e2.bs), vr(y.bs)], cov_ab: [kov(e1.as, e1.bs), kov(e2.as, e2.bs), kov(y.as, y.bs)], cor_ab: [kor(e1.as, e1.bs), kor(e2.as, e2.bs), kor(y.as, y.bs)], cor_nb: [kor(e1.ns, e1.bs), kor(e2.ns, e2.bs), kor(y.ns, y.bs)] };
  // göreli fark: yeni − eski, eski2 − eski (gürültü ölçeği); yüzdelik farkı gürültünün 4 katını ve %1,5'i birlikte aşmamalı
  const relq = k => sat[k].map(z => ({ q: z.q, dY: (z.yeni - z.eski) / z.eski, dE: (z.eski2 - z.eski) / z.eski }));
  let qOk = true; for (const k of ['bs', 'as', 'l6', 'p7']) for (const z of relq(k)) if (Math.abs(z.dY) > Math.max(4 * Math.abs(z.dE), 0.015)) qOk = false;
  const sd = mom.b_var.map(Math.sqrt), mOk = Math.abs(mom.b_ort[2] - mom.b_ort[0]) < 4 * Math.sqrt(mom.b_var[0] / K * 2) && Math.abs(mom.b_var[2] / mom.b_var[0] - 1) < 4 * Math.sqrt(2 / (K - 1)) * Math.SQRT2
    && Math.abs(mom.cor_ab[2] - mom.cor_ab[0]) < 4 * Math.SQRT2 * (1 - mom.cor_ab[0] ** 2) / Math.sqrt(K) + 1e-3;
  R.senaryo.push({ ad, n, b, Mc, dm, T, K, ks_yeni_eski: ksY, ks_eski_eski: ksE, ks_a: ksA, yuzdelik: sat, moment: mom });
  console.log(`\n── ${ad}: n = ${n}, b = ${b}, Mc = ${Mc}, ΔM = ${dm}, örnek ${K} (her biri)`);
  console.log(`   b*: KS yeni–eski D = ${ksY.D.toFixed(4)}, p = ${ksY.p.toFixed(3)}  |  eski–eski D = ${ksE.D.toFixed(4)}, p = ${ksE.p.toFixed(3)}  |  a*: KS yeni–eski p = ${ksA.p.toFixed(3)}`);
  console.log(`   b* ort ${mom.b_ort.map(v => v.toFixed(5)).join(' / ')}  sd ${sd.map(v => v.toFixed(5)).join(' / ')}  (eski / eski2 / yeni)`);
  console.log(`   cov(a*,b*) ${mom.cov_ab.map(v => v.toExponential(3)).join(' / ')}  corr(a*,b*) ${mom.cor_ab.map(v => v.toFixed(4)).join(' / ')}  corr(n*,b*) ${mom.cor_nb.map(v => v.toFixed(4)).join(' / ')}`);
  for (const [k, lb] of [['bs', 'b*'], ['l6', 'λ*(≥6)'], ['p7', 'P*(≥7;50)']]) console.log(`   ${lb.padEnd(10)} ` + sat[k].map(z => `q${(100 * z.q).toFixed(1)}: ${z.eski.toPrecision(4)}→${z.yeni.toPrecision(4)} (${(100 * (z.yeni - z.eski) / z.eski).toFixed(2)}%; gürültü ${(100 * (z.eski2 - z.eski) / z.eski).toFixed(2)}%)`).join('  '));
  ok(ksY.p > 0.01 && ksA.p > 0.01, `(2) ${ad}: b* ve a* için KS yeni–eski p = ${ksY.p.toFixed(3)} / ${ksA.p.toFixed(3)} (> 0,01; aynı dağılım reddedilmiyor)`);
  ok(qOk && mOk, `(2) ${ad}: yüzdelikler (a*, b*, λ*, P*; 2,5–97,5) ve ortalama, varyans, corr(a*, b*) eski–eski gürültüsü düzeyinde`);
}
// (3) S | n* kesin NegBin'e karşı χ²
R.chi2 = []; for (const ns of [12, 30, 200]) { const b = 1.0, dm = 0.1, q = Math.pow(10, -b * dm), p = 1 - q, K = 40000, th = q / p, lg = N.logGamma;
  const pmf = s => Math.exp(lg(s + ns) - lg(s + 1) - lg(ns) + ns * Math.log(p) + s * Math.log(q));
  const beta = b * Math.LN10, inc = (m, k) => m.set(k, (m.get(k) || 0) + 1);
  const ornek = (eski, seed) => { const rr = eski ? O.mulberry32(seed) : N.mulberry32(seed), c = new Map();
    for (let k = 0; k < K; k++) { if (eski) { let S = 0; for (let i = 0; i < ns; i++) S += Math.round((O.bGridRound(4 - dm / 2 - Math.log(1 - rr()) / beta, 4, dm) - 4) / dm); inc(c, S); } else inc(c, N.poissonSample(N.gammaSample(ns, rr) * th, rr)); } return c; };
  const chi = c => { const mu = ns * q / p, sdv = Math.sqrt(ns * q) / p, lo = Math.max(0, Math.floor(mu - 4 * sdv)), hi = Math.ceil(mu + 4 * sdv), bins = []; let acc = 0, accE = 0, s0 = 0;
    // kuyruklar birleştirilir; her hücrede beklenen ≥ 20
    let cdfLo = 0; for (let s = 0; s < lo; s++) cdfLo += pmf(s); let oLo = 0; for (const [s, v] of c) if (s < lo) oLo += v; bins.push([oLo, K * cdfLo]);
    for (let s = lo; s <= hi; s++) { acc += c.get(s) || 0; accE += K * pmf(s); if (accE >= 20) { bins.push([acc, accE]); acc = 0; accE = 0; } }
    let eTot = bins.reduce((x, y) => x + y[1], 0) + accE, oTot = bins.reduce((x, y) => x + y[0], 0) + acc; bins.push([K - (oTot - acc), K - (eTot - accE)]);   // son hücre: birikmiş artık + üst kuyruk (gözlenen ve beklenen aynı küme)
    const B2 = bins.filter(x => x[1] > 0); const X2 = B2.reduce((x, [o, e]) => x + (o - e) ** 2 / e, 0), df = B2.length - 1; return { X2, df, p: 1 - N_chi2cdf(X2, df) }; };
  function N_chi2cdf(x, k) { // düzenli alt eksik gama P(k/2, x/2) — seri / sürekli kesir
    const a = k / 2, z = x / 2; if (z < a + 1) { let s = 1 / a, t = s; for (let n = 1; n < 500; n++) { t *= z / (a + n); s += t; } return s * Math.exp(-z + a * Math.log(z) - lg(a)); }
    let b0 = z + 1 - a, c = 1e300, d = 1 / b0, h = d; for (let i = 1; i < 500; i++) { const an = -i * (i - a); b0 += 2; d = an * d + b0; d = 1 / d; c = b0 + an / c; h *= d * c; } return 1 - Math.exp(-z + a * Math.log(z) - lg(a)) * h; }
  const pE = [1, 2, 3, 4, 5].map(k => chi(ornek(true, 100 * ns + k)).p), pN = [1, 2, 3, 4, 5].map(k => chi(ornek(false, 100 * ns + 50 + k)).p);
  const fisher = P => { const X = -2 * P.reduce((a, v) => a + Math.log(Math.max(v, 1e-300)), 0); return 1 - N_chi2cdf(X, 2 * P.length); }, fE = fisher(pE), fN = fisher(pN);
  R.chi2.push({ ns, b, dm, K, eski_p: pE, yeni_p: pN, fisher_eski: fE, fisher_yeni: fN });
  ok(fE > 0.01 && fN > 0.01, `(3) S | n* = ${ns} ~ NegBin(${ns}, 1 − 10^(−bΔM)), 5 × ${K}: χ² p eski [${pE.map(v => v.toFixed(2)).join(', ')}] Fisher ${fE.toFixed(3)}; yeni [${pN.map(v => v.toFixed(2)).join(', ')}] Fisher ${fN.toFixed(3)}`); }
// (4) kapsama
if (!KISA) { const K = 300, lam0 = 20, T = 30, b0 = 1.0, Mc = 4.0, dm = 0.1, B = 2000, H = [[5, 10], [6, 30], [7, 100]], cE = H.map(() => 0), cN = H.map(() => 0), r = N.mulberry32(4242), beta = b0 * Math.LN10;
  for (let k = 0; k < K; k++) { const n = N.poissonSample(lam0 * T, r), mg = []; for (let i = 0; i < n; i++) mg.push(N.bGridRound(Mc - dm / 2 - Math.log(1 - r()) / beta, Mc, dm)); const bh = N.computeBvalue(mg, Mc, dm);
    const dE = eskiDraws(n, bh, Mc, dm, B, 9000 + k).D, dN = yeniDraws(n, bh, Mc, dm, B, 9000 + k).D;
    H.forEach(([M, t], j) => { const P0 = N.grPoissonP(lam0 * Math.pow(10, -b0 * (M - Mc)), t), pr = D => { const P = D.map(([ns, bs]) => N.grPoissonP(N.grLambdaSimple(ns, T, bs, Mc, M), t)); return [pct(P, 0.025), pct(P, 0.975)]; };
      const [l1, h1] = pr(dE), [l2, h2] = pr(dN); if (l1 <= P0 && P0 <= h1) cE[j]++; if (l2 <= P0 && P0 <= h2) cN[j]++; }); }
  R.kapsama = H.map(([M, t], j) => ({ M, t, eski: cE[j] / K, yeni: cN[j] / K }));
  H.forEach(([M, t], j) => ok(Math.abs(cE[j] - cN[j]) / K <= 0.03 && cN[j] / K >= 0.91, `(4) kapsama P(≥${M}; ${t} yıl), ${K} katalog, B = ${B}: eski %${(100 * cE[j] / K).toFixed(1)}, yeni %${(100 * cN[j] / K).toFixed(1)} (beklenen ≈ %95)`)); }
// (5) süre
if (!KISA) { const n = 27346, b = 1.14, B = 2000; let t0 = Date.now(); eskiDraws(n, b, 3.2, 0.1, B, 1); const tE = Date.now() - t0; t0 = Date.now(); yeniDraws(n, b, 3.2, 0.1, B, 1); const tN = Date.now() - t0;
  R.sure_ms = { n, B, eski: tE, yeni: tN }; console.log(`\n(5) süre, n = ${n}, B = ${B}: eski ${tE} ms, yeni ${tN} ms (eski şema tarayıcıda 4·10⁶ çekiliş sınırıyla B = 200'e düşüyordu)`); }
if (!KISA) fs.writeFileSync(path.join(__dirname, 'negbin_karsilastirma.json'), JSON.stringify(R, null, 1));
console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
