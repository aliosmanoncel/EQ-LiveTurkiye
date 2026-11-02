// Kabul testi (2026-11-02, 2b): bölge karşılaştırma tablosunda kullanıcı tanımlı büyüklük (seçilen M) için λ, Tr, Tr/T ve P(10/50/100).
// Önce = verilen index.html (main 0408c0e), sonra = depodaki index.html. Bölgeler kabul_cmp_prob.js ile aynı (Türkiye GK74 kapalı, Marmara GK74 açık, Doğu Anadolu GK74 kapalı).
// Kabul koşulları:
//   (0) Varsayılan: 'seçilen M' alanı sayfa açılışında boş; dokunulmadan tablo, cmpSvg ve şekil önce = sonra (kullanıcı kararı 2026-11-02: varsayılan görünüm değişmez).
//   (1) Seçilen M boşken tablo, cmpSvg ve olasılık şekli önce = sonra. Kullanıcı 7,5 ve 8 girince: main'deki bütün tablo satırları aynı değerlerle;
//       yalnız 4 yeni satır; cmpSvg ve şekil aynı.
//   (2) Aynı hesap yolu: yeni satır değerleri cmpProb(...).cell(M, t) ile ve G–R panelinin fonksiyonu grPoissonBootSimple ile (λ, λ %95, P, P %95) birebir;
//       G–R panelinin kendisi (M girdisi = 8) gösterilen bölge için tabloyla aynı λ, Tr aralığı ve P aralığı.
//   (3) M≥6 tekrarlanma satırı (tr6) = 1/λ(≥6) olasılık satırlarıyla aynı model (Aki–Utsu).
//   (4) Bender seçilince yeni satırlar Bender'e geçer (bağımsız hesapla aynı); Aki–Utsu'ya dönünce ilk hâl.
//   (5) Yeniden üretim JSON'u seçilen M hücrelerini içerir ve yeniden_uret.js hepsini birebir üretir.
//   (6) Ham katalog işareti (ʰ) yalnız GK74 kapalı bölgelerde; dipnot var. (7) Girdi biçimleri. (8) Sayfa hatası yok; 390 px'te sayfa taşması yok.
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/poisson_olasilik/kabul_secili_M.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_secili_M.js <önceki_index.html>'); process.exit(2); }
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
const rel = (a, b) => a === b ? 0 : Math.abs(a - b) / Math.max(Math.abs(a), Math.abs(b));
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), R = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR);
    for (let i = 0; i < BOLGE.length; i++) await p.evaluate(a => __bolge(...a), [...BOLGE[i], i === 0]);
    const set = async v => p.evaluate(v => { const e = document.getElementById('cmpPM'); if (e) e.value = v; cmpRender(); }, v);
    R[ad] = { ilk: await p.evaluate(() => ({ v: document.getElementById('cmpPM') ? document.getElementById('cmpPM').value : null, o: __oku() })) };
    await set(''); await p.waitForTimeout(200); R[ad].bos = await p.evaluate(() => __oku());
    await set('7.5 8'); await p.waitForTimeout(200); R[ad].vars = await p.evaluate(() => __oku());
    if (ad === 'sonra') {
      R.yol = await p.evaluate(() => { const S = CMP.map(cmpStats); return CMP.map((r, i) => { const s = S[i], pr = cmpProb(r, s, 'aki');
        return { ad: r.name, gk74: r.gk74, tr6: s.tr6, tr6b: pr.cell(6, 10).tr, M: cmpSelM().map(M => { const g = grPoissonBootSimple(s.n, s.T, s.b, r.Mc, r.dm || 0.1, M, 50, { }), L = cmpLamCi(pr, s, r, M);
          return { M, lam: pr.cell(M, 50).lam, lamG: grLambdaSimple(s.n, s.T, s.b, r.Mc, M), Llo: L.lo, Lhi: L.hi, gLlo: g.lamLo, gLhi: g.lamHi,
            c: [10, 50, 100].map(t => { const c = pr.cell(M, t), g2 = grPoissonBootSimple(s.n, s.T, s.b, r.Mc, r.dm || 0.1, M, t); return { t, P: c.P, lo: c.lo, hi: c.hi, gP: grPoissonP(grLambdaSimple(s.n, s.T, s.b, r.Mc, M), t), glo: g2.pLo, ghi: g2.pHi, tr: c.tr, trT: c.trT, exC: c.exC }; }) }; }) }; }); });
      // G–R panelinin kendisi: gösterilen (son eklenen) bölge, M = 8, t = 50
      R.gr = await p.evaluate(() => { document.getElementById('grPM').value = '8'; document.getElementById('grPt').value = '50'; onGrBinSizeChange(); const q = lastGrPois;
        const i = CMP.length - 1, r = CMP[i], s = cmpStats(r), pr = cmpProb(r, s, 'aki'), c = pr.cell(8, 50), L = cmpLamCi(pr, s, r, 8);
        return { path: q.path, lam: q.lam, lamLo: q.ci.lamLo, lamHi: q.ci.lamHi, pLo: q.ci.pLo, pHi: q.ci.pHi, n: q.n, T: q.T, b: q.b, mc: q.mc, tab: { lam: c.lam, Llo: L.lo, Lhi: L.hi, lo: c.lo, hi: c.hi, n: s.n, T: s.T, b: s.b, Mc: r.Mc } }; });
      R.hucre = await p.evaluate(() => __tablo());
      R.bender = await p.evaluate(() => { CMP_B_EST = 'bender'; cmpRender(); const t = __tablo(), S = CMP.map(cmpStats);
        const bag = CMP.map((r, i) => { const s = S[i]; return [7.5, 8].map(M => [10, 50, 100].map(t => -Math.expm1(-(s.n / s.T) * Math.pow(10, -s.bB * (M - r.Mc)) * t))); });
        const cell = CMP.map((r, i) => { const pr = cmpProb(r, S[i], 'bender'); return [7.5, 8].map(M => [10, 50, 100].map(t => pr.cell(M, t).P)); });
        CMP_B_EST = 'aki'; cmpRender(); return { t, bag, cell, geri: __tablo() }; });
      const [dJ] = await Promise.all([p.waitForEvent('download'), p.evaluate(() => cmpProbFigDownload('json', 'en'))]); await dJ.saveAs(path.join(__dirname, 'secili_M_yeniden_uretim.json'));
      R.girdi = await p.evaluate(() => { const o = {}; for (const v of ['7,5; 8', '7.5, 8', '6 7', '8 7.5 7.5', '10 2', '7,5 8 8,5 9']) { document.getElementById('cmpPM').value = v; o[v] = cmpSelM(); } document.getElementById('cmpPM').value = '7.5 8'; cmpRender(); return o; });
      const el = await p.$('#cmpTable'); await el.scrollIntoViewIfNeeded(); await el.screenshot({ path: path.join(__dirname, 'secili_M_tablo.png') });
      await p.setViewportSize({ width: 390, height: 844 }); await p.waitForTimeout(300); R.mobil = await p.evaluate(() => ({ vw: innerWidth, sw: document.documentElement.scrollWidth }));
    }
    R[ad].hatalar = hatalar; await ctx.close();
  }
  const O = R.once, Y = R.sonra, keys = o => Object.keys(o.tablo || {});
  ok(Y.ilk.v === '' && JSON.stringify(O.ilk.o.tablo) === JSON.stringify(Y.ilk.o.tablo) && O.ilk.o.cmpSvg === Y.ilk.o.cmpSvg && O.ilk.o.fig === Y.ilk.o.fig, `(0) Varsayılan: seçilen M alanı boş ("${Y.ilk.v}"); dokunulmadan tablo (${keys(Y.ilk.o).length} satır), cmpSvg ve şekil önce = sonra`);
  ok(JSON.stringify(O.bos.tablo) === JSON.stringify(Y.bos.tablo) && O.bos.cmpSvg === Y.bos.cmpSvg && O.bos.fig === Y.bos.fig, `(1) Seçilen M boş: tablo (${keys(Y.bos).length} satır), cmpSvg ve olasılık şekli önce = sonra`);
  const eski = keys(O.vars), yeni = keys(Y.vars).filter(k => !eski.includes(k)), ayni = eski.every(k => JSON.stringify(O.vars.tablo[k]) === JSON.stringify(Y.vars.tablo[k]));
  ok(ayni && yeni.length === 4 && O.vars.cmpSvg === Y.vars.cmpSvg && O.vars.fig === Y.vars.fig, `(1) Kullanıcı 7,5 ve 8 girdi: main'deki ${eski.length} satır aynı değerlerle; yalnız ${yeni.length} yeni satır: ${yeni.map(k => k.split(' — ')[0]).join(' | ')}; cmpSvg ve şekil aynı`);
  let mx = 0, mxG = 0; for (const b of R.yol) for (const m of b.M) { mx = Math.max(mx, rel(m.lam, m.lamG), ...m.c.map(c => rel(c.P, c.gP))); mxG = Math.max(mxG, rel(m.Llo, m.gLlo), rel(m.Lhi, m.gLhi), ...m.c.map(c => Math.max(Math.abs(c.lo - c.glo), Math.abs(c.hi - c.ghi)))); }
  ok(mx === 0 && mxG === 0, `(2) Yeni satırlar = cmpProb.cell = G–R fonksiyonları (grLambdaSimple, grPoissonBootSimple): λ, P en büyük göreli fark ${mx}; λ %95 ve P %95 en büyük fark ${mxG}`);
  for (const b of R.yol) for (const m of b.M) { const c50 = m.c[1]; const k = b.ad;
    const tx = (Y.vars.tablo[`Seçilen M ≥ ${String(m.M).replace('.', ',')}: P(t), % [%95] — Poisson, tüm bölge, b: Aki–Utsu`] || [])[R.yol.indexOf(b)] || '';
    console.log(`     ${k} M≥${m.M}: λ = ${m.lam.toExponential(3)} [${m.Llo.toExponential(3)}–${m.Lhi.toExponential(3)}], Tr = ${c50.tr.toFixed(0)} yıl, Tr/T = ${c50.trT.toFixed(1)} (${c50.exC}); ekranda P: ${tx.replace(/\s+/g, ' ')}`); }
  const g = R.gr, gt = g.tab;
  ok(g.path === 'tekMc' && g.n === gt.n && g.mc === gt.Mc && rel(g.T, gt.T) < 1e-12 && g.b === gt.b && rel(g.lam, gt.lam) < 1e-12 && g.lamLo === gt.Llo && g.lamHi === gt.Lhi && g.pLo === gt.lo && g.pHi === gt.hi,
    `(2) G–R panelinin kendisi (M = 8, t = 50, Doğu Anadolu): n ${g.n}/${gt.n}, Mc ${g.mc}/${gt.Mc}, T ${g.T.toFixed(4)}/${gt.T.toFixed(4)}, b ${g.b}/${gt.b}; λ ${g.lam.toExponential(4)}/${gt.lam.toExponential(4)}; Tr aralığı ve P aralığı tabloyla birebir`);
  if (!(g.lamLo === gt.Llo && g.pLo === gt.lo)) console.log('   G–R:', JSON.stringify(g));
  ok(R.yol.every(b => rel(b.tr6, b.tr6b) < 1e-12), `(3) M≥6 tekrarlanma satırı = Tr(≥6) olasılık satırı (Aki–Utsu): ${R.yol.map(b => `${b.ad} ${b.tr6.toFixed(3)} / ${b.tr6b.toFixed(3)}`).join('; ')}`);
  const bOk = R.bender.bag.every((x, i) => x.every((y, j) => y.every((v, k) => rel(v, R.bender.cell[i][j][k]) < 1e-12)));
  const bKey = Object.keys(R.bender.t).filter(k => /^Seçilen M/.test(k));
  ok(bOk && bKey.length === 4 && bKey.every(k => /b: Bender/.test(k)) && JSON.stringify(R.bender.geri) === JSON.stringify(R.hucre), `(4) Bender: yeni satırlar Bender'e geçti, P bağımsız hesapla aynı; Aki–Utsu'ya dönünce tablo ilk hâl`);
  const J = JSON.parse(fs.readFileSync(path.join(__dirname, 'secili_M_yeniden_uretim.json'), 'utf8')), sM = J.bolgeler.map(b => b.sonuc.filter(c => c.M === 7.5 || c.M === 8).length);
  const cp = require('child_process').spawnSync('node', [path.join(__dirname, 'yeniden_uret.js'), path.join(__dirname, 'secili_M_yeniden_uretim.json')], { encoding: 'utf8', timeout: 300000 });
  const son = (cp.stdout + cp.stderr).trim().split('\n'); son.filter(l => /\(5\)/.test(l)).forEach(l => console.log('     ' + l.slice(0, 200)));
  ok(JSON.stringify(J.ayarlar.olasilik.M_secilen) === '[7.5,8]' && sM.every(n => n === 2 * J.bolgeler[0].sonuc.map(c => c.t).filter((t, i, a) => a.indexOf(t) === i).length) && cp.status === 0, `(5) JSON: M_secilen = [7.5, 8], bölge başına ${sM.join('/')} seçilen M hücresi; yeniden_uret.js: ${son.slice(-1)[0]}`);
  const hk = Object.keys(Y.vars.tablo).filter(k => /^Seçilen M/.test(k)), ham = R.yol.map((b, i) => hk.every(k => /ʰ/.test(Y.vars.tablo[k][i])));
  ok(R.yol.every((b, i) => ham[i] === (b.gk74 === false)), `(6) ʰ işareti: ${R.yol.map((b, i) => `${b.ad} (GK74 ${b.gk74 ? 'açık' : 'kapalı'}) ${ham[i] ? 'var' : 'yok'}`).join(', ')}`);
  const G = R.girdi;
  ok(JSON.stringify(G['7,5; 8']) === '[7.5,8]' && JSON.stringify(G['7.5, 8']) === '[7.5,8]' && JSON.stringify(G['6 7']) === '[]' && JSON.stringify(G['8 7.5 7.5']) === '[7.5,8]' && JSON.stringify(G['10 2']) === '[]' && G['7,5 8 8,5 9'].length === 3,
    `(7) Girdi: ${Object.entries(G).map(([k, v]) => `"${k}" → [${v}]`).join('; ')}`);
  ok(!O.hatalar.length && !Y.hatalar.length && R.mobil.sw <= R.mobil.vw, `(8) Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length}); 390 px'te scrollWidth ${R.mobil.sw}`);
  await br.close(); srv.close();
  fs.writeFileSync(path.join(__dirname, 'kabul_secili_M_sonuc.json'), JSON.stringify({ kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
