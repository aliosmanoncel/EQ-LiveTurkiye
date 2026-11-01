// Birinci fark (Δa–Δb) araştırması — analiz (2026-11-01). a(t) RAPOR §4.4'teki planın uygulaması. Girdi: analysis/tur_gecisi/disa_aktar.js çıktısı
// (uygulamanın kendi kodu: bölge, GK74; olaylar t, m, mt, gk). Uygulama fonksiyonları (aWinValue, aChi2Q, aPearson, aLag1, aNeffTest, computeBvalue,
// computeMcSrc) index.html'den okunur; index.html, data/ ve GK74 değişmez. Çıktı: sonuc.json + konsol özeti.
// AMAÇ: sismisite rejiminin zamansal değişimini betimlemek. Tahmin ya da öncül araştırması DEĞİLDİR; Δa–Δb ilişkisi fiziksel mekanizma ya da deprem
// habercisi olarak yorumlanmaz.
// ÖNCEDEN SABİTLENEN TASARIM (sonuçlar görülmeden):
//   • Pencereler: aynı Mc'deki olaylar zamana göre sıralanır; baştan başlayarak ardışık, ÖRTÜŞMEYEN n'lik pencereler (son eksik pencere atılır).
//     a_i = log10(n/T_i), T_i = son − ilk olay zamanı (yıl, 365,25 gün; uygulamanın aWinValue'su). b_i: Aki (1965), ΔM = 0,1 (uygulamanın computeBvalue'su).
//     Δa_i = a_i − a_{i−1}, Δb_i = b_i − b_{i−1}. Panelin örtüşen pencereleri (adım 10) KULLANILMAZ: farkları ortak olayları ölçer.
//   • Tür dönemleri (analysis/tur_gecisi): MD 1998-01-01 – 2011-01-01, ML 2012-01-01 – pencere sonu. 2011 (geçiş yılı) dışarıda; dönemler arası fark alınmaz.
//     Gösterim için yalnız bir 'kesen' durum (Türkiye, GK74, Mc 3,5, n 100, 1998–son): tür geçişinin yapay sıçraması; yorumlanmaz.
//   • Bölgeler: Türkiye kutusu 36–42° K / 26–45° D, Marmara 40–41,5° K / 26–31° D. GK74 açık (ana) ve kapalı.
//   • Mc: 3,2 (uygulamanın Mc'si; katalog kesimi 3,0 + 0,2), 3,5, 4,0. Pencere n: 50, 100 (panelle aynı), 200. En az 6 pencere (5 fark) yoksa 'yetersiz'.
//   • Sıfır modeli (ana): büyüklük karıştırma — olay zamanları korunur, büyüklükler dönem içinde rastgele karıştırılır (2000 kez, tohum 2026).
//     a serisi ve öz-ilişkisi aynen kalır; yalnız büyüklük–zaman bağı yok edilir. İki yönlü p = (1 + #|r*| ≥ |r|)/(N + 1). Karşılaştırma için
//     Bartlett n_eff düzeltmeli Fisher z p (uygulamanın aNeffTest'i; fark serisinde gecikme-1 öz-ilişki).
//   • Ölçüler: Pearson r(Δa, Δb) (ana), Spearman; gecikmeli r(Δa_i, Δb_{i+L}), L = −2…2 (L > 0: b değişimi a değişiminden sonra); dört bölge sayıları
//     (Δa ±, Δb ±) ve karıştırma altında beklenenleri; düzey korelasyonu r(a, b) (karşılaştırma).
//   • Tamlık tanısı: her pencerenin veri Mc'si (uygulamanın computeMcSrc'si); Mc_pencere > Mc + 0,2 olan pencereler 'eksik kuşkulu'. Duyarlılık: bu
//     pencerelere dokunan farklar çıkarılarak r ve karıştırma p'si yeniden.
//   • BİRİNCİL AİLE (çoklu test, Holm): GK74 açık, Mc 3,5, n 100, Türkiye MD ve ML dönemleri (2 test). Marmara'da olay sayısı az olduğundan
//     birincil aileye alınmadı (ikincil). Diğer tüm birleşimler keşifsel.
// Kullanım (depo kökünde): node analysis/fark_ab/analiz.js <disa_aktar çıktısı.json>
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..', '..');
const src = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fnCut = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const X = {}; vm.createContext(X); vm.runInContext(['aChi2Q', 'aWinValue', 'aPearson', 'aLag1', 'aNeffTest', 'computeBvalue', 'mcSrcMag', 'computeMcSrc'].map(fnCut).join('\n'), X);
const YIL = 365.25 * 864e5, Y = y => Date.UTC(y, 0, 1), NPERM = 2000;
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const pearson = (x, y) => { const n = x.length; if (n < 3) return null; const mx = x.reduce((a, v) => a + v, 0) / n, my = y.reduce((a, v) => a + v, 0) / n; let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) { const dx = x[i] - mx, dy = y[i] - my; sxy += dx * dy; sxx += dx * dx; syy += dy * dy; } return sxx > 0 && syy > 0 ? sxy / Math.sqrt(sxx * syy) : null; };
const sira = v => { const o = v.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]), r = new Array(v.length); for (let i = 0; i < o.length;) { let j = i; while (j + 1 < o.length && o[j + 1][0] === o[i][0]) j++; for (let k = i; k <= j; k++) r[o[k][1]] = (i + j) / 2; i = j + 1; } return r; };
const fark = v => v.slice(1).map((x, i) => x - v[i]);
const gecikmeli = (da, db, L) => { const x = [], y = []; for (let i = 0; i < da.length; i++) { const j = i + L; if (j >= 0 && j < db.length) { x.push(da[i]); y.push(db[j]); } } return pearson(x, y); };
const dortlu = (da, db, maske) => { const c = { '++': 0, '+-': 0, '-+': 0, '--': 0 }; da.forEach((v, i) => { if (maske && !maske[i] || v === 0 || db[i] === 0) return; c[(v > 0 ? '+' : '-') + (db[i] > 0 ? '+' : '-')]++; }); return c; };
// Bir dönem için pencereler (a, b, veri Mc'si) ve ölçüler; büyüklük dizisi m verilirse b'ler ondan (karıştırma için)
function pencereler(ol, n, Mc, m) {
  const K = Math.floor(ol.length / n), w = [];
  for (let k = 0; k < K; k++) { const s = k * n, e = s + n, mags = (m || ol.map(o => o.m)).slice(s, e), T = (ol[e - 1].t - ol[s].t) / YIL, A = X.aWinValue(n, T);
    w.push({ t0: ol[s].t, t1: ol[e - 1].t, a: A ? A.a : null, b: X.computeBvalue(mags, Mc, 0.1), mcW: m ? null : X.computeMcSrc(mags.map(v => ({ mag: v }))) }); }
  return w; }
