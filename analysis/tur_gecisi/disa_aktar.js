// Büyüklük türü geçişi (MD → ML) analizi — veri dışa aktarma (2026-11-01). poisson-donem-sinamasi dalındaki disa_aktar.js'in kopyası; olaylara üç alan eklendi:
// mt (ham büyüklük türü dizgisi, büyük/küçük harf korunur: 'ML' EMSC'nin, 'ml' katkıcının), lat, lon. Ham veri yalnız okunur; uygulamanın kendi kodu (bölge sorgusu, GK74,
// büyüklük dönüşümü, computeMc) tarayıcıda çalıştırılır ve olay listesi geçici bir JSON'a yazılır (depoya eklenmez; analiz.js okur).
// Senaryolar:
//   tr_emsc       Türkiye kutusu 36–42° K / 26–45° D, EMSC 1998– (ana sınama)
//   mar_emsc      Marmara 40–41,5° K / 26–31° D, EMSC 1998– (ikinci bölge, sağlamlık)
//   tr_isc_emsc   Türkiye kutusu, ISC 1971–1997 + EMSC 1998– (ikincil sınama: katalog sınırı)
// Her olay: t (ms), m (ham, dönüşüm yok), ms (Scordilis 2006 dönüşümü uygulanabiliyorsa), tur, gk (GK74 sonrası kalıyor mu).
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/poisson_donem/disa_aktar.js <çıktı.json>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), LD = process.env.LEAFLET_DIR, OUT = process.argv[2];
if (!OUT || !LD) { console.error('kullanım: LEAFLET_DIR=... node disa_aktar.js <çıktı.json>'); process.exit(2); }
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]), f = path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT)) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); }); });
const SEN = {
  tr_emsc:     { p: [[1998, null]], r: [36, 26, 42, 45] },
  mar_emsc:    { p: [[1998, null]], r: [40, 26, 41.5, 31] },
  tr_isc_emsc: { p: [[1971, 1997], [1998, null]], r: [36, 26, 42, 45] },
};
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), out = { uretim: new Date().toISOString(), senaryolar: {} }, hatalar = [];
  for (const [ad, c] of Object.entries(SEN)) {
    const ctx = await br.newContext(), p = await ctx.newPage(); p.on('pageerror', e => hatalar.push(String(e)));
    await ctx.route('**/*', rt => { const u = rt.request().url();
      if (u.startsWith('http://127.0.0.1')) return rt.continue();
      if (/leaflet@1\.9\.4\/dist\/leaflet\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.js'), contentType: 'text/javascript' });
      if (/leaflet@1\.9\.4\/dist\/leaflet\.css/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.css'), contentType: 'text/css' });
      if (/leaflet-heat\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet.heat/dist/leaflet-heat.js'), contentType: 'text/javascript' });
      return rt.abort(); });
    await p.routeWebSocket(/.*/, ws => ws.close()).catch(() => {});
    await p.goto(`http://127.0.0.1:${srv.address().port}/`, { waitUntil: 'load' });
    await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function' && typeof map !== 'undefined'); await p.waitForTimeout(300);
    out.senaryolar[ad] = await p.evaluate(async c => {
      for (const [a, b] of c.p) await toggleHistoricalWindow(document.querySelector(b ? '.tbtn[data-hist="' + a + '"]' : '.tbtn[data-hist="' + a + '"]:not([data-hist-src])'), a, b);
      regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(c.r[0], c.r[1]) }); map.fire('mousemove', { latlng: L.latLng(c.r[2], c.r[3]) }); await regionMouseUp();
      for (let i = 0; i < 600 && (regionLoading || !regionEvents || !regionEvents.length); i++) await new Promise(r => setTimeout(r, 50));
      const ham = regionEvents.slice();
      await toggleRegionDecluster(); applyGk74Filter(ham); const keep = gk74Cache.keep;
      const sc = applyMagConversionForDisplay(ham, 'scordilis2006').list;
      const tur = e => { const t = (e.mtype || '?').toLowerCase(); return t === 'mb' ? 'mb' : t === 'ms' ? 'Ms' : t === 'ml' ? 'ML' : t === 'md' ? 'MD' : /^mw/.test(t) ? 'Mw' : 'diğer'; };
      const olaylar = ham.map((e, i) => ({ t: +e.time, m: panelBaseMag(e), ms: sc[i].mw ?? sc[i].mag, tur: tur(e), mt: e.mtype || '?', lat: e.lat, lon: e.lon, gk: keep.has(e) ? 1 : 0 })).sort((a, b) => a.t - b.t);
      // Mc'ler uygulamanın computeMc'siyle (maks. eğrilik + 0,2): dönem alt kümeleri, ham ve GK74 ayrı
      const altkume = (t0, t1, gk) => ham.filter(e => +e.time >= t0 && +e.time < t1 && (!gk || keep.has(e)));
      const Y = y => Date.UTC(y, 0, 1), donemler = { d1998_2011: [Y(1998), Y(2012)], d2012_son: [Y(2012), Y(2100)], d1971_1997: [Y(1971), Y(1998)], d1998_son: [Y(1998), Y(2100)],
        d2012_2018: [Y(2012), Y(2019)], d2019_son: [Y(2019), Y(2100)], d1998_2003: [Y(1998), Y(2004)], d2004_2009: [Y(2004), Y(2010)] };   // son dördü: homojen tür dönemleri (ML 2012–, MD 1998–2009)
      const mc = {}; for (const [k, [a, b]] of Object.entries(donemler)) for (const gk of [false, true]) { const s = altkume(a, b, gk); mc[`${k}|${gk ? 'gk74' : 'ham'}`] = s.length >= 50 ? { mc: computeMc(s), n: s.length } : { mc: null, n: s.length }; }
      return { bolge: c.r, pencere: c.p, pencereBas: +regionWindowStart, pencereSon: +regionWindowEnd, n: ham.length, nGk: keep.size, mc, olaylar };
    }, c);
    console.log(`${ad}: ${out.senaryolar[ad].n} olay (GK74 sonrası ${out.senaryolar[ad].nGk}); pencere ${new Date(out.senaryolar[ad].pencereBas).toISOString().slice(0, 10)} → ${new Date(out.senaryolar[ad].pencereSon).toISOString().slice(0, 10)}; Mc ${JSON.stringify(Object.fromEntries(Object.entries(out.senaryolar[ad].mc).filter(([, v]) => v.mc !== null).map(([k, v]) => [k, v.mc])))}`);
    await ctx.close();
  }
  out.hatalar = hatalar; fs.writeFileSync(OUT, JSON.stringify(out)); console.log('yazıldı:', OUT, (fs.statSync(OUT).size / 1e6).toFixed(1), 'MB; sayfa hatası', hatalar.length);
  await br.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
