// Kabul testi (2026-10-31): a(t) paneli (Öncel & Wilson 2007, Eş. 3) b(t)'nin altında.
// Önce = verilen index.html (main), sonra = depodaki index.html. Veri yerel, ağ gerekmez.
// Senaryolar: (A) Türkiye, ISC 1971–1997, dikdörtgen 36–42° K / 26–45° D, tek Mc; (B) aynı bölge, tamlık basamakları 1971 M ≥ 5,0 / 1990 M ≥ 3,9;
//             (C) Marmara (40–41,5° K / 26–31° D), EMSC 1998–2026, tek Mc (1999 İzmit ve Düzce artçıları dahil).
// Denetimler: (1) b(t) grafiği ve metni, G–R metni önce = sonra; (2) a(t) pencere sayısı = b(t) pencere sayısı (karışık olanlar hariç),
//   a = log₁₀(n/T) bağımsız hesapla aynı; (3) tamlık basamaklarında karışık pencere işaretli, segmentler Mc ile etiketli;
//   (4) korelasyon yalnız örtüşmeyen pencerelerle p'li; tanım ve uyarı metinleri; (5) sayfa hatası yok. Ekran görüntüleri: a_tekMc.png, a_basamak.png, a_marmara.png
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/a_zaman/kabul_a.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_a.js <önceki_index.html>'); process.exit(2); }
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
window.__kur = async (pencere, S, W, N, E) => { await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="' + pencere[0] + '"]'), pencere[0], pencere[1]);
  regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(S, W) }); map.fire('mousemove', { latlng: L.latLng(N, E) }); await regionMouseUp();
  for (let i = 0; i < 600 && (regionLoading || !regionEvents || !regionEvents.length); i++) await new Promise(r => setTimeout(r, 50));
  if (!showTimeMag) toggleTimeMag(); else renderTimeMag([...events, ...liveEvents]); };
window.__cs = steps => { csSteps = steps.map(([start, mc]) => ({ start, mc })); csEnabled = true; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = true; csRenderRows(); onCsChange(true); renderTimeMag([...events, ...liveEvents]); };
window.__oku = () => ({ bSvg: document.getElementById('tmSvgB').innerHTML, bTxt: document.getElementById('tmStatsB').textContent, grTxt: document.getElementById('tmStatsGR').textContent,
  aTxt: document.getElementById('tmStatsA') ? document.getElementById('tmStatsA').textContent : null, aSvg: document.getElementById('tmSvgA') ? document.getElementById('tmSvgA').innerHTML : null,
  bN: lastBts ? lastBts.ser.length : null, bSer: lastBts ? lastBts.ser.map(q => ({ t: q.t, b: q.b, t0: q.t0, t1: q.t1 })) : null,
  ats: typeof lastAts !== 'undefined' && lastAts ? { NW: lastAts.NW, step: lastAts.step, pts: lastAts.pts.map(q => ({ t: q.t, a: q.a, lo: q.lo, hi: q.hi, mc: q.mc, mixed: q.mixed, Tyr: q.Tyr, b: q.b })) } : null });
