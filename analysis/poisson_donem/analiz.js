// Poisson bağımsız dönem sınaması ve dağılım testi — analiz (2026-11-01). Girdi: disa_aktar.js çıktısı. Çıktı: sonuc.json + konsol özeti.
// ÖNCEDEN SABİTLENEN KURALLAR (sınama dönemine bakılmadan):
//   • Önceden seçilen sınama: EMSC içinde; K = 1998-01-01 … 2012-01-01 (14,0 yıl), S = 2012-01-01 … pencere sonu. DÜZELTME (tür bileşimi denetimi,
//     sınama sonuçlarına bakılmadan): EMSC'de 2010–2012'de MD → ML geçişi var; ana sınama ML dönemi içinde (2012–2018 → 2019–son), ikinci denetim
//     MD dönemi içinde (1998–2003 → 2004–2009). Önceden seçilen bölünme 'karışık' etiketiyle raporlanır.
//   • Mc = kurma döneminin Mc'si (uygulamanın computeMc'si). Sınama döneminin Mc'si yalnız tamlık denetimi için raporlanır.
//   • Eşikler: Mc, 4,0, 4,5, 5,0, 5,5, 6,0. Büyüklük: ham (dönüşüm yok); Scordilis (2006) yalnız duyarlılık. GK74 kapalı ve açık.
//   • Model 1 (sabit hız, ampirik): λ̂(≥M) = N_K(≥M)/T_K. Sınama: koşullu binom N_S | N_K + N_S ~ Bin(N, T_S/(T_K + T_S)) (λ̂'nın belirsizliği dahil),
//     iki yönlü kesin p; hız oranı R = (N_S/T_S)/(N_K/T_K), %95 aralık (Clopper–Pearson'dan).
//   • Model 2 (sabit hız, G–R uzatması): λ(≥M) = N_K(≥Mc)/T_K · 10^(−b̂(M − Mc)), b̂ Aki–Utsu (ΔM = 0,1). Öngörü dağılımı parametrik bootstrap
//     (N* ~ Poisson(N_K(≥Mc)), b* ~ N(b̂, b̂/√N), X ~ Poisson(λ*·T_S); 20 000 çekiliş, tohum 2026); iki yönlü öngörü p'si.
//   • Model 3 (zamanla değişen hız): yıllık sayılarda log-doğrusal Poisson regresyonu (yalnız K'nın tam yılları). Gerekçe ölçütü: K içinde eğilim için
//     olabilirlik oranı testi p < 0,05. Öngörü başarısı: S'nin tam yıllarının Poisson log-olabilirliği (log-skor), Model 1 ile karşılaştırma.
//   • Dağılım testi: tam yıllık sayılar (K: 1998–2011, S: 2012–2025), D = Σ(x − x̄)²/x̄ ~ χ²(n − 1), üst kuyruk; ayrıca eğilim çıkarılmış
//     (log-doğrusal uyum) Pearson χ²/sd, sd = n − 2. Eşikler Mc, 4,0, 4,5.
//   • İkincil (katalog sınırı): Türkiye ISC → EMSC. (i) K = 1990–1997 (8 yıl), S = 1998–pencere sonu, M ≥ 4,0 ve 4,5;
//     (ii) K = 1971–1997, M ≥ 5,0 ve 5,5 (ISC'nin 1970–80'lerdeki yıllık Mc'si 5,0'a çıktığı için 4,x eşikleri bu dönemde tam değil). Ham ve Scordilis.
//   • Maruziyet: T = (bitiş − başlangıç)/365,25 gün. 'son' biten sınama dönemi pencere sonuna (katalogun son olayı) kadar gider; kısmi son yıl öngörü
//     sınamasına maruziyet olarak girer. Dağılım testi ve Model 3 yalnız tam takvim yıllarını kullanır (kısmi yıl farklı maruziyetli bir sayımdır).
// SONRADAN EKLENEN (2026-11-01, sonuçlar görüldükten sonra; testlerin kendisi değişmedi): çoklu test düzeltmesi. Tek bir birincil test önceden
//   tanımlanmamıştı; bu yüzden 'birincil' seçilmez, önceden sabitlenen test ailelerine Holm (1979) adım-adım düzeltmesi uygulanır (FWER, bağımlılık
//   varsayımı yok). Aileler: (a) Model 1, GK74, ham büyüklük, ml + md bölünmeleri × Türkiye + Marmara, M ≥ 4,0–6,0 (20 test); (b) aynı, Mc dahil
//   (24 test); (c) dağılım testi, GK74, M ≥ 4,0 ve 4,5, aynı bölünme ve bölgelerin K ve S dönemleri (16 test). Ham p'ler değişmeden raporlanır.
// Kullanım (depo kökünde): node analysis/poisson_donem/analiz.js <disa_aktar çıktısı.json>
'use strict';
const fs = require('fs'), path = require('path');
const V = require.main === module ? JSON.parse(fs.readFileSync(process.argv[2], 'utf8')) : null;
const YIL = 365.25 * 864e5, Y = y => Date.UTC(y, 0, 1);
// ── Sayısal yardımcılar ──
const lgam = x => { const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]; let y = x, t = x + 5.5; t -= (x + 0.5) * Math.log(t); let s = 1.000000000190015; for (const v of c) s += v / ++y; return -t + Math.log(2.5066282746310005 * s / x); };
function gammaP(a, x) { if (x <= 0) return 0; const lg = a * Math.log(x) - x - lgam(a);
  if (x < a + 1) { let ap = a, sum = 1 / a, d = sum; for (let n = 0; n < 100000; n++) { ap++; d *= x / ap; sum += d; if (Math.abs(d) < Math.abs(sum) * 1e-15) break; } return Math.min(1, sum * Math.exp(lg)); }
  let b = x + 1 - a, c = 1e300, d = 1 / b, h = d; for (let i = 1; i < 100000; i++) { const an = -i * (i - a); b += 2; d = an * d + b; if (Math.abs(d) < 1e-300) d = 1e-300; c = b + an / c; if (Math.abs(c) < 1e-300) c = 1e-300; d = 1 / d; const del = d * c; h *= del; if (Math.abs(del - 1) < 1e-15) break; }
  return Math.max(0, 1 - Math.exp(lg) * h); }
