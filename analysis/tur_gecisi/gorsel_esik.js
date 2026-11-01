// Görsel regresyon (2026-11-01): tür geçişi uyarısının farklı eşiklerde tarayıcıdaki davranışı. Önce = verilen index.html (main), sonra = depodaki.
// Senaryolar: Türkiye EMSC 1998– ve Marmara EMSC 1998– + GK74. Her birinde TUR_QC (sayfadaki nesne) 9 birleşime ayarlanıp panel yeniden çizilir.
// Denetimler: (1) b(t), a(t) grafikleri, uyarılar dışındaki metinler ve G–R metni 9 birleşimin hepsinde main ile aynı (eşik yalnız uyarıyı etkiler);
//   (2) uyarının tarayıcıdaki durumu esik_duyarlilik.js (Node) ile aynı; (3) b(t) ve a(t) notları tutarlı; (4) sayfa hatası yok;
//   (5) Marmara GK74, yıllık 30 olay: 'değerlendirilemedi' notu (2026-11-01 güncelleme, RAPOR §9).
// Ekran görüntüleri: gorsel_<senaryo>_<pay>_<minN>.png (üç birleşim: %50/10, %60/20, %70/30).
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/tur_gecisi/gorsel_esik.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node gorsel_esik.js <önceki_index.html>'); process.exit(2); }
const srv = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split('?')[0]), f = u === '/__once.html' ? ONCE : path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT) && f !== ONCE) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); });
});
let pass = 0, fail = 0; const kayit = [];
const ok = (c, m) => { (c ? pass++ : fail++); kayit.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };
async function sayfa(br, yol) {
  const ctx = await br.newContext({ viewport: { width: 1400, height: 1100 } }), p = await ctx.newPage(), hatalar = [];
  p.on('pageerror', e => hatalar.push(String(e)));
  await ctx.route('**/*', rt => { const u = rt.request().url();
    if (u.startsWith('http://127.0.0.1')) return rt.continue();
    if (/leaflet@1\.9\.4\/dist\/leaflet\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.js'), contentType: 'text/javascript' });
    if (/leaflet@1\.9\.4\/dist\/leaflet\.css/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.css'), contentType: 'text/css' });
    if (/leaflet-heat\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet.heat/dist/leaflet-heat.js'), contentType: 'text/javascript' });
    return rt.abort(); });
  await p.routeWebSocket(/.*/, ws => ws.close()).catch(() => {});
  await p.goto(`http://127.0.0.1:${srv.address().port}${yol}`, { waitUntil: 'load' });
  await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function' && typeof map !== 'undefined'); await p.waitForTimeout(400);
  return { p, ctx, hatalar };
}
const KUR = `
window.__kur = async (pencereler, S, W, N, E) => { for (const [a, b] of pencereler) await toggleHistoricalWindow(document.querySelector(b ? '.tbtn[data-hist="' + a + '"]' : '.tbtn[data-hist="' + a + '"]:not([data-hist-src])'), a, b);
  regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(S, W) }); map.fire('mousemove', { latlng: L.latLng(N, E) }); await regionMouseUp();
  for (let i = 0; i < 600 && (regionLoading || !regionEvents || !regionEvents.length); i++) await new Promise(r => setTimeout(r, 50));
  if (!showTimeMag) toggleTimeMag(); else renderTimeMag([...events, ...liveEvents]); };
window.__qc = (pay, minN) => { if (typeof TUR_QC !== 'undefined') { TUR_QC.pay = pay; TUR_QC.minN = minN; } renderTimeMag([...events, ...liveEvents]); };
window.__oku = () => { const tx = id => { const el = document.getElementById(id); if (!el) return null; const c = el.cloneNode(true); c.querySelectorAll('#mcUyariB, #mcUyariA, #turUyariB, #turUyariA, #turYetersizB, #turYetersizA').forEach(n => n.remove()); return c.textContent; };
  const sa = document.getElementById('tmSvgA'), t = id => document.getElementById(id) ? document.getElementById(id).textContent : null;
  return { bSvg: document.getElementById('tmSvgB').innerHTML, bTxt: tx('tmStatsB'), aSvg: sa ? sa.innerHTML : null, aTxt: tx('tmStatsA'), grTxt: document.getElementById('tmStatsGR').textContent,
    mcB: t('mcUyariB'), turB: t('turUyariB'), turA: t('turUyariA'), yetB: t('turYetersizB'), yetA: t('turYetersizA'), durum: typeof lastTurUyari !== 'undefined' && lastTurUyari ? JSON.parse(JSON.stringify(lastTurUyari)) : null }; };
`;
const SEN = { tr: { p: [[1998, null]], r: [36, 26, 42, 45] }, mar_gk74: { p: [[1998, null]], r: [40, 26, 41.5, 31], gk: true } };
const BIR = []; for (const pay of [0.5, 0.6, 0.7]) for (const minN of [10, 20, 30]) BIR.push([pay, minN]);
const RESIM = new Set(['0.5_10', '0.6_20', '0.7_30']);
const ozet = d => d && d.on ? JSON.stringify({ g: d.gecisler.map(x => [x.a, x.b, x.ySon, x.yIlk, x.karisik]), o: d.oner ? [d.oner.Mlo, d.oner.Mhi, d.oner.aralik.map(a => [a.pay, a.M, a.nYil ?? null])] : null }) : d && d.degerlendirilemedi ? 'yetersiz' : 'yok';
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), hatalar = [], N = JSON.parse(fs.readFileSync(path.join(__dirname, 'esik_duyarlilik.json'), 'utf8')).senaryolar, nodeAd = { tr: 'tr', mar_gk74: 'mar_gk74' };
  for (const [k, c] of Object.entries(SEN)) {
    const o = await sayfa(br, '/__once.html'); await o.p.evaluate(KUR); await o.p.evaluate(a => __kur(...a), [c.p, ...c.r]);
    if (c.gk) await o.p.evaluate(async () => { await toggleRegionDecluster(); applyGk74Filter(regionEvents); renderTimeMag([...events, ...liveEvents]); });
    const O = await o.p.evaluate(() => __oku()); hatalar.push(...o.hatalar); await o.ctx.close();
    const y = await sayfa(br, '/'); await y.p.evaluate(KUR); await y.p.evaluate(a => __kur(...a), [c.p, ...c.r]);
    if (c.gk) await y.p.evaluate(async () => { await toggleRegionDecluster(); applyGk74Filter(regionEvents); renderTimeMag([...events, ...liveEvents]); });
    for (const [pay, minN] of BIR) {
      await y.p.evaluate(a => __qc(...a), [pay, minN]); await y.p.waitForTimeout(100); const Y = await y.p.evaluate(() => __oku()), et = `${k} %${pay * 100}/${minN}`;
      ok(O.bSvg === Y.bSvg && O.bTxt === Y.bTxt && O.aSvg === Y.aSvg && O.aTxt === Y.aTxt && O.grTxt === Y.grTxt && O.mcB === Y.mcB, `(1) ${et}: b(t), a(t), G–R ve Mc uyarısı main ile aynı`);
      const n = N[nodeAd[k]].sonuc.find(x => x.pay === pay && x.minN === minN && x.minNOner === 10);
      const nOz = n.on ? JSON.stringify({ g: n.gecisler.map(x => [x.a, x.b, x.ySon, x.yIlk, x.karisik]), o: n.oner ? [n.oner.Mlo, n.oner.Mhi, n.oner.aralik.map(a => [a.pay, a.M, a.nYil ?? null])] : null }) : n.degerlendirilemedi ? 'yetersiz' : 'yok';
      ok(ozet(Y.durum) === nOz, `(2) ${et}: tarayıcı = Node (${Y.durum && Y.durum.on ? Y.durum.gecisler.map(x => `${x.a}→${x.b} ${x.ySon}→${x.yIlk}`).join('; ') + (Y.durum.oner ? `, öneri M ${Y.durum.oner.Mlo}–${Y.durum.oner.Mhi}` : ', öneri yok') : Y.durum && Y.durum.degerlendirilemedi ? `değerlendirilemedi (${Y.durum.nYetersiz}/${Y.durum.yilTum} yıl yetersiz)` : 'uyarı yok'})`);
      ok(!!Y.turB === !!Y.turA && !!Y.turB === !!(Y.durum && Y.durum.on) && !!Y.yetB === !!Y.yetA && !!Y.yetB === !!(Y.durum && !Y.durum.on && Y.durum.degerlendirilemedi), `(3) ${et}: b(t) ve a(t) notları tutarlı (${Y.turB ? 'uyarı' : Y.yetB ? 'değerlendirilemedi' : 'yok'})`);
      if (k === 'mar_gk74' && minN === 30) ok(!!Y.yetB && /geçişi olmadığı anlamına gelmez/.test(Y.yetB), `(5) ${et}: 29 yılın çoğu yetersiz → "değerlendirilemedi" notu (önceki sürümde sessizce "uyarı yok")`);
      if (RESIM.has(`${pay}_${minN}`)) { const el = await y.p.$(Y.turB ? '#turUyariB' : Y.yetB ? '#turYetersizB' : '#tmStatsB'); await el.scrollIntoViewIfNeeded(); await el.screenshot({ path: path.join(__dirname, `gorsel_${k}_${pay * 100}_${minN}.png`) }); }
    }
    await y.p.evaluate(() => __qc(0.6, 20)); hatalar.push(...y.hatalar); await y.ctx.close();
  }
  ok(!hatalar.length, `(4) Sayfa hatası yok (${hatalar.length})` + (hatalar.length ? ': ' + hatalar.join(' | ') : ''));
  fs.writeFileSync(path.join(__dirname, 'gorsel_sonuc.json'), JSON.stringify({ denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
