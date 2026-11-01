// Büyüklük türü geçişi (MD → ML) — araştırma analizi (2026-11-01). Girdi: disa_aktar.js çıktısı (uygulamanın kendi kodu: bölge, GK74) ve
// data/eq_marmara_emsc_ml20.txt (yalnız okunur; büyüklük yazarı sütunu). Çıktı: sonuc.json + konsol özeti. index.html ve data/ değişmez.
// SORULAR VE KURALLAR (tür bileşimi görüldükten sonra, aşağıdaki sonuçlar görülmeden yazıldı):
//   1. Geçiş penceresi: M ≥ 3,0 olaylarında baskın türün payı ≥ %80 olmayan yıllar 'geçiş yılı'. Tür dizgisi büyük/küçük harf korunarak da
//      raporlanır ('ML' EMSC'nin kendi ML'si, 'ml' katkıcının ML'si).
//   2. Homojen tür dönemleri: MD 2004–2009 (1999 İzmit–Düzce dizisini dışarıda bırakır), ML 2013–2018 (geçişi ve 2023 dizisini dışarıda bırakır);
//      6'şar tam yıl. GK74 açık (ana) ve kapalı.
//   3. Mc yeniden değerlendirmesi: MAXC (uygulamanın computeMcSrc'si: en büyük eğrilik + 0,2), GFT (Wiemer & Wyss 2000; birikimli, R ≥ %90 ve %95
//      ilk Mc), MBS (Cao & Gao 2002; Woessner & Wiemer 2005 biçimi: |b_ort(Mc…Mc+0,5) − b(Mc)| ≤ δb, δb Shi & Bolt 1982). Aday Mc 3,0–4,5,
//      en az 50 olay. b: Aki (1965), ΔM = 0,1 (Utsu düzeltmesi Mc − 0,05).
//   4. Ölçek karşılığı (sabit kayma varsaymadan): ML dönemindeki yıllık hız λ_ML(≥M) için MD döneminde aynı yıllık hızı veren M' bulunur
//      (log λ_MD doğrusal ara değerle), Δ(M) = M − M'. VARSAYIM: iki dönem arasında gerçek sismisite hızı ve algılama değişmedi; bu varsayım
//      sınanamaz, sonuç bir ölçek kalibrasyonu değil, 'görünür' karşılıktır. Belirsizlik: dönem içi olayların yeniden örneklenmesi (bootstrap,
//      2000 çekiliş, tohum 2026; GK74 sonrası olaylar bağımsız sayılır). Sabit kayma sınaması: Δ(M)'nin eşikler boyunca eğimi.
//   5. 2010–2012 geçiş yıllarında türlerin mekânsal dağılımı (boylam), türlerin aynı popülasyondan örnek olup olmadığını görmek için.
// Kullanım (depo kökünde): node analysis/tur_gecisi/analiz.js <disa_aktar çıktısı.json>
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..', '..');
// Uygulamanın Mc fonksiyonu (dönüşüm yokken computeMc ≡ computeMcSrc), index.html'den okunur
const src = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fnCut = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const X = {}; vm.createContext(X); vm.runInContext(['mcSrcMag', 'computeMcSrc'].map(fnCut).join('\n'), X);
const maxc = mags => X.computeMcSrc(mags.map(m => ({ mag: m })));
const LOG10E = Math.LOG10E, DM = 0.1, YIL = 365.25 * 864e5, Y = y => Date.UTC(y, 0, 1);
const r1 = v => Math.round(v * 10) / 10;
function akiB(mags, Mc) { const s = mags.filter(m => m >= Mc - 1e-9); if (s.length < 10) return null; const mu = s.reduce((a, v) => a + v, 0) / s.length;
  const b = LOG10E / (mu - (Mc - DM / 2)), sb = 2.3 * b * b * Math.sqrt(s.reduce((a, v) => a + (v - mu) ** 2, 0) / (s.length * (s.length - 1)));   // Shi & Bolt (1982)
  return { b, sb, n: s.length }; }