const chi2Sf = (x, k) => 1 - gammaP(k / 2, x / 2);
const poisCdf = (k, mu) => k < 0 ? 0 : 1 - gammaP(k + 1, mu);          // P(X ≤ k)
const lbinom = (k, n, q) => lgam(n + 1) - lgam(k + 1) - lgam(n - k + 1) + k * Math.log(q) + (n - k) * Math.log(1 - q);
function binom2(k, n, q) { if (n === 0) return 1; const p0 = lbinom(k, n, q); let s = 0; for (let j = 0; j <= n; j++) { const l = lbinom(j, n, q); if (l <= p0 + 1e-9) s += Math.exp(l); } return Math.min(1, s); }
function betaInvCP(k, n, alfa) {   // Clopper–Pearson sınırları ikiye bölmeyle (binom kuyrukları)
  const cdf = (j, q) => { let s = 0; for (let i = 0; i <= j; i++) s += Math.exp(lbinom(i, n, q)); return s; };
  const bis = f => { let lo = 1e-12, hi = 1 - 1e-12; for (let i = 0; i < 100; i++) { const m = (lo + hi) / 2; if (f(m)) lo = m; else hi = m; } return (lo + hi) / 2; };
  const alt = k === 0 ? 0 : bis(q => 1 - cdf(k - 1, q) < alfa / 2), ust = k === n ? 1 : bis(q => cdf(k, q) > alfa / 2);
  return [alt, ust]; }
const rng = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
function poisRand(mu, r) { if (mu < 30) { let k = 0, p = Math.exp(-mu), c = p; const u = r(); while (u > c) { k++; p *= mu / k; c += p; } return k; }
  const g = Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r()); return Math.max(0, Math.round(mu + Math.sqrt(mu) * g)); }   // μ ≥ 30: normal yaklaşımı
