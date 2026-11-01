// Kod incelemesi denetimi (2026-11-01, RAPOR §10): turGecisDurum'un hızlandırılmış ve sağlamlaştırılmış sürümü, önceki sürümle (b8a6f81) aynı sonucu
// veriyor mu? Gerçek veri (disa_aktar.js çıktısı): Türkiye, Marmara, ISC + EMSC; ham ve GK74; Mc 3,2 ve 3,5; 9 eşik birleşimi. Ayrıca süre ölçümü.
// Kullanım (depo kökünde): node analysis/tur_gecisi/esdegerlik_denetimi.js <disa_aktar çıktısı.json>
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), { execSync } = require('child_process');
const ROOT = path.join(__dirname, '..', '..');
const yukle = src => { src = src.replace(/\r\n/g, '\n'); const fn = n => { const i = src.indexOf('\nfunction ' + n + '('); if (i < 0) return ''; const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
  const X = {}; vm.createContext(X); vm.runInContext(src.match(/\nconst TUR_QC = \{[^\n]*\};/)[0].replace('const TUR_QC', 'var TUR_QC') + '\n' + ['turNorm', 'turSayac', 'turYillikSay', 'turYillik', 'turGecisDurum'].map(fn).join('\n'), X); return X; };
const ESKI = yukle(execSync('git show b8a6f81:index.html', { cwd: ROOT, maxBuffer: 1 << 28 }).toString()), YENI = yukle(fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8'));
const V = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let ayni = 0, farkli = 0; const sure = { eski: 0, yeni: 0 };
for (const sen of ['tr_emsc', 'mar_emsc', 'tr_isc_emsc']) for (const gk of [0, 1]) for (const Mc of [3.2, 3.5]) {
  const ol = V.senaryolar[sen].olaylar.filter(e => (!gk || e.gk) && e.m >= Mc - 1e-9).map(e => ({ t: e.t, mt: e.mt, m: e.m }));
  for (const pay of [0.5, 0.6, 0.7]) for (const minN of [10, 20, 30]) {
    for (const X of [ESKI, YENI]) Object.assign(X.TUR_QC, { pay, minN });
    let t = Date.now(); const a = ESKI.turGecisDurum(ol, true, Mc); sure.eski += Date.now() - t;
    t = Date.now(); const b = YENI.turGecisDurum(ol, true, Mc); sure.yeni += Date.now() - t;
    if (JSON.stringify(a) === JSON.stringify(b)) ayni++; else { farkli++; console.log('FARKLI', sen, gk, Mc, pay, minN); } } }
console.log(`eşdeğerlik: ${ayni} aynı, ${farkli} farklı (3 bölge × ham/GK74 × Mc 3,2/3,5 × 9 birleşim = 108); toplam süre eski ${sure.eski} ms, yeni ${sure.yeni} ms (${(sure.eski / Math.max(1, sure.yeni)).toFixed(1)}×)`);
fs.writeFileSync(path.join(__dirname, 'esdegerlik_sonuc.json'), JSON.stringify({ ayni, farkli, sure }, null, 1));
process.exit(farkli ? 1 : 0);
