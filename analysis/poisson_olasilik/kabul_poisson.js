// Kabul testi (2026-10-27): G–R panelinde Poisson aşılma olasılığı satırı.
// Aynı senaryolar ÖNCE (verilen index.html, ör. main) ve SONRA (depodaki index.html) sayfalarında çalışır.
// Veri: yerel tarihsel katalog (Türkiye modu, ISC 1971–1997 penceresi; dikdörtgen bölge 36–42° K, 26–45° D) — ağ gerekmez.
// Kabul koşulları:
//   (1) Mevcut çıktılar değişmez: G–R grafiği (SVG) ve Poisson satırı dışındaki istatistik metni önce = sonra
//       (tek Mc / Weichert; GK74 kapalı/açık; Mx boş/7,5). Tek istisna tek Mc panelinin "a" gösterimidir (Ham modda aynı kalmalı).
//   (2) λ, Tr ve P panelden bağımsız yeniden hesaplanır: tek Mc λ = N(≥Mc)/T·10^(−b(M−Mc)); Weichert λ = lastGrFit.fnBest(M) (panel eğrisi);
//       P = 1 − e^(−λt), Tr = 1/λ; ekrandaki yüzde ve yıl değerleri bu sayılarla aynı.
//   (3) Girdiler: M ve t değişince değerler güncellenir, URL'ye yazılır (pm, pt); varsayılan M ≥ 7, t = 50.
//   (4) Uyarılar: GK74 kapalıyken uyarı var, açıkken yok; M > gözlenen en büyük → ekstrapolasyon uyarısı; Mx girildi ve M ≥ Mx → λ = 0 ve uyarı.
//   (5) Bölge bütünü / tahmin değildir notu ve belirsizlik kapsamı (dahil/dahil değil) metinde.
// Ekran görüntüleri: poisson_tekMc_gk74kapali.png, poisson_tekMc_gk74acik.png, poisson_weichert.png, poisson_weichert_mx.png
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/poisson_olasilik/kabul_poisson.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_poisson.js <önceki_index.html>'); process.exit(2); }
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
  // Tamlık denetimi: pencerenin ilk yarısı boşsa uyarı (seçili pencere 1971–1997 iken 1900'den başlatılmış gibi; yalnız test için)
  ['tekMc_ilkYariBos', async p => p.evaluate(() => { __cs(false); __set('grMx', ''); __set('grPM', '7'); regionWindowStart = new Date('1900-01-01T00:00:00Z'); renderTimeMag([...events, ...liveEvents]); })],
];
const GORUNTU = { tekMc_gk74kapali: 'poisson_tekMc_gk74kapali.png', tekMc_gk74acik: 'poisson_tekMc_gk74acik.png', weichert_gk74kapali: 'poisson_weichert.png', weichert_mx75_M8: 'poisson_weichert_mx.png' };
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), S = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR); await p.evaluate(() => __kur()); await p.waitForTimeout(300);
    S[ad] = {};
    for (const [k, f] of ADIM) { await f(p); await p.waitForTimeout(150); S[ad][k] = await p.evaluate(() => __oku());
      if (ad === 'sonra' && GORUNTU[k]) { await p.evaluate(() => { const s = document.getElementById('tmSvgGR'); s.parentElement.scrollIntoView(); });
        const el = await p.evaluateHandle(() => { const s = document.getElementById('tmSvgGR'), d = document.createElement('div'); return s.parentElement; });
        const box = await p.evaluate(() => { const a = document.getElementById('grPoisInRow').getBoundingClientRect(), b = document.getElementById('tmStatsGR'), r = document.getElementById('grPoisRow');
          const y0 = a.top + scrollY - 4, y1 = (r ? r.getBoundingClientRect().bottom : b.getBoundingClientRect().bottom) + scrollY + 6, x0 = b.getBoundingClientRect().left + scrollX - 4;
          return { x: Math.max(0, x0), y: Math.max(0, y0), width: b.getBoundingClientRect().width + 8, height: y1 - y0 }; });
        await p.screenshot({ path: path.join(__dirname, GORUNTU[k]), clip: box, fullPage: true }); } }
    S[ad].hatalar = hatalar; await ctx.close();
  }
  const O = S.once, Y = S.sonra;
  // (1) mevcut çıktılar değişmedi
  for (const [k] of ADIM.filter(([k]) => k !== 'tekMc_ilkYariBos')) {
    // Beklenen tek metin farkı: tek Mc panelinde a'nın tanımı (Ham modda değer aynı, yalnız tanım eklendi)
    const ETIKET = ' (log₁₀N = a − bM; N: dönem toplamı)', yM = Y[k].metin.replace(ETIKET, '');
    const sv = O[k].svg === Y[k].svg, mt = O[k].metin === yM;
    if (k.startsWith('tekMc')) ok(Y[k].metin.includes(ETIKET) && !O[k].metin.includes(ETIKET), `(1) ${k}: beklenen tek metin farkı — a'nın tanımı eklendi ("a=… (log₁₀N = a − bM; N: dönem toplamı)"), a değeri aynı`);
    ok(sv && mt, `(1) ${k}: G–R grafiği önce = sonra (${sv ? 'aynı' : 'FARKLI'}), Poisson satırı ve a tanımı dışındaki metin önce = sonra (${mt ? 'aynı' : 'FARKLI'})`);
    if (!mt) { const a = O[k].metin, b = yM; let i = 0; while (i < a.length && a[i] === b[i]) i++; console.log('   fark: …' + a.slice(Math.max(0, i - 60), i + 80) + '\n   yeni: …' + b.slice(Math.max(0, i - 60), i + 80)); }
  }
  ok(O.tekMc_gk74kapali.pois === null && Y.tekMc_gk74kapali.pois !== null, '(1) Önce Poisson satırı yok; sonra var');
  // (2) bağımsız yeniden hesap
  const P = (l, t) => -Math.expm1(-l * t), pct = v => (100 * v).toFixed(1).replace('.', ',');
  for (const k of ['tekMc_gk74kapali', 'tekMc_M6_t75', 'tekMc_M8_5', 'tekMc_gk74acik']) {
    const y = Y[k], q = y.pois_n, g = y.simple, lam = g.n / y.T * Math.pow(10, -g.b * (q.M - g.mc));
    const rel = Math.abs(q.lam / lam - 1), pTxt = `P = %${pct(P(lam, q.t))}`;
    ok(q.path === 'tekMc' && rel < 1e-12 && Math.abs(q.T - y.T) < 1e-9 && y.pois.includes(pTxt) && q.ci.lamLo <= lam && lam <= q.ci.lamHi,
      `(2) ${k}: λ(≥${q.M}) = ${lam.toExponential(3)}/yıl = N(≥Mc)/T·10^(−b(M−Mc)) [N=${g.n}, T=${y.T.toFixed(2)}, b=${g.b.toFixed(3)}, Mc=${g.mc}] (göreli fark ${rel.toExponential(1)}); Tr = ${(1 / lam).toPrecision(3)} yıl; ${q.t} yılda ${pTxt} ekranda; %95 [${q.ci.lamLo.toExponential(2)}, ${q.ci.lamHi.toExponential(2)}] λ'yı içeriyor`);
  }
  for (const k of ['weichert_gk74acik', 'weichert_gk74kapali', 'weichert_mx75_M7', 'weichert_mx75_M8']) {
    const y = Y[k], q = y.pois_n, lam = y.fnBest;
    const same = q && lam !== null && (lam === 0 ? q.lam === 0 : Math.abs(q.lam / lam - 1) < 1e-12);
    ok(q && q.path === 'weichert' && same && y.pois.includes(`P = %${pct(P(lam, q.t))}`),
      `(2) ${k}: λ(≥${q.M}) = ${lam === 0 ? '0' : lam.toExponential(3)}/yıl = panel en iyi tahmin eğrisi (lastGrFit.fnBest)${q.mx !== null ? `, Mx = ${q.mx}` : ''}; P = %${pct(P(lam, q.t))} ekranda; b = ${q.b.toFixed(3)}, m₀ = ${q.m0}`);
  }
  // Tarihsel pencere (tarihsel-pencere-T düzeltmesiyle): tek Mc T = seçili pencere
  ok(Math.abs(Y.tekMc_gk74kapali.pois_n.T - 27) < 0.01 && /T = 27\.0 yıl/.test(Y.tekMc_gk74kapali.pois), `(2) Tek Mc T = ${Y.tekMc_gk74kapali.pois_n.T.toFixed(3)} yıl = seçili pencere ISC 1971–1997 (düzeltme öncesi 126,7)`);
  { const w = s => (s.match(/ilk yarısında belirgin az \(([^)]*)\)/) || [null, null])[1];
    const a = Y.tekMc_gk74kapali, z = Y.tekMc_ilkYariBos;
    ok(/ilk yarısında belirgin az \(0 \/ /.test(z.pois), `(2) İlk yarı boş (T 1900'den): tamlık uyarısı "${w(z.pois)}"`);
    console.log(`     Seçili pencerede (1971–1997) tamlık denetimi: ${w(a.pois) ? 'uyarı "' + w(a.pois) + '" (ISC 1971–1984 dönemi M ≥ Mc = 3,7 için eksik)' : 'uyarı yok'}`); }
  // (3) girdiler
  ok(Y.tekMc_gk74kapali.pois_n.M === 7 && Y.tekMc_gk74kapali.pois_n.t === 50, '(3) Varsayılan M ≥ 7, t = 50 yıl');
  ok(Y.tekMc_M6_t75.pois_n.M === 6 && Y.tekMc_M6_t75.pois_n.t === 75 && /pm=6/.test(Y.tekMc_M6_t75.url) && /pt=75/.test(Y.tekMc_M6_t75.url), `(3) M = 6, t = 75 girdisi uygulandı ve URL'ye yazıldı (${Y.tekMc_M6_t75.url.match(/p[mt]=[^&]*/g).join(', ')})`);
  ok(Y.tekMc_M6_t75.pois_n.lam > Y.tekMc_gk74kapali.pois_n.lam, '(3) λ(≥6) > λ(≥7)');
  // (4) uyarılar
  const gkU = s => /GK74 artçı ayıklama kapalı/.test(s);
  ok(gkU(Y.tekMc_gk74kapali.pois) && !gkU(Y.tekMc_gk74acik.pois) && gkU(Y.weichert_gk74kapali.pois) && !gkU(Y.weichert_gk74acik.pois), '(4) GK74 uyarısı: kapalıyken var, açıkken yok (tek Mc ve Weichert)');
  ok(/ekstrapolasyon/.test(Y.tekMc_M8_5.pois) && Y.tekMc_M8_5.mObsMax < 8.5, `(4) M ≥ 8,5 > gözlenen en büyük (${Y.tekMc_M8_5.mObsMax.toFixed(1)}): ekstrapolasyon uyarısı`);
  ok(Y.weichert_mx75_M8.pois_n.lam === 0 && /M ≥ Mx/.test(Y.weichert_mx75_M8.pois) && /P = %0,0/.test(Y.weichert_mx75_M8.pois), '(4) Mx = 7,5, M ≥ 8: λ = 0, P = %0,0 ve "M ≥ Mx" uyarısı');
  ok(Y.weichert_mx75_M7.pois_n.lam < Y.weichert_gk74kapali.pois_n.lam, `(4) Kesik G–R (Mx = 7,5) λ(≥7) = ${Y.weichert_mx75_M7.pois_n.lam.toExponential(2)} < kesilmesiz ${Y.weichert_gk74kapali.pois_n.lam.toExponential(2)}`);
  // (5) kapsam notları
  ok(['tekMc_gk74kapali', 'weichert_gk74kapali'].every(k => /seçili bölgenin tamamı/.test(Y[k].pois) && /tahmin değildir/.test(Y[k].pois) && /Dahil değil: Mc\/tamlık seçimi, Mx, büyüklük hataları/.test(Y[k].pois) && /parametrik bootstrap/.test(Y[k].pois)),
    '(5) "bölgenin tamamı / tahmin değildir" notu ve belirsizlik kapsamı (bootstrap; dahil değil listesi) iki yolda da var');
  ok(!O.hatalar.length && !Y.hatalar.length, `Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length})` + (Y.hatalar.length ? ': ' + Y.hatalar.join(' | ') : ''));
  const ozet = {}; for (const [k] of ADIM) ozet[k] = { poisson: Y[k].pois, sayisal: Y[k].pois_n };
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify({ senaryo: 'Türkiye modu, ISC 1971–1997, dikdörtgen 36–42 K / 26–45 D; Weichert basamakları 1971 M≥4,5, 1985 M≥4,0', sonuc: ozet, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
