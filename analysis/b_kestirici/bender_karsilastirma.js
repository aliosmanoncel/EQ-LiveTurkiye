// Aki–Utsu ve Bender (1983) b kestiricilerinin karşılaştırması (2026-11-01). AYRI ANALİZ: uygulama (index.html) değiştirilmez;
// Aki–Utsu referans yöntem olarak kalır. Kaynak: Bender, B. (1983). BSSA 73(3), 831–851 (Zotero, DVM4CQ9X), Ek Denk. (A7) ve Denk. (10).
//
// Tanımlar (ΔM sınıf genişliği; Mc = katalogdaki en küçük tam sınıfın MERKEZİ, uygulamadaki tanım; Bender'in m_min'i = Mc − ΔM/2, alt sınır):
//   Kᵢ = (mᵢ − Mc)/ΔM ∈ {0, 1, …}, K̄ = (m̄ − Mc)/ΔM.
//   Aki–Utsu (uygulama, computeBvalue): b_AU = log₁₀e / (m̄ − Mc + ΔM/2).
//   Bender, Mmax = ∞ (Denk. A7 ⇔ Denk. 10, n → ∞): q/(1 − q) = K̄, q = 10^(−bΔM) ⇒ b_B = log₁₀(1 + 1/K̄) / ΔM = log₁₀(1 + ΔM/(m̄ − Mc)) / ΔM.
//   Bender, sonlu Mmax (Denk. 10; n sınıf, son sınıf Mmax): q/(1 − q) − n·qⁿ/(1 − qⁿ) = K̄ — yalnız duyarlılık (Mmax = gözlenen en büyük sınıf;
//   Bender s. 834: bu, olası en büyük büyüklük değildir; kesik G–R aşama 5'te ayrıca planlanacak).
//   Bender ΔM → 0'da Aki'ye iner; ΔM > 0'da gruplanmış geometrik modelin kesin en çok olabilirlik kestiricisidir.
//
// Denetimler ve çıktılar:
//   (0) Büyüklük tanımı: kayıttaki büyüklükler uygulamadaki gibi ΔM ızgarasına (bGridVals) alınır; ızgara dışı olay sayısı raporlanır;
//       b_AU kayıttaki b ile birebir aynı olmalı (aynı girdi, aynı tanım).
//   (1) Gerçek bölgeler (Türkiye, Marmara, Doğu Anadolu; poisson_olasilik/cmp_yeniden_uretim.json): b_AU, b_B (∞), b_B (sonlu Mmax);
//       moment uyumu (modelin öngördüğü K̄ = q/(1 − q) ile gözlenen K̄); sınıf sayılarına χ² uyumu.
//   (2) Bootstrap (B = 2000, tohum 20261027; uygulamanın örnekleyicisiyle aynı (n*, S) çekilişi, her kestirici kendi b'sinden üretir):
//       %95 aralık, ortanca sapması, nokta kestiriminin bootstrap dağılımındaki yüzdelik konumu (0,5 = aralıkla tam uyum).
//   (3) Olasılığa etkisi: P(≥M; t), M 5/6/7, t 10/50/100, iki kestiriciyle (nokta ve %95).
//   (4) Benzetim: bilinen b ∈ {0,8; 1,0; 1,14; 1,3}, n ∈ {100; 624; 5000; 27 346}, ΔM = 0,1; olay olay üretilen 400 katalog: yanlılık, RMSE,
//       %95 bootstrap aralığının gerçek b'yi ve gerçek P(≥7; 50 yıl)'ı kapsama oranı (B = 500).
// Kullanım (depo kökünde): node analysis/b_kestirici/bender_karsilastirma.js   (KISA=1: benzetimde 100 katalog)
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..', '..'), KISA = process.env.KISA === '1';
const src = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = n => { const i = src.indexOf('\nfunction ' + n + '('); if (i < 0) throw new Error('yok ' + n); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const X = { B_GRID_MODE: 'sinif' }; vm.createContext(X);
vm.runInContext([src.match(/^const GR_POIS = [^\n]*$/m)[0], src.match(/^const GR_QC = [^\n]*$/m)[0]].map(l => l.replace(/^const /, 'var ')).join('\n') + '\n' +
  ['mulberry32', 'logGamma', 'poissonSample', 'gammaSample', 'grBootDraws', 'bGridRound', 'bGridOffCount', 'bGridVals', 'computeBvalue', 'grPoissonP', 'grLambdaSimple', 'grPctl'].map(fn).join('\n'), X);
vm.runInContext(src.match(/^const LANCZOS_C = \[[\s\S]*?\];$/m)[0].replace(/^const /, 'var '), X);
const LOG10E = Math.LOG10E, SEED = 20261027;
// ── kestiriciler (K̄ ya da (n, S) üzerinden; S = ΣK)
const bAU = (Kb, dm) => LOG10E / (dm * Kb + dm / 2);
const bB = (Kb, dm) => Kb > 0 ? Math.log10(1 + 1 / Kb) / dm : Infinity;
function bBfin(Kb, dm, nInt) {   // Denk. 10: g(q) = q/(1−q) − n qⁿ/(1−qⁿ) artan; g(q) = K̄ ikiye bölme ile
  if (!(Kb > 0) || nInt < 2 || Kb >= (nInt - 1) / 2) return null;   // K̄ ≥ (n−1)/2: düzgün dağılım sınırı, b ≤ 0
  const g = q => q / (1 - q) - nInt * Math.pow(q, nInt) / (1 - Math.pow(q, nInt)); let lo = 1e-12, hi = 1 - 1e-12;
  for (let k = 0; k < 200; k++) { const m = (lo + hi) / 2; (g(m) < Kb ? lo = m : hi = m); } return -Math.log10((lo + hi) / 2) / dm; }
const qOf = (b, dm) => Math.pow(10, -b * dm);
// ── (n*, S) çekilişi: grBootDraws ile aynı akış (birebir denetlenir), S de döndürülür
function draws(n, bGen, dm, B, seed) { const rnd = X.mulberry32(seed), q = qOf(bGen, dm), th = q / (1 - q), D = [];
  for (let r = 0; r < B; r++) { const ns = X.poissonSample(n, rnd); if (ns < 10) continue; D.push([ns, X.poissonSample(X.gammaSample(ns, rnd) * th, rnd)]); } return D; }
const pct = (a, q) => X.grPctl(a, q), rank = (a, v) => a.filter(x => x < v).length / a.length + 0.5 * a.filter(x => x === v).length / a.length;
const R = { kaynak: 'Bender, B. (1983) BSSA 73(3) 831–851; Ek (A7), Denk. (10)', uretim: new Date().toISOString(), node: process.version, bolgeler: [], benzetim: [], denetim: [] };
let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; R.denetim.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };
// sağlama: draws = grBootDraws (aynı tohum, aynı akış)
{ const a = draws(624, 1.0, 0.1, 300, SEED), b = X.grBootDraws(624, 1.0, 3.2, 0.1, 300, SEED).D;
  ok(a.length === b.length && a.every(([ns, S], i) => ns === b[i][0] && Math.abs(bAU(S / ns, 0.1) - b[i][1]) < 1e-12), '(0) çekiliş akışı uygulamanın grBootDraws\'u ile birebir aynı (Aki–Utsu b* eşit)'); }