const akiB = (ms, Mc) => { const v = ms.filter(m => m >= Mc - 1e-9); if (v.length < 10) return null; const o = v.reduce((a, x) => a + x, 0) / v.length; return { b: Math.LOG10E / (o - (Mc - 0.05)), n: v.length }; };
// Log-doğrusal Poisson regresyonu (IRLS): x_i ~ Poisson(exp(α + β·t_i)); t merkezli
function poisReg(t, x) { const tm = t.reduce((a, v) => a + v, 0) / t.length, u = t.map(v => v - tm); let a = Math.log(Math.max(0.5, x.reduce((s, v) => s + v, 0) / x.length)), b = 0;
  for (let it = 0; it < 100; it++) { let g0 = 0, g1 = 0, h00 = 0, h01 = 0, h11 = 0; u.forEach((ui, i) => { const mu = Math.exp(a + b * ui); g0 += x[i] - mu; g1 += (x[i] - mu) * ui; h00 += mu; h01 += mu * ui; h11 += mu * ui * ui; });
    const det = h00 * h11 - h01 * h01; if (!(det > 0)) break; const da = (h11 * g0 - h01 * g1) / det, db = (h00 * g1 - h01 * g0) / det; a += da; b += db; if (Math.abs(da) + Math.abs(db) < 1e-12) break; }
  const ll = u.reduce((s, ui, i) => { const mu = Math.exp(a + b * ui); return s + x[i] * Math.log(mu) - mu - lgam(x[i] + 1); }, 0);
  return { a, b, tm, ll, mu: tt => Math.exp(a + b * (tt - tm)) }; }
const llSabit = x => { const m = x.reduce((a, v) => a + v, 0) / x.length; return x.reduce((s, v) => s + (v > 0 ? v * Math.log(m) : 0) - m - lgam(v + 1), 0); };
const logSkor = (x, mus) => x.reduce((s, v, i) => s + v * Math.log(mus[i]) - mus[i] - lgam(v + 1), 0);
// ── Analiz ──
const ESIKLER = mc => [mc, 4.0, 4.5, 5.0, 5.5, 6.0].filter((v, i, a) => a.indexOf(v) === i && v >= mc - 1e-9);
function say(ev, t0, t1, M, key) { let n = 0; for (const e of ev) if (e.t >= t0 && e.t < t1 && e[key] >= M - 1e-9) n++; return n; }
function yillik(ev, y0, y1, M, key) { const c = {}; for (let y = y0; y <= y1; y++) c[y] = 0; for (const e of ev) { const y = new Date(e.t).getUTCFullYear(); if (y >= y0 && y <= y1 && e[key] >= M - 1e-9) c[y]++; } return Object.entries(c).map(([y, v]) => [+y, v]); }
function sinama(ev, K, S, Mc, key, esikler, etiket) {
  const TK = (K[1] - K[0]) / YIL, TS = (S[1] - S[0]) / YIL, magsK = ev.filter(e => e.t >= K[0] && e.t < K[1]).map(e => e[key]), bk = akiB(magsK, Mc), NKmc = say(ev, K[0], K[1], Mc, key);
  const r = rng(2026), sonuc = { etiket, TK, TS, Mc, b: bk ? bk.b : null, NKmc, esik: [] };
  for (const M of esikler) {
    const NK = say(ev, K[0], K[1], M, key), NS = say(ev, S[0], S[1], M, key), q = TS / (TK + TS), N = NK + NS;
    const pBin = binom2(NS, N, q), [pl, pu] = N > 0 ? betaInvCP(NS, N, 0.05) : [0, 1], oran = x => (x / (1 - x)) * (TK / TS);
    // G–R uzatması (Model 2) ve öngörü bootstrap'ı
    let gr = null;
    if (bk && M > Mc + 1e-9) { const lam = NKmc / TK * Math.pow(10, -bk.b * (M - Mc)), sd = bk.b / Math.sqrt(bk.n), X = [];
      for (let i = 0; i < 20000; i++) { const nS = poisRand(NKmc, r), bS = bk.b + sd * Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r()); X.push(poisRand(nS / TK * Math.pow(10, -bS * (M - Mc)) * TS, r)); }
      X.sort((a, b) => a - b); const le = X.filter(v => v <= NS).length / X.length, ge = X.filter(v => v >= NS).length / X.length;
      gr = { beklenen: lam * TS, alt: X[Math.floor(0.025 * X.length)], ust: X[Math.floor(0.975 * X.length)], p: Math.min(1, 2 * Math.min(le, ge)) }; }
    sonuc.esik.push({ M, NK, NS, beklenen1: NK / TK * TS, oran: NK > 0 && NS > 0 ? (NS / TS) / (NK / TK) : null, oranAlt: N > 0 && pl > 0 ? oran(pl) : 0, oranUst: N > 0 && pu < 1 ? oran(pu) : Infinity, pBin, gr });
  }
  return sonuc;
}
function zamanModeli(ev, KY, SY, M, key) {   // KY, SY: [ilk tam yıl, son tam yıl]
  const k = yillik(ev, KY[0], KY[1], M, key), s = yillik(ev, SY[0], SY[1], M, key), tk = k.map(v => v[0]), xk = k.map(v => v[1]), ts = s.map(v => v[0]), xs = s.map(v => v[1]);
  const reg = poisReg(tk, xk), l0 = llSabit(xk), LR = 2 * (reg.ll - l0), pLR = chi2Sf(Math.max(0, LR), 1), mK = xk.reduce((a, v) => a + v, 0) / xk.length;
  return { M, KY, SY, egimYuzde: 100 * (Math.exp(reg.b) - 1), pEgimK: pLR, gerekce: pLR < 0.05, logSkor1: logSkor(xs, xs.map(() => mK)), logSkor3: logSkor(xs, ts.map(t => reg.mu(t))),
    beklenen1: mK * xs.length, beklenen3: ts.reduce((a, t) => a + reg.mu(t), 0), gozlenen: xs.reduce((a, v) => a + v, 0) }; }