function gft(mags, Mc) {   // Wiemer & Wyss (2000): birikimli gözlenen ve G–R öngörüsü, Mc'den en büyük bine
  const s = mags.filter(m => m >= Mc - 1e-9); if (s.length < 50) return null; const B = akiB(mags, Mc), mx = Math.max(...s), N = s.length; let num = 0, den = 0;
  for (let M = Mc; M <= mx + 1e-9; M = r1(M + DM)) { const obs = s.filter(m => m >= M - 1e-9).length, pre = N * Math.pow(10, -B.b * (M - Mc)); num += Math.abs(obs - pre); den += obs; }
  return 100 - 100 * num / den; }
function mcYontem(mags) {
  const ad = []; for (let M = 3.0; M <= 4.5 + 1e-9; M = r1(M + DM)) { const B = akiB(mags, M); if (B && B.n >= 50) ad.push({ M, ...B, R: gft(mags, M) }); }
  const gft90 = ad.find(a => a.R >= 90), gft95 = ad.find(a => a.R >= 95);
  const mbs = ad.find((a, i) => { const w = ad.slice(i, i + 6); if (w.length < 6) return false; const bo = w.reduce((s, v) => s + v.b, 0) / w.length; return Math.abs(bo - a.b) <= a.sb; });
  return { MAXC: maxc(mags), GFT90: gft90 ? gft90.M : null, GFT95: gft95 ? gft95.M : null, MBS: mbs ? mbs.M : null, adaylar: ad.map(a => ({ M: a.M, b: +a.b.toFixed(3), sb: +a.sb.toFixed(3), n: a.n, R: a.R === null ? null : +a.R.toFixed(1) })) }; }
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
// Hız eşleştirmesi: ML dönemi eşiği M için MD döneminde aynı yıllık hızı veren M'
const sayGe = (srt, x) => { let lo = 0, hi = srt.length; while (lo < hi) { const m = (lo + hi) >> 1; if (srt[m] < x - 1e-9) lo = m + 1; else hi = m; } return srt.length - lo; };   // srt artan sıralı
function esdeger(mdM, TMD, mlM, TML, M) {   // girdiler artan sıralı; M 0,1 ızgarasında. MD'nin log-hızı 0,1 ızgara noktaları (2,9 = kesimin
  // hemen altı değil: 3,0 ilk tam nokta) arasında doğrusal ara değerle (basamaklı birikimli sayımın kuantizasyonundan kaçınmak için)
  const lamML = sayGe(mlM, M) / TML; if (!(lamML > 0)) return null;
  let x0 = 3.0, l0 = sayGe(mdM, x0) / TMD; if (l0 < lamML) return null;   // katalog kesimi 3,0: MD ≥ 3,0'ın hızı ML hızından düşükse karşılık kesimin altında
  for (let k = 31; k <= 70; k++) { const x1 = k / 10, l1 = sayGe(mdM, x1) / TMD;
    if (l1 <= lamML) { if (l1 === 0) return null; if (l0 === l1) return x0; const f = (Math.log(lamML) - Math.log(l0)) / (Math.log(l1) - Math.log(l0)); return x0 + f * (x1 - x0); }
    x0 = x1; l0 = l1; }
  return null; }
