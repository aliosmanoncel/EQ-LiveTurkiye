// Denetim (2026-10-31): C bölümündeki "Mc = 4,0'da 1998 sıçraması kayboluyor" iddiasının dönem bazında doğrudan sınanması.
// P1 = 1990–1997, P2 = 1998–2005; tek basamak Weichert (= tek Mc), Mc = 4,0; mod: ham ve Scordilis (2006); GK74 kapalı/açık.
// b ± σ (Weichert 1980), λ(≥4,0) = N/T ve kesin %95 (Garwood; Wilson–Hilferty χ²); fark testleri: b için z = Δb/√(σ₁² + σ₂²),
// hız için koşullu binom (N₂ | N₁ + N₂ ~ Bin(N₁ + N₂, T₂/(T₁ + T₂))), iki yönlü. Ham veri yalnız okunur.
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/olcek_isc_emsc/mc40_dogrudan.js
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), LD = process.env.LEAFLET_DIR;
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]), f = path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT)) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); }); });
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), ctx = await br.newContext(), p = await ctx.newPage(), hatalar = [];
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
    await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="1971"]'), 1971, 1997);
    await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="1998"]:not([data-hist-src])'), 1998);
    regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(36, 26) }); map.fire('mousemove', { latlng: L.latLng(42, 45) }); await regionMouseUp();
    for (let i = 0; i < 600 && (regionLoading || !regionEvents || !regionEvents.length); i++) await new Promise(r => setTimeout(r, 50));
    if (!showTimeMag) toggleTimeMag();
    const w = steps => { csSteps = steps.map(([start, mc]) => ({ start, mc: String(mc) })); csEnabled = true; csRenderRows(); onCsChange(true); renderTimeMag([...events, ...liveEvents]);
      const c = lastGrFit.curves[0], T = lastCs.periods.filter(q => q.mc < 50).reduce((s, q) => s + (q.t1 - q.t0), 0) / (365.25 * 864e5);
      return { b: c.b, sig: lastGrFit.sigB, N: lastGrFit.N, T }; };
    const out = {};
    for (const gk of [false, true]) { if (gk !== !!regionDeclusterOn) { await toggleRegionDecluster(); applyGk74Filter(regionEvents); }
      for (const mod of ['none', 'scordilis2006']) { document.getElementById('tmConversionSel').value = mod; mcConversionMode = mod;
        out[`${gk ? 'gk74' : 'ham'}|${mod}`] = { P1: w([['1990-01-01', 4.0], ['1998-01-01', 99]]), P2: w([['1971-01-01', 99], ['1998-01-01', 4.0], ['2006-01-01', 99]]) }; } }
    return out; });
  const chi = (p, k) => { const z = p > 0.5 ? 1.959963985 : -1.959963985, c = 2 / (9 * k); return k * Math.pow(1 - c + z * Math.sqrt(c), 3); };
  const erfc = v => { const t = 1 / (1 + 0.5 * Math.abs(v)), e = t * Math.exp(-v * v - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277))))))))); return v >= 0 ? e : 2 - e; };
  const lgam = x => { const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]; let y = x, t = x + 5.5; t -= (x + 0.5) * Math.log(t); let s = 1.000000000190015; for (const v of c) s += v / ++y; return -t + Math.log(2.5066282746310005 * s / x); };
  const binom2 = (k, n, q) => { const pmf = j => Math.exp(lgam(n + 1) - lgam(j + 1) - lgam(n - j + 1) + j * Math.log(q) + (n - j) * Math.log(1 - q)); const p0 = pmf(k); let s = 0; for (let j = 0; j <= n; j++) { const pj = pmf(j); if (pj <= p0 * (1 + 1e-9)) s += pj; } return Math.min(1, s); };
  const satir = [];
  for (const [k, v] of Object.entries(R)) { const a = v.P1, b = v.P2, l1 = a.N / a.T, l2 = b.N / b.T;
    const ci = x => [x.N > 0 ? chi(0.025, 2 * x.N) / (2 * x.T) : 0, chi(0.975, 2 * x.N + 2) / (2 * x.T)];
    const zb = (b.b - a.b) / Math.sqrt(a.sig ** 2 + b.sig ** 2), pb = erfc(Math.abs(zb) / Math.SQRT2), pl = binom2(b.N, a.N + b.N, b.T / (a.T + b.T));
    const s = { senaryo: k, P1: { b: a.b, sig: a.sig, N: a.N, T: a.T, lam: l1, ci: ci(a) }, P2: { b: b.b, sig: b.sig, N: b.N, T: b.T, lam: l2, ci: ci(b) }, db: b.b - a.b, pb, dlog: Math.log10(l2 / l1), pl };
    satir.push(s);
    console.log(`${k.padEnd(20)} b ${a.b.toFixed(2)} ± ${a.sig.toFixed(2)} → ${b.b.toFixed(2)} ± ${b.sig.toFixed(2)} (Δb ${s.db.toFixed(2)}, p = ${pb.toFixed(3)}) | λ(≥4) ${l1.toFixed(1)} [${s.P1.ci.map(x => x.toFixed(1)).join('–')}] → ${l2.toFixed(1)} [${s.P2.ci.map(x => x.toFixed(1)).join('–')}] /yıl (Δlog ${s.dlog.toFixed(3)}, p = ${pl < 1e-4 ? pl.toExponential(1) : pl.toFixed(3)}) | N ${a.N}/${b.N}, T ${a.T.toFixed(2)}/${b.T.toFixed(2)}`); }
  fs.writeFileSync(path.join(__dirname, 'mc40_dogrudan.json'), JSON.stringify({ satir, hatalar }, null, 1));
  console.log('Sayfa hatası:', hatalar.length); await br.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