function dagilim(ev, y0, y1, M, key) {
  const c = yillik(ev, y0, y1, M, key), x = c.map(v => v[1]), n = x.length, m = x.reduce((a, v) => a + v, 0) / n, s2 = x.reduce((a, v) => a + (v - m) ** 2, 0) / (n - 1), D = (n - 1) * s2 / m;
  const reg = poisReg(c.map(v => v[0]), x), P = x.reduce((a, v, i) => { const mu = reg.mu(c[i][0]); return a + (v - mu) ** 2 / mu; }, 0);
  return { M, yillar: [y0, y1], n, ort: m, varyans: s2, oran: s2 / m, p: chi2Sf(D, n - 1), egimsizOran: P / (n - 2), pEgimsiz: chi2Sf(P, n - 2), min: Math.min(...x), max: Math.max(...x) }; }
function holm(p) {   // Holm (1979): sıralı p_(i)·(m − i + 1), birikimli maksimum, 1'de kesilir; giriş sırasıyla döner
  const m = p.length, o = p.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]), q = new Array(m); let run = 0;
  o.forEach(([v, i], r) => { run = Math.max(run, Math.min(1, v * (m - r))); q[i] = run; }); return q; }
module.exports = { gammaP, chi2Sf, poisCdf, binom2, betaInvCP, poisReg, akiB, dagilim, yillik, holm };
if (require.main === module) {
const R = { girdi: V.uretim, kurallar: 'analiz.js başlığı', bolunmeler: {}, ana: {}, zaman: {}, dagilim: {}, bilesim: {}, ikincil: {} };
// Bölünmeler. 'karisik' önceden seçilen bölünmedir; tür bileşimi denetimi (sınama sonuçlarına bakılmadan) EMSC'de 2010–2012 arasında MD → ML geçişini gösterdi
// (Türkiye M ≥ 3,2: 1998–2009 MD %73–94; 2012– MD %0, ML %85–93). Bu yüzden ana sınama tek tür dönemi içinde yapılır: 'ml' (ana) ve 'md' (ikinci denetim).
const BOL = {
  ml:      { ad: 'ML dönemi (ana): 2012–2018 → 2019–son', K: [Y(2012), Y(2019)], Sson: true, S0: Y(2019), mcK: 'd2012_2018', mcS: 'd2019_son', yK: [2012, 2018], yS: [2019, 2025] },
  md:      { ad: 'MD dönemi (ikinci): 1998–2003 → 2004–2009', K: [Y(1998), Y(2004)], S: [Y(2004), Y(2010)], mcK: 'd1998_2003', mcS: 'd2004_2009', yK: [1998, 2003], yS: [2004, 2009] },
  karisik: { ad: 'Önceden seçilen (MD → ML geçişini kesiyor; karışık): 1998–2011 → 2012–son', K: [Y(1998), Y(2012)], Sson: true, S0: Y(2012), mcK: 'd1998_2011', mcS: 'd2012_son', yK: [1998, 2011], yS: [2012, 2025] },
};
const bilesim = (ev, a, b, M) => { const c = {}; let n = 0; for (const e of ev) if (e.t >= a && e.t < b && e.m >= M - 1e-9) { c[e.tur] = (c[e.tur] || 0) + 1; n++; } return Object.fromEntries(Object.entries(c).sort((x, y) => y[1] - x[1]).map(([k, v]) => [k, +(100 * v / n).toFixed(1)])); };
for (const [bk, B] of Object.entries(BOL)) { R.bolunmeler[bk] = B.ad;
  for (const sen of ['tr_emsc', 'mar_emsc']) { const s = V.senaryolar[sen], K = B.K, S = B.Sson ? [B.S0, s.pencereSon] : B.S;
    for (const gk of [0, 1]) { const ev = gk ? s.olaylar.filter(e => e.gk) : s.olaylar, g = gk ? 'gk74' : 'ham', ad = `${bk}|${sen}|${g}`, Mc = s.mc[`${B.mcK}|${g}`].mc;
      R.ana[ad] = sinama(ev, K, S, Mc, 'm', ESIKLER(Mc), ad); R.ana[ad].McS = s.mc[`${B.mcS}|${g}`].mc;
      if (sen === 'tr_emsc') R.ana[ad + '|scordilis'] = sinama(ev, K, S, Mc, 'ms', ESIKLER(Mc).filter(v => v >= 4.0), ad + '|scordilis');
      R.zaman[ad] = [Mc, 4.0, 4.5].map(M => zamanModeli(ev, B.yK, B.yS, M, 'm'));
      R.dagilim[ad] = [Mc, 4.0, 4.5].flatMap(M => [dagilim(ev, B.yK[0], B.yK[1], M, 'm'), dagilim(ev, B.yS[0], B.yS[1], M, 'm')]);
      if (!gk) R.bilesim[`${bk}|${sen}`] = { K: { 'M≥Mc': bilesim(ev, K[0], K[1], Mc), 'M≥4,0': bilesim(ev, K[0], K[1], 4.0) }, S: { 'M≥Mc': bilesim(ev, S[0], S[1], Mc), 'M≥4,0': bilesim(ev, S[0], S[1], 4.0) } }; } } }
{ const s = V.senaryolar.tr_isc_emsc, S = [Y(1998), s.pencereSon];
  for (const gk of [0, 1]) { const ev = gk ? s.olaylar.filter(e => e.gk) : s.olaylar, g = gk ? 'gk74' : 'ham';
    for (const key of ['m', 'ms']) { const k = key === 'm' ? 'ham' : 'scordilis';
      R.ikincil[`1990_1997|${g}|${k}`] = sinama(ev, [Y(1990), Y(1998)], S, 4.0, key, [4.0, 4.5], `ISC 1990–1997 → EMSC|${g}|${k}`);
      R.ikincil[`1971_1997|${g}|${k}`] = sinama(ev, [Y(1971), Y(1998)], S, 5.0, key, [5.0, 5.5], `ISC 1971–1997 → EMSC|${g}|${k}`); } } }
// Çoklu test düzeltmesi (sonradan; bkz. başlık)
R.coklu = {};
{ const aile = (ad, ogeler) => { const q = holm(ogeler.map(o => o.p)); R.coklu[ad] = { m: ogeler.length, testler: ogeler.map((o, i) => ({ ...o, pHolm: q[i] })),
    ham005: ogeler.filter(o => o.p < 0.05).length, holm005: q.filter(v => v < 0.05).length }; };
  const m1 = (mcDahil) => { const L = []; for (const bk of ['ml', 'md']) for (const sen of ['tr_emsc', 'mar_emsc']) { const x = R.ana[`${bk}|${sen}|gk74`];
    for (const e of x.esik) if (mcDahil || e.M >= 4.0 - 1e-9) L.push({ test: `${bk}|${sen}|gk74`, M: e.M, NK: e.NK, NS: e.NS, p: e.pBin }); } return L; };
  aile('model1_gk74_M4_6', m1(false)); aile('model1_gk74_McDahil', m1(true));
  const D = []; for (const bk of ['ml', 'md']) for (const sen of ['tr_emsc', 'mar_emsc']) for (const d of R.dagilim[`${bk}|${sen}|gk74`])
    if (d.M >= 4.0 - 1e-9) D.push({ test: `${bk}|${sen}|gk74`, yillar: d.yillar, M: d.M, oran: d.oran, p: d.p });
  aile('dagilim_gk74_M4_45', D); }
fs.writeFileSync(path.join(__dirname, 'sonuc.json'), JSON.stringify(R, null, 1));
// ── Özet ──
const f = (v, d = 2) => v === null || v === undefined || !Number.isFinite(v) ? '—' : v.toFixed(d), pp = v => v < 1e-4 ? v.toExponential(1) : v.toFixed(3);
const tablo = (b, x) => { console.log(`\n${x.etiket}: T_K ${f(x.TK, 1)} yıl, T_S ${f(x.TS, 1)} yıl, Mc ${x.Mc}${x.McS !== undefined ? ` (S'nin Mc'si ${x.McS})` : ''}, b̂ ${f(x.b)}`);
  x.esik.forEach(e => console.log(`  M≥${e.M.toFixed(1)}: N_K ${String(e.NK).padStart(5)} → beklenen ${f(e.beklenen1, 1).padStart(7)} | gözlenen ${String(e.NS).padStart(5)} | oran ${f(e.oran)} [${f(e.oranAlt)}–${f(e.oranUst)}] p=${pp(e.pBin)}` + (e.gr ? ` | G–R: beklenen ${f(e.gr.beklenen, 1)} [${e.gr.alt}–${e.gr.ust}] p=${pp(e.gr.p)}` : ''))); };
console.log('══ SINAMALAR (bölünme|bölge|katalog[|ölçek]) ══'); Object.entries(R.ana).forEach(([k, x]) => tablo(k, x));
console.log('\n══ TÜR BİLEŞİMİ (%; ham) ══'); Object.entries(R.bilesim).forEach(([k, v]) => console.log(`  ${k}: K ${JSON.stringify(v.K)} | S ${JSON.stringify(v.S)}`));
console.log('\n══ ZAMANLA DEĞİŞEN HIZ (log-doğrusal; yıllık; gerekçe: K içinde eğilim p < 0,05) ══');
Object.entries(R.zaman).forEach(([k, a]) => a.forEach(z => console.log(`  ${k.padEnd(16)} M≥${z.M.toFixed(1)}: eğim %${f(z.egimYuzde, 1)}/yıl (K içinde p=${pp(z.pEgimK)}; ${z.gerekce ? 'gerekçeli' : 'gerekçesiz'}) | S toplamı: sabit ${f(z.beklenen1, 0)}, eğilimli ${f(z.beklenen3, 0)}, gözlenen ${z.gozlenen} | log-skor sabit ${f(z.logSkor1, 1)}, eğilimli ${f(z.logSkor3, 1)}`)));
console.log('\n══ DAĞILIM TESTİ (tam yıllar; varyans/ortalama; χ²) ══');
Object.entries(R.dagilim).forEach(([k, a]) => a.forEach(d => console.log(`  ${k.padEnd(16)} ${d.yillar.join('–')} M≥${d.M.toFixed(1)}: n=${d.n} ort ${f(d.ort, 1)} var/ort ${f(d.oran)} p=${pp(d.p)} | eğilimsiz Pearson/sd ${f(d.egimsizOran)} p=${pp(d.pEgimsiz)} | min–maks ${d.min}–${d.max}`)));
console.log('\n══ İKİNCİL (katalog sınırı ISC → EMSC) ══'); Object.entries(R.ikincil).forEach(([k, x]) => tablo(k, x));
console.log('\n══ ÇOKLU TEST (Holm; sonradan) ══'); Object.entries(R.coklu).forEach(([k, a]) => { console.log(`  ${k}: m = ${a.m}; ham p < 0,05: ${a.ham005}; Holm p < 0,05: ${a.holm005}`);
  a.testler.filter(t => t.p < 0.1).forEach(t => console.log(`    ${t.test.padEnd(18)} ${t.yillar ? t.yillar.join('–') + ' ' : ''}M≥${t.M.toFixed(1)}: p = ${pp(t.p)} → Holm ${pp(t.pHolm)}`)); });

}
