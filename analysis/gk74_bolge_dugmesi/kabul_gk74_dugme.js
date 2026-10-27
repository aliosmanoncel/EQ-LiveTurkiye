// Kabul testi (2026-10-27): Bölge Analizi'nde dikdörtgen, poligon ve linkle açılan bölgede GK74 düğmesi görünür.
// Kapsam: yalnız düğme görünürlüğü; GK74 yöntemi, bağlamlı GK74 (yalnız daire), Araştırma Bölgesi ve küresel ISC-GEM penceresi değişmez.
// Aynı senaryolar ÖNCE (verilen index.html, ör. main) ve SONRA (depodaki index.html) sayfalarında çalışır. Veri: yerel tarihsel katalog
// (Türkiye modu, ISC 1971–1997 penceresi) — ağ gerekmez. Dış istekler engellenir; Leaflet yerel kopyadan (LEAFLET_DIR).
// Kabul koşulları: (1) dikdörtgen/poligon/link (dikdörtgen, poligon, daire) bölgelerinde düğme görünür; (2) aynı 6 köşeli poligon
// Bölge Analizi'nden ve Araştırma Bölgesi'nden aynı olay ve ana şok sayısını verir; (3) daire davranışı ve bağlamlı GK74 kısıtı
// (poligon/dikdörtgende kutucuk devre dışı, dairede etkin) önce/sonra aynı; ayrıca Araştırma Bölgesi poligonu ve küresel ISC-GEM penceresi önce = sonra.
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/gk74_bolge_dugmesi/kabul_gk74_dugme.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_gk74_dugme.js <önceki_index.html>'); process.exit(2); }
const srv = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split('?')[0]), f = u === '/__once.html' ? ONCE : path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT) && f !== ONCE) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); });
});
let pass = 0, fail = 0; const kayit = [];
const ok = (c, m) => { (c ? pass++ : fail++); kayit.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };
async function sayfa(br, yol) {
  const ctx = await br.newContext(), p = await ctx.newPage(), hatalar = [];
  p.on('pageerror', e => hatalar.push(String(e)));
  await ctx.route('**/*', rt => { const u = rt.request().url();
    if (u.startsWith('http://127.0.0.1')) return rt.continue();
    if (/leaflet@1\.9\.4\/dist\/leaflet\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.js'), contentType: 'text/javascript' });
    if (/leaflet@1\.9\.4\/dist\/leaflet\.css/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.css'), contentType: 'text/css' });
    if (/leaflet-heat\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet.heat/dist/leaflet-heat.js'), contentType: 'text/javascript' });
    return rt.abort(); });
  await p.routeWebSocket(/.*/, ws => ws.close()).catch(() => {});
  await p.goto(`http://127.0.0.1:${srv.address().port}${yol}`, { waitUntil: 'load' });
  await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function' && typeof map !== 'undefined');
  await p.waitForTimeout(400);
  return { p, ctx, hatalar };
}
const POLY = [[38.0, 27.0], [39.5, 28.0], [40.0, 30.0], [39.0, 31.5], [37.5, 30.5], [37.0, 28.5]];   // 6 köşe (>4: Araştırma Bölgesi de poligon olarak sorgular)
// Tarayıcı içi yardımcılar: tarihsel pencereyi aç, bölge kur, GK74'ü çalıştır, durum oku
const KUR = `
window.__bekle = async () => { for (let i = 0; i < 400; i++) { if (!regionLoading && regionEvents && regionEvents.length) return true; await new Promise(r => setTimeout(r, 50)); } return false; };
window.__durum = () => { const b = document.getElementById('btnRegionDecluster'), cb = document.getElementById('regionDeclusterCtx');
  return { dugme: !!b && b.style.display !== 'none', ctxDevreDisi: !!(cb && cb.disabled), sekil: regionIsCircle ? 'daire' : regionIsPolygon ? 'poligon' : (regionRect ? 'dikdörtgen' : 'yok'),
           kose: regionIsPolygon ? regionRect.getLatLngs()[0].length : null, baglamDestegi: regionCtxSupported() }; };
window.__gk = async (ctxAcik) => { const cb = document.getElementById('regionDeclusterCtx'); if (cb && !cb.disabled) { cb.checked = !!ctxAcik; onRegionDeclusterCtxChange(); }
  await toggleRegionDecluster(); if (ctxAcik && typeof regionCtxPending !== 'undefined' && regionCtxPending) await regionCtxPending;
  applyGk74Filter(regionEvents);
  const r = { n: regionEvents.length, ana: gk74Cache ? gk74Cache.keep.size : null, baglam: !!(gk74Cache && gk74Cache.ctx), metin: document.getElementById('btnRegionDecluster').textContent };
  await toggleRegionDecluster(); return r; };
`;
async function hazirla(p) { await p.evaluate(KUR); await p.evaluate(async () => { const b = document.querySelector('.tbtn[data-hist="1971"]'); await toggleHistoricalWindow(b, 1971, 1997); }); }
const senaryo = {
  dikdortgen: async p => p.evaluate(async () => { regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(37, 26) }); map.fire('mousemove', { latlng: L.latLng(40, 30) });
    await regionMouseUp(); await __bekle(); return { ...__durum(), gk: await __gk(false) }; }),
  bolge_poligon: async p => p.evaluate(async P => { polygonSelectStart(); for (const [a, b] of P) map.fire('click', { latlng: L.latLng(a, b) });
    await polygonFinish(); await __bekle(); return { ...__durum(), gk: await __gk(false) }; }, POLY),
  arastirma_poligon: async p => p.evaluate(async P => { regionDeselect(); litRegionLayer = L.polygon(P); litRegionCommitToQuery(); await __bekle();
    return { ...__durum(), gk: await __gk(false) }; }, POLY),
  arastirma_daire: async p => p.evaluate(async () => { regionDeselect(); litRegionLayer = L.circle([38.5, 28.5], { radius: 120000 }); litRegionCommitToQuery(); await __bekle();
    const d = __durum(); return { ...d, gk: await __gk(false), gkBaglam: await __gk(true) }; }),
};
const LINK = { link_dikdortgen: '?rminlat=37&rmaxlat=40&rminlon=26&rmaxlon=30', link_poligon: '?rminlat=37&rmaxlat=40&rminlon=27&rmaxlon=31.5&rpoly=' + POLY.map(x => x.join(',')).join(';'),
               link_daire: '?rminlat=37.4&rmaxlat=39.6&rminlon=27.1&rmaxlon=29.9&rcirc=38.5,28.5,120' };
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), S = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    S[ad] = {}; const hat = [];
    for (const [k, f] of Object.entries(senaryo)) { const { p, ctx, hatalar } = await sayfa(br, yol); await hazirla(p); S[ad][k] = await f(p); hat.push(...hatalar); await ctx.close(); }
    // Link: sayfa linkle açılır (canlı kaynak test ortamında erişilemez), sonra yerel tarihsel pencere açılınca bölge sorgusu yeniden çalışır
    for (const [k, q] of Object.entries(LINK)) { const { p, ctx, hatalar } = await sayfa(br, yol + q); await p.waitForTimeout(800); await p.evaluate(KUR);
      const ilk = await p.evaluate(() => __durum()); await hazirla(p); await p.evaluate(() => __bekle());
      S[ad][k] = { ...(await p.evaluate(() => __durum())), acilista_dugme: ilk.dugme, gk: await p.evaluate(() => __gk(false)) }; hat.push(...hatalar); await ctx.close(); }
    { const { p, ctx, hatalar } = await sayfa(br, yol); S[ad].iscgem = await p.evaluate(async () => { setScope('global'); const b = document.querySelector('.tbtn[data-hist-src="ISCGEM-GLOBAL"]');
        await toggleHistoricalWindow(b, 1904, 2021, 'ISCGEM-GLOBAL'); return { n: events.length, ipucu: document.getElementById('histHint').textContent }; }); hat.push(...hatalar); await ctx.close(); }
    S[ad].hatalar = hat;
  }
  const O = S.once, Y = S.sonra;
  // (1) düğme görünürlüğü
  ok(Y.dikdortgen.dugme && Y.dikdortgen.sekil === 'dikdörtgen', `(1) Bölge Analizi dikdörtgen: düğme görünür (önce ${O.dikdortgen.dugme ? 'görünür' : 'gizli'})`);
  ok(Y.bolge_poligon.dugme && Y.bolge_poligon.sekil === 'poligon' && Y.bolge_poligon.kose === 6, `(1) Bölge Analizi poligon (6 köşe): düğme görünür (önce ${O.bolge_poligon.dugme ? 'görünür' : 'gizli'})`);
  for (const k of Object.keys(LINK)) ok(Y[k].dugme && Y[k].acilista_dugme, `(1) ${k}: düğme açılışta ve sorgudan sonra görünür (önce açılışta ${O[k].acilista_dugme ? 'görünür' : 'gizli'}; şekil ${Y[k].sekil})`);
  // (2) aynı poligon iki yoldan aynı sonuç
  const a = Y.bolge_poligon.gk, b = Y.arastirma_poligon.gk;
  ok(Y.arastirma_poligon.sekil === 'poligon' && Y.arastirma_poligon.kose === 6 && a.n === b.n && a.ana === b.ana && a.n > 0 && a.ana < a.n,
    `(2) Aynı poligon: Bölge Analizi ${a.n} olay → ${a.ana} ana şok; Araştırma Bölgesi ${b.n} → ${b.ana}`);
  ok(Y.dikdortgen.gk.n > 0 && Y.dikdortgen.gk.ana > 0 && Y.dikdortgen.gk.ana <= Y.dikdortgen.gk.n && !Y.dikdortgen.gk.baglam, `Dikdörtgende GK74 çalışıyor: ${Y.dikdortgen.gk.n} → ${Y.dikdortgen.gk.ana} (bağlamsız)`);
  // (3) daire ve bağlam kısıtı
  ok(JSON.stringify(O.arastirma_daire) === JSON.stringify(Y.arastirma_daire) && Y.arastirma_daire.dugme && !Y.arastirma_daire.ctxDevreDisi && Y.arastirma_daire.gkBaglam.baglam,
    `(3) Daire önce = sonra: ${Y.arastirma_daire.gk.n} → ${Y.arastirma_daire.gk.ana} (bağlamsız), ${Y.arastirma_daire.gkBaglam.ana} (bağlamlı); bağlam kutucuğu etkin`);
  ok(Y.dikdortgen.ctxDevreDisi && Y.bolge_poligon.ctxDevreDisi && Y.arastirma_poligon.ctxDevreDisi && !Y.bolge_poligon.gk.baglam, '(3) Bağlamlı GK74 kutucuğu dikdörtgen ve poligonda devre dışı; bağlam kullanılmadı');
  ok(!Y.link_daire.ctxDevreDisi && Y.link_poligon.ctxDevreDisi && Y.link_dikdortgen.ctxDevreDisi, '(3) Link: bağlam kutucuğu dairede etkin, poligon/dikdörtgende devre dışı');
  ok(['dikdortgen', 'bolge_poligon', 'arastirma_poligon', 'link_dikdortgen', 'link_poligon'].every(k => !Y[k].baglamDestegi && !Y[k].gk.baglam) && Y.arastirma_daire.baglamDestegi && Y.link_daire.baglamDestegi,
    '(3) regionCtxSupported(): yalnız dairede true; dikdörtgen/poligonda GK74 bağlam kullanmadı');
  ok(Y.link_poligon.gk.n === a.n && Y.link_poligon.gk.ana === a.ana, `Link poligonu da aynı sonucu verdi: ${Y.link_poligon.gk.n} → ${Y.link_poligon.gk.ana}`);
  // etkilenmemesi gerekenler
  ok(JSON.stringify(O.arastirma_poligon) === JSON.stringify(Y.arastirma_poligon), `Araştırma Bölgesi poligonu önce = sonra (${Y.arastirma_poligon.gk.n} → ${Y.arastirma_poligon.gk.ana})`);
  ok(O.dikdortgen.gk.n === Y.dikdortgen.gk.n && O.bolge_poligon.gk.n === Y.bolge_poligon.gk.n, `Bölge sorgusu olay sayıları önce = sonra (dikdörtgen ${Y.dikdortgen.gk.n}, poligon ${Y.bolge_poligon.gk.n}) — yalnız düğme değişti`);
  ok(O.iscgem.n === Y.iscgem.n && O.iscgem.ipucu === Y.iscgem.ipucu && Y.iscgem.n === 74159, `Küresel ISC-GEM penceresi önce = sonra (${Y.iscgem.n} olay)`);
  ok(!O.hatalar.length && !Y.hatalar.length, `Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length})` + (Y.hatalar.length ? ': ' + Y.hatalar.join(' | ') : ''));
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify({ poligon: POLY, link: LINK, sonuc: S, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
