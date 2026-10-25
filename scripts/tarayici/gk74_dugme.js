// Tarayıcı testi (CI dışı, elle): GK74 düğmesinin durumları ve sonuç raporu (2026-10-25).
// Senaryo: tarihsel katalog (ağ gerektirmez) → bölge → aç (hemen ÇALIŞIYOR, sonra AÇIK + rapor) → kapat → açıkken yavaş yüklenen
// yeni bölge (yükleme sırasında ÇALIŞIYOR, sonra yeni sayılar) → bölgeyi temizle (KAPALI). Raporun ana şok sayısı applyGk74Filter ile karşılaştırılır.
// Ortam: LB = leaflet@1.9.4 ve leaflet.heat@0.2.0 klasörü (npm pack), SP = çıktı klasörü; depo kökü http://localhost:8772'de sunulur.
const { chromium } = require('playwright'); const LB = process.env.LB, SP = process.env.SP;
(async () => { const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1400, height: 950 } })).newPage(); const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 160)); });
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.js/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.js', contentType: 'application/javascript' }));
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.css/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.css', contentType: 'text/css' }));
  await p.route(/leaflet-heat\.js/, r => r.fulfill({ path: LB + '/leaflet.heat-0.2.0/dist/leaflet-heat.js', contentType: 'application/javascript' }));
  await p.route(u => !/^http:\/\/localhost/.test(u.href) && !/leaflet/.test(u.href), r => r.abort());
  await p.goto('http://localhost:8772/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => typeof events !== 'undefined' && events.length > 100, null, { timeout: 90000 });
  await p.evaluate(() => { const bt = document.querySelector('[data-hist="1971"][data-hist-end="1997"]'); toggleHistoricalWindow(bt, 1971, 1997); });
  await p.waitForFunction(() => events.length > 3000, null, { timeout: 90000 });
  const L = () => p.evaluate(() => ({ btn: document.getElementById('btnRegionDecluster').textContent, cls: document.getElementById('btnRegionDecluster').className,
    rep: (document.getElementById('gkReport').style.display === 'none' ? '(gizli)' : document.getElementById('gkReport').innerText.replace(/\s+/g, ' ')) }));
  const region = (s, n, w, e) => p.evaluate(([s, n, w, e]) => { if (regionRect) map.removeLayer(regionRect); const bnd = L.latLngBounds([s, w], [n, e]); regionIsCircle = false; regionIsPolygon = false;
    regionRect = L.rectangle(bnd).addTo(map); document.getElementById('btnRegionDecluster').style.display = ''; return fetchRegionEvents(bnd); }, [s, n, w, e]);
  const out = {};
  await region(38, 41, 26, 31); out['1 bölge (Marmara), kapalı'] = await L();
  await p.evaluate(() => { window.__p = toggleRegionDecluster(); }); out['2a tıklamadan hemen sonra'] = await L();
  await p.evaluate(() => window.__p); out['2b tamamlandı'] = await L();
  await p.screenshot({ path: SP + '/gk_acik.png', clip: await p.evaluate(() => { const r = document.getElementById('btnRegionDecluster').getBoundingClientRect(), q = document.getElementById('gkReport').getBoundingClientRect();
    return { x: Math.max(0, Math.min(r.x, q.x) - 6), y: Math.max(0, r.y - 6), width: Math.max(r.width, q.width) + 12, height: q.bottom - r.y + 12 }; }) });
  out['2c bilgi kutusu tutarlı mı'] = await p.evaluate(() => { const n1 = applyGk74Filter(regionEvents).length; return { regionEvents: regionEvents.length, anaSok: n1, raporda: document.getElementById('gkReport').innerText.includes(n1.toLocaleString('tr-TR')) }; });
  await p.evaluate(() => toggleRegionDecluster()); out['3 kapatıldı'] = await L();
  await p.evaluate(() => toggleRegionDecluster());
  await p.evaluate(() => { const orig = fetchRegionEventsFromHistorical; window.fetchRegionEventsFromHistorical = async bnd => { await new Promise(r => setTimeout(r, 2000)); return orig(bnd); }; });
  const pr = region(36, 39, 35, 40); await p.waitForTimeout(500); out['4a açıkken yeni bölge yüklenirken'] = await L(); await pr; out['4b yeni bölge (Doğu Anadolu) hazır'] = await L();
  await p.evaluate(() => { const nb = document.querySelector('[onclick*="clearRegion"]'); regionDeselect(); }); out['5 bölge temizlendi'] = await L();
  out.hatalar = errs.filter(e => !/Failed to load|ERR_|net::|seismicportal/.test(e));
  console.log(JSON.stringify(out, null, 1)); await b.close(); })();
