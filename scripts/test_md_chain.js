// Birim testleri: KOERI Md zinciri (Cambaz vd. 2019 Md→ML + Çıvgın & Scordilis 2019 ML→Mw) — 2026-09-29.
// Kullanım (depo kökünde): node scripts/test_md_chain.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
const ctx = {}; vm.createContext(ctx);
vm.runInContext(src.match(/^const TURKEY_REGIONAL_BBOX = [^\n]*$/m)[0].replace('const ', 'var '), ctx);
vm.runInContext(cut('function inTurkeyRegional(e)', '\n}\n') + '\n}\n', ctx);
vm.runInContext('var MAG_CONVERSIONS = ' + cut('const MAG_CONVERSIONS = {', '\nfunction onTmConversionChange').replace('const MAG_CONVERSIONS = ', '') + ';globalThis.C = MAG_CONVERSIONS;', ctx);
const C = ctx.C; let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
const E = (mtype, mag, lat = 37.4, lon = 38.9) => ({ mtype, mag, lat, lon });
const md = C.koeri_md_chain, cd = C.combined_dispatch, cdm = C.combined_dispatch_md;
const exp = m => 0.93 * (1.0313 * m - 0.7677) + 0.29;
for (const m of [2.5, 3.0, 3.5, 3.9]) ok(Math.abs(md.convert(E('MD', m)) - exp(m)) < 1e-12 && md.applicable(E('MD', m)), `Md ${m} → Mw ${exp(m).toFixed(3)} (zincir birebir)`);
ok(!md.applicable(E('md', 2.3)), 'Md 2,3: ara ML < 1,7 → dönüştürülmez (civgin2019 aralığına devredildi)');
ok(!md.applicable(E('MD', 4.0)) && !md.applicable(E('MD', 6.9)), 'Md ≥ 4,0 dönüştürülmez (doyum; 1999 İzmit Md 6,9 → zincir 6,19 olurdu, gerçek Mw ≈ 7,4–7,6)');
ok(!md.applicable(E('MD', 3.0, 50, 10)), 'Türkiye/çevresi dışında uygulanmaz');
ok(!md.applicable(E('ML', 3.0)) && !md.applicable(E('mb', 4.5)), 'yalnız md tipi');
// Mevcut EQ-Live dönüşümleri değişmedi
for (const [t, m] of [['ml', 2.0], ['ml', 4.4], ['mb', 4.5], ['ms', 5.0]]) {
  ok(cdm.applicable(E(t, m)) === cd.applicable(E(t, m)) && cdm.convert(E(t, m)) === cd.convert(E(t, m)), `${t} ${m}: combined_dispatch_md ≡ combined_dispatch (mevcut kol değişmedi)`); }
ok(C.civgin2019.convert(E('ml', 3.0)) === 0.93 * 3.0 + 0.29 && C.scordilis2006.applicable(E('mb', 4.5)), 'civgin2019 ve scordilis2006 kayıtları aynen');
ok(!cd.applicable(E('md', 3.0)), 'varsayılan combined_dispatch MD dönüştürmüyor (eski davranış korunuyor)');
ok(cdm.applicable(E('md', 3.0)) && Math.abs(cdm.convert(E('md', 3.0)) - exp(3.0)) < 1e-12, 'combined_dispatch_md MD kolunu koeri_md_chain\'e yönlendiriyor');
ok(/<option value="combined_dispatch_md">/.test(src), 'UI: yeni seçenek dönüşüm listesinde (varsayılan değil)');
console.log(`\nPASS ${pass} FAIL ${fail}`); process.exit(fail ? 1 : 0);
