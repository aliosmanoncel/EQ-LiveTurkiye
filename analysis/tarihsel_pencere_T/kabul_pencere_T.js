// Kabul testi (2026-10-27): tarihsel modda bölge analizi penceresi = seçili tarihsel pencere(ler).
// Hata (main 543ac56): fetchRegionEventsFromHistorical, regionWindowStart/End'i tüm kataloğun starttime/endtime değerinden
// (1900-01-01 → katalog sonu) alıyordu. Bu pencere T olarak şu bileşenlere giriyordu: Weichert dönem sonu (csBuild), Oran/Yoğunluk
// modu (renderGutenbergRichter), Bölge karşılaştırması (cmpAdd t0/t1), bölge bilgi satırı (Aktivite Yoğunluğu) ve pencere etiketi.
// Aynı senaryolar ÖNCE (verilen index.html, ör. main) ve SONRA (depodaki index.html) sayfalarında çalışır. Veri yerel, ağ gerekmez.
// Denetimler (ChatGPT kontrol listesi):
//   (1) Seçili aralık bütün bileşenlerde kullanılıyor (pencere, Weichert dönemleri, Oran modu T, karşılaştırma t0/t1, bilgi satırı).
//   (2) Sınır durumları: olaylar [başlangıç, bitiş] içinde; 1971–1997 için T = 27,0 yıl; açık uçlu pencere (EMSC 1998–) katalog sonunda
//       biter (şimdiki zamanda değil); bitişik pencereler tek aralık; bitişik olmayan pencerelerde uyarı; küresel ISC-GEM 1904–2021.
//   (3) Tek Mc ve Weichert ayrı ayrı: tek Mc b/Mc/N değişmez (T'ye bağlı değil); Weichert b ve λ önce/sonra raporlanır.
//   (4) Oran/Yoğunluk, Bölge karşılaştırması ve bölge bilgi satırı yeni T ile tutarlı (bağımsız yeniden hesap).
//   (5) Canlı mod ve tarihsel pencere seçili değilken davranış değişmez (histSelWindow = null).
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/tarihsel_pencere_T/kabul_pencere_T.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_pencere_T.js <önceki_index.html>'); process.exit(2); }
const srv = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split('?')[0]), f = u === '/__once.html' ? ONCE : path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT) && f !== ONCE) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); });
});
let pass = 0, fail = 0; const kayit = [];
const ok = (c, m) => { (c ? pass++ : fail++); kayit.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };
async function sayfa(br, yol) {
  const ctx = await br.newContext({ viewport: { width: 1400, height: 1000 } }), p = await ctx.newPage(), hatalar = [];
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
const KUR = `
window.__bekle = async () => { for (let i = 0; i < 600; i++) { if (!regionLoading && regionEvents && regionEvents.length) return true; await new Promise(r => setTimeout(r, 50)); } return false; };
window.__pencere = async ks => { for (const k of ks) { const [a, b, s] = k; const sel = s ? '.tbtn[data-hist-src="' + s + '"]' : '.tbtn[data-hist="' + a + '"]:not([data-hist-src])';
  if (s === 'ISCGEM-GLOBAL') setScope('global'); await toggleHistoricalWindow(document.querySelector(sel), a, b, s); } };
window.__dikdortgen = async (S, W, N, E) => { regionSelectStart(); map.fire('mousedown', { latlng: L.latLng(S, W) }); map.fire('mousemove', { latlng: L.latLng(N, E) }); await regionMouseUp(); await __bekle(); };
window.__daire = async (lat, lon, km) => { regionDeselect(); litRegionLayer = L.circle([lat, lon], { radius: km * 1000 }); litRegionCommitToQuery(); await __bekle(); };
window.__oku = () => { const Y = 365.25 * 864e5, ts = regionEvents.map(e => +e.time);
  return { ws: regionWindowStart ? regionWindowStart.toISOString() : null, we: regionWindowEnd ? regionWindowEnd.toISOString() : null,
    T: regionWindowStart && regionWindowEnd ? (regionWindowEnd - regionWindowStart) / Y : null, n: regionEvents.length,
    tmin: new Date(Math.min(...ts)).toISOString(), tmax: new Date(Math.max(...ts)).toISOString(), durum: document.getElementById('statusTxt').textContent,
    bilgi: document.getElementById('regionInfo') ? document.getElementById('regionInfo').textContent : '',
    sel: typeof histSelWindow !== 'undefined' && histSelWindow ? { contiguous: histSelWindow.contiguous, parca: histSelWindow.parts.length } : null }; };
window.__tm = () => { if (!showTimeMag) toggleTimeMag(); else renderTimeMag([...events, ...liveEvents]); };
window.__tekMc = () => { csEnabled = false; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = false; onCsChange(true); __tm(); return lastGrSimple ? { b: lastGrSimple.b, a: lastGrSimple.a, n: lastGrSimple.n, mc: lastGrSimple.mc } : null; };
window.__weichert = steps => { csSteps = steps.map(([start, mc]) => ({ start, mc })); csEnabled = true; const cb = document.getElementById('csEnabled'); if (cb) cb.checked = true; csRenderRows(); onCsChange(true); __tm();
  const c = lastGrFit && lastGrFit.curves[0]; return { donem: lastCs.periods.map(q => [new Date(q.t0).toISOString().slice(0, 10), new Date(q.t1).toISOString().slice(0, 10), q.mc]),
    b: c ? c.b : null, rate0: c ? c.rate0 : null, m0: lastGrFit ? lastGrFit.m0 : null, lam7: lastGrFit && lastGrFit.fnBest ? lastGrFit.fnBest(7) : null }; };
window.__oran = () => { csEnabled = false; onCsChange(true); setGrNormMode('rate'); __tm(); const r = { ...window.lastGrNorm }; setGrNormMode('raw'); return { years: r.years, mode: r.mode }; };
window.__cmp = () => { CMP = []; cmpAdd(); const c = CMP[CMP.length - 1]; const r = { t0: new Date(c.t0).toISOString(), t1: new Date(c.t1).toISOString(), T: (c.t1 - c.t0) / (365.25 * 864e5) }; CMP = []; return r; };
`;
const STEPS_TR = [['1971-01-01', '4.5'], ['1985-01-01', '4.0']];
const STEPS_ERKEN = [['1960-01-01', '4.5'], ['1985-01-01', '4.0']];   // ilk basamak pencere başından (1971) önce: dönem pencere başında kırpılmalı
const SEN = {   // ad: [pencereler, bölge]
  isc71_97:      [[[1971, 1997]], ['r', 36, 26, 42, 45]],
  isc71_97_emsc: [[[1971, 1997], [1998]], ['r', 36, 26, 42, 45]],
  emsc98:        [[[1998]], ['r', 36, 26, 42, 45]],
  bosluklu:      [[[1900, 1970], [1998]], ['r', 36, 26, 42, 45]],
  daire71_97:    [[[1971, 1997]], ['c', 38.5, 28.5, 150]],
  iscgem_kuresel:[[[1904, 2021, 'ISCGEM-GLOBAL']], ['r', 30, 20, 45, 50]],
};
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), S = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    S[ad] = {}; const hat = [];
    for (const [k, [ws, bolge]] of Object.entries(SEN)) {
      const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR); await p.evaluate(w => __pencere(w), ws);
      let hataBolge = null;
      try { if (bolge[0] === 'r') await p.evaluate(b => __dikdortgen(...b), bolge.slice(1)); else await p.evaluate(b => __daire(...b), bolge.slice(1)); }
      catch (e) { hataBolge = String(e.message || e).split('\n')[0]; }
      if (hataBolge) { S[ad][k] = { hataBolge }; hat.push(...hatalar); await ctx.close(); continue; }
      const r = await p.evaluate(() => __oku());
      r.tek = await p.evaluate(() => __tekMc()); r.cmp = await p.evaluate(() => __cmp());
      if (k === 'isc71_97' || k === 'isc71_97_emsc') r.w = await p.evaluate(s => __weichert(s), STEPS_TR);
      if (k === 'isc71_97') r.wErken = await p.evaluate(s => __weichert(s), STEPS_ERKEN);
      if (k === 'daire71_97') r.oran = await p.evaluate(() => __oran());
      S[ad][k] = r; hat.push(...hatalar); await ctx.close();
    }
    { const { p, ctx, hatalar } = await sayfa(br, yol); await p.evaluate(KUR);   // (5) canlı mod: tarihsel pencere yok
      S[ad].canli = await p.evaluate(() => ({ hist: historicalMode, sel: typeof histSelWindow === 'undefined' ? 'yok' : histSelWindow })); hat.push(...hatalar); await ctx.close(); }
    S[ad].hatalar = hat;
  }
  const O = S.once, Y = S.sonra, d10 = s => s.slice(0, 10), approx = (a, b, t) => Math.abs(a - b) <= t;
  console.log('\nÖnce → sonra pencere ve T:');
  for (const k of Object.keys(SEN)) console.log(O[k].hataBolge ? `  ${k.padEnd(15)} önce: HATA (${O[k].hataBolge})  ⇒  ${d10(Y[k].ws)} → ${d10(Y[k].we)} (T ${Y[k].T.toFixed(2)}); N = ${Y[k].n}` : `  ${k.padEnd(15)} ${O[k].ws ? d10(O[k].ws) : '—'} → ${O[k].we ? d10(O[k].we) : '—'} (T ${O[k].T ? O[k].T.toFixed(2) : '—'})  ⇒  ${d10(Y[k].ws)} → ${d10(Y[k].we)} (T ${Y[k].T.toFixed(2)}); N = ${Y[k].n}`);
  // (1) seçili aralık
  const s1 = Y.isc71_97;
  ok(d10(s1.ws) === '1971-01-01' && s1.we.startsWith('1997-12-31T23:59:59') && approx(s1.T, 27, 0.01), `(1)(2) ISC 1971–1997: pencere ${d10(s1.ws)} → ${s1.we.slice(0, 19)}, T = ${s1.T.toFixed(3)} yıl (önce ${O.isc71_97.T.toFixed(1)})`);
  ok(s1.w.donem[s1.w.donem.length - 1][1] <= '1998-01-01' && s1.w.donem[0][0] === '1971-01-01', `(1) Weichert dönemleri: ${s1.w.donem.map(q => q.join('→')).join(', ')} (önce son dönem ${O.isc71_97.w.donem.slice(-1)[0].slice(0, 2).join('→')})`);
  ok(approx(s1.cmp.T, s1.T, 1e-9) && d10(s1.cmp.t0) === '1971-01-01', `(1)(4) Bölge karşılaştırması t0–t1 = ${d10(s1.cmp.t0)} → ${d10(s1.cmp.t1)}, T = ${s1.cmp.T.toFixed(3)} (önce ${O.isc71_97.cmp.T.toFixed(1)})`);
  ok(/Pencere: Tarihsel Katalog \(1971–1997\)/.test(s1.bilgi), `(1) Bölge bilgi satırı: "${(s1.bilgi.match(/Pencere: Tarihsel Katalog \([^)]*\)/) || ['—'])[0]}" (önce "${(O.isc71_97.bilgi.match(/Pencere: Tarihsel Katalog \([^)]*\)/) || ['—'])[0]}")`);
  // (4) bilgi satırındaki Aktivite Yoğunluğu = N(M≥Mc)/T/A·1e6 (alan sayfadaki regionAreaKm2 ile aynı; yalnız T oranı denetlenir)
  { const d0 = O.daire71_97, d1 = Y.daire71_97; const ro = d0.bilgi.match(/Aktivite Yoğunluğu = ([\d.]+)/), rs = d1.bilgi.match(/Aktivite Yoğunluğu = ([\d.]+)/);
    const oranOS = ro && rs ? +rs[1] / +ro[1] : null, beklenen = d0.T / d1.T;
    ok(oranOS !== null && approx(oranOS, beklenen, 0.02 * beklenen), `(4) Daire bölge bilgi satırı Aktivite Yoğunluğu ${ro ? ro[1] : '—'} → ${rs ? rs[1] : '—'} /10⁶km²/yıl; oran ${oranOS ? oranOS.toFixed(3) : '—'} = T_önce/T_sonra ${beklenen.toFixed(3)} (N ve A aynı)`); }
  // (2) sınırlar
  ok(Object.keys(SEN).every(k => Y[k].tmin >= Y[k].ws && Y[k].tmax <= Y[k].we), '(2) Tüm senaryolarda olaylar [pencere başı, pencere sonu] içinde');
  ok(Object.keys(SEN).every(k => O[k].hataBolge || Y[k].n === O[k].n), `(2) Olay sayıları önce = sonra (yalnız T değişti): ${Object.keys(SEN).map(k => `${k} ${Y[k].n}`).join(', ')}`);
  ok(d10(Y.emsc98.ws) === '1998-01-01' && d10(Y.emsc98.we) === d10(O.emsc98.we) && Y.emsc98.we >= Y.emsc98.tmax, `(2) Açık uçlu EMSC 1998–: katalog sonunda biter (${d10(Y.emsc98.we)}, şimdiki zaman değil); başlangıç 1900 → 1998`);
  ok(d10(Y.isc71_97_emsc.ws) === '1971-01-01' && Y.isc71_97_emsc.sel.contiguous && !/bitişik değil/.test(Y.isc71_97_emsc.durum), '(2) Bitişik pencereler (1971–1997 + 1998–): tek aralık 1971 → katalog sonu, uyarı yok');
  ok(!Y.bosluklu.sel.contiguous && /bitişik değil/.test(Y.bosluklu.durum) && d10(Y.bosluklu.ws) === '1900-01-01', `(2) Bitişik olmayan pencereler (1900–1970 + 1998–): uyarı "${(Y.bosluklu.durum.match(/⚠[^·]*/) || [''])[0].trim()}"`);
  ok(d10(Y.iscgem_kuresel.ws) === '1904-01-01' && d10(Y.iscgem_kuresel.we) === '2021-12-31', `(2) Küresel ISC-GEM 1904–2021: pencere ${d10(Y.iscgem_kuresel.ws)} → ${d10(Y.iscgem_kuresel.we)} — önce: ${O.iscgem_kuresel.hataBolge ? 'bölge sorgusu hata veriyordu (' + O.iscgem_kuresel.hataBolge + ')' : O.iscgem_kuresel.ws ? d10(O.iscgem_kuresel.ws) + ' → ' + d10(O.iscgem_kuresel.we) : 'pencere yok'}`);
  ok(!Y.iscgem_kuresel.hataBolge && Y.iscgem_kuresel.n > 0 && Y.iscgem_kuresel.tek, `(2) Küresel ISC-GEM penceresinde bölge sorgusu çalışıyor (N = ${Y.iscgem_kuresel.n}; G–R tek Mc b = ${Y.iscgem_kuresel.tek ? Y.iscgem_kuresel.tek.b.toFixed(3) : '—'})`);
  // (3) tek Mc ve Weichert
  ok(Object.keys(SEN).every(k => O[k].hataBolge || JSON.stringify(Y[k].tek) === JSON.stringify(O[k].tek)), `(3) Tek Mc b, a, N, Mc önce = sonra (T'ye bağlı değil) — ör. ISC 1971–1997: b = ${s1.tek.b.toFixed(3)}, N(≥Mc) = ${s1.tek.n}`);
  for (const k of ['isc71_97', 'isc71_97_emsc']) { const o = O[k].w, y = Y[k].w;
    console.log(`     Weichert ${k}: b ${o.b.toFixed(3)} → ${y.b.toFixed(3)}; λ(≥${y.m0}) ${o.rate0.toFixed(2)} → ${y.rate0.toFixed(2)}/yıl; λ(≥7) ${o.lam7.toExponential(3)} → ${y.lam7.toExponential(3)}/yıl`); }
  ok(Y.isc71_97.w.rate0 > O.isc71_97.w.rate0, '(3) ISC 1971–1997 Weichert: λ(≥m₀) arttı (boş 1998–2026 yılları artık sayılmıyor)');
  ok(JSON.stringify(Y.isc71_97_emsc.w.donem) === JSON.stringify(O.isc71_97_emsc.w.donem) && approx(Y.isc71_97_emsc.w.b, O.isc71_97_emsc.w.b, 1e-4) && approx(Y.isc71_97_emsc.w.rate0 / O.isc71_97_emsc.w.rate0, 1, 1e-4), `(3) 1971–2026 (bitişik, katalog sonuna kadar): Weichert dönemleri aynı; b ${O.isc71_97_emsc.w.b.toFixed(6)} → ${Y.isc71_97_emsc.w.b.toFixed(6)} (göreli fark < 1e-4: pencere sonu katalog tarihinin 00:00'ı yerine seçili penceredeki son olay zamanı — birkaç saat)`);
  { const o = O.isc71_97.wErken, y = Y.isc71_97.wErken;
    ok(y.donem[0][0] === '1971-01-01' && JSON.stringify(y.donem) === JSON.stringify(s1.w.donem) && Math.abs(y.b - s1.w.b) < 1e-12,
      `(2) İlk basamak pencere başından önce (1960): dönem 1971'de kırpılıyor, sonuç 1971 basamağıyla aynı (b = ${y.b.toFixed(3)}); önce ilk dönem ${o.donem[0].slice(0, 2).join('→')}, b = ${o.b.toFixed(3)}`); }
  // (4) Oran modu
  ok(Y.daire71_97.oran.mode === 'rate' && approx(Y.daire71_97.oran.years, 27, 0.01), `(4) Daire bölge, Oran modu: T = ${Y.daire71_97.oran.years.toFixed(3)} yıl (önce ${O.daire71_97.oran.years ? O.daire71_97.oran.years.toFixed(1) : '—'})`);
  // (5) canlı mod
  ok(!Y.canli.hist && Y.canli.sel === null, '(5) Canlı mod: tarihsel pencere yok, histSelWindow = null (canlı yol değişmedi)');
  ok(!O.hatalar.length && !Y.hatalar.length, `Sayfa hatası yok (önce ${O.hatalar.length}, sonra ${Y.hatalar.length})` + (Y.hatalar.length ? ': ' + Y.hatalar.join(' | ') : ''));
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify({ senaryolar: SEN, weichert_basamaklari: STEPS_TR, erken_basamaklar: STEPS_ERKEN, sonuc: S, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
