// Büyüklük türü geçişi uyarısı — eşik duyarlılığı (2026-11-01). Uygulamanın kendi kodu (TUR_QC, turNorm, turYillik, turGecisDurum) index.html'den
// okunur; TUR_QC.pay ∈ {0,5, 0,6, 0,7} × TUR_QC.minN ∈ {10, 20, 30} (9 birleşim) denenir. TUR_QC.minNOner (önerilen eşik için yıllık en az olay)
// 10'da sabit tutulur; ayrıca 9 birleşimin her birinde minNOner = minN ile de raporlanır (öneri ölçütünün minN'e bağlanması durumunda ne olur).
// Girdi: disa_aktar.js çıktısı (olaylar: t, mt, m = panelBaseMag; EMSC'de uygulamanın b(t) panelindeki e.mw ?? e.mag ile aynı). Analize giren
// olaylar uygulamadaki gibi M ≥ Mc (tek Mc). Senaryolar: Türkiye ve Marmara, EMSC 1998–, ham ve GK74, Mc 3,2 (uygulamanın Mc'si) ve 3,5.
// Doğrulama: varsayılan (0,6 / 20) sonuçları kabul testindeki tarayıcı sonuçlarıyla (kabul_sonuc.json) karşılaştırılır.
// UYARI: Bu bir tür etiketi duyarlılığıdır; tamlık (Mc) değişimi hakkında bilgi vermez (RAPOR §8).
// Kullanım (depo kökünde): node analysis/tur_gecisi/esik_duyarlilik.js <disa_aktar çıktısı.json>
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..', '..');
const src = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fnCut = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const qc = src.match(/\nconst TUR_QC = \{[^\n]*\};/); if (!qc) throw new Error('bulunamadı: TUR_QC');
const X = {}; vm.createContext(X); vm.runInContext(qc[0].replace('const TUR_QC', 'var TUR_QC') + '\n' + ['turNorm', 'turYillik', 'turGecisDurum', 'turUyariHtml'].map(fnCut).join('\n'), X);
const VARSAYILAN = { ...X.TUR_QC };
const V = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const SEN = { tr: ['tr_emsc', 0, 3.2], tr_gk74: ['tr_emsc', 1, 3.2], tr_mc35: ['tr_emsc', 0, 3.5], mar: ['mar_emsc', 0, 3.2], mar_gk74: ['mar_emsc', 1, 3.2] };
// Öneri (2026-11-01 güncelleme, RAPOR §9): pay aralığı %50–70 için ayrı ayrı aranır, en az 5 yıl; durum 'değerlendirilemedi' de raporlanır
const ozet = d => d.on ? { on: true, gecisler: d.gecisler.map(g => ({ a: g.a, b: g.b, ySon: g.ySon, yIlk: g.yIlk, karisik: g.karisik })), donemler: d.donemler.map(x => ({ tur: x.tur, y0: x.y0, y1: x.y1 })),
  oner: d.oner ? { Mlo: d.oner.Mlo, Mhi: d.oner.Mhi, aralik: d.oner.aralik } : null } : { on: false, degerlendirilemedi: !!d.degerlendirilemedi };
