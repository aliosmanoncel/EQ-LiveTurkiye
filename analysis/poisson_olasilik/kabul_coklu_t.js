// Kabul testi (2026-11-02, 2a): G–R panelindeki Poisson satırında 10, 50 ve 100 yıllık olasılıklar aynı anda.
// Aynı senaryolar ÖNCE (verilen index.html, ör. main 0408c0e) ve SONRA (depodaki index.html) sayfalarında çalışır (senaryolar kabul_poisson.js ile aynı).
// Kabul koşulları:
//   (1) Mevcut çıktılar değişmez: G–R grafiği ve metni önce = sonra; Poisson satırı yeni süre satırı (#grPoisPt) çıkarılınca önce = sonra;
//       λ, Tr aralığı, kullanıcının t'si için P aralığı (ci.lamLo/lamHi/pLo/pHi, B, nFail) birebir aynı (bootstrap akışı değişmedi).
//   (2) Gösterilen süreler {10, 50, 100} ∪ {t}, artan sırada.
//   (3) Her süre için P = 1 − e^(−λt) (aynı λ); kullanıcının t'si için aralık mevcut satırın aralığıyla birebir aynı.
//   (4) Tek Mc yolunda aralıklar sayfadan bağımsız yeniden hesapla aynı: grBootDraws(n, b, Mc, ΔM, B, tohum) çekilişlerinden λ*, P*(t) yüzdelikleri.
//   (5) Ekrandaki yüzdeler bu sayılarla aynı. (6) Sayfa hatası yok.
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/poisson_olasilik/kabul_coklu_t.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_coklu_t.js <önceki_index.html>'); process.exit(2); }
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
  await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function' && typeof map !== 'undefined');
  await p.waitForTimeout(400);
  return { p, ctx, hatalar };
}
// Tarayıcı içi: pencere + bölge + Time-Mag; durum okuma (Poisson satırı ayrı, kalan metin ayrı)
const KUR = `
window.__bekle = async () => { for (let i = 0; i < 600; i++) { if (!regionLoading && regionEvents && regionEvents.length) return true; await new Promise(r => setTimeout(r, 50)); } return false; };
window.__kur = async () => { await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="1971"]'), 1971, 1997);
  regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(36, 26) }); map.fire('mousemove', { latlng: L.latLng(42, 45) }); await regionMouseUp(); await __bekle();
  if (!showTimeMag) toggleTimeMag(); else renderTimeMag([...events, ...liveEvents]); };
window.__oku = () => { const st = document.getElementById('tmStatsGR'), row = document.getElementById('grPoisRow');
  const c = st.cloneNode(true); const r = c.querySelector('#grPoisRow'); if (r) r.remove();
  return { svg: document.getElementById('tmSvgGR').innerHTML, metin: c.textContent, pois: row ? row.textContent : null,
    pois_n: typeof lastGrPois !== 'undefined' && lastGrPois ? JSON.parse(JSON.stringify(lastGrPois)) : null,
    simple: typeof lastGrSimple !== 'undefined' && lastGrSimple ? { ...lastGrSimple } : null,
    fnBest: typeof lastGrFit !== 'undefined' && lastGrFit && lastGrFit.fnBest && typeof lastGrPois !== 'undefined' && lastGrPois ? lastGrFit.fnBest(lastGrPois.M) : null,
    T: regionWindowStart && regionWindowEnd ? (regionWindowEnd - regionWindowStart) / (365.25 * 864e5) : null, url: location.search,
    mObsMax: lastGrEvList ? Math.max(...lastGrEvList.map(e => e.mw ?? e.mag)) : null }; };
window.__set = (id, v) => { const e = document.getElementById(id); if (e) { e.value = v; onGrBinSizeChange(); } };
window.__gk = async on => { if (!!regionDeclusterOn !== on) { await toggleRegionDecluster(); applyGk74Filter(regionEvents); } renderTimeMag([...events, ...liveEvents]); };
window.__cs = on => { if (on) { csSteps = [{ start: '1971-01-01', mc: '4.5' }, { start: '1985-01-01', mc: '4.0' }]; csEnabled = true; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = true; csRenderRows(); }
  else { csEnabled = false; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = false; } onCsChange(true); renderTimeMag([...events, ...liveEvents]); };
`;
const ADIM = [   // [ad, işlem]
  ['tekMc_gk74kapali', async p => {}],
  ['tekMc_M6_t75', async p => p.evaluate(() => { __set('grPM', '6'); __set('grPt', '75'); })],
  ['tekMc_M8_5', async p => p.evaluate(() => { __set('grPM', '8.5'); __set('grPt', '50'); })],
  ['tekMc_gk74acik', async p => p.evaluate(async () => { __set('grPM', '7'); await __gk(true); })],
  ['weichert_gk74acik', async p => p.evaluate(() => __cs(true))],
  ['weichert_gk74kapali', async p => p.evaluate(async () => { await __gk(false); })],
  ['weichert_mx75_M7', async p => p.evaluate(() => { __set('grMx', '7.5'); })],
  ['weichert_mx75_M8', async p => p.evaluate(() => { __set('grPM', '8'); })],
  ['weichert_M6', async p => p.evaluate(() => { __set('grMx', ''); __set('grPM', '6'); })],
  // Tamlık denetimi: pencerenin ilk yarısı boşsa uyarı (seçili pencere 1971–1997 iken 1900'den başlatılmış gibi; yalnız test için)
  ['tekMc_ilkYariBos', async p => p.evaluate(() => { __cs(false); __set('grMx', ''); __set('grPM', '7'); regionWindowStart = new Date('1900-01-01T00:00:00Z'); renderTimeMag([...events, ...liveEvents]); })],
];
const pc = v => v === null || !Number.isFinite(v) ? '—' : (100 * v < 0.1 && v > 0 ? '< 0,1' : (100 * v).toFixed(1).replace('.', ','));
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), S = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR); await p.evaluate(() => __kur()); await p.waitForTimeout(300);
    S[ad] = {};
    for (const [k, f] of ADIM) { await f(p); await p.waitForTimeout(150);
      S[ad][k] = await p.evaluate(() => { const o = __oku(), r = document.getElementById('grPoisRow');
        if (r) { const c = r.cloneNode(true), n = c.querySelector('#grPoisPt'); o.ptTxt = n ? n.textContent : null; if (n) { const br = n.previousSibling; n.remove(); if (br && br.nodeName === 'BR') br.remove(); } o.poisEski = c.textContent; }
        const q = lastGrPois;
        if (q && q.path === 'tekMc') { const bt = grBootDraws(q.n, q.b, q.mc, tmMagDM, GR_POIS.B, GR_POIS.seed);   // bağımsız: aynı örnekleyiciden çekilişler, yüzdelikler burada
          const pct = (a, z) => { const s = a.filter(Number.isFinite).sort((x, y) => x - y), h = (s.length - 1) * z, i = Math.floor(h); return s[i] + (s[Math.min(i + 1, s.length - 1)] - s[i]) * (h - i); };
          o.bag = [10, 50, 100, q.t].map(t => { const P = bt.D.map(([ns, bs]) => { const l = (ns / q.T) * Math.pow(10, -bs * (q.M - q.mc)); return 1 - Math.exp(-l * t); }); return { t, lo: pct(P, 0.025), hi: pct(P, 0.975) }; }); }
        return o; });
      if (ad === 'sonra' && k === 'tekMc_M6_t75') { const el = await p.$('#grPoisRow'); await el.scrollIntoViewIfNeeded(); await el.screenshot({ path: path.join(__dirname, 'coklu_t_tekMc.png') }); }
      if (ad === 'sonra' && k === 'weichert_gk74kapali') { const el = await p.$('#grPoisRow'); await el.scrollIntoViewIfNeeded(); await el.screenshot({ path: path.join(__dirname, 'coklu_t_weichert.png') }); } }
    S[ad].hatalar = hatalar; await ctx.close();
  }
  const O = S.once, Y = S.sonra;
  for (const [k] of ADIM) {
    const o = O[k], y = Y[k], qo = o.pois_n, qy = y.pois_n;
    ok(o.svg === y.svg && o.metin === y.metin, `(1) ${k}: G–R grafiği ve Poisson satırı dışındaki metin önce = sonra`);
    ok(o.poisEski === y.poisEski, `(1) ${k}: Poisson satırı, yeni süre satırı çıkarılınca önce = sonra`);
    if (o.poisEski !== y.poisEski) { const a = o.poisEski || '', b = y.poisEski || ''; let i = 0; while (i < a.length && a[i] === b[i]) i++; console.log('   önce: …' + a.slice(Math.max(0, i - 60), i + 90) + '\n   sonra: …' + b.slice(Math.max(0, i - 60), i + 90)); }
    if (!qy) { ok(!qo, `(1) ${k}: Poisson satırı yok (önce de yok)`); continue; }
    const ciSame = ['lamLo', 'lamHi', 'pLo', 'pHi', 'B', 'nFail', 'seed'].every(f => qo.ci[f] === qy.ci[f]) && qo.lam === qy.lam;
    ok(ciSame, `(1) ${k}: λ = ${qy.lam === 0 ? 0 : qy.lam.toExponential(4)}, λ ve P(t = ${qy.t}) aralıkları, B = ${qy.ci.B}, nFail = ${qy.ci.nFail} önce = sonra (bootstrap akışı değişmedi)`);
    const ts = qy.Pt.map(x => x.t), bek = [...new Set([10, 50, 100, qy.t])].sort((a, b) => a - b);
    ok(JSON.stringify(ts) === JSON.stringify(bek), `(2) ${k}: süreler ${ts.join(', ')} yıl (t = ${qy.t})`);
    const pOk = qy.Pt.every(x => Math.abs(x.P - (qy.lam > 0 ? -Math.expm1(-qy.lam * x.t) : 0)) < 1e-15), u = qy.Pt.find(x => x.t === qy.t);
    ok(pOk && u.lo === qy.ci.pLo && u.hi === qy.ci.pHi, `(3) ${k}: her süre için P = 1 − e^(−λt); t = ${qy.t} aralığı [%${pc(u.lo)}–%${pc(u.hi)}] mevcut satırla birebir`);
    if (y.bag) { let mx = 0; for (const b of y.bag) { const x = qy.Pt.find(z => z.t === b.t); mx = Math.max(mx, Math.abs(x.lo - b.lo), Math.abs(x.hi - b.hi)); }
      ok(mx < 1e-12, `(4) ${k}: %95 aralıkları bağımsız yeniden hesapla aynı (en büyük mutlak fark ${mx.toExponential(1)})`); }
    const goster = qy.Pt.every(x => y.ptTxt.includes(`${x.t} yıl: %${pc(x.P)}`) && (x.lo === null || y.ptTxt.includes(`[%${pc(x.lo)}–%${pc(x.hi)}]`)));
    ok(goster, `(5) ${k}: ekranda — ${y.ptTxt.replace(/\s+/g, ' ').slice(0, 170)}`);
  }
  ok(!O.hatalar.length && !Y.hatalar.length, `(6) Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length})`);
  await br.close(); srv.close();
  fs.writeFileSync(path.join(__dirname, 'kabul_coklu_t_sonuc.json'), JSON.stringify({ kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
