// Kullanım: node par.js <port> <query> <çıktı.json>
const { chromium } = require('playwright'); const fs = require('fs');
const [port, q, out] = process.argv.slice(2), LB = process.env.LB;
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ acceptDownloads: true, timezoneId: 'UTC', locale: 'tr-TR' }); const p = await ctx.newPage(); const errs = [];
  await p.addInitScript(() => { const T = Date.parse('2026-10-25T00:00:00Z'), D = Date; let k = 0;   // sabit saat: iki sürüm aynı "şimdi"yi görsün
    globalThis.Date = class extends D { constructor(...a) { if (a.length) super(...a); else super(T); } static now() { return T; } };
    const ft = CanvasRenderingContext2D.prototype.fillText; window.__txt = []; CanvasRenderingContext2D.prototype.fillText = function (t, ...a) { window.__txt.push(String(t)); return ft.call(this, t, ...a); };
    Math.random = () => { k = (k * 9301 + 49297) % 233280; return k / 233280; }; });
  p.on('dialog', d => { errs.push('dialog: ' + d.message()); d.dismiss(); }); p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text().slice(0, 200)); });
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.js/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.js', contentType: 'application/javascript' }));
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.css/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.css', contentType: 'text/css' }));
  await p.route(/leaflet-heat\.js/, r => r.fulfill({ path: LB + '/leaflet.heat-0.2.0/dist/leaflet-heat.js', contentType: 'application/javascript' }));
  await p.route(u => !/^http:\/\/localhost/.test(u.href) && !/leaflet/.test(u.href), r => r.abort());
  await p.goto(`http://localhost:${port}/index.html${q}`, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await p.waitForFunction(() => typeof events !== 'undefined' && events.length > 100, null, { timeout: 90000 }); await p.waitForTimeout(2500);
  const grab = async tag => p.evaluate(tag => { const o = {}; document.querySelectorAll('[id^="tm"],#sensTable,#pbSeqPanel,#aftMeta').forEach(e => { if (e.innerHTML) o[tag + ':' + e.id] = e.innerHTML; });
    const J = v => { try { return JSON.stringify(v); } catch (e) { return String(e); } };
    o[tag + ':lastBts'] = J(typeof lastBts !== 'undefined' ? lastBts : null); o[tag + ':lastGrSimple'] = J(typeof lastGrSimple !== 'undefined' ? lastGrSimple : null);
    o[tag + ':lastPBSeq'] = J(window.lastPBSeq || null); return o; }, tag);
  const R = { meta: {} };
  await p.evaluate(() => openTimeMagMode('normal')); await p.waitForTimeout(4000);
  Object.assign(R, await grab('canli'));
  R['canli:region'] = await p.evaluate(() => { try { const Mc = computeMc(events); return computeRegionStatsLine(events, 'time', false, 1e5); } catch (e) { return 'HATA ' + e.message; } });
  await p.evaluate(() => { try { if (window.__pbOk && window.__pbOk.length) openPBSeqPanel(0); } catch (e) { console.error('pbpanel ' + e.message); } }); await p.waitForTimeout(1500);
  R['canli:pbSeqPanel'] = await p.evaluate(() => document.getElementById('pbSeqPanel')?.innerHTML || '');
  // Tarihsel pencere: uzun b(t) (bant gösterimi, sınıflama şeridi)
  await p.evaluate(() => { const bt = document.querySelector('[data-hist="1900"][data-hist-end="1970"]') || document.querySelector('[data-hist]'); toggleHistoricalWindow(bt, +bt.dataset.hist, +(bt.dataset.histEnd || 2026)); });
  await p.waitForTimeout(6000); await p.evaluate(() => { if (!showTimeMag) openTimeMagMode('normal'); }); await p.waitForTimeout(5000);
  Object.assign(R, await grab('tarihsel'));
  // Poster (metin + PNG)
  await p.evaluate(() => { window.__txt = []; });
  try { const dl = p.waitForEvent('download', { timeout: 90000 }); await p.evaluate(async () => { document.getElementById('posterLang').value = 'tr'; await exportPosterAGU(1, null); });
    const d = await dl; const f = out.replace(/\.json$/, '_poster.png'); await d.saveAs(f); R.meta.poster = f; } catch (e) { R.meta.poster = 'HATA ' + e.message; }
  R['poster:txt'] = await p.evaluate(() => window.__txt.join('\n'));
  R.meta.errs = errs.filter(e => !/Failed to load resource|ERR_|net::|tile/i.test(e)).slice(0, 20); R.meta.bci = await p.evaluate(() => typeof B_CI_METHOD !== 'undefined' ? B_CI_METHOD : '(yok)');
  fs.writeFileSync(out, JSON.stringify(R, null, 1)); console.log(out, Object.keys(R).length - 1, 'öğe; bci =', R.meta.bci, '; hata', R.meta.errs.length, R.meta.errs.slice(0, 3)); await b.close();
})();