const R = { girdi: V.uretim, varsayilan: VARSAYILAN, senaryolar: {}, dogrulama: {} };
for (const [ad, [sen, gk, Mc]] of Object.entries(SEN)) {
  const s = V.senaryolar[sen], ol = s.olaylar.filter(e => (!gk || e.gk) && e.m >= Mc - 1e-9).map(e => ({ t: e.t, mt: e.mt, m: e.m }));
  const yilTum = new Set(ol.map(e => new Date(e.t).getUTCFullYear())).size, sonuc = [];
  for (const pay of [0.5, 0.6, 0.7]) for (const minN of [10, 20, 30]) for (const onerBagli of [false, true]) {
    Object.assign(X.TUR_QC, { pay, minN, minNOner: onerBagli ? minN : VARSAYILAN.minNOner });
    const d = X.turGecisDurum(ol, true, Mc), yy = X.turYillik(ol, minN);
    sonuc.push({ pay, minN, minNOner: X.TUR_QC.minNOner, ...ozet(d), yilTum: d.yilTum, nDeg: d.nDeg, nYetersiz: d.nYetersiz, yilDegerlendirilen: yy.length, yilKarisik: yy.filter(q => !q.tur).length, yilYetersiz: yilTum - yy.length,
      yetersizYillar: [...new Set(ol.map(e => new Date(e.t).getUTCFullYear()))].filter(y => !yy.some(q => q.y === y)).sort((a, b) => a - b), metin: X.turUyariHtml(d).replace(/<[^>]+>/g, '') }); }
  Object.assign(X.TUR_QC, VARSAYILAN);
  R.senaryolar[ad] = { sen, gk, Mc, n: ol.length, yilTum, sonuc };
}
// Doğrulama: varsayılan birleşim = tarayıcıdaki kabul testi sonucu (emsc98 → tr, emsc98_gk74 → tr_gk74, emsc98_mc35 → tr_mc35, marmara → mar, marmara_gk74 → mar_gk74)
{ const K = JSON.parse(fs.readFileSync(path.join(__dirname, 'kabul_sonuc.json'), 'utf8')).sonuc, es = { tr: 'emsc98', tr_gk74: 'emsc98_gk74', tr_mc35: 'emsc98_mc35', mar: 'marmara', mar_gk74: 'marmara_gk74' };
  for (const [a, k] of Object.entries(es)) { const v = R.senaryolar[a].sonuc.find(x => x.pay === VARSAYILAN.pay && x.minN === VARSAYILAN.minN && x.minNOner === VARSAYILAN.minNOner), b = K[k].durum;
    const ayni = JSON.stringify(ozet(b)) === JSON.stringify({ ...(v.on ? { on: true, gecisler: v.gecisler, donemler: v.donemler, oner: v.oner } : { on: false, degerlendirilemedi: v.degerlendirilemedi }) });
    R.dogrulama[a] = { kabul: k, ayni }; } }
fs.writeFileSync(path.join(__dirname, 'esik_duyarlilik.json'), JSON.stringify(R, null, 1));
// ── Özet ──
const g = x => !x.on ? (x.degerlendirilemedi ? `DEĞERLENDİRİLEMEDİ (${x.nYetersiz}/${x.yilTum} yıl yetersiz)` : 'uyarı yok') : x.gecisler.map(q => `${q.a}→${q.b} ${q.ySon}→${q.yIlk}${q.karisik.length ? ` [karışık ${q.karisik.length === 1 ? q.karisik[0] : q.karisik[0] + '–' + q.karisik[q.karisik.length - 1]}]` : ''}`).join('; ');
console.log('Doğrulama (varsayılan = tarayıcı kabul testi):', Object.entries(R.dogrulama).map(([a, v]) => `${a} ${v.ayni ? 'AYNI' : 'FARKLI'}`).join(', '));
for (const [ad, S] of Object.entries(R.senaryolar)) { console.log(`\n══ ${ad} (${S.sen}${S.gk ? ', GK74' : ''}, M ≥ ${S.Mc}; n ${S.n}, ${S.yilTum} yıl) ══`);
  S.sonuc.filter((x, i, A) => x.minNOner === VARSAYILAN.minNOner && A.findIndex(y => y.pay === x.pay && y.minN === x.minN && y.minNOner === x.minNOner) === i).forEach(x => { const b = S.sonuc.find(y => y.pay === x.pay && y.minN === x.minN && y.minNOner === x.minN);
    console.log(`  %${100 * x.pay} / ${String(x.minN).padStart(2)}${x.pay === VARSAYILAN.pay && x.minN === VARSAYILAN.minN ? '*' : ' '}: ${g(x).padEnd(64)} | öneri ${x.oner ? `M ${x.oner.Mlo}–${x.oner.Mhi} (${x.oner.aralik.map(a => `%${a.pay * 100}: ${a.M ?? '—'}${a.M !== null ? '/' + a.nYil + 'y' : ''}`).join(' ')})` : '—'.padEnd(8)} | öneri (minNOner = minN) ${b.oner ? `M ${b.oner.Mlo}–${b.oner.Mhi}` : '—'} | yıl: değerl. ${x.yilDegerlendirilen}, karışık ${x.yilKarisik}, yetersiz ${x.yilYetersiz}`); }); }