function olcu(w, maske) {   // maske: fark i (pencere i → i+1) kullanılsın mı
  const a = w.map(q => q.a), b = w.map(q => q.b), da = fark(a), db = fark(b), sec = (v) => maske ? v.filter((_, i) => maske[i]) : v;
  const x = sec(da), y = sec(db);
  return { r: pearson(x, y), rs: x.length >= 3 ? pearson(sira(x), sira(y)) : null, nFark: x.length, gec: [-2, -1, 0, 1, 2].map(L => maske ? null : gecikmeli(da, db, L)), d4: dortlu(da, db, maske), rDuzey: pearson(a, b), da, db }; }
function senaryo(ol, n, Mc, perm = NPERM, seed = 2026) {
  const w = pencereler(ol, n, Mc); if (w.length < 6 || w.some(q => q.a === null || q.b === null)) return { yetersiz: true, nOlay: ol.length, nPencere: w.length };
  const O = olcu(w), eksik = w.map(q => q.mcW !== null && q.mcW > Mc + 0.2 + 1e-9), maske = O.da.map((_, i) => !eksik[i] && !eksik[i + 1]), Om = olcu(w, maske);
  // n_eff (uygulamanın yöntemi): fark serilerinin gecikme-1 öz-ilişkisi, tek segment
  const rhoA = X.aLag1([O.da], v => v), rhoB = X.aLag1([O.db], v => v), ne = O.r !== null ? X.aNeffTest(O.r, O.nFark, rhoA ? rhoA.r : null, rhoB ? rhoB.r : null) : null;
  // Büyüklük karıştırma
  const r = rng(seed), mags = ol.map(o => o.m), perm0 = [], permG = [[], [], [], [], []], permM = [], permD = [], permQ = { '++': 0, '+-': 0, '-+': 0, '--': 0 };
  for (let p = 0; p < perm; p++) { const m = mags.slice(); for (let i = m.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)), t = m[i]; m[i] = m[j]; m[j] = t; }
    const wp = pencereler(ol, n, Mc, m).map((q, i) => ({ ...q, a: w[i].a })); if (wp.some(q => q.b === null)) continue;
    const P = olcu(wp); perm0.push(P.r); P.gec.forEach((v, i) => permG[i].push(v)); permD.push(P.rDuzey); for (const k in permQ) permQ[k] += P.d4[k];
    if (Om.nFark >= 5) permM.push(olcu(wp, maske).r); }
  const pp = (obs, arr) => obs === null || !arr.length ? null : (1 + arr.filter(v => v !== null && Math.abs(v) >= Math.abs(obs) - 1e-12).length) / (arr.length + 1);
  const q = (arr, f) => { const s = arr.filter(v => v !== null).sort((a, b) => a - b); return s.length ? s[Math.floor(f * (s.length - 1))] : null; };
  const span = w.map(v => (v.t1 - v.t0) / YIL).sort((a, b) => a - b);
  return { nOlay: ol.length, nPencere: w.length, nFark: O.nFark, pencereSureMedyanYil: span[Math.floor(span.length / 2)], aSd: sd(w.map(v => v.a)), bSd: sd(w.map(v => v.b)),
    r: O.r, rs: O.rs, pPerm: pp(O.r, perm0), permAralik: [q(perm0, 0.025), q(perm0, 0.975)], permOrt: perm0.reduce((s, v) => s + v, 0) / perm0.length, nPerm: perm0.length,
    neff: ne, rhoDa: rhoA ? rhoA.r : null, rhoDb: rhoB ? rhoB.r : null,
    gecikme: [-2, -1, 0, 1, 2].map((L, i) => ({ L, r: O.gec[i], p: pp(O.gec[i], permG[i]) })),
    dortlu: O.d4, dortluBeklenen: Object.fromEntries(Object.entries(permQ).map(([k, v]) => [k, +(v / perm0.length).toFixed(1)])),
    rDuzey: O.rDuzey, pDuzey: pp(O.rDuzey, permD),
    eksik: { nPencere: eksik.filter(Boolean).length, r: Om.r, nFark: Om.nFark, p: Om.nFark >= 5 ? pp(Om.r, permM) : null },
    pencereler: w.map(v => ({ t0: new Date(v.t0).toISOString().slice(0, 10), t1: new Date(v.t1).toISOString().slice(0, 10), a: +v.a.toFixed(4), b: +v.b.toFixed(4), mcW: v.mcW })) }; }
