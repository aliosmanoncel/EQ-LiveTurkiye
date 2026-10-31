// Birim testleri: büyüklük türü geçişi uyarısı (2026-11-01). index.html'den TUR_QC, turNorm, turYillik, turGecisDurum, turUyariHtml okunur.
// Denetimler: geçiş algılama (baskın tür ≥ %60, yıllık ≥ 20 olay), karışık yıllar, az olaylı yılların yok sayılması, A → B → A, önerilen eşik
// (iki yanda yıl şartı), metin (tam / kısa / boş), tür adlarının birleştirilmesi.
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const qc = src.match(/\nconst TUR_QC = \{[^\n]*\};/); if (!qc) throw new Error('bulunamadı: TUR_QC');
const X = {}; vm.createContext(X); vm.runInContext(qc[0].replace('const TUR_QC', 'var TUR_QC') + '\n' + ['turNorm', 'turYillik', 'turGecisDurum', 'turUyariHtml'].map(fn).join('\n'), X);
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
  ok(!d.on && X.turUyariHtml(d) === '' && X.turUyariHtml(d, true) === '', 'tek baskın tür → uyarı yok, metin boş'); }
{ const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ML', 15]];
  ok(!X.turGecisDurum(kat(s), true, 3.0).on, 'ML yılları < 20 olaylı → değerlendirilmiyor, uyarı yok'); }
{ const s = {}; for (let y = 2004; y <= 2007; y++) s[y] = [['MD', 50]]; for (let y = 2008; y <= 2011; y++) s[y] = [['ML', 50]]; for (let y = 2012; y <= 2015; y++) s[y] = [['MD', 50]];
  const d = X.turGecisDurum(kat(s), true, 3.0); ok(d.on && d.gecisler.length === 2 && d.gecisler[1].a === 'ML' && d.gecisler[1].b === 'MD', 'MD → ML → MD: iki geçiş'); }
{ // Küçük olaylarda MD → ML, M ≥ 4,0'da her iki yanda mb baskın (yıllık 12) → öneri M 4,0 (mb)
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80, 3.4], ['mb', 12, 4.2], ['ML', 3, 4.1]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 80, 3.4], ['mb', 12, 4.3], ['ML', 4, 4.0]];
  const d = X.turGecisDurum(kat(s), true, 3.2);
  ok(d.on && d.oner && d.oner.M === 3.5 && d.oner.tur === 'mb' && d.oner.nYil === 14, `öneri: türün değişmediği en küçük eşik ${d.oner && d.oner.M} (mb, ${d.oner && d.oner.nYil} yıl)`);
  ok(/en küçük eşik ≈ M 3,5 \(14 yıl değerlendirildi, yıllık en az 10 olay; baskın tür mb\)/.test(X.turUyariHtml(d)), 'önerilen eşik metinde'); }
{ // M ≥ 4,0'da yıllar karışık (mb %50 / ML %50): geçiş yok sayılır → öneri, karışık yıl sayısıyla
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80, 3.4], ['mb', 6, 4.2], ['ML', 6, 4.1]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 80, 3.4], ['mb', 6, 4.3], ['ML', 6, 4.0]];
  const d = X.turGecisDurum(kat(s), true, 3.2);
  ok(d.on && d.oner && d.oner.M === 3.5 && d.oner.tur === null && d.oner.nKarisik === 14 && /baskın tür yok, 14 yıl karışık türlü/.test(X.turUyariHtml(d)), 'karışık türlü yıllar geçiş sayılmıyor → öneri M 3,5, metinde "14 yıl karışık türlü"'); }
{ // Yüksek eşikte yalnız geçiş sonrası yıllar değerlendirilebilir → öneri yapılmaz (iki yan şartı)
  const s = {}; for (let y = 2004; y <= 2010; y++) s[y] = [['MD', 80, 3.4]]; for (let y = 2012; y <= 2018; y++) s[y] = [['ml', 80, 3.4], ['mb', 12, 4.3]];
  const d = X.turGecisDurum(kat(s), true, 3.2); ok(d.on && d.oner === null, 'eşiğin üstünde yalnız geçiş sonrası yıllar → öneri yok (eşdeğerlik sınanamaz)'); }
{ const d = X.turGecisDurum(kat({ 2010: [['MD', 30]], 2011: [['ML', 30]] }), false, 3.0); ok(d.on && d.oner === null, 'mag verilmezse öneri aranmaz'); }
console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
