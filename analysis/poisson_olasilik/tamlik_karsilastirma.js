// Tamlık modeli duyarlılığı (2026-10-27): aynı bölge ve pencerede (Türkiye, ISC 1971–1997, dikdörtgen 36–42° K / 26–45° D, T = 27 yıl)
// farklı tamlık seçimleriyle b, λ(≥6), λ(≥7) ve gözlenen–öngörülen (N_gözl, λT, kesin Poisson p).
// Seçimler:
//   A  test basamakları (önceki kabul testinde): 1971 M ≥ 4,5; 1985 M ≥ 4,0 — doğrulanmamış, yalnız test amaçlı
//   B  katalog üst verisi (data/eq_historical.json completeness): 1960–1998 Mc = 4,5 (ISC) → tek basamak 1971 M ≥ 4,5
//   C  uygulamanın "Otomatik öner"i (csSuggest: yıllık maksimum eğrilik Mc + 0,2; ≥ 50 olaylı yıllar; 0,3 değişimde yeni basamak)
//   D  tek Mc yolu, elle Mc = 4,5 (B ile aynı eşik; Aki–Utsu) — aynı veri alt kümesinde yöntem farkını ayırmak için
//   E  tek Mc yolu, otomatik Mc (3,7) — panel varsayılanı
// Ayrıca yıllık Mc (computeMc, ≥ 50 olaylı yıllar) tablosu.
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/poisson_olasilik/tamlik_karsilastirma.js
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), LD = process.env.LEAFLET_DIR;
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]), f = path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT)) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); }); });
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), ctx = await br.newContext({ viewport: { width: 1400, height: 1000 } }), p = await ctx.newPage(), hatalar = [];
  p.on('pageerror', e => hatalar.push(String(e)));
  await ctx.route('**/*', rt => { const u = rt.request().url();
    if (u.startsWith('http://127.0.0.1')) return rt.continue();
    if (/leaflet@1\.9\.4\/dist\/leaflet\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.js'), contentType: 'text/javascript' });
    if (/leaflet@1\.9\.4\/dist\/leaflet\.css/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.css'), contentType: 'text/css' });
    if (/leaflet-heat\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet.heat/dist/leaflet-heat.js'), contentType: 'text/javascript' });
    return rt.abort(); });
  await p.routeWebSocket(/.*/, ws => ws.close()).catch(() => {});
  await p.goto(`http://127.0.0.1:${srv.address().port}/`, { waitUntil: 'load' });
  await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function' && typeof map !== 'undefined'); await p.waitForTimeout(400);
  const R = await p.evaluate(async () => {
    const bekle = async () => { for (let i = 0; i < 600; i++) { if (!regionLoading && regionEvents && regionEvents.length) return; await new Promise(r => setTimeout(r, 50)); } };
    await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="1971"]'), 1971, 1997);
    regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(36, 26) }); map.fire('mousemove', { latlng: L.latLng(42, 45) }); await regionMouseUp(); await bekle();
    if (!showTimeMag) toggleTimeMag();
    const out = { meta: historicalCache.completeness, yillik: [] };
    // Yıllık Mc (uygulamanın computeMc'si; ≥ 50 olaylı yıllar)
    const by = {}; lastTmEvList.forEach(e => { const y = e.time.getUTCFullYear(); (by[y] = by[y] || []).push(e); });
    Object.keys(by).map(Number).sort((a, b) => a - b).forEach(y => out.yillik.push([y, by[y].length, by[y].length >= 50 ? computeMc(by[y]) : null]));
    const setPM = M => { document.getElementById('grPM').value = String(M); };
    const oku = () => { const q = lastGrPois; return q ? { b: q.b, lam: q.lam, obs: q.obs ? { n: q.obs.nObs, mu: q.obs.mu, p: q.obs.p, T: q.obs.Tobs } : null, compWarn: !!q.compWarn } : null; };
    const iki = () => { const r = {}; for (const M of [6, 7]) { setPM(M); renderTimeMag([...events, ...liveEvents]); r['M' + M] = oku(); } return r; };
    const weichert = steps => { csSteps = steps.map(([start, mc]) => ({ start, mc })); csEnabled = true; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = true; csRenderRows(); onCsChange(true);
      const r = iki(); r.donem = lastCs.periods.map(q => [new Date(q.t0).toISOString().slice(0, 10), new Date(q.t1).toISOString().slice(0, 10), q.mc]); r.N = lastGrFit ? lastGrFit.N : null; return r; };
    const tekMc = mc => { csEnabled = false; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = false; onCsChange(true);
      document.getElementById('regionMcOverride').value = mc === null ? '' : String(mc); const r = iki(); r.mc = lastGrSimple ? lastGrSimple.mc : null; r.n = lastGrSimple ? lastGrSimple.n : null;
      document.getElementById('regionMcOverride').value = ''; return r; };
    out.A = weichert([['1971-01-01', '4.5'], ['1985-01-01', '4.0']]);
    out.B = weichert([['1971-01-01', '4.5']]);
    csSteps = []; csSuggest(); out.C_basamak = csSteps.map(s => [s.start, s.mc]); out.C = csSteps.length ? weichert(out.C_basamak) : null;
    out.D = tekMc(4.5); out.E = tekMc(null);
    // Gözlenen sayılar (pencere, M ≥ 6 ve M ≥ 7)
    out.gozlenen = { M6: lastTmEvList.filter(e => (e.mw ?? e.mag) >= 6 - 1e-9).length, M7: lastTmEvList.filter(e => (e.mw ?? e.mag) >= 7 - 1e-9).length };
    return out; });
  R.hatalar = hatalar;
  fs.writeFileSync(path.join(__dirname, 'tamlik_karsilastirma.json'), JSON.stringify(R, null, 1));
  const f = (x, d = 3) => x === null || x === undefined ? '—' : x.toFixed(d), pp = v => v < 1e-3 ? v.toExponential(1) : v.toFixed(3);
  console.log('Katalog üst verisi:', JSON.stringify(R.meta));
  console.log('Yıllık Mc (≥ 50 olay):', R.yillik.filter(r => r[2] !== null).map(r => `${r[0]}:${r[2]}(${r[1]})`).join(' '));
  console.log('C (Otomatik öner) basamakları:', JSON.stringify(R.C_basamak));
  console.log(`Gözlenen: M≥6 ${R.gozlenen.M6}, M≥7 ${R.gozlenen.M7} (27 yıl)`);
  for (const [k, ad] of [['A', 'Weichert, test basamakları'], ['B', 'Weichert, katalog üst verisi 1971 M≥4,5'], ['C', 'Weichert, Otomatik öner'], ['D', 'Tek Mc = 4,5 (elle)'], ['E', 'Tek Mc otomatik']]) {
    const r = R[k]; if (!r) { console.log(k, ad, '—'); continue; }
    console.log(`${k} ${ad}: b = ${f(r.M6.b)}${r.mc !== undefined ? `, Mc = ${r.mc}, N(≥Mc) = ${r.n}` : `, N = ${r.N}`} | M≥6: beklenen ${f(r.M6.obs.mu, 1)} (gözl ${r.M6.obs.n}), p = ${pp(r.M6.obs.p)} | M≥7: beklenen ${f(r.M7.obs.mu, 2)} (gözl ${r.M7.obs.n}), p = ${pp(r.M7.obs.p)}${r.M6.compWarn ? ' | tamlık uyarısı' : ''}`);
  }
  console.log('Sayfa hatası:', hatalar.length);
  await br.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