function sd(v) { const m = v.reduce((a, x) => a + x, 0) / v.length; return Math.sqrt(v.reduce((a, x) => a + (x - m) ** 2, 0) / (v.length - 1)); }
function holm(p) { const m = p.length, o = p.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]), q = new Array(m); let run = 0; o.forEach(([v, i], k) => { run = Math.max(run, Math.min(1, v * (m - k))); q[i] = run; }); return q; }
module.exports = { pencereler, olcu, senaryo, fark, pearson, holm, X };
if (require.main === module) {
const V = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')), R = { girdi: V.uretim, kurallar: 'analiz.js başlığı', senaryolar: {}, birincil: null };
const DON = { MD: [Y(1998), Y(2011)], ML: [Y(2012), Infinity] };
for (const sen of ['tr_emsc', 'mar_emsc']) for (const gk of [1, 0]) for (const Mc of [3.2, 3.5, 4.0]) for (const n of [50, 100, 200]) for (const [d, [t0, t1]] of Object.entries(DON)) {
  const ol = V.senaryolar[sen].olaylar.filter(e => (!gk || e.gk) && e.m >= Mc - 1e-9 && e.t >= t0 && e.t < t1).sort((a, b) => a.t - b.t);
  const k = `${sen}|${gk ? 'gk74' : 'ham'}|Mc${Mc.toFixed(1)}|n${n}|${d}`; R.senaryolar[k] = senaryo(ol, n, Mc); }
{ const ol = V.senaryolar.tr_emsc.olaylar.filter(e => e.gk && e.m >= 3.5 - 1e-9).sort((a, b) => a.t - b.t); R.senaryolar['tr_emsc|gk74|Mc3.5|n100|KESEN'] = senaryo(ol, 100, 3.5); }
{ const ad = ['tr_emsc|gk74|Mc3.5|n100|MD', 'tr_emsc|gk74|Mc3.5|n100|ML'], p = ad.map(a => R.senaryolar[a].pPerm), q = holm(p);
  R.birincil = ad.map((a, i) => ({ senaryo: a, r: R.senaryolar[a].r, pPerm: p[i], pHolm: q[i], nFark: R.senaryolar[a].nFark })); }
fs.writeFileSync(path.join(__dirname, 'sonuc.json'), JSON.stringify(R, null, 1));
const f = (v, d = 2) => v === null || v === undefined || !Number.isFinite(v) ? '—' : v.toFixed(d), pp = v => v === null || v === undefined ? '—' : v < 0.001 ? v.toExponential(1) : v.toFixed(3);
console.log('══ BİRİNCİL (GK74, Mc 3,5, n 100, Türkiye; Holm m = 2) ══'); R.birincil.forEach(b => console.log(`  ${b.senaryo}: r(Δa, Δb) ${f(b.r)} (${b.nFark} fark), p_karıştırma ${pp(b.pPerm)}, Holm ${pp(b.pHolm)}`));
console.log('\n══ TÜM SENARYOLAR ══');
for (const [k, s] of Object.entries(R.senaryolar)) { if (s.yetersiz) { console.log(`  ${k.padEnd(34)} YETERSİZ (${s.nOlay} olay, ${s.nPencere} pencere)`); continue; }
  console.log(`  ${k.padEnd(34)} ${String(s.nPencere).padStart(3)} pnc (medyan ${f(s.pencereSureMedyanYil, 2)} yıl) | r ${f(s.r).padStart(5)} rs ${f(s.rs).padStart(5)} p_k ${pp(s.pPerm).padStart(7)} [sıfır %95 ${f(s.permAralik[0])}, ${f(s.permAralik[1])}] p_neff ${pp(s.neff && s.neff.p).padStart(7)} | düzey r ${f(s.rDuzey).padStart(5)} p ${pp(s.pDuzey)} | eksik pnc ${s.eksik.nPencere}, r ${f(s.eksik.r)} p ${pp(s.eksik.p)} | gecikme ${s.gecikme.map(g => `${g.L}:${f(g.r)}${g.p !== null && g.p < 0.05 ? '*' : ''}`).join(' ')} | 4lü ${JSON.stringify(s.dortlu)} bekl ${JSON.stringify(s.dortluBeklenen)}`); }
}