`;
const SEN = {
  tekMc:   { p: [1971, 1997], r: [36, 26, 42, 45], cs: null, png: 'a_tekMc.png' },
  basamak: { p: [1971, 1997], r: [36, 26, 42, 45], cs: [['1971-01-01', '5.0'], ['1990-01-01', '3.9']], png: 'a_basamak.png' },
  marmara: { p: [1998, null], r: [40, 26, 41.5, 31], cs: null, png: 'a_marmara.png' },
};
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), S = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    S[ad] = {}; const hat = [];
    for (const [k, c] of Object.entries(SEN)) {
      const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR);
      await p.evaluate(a => __kur(...a), [c.p, ...c.r]); if (c.cs) await p.evaluate(s => __cs(s), c.cs); await p.waitForTimeout(200);
      S[ad][k] = await p.evaluate(() => __oku());
      if (ad === 'sonra') { const box = await p.$('#aTsBox'); await box.scrollIntoViewIfNeeded(); await box.screenshot({ path: path.join(__dirname, c.png) }); }
      hat.push(...hatalar); await ctx.close();
    }
    S[ad].hatalar = hat;
  }
  const O = S.once, Y = S.sonra, YR = 365.25 * 864e5;
  for (const k of Object.keys(SEN)) {
    const o = O[k], y = Y[k];
    ok(o.bSvg === y.bSvg && o.bTxt === y.bTxt && o.grTxt === y.grTxt, `(1) ${k}: b(t) grafiği, b(t) metni ve G–R metni önce = sonra`);
    ok(o.aSvg === null && y.aSvg && y.aSvg.includes('<polyline'), `(1) ${k}: a(t) paneli önce yok, sonra çizildi`);
    const pts = y.ats.pts, nOk = pts.filter(q => !q.mixed).length;
    ok(pts.length === y.bN, `(2) ${k}: a(t) pencere sayısı ${pts.length} = b(t) pencere sayısı ${y.bN} (çizilen ${nOk}, karışık ${pts.length - nOk})`);
    if (!SEN[k].cs) { let d = 0; y.bSer.forEach((q, i) => { const a = Math.log10(y.ats.NW / ((q.t1 - q.t0) / YR)); d = Math.max(d, Math.abs(a - pts[i].a)); });
      ok(d < 1e-12, `(2) ${k}: a = log₁₀(n/T) bağımsız hesapla aynı (en büyük fark ${d.toExponential(1)}); T medyan ${pts.map(q => q.Tyr).sort((a, b) => a - b)[Math.floor(pts.length / 2)].toPrecision(3)} yıl`); }
    ok(/Mc'deki yıllık olay hızıdır/.test(y.aTxt) && /a\s*GR/.test(y.aTxt.replace(/<[^>]+>/g, '')) && /tahmini ya da öncü kanıtı değildir/.test(y.aTxt) && /b–a korelasyonu yapay olabilir/.test(y.aTxt) && /p verilmez — pencereler bağımsız değil/.test(y.aTxt),
      `(4) ${k}: tanım (Mc'deki hız), a_GR uyarısı, örtüşen r için p verilmemesi ve "tahmin değildir" ve tamlık kaynaklı yapay korelasyon notları var`);
    const rm = y.aTxt.match(/r = (−?-?[\d,]+) \(örtüşmeyen (\d+) pencere, p = ([^)]+)\)/); console.log(`     ${k}: ${rm ? `r(b, a) = ${rm[1]}, örtüşmeyen ${rm[2]} pencere, p = ${rm[3]}` : 'korelasyon yok'}; a aralığı ${Math.min(...pts.filter(q => !q.mixed).map(q => q.a)).toFixed(2)}–${Math.max(...pts.filter(q => !q.mixed).map(q => q.a)).toFixed(2)}`);
  }
  { const y = Y.basamak, mixed = y.ats.pts.filter(q => q.mixed).length, mcs = [...new Set(y.ats.pts.filter(q => !q.mixed).map(q => q.mc))];
    ok(mixed > 0 && mcs.length === 2 && /Mc 5,0|Mc 5\.0/.test(y.aSvg) && /Mc 3,9|Mc 3\.9/.test(y.aSvg) && /tamlık basamağı geçişindeki pencere/.test(y.aTxt),
      `(3) Tamlık basamakları: ${mixed} karışık pencere çizilmedi; segmentler Mc ${mcs.join(' / ')} etiketli; "farklı Mc segmentleri karşılaştırılamaz" notu`); }
  ok(/GK74 kapalı/.test(Y.marmara.aTxt), '(4) GK74 kapalıyken artçı tepeleri uyarısı');
  ok(!O.hatalar.length && !Y.hatalar.length, `(5) Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length})` + (Y.hatalar.length ? ': ' + Y.hatalar.join(' | ') : ''));
  const ozet = {}; for (const k of Object.keys(SEN)) ozet[k] = { metin: Y[k].aTxt, pencere: Y[k].ats.pts.length };
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify({ senaryolar: SEN, sonuc: ozet, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
