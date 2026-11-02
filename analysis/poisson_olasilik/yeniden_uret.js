// Yeniden üretim betiği (aşama 4, 2026-11-01). Uygulamadan indirilen "Yeniden üretim (JSON)" kaydını okur. Kayıttaki girdilerden
// N(≥Mc), b, a, λ, P ve bootstrap aralıklarını uygulamanın KENDİ fonksiyonlarıyla (index.html'den okunur, kopya tutulmaz) yeniden hesaplar,
// kayıttaki sonuçlarla karşılaştırır.
// Denetimler:
//   (1) Yazılım kimliği: depodaki index.html'in git blob SHA-1'i = kayıttaki. Eşleşmezse önce kayıttaki commit'e geçin
//       (git log --all --find-object=<sha>). Sayılar yine hesaplanır; eşleşmeme uyarı olarak raporlanır.
//   (2) Katalog kimliği: kayıttaki dosyaların git blob SHA-1'i, depodaki dosyalarla karşılaştırılır (bilgi; canlı sorgularda dosya yoktur).
//   (3) Girdi büyüklükleri: SHA-256 kayıttakiyle aynı.
//   (4) N(≥Mc), T, b, σ_b, a ve Mmax,gözl. aynı.
//   (5) Her (M, t) hücresinde λ, P, %95 ve 16.–84. yüzdelik sınırları, Tr, Tr/T ve ekstrapolasyon sınıfı aynı (göreli fark ≤ 1e-12).
// Kullanım (depo kökünde): node analysis/poisson_olasilik/yeniden_uret.js <kayıt.json> [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..', '..'), dosya = process.argv[2], idx = process.argv[3] || path.join(ROOT, 'index.html');
if (!dosya) { console.error('kullanım: node yeniden_uret.js <kayıt.json> [index.html]'); process.exit(2); }
const K = JSON.parse(fs.readFileSync(dosya, 'utf8'));
const blob = buf => crypto.createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${buf.length}\0`), buf])).digest('hex');
const srcBuf = fs.readFileSync(idx), src = srcBuf.toString('utf8').replace(/\r\n/g, '\n');
const fn = n => { const i = src.indexOf('\nfunction ' + n + '('); if (i < 0) throw new Error('bulunamadı: ' + n); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const line = re => { const m = src.match(re); if (!m) throw new Error('bulunamadı: ' + re); return m[0].replace(/^const /, 'var '); };
let pass = 0, fail = 0, uyari = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); }, uy = m => { uyari++; console.log('UYARI ' + m); };
// (1) yazılım
{ const b = blob(srcBuf), k = K.yazilim && K.yazilim.index_html_git_blob_sha1;
  if (k && b === k) ok(true, `(1) index.html git blob ${b.slice(0, 12)} = kayıttaki${K.yazilim.commit ? ` (commit ${K.yazilim.commit.slice(0, 10)})` : ''}`);
  else uy(`(1) index.html git blob ${b.slice(0, 12)} ≠ kayıttaki ${k ? k.slice(0, 12) : '—'}: kayıttaki sürüme geçin (git log --all --find-object=${k || '<sha>'}); hesap yine de denenir`); }
// bağlam: kayıttaki ayarlar
const A = K.ayarlar;
// Bağımlılıklar: uygulama fonksiyonları index.html'den alınır; deneme hesabında "X is not defined" çıkarsa X (fonksiyon ya da tek satırlık
// const/let) eklenir ve bağlam yeniden kurulur (kopya tutulmaz; hangi fonksiyonların kullanıldığı çıktıda listelenir).
const adlar = ['mulberry32', 'logGamma', 'poissonSample', 'gammaSample', 'grBootDraws', 'bGridRound', 'bGridOffCount', 'bGridVals', 'computeBvalue', 'bConfidence95', 'bCiFields',
  'grPoissonP', 'grLambdaSimple', 'grPctl', 'cmpStats', 'cmpProbBoot', 'cmpProbAt', 'cmpProb', 'cmpProbExtrap', 'cmpProbMk'], ekSatir = [];
function kur() {
  const c = { document: { getElementById: id => id === 'cmpUnit' ? { value: A.birim } : null }, B_CI_METHOD: A.b_aralik_yontemi, B_GRID_MODE: A.b_izgara_kipi }; vm.createContext(c);
  vm.runInContext([line(/^const GR_POIS = [^\n]*$/m), line(/^const GR_QC = [^\n]*$/m), line(/^const CMP_PROB = [^\n]*$/m), ...ekSatir, ...adlar.map(fn), 'var cmpProbCache = new Map();'].join('\n'), c);
  vm.runInContext(src.match(/^const LANCZOS_C = \[[\s\S]*?\];$/m)[0].replace(/^const /, 'var '), c);
  Object.assign(c.GR_POIS, { B: A.bootstrap.B, seed: A.bootstrap.tohum }); c.CMP_PROB.exK = A.olasilik.exK; return c; }
let ctx = null;
for (let k = 0; k < 60; k++) { ctx = kur(); const B0 = K.bolgeler.find(b => b.girdi_buyukluklar); if (!B0) break;
  try { const r = { t0: B0.donem.t0_ms, t1: B0.donem.t1_ms, area: B0.bolge.alan_km2, cLat: B0.bolge.merkez_enlem, mags: B0.girdi_buyukluklar.slice(0, 2000), Mc: B0.Mc, dm: B0.dM }, s = ctx.cmpStats(r); ctx.cmpProb(r, s).cell(6, 10); ctx = kur(); break; }
  catch (e) { const m = /^(\w+) is not defined/.exec(e.message); if (!m) throw e; const ad = m[1];
    if (src.includes('\nfunction ' + ad + '(')) adlar.push(ad); else { const t = src.match(new RegExp('^(?:const|let) ' + ad + ' = [^\\n]*$', 'm')); if (!t) throw e; ekSatir.push(t[0].replace(/^(const|let) /, 'var ')); } } }
console.log(`index.html'den okunan fonksiyonlar (${adlar.length}): ${adlar.join(', ')}${ekSatir.length ? ' + ' + ekSatir.length + ' sabit' : ''}`);
const esit = (x, y, tol = 1e-12) => (x === null || x === undefined) ? (y === null || y === undefined) : (y !== null && y !== undefined && (x === y || Math.abs(x - y) <= tol * Math.max(1, Math.abs(x), Math.abs(y))));
for (const B of K.bolgeler) {
  console.log(`\n── (${B.panel}) ${B.ad} — ${B.katalog.kaynak || ''}; ${B.donem.t0.slice(0, 10)} – ${B.donem.t1.slice(0, 10)}`);
  // (2) katalog
  if (B.katalog.blob) for (const [f, sha] of Object.entries(B.katalog.blob)) { const p = path.join(ROOT, f);
    if (!fs.existsSync(p)) uy(`(2) ${f} depoda yok`); else { const b = blob(fs.readFileSync(p)); b === sha ? ok(true, `(2) ${f} git blob ${b.slice(0, 12)} = kayıttaki (katalog üretimi ${B.katalog.uretim || '—'})`) : uy(`(2) ${f} depodaki sürüm farklı (${b.slice(0, 12)} ≠ ${String(sha).slice(0, 12)}): kayıttaki sürüm için git log --all --find-object=${sha}`); } }
  else uy(`(2) katalog dosya kimliği yok (${B.katalog.tur}); girdi büyüklükleri kayıttan kullanılıyor`);
  if (!B.girdi_buyukluklar) { ok(false, '(3) kayıtta girdi büyüklükleri yok (SVG özeti tam kayıt değildir; JSON kullanın)'); continue; }
  // (3) büyüklükler
  const ms = B.girdi_buyukluklar.slice().sort((a, b) => a - b).map(m => m.toFixed(2)).join(','), h = crypto.createHash('sha256').update(ms).digest('hex');
  ok(h === B.girdi_buyukluk_sha256 && B.girdi_buyukluklar.length === B.N_tum, `(3) girdi büyüklükleri: ${B.N_tum} olay, SHA-256 ${h.slice(0, 12)} = kayıttaki`);
  // (4) parametreler
  const r = { t0: B.donem.t0_ms, t1: B.donem.t1_ms, area: B.bolge.alan_km2, cLat: B.bolge.merkez_enlem, mags: B.girdi_buyukluklar, Mc: B.Mc, dm: B.dM }, s = ctx.cmpStats(r);
  ok(s.n === B.N_geMc && esit(s.T, B.donem.T_yil) && esit(s.b, B.b) && esit(s.sb, B.sigma_b) && esit(s.a, B.a) && esit(s.Mmax, B.Mmax_gozl),
    `(4) N(≥Mc) = ${s.n}, T = ${s.T.toFixed(3)} yıl, b = ${s.b.toFixed(4)}, a = ${s.a.toFixed(4)} (${B.a_birim}), Mmax,gözl. = ${s.Mmax}`);
  // (5) sonuçlar
  if (!B.sonuc) { uy('(5) kayıtta sonuç tablosu yok'); continue; }
  const est = (A.b_kestiricisi && A.b_kestiricisi.secili) || 'aki', p = ctx.cmpProb(r, s, est);
  if (B.b_Bender !== undefined) ok(esit(s.bB, B.b_Bender) && esit(p.b, B.b_olasilikta), `(4) b kestiricisi (olasılıkta): ${est}; b_Bender = ${s.bB.toFixed(4)}, olasılıkta kullanılan b = ${p.b.toFixed(4)} — kayıttakiyle aynı`); let uyan = 0, ilk = null;
  for (const c of B.sonuc) { const q = p.cell(c.M, c.t), ayni = esit(q.lam, c.lambda) && esit(q.P, c.P) && esit(q.lo, c.alt95) && esit(q.hi, c.ust95) && esit(q.l16, c.y16) && esit(q.h84, c.y84) && esit(q.tr, c.Tr_yil) && esit(q.trT, c.Tr_T) && q.exC === c.ekstrapolasyon && q.ex === c.M_gt_Mmax_gozl;
    if (ayni) uyan++; else if (!ilk) ilk = `M ≥ ${c.M}, t = ${c.t}: P ${q.P} / ${c.P}, %95 [${q.lo}, ${q.hi}] / [${c.alt95}, ${c.ust95}]`; }
  ok(uyan === B.sonuc.length && p.bt.B === B.bootstrap.B && p.bt.nFail === B.bootstrap.kurulamayan, `(5) ${B.sonuc.length} hücrenin ${uyan}'i aynı (λ, P, %95, 16.–84., Tr, Tr/T, sınıf); B = ${p.bt.B}, tohum ${p.bt.seed}, b: ${est}${ilk ? ' — ilk fark: ' + ilk : ''}`);
  const c7 = B.sonuc.find(c => c.M === 7 && c.t === 50); if (c7) console.log(`     örnek: P(≥7; 50 yıl) = %${(100 * c7.P).toFixed(2)} [%95 ${(100 * c7.alt95).toFixed(2)}–${(100 * c7.ust95).toFixed(2)}], Tr = ${c7.Tr_yil.toFixed(1)} yıl (${c7.ekstrapolasyon})`);
}
console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı, ${uyari} uyarı`); process.exit(fail ? 1 : 0);
