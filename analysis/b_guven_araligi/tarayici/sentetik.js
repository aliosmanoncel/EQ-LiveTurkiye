// Sentetik katalog (YAPAY VERİ): b = 1 arka plan + iki ana şok ve Omori artçıları; son bölümde b ≈ 2,6 (T–M yolunu tetiklemek için)
const { chromium } = require('playwright'); const fs = require('fs');
const [port, q, tag] = process.argv.slice(2), LB = process.env.LB, SP = process.env.SP;
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1500, height: 1100 }, timezoneId: 'UTC' })).newPage(); const errs = [];
  p.on('dialog', d => { errs.push('dialog: ' + d.message()); d.dismiss(); }); p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 200)); });
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.js/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.js', contentType: 'application/javascript' }));
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.css/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.css', contentType: 'text/css' }));
  await p.route(/leaflet-heat\.js/, r => r.fulfill({ path: LB + '/leaflet.heat-0.2.0/dist/leaflet-heat.js', contentType: 'application/javascript' }));
  await p.route(u => !/^http:\/\/localhost/.test(u.href) && !/leaflet/.test(u.href), r => r.abort());
  await p.goto(`http://localhost:${port}/index.html${q}`, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await p.waitForFunction(() => typeof events !== 'undefined' && events.length > 100, null, { timeout: 90000 }); await p.waitForTimeout(2000);
  const R = await p.evaluate(() => {
    let s = 12345; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647, L10 = Math.LN10;
    const gr = (b, m0) => Math.floor((m0 - 0.05 + -Math.log(1 - rnd()) / (b * L10)) * 10 + 1e-9) / 10 + 0.0;   // 0,1 ızgarası
    const tmpl = events[0], list = []; let id = 0;
    const mk = (t, m, la, lo) => ({ ...tmpl, id: 'syn' + (id++), time: new Date(t), mag: +m.toFixed(1), mw: undefined, lat: la, lon: lo, depth: 10 });
    const T0 = Date.parse('2010-01-01'), T1 = Date.parse('2024-01-01');
    for (let i = 0; i < 1800; i++) list.push(mk(T0 + rnd() * (T1 - T0), gr(1.0, 3.0), 38 + rnd() * 2, 30 + rnd() * 4));
    [[Date.parse('2014-05-01'), 6.6, 38.5, 31.0], [Date.parse('2019-09-10'), 6.4, 39.4, 33.0]].forEach(([t, M, la, lo]) => { list.push(mk(t, M, la, lo));
      for (let i = 0; i < 260; i++) { const dt = 0.05 * (Math.pow(1 - rnd(), -1 / 0.1) - 1) * 86400e3; if (dt > 400 * 86400e3) continue; list.push(mk(t + 60e3 + dt, Math.min(M - 0.5, gr(1.0, 3.0)), la + (rnd() - .5) * .2, lo + (rnd() - .5) * .2)); } });
    const T2 = Date.parse('2024-01-01'), T3 = Date.parse('2026-06-01');
    for (let i = 0; i < 2500; i++) list.push(mk(T2 + rnd() * (T3 - T2), gr(2.6, 3.0), 38 + rnd() * 2, 30 + rnd() * 4));
    list.sort((a, c) => a.time - c.time); window.__syn = list; document.getElementById('sensMcs').value = '3.0, 3.2, 3.5';
    document.getElementById('sensBounds').value = '2010-01-01, 2014-01-01, 2019-01-01, 2024-01-01, 2026-06-01';
    return list.length; });
  await p.evaluate(() => { if (!showTimeMag) openTimeMagMode('normal'); }); await p.waitForTimeout(3000);
  await p.evaluate(() => { tmMcOverride = null; renderTimeMag(window.__syn); }); await p.waitForTimeout(3000);
  const out = await p.evaluate(() => { const g = id => document.getElementById(id)?.innerHTML || ''; const tx = s => s.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
    const ser = (lastBts && lastBts.ser) || []; const cnt = {}; ser.forEach(q => cnt[q.ciM] = (cnt[q.ciM] || 0) + 1);
    const tmW = ser.filter(q => q.ciM === 'tm').slice(-3).map(q => [q.b.toFixed(3), q.lo.toFixed(3), Number.isFinite(q.hi) ? q.hi.toFixed(3) : 'inf']);
    return { n: window.__syn.length, statsB: tx(g('tmStatsB')).slice(0, 260), gr: tx(g('tmStatsGR')).slice(0, 220), sens: tx(g('sensTable')).slice(0, 700), pb: tx(g('tmStatsPB')).slice(0, 500),
      pbRows: (window.lastPBSeq && window.lastPBSeq.seq || []).map(s => [s.N, s.b && s.b.toFixed(3), s.bLo && s.bLo.toFixed(3), s.bHi && s.bHi.toFixed(3), s.bCiM]), ciCount: cnt, tmWindows: tmW, cls: lastBts && lastBts.cls,
      svgBad: ['tmSvgB', 'tmSvgBz', 'tmSvgGR', 'tmSvgPB'].filter(id => /NaN|Infinity/.test(g(id))) }; });
  await p.evaluate(() => { try { if (window.__pbOk && window.__pbOk.length) openPBSeqPanel(0); } catch (e) { console.error('pb ' + e.message); } }); await p.waitForTimeout(2000);
  out.pbPanelBad = await p.evaluate(() => /NaN|Infinity/.test(document.getElementById('pbSeqPanel')?.innerHTML || '')); out.pbPanelLen = await p.evaluate(() => (document.getElementById('pbSeqPanel')?.innerHTML || '').length);
  out.cmp = await p.evaluate(() => { try { const L = window.__syn, mkR = (nm, a, z) => { const ev = L.filter(e => e.time >= Date.parse(a) && e.time < Date.parse(z));
      return { name: nm, src: 'sentetik', shape: 'kutu', area: 50000, cLat: 39, t0: Date.parse(a), t1: Date.parse(z), Mc: 3.2, dm: 0.1, mags: ev.map(e => Math.round(e.mag * 100) / 100), types: {}, url: '', added: '', pts: ev.map(e => [e.lat, e.lon, e.mag]) }; };
      CMP.length = 0; CMP.push(mkR('A 2010–2014', '2010-01-01', '2014-01-01'), mkR('B 2024–2026', '2024-01-01', '2026-06-01')); cmpRender();
      return (document.getElementById('cmpTable')?.innerText || '').replace(/\s+/g, ' ').slice(0, 700); } catch (e) { return 'HATA ' + e.message; } });
  const shot = async (id, f) => { const e = await p.$('#' + id); if (e && await e.isVisible()) { await e.screenshot({ path: `${SP}/${tag}_${f}.png` }); return f; } return null; };
  out.shots = [await shot('pbSeqSvg', 'pbseq')];
  await p.evaluate(() => { const pn = document.getElementById('pbSeqPanel'); if (pn) pn.style.display = 'none'; });
  out.shots.push(await shot('tmSvgB', 'bt'), await shot('tmSvgBz', 'btz'), await shot('tmSvgGR', 'gr'), await shot('sensTable', 'sens'), await shot('tmSvgPB', 'pb'));
  out.errs = errs.filter(e => !/seismicportal|Failed to load|ERR_|net::/.test(e)); console.log(JSON.stringify(out, null, 1)); await b.close(); })();
