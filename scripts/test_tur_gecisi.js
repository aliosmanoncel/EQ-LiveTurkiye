// Birim testleri: büyüklük türü geçişi uyarısı (2026-11-01). index.html'den TUR_QC, turNorm, turYillik, turGecisDurum, turUyariHtml okunur.
// Denetimler: geçiş algılama (baskın tür ≥ %60, yıllık ≥ 20 olay), karışık yıllar, az olaylı yılların yok sayılması, A → B → A, önerilen eşik
// (pay aralığı %50–70, en az 5 yıl, iki yanda yıl şartı), 'değerlendirilemedi' durumu, metin (tam / kısa / boş / yetersiz), tür adlarının birleştirilmesi.
// 2026-11-01 güncelleme: öneri aralık olarak (RAPOR §9), 5 yıl asgari raporlama kuralı, yetersiz veride 'değerlendirilemedi';
// kod incelemesi: büyük girdide yığın taşması yok, güvenli sarmalayıcı (RAPOR §10).
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const qc = src.match(/\nconst TUR_QC = \{[^\n]*\};/); if (!qc) throw new Error('bulunamadı: TUR_QC');
const X = {}; vm.createContext(X); vm.runInContext(qc[0].replace('const TUR_QC', 'var TUR_QC') + '\n' + ['turNorm', 'turSayac', 'turYillikSay', 'turYillik', 'turGecisDurum', 'turUyariHtml', 'turUyariHtmlG'].map(fn).join('\n'), X);
let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
// Yapay katalog: yıl y için { tür: sayı } ve büyüklük m (aynı yıl içinde gün gün yayılır)
const kat = spec => { const o = []; for (const [y, turler] of Object.entries(spec)) for (const [mt, n, m] of turler) for (let i = 0; i < n; i++) o.push({ t: Date.UTC(+y, 0, 1) + (i % 360) * 864e5, mt, m: m ?? 3.5 }); return o; };
ok(X.turNorm('ML') === 'ML' && X.turNorm('ml') === 'ML' && X.turNorm('mww') === 'Mw' && X.turNorm('Mb') === 'mb' && X.turNorm('md') === 'MD' && X.turNorm(undefined) === 'diğer', 'tür adları birleşiyor (ML/ml, mww → Mw, Mb → mb, tanımsız → diğer)');
{ const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80], ['ML', 10]]; s[2011] = [['MD', 40], ['ML', 50]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 90], ['md', 5]];
  const d = X.turGecisDurum(kat(s), true, 3.2), g = d.gecisler && d.gecisler[0];
  ok(d.on && d.gecisler.length === 1 && g.a === 'MD' && g.b === 'ML' && g.ySon === 2010 && g.yIlk === 2012 && g.karisik.join() === '2011', `MD → ML: son MD yılı ${g && g.ySon}, ilk ML yılı ${g && g.yIlk}, karışık ${g && g.karisik.join()} (2011'de ML %56 < %60)`);
  ok(d.donemler.map(x => `${x.tur}${x.y0}-${x.y1}`).join() === 'MD2004-2010,ML2012-2018', 'baskın tür dönemleri MD 2004–2010, ML 2012–2018');
  const h = X.turUyariHtml(d), k = X.turUyariHtml(d, true);
  ok(/id="turUyariB"/.test(h) && /MD → ML \(son MD yılı 2010, ilk ML yılı 2012; karışık: 2011\)/.test(h) && /Mc uyarısı tamlığı denetler, tür farkını denetlemez/.test(h) && /ISC → EMSC/.test(h) && /ölçek eşdeğerliğini kanıtlamaz/.test(h), 'tam metin: geçiş, Mc uyarısıyla ilişki, ajans sınırı ve eşdeğerlik çekincesi');
  ok(/id="turUyariA"/.test(k) && !/turUyariB/.test(k) && /a\(t\)/.test(k), 'kısa metin (a(t) paneli) ayrı');
  ok(d.oner === null && /geçişinin görülmediği bir eşik bulunamadı/.test(h), 'tüm olaylar 3,5 iken daha yüksek eşikte yıl kalmıyor → öneri yok, metin bunu söylüyor'); }
{ const s = {}; for (let y = 2004; y <= 2018; y++) s[y] = [['ML', 80], ['mb', 10]]; const d = X.turGecisDurum(kat(s), true, 3.0);
  ok(!d.on && !d.degerlendirilemedi && X.turUyariHtml(d) === '' && X.turUyariHtml(d, true) === '', 'tek baskın tür, veri yeterli → uyarı yok, metin boş'); }
{ const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ML', 15]];
  const d = X.turGecisDurum(kat(s), true, 3.0), h = X.turUyariHtml(d), k = X.turUyariHtml(d, true);
  ok(!d.on && d.degerlendirilemedi && d.yilTum === 15 && d.nDeg === 7 && d.nYetersiz === 8, `ML yılları < 20 olaylı, 2011 olaysız → 15 yıldan 8'i yetersiz (> %50) → 'değerlendirilemedi' (uyarı yok değil)`);
  ok(/id="turYetersizB"/.test(h) && /değerlendirilemedi/.test(h) && /15 takvim yılından 8 tanesi/.test(h) && /geçişi olmadığı anlamına gelmez/.test(h) && !/turUyariB/.test(h), 'yetersiz veri metni: yıl sayıları ve "olmadığı anlamına gelmez"');
  ok(/id="turYetersizA"/.test(k) && !/turYetersizB/.test(k), 'yetersiz veri kısa notu (a(t) paneli)'); }
{ // Sınır: yetersiz yıl oranı tam %50 → değerlendirilebilir sayılır (koşul '> %50'); tek tür → uyarı yok
  const s = {}; for (let y = 2001; y <= 2005; y++) s[y] = [['ML', 30]]; for (let y = 2006; y <= 2010; y++) s[y] = [['ML', 5]];
  const d = X.turGecisDurum(kat(s), true, 3.0); ok(!d.on && !d.degerlendirilemedi && d.nYetersiz === 5 && d.yilTum === 10 && X.turUyariHtml(d) === '', 'yetersiz oranı tam %50 → değerlendirilmiş, uyarı yok'); }
{ const d = X.turGecisDurum(kat({ 2010: [['MD', 30]] }), true, 3.0); ok(!d.on && d.degerlendirilemedi, 'tek değerlendirilebilir yıl → değerlendirilemedi'); }
{ const d = X.turGecisDurum([], true, 3.0); ok(!d.on && d.degerlendirilemedi && /Analize giren olay yok/.test(X.turUyariHtml(d)) && X.turUyariHtml(null) === '', 'olay yok → değerlendirilemedi ("analize giren olay yok"); durum yoksa metin boş'); }
{ const s = {}; for (let y = 2004; y <= 2007; y++) s[y] = [['MD', 50]]; for (let y = 2008; y <= 2011; y++) s[y] = [['ML', 50]]; for (let y = 2012; y <= 2015; y++) s[y] = [['MD', 50]];
  const d = X.turGecisDurum(kat(s), true, 3.0); ok(d.on && d.gecisler.length === 2 && d.gecisler[1].a === 'ML' && d.gecisler[1].b === 'MD', 'MD → ML → MD: iki geçiş'); }
{ // Küçük olaylarda MD → ML, M ≥ 3,5'te her iki yanda mb baskın (%75–80) → üç payda da öneri M 3,5
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80, 3.4], ['mb', 12, 4.2], ['ML', 3, 4.1]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 80, 3.4], ['mb', 12, 4.3], ['ML', 4, 4.0]];
  const d = X.turGecisDurum(kat(s), true, 3.2), o = d.oner;
  ok(d.on && o && o.Mlo === 3.5 && o.Mhi === 3.5 && o.aralik.every(a => a.M === 3.5 && a.tur === 'mb' && a.nYil === 14), `öneri: üç payda da M ${o && o.Mlo} (mb, 14 yıl)`);
  const h = X.turUyariHtml(d);
  ok(/baskınlık payı seçimine göre ≈ M 3,5 \(%50: 3,5, 14 yıl; %60: 3,5, 14 yıl; %70: 3,5, 14 yıl\)/.test(h) && /Bu bir tamlık \(Mc\) eşiği değildir/.test(h) && /asgari raporlama kuralıdır, istatistiksel güvenilirlik ölçütü değildir/.test(h), 'önerilen eşik metinde; "tamlık eşiği değildir" ve "asgari raporlama kuralı" ifadeleri'); }
{ // Pay duyarlılığı: M ≥ 3,5'te mb %53 (önce) / ML %53 (sonra) → %50'de geçiş sürer (öneri M 4,1: yalnız Mw), %60–70'te karışık (öneri M 3,5)
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80, 3.4], ['mb', 18, 4.0], ['ML', 6, 4.0], ['Mw', 10, 4.6]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 80, 3.4], ['ML', 18, 4.0], ['mb', 6, 4.0], ['Mw', 10, 4.6]];
  const d = X.turGecisDurum(kat(s), true, 3.2), o = d.oner, a = o && Object.fromEntries(o.aralik.map(x => [x.pay, x.M]));
  ok(d.on && o && a[0.5] === 4.1 && a[0.6] === 3.5 && a[0.7] === 3.5 && o.Mlo === 3.5 && o.Mhi === 4.1 && /≈ M 3,5–4,1 \(%50: 4,1/.test(X.turUyariHtml(d)), `öneri paya duyarlı → aralık M ${o && o.Mlo}–${o && o.Mhi} (%50: ${a && a[0.5]}, %60: ${a && a[0.6]}, %70: ${a && a[0.7]})`); }
{ // 5 yıl kuralı: eşiğin üstünde yalnız 4 yıl (2009–2010 ve 2012–2013) değerlendirilebilir → öneri yok (eski 3 yıl kuralında olurdu)
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80, 3.4], ...(y >= 2009 ? [['mb', 12, 4.2]] : [])]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 80, 3.4], ...(y <= 2013 ? [['mb', 12, 4.3]] : [])];
  const d = X.turGecisDurum(kat(s), true, 3.2); ok(d.on && d.oner === null && /bir eşik bulunamadı/.test(X.turUyariHtml(d)), '4 değerlendirilebilir yıl < 5 → öneri yok'); }
{ // Geçiş var ama bazı yıllar yetersiz → metinde değerlendirilen yıl sayısı
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80]]; s[2011] = [['ML', 5]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ML', 80]];
  const d = X.turGecisDurum(kat(s), true, 3.0); ok(d.on && d.nYetersiz === 1 && /değerlendirilen yıl 14 \/ 15/.test(X.turUyariHtml(d)), 'geçiş + 1 yetersiz yıl → "değerlendirilen yıl 14 / 15"'); }
{ // Yüksek eşikte yalnız geçiş sonrası yıllar değerlendirilebilir → öneri yapılmaz (iki yan şartı)
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80, 3.4]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 80, 3.4], ['mb', 12, 4.3]];
  const d = X.turGecisDurum(kat(s), true, 3.2); ok(d.on && d.oner === null, 'eşiğin üstünde yalnız geçiş sonrası yıllar → öneri yok (eşdeğerlik sınanamaz)'); }
{ const d = X.turGecisDurum(kat({ 2010: [['MD', 30]], 2011: [['ML', 30]] }), false, 3.0); ok(d.on && d.oner === null, 'mag verilmezse öneri aranmaz'); }
{ // Kod incelemesi (2026-11-01): çok büyük girdide yığın taşması yok (Math.max(...dizi) kaldırıldı); bozuk durumda güvenli sarmalayıcı boş metin döner
  const s = {}; for (let y = 1990; y <= 2010; y++) s[y] = [['MD', 9000]]; for (let y = 2011; y <= 2030; y++) s[y] = [['ML', 9000]];
  let d = null, hata = null; try { d = X.turGecisDurum(kat(s), true, 3.2); } catch (e) { hata = e.message; }
  ok(!hata && d.on && d.gecisler[0].ySon === 2010 && d.gecisler[0].yIlk === 2011, `369 000 olay: hata yok${hata ? ' (' + hata + ')' : ''}, geçiş 2010 → 2011`);
  ok(X.turUyariHtmlG({ on: true }) === '' && X.turUyariHtmlG(null) === '' && X.turUyariHtmlG(d) === X.turUyariHtml(d), 'güvenli sarmalayıcı: bozuk durumda boş metin, normalde turUyariHtml ile aynı'); }
console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