module.exports = { akiB, gft, mcYontem, esdeger, sayGe };
if (require.main === module) {
const V = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')), R = { girdi: V.uretim, kurallar: 'analiz.js başlığı', bilesim: {}, yazar: {}, gecisYillari: {}, mc: {}, b: {}, karsilik: {}, mekan: {} };
const yil = e => new Date(e.t).getUTCFullYear();
// 1. Yıllık bileşim (M ≥ 3,0 ve M ≥ 4,0), tür dizgisi büyük/küçük harf korunarak ve birleşik türle
for (const sen of ['tr_emsc', 'mar_emsc']) { const ev = V.senaryolar[sen].olaylar; R.bilesim[sen] = {}; R.gecisYillari[sen] = [];
  for (let y = 1998; y <= 2025; y++) { const o = {};
    for (const M of [3.0, 4.0]) { const s = ev.filter(e => yil(e) === y && e.m >= M - 1e-9), c = {}, ct = {}; s.forEach(e => { c[e.mt] = (c[e.mt] || 0) + 1; ct[e.tur] = (ct[e.tur] || 0) + 1; });
      const pay = k => Object.fromEntries(Object.entries(k).sort((a, b) => b[1] - a[1]).map(([t, v]) => [t, +(100 * v / s.length).toFixed(1)]));
      o['M≥' + M.toFixed(1)] = { n: s.length, tur: pay(ct), dizgi: pay(c) }; }
    R.bilesim[sen][y] = o; const d = o['M≥3.0'], ust = Math.max(...Object.values(d.tur));
    if (d.n >= 20 && ust < 80) R.gecisYillari[sen].push({ y, n: d.n, tur: d.tur, dizgi: d.dizgi }); } }
// Marmara: büyüklük yazarı (ham metin dosyası; sütun 12), M ≥ 3,0, 1998–2025
{ const by = {}; for (const l of fs.readFileSync(path.join(ROOT, 'data', 'eq_marmara_emsc_ml20.txt'), 'utf8').split('\n')) { const f = l.split('|'); if (f.length < 13 || !/^\d{4}/.test(f[1])) continue;
    const y = +f[1].slice(0, 4), m = +f[10]; if (y < 1998 || y > 2025 || !(m >= 3.0 - 1e-9)) continue; const k = `${f[9]}/${f[11]}`; by[y] = by[y] || {}; by[y][k] = (by[y][k] || 0) + 1; }
  for (const y of Object.keys(by)) { const n = Object.values(by[y]).reduce((a, v) => a + v, 0); R.yazar[y] = { n, pay: Object.fromEntries(Object.entries(by[y]).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([k, v]) => [k, +(100 * v / n).toFixed(1)])) }; } }
// 2–3. Homojen tür dönemleri: Mc yöntemleri ve b
const DON = { MD: { yy: [2004, 2009], tur: 'MD' }, ML: { yy: [2013, 2018], tur: 'ML' } };
const donemOlay = (ev, D, gk, yalnizTur) => ev.filter(e => yil(e) >= D.yy[0] && yil(e) <= D.yy[1] && (!gk || e.gk) && (!yalnizTur || e.tur === D.tur));
for (const sen of ['tr_emsc', 'mar_emsc']) for (const gk of [1, 0]) { const ev = V.senaryolar[sen].olaylar, g = gk ? 'gk74' : 'ham';
  for (const [k, D] of Object.entries(DON)) { const tum = donemOlay(ev, D, gk, false).map(e => e.m), tek = donemOlay(ev, D, gk, true).map(e => e.m), ad = `${sen}|${g}|${k}`;
    R.mc[ad] = { n: tum.length, nTur: tek.length, turPay: +(100 * tek.length / tum.length).toFixed(1), tum: mcYontem(tum), yalnizTur: mcYontem(tek) };
    { const c = {}, s4 = donemOlay(ev, D, gk, false).filter(e => e.m >= 4.0 - 1e-9); s4.forEach(e => { c[e.tur] = (c[e.tur] || 0) + 1; });
      R.mc[ad].M4 = { n: s4.length, tur: Object.fromEntries(Object.entries(c).sort((a, b) => b[1] - a[1]).map(([t, v]) => [t, +(100 * v / s4.length).toFixed(1)])) };
      const c35 = {}, s35 = donemOlay(ev, D, gk, false).filter(e => e.m >= 3.5 - 1e-9 && e.m < 4.0 - 1e-9); s35.forEach(e => { c35[e.tur] = (c35[e.tur] || 0) + 1; });
      R.mc[ad].M35_40 = { n: s35.length, tur: Object.fromEntries(Object.entries(c35).sort((a, b) => b[1] - a[1]).map(([t, v]) => [t, +(100 * v / s35.length).toFixed(1)])) }; }
    R.b[ad] = Object.fromEntries([3.0, 3.5, 4.0].map(M => { const B = akiB(tum, M); return [M.toFixed(1), B ? { b: +B.b.toFixed(3), sb: +B.sb.toFixed(3), n: B.n } : null]; })); } }