// ── (1)–(3) gerçek bölgeler
const J = JSON.parse(fs.readFileSync(path.join(ROOT, 'analysis', 'poisson_olasilik', 'cmp_yeniden_uretim.json'), 'utf8'));
R.girdi = { dosya: 'analysis/poisson_olasilik/cmp_yeniden_uretim.json', yazilim_blob: J.yazilim.index_html_git_blob_sha1, katalog: J.bolgeler[0].katalog.dosyalar, katalog_blob: J.bolgeler[0].katalog.blob, uretim: J.bolgeler[0].katalog.uretim };
const MS = [5, 6, 7], TS = [10, 50, 100], B = 2000;
for (const G of J.bolgeler) {
  const dm = G.dM, Mc = G.Mc, T = G.donem.T_yil, gM = X.bGridVals(G.girdi_buyukluklar, dm !== 0.1 ? Mc : 0, dm), sub = gM.vals.filter(m => m >= Mc - 1e-9), n = sub.length;
  const K = sub.map(m => Math.round((m - Mc) / dm)), S = K.reduce((a, k) => a + k, 0), Kb = S / n, ongrid = sub.every((m, i) => Math.abs(m - (Mc + dm * K[i])) < 1e-6);
  const au = bAU(Kb, dm), be = bB(Kb, dm), Kmax = Math.max(...K), bf = bBfin(Kb, dm, Kmax + 1);
  ok(n === G.N_geMc && Math.abs(au - G.b) < 1e-12 && Math.abs(X.computeBvalue(gM.vals, Mc, dm) - G.b) < 1e-12 && ongrid, `(0) ${G.ad}: N(≥Mc) = ${n}, b_AU = ${au.toFixed(4)} = kayıttaki b; ${gM.nOff} büyüklük ızgara dışıydı (uygulamadaki gibi sınıf merkezine alındı), Mc üstü hepsi Mc + kΔM ızgarasında`);
  // moment uyumu ve χ² (sınıflar; beklenen ≥ 5 olacak biçimde kuyruk birleştirilir)
  const cnt = new Map(); K.forEach(k => cnt.set(k, (cnt.get(k) || 0) + 1));
  const chi = b => { const q = qOf(b, dm), p = 1 - q; let X2 = 0, df = -2, k = 0, cumE = 0, cumO = 0; while (true) { const e = n * p * Math.pow(q, k), o = cnt.get(k) || 0;
      if (n * Math.pow(q, k + 1) < 5) { const eT = n * Math.pow(q, k), oT = [...cnt].filter(([kk]) => kk >= k).reduce((a, [, v]) => a + v, 0); X2 += (oT - eT) ** 2 / eT; df++; break; }
      X2 += (o - e) ** 2 / e; df++; k++; } return { X2, df }; };
  const yer = (b) => { const q = qOf(b, dm); return q / (1 - q); };
  const D_au = draws(n, au, dm, B, SEED), D_be = draws(n, be, dm, B, SEED);
  const bsA = D_au.map(([ns, s]) => bAU(s / ns, dm)), bsB = D_be.map(([ns, s]) => bB(s / ns, dm));
  const P = (D, est, M, t) => D.map(([ns, s]) => X.grPoissonP(X.grLambdaSimple(ns, T, est(s / ns, dm), Mc, M), t));
  const olas = []; for (const M of MS) for (const t of TS) { const pa = P(D_au, bAU, M, t), pb = P(D_be, bB, M, t);
    olas.push({ M, t, AU: { P: X.grPoissonP(X.grLambdaSimple(n, T, au, Mc, M), t), lo: pct(pa, 0.025), hi: pct(pa, 0.975) }, B83: { P: X.grPoissonP(X.grLambdaSimple(n, T, be, Mc, M), t), lo: pct(pb, 0.025), hi: pct(pb, 0.975) } }); }
  const z = { ad: G.ad, n, Mc, dM: dm, T, Kort: Kb, Kmax, Mmax_sinif: Mc + dm * Kmax, izgara_disi: gM.nOff,
    b_AU: au, b_Bender: be, b_Bender_sonluMmax: bf, fark_B_AU: be - au,
    moment: { gozlenen_K: Kb, AU_ongorulen_K: yer(au), Bender_ongorulen_K: yer(be) }, chi2: { AU: chi(au), Bender: chi(be) },
    boot: { B, tohum: SEED, AU: { lo: pct(bsA, 0.025), med: pct(bsA, 0.5), hi: pct(bsA, 0.975), sd: Math.sqrt(bsA.reduce((a, v) => a + (v - bsA.reduce((x, y) => x + y, 0) / bsA.length) ** 2, 0) / (bsA.length - 1)), nokta_yuzdelik: rank(bsA, au) },
      Bender: { lo: pct(bsB, 0.025), med: pct(bsB, 0.5), hi: pct(bsB, 0.975), sd: Math.sqrt(bsB.reduce((a, v) => a + (v - bsB.reduce((x, y) => x + y, 0) / bsB.length) ** 2, 0) / (bsB.length - 1)), nokta_yuzdelik: rank(bsB, be) } }, olasilik: olas };
  R.bolgeler.push(z);
  ok(Math.abs(z.moment.Bender_ongorulen_K - Kb) < 1e-9, `(1) ${G.ad}: Bender modelin öngördüğü ortalama sınıfı gözlenenle aynı veriyor (K̄ = ${Kb.toFixed(4)}); Aki–Utsu ${z.moment.AU_ongorulen_K.toFixed(4)}`);
  console.log(`   b_AU = ${au.toFixed(4)} [${z.boot.AU.lo.toFixed(4)}–${z.boot.AU.hi.toFixed(4)}], ortanca ${z.boot.AU.med.toFixed(4)}, nokta yüzdeliği ${z.boot.AU.nokta_yuzdelik.toFixed(3)}`);
  console.log(`   b_B  = ${be.toFixed(4)} [${z.boot.Bender.lo.toFixed(4)}–${z.boot.Bender.hi.toFixed(4)}], ortanca ${z.boot.Bender.med.toFixed(4)}, nokta yüzdeliği ${z.boot.Bender.nokta_yuzdelik.toFixed(3)}; sonlu Mmax (${(Mc + dm * Kmax).toFixed(1)}): ${bf === null ? '—' : bf.toFixed(4)}`);
  console.log(`   χ² (sınıf sayıları): AU ${z.chi2.AU.X2.toFixed(1)}/${z.chi2.AU.df} sd, Bender ${z.chi2.Bender.X2.toFixed(1)}/${z.chi2.Bender.df} sd`);
  for (const o of olas.filter(o => o.M === 7)) console.log(`   P(≥7; ${o.t}): AU %${(100 * o.AU.P).toFixed(2)} [${(100 * o.AU.lo).toFixed(2)}–${(100 * o.AU.hi).toFixed(2)}]  Bender %${(100 * o.B83.P).toFixed(2)} [${(100 * o.B83.lo).toFixed(2)}–${(100 * o.B83.hi).toFixed(2)}]`);
}
// ── (4) benzetim
{ const NR = KISA ? 100 : 400, Bs = 500, T = 28.7, Mc = 3.2, dm = 0.1, Mp = 7, tp = 50;
  for (const b0 of [0.8, 1.0, 1.14, 1.3]) for (const n0 of [100, 624, 5000, 27346]) {
    const rnd = X.mulberry32(Math.round(b0 * 1000) * 100000 + n0), beta = b0 * Math.LN10, P0 = X.grPoissonP(X.grLambdaSimple(n0, T, b0, Mc, Mp), tp);
    const st = { AU: { e: [], cb: 0, cp: 0, med: [] }, Bender: { e: [], cb: 0, cp: 0, med: [] } };
    for (let r = 0; r < NR; r++) { const n = X.poissonSample(n0, rnd); let S = 0;
      for (let i = 0; i < n; i++) S += Math.round((X.bGridRound(Mc - dm / 2 - Math.log(1 - rnd()) / beta, Mc, dm) - Mc) / dm);   // olay olay, uygulamanın ızgarası
      for (const [ad, est] of [['AU', bAU], ['Bender', bB]]) { const bh = est(S / n, dm), D = draws(n, bh, dm, Bs, 7000 + r), bs = D.map(([ns, s]) => est(s / ns, dm)), pp = D.map(([ns, s]) => X.grPoissonP(X.grLambdaSimple(ns, T, est(s / ns, dm), Mc, Mp), tp));
        const o = st[ad]; o.e.push(bh - b0); if (pct(bs, 0.025) <= b0 && b0 <= pct(bs, 0.975)) o.cb++; if (pct(pp, 0.025) <= P0 && P0 <= pct(pp, 0.975)) o.cp++; } }
    const oz = o => ({ yanlilik: o.e.reduce((a, v) => a + v, 0) / NR, rmse: Math.sqrt(o.e.reduce((a, v) => a + v * v, 0) / NR), kapsama_b: o.cb / NR, kapsama_P7_50: o.cp / NR });
    const z = { b: b0, n: n0, katalog: NR, B: Bs, AU: oz(st.AU), Bender: oz(st.Bender), P0 }; R.benzetim.push(z);
    console.log(`(4) b = ${b0}, n = ${String(n0).padStart(5)}: yanlılık AU ${z.AU.yanlilik.toFixed(4)} / B ${z.Bender.yanlilik.toFixed(4)}; RMSE ${z.AU.rmse.toFixed(4)} / ${z.Bender.rmse.toFixed(4)}; kapsama b %${(100 * z.AU.kapsama_b).toFixed(1)} / %${(100 * z.Bender.kapsama_b).toFixed(1)}; P(≥7;50) %${(100 * z.AU.kapsama_P7_50).toFixed(1)} / %${(100 * z.Bender.kapsama_P7_50).toFixed(1)}`); }
  const se = s => 1.96 * Math.sqrt(0.95 * 0.05 / NR) + 0.01;
  ok(R.benzetim.every(z => Math.abs(z.Bender.kapsama_b - 0.95) <= se() && Math.abs(z.Bender.yanlilik) < 3 * z.Bender.rmse / Math.sqrt(NR) + 1e-3), `(4) Bender: 16 senaryonun hepsinde yanlılık istatistik gürültüsü düzeyinde ve b kapsaması %95 ± ${(100 * se()).toFixed(1)}`); }
fs.writeFileSync(path.join(__dirname, KISA ? 'bender_karsilastirma_kisa.json' : 'bender_karsilastirma.json'), JSON.stringify(R, null, 1));
console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
