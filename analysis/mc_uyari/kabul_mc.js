// Kabul testi (2026-10-31): Katalog tamlık (Mc uyumsuzluğu) uyarısı. Önce = verilen index.html (main), sonra = depodaki index.html. Veri yerel.
// Senaryolar (Türkiye kutusu 36–42° K / 26–45° D; Marmara 40–41,5° K / 26–31° D):
//   birlesik       ISC 1971–1997 + EMSC 1998–, otomatik Mc (ISC–EMSC araştırmasındaki yapay 1998 sıçraması durumu) → uyarı beklenir
//   birlesik_mc40  aynı, elle Mc = 4,0
//   isc71_97       ISC 1971–1997, otomatik Mc
//   emsc98         EMSC 1998–, otomatik Mc
//   basamak_test   ISC 1971–1997, basamaklar 1971 M ≥ 4,5 / 1985 M ≥ 4,0 (Poisson raporunda iyimser bulunan test basamakları)
//   basamak_oto    ISC 1971–1997, "Otomatik öner" basamakları (5,0 / 4,2 / 4,8 / 3,9)
//   marmara        Marmara, EMSC 1998–, otomatik Mc
//   + GK74 açık, Mc 4,5, basamak + GK74, Kahramanmaraş (36,5–38,5° K / 35,5–39° D; 2023 artçıları) GK74 kapalı/açık: geçici/kalıcı ayrımı
// Denetimler: (1) b(t) ve a(t) grafikleri, uyarı bloğu dışındaki b(t)/a(t) metinleri ve G–R metni önce = sonra (hesap değişmedi);
//   (2) uyarı b(t)'de varsa a(t)'de kısa notu da var (ve tersi); (3) birlesik senaryosunda uyarı var; iyimser 1985 basamağı yıllık Mc ile yakalanıyor; (4) sayfa hatası yok.
// Ekran görüntüsü: mc_uyari_birlesik.png
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/mc_uyari/kabul_mc.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_mc.js <önceki_index.html>'); process.exit(2); }
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
window.__cs = steps => { csSteps = steps.map(([start, mc]) => ({ start, mc })); csEnabled = true; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = true; csRenderRows(); onCsChange(true); renderTimeMag([...events, ...liveEvents]); };
window.__mc = v => { document.getElementById('regionMcOverride').value = v; renderTimeMag([...events, ...liveEvents]); };
window.__oku = () => { const tx = id => { const el = document.getElementById(id); if (!el) return null; const c = el.cloneNode(true); c.querySelectorAll('#mcUyariB, #mcUyariA').forEach(n => n.remove()); return c.textContent; };
  const sa = document.getElementById('tmSvgA');
  return { bSvg: document.getElementById('tmSvgB').innerHTML, bTxt: tx('tmStatsB'), aSvg: sa ? sa.innerHTML : null, aTxt: tx('tmStatsA'), grTxt: document.getElementById('tmStatsGR').textContent,
    uyariB: document.getElementById('mcUyariB') ? document.getElementById('mcUyariB').textContent : null, uyariA: !!document.getElementById('mcUyariA'),
    durum: typeof lastMcUyari !== 'undefined' && lastMcUyari ? JSON.parse(JSON.stringify(lastMcUyari)) : null, Mc: lastGrMc, csAktif: !!lastCs }; };
