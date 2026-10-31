// ISC–EMSC büyüklük ölçeği araştırması (2026-10-31). Ham kataloglara dokunulmaz: veriler sayfadan okunur, dönüşümler bellekte uygulanır.
// A) Ölçek farkı: data/mw_iscgem.json 'aktarim' kayıtları (EQ-Live olayı ↔ ISC-GEM v12.1 Mw; önceden eşleştirilmiş). Her olay için
//    Δ = M − Mw_ISCGEM; M: kataloğun ham büyüklüğü ve uygulamanın dönüşüm bankasındaki (MAG_CONVERSIONS) her mod. Dönem (ISC ≤ 1997 / EMSC ≥ 1998)
//    × büyüklük türü; referans yalnız doğrudan Mw (iscgem_direct) ve tümü (doğrudan + vekil). Not: ISC-GEM M ≳ 5 içerir; küçük büyüklüklerin
//    (EMSC'de baskın ML/MD) ölçeği bu yolla sınanamaz.
// B) 1998 sınırı: Türkiye kutusu 36–42° K / 26–45° D, ISC 1971–1997 + EMSC 1998– pencereleri. P1 = 1990–1997, P2 = 1998–2005 (8'er yıl).
//    Her dönüşüm modu ve GK74 kapalı/açık için: dönem Mc'leri (uygulamanın computeMcScale'i), ortak eşik Mc_ort = max(Mc1, Mc2),
//    her dönem ayrı Weichert (tek basamak = tek Mc; uygulamanın renderGutenbergRichterCS hesabı) → b ve λ(≥Mc_ort), λ(≥4,5).
//    Ayrıca tür bileşimi (dönem başına), ve a(t)/b(t) serilerinin 1998 öncesi/sonrası 3 yıllık ortalamaları.
// C) Mc etkisi: dönüşümsüz a(t)/b(t) 1998 sıçraması, birleşik pencerenin otomatik Mc'si ile ve elle Mc = 4,0 ile (GK74 kapalı/açık).
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/olcek_isc_emsc/olcek.js
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), LD = process.env.LEAFLET_DIR;
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]), f = path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT)) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); }); });
const MODLAR = ['none', 'scordilis2006', 'civgin2019', 'combined_dispatch', 'iscgem2015', 'lolli2014'];
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
  const R = await p.evaluate(async MODLAR => {
    const bekle = async () => { for (let i = 0; i < 600 && (regionLoading || !regionEvents || !regionEvents.length); i++) await new Promise(r => setTimeout(r, 50)); };
    await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="1971"]'), 1971, 1997);
    await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="1998"]:not([data-hist-src])'), 1998);
    const tur = e => { const t = (e.mtype || '?').toLowerCase(); return t === 'mb' ? 'mb' : t === 'ms' ? 'Ms' : t === 'ml' ? 'ML' : t === 'md' ? 'MD' : /^mw/.test(t) ? 'Mw' : 'diğer'; };
    const ozet = v => { if (!v.length) return null; const s = v.slice().sort((a, b) => a - b), n = v.length, m = v.reduce((a, x) => a + x, 0) / n;
      return { n, ort: m, med: s[Math.floor(n / 2)], ss: n > 1 ? Math.sqrt(v.reduce((a, x) => a + (x - m) ** 2, 0) / (n - 1)) : null }; };
    const out = { A: {}, B: {}, bilesim: {} };
    // ── A) ISC-GEM ile ölçek farkı ──
    const mwj = await (await fetch('data/mw_iscgem.json')).json(), byId = new Map(historicalCache.events.map(e => [e.id, e]));
    const es = mwj.aktarim.map(r => ({ r, e: byId.get(r.A_id) })).filter(x => x.e && Number.isFinite(x.r.Mw));
    out.A.eslesen = es.length; out.A.toplam = mwj.aktarim.length;
    for (const ref of ['dogrudan', 'tumu']) { out.A[ref] = {};
      for (const mod of MODLAR) { const conv = MAG_CONVERSIONS[mod], g = {};
        es.filter(x => ref === 'tumu' || x.r.mw_src === 'iscgem_direct').forEach(({ r, e }) => {
          const ev = { ...e, time: new Date(e.time) }, M = mod === 'none' ? panelBaseMag(ev) : (conv.applicable(ev) ? conv.convert(ev) : panelBaseMag(ev));
          const k = `${e.src}|${tur(e)}`; (g[k] = g[k] || []).push(M - r.Mw); const kk = `${e.src}|tümü`; (g[kk] = g[kk] || []).push(M - r.Mw); });
        out.A[ref][mod] = Object.fromEntries(Object.entries(g).map(([k, v]) => [k, ozet(v)])); } }
    // ── B) 1998 sınırı ──
    regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(36, 26) }); map.fire('mousemove', { latlng: L.latLng(42, 45) }); await regionMouseUp(); await bekle();
    if (!showTimeMag) toggleTimeMag();
    const Y = 365.25 * 864e5, P1 = [Date.UTC(1990, 0, 1), Date.UTC(1998, 0, 1)], P2 = [Date.UTC(1998, 0, 1), Date.UTC(2006, 0, 1)];
    const icinde = (e, P) => +e.time >= P[0] && +e.time < P[1];
    // Tür bileşimi (ham, GK74 kapalı)
    for (const [ad, P] of [['P1_1990_1997', P1], ['P2_1998_2005', P2]]) { const c = {}; regionEvents.filter(e => icinde(e, P)).forEach(e => { const t = tur(e); c[t] = (c[t] || 0) + 1; }); out.bilesim[ad] = c; }
    const weichert = steps => { csSteps = steps.map(([start, mc]) => ({ start, mc: String(mc) })); csEnabled = true; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = true; csRenderRows(); onCsChange(true); renderTimeMag([...events, ...liveEvents]);
      const c = lastGrFit && lastGrFit.curves[0]; if (!c) return null; const lam = M => lastGrFit.fnBest ? lastGrFit.fnBest(M) : null;
      return { b: c.b, m0: lastGrFit.m0, lamM0: c.rate0, lam45: lam(4.5), N: lastGrFit.N, donem: lastCs.periods.filter(q => q.mc < 50).map(q => [new Date(q.t0).toISOString().slice(0, 10), new Date(q.t1).toISOString().slice(0, 10), q.mc]) }; };
    for (const gk of [false, true]) {
      if (gk !== !!regionDeclusterOn) { await toggleRegionDecluster(); applyGk74Filter(regionEvents); }
      for (const mod of MODLAR) {
        document.getElementById('tmConversionSel').value = mod; mcConversionMode = mod;
        const evs = regionEvents, conv = applyMagConversionForDisplay(evs, mod).list;
        const sc1 = computeMcScale(conv.filter(e => icinde(e, P1))), sc2 = computeMcScale(conv.filter(e => icinde(e, P2)));
        const mc1 = sc1 ? sc1.mc : null, mc2 = sc2 ? sc2.mc : null, mcO = Math.ceil((Math.max(mc1, mc2) - 1e-9) * 10) / 10;
        const w1 = weichert([['1990-01-01', mcO], ['1998-01-01', 99]]), w2 = weichert([['1971-01-01', 99], ['1998-01-01', mcO], ['2006-01-01', 99]]);
        // a(t)/b(t): basamaksız, tüm pencere; 1998 öncesi/sonrası 3 yıl (pencere tümüyle o yanda)
        csEnabled = false; onCsChange(true); renderTimeMag([...events, ...liveEvents]);
        const yan = (t0, t1) => { const ser = lastAts ? lastAts.pts.filter(q => q.t >= t0 && q.t < t1) : []; return ser.length ? { n: ser.length, a: ser.reduce((s, q) => s + q.a, 0) / ser.length, b: ser.reduce((s, q) => s + q.b, 0) / ser.length } : null; };
        out.B[`${gk ? 'gk74' : 'ham'}|${mod}`] = { mc1, mc2, mcO, w1, w2, onceki3: yan(Date.UTC(1995, 0, 1), Date.UTC(1998, 0, 1)), sonraki3: yan(Date.UTC(1998, 0, 1), Date.UTC(2001, 0, 1)), aMc: lastAts ? lastAts.pts[0] && lastGrMc : null };
      }
    }
    // ── C) Mc etkisi: a(t)/b(t) 1998 sıçraması, otomatik Mc (birleşik pencere) ve elle Mc = 4,0 (iki dönemde de tam; seçim kutusunda 0,5 adımlı değerler var), dönüşüm yok ──
    document.getElementById('tmConversionSel').value = 'none'; mcConversionMode = 'none'; csEnabled = false; onCsChange(true); out.C = {};
    for (const gk of [false, true]) { if (gk !== !!regionDeclusterOn) { await toggleRegionDecluster(); applyGk74Filter(regionEvents); }
      for (const mc of ['', '4.0']) { document.getElementById('regionMcOverride').value = mc; renderTimeMag([...events, ...liveEvents]);
        const yan = (t0, t1) => { const ser = lastAts ? lastAts.pts.filter(q => q.t >= t0 && q.t < t1) : []; return ser.length ? { n: ser.length, a: ser.reduce((s, q) => s + q.a, 0) / ser.length, b: ser.reduce((s, q) => s + q.b, 0) / ser.length } : null; };
        out.C[`${gk ? 'gk74' : 'ham'}|Mc ${mc || 'oto'}`] = { mc: lastGrMc, once: yan(Date.UTC(1995, 0, 1), Date.UTC(1998, 0, 1)), sonra: yan(Date.UTC(1998, 0, 1), Date.UTC(2001, 0, 1)), sonra2: yan(Date.UTC(2001, 0, 1), Date.UTC(2004, 0, 1)) }; } }
    document.getElementById('regionMcOverride').value = '';
    return out; }, MODLAR);
  R.hatalar = hatalar;
  fs.writeFileSync(path.join(__dirname, 'olcek_sonuc.json'), JSON.stringify(R, null, 1));
  const f = (v, d = 2) => v === null || v === undefined || !Number.isFinite(v) ? '—' : v.toFixed(d);
  console.log(`A) Eşleşen olay: ${R.A.eslesen} / ${R.A.toplam}`);
  for (const ref of ['dogrudan', 'tumu']) { console.log(`\nA — referans: ${ref === 'dogrudan' ? 'yalnız doğrudan Mw' : 'doğrudan + vekil Mw'}  (medyan Δ = M − Mw [n])`);
    const keys = [...new Set(MODLAR.flatMap(m => Object.keys(R.A[ref][m])))].sort();
    console.log('  ' + 'kaynak|tür'.padEnd(14) + MODLAR.map(m => m.slice(0, 14).padStart(16)).join(''));
    keys.forEach(k => console.log('  ' + k.padEnd(14) + MODLAR.map(m => { const o = R.A[ref][m][k]; return (o ? `${f(o.med)} [${o.n}]` : '—').padStart(16); }).join(''))); }
  console.log('\nTür bileşimi:', JSON.stringify(R.bilesim));
  console.log('\nB) 1998 sınırı (P1 1990–1997 / P2 1998–2005): Mc1, Mc2 → Mc_ort; b1 → b2; log10 λ(≥Mc_ort) P1 → P2 (Δ); log10 λ(≥4,5) Δ; a(t) ve b(t) 1995–97 → 1998–2000');
  for (const [k, v] of Object.entries(R.B)) { const l = x => x ? Math.log10(x) : NaN;
    console.log(`  ${k.padEnd(26)} Mc ${f(v.mc1, 2)}/${f(v.mc2, 2)} → ${f(v.mcO, 1)} | b ${f(v.w1 && v.w1.b)} → ${f(v.w2 && v.w2.b)} (Δ ${f(v.w2 && v.w1 ? v.w2.b - v.w1.b : NaN)}) | log λ(≥Mc) ${f(l(v.w1 && v.w1.lamM0))} → ${f(l(v.w2 && v.w2.lamM0))} (Δ ${f(l(v.w2 && v.w2.lamM0) - l(v.w1 && v.w1.lamM0))}) | Δlog λ(≥4,5) ${f(l(v.w2 && v.w2.lam45) - l(v.w1 && v.w1.lam45))} | a(t) ${f(v.onceki3 && v.onceki3.a)} → ${f(v.sonraki3 && v.sonraki3.a)}, b(t) ${f(v.onceki3 && v.onceki3.b)} → ${f(v.sonraki3 && v.sonraki3.b)}`); }
  console.log('\nC) Mc etkisi (dönüşüm yok): a(t) ve b(t) ortalamaları 1995–97 → 1998–2000 → 2001–03');
  for (const [k, v] of Object.entries(R.C)) console.log(`  ${k.padEnd(14)} Mc = ${v.mc} | a ${f(v.once && v.once.a)} → ${f(v.sonra && v.sonra.a)} → ${f(v.sonra2 && v.sonra2.a)} | b ${f(v.once && v.once.b)} → ${f(v.sonra && v.sonra.b)} → ${f(v.sonra2 && v.sonra2.b)} | pencere ${v.once ? v.once.n : 0}/${v.sonra ? v.sonra.n : 0}/${v.sonra2 ? v.sonra2.n : 0}`);
  console.log('\nSayfa hatası:', hatalar.length);
  await br.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
