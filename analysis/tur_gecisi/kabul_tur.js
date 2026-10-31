// Kabul testi (2026-11-01): büyüklük türü geçişi uyarısı. Önce = verilen index.html (main), sonra = depodaki index.html. Veri yerel.
// Senaryolar (Türkiye kutusu 36–42° K / 26–45° D; Marmara 40–41,5° K / 26–31° D):
//   emsc98 (+ GK74, + Mc 3,5, + Mc 4,0), marmara (+ GK74), birlesik ISC 1971–1997 + EMSC 1998– (+ basamaklar 1971 M ≥ 4,5 / 1998 M ≥ 3,5),
//   isc71_97 (yalnız ISC), kmaras (2023 dizisi; yalnız ML dönemi) — uyarı beklenmez.
// Denetimler: (1) b(t) ve a(t) grafikleri, uyarı blokları (Mc ve tür) dışındaki b(t)/a(t) metinleri ve G–R metni önce = sonra (hesap değişmedi);
//   (2) Mc uyarısı önce = sonra; (3) tür uyarısı b(t)'de varsa a(t)'de kısa notu da var (ve tersi), önce yok; (4) emsc98'de MD → ML geçişi
//   (2010/2011 → 2012) algılanıyor; kmaras'ta uyarı yok; (5) sayfa hatası yok.
// Ekran görüntüsü: tur_uyari_emsc98.png
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/tur_gecisi/kabul_tur.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_tur.js <önceki_index.html>'); process.exit(2); }
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
window.__oku = () => { const tx = id => { const el = document.getElementById(id); if (!el) return null; const c = el.cloneNode(true); c.querySelectorAll('#mcUyariB, #mcUyariA, #turUyariB, #turUyariA').forEach(n => n.remove()); return c.textContent; };
  const sa = document.getElementById('tmSvgA'), t = id => document.getElementById(id) ? document.getElementById(id).textContent : null;
  return { bSvg: document.getElementById('tmSvgB').innerHTML, bTxt: tx('tmStatsB'), aSvg: sa ? sa.innerHTML : null, aTxt: tx('tmStatsA'), grTxt: document.getElementById('tmStatsGR').textContent,
    mcB: t('mcUyariB'), mcA: t('mcUyariA'), turB: t('turUyariB'), turA: t('turUyariA'),
    durum: typeof lastTurUyari !== 'undefined' && lastTurUyari ? JSON.parse(JSON.stringify(lastTurUyari)) : null, Mc: lastGrMc, csAktif: !!lastCs }; };
`;
const TR = [36, 26, 42, 45], MAR = [40, 26, 41.5, 31];
const SEN = {
  emsc98:        { p: [[1998, null]], r: TR },
  emsc98_gk74:   { p: [[1998, null]], r: TR, gk: true },
  emsc98_mc35:   { p: [[1998, null]], r: TR, mc: '3.5' },
  emsc98_mc40:   { p: [[1998, null]], r: TR, mc: '4.0' },
  marmara:       { p: [[1998, null]], r: MAR },
  marmara_gk74:  { p: [[1998, null]], r: MAR, gk: true },
  birlesik:      { p: [[1971, 1997], [1998, null]], r: TR },
  birlesik_cs:   { p: [[1971, 1997], [1998, null]], r: TR, cs: [['1971-01-01', '4.5'], ['1998-01-01', '3.5']] },
  isc71_97:      { p: [[1971, 1997]], r: TR },
  kmaras:        { p: [[1998, null]], r: [36.5, 35.5, 38.5, 39] },
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
      if (ad === 'sonra' && k === 'emsc98') { const el = await p.$('#tmStatsB'); await el.scrollIntoViewIfNeeded(); await el.screenshot({ path: path.join(__dirname, 'tur_uyari_emsc98.png') }); }
      hat.push(...hatalar); await ctx.close();
    }
    S[ad].hatalar = hat;
  }
  const O = S.once, Y = S.sonra;
  for (const k of Object.keys(SEN)) { const o = O[k], y = Y[k];
    ok(o.bSvg === y.bSvg && o.bTxt === y.bTxt && o.aSvg === y.aSvg && o.aTxt === y.aTxt && o.grTxt === y.grTxt, `(1) ${k}: b(t) ve a(t) grafikleri, uyarılar dışındaki metinler ve G–R metni önce = sonra`);
    ok(o.mcB === y.mcB && o.mcA === y.mcA, `(2) ${k}: Mc uyarısı önce = sonra (${y.mcB ? 'var' : 'yok'})`);
    ok(!!y.turB === !!y.turA && !!y.turB === !!(y.durum && y.durum.on) && !o.turB && !o.turA, `(3) ${k}: tür uyarısı ${y.turB ? 'VAR' : 'yok'} (b(t) ve a(t) tutarlı; önce yok)`);
    const d = y.durum; console.log(`     ${k}: Mc ${y.Mc}${y.csAktif ? ' (basamaklı)' : ''}${SEN[k].gk ? ', GK74' : ''}; ` + (d && d.on ? `geçişler ${d.gecisler.map(g => `${g.a}→${g.b} ${g.ySon}–${g.yIlk}${g.karisik.length ? ' (karışık ' + g.karisik.join(',') + ')' : ''}`).join('; ')}; dönemler ${d.donemler.map(x => `${x.tur} ${x.y0}–${x.y1}`).join(', ')}; öneri ${d.oner ? `M ${d.oner.M} (${d.oner.tur}, ${d.oner.nYil} yıl)` : '—'}` : `uyarı yok; yıllar ${d ? d.yillar.map(q => q.y + ':' + (q.tur || 'karışık')).join(' ') : '—'}`)); }
  { const d = Y.emsc98.durum, g = d && d.on && d.gecisler.find(x => x.a === 'MD' && x.b === 'ML');
    ok(!!g && (g.ySon === 2010 || g.ySon === 2011) && g.yIlk >= 2011 && g.yIlk <= 2012, `(4) Türkiye EMSC 1998–: MD → ML geçişi algılanıyor (${g ? g.ySon + ' → ' + g.yIlk : '—'})`); }
  ok(!(Y.kmaras.durum && Y.kmaras.durum.on) || Y.kmaras.durum.gecisler.every(x => x.ySon < 2013), '(4) Kahramanmaraş: ML dönemi içinde tür geçişi yok (yalnız 2012 öncesi geçiş olabilir)');
  ok(!O.hatalar.length && !Y.hatalar.length, `(5) Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length})` + (Y.hatalar.length ? ': ' + Y.hatalar.join(' | ') : ''));
  const ozet = {}; for (const k of Object.keys(SEN)) ozet[k] = { Mc: Y[k].Mc, durum: Y[k].durum, uyari: Y[k].turB, mcUyari: Y[k].mcB };
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify({ senaryolar: SEN, sonuc: ozet, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
