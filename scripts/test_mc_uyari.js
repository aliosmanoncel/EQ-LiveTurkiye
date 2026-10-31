// Birim testleri: katalog tamlık (Mc uyumsuzluğu) uyarısı (2026-10-31). index.html'den mcUyariDurum ve mcUyariHtml okunur.
// Denetimler: tek Mc'de eşik (%5 'inc'), önerilen ortak Mc (en yüksek Mc(t), 0,1'e yukarı), tamlık basamaklarında CS_QC.mcGap ölçütü,
// uyarı yokken boş metin, metinde ölçek/algılama uyarısı.
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const X = {}; vm.createContext(X); vm.runInContext(['mcUyariDurum', 'mcUyariHtml'].map(fn).join('\n'), X);
let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
const ser = (n, k) => Array.from({ length: n }, (_, i) => ({ inc: i < k }));
const mcSer = [{ t: 0, mc: 3.2 }, { t: 1, mc: 3.74 }, { t: 2, mc: 3.3 }];
{ const d = X.mcUyariDurum({ cs: false, ser: ser(100, 5), mcSer, Mc: 3.2 });
  ok(d.on && d.tur === 'tekMc' && Math.abs(d.frac - 0.05) < 1e-12 && d.oner === 3.8 && d.mcMin === 3.2 && d.mcMax === 3.74, `tek Mc, %5 'inc' → uyarı; önerilen Mc ${d.oner} (en yüksek Mc(t) 3,74 yukarı yuvarlandı)`); }
{ const d = X.mcUyariDurum({ cs: false, ser: ser(100, 4), mcSer, Mc: 3.2 }); ok(!d.on, "tek Mc, %4 'inc' → uyarı yok"); }
{ const d = X.mcUyariDurum({ cs: false, ser: ser(100, 50), mcSer: [{ t: 0, mc: 3 }], Mc: 3 }); ok(!d.on, 'Mc(t) şeridi < 2 nokta → uyarı yok (karar verilemez)'); }
{ const P = [{ mc: 4.5, mcData: 4.6, t0: 0, t1: 1 }, { mc: 4.0, mcData: 4.8, t0: 1, t1: 2 }, { mc: 4.0, mcData: null, t0: 2, t1: 3 }];
  const d = X.mcUyariDurum({ cs: true, periods: P, gap: 0.2 });
  ok(d.on && d.tur === 'basamak' && d.donemler.length === 1 && d.donemler[0].mcData === 4.8, 'basamaklar: yalnız eşiği veri Mc − 0,2\'nin altında olan dönem işaretlenir (4,0 < 4,8 − 0,2); 4,5 ile 4,6 farkı ve veri Mc yokluğu uyarı üretmez');
  ok(!X.mcUyariDurum({ cs: true, periods: [{ mc: 4.5, mcData: 4.65 }], gap: 0.2 }).on, 'basamaklar: fark ≤ 0,2 → uyarı yok'); }
{ // Dönem içi değişim: dönemin bütün Mc'si 3,9 (eşik 4,0 ile uyumlu) ama 1985–1989 Mc(t) 4,7–4,8
  const P = [{ mc: 4.0, mcData: 3.9, t0: 0, t1: 13 }], ms = [4.8, 4.7, 4.75, 3.9, 3.8, 3.7, 3.7, 3.8, 3.7, 3.7].map((mc, i) => ({ t: i + 0.5, mc }));
  const d = X.mcUyariDurum({ cs: true, periods: P, gap: 0.2, mcSer: ms });
  ok(d.on && d.donemler[0].mcTmax === 4.8 && Math.abs(d.donemler[0].oran - 0.3) < 1e-12, 'basamaklar: dönem içi Mc(t) değişimi yakalanıyor (3/10 nokta eşik + 0,2 üstünde, en yüksek 4,8)');
  ok(!X.mcUyariDurum({ cs: true, periods: P, gap: 0.2, mcSer: ms.map((m, i) => i === 0 ? m : { ...m, mc: 3.8 }) }).on, 'basamaklar: tek aykırı Mc(t) noktası uyarı üretmez (en az 2 nokta gerekir)'); }
{ // Yıllık ölçüt: Mc(t) seyrek dönemi yakalamıyor (hepsi 3,9), yıllık Mc 1986: 4,8 ve 1988: 4,7 (eşik 4,0) → uyarı; tek yıl → uyarı yok
  const Y = y => Date.UTC(y, 0, 1), P = [{ mc: 4.0, mcData: 3.9, t0: Y(1985), t1: Y(1998) }], ms = [{ t: Y(1990), mc: 3.9 }, { t: Y(1995), mc: 3.9 }];
  const yl = [{ y: 1986, n: 56, mc: 4.8 }, { y: 1988, n: 60, mc: 4.7 }, { y: 1992, n: 179, mc: 3.7 }].map(q => ({ ...q, t0: Y(q.y), t1: Y(q.y + 1) }));
  const d = X.mcUyariDurum({ cs: true, periods: P, gap: 0.2, mcSer: ms, yillik: yl });
  ok(d.on && d.donemler[0].neden.join() === 'yıllık' && d.donemler[0].yillar.map(q => q.y).join() === '1986,1988', 'basamaklar: yıllık ölçüt dönem içi eksikliği yakalıyor (1986, 1988)');
  ok(!X.mcUyariDurum({ cs: true, periods: P, gap: 0.2, mcSer: ms, yillik: yl.slice(1) }).on, 'basamaklar: tek yıl yetmez (en az 2 yıl)');
  ok(/1986: 4,8, 1988: 4,7/.test(X.mcUyariHtml(d)), 'uyarı metninde yıllık Mc değerleri'); }
{ const h = X.mcUyariHtml(X.mcUyariDurum({ cs: false, ser: ser(20, 10), mcSer, Mc: 3.2 }));
  ok(/Katalog Tamlık Uyarısı/.test(h) && /yapay değişimlere/.test(h) && /kanıtlamaz/.test(h) && /büyüklük ölçeği/.test(h) && /algılama/.test(h) && /%50 kadarı \(10 \/ 20\)/.test(h), 'uyarı metni: başlık, yapay değişim, "kanıtlamaz", ölçek ve algılama uyarısı, oran');
  ok(X.mcUyariHtml({ on: false }) === '' && X.mcUyariHtml(null) === '' && /mcUyariA/.test(X.mcUyariHtml({ on: true, tur: 'tekMc' }, true)), 'uyarı yokken boş; kısa sürüm a(t) için'); }
console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