// 4. Görünür ölçek karşılığı (GK74, yalnız baskın tür; ham ile duyarlılık)
const ESIK = [3.3, 3.5, 3.7, 3.9, 4.1, 4.3, 4.5, 4.7];
for (const sen of ['tr_emsc', 'mar_emsc']) for (const gk of [1, 0]) for (const yt of [false, true]) { const ev = V.senaryolar[sen].olaylar, g = gk ? 'gk74' : 'ham';
  const srt = a => a.slice().sort((x, y) => x - y), md = srt(donemOlay(ev, DON.MD, gk, yt).map(e => e.m)), ml = srt(donemOlay(ev, DON.ML, gk, yt).map(e => e.m)), T = 6;   // 6'şar tam yıl
  const nokta = ESIK.map(M => { const e = esdeger(md, T, ml, T, M), nML = sayGe(ml, M); return { M, nML, MD: e, fark: e === null ? null : M - e }; });
  const r = rng(2026), bs = ESIK.map(() => []), egim = [];
  for (let i = 0; i < 2000; i++) { const a = srt(md.map(() => md[Math.floor(r() * md.length)])), b = srt(ml.map(() => ml[Math.floor(r() * ml.length)]));
    const v = ESIK.map(M => esdeger(a, T, b, T, M)); v.forEach((x, j) => { if (x !== null) bs[j].push(ESIK[j] - x); });
    const p = v.map((x, j) => [ESIK[j], x]).filter(q => q[1] !== null && nokta.find(n => n.M === q[0]).nML >= 10);
    if (p.length >= 3) { const mx = p.reduce((s, q) => s + q[0], 0) / p.length, my = p.reduce((s, q) => s + (q[0] - q[1]), 0) / p.length;
      egim.push(p.reduce((s, q) => s + (q[0] - mx) * ((q[0] - q[1]) - my), 0) / p.reduce((s, q) => s + (q[0] - mx) ** 2, 0)); } }
  const q = (a, f) => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[Math.min(s.length - 1, Math.floor(f * s.length))] : null; };
  nokta.forEach((n, j) => { n.alt = q(bs[j], 0.025); n.ust = q(bs[j], 0.975); n.nBoot = bs[j].length; });
  const pp = nokta.filter(n => n.fark !== null && n.nML >= 10), mx = pp.reduce((s, n) => s + n.M, 0) / pp.length, my = pp.reduce((s, n) => s + n.fark, 0) / pp.length;
  const e0 = pp.length >= 3 ? pp.reduce((s, n) => s + (n.M - mx) * (n.fark - my), 0) / pp.reduce((s, n) => s + (n.M - mx) ** 2, 0) : null;
  R.karsilik[`${sen}|${g}|${yt ? 'yalnizTur' : 'tum'}`] = { nMD: md.length, nML: ml.length, nokta, egim: e0, egimAlt: q(egim, 0.025), egimUst: q(egim, 0.975), egimNBoot: egim.length,
    sabitKaymaUyumlu: egim.length ? (q(egim, 0.025) <= 0 && q(egim, 0.975) >= 0) : null }; }
// 5. Geçiş yıllarında türlerin mekânsal dağılımı (Türkiye, M ≥ 3,0, ham)
{ const ev = V.senaryolar.tr_emsc.olaylar;
  for (const y of [2010, 2011, 2012]) { const o = {}; const s = ev.filter(e => yil(e) === y);
    for (const t of [...new Set(s.map(e => e.mt))]) { const x = s.filter(e => e.mt === t); if (x.length < 30) continue; const lon = x.map(e => e.lon).sort((a, b) => a - b), q = f => lon[Math.floor(f * (lon.length - 1))];
      o[t] = { n: x.length, lonMedyan: +q(0.5).toFixed(2), lonQ1: +q(0.25).toFixed(2), lonQ3: +q(0.75).toFixed(2), dogu42: +(100 * x.filter(e => e.lon >= 42).length / x.length).toFixed(1) }; }
    R.mekan[y] = o; } }
