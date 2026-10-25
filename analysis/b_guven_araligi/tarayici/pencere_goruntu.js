const { chromium } = require('playwright'); const LB = process.env.LB, SP = process.env.SP;
(async () => { const b = await chromium.launch();   const mkp = async () => { const p = await (await b.newContext({ viewport: { width: 1500, height: 1100 }, timezoneId: 'UTC' })).newPage();
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.js/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.js', contentType: 'application/javascript' }));
  await p.route(/leaflet@1\.9\.4\/dist\/leaflet\.css/, r => r.fulfill({ path: LB + '/leaflet-1.9.4/dist/leaflet.css', contentType: 'text/css' }));
  await p.route(/leaflet-heat\.js/, r => r.fulfill({ path: LB + '/leaflet.heat-0.2.0/dist/leaflet-heat.js', contentType: 'application/javascript' }));
  await p.route(u => !/^http:\/\/localhost/.test(u.href) && !/leaflet/.test(u.href), r => r.abort());
  return p; };
  for (const n of [100, 30]) { const p = await mkp();
    await p.goto(`http://localhost:8772/index.html?btn=${n}`, { waitUntil: 'domcontentloaded' });
    await p.waitForFunction(() => typeof events !== 'undefined' && events.length > 100, null, { timeout: 90000 }); await p.waitForTimeout(2000);
    await p.evaluate(() => { const bt = document.querySelector('[data-hist="1900"][data-hist-end="1970"]'); toggleHistoricalWindow(bt, 1900, 1970); }); await p.waitForTimeout(5000);
    await p.evaluate(() => { if (!showTimeMag) openTimeMagMode('normal'); }); await p.waitForTimeout(4000);
    const e = await p.$('#tmSvgB'); await e.screenshot({ path: `${SP}/bt_hist_N${n}.png` });
    const t = await p.$('.tmTitle'); console.log(n, await p.evaluate(() => document.getElementById('btWinSel').value + ' | ' + document.getElementById('tmWinLbl').textContent + ' | adım ' + document.getElementById('tmStepLbl').textContent + ' | URL ' + location.search));
  }
  await b.close(); })();