`;
const SEN = {
  birlesik:      { p: [[1971, 1997], [1998, null]], r: [36, 26, 42, 45] },
  birlesik_mc40: { p: [[1971, 1997], [1998, null]], r: [36, 26, 42, 45], mc: '4.0' },
  isc71_97:      { p: [[1971, 1997]], r: [36, 26, 42, 45] },
  emsc98:        { p: [[1998, null]], r: [36, 26, 42, 45] },
  basamak_test:  { p: [[1971, 1997]], r: [36, 26, 42, 45], cs: [['1971-01-01', '4.5'], ['1985-01-01', '4.0']] },
  basamak_oto:   { p: [[1971, 1997]], r: [36, 26, 42, 45], cs: [['1971-01-01', '5.0'], ['1984-01-01', '4.2'], ['1986-01-01', '4.8'], ['1990-01-01', '3.9']] },
  marmara:       { p: [[1998, null]], r: [40, 26, 41.5, 31] },
  // Geriye dönük uyumluluk (ChatGPT m. 3): GK74 açık, farklı Mc modları, basamaklar + GK74; geçici eksiklik (büyük artçı dizisi)
  birlesik_gk74:     { p: [[1971, 1997], [1998, null]], r: [36, 26, 42, 45], gk: true },
  isc71_97_mc45:     { p: [[1971, 1997]], r: [36, 26, 42, 45], mc: '4.5' },
  marmara_gk74:      { p: [[1998, null]], r: [40, 26, 41.5, 31], gk: true },
  basamak_test_gk74: { p: [[1971, 1997]], r: [36, 26, 42, 45], cs: [['1971-01-01', '4.5'], ['1985-01-01', '4.0']], gk: true },
  kmaras:            { p: [[1998, null]], r: [36.5, 35.5, 38.5, 39] },
  kmaras_gk74:       { p: [[1998, null]], r: [36.5, 35.5, 38.5, 39], gk: true },
};
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), S = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    S[ad] = {}; const hat = [];
    for (const [k, c] of Object.entries(SEN)) {
      const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR);
      await p.evaluate(a => __kur(...a), [c.p, ...c.r]); if (c.gk) await p.evaluate(async () => { await toggleRegionDecluster(); applyGk74Filter(regionEvents); renderTimeMag([...events, ...liveEvents]); }); if (c.mc) await p.evaluate(v => __mc(v), c.mc); if (c.cs) await p.evaluate(s => __cs(s), c.cs); await p.waitForTimeout(200);
      S[ad][k] = await p.evaluate(() => __oku());
      if (ad === 'sonra' && k === 'birlesik') { const el = await p.$('#tmStatsB'); await el.scrollIntoViewIfNeeded(); await el.screenshot({ path: path.join(__dirname, 'mc_uyari_birlesik.png') }); }
      hat.push(...hatalar); await ctx.close();
    }
    S[ad].hatalar = hat;
  }
  const O = S.once, Y = S.sonra;
  for (const k of Object.keys(SEN)) { const o = O[k], y = Y[k];
    ok(o.bSvg === y.bSvg && o.bTxt === y.bTxt && o.aSvg === y.aSvg && o.aTxt === y.aTxt && o.grTxt === y.grTxt, `(1) ${k}: b(t) ve a(t) grafikleri, uyarı dışındaki b(t)/a(t) metinleri ve G–R metni önce = sonra`);
    ok(!!y.uyariB === y.uyariA && (!!y.uyariB) === !!(y.durum && y.durum.on) && !o.uyariB, `(2) ${k}: uyarı ${y.uyariB ? 'VAR' : 'yok'} (b(t) ve a(t) tutarlı; önce yok)`);
    const d = y.durum; console.log(`     ${k}: Mc = ${y.Mc}${y.csAktif ? ' (basamaklı)' : ''}${SEN[k].gk ? ', GK74' : ''}; tür ${d && d.on ? d.tur : '—'}; ` + (d && d.sureOran !== undefined ? `süre oranı %${(100 * d.sureOran).toFixed(1)}; ` : '') + (d ? ((d.tur === 'tekMc' || d.tur === 'gecici') ? `Mc(t) ${d.mcMin?.toFixed(2)}–${d.mcMax?.toFixed(2)}, 'inc' %${(100 * d.frac).toFixed(0)}${d.on ? `, önerilen Mc ${d.oner}` : ''}` : d.tur === 'basamak' ? `dönemler: ${d.donemler.map(q => `eşik ${q.mc} < veri ${q.mcData}`).join('; ')}` : 'uyarı koşulu yok') : '—'));
  }
  ok(Y.birlesik.durum && Y.birlesik.durum.on && /Katalog Tamlık Uyarısı/.test(Y.birlesik.uyariB), '(3) Birleşik ISC + EMSC, otomatik Mc: uyarı gösteriliyor');
  { const d = Y.basamak_test.durum, p85 = d && d.donemler.find(q => new Date(q.t0).getUTCFullYear() === 1985);
    ok(!!p85 && p85.neden.includes('yıllık') && p85.yillar.some(q => q.y === 1986) && p85.yillar.some(q => q.y === 1988) && /1986: 4,8/.test(Y.basamak_test.uyariB),
      `(3) İyimser test basamağı (1985 M ≥ 4,0) yıllık Mc ile yakalanıyor: ${p85 ? p85.yillar.map(q => q.y + ': ' + q.mc).join(', ') : '—'} (Poisson raporu §4.5 ile tutarlı)`); }
  ok(Y.birlesik.durum.tur === 'tekMc' && Y.birlesik_gk74.durum.on && Y.birlesik_gk74.durum.tur === 'tekMc', '(3) Birleşik ISC + EMSC: kalıcı uyarı GK74 kapalı ve açıkken');
  ok(Object.values(Y).filter(v => v && v.durum).every(v => !v.durum.on || ['tekMc', 'gecici', 'basamak'].includes(v.durum.tur)), '(3) Tüm senaryolarda uyarı türü tanımlı (kalıcı / geçici / basamak)');
  ok(!O.hatalar.length && !Y.hatalar.length, `(4) Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length})` + (Y.hatalar.length ? ': ' + Y.hatalar.join(' | ') : ''));
  const ozet = {}; for (const k of Object.keys(SEN)) ozet[k] = { Mc: Y[k].Mc, durum: Y[k].durum, uyari: Y[k].uyariB };
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify({ senaryolar: SEN, sonuc: ozet, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
