// Kabul testi (2026-11-01): bölge karşılaştırmasında Poisson aşılma olasılığı (tablo satırları + yayın şekli).
// Önce = verilen index.html (main), sonra = depodaki index.html. Veri yerel (tarihsel katalog). Üç bölge karşılaştırmaya eklenir:
//   Türkiye EMSC 1998– (GK74 kapalı), Marmara EMSC 1998– (GK74 açık), Doğu Anadolu 36,5–39° K / 36–41° D EMSC 1998– (GK74 kapalı).
// Denetimler: (1) önce = sonra — main'deki tablo satırlarının hepsi aynı değerlerle duruyor; cmpSvg aynı; G–R paneli (Poisson satırı dışında),
//   b(t) ve a(t) grafikleri ve metinleri aynı. (2) Yeni satırlar: P(≥M; t) hücreleri cmpStats değerlerinden bağımsız hesapla aynı ve
//   P(≥6; t) = 1 − e^(−t/tr6). (3) Uyarılar: GK74 durumu kayıtla tutarlı. (4) Yayın şekli: SVG var, 493 pt, 3 panel, 4 süre; bant düğmesi
//   şekli değiştiriyor; altyazı. (7) Aşama 2: '±1σ' yok; Tr/T satırı bağımsız hesapla aynı ve sınıflar (†, ‡) doğru; Marmara M≥7 ‡;
//   şekilde Tr = T çizgisi ve Tr > 10T zemini. (8) Aşama 3: NegBin örnekleyici, üç bölgede B = 2000; sağlamlık B = 5000 ile %95 sınır farkları
//   (yüzde puan) raporlanır; G–R panelinin bootstrap'ı ile karşılaştırma tablosu aynı çekilişleri kullanır. (9) Aşama 4: SVG <metadata> zorunlu
//   alanları içeriyor; 'Yeniden üretim (JSON)' indiriliyor ve yeniden_uret.js bu dosyadan bütün sayıları birebir yeniden üretiyor.
//   (10) b kestiricisi seçimi: varsayılan Aki–Utsu ile olasılık satırları önceki sürümle (ONCEKI_SONUC) birebir; yan yana satır; Bender seçilince
//   hücreler bağımsız hesapla (b_B, aynı n, T, Mc) aynı, şekil/altyazı/JSON/SVG kestiriciyi kaydediyor, yeniden_uret.js Bender kaydını da üretiyor;
//   Aki–Utsu'ya dönünce tablo ilk hâliyle aynı. (5) PNG 600 dpi indirme: boyut 4108 × (H/72·600) px. (6) Sayfa hatası yok.
// Ekran görüntüleri: cmp_tablo.png, cmp_sekil_95.png, cmp_sekil_68.png; indirilen dosyalar: cmp_sekil_EN.svg, cmp_sekil_EN_600dpi.png
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/poisson_olasilik/kabul_cmp_prob.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_cmp_prob.js <önceki_index.html>'); process.exit(2); }
const srv = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split('?')[0]), f = u === '/__once.html' ? ONCE : path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT) && f !== ONCE) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); });
});
let pass = 0, fail = 0; const kayit = [];
const ok = (c, m) => { (c ? pass++ : fail++); kayit.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };
async function sayfa(br, yol) {
  const ctx = await br.newContext({ viewport: { width: 1500, height: 1200 }, acceptDownloads: true }), p = await ctx.newPage(), hatalar = [];
  p.on('pageerror', e => hatalar.push(String(e)));
  await ctx.route('**/*', rt => { const u = rt.request().url();
    if (u.startsWith('http://127.0.0.1') || u.startsWith('blob:') || u.startsWith('data:')) return rt.continue();
    if (/leaflet@1\.9\.4\/dist\/leaflet\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.js'), contentType: 'text/javascript' });
    if (/leaflet@1\.9\.4\/dist\/leaflet\.css/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.css'), contentType: 'text/css' });
    if (/leaflet-heat\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet.heat/dist/leaflet-heat.js'), contentType: 'text/javascript' });
    return rt.abort(); });
  await p.routeWebSocket(/.*/, ws => ws.close()).catch(() => {});
  await p.goto(`http://127.0.0.1:${srv.address().port}${yol}`, { waitUntil: 'load' });
  await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function' && typeof map !== 'undefined'); await p.waitForTimeout(400);
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} if (typeof CMP !== 'undefined') { CMP.length = 0; } });
  return { p, ctx, hatalar };
}
const KUR = `
window.__bolge = async (S, W, N, E, gk, ad, ilk) => {
  if (ilk) await toggleHistoricalWindow(document.querySelector('.tbtn[data-hist="1998"]:not([data-hist-src])'), 1998, null);
  regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(S, W) }); map.fire('mousemove', { latlng: L.latLng(N, E) }); await regionMouseUp();
  for (let i = 0; i < 600 && (regionLoading || !regionEvents || !regionEvents.length); i++) await new Promise(r => setTimeout(r, 50));
  if (gk !== !!regionDeclusterOn) { await toggleRegionDecluster(); applyGk74Filter(regionEvents); }
  if (!showTimeMag) toggleTimeMag(); else renderTimeMag([...events, ...liveEvents]);
  await new Promise(r => setTimeout(r, 300));
  document.getElementById('cmpName').value = ad; cmpAdd(); await new Promise(r => setTimeout(r, 200)); };
window.__tablo = () => { const t = document.querySelector('#cmpTable table'); if (!t) return null; const o = {};
  [...t.querySelectorAll('tr')].slice(1).forEach(tr => { const td = [...tr.children]; const k = td[0].textContent.trim(); if (k) o[k] = td.slice(1).map(x => x.textContent.trim()); }); return o; };
window.__oku = () => { const tx = id => { const el = document.getElementById(id); if (!el) return null; const c = el.cloneNode(true); c.querySelectorAll('#grPoisRow, #mcUyariB, #mcUyariA, #turUyariB, #turUyariA, #turYetersizB, #turYetersizA').forEach(n => n.remove()); return c.textContent; };
  const sa = document.getElementById('tmSvgA');
  return { cmpSvg: document.getElementById('cmpSvg').innerHTML, tablo: __tablo(), bSvg: document.getElementById('tmSvgB').innerHTML, bTxt: tx('tmStatsB'), aSvg: sa ? sa.innerHTML : null, aTxt: tx('tmStatsA'),
    grSvg: document.getElementById('tmSvgGR').innerHTML, grTxt: tx('tmStatsGR'), fig: document.getElementById('cmpProbFigSvg') ? document.getElementById('cmpProbFigSvg').innerHTML : null }; };
`;
const BOLGE = [[36, 26, 42, 45, false, 'Türkiye'], [40, 26, 41.5, 31, true, 'Marmara'], [36.5, 36, 39, 41, false, 'Doğu Anadolu']];
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), R = {}, hat = [];
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR);
    for (let i = 0; i < BOLGE.length; i++) await p.evaluate(a => __bolge(...a), [...BOLGE[i], i === 0]);
    await p.evaluate(() => cmpRender()); await p.waitForTimeout(300);
    R[ad] = await p.evaluate(() => __oku());
    if (ad === 'sonra') {
      R.kayit = await p.evaluate(() => CMP.map((r, i) => { const s = cmpStats(r); return { name: r.name, gk74: r.gk74, mcU: r.mcU, turU: r.turU, n: s.n, T: s.T, b: s.b, Mc: r.Mc, tr6: s.tr6, Mmax: s.Mmax }; }));
      R.cap = await p.evaluate(() => cmpProbFigLast && { en: cmpProbFigLast.capEn, tr: cmpProbFigLast.capTr });
      const tEl = await p.$('#cmpTable'); await tEl.scrollIntoViewIfNeeded(); await tEl.screenshot({ path: path.join(__dirname, 'cmp_tablo.png') });
      const fEl = await p.$('#cmpProbFigSvg'); await fEl.scrollIntoViewIfNeeded(); await fEl.screenshot({ path: path.join(__dirname, 'cmp_sekil_95.png') });
      const [dS] = await Promise.all([p.waitForEvent('download'), p.evaluate(() => cmpProbFigDownload('svg', 'en'))]); await dS.saveAs(path.join(__dirname, 'cmp_sekil_EN.svg'));
      const [dJ] = await Promise.all([p.waitForEvent('download'), p.evaluate(() => cmpProbFigDownload('json', 'en'))]); await dJ.saveAs(path.join(__dirname, 'cmp_yeniden_uretim.json'));
      const [dP] = await Promise.all([p.waitForEvent('download'), p.evaluate(() => cmpProbFigDownload('png', 'en'))]); await dP.saveAs(path.join(__dirname, 'cmp_sekil_EN_600dpi.png'));
      R.boot = await p.evaluate(() => { const S = CMP.map(cmpStats), hucre = B => { GR_POIS.B = B; cmpProbCache.clear(); const o = CMP.map((r, i) => { const pr = cmpProb(r, S[i]); return { B: pr.bt.B, nFail: pr.bt.nFail, sampler: pr.bt.sampler, c: [5, 6, 7].flatMap(M => [10, 50, 100].map(t => { const c = pr.cell(M, t); return { M, t, P: c.P, lo: c.lo, hi: c.hi }; })) }; }); return o; };
        const b2 = hucre(2000), b5 = hucre(5000); GR_POIS.B = 2000; cmpProbCache.clear();
        const gr = CMP.map((r, i) => { const g = grPoissonBootSimple(S[i].n, S[i].T, S[i].b, r.Mc, r.dm || 0.1, 7, 50), c = cmpProb(r, S[i]).cell(7, 50); return { lo: g.pLo, hi: g.pHi, clo: c.lo, chi: c.hi, B: g.B }; });
        return { b2, b5, gr }; });
      R.bender = await p.evaluate(async () => { const t0 = __tablo(); CMP_B_EST = 'bender'; cmpRender(); const t1 = __tablo(), fig = document.getElementById('cmpProbFigSvg').innerHTML, cap = cmpProbFigLast.capEn,
          kayit = CMP.map((r, i) => { const s = cmpStats(r); return { n: s.n, T: s.T, Mc: r.Mc, bB: s.bB, b: s.b }; }); return { t0, t1, fig, cap, kayit }; });
      { const [dJ2] = await Promise.all([p.waitForEvent('download'), p.evaluate(() => cmpProbFigDownload('json', 'en'))]); await dJ2.saveAs(path.join(__dirname, 'cmp_yeniden_uretim_bender.json'));
        const [dS2] = await Promise.all([p.waitForEvent('download'), p.evaluate(() => cmpProbFigDownload('svg', 'en'))]); await dS2.saveAs(path.join(__dirname, 'cmp_sekil_EN_bender.svg')); }
      const fB = await p.$('#cmpProbFigSvg'); await fB.screenshot({ path: path.join(__dirname, 'cmp_sekil_95_bender.png') });
      R.benderGeri = await p.evaluate(() => { CMP_B_EST = 'aki'; cmpRender(); return __tablo(); });
      R.dipnot = await p.evaluate(() => document.getElementById('cmpTable').innerText);
      R.dugme = await p.evaluate(() => [...document.querySelectorAll('#cmpProbFig button')].map(b => b.textContent).join(' | '));
      R.fig68 = await p.evaluate(() => { cmpProbFigBand = '68'; cmpRender(); return document.getElementById('cmpProbFigSvg').innerHTML; });
      const fEl2 = await p.$('#cmpProbFigSvg'); await fEl2.screenshot({ path: path.join(__dirname, 'cmp_sekil_68.png') });
      await p.evaluate(() => { cmpProbFigBand = '95'; cmpRender(); });
    }
    hat.push(...hatalar); await ctx.close();
  }
  const O = R.once, Y = R.sonra;
  // (1) önce = sonra
  const eskiSat = Object.keys(O.tablo), degisen = eskiSat.filter(k => JSON.stringify(O.tablo[k]) !== JSON.stringify(Y.tablo[k]));
  ok(eskiSat.length > 10 && degisen.length === 0, `(1) main'deki ${eskiSat.length} tablo satırının hepsi aynı değerlerle duruyor${degisen.length ? ' — değişen: ' + degisen.join(', ') : ''}`);
  const yeni = Object.keys(Y.tablo).filter(k => !(k in O.tablo)); ok(yeni.length === 6 && yeni.filter(k => /^P\(≥[567]; t\)/.test(k)).length === 3 && yeni.includes('Olasılık uyarıları') && yeni.some(k => /^Tr\(≥M\) \/ T/.test(k)) && yeni.some(k => /^b \[%95 bootstrap\]/.test(k)), `(1) yalnız 6 yeni satır: ${yeni.join(' | ')}`);
  ok(O.cmpSvg === Y.cmpSvg, '(1) karşılaştırma grafiği (cmpSvg) aynı');
  ok(O.grSvg === Y.grSvg && O.grTxt === Y.grTxt, '(1) G–R grafiği ve metni (Poisson satırı dışında) aynı');
  ok(O.bSvg === Y.bSvg && O.bTxt === Y.bTxt && O.aSvg === Y.aSvg && O.aTxt === Y.aTxt, '(1) b(t) ve a(t) grafikleri ve metinleri aynı');
  // (2) yeni hücreler bağımsız hesapla
  const pc = v => v > 0.999 ? '> 99,9' : v < 0.001 ? '< 0,1' : (100 * v).toFixed(1).replace('.', ',');
  let uy = 0, top = 0, tr6ok = true;
  R.kayit.forEach((k, i) => { for (const M of [5, 6, 7]) { const lam = k.n / k.T * Math.pow(10, -k.b * (M - k.Mc)), hucre = Y.tablo[Object.keys(Y.tablo).find(z => z.startsWith(`P(≥${M}; t)`))][i];
    for (const t of [10, 50, 100]) { top++; const P = -Math.expm1(-lam * t); if (hucre.includes(`${t} yıl: ${pc(P)}`)) uy++; if (M === 6 && Math.abs(P - (1 - Math.exp(-t / k.tr6))) > 1e-12) tr6ok = false; } } });
  ok(uy === top, `(2) ${top} hücrenin ${uy}'i bağımsız hesapla aynı (P = 1 − e^(−λt), λ = n/T·10^(−b(M − Mc)))`);
  ok(tr6ok, '(2) P(≥6; t) = 1 − e^(−t/tr6): tablodaki tekrarlanma süresiyle tutarlı');
  // (3) uyarılar
  ok(R.kayit[0].gk74 === false && R.kayit[1].gk74 === true && /GK74 kapalı/.test(Y.tablo['Olasılık uyarıları'][0]) && /GK74 açık/.test(Y.tablo['Olasılık uyarıları'][1]), '(3) GK74 durumu kayıtta ve uyarıda doğru (Türkiye kapalı, Marmara açık)');
  ok(R.kayit.every(k => k.turU !== undefined && k.mcU !== undefined), `(3) tamlık ve tür uyarı alanları kayıtlı (${R.kayit.map(k => `${k.name}: tür ${k.turU || 'yok'}`).join('; ')})`);
  // (4) şekil
  const F = Y.fig || ''; ok(/width="493pt"/.test(F) && (F.match(/font-weight="bold">\([abc]\)/g) || []).length === 3 && [10, 25, 50, 100].every(t => F.includes(`t = ${t} yr`)), '(4) yayın şekli: 493 pt, 3 panel (a–c), 4 süre');
  ok(R.fig68 && R.fig68 !== F && /16th–84th percentile</.test(R.fig68), '(4) bant düğmesi (16.–84. yüzdelik) şekli değiştiriyor');
  // (7) aşama 2: etiket ve ekstrapolasyon sınıfı
  const tumMetin = [F, R.fig68, R.cap.en, R.cap.tr, JSON.stringify(Y.tablo), R.dugme || ''].join(' ');
  ok(!/±1σ|±1 σ/.test(tumMetin) && /16\.–84\. yüzdelik/.test(R.dugme || ''), `(7) şekil, altyazı, tablo ve düğmede '±1σ' yok (düğme: "${R.dugme}")`);
  const trSat = Y.tablo[Object.keys(Y.tablo).find(z => /^Tr\(≥M\) \/ T/.test(z))], sinif = []; let trUy = 0, trTop = 0;
  R.kayit.forEach((k, i) => { for (const M of [5, 6, 7]) { trTop++; const tr = k.T / (k.n * Math.pow(10, -k.b * (M - k.Mc))), q = tr / k.T, c = q <= 1 ? '' : q <= 10 ? '†' : '‡';
    const trS = tr >= 100 ? Math.round(tr).toLocaleString('tr-TR') : tr.toFixed(tr >= 10 ? 0 : 1).replace('.', ','), satir = trSat[i].split(/(?=M≥)/).find(z => z.startsWith(`M≥${M}:`)) || '';
    if (satir.startsWith(`M≥${M}: ${trS} yıl`) && (c ? satir.trim().endsWith(c) : !/[†‡]/.test(satir))) trUy++; sinif.push(`${k.name} M≥${M}: Tr ${trS} yıl, Tr/T ${q.toFixed(2)}${c ? ' ' + c : ''}`); } });
  ok(trUy === trTop, `(7) Tr/T satırı: ${trTop} hücrenin ${trUy}'i bağımsız hesapla ve sınıfla aynı`);
  console.log('     ' + sinif.join('\n     '));
  { const k = R.kayit[1], tr7 = k.T / (k.n * Math.pow(10, -k.b * (7 - k.Mc))), u = Y.tablo['Olasılık uyarıları'][1];
    ok(tr7 / k.T > 10 && /‡ M≥7: Tr ≈ .* yüksek ekstrapolasyon belirsizliği/.test(u), `(7) Marmara M≥7: Tr ≈ ${tr7.toFixed(0)} yıl, T = ${k.T.toFixed(1)} yıl (Tr/T = ${(tr7 / k.T).toFixed(2)}) → ‡ belirgin uyarı`); }
  ok((F.match(/<tspan dy="-1\.5"> = T<\/tspan>/g) || []).length === 3 && /fill-opacity="0\.06"/.test(F) && /Grey area: Tr > 10T/.test(R.cap.en), '(7) şekil: her panelde Tr = T çizgisi, Tr > 10T gri zemin, lejant ve altyazı');
  ok(/operational criterion/.test(R.cap.en) && /operasyonel bir değerlendirme ölçütüdür/.test(R.cap.tr) && /operasyonel bir ölçüttür/.test(JSON.stringify(R.dipnot || '')), '(7) 10T sınırı altyazıda (EN/TR) ve tablo dipnotunda operasyonel ölçüt olarak belirtiliyor');
  ok(R.cap && /not an earthquake forecast/.test(R.cap.en) && /deprem tahmini değildir/.test(R.cap.tr) && /\(c\) Doğu Anadolu/.test(R.cap.en), '(4) altyazı EN/TR, üç bölge');
  ok(!O.fig, '(4) önce (main) yayın şekli yok');
  // (8) aşama 3: NegBin, B = 2000, sağlamlık B = 5000
  { const { b2, b5, gr } = R.boot; let mx = 0, mxAt = ''; const sat = [];
    b2.forEach((x, i) => x.c.forEach((c, j) => { const d = b5[i].c[j], dl = 100 * Math.max(Math.abs(c.lo - d.lo), Math.abs(c.hi - d.hi)); if (dl > mx) { mx = dl; mxAt = `${R.kayit[i].name} M≥${c.M}, t = ${c.t}`; }
      if (c.M === 7 && c.t === 50) sat.push(`${R.kayit[i].name}: %95 [${(100 * c.lo).toFixed(2)}–${(100 * c.hi).toFixed(2)}] (B 2000) / [${(100 * d.lo).toFixed(2)}–${(100 * d.hi).toFixed(2)}] (B 5000)`); }));
    R.sonuc_boot = { maks_fark_yp: mx, yer: mxAt, M7_t50: sat };
    ok(b2.every(x => x.B === 2000 && x.sampler === 'NegBin (Gamma–Poisson)') && b5.every(x => x.B === 5000), `(8) üç bölgede B = 2000 (NegBin; Türkiye dahil, eski şemada 200); sağlamlık B = 5000 hesaplandı`);
    ok(mx < 1.0, `(8) B = 2000 ile 5000 arasında %95 sınırlarının en büyük farkı ${mx.toFixed(3)} yüzde puan (${mxAt}); P(≥7; 50 yıl): ${sat.join('; ')}`);
    ok(gr.every(g => g.lo === g.clo && g.hi === g.chi && g.B === 2000), '(8) G–R panelinin bootstrap\'ı (grPoissonBootSimple) ile karşılaştırma tablosu aynı çekilişler: P(≥7; 50 yıl) sınırları birebir aynı');
  }
  // (9) aşama 4: yeniden üretim
  { const sv = fs.readFileSync(path.join(__dirname, 'cmp_sekil_EN.svg'), 'utf8'), mm = sv.match(/<metadata id="eqlive-repro"><!\[CDATA\[([\s\S]*?)\]\]><\/metadata>/); let M = null; try { M = mm && JSON.parse(mm[1]); } catch (e) {}
    const b0 = M && M.bolgeler[0], gerek = M && b0 && b0.katalog && b0.katalog.uretim && b0.katalog.dosyalar && b0.katalog.blob && b0.donem.T_yil > 0 && b0.Mc !== undefined && b0.a !== undefined && b0.b > 0 && b0.N_geMc > 0 && b0.bolge.geometri
      && M.model.tur && M.model.Mmax && M.model.Mmax.varsayim && M.model.Mmax.kaynak && M.ayarlar.bootstrap.B === 2000 && M.ayarlar.bootstrap.tohum === 20261027 && M.yazilim.index_html_git_blob_sha1 && /<title>/.test(sv) && /<desc>Figure\./.test(sv);
    ok(!!gerek && M.bolgeler.length === 3 && !('girdi_buyukluklar' in b0) && /^[0-9a-f]{64}$/.test(b0.girdi_buyukluk_sha256),
      `(9) SVG <metadata>: katalog (${b0 ? b0.katalog.dosyalar.join(', ') + ', üretim ' + b0.katalog.uretim + ', blob ' + Object.values(b0.katalog.blob)[0].slice(0, 10) : '—'}), bölge ve dönem, Mc, a, b, N, T, model, B ve tohum, Mmax varsayımı ve kaynağı, yazılım blob ${M ? String(M.yazilim.index_html_git_blob_sha1).slice(0, 10) : '—'}; <title> ve <desc>`);
    const J = JSON.parse(fs.readFileSync(path.join(__dirname, 'cmp_yeniden_uretim.json'), 'utf8'));
    ok(J.bolgeler.length === 3 && J.bolgeler.every(b => b.girdi_buyukluklar && b.girdi_buyukluklar.length === b.N_tum && b.sonuc && b.sonuc.length === 3 * 4), `(9) JSON kaydı: 3 bölge, girdi büyüklükleri (${J.bolgeler.map(b => b.N_tum).join(' / ')}), 12 hücre/bölge (M 5–7 × t 10/25/50/100), ayarlar, model, yazılım (${(fs.statSync(path.join(__dirname, 'cmp_yeniden_uretim.json')).size / 1024).toFixed(0)} KB)`);
    const { execFileSync } = require('child_process'); let out = '', kod = 0; try { out = execFileSync(process.execPath, [path.join(__dirname, 'yeniden_uret.js'), path.join(__dirname, 'cmp_yeniden_uretim.json')], { encoding: 'utf8' }); } catch (e) { out = String(e.stdout || ''); kod = e.status; }
    const son = out.trim().split('\n').pop(); R.yeniden = out;
    ok(kod === 0 && /GEÇTİ: \d+ geçti, 0 kaldı/.test(son) && (out.match(/\(5\) 12 hücrenin 12'i aynı/g) || []).length === 3, `(9) yeniden_uret.js kayıttan bütün sayıları birebir yeniden üretti: ${son}`); }
  // (10) b kestiricisi seçimi
  { const ON = process.env.ONCEKI_SONUC ? JSON.parse(fs.readFileSync(process.env.ONCEKI_SONUC, 'utf8')).tablo : null, sat = (T, re) => T[Object.keys(T).find(k => re.test(k))];
    if (ON) { const es = [5, 6, 7].every(M => JSON.stringify(sat(Y.tablo, new RegExp(`^P\\(≥${M}; t\\)`))) === JSON.stringify(sat(ON, new RegExp(`^P\\(≥${M}; t\\)`)))) && JSON.stringify(sat(Y.tablo, /^Tr\(≥M\)/)) === JSON.stringify(sat(ON, /^Tr\(≥M\)/)) && JSON.stringify(Y.tablo['Olasılık uyarıları']) === JSON.stringify(ON['Olasılık uyarıları']);
      ok(es, '(10) varsayılan (Aki–Utsu): P(≥5/6/7; t), Tr/T ve uyarı satırları önceki sürümle birebir aynı'); }
    const yy = sat(Y.tablo, /^b \[%95 bootstrap\]/), BB = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'b_kestirici', 'bender_karsilastirma.json'), 'utf8')).bolgeler;
    ok(yy && yy.every((c, i) => c.includes(`Aki–Utsu: ${BB[i].b_AU.toFixed(3)} [${BB[i].boot.AU.lo.toFixed(3)}–${BB[i].boot.AU.hi.toFixed(3)}]`) && c.includes(`Bender: ${BB[i].b_Bender.toFixed(3)} [${BB[i].boot.Bender.lo.toFixed(3)}–${BB[i].boot.Bender.hi.toFixed(3)}]`)),
      `(10) yan yana satır: b ve %95 aralık iki kestiriciyle; ayrı analizle (b_kestirici) aynı — ${yy ? yy.map(c => c.split('P(≥7')[0]).join(' | ') : '—'}`);
    const pc = v => v > 0.999 ? '> 99,9' : v < 0.001 ? '< 0,1' : (100 * v).toFixed(1).replace('.', ','), Bt = R.bender.t1; let uy = 0, top = 0;
    R.bender.kayit.forEach((k, i) => { for (const M of [5, 6, 7]) { const h = sat(Bt, new RegExp(`^P\\(≥${M}; t\\)`))[i]; for (const t of [10, 50, 100]) { top++; if (h.includes(`${t} yıl: ${pc(-Math.expm1(-k.n / k.T * Math.pow(10, -k.bB * (M - k.Mc)) * t))}`)) uy++; } } });
    ok(uy === top && Object.keys(Bt).some(k => /^P\(≥7; t\).*b: Bender$/.test(k)) && /b \(Bender\) = /.test(R.bender.fig) && /Bender \(1983\) maximum-likelihood estimate/.test(R.bender.cap), `(10) Bender seçili: ${top} hücrenin ${uy}'i bağımsız hesapla (b_B, aynı n, T, Mc) aynı; satır etiketi, şekil başlığı ve altyazı kestiriciyi belirtiyor`);
    const JB = JSON.parse(fs.readFileSync(path.join(__dirname, 'cmp_yeniden_uretim_bender.json'), 'utf8')), sv = fs.readFileSync(path.join(__dirname, 'cmp_sekil_EN_bender.svg'), 'utf8');
    const { execFileSync } = require('child_process'); let out = '', kod = 0; try { out = execFileSync(process.execPath, [path.join(__dirname, 'yeniden_uret.js'), path.join(__dirname, 'cmp_yeniden_uretim_bender.json')], { encoding: 'utf8' }); } catch (e) { out = String(e.stdout || ''); kod = e.status; }
    ok(JB.ayarlar.b_kestiricisi.secili === 'bender' && JB.bolgeler.every(b => b.bootstrap.b_kestiricisi === 'bender' && b.b_olasilikta === b.b_Bender) && /"secili": "bender"/.test(sv) && kod === 0 && (out.match(/12 hücrenin 12'i aynı/g) || []).length === 3,
      `(10) JSON ve SVG metadata kestiriciyi kaydediyor (secili: bender); yeniden_uret.js Bender kaydını birebir üretti: ${out.trim().split('\n').pop()}`);
    ok(JSON.stringify(R.benderGeri) === JSON.stringify(R.bender.t0), '(10) Aki–Utsu\'ya dönünce tablo ilk hâliyle birebir aynı'); }
  // (5) indirilen dosyalar
  const svgD = fs.readFileSync(path.join(__dirname, 'cmp_sekil_EN.svg'), 'utf8'), png = fs.readFileSync(path.join(__dirname, 'cmp_sekil_EN_600dpi.png'));
  const Wp = png.readUInt32BE(16), Hp = png.readUInt32BE(20), m = svgD.match(/viewBox="0 0 ([0-9.]+) ([0-9.]+)"/);
  ok(/^<\?xml/.test(svgD) && m && +m[1] === 493, `(5) SVG indirildi (${(svgD.length / 1024).toFixed(0)} KB, vektörel, 493 × ${m && m[2]} pt)`);
  ok(Wp === Math.round(493 * 600 / 72) && Hp === Math.round(+m[2] * 600 / 72), `(5) PNG 600 dpi: ${Wp} × ${Hp} px (= 174 mm genişlik)`);
  ok(!hat.length, `(6) sayfa hatası yok (${hat.length})` + (hat.length ? ': ' + hat.join(' | ') : ''));
  fs.writeFileSync(path.join(__dirname, 'kabul_cmp_prob_sonuc.json'), JSON.stringify({ kayit: R.kayit, tablo: Y.tablo, bootstrap: R.sonuc_boot, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