fs.writeFileSync(path.join(__dirname, 'sonuc.json'), JSON.stringify(R, null, 1));
// ── Özet ──
const f = (v, d = 2) => v === null || v === undefined || !Number.isFinite(v) ? '—' : v.toFixed(d);
console.log('══ GEÇİŞ YILLARI (M ≥ 3,0; baskın tür < %80) ══'); for (const [s, a] of Object.entries(R.gecisYillari)) a.forEach(o => console.log(`  ${s} ${o.y}: n ${o.n} tür ${JSON.stringify(o.tur)} dizgi ${JSON.stringify(o.dizgi)}`));
console.log('\n══ TÜRKİYE BİLEŞİMİ 2008–2014 (M ≥ 3,0 dizgi | M ≥ 4,0 tür) ══'); for (let y = 2008; y <= 2014; y++) { const o = R.bilesim.tr_emsc[y]; console.log(`  ${y}: ${JSON.stringify(o['M≥3.0'].dizgi)} | M≥4: n ${o['M≥4.0'].n} ${JSON.stringify(o['M≥4.0'].tur)}`); }
console.log('\n══ MARMARA YAZAR (tür/yazar, M ≥ 3,0) 2009–2013 ══'); for (let y = 2009; y <= 2013; y++) console.log(`  ${y}: n ${R.yazar[y].n} ${JSON.stringify(R.yazar[y].pay)}`);
console.log('\n══ Mc YÖNTEMLERİ (tüm olaylar | yalnız baskın tür) ══'); for (const [k, v] of Object.entries(R.mc)) console.log(`  ${k.padEnd(18)} n ${v.n} (tür %${v.turPay}) | MAXC ${v.tum.MAXC} GFT90 ${v.tum.GFT90} GFT95 ${v.tum.GFT95} MBS ${v.tum.MBS} | tür: MAXC ${v.yalnizTur.MAXC} GFT90 ${v.yalnizTur.GFT90} GFT95 ${v.yalnizTur.GFT95} MBS ${v.yalnizTur.MBS}`);
console.log('\n══ TÜR PAYI: 3,5 ≤ M < 4,0 | M ≥ 4,0 ══'); for (const [k, v] of Object.entries(R.mc)) console.log(`  ${k.padEnd(18)} ${JSON.stringify(v.M35_40)} | ${JSON.stringify(v.M4)}`);
console.log('\n══ b (Aki, tüm olaylar) ══'); for (const [k, v] of Object.entries(R.b)) console.log(`  ${k.padEnd(18)} ${Object.entries(v).map(([M, x]) => `Mc ${M}: ${x ? `${f(x.b)} ± ${f(x.sb)} (n ${x.n})` : '—'}`).join(' | ')}`);
console.log('\n══ GÖRÜNÜR KARŞILIK: ML eşiği → aynı yıllık hızı veren MD büyüklüğü (Δ = ML − MD) ══');
for (const [k, v] of Object.entries(R.karsilik)) { console.log(`  ${k} (n MD ${v.nMD}, ML ${v.nML}); Δ'nın M'ye eğimi ${f(v.egim)} [${f(v.egimAlt)}, ${f(v.egimUst)}] → sabit kaymayla ${v.sabitKaymaUyumlu ? 'uyumlu' : 'UYUMSUZ'}`);
  v.nokta.forEach(n => console.log(`    ML ≥ ${n.M.toFixed(2)} (n ${n.nML}) ↔ MD ≥ ${f(n.MD)}; Δ ${f(n.fark)} [${f(n.alt)}, ${f(n.ust)}]`)); }
console.log('\n══ GEÇİŞ YILLARINDA MEKÂN (Türkiye, boylam) ══'); for (const [y, o] of Object.entries(R.mekan)) for (const [t, x] of Object.entries(o)) console.log(`  ${y} ${t.padEnd(3)} n ${x.n} boylam medyan ${x.lonMedyan} [${x.lonQ1}–${x.lonQ3}] 42°D doğusu %${x.dogu42}`);
}
