// Kabul testi (2026-10-26): canlı zaman düğmesi (1s/24s/1 Hafta/1 Ay/90 Gün/1 Yıl) tarihsel pencere seçim listesini (activeHistWindows) temizler.
// Hata (düzeltme öncesi): düğmelerin vurgusu kalkıyor, liste kalıyordu → sonraki tarihsel seçim, görünmeyen eski pencereleri de birleşime katıyordu;
// aynı pencereye yeniden basmak onu açmak yerine kapatıyordu.
// Aynı senaryolar ÖNCE (verilen index.html) ve SONRA (depodaki index.html) sayfalarında çalışır.
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/tarihsel_pencere/kabul_pencere_secimi.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_pencere_secimi.js <önceki_index.html>'); process.exit(2); }
const srv = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split('?')[0]), f = u === '/__once.html' ? ONCE : path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT) && f !== ONCE) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': f.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' }); r.end(b); });
});
let pass = 0, fail = 0; const kayit = [];
const ok = (c, m) => { (c ? pass++ : fail++); kayit.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };
async function sayfa(br, yol) {
  const ctx = await br.newContext(), p = await ctx.newPage(), hatalar = [];
  p.on('pageerror', e => hatalar.push(String(e)));
  await ctx.route('**/*', rt => { const u = rt.request().url();
    if (u.startsWith('http://127.0.0.1')) return rt.continue();
    if (/leaflet@1\.9\.4\/dist\/leaflet\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.js'), contentType: 'text/javascript' });
    if (/leaflet@1\.9\.4\/dist\/leaflet\.css/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.css'), contentType: 'text/css' });
    if (/leaflet-heat\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet.heat/dist/leaflet-heat.js'), contentType: 'text/javascript' });
    return rt.abort(); });
  await p.routeWebSocket(/.*/, ws => ws.close()).catch(() => {});
  await p.goto(`http://127.0.0.1:${srv.address().port}${yol}`, { waitUntil: 'load' });
  await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function');
  return { p, hatalar };
}
// Adımlar: 'h:<sec>' tarihsel düğme (onclick ile aynı çağrı), 'c:<data-h>' canlı zaman düğmesi (gerçek tıklama)
async function senaryo(p, adimlar) {
  return p.evaluate(async adimlar => {
    for (const a of adimlar) {
      if (a.startsWith('h:')) { const b = document.querySelector(a.slice(2));
        await toggleHistoricalWindow(b, +b.dataset.hist, b.dataset.histEnd ? +b.dataset.histEnd : undefined, b.dataset.histSrc || undefined); }
      else { document.querySelector(`.tbtn[data-h="${a.slice(2)}"]`).click(); await new Promise(r => setTimeout(r, 50)); }
    }
    const aktif = [...document.querySelectorAll('.tbtn[data-hist].active')].map(b => b.dataset.hist + (b.dataset.histSrc ? '/' + b.dataset.histSrc : ''));
    const n = historicalMode ? events.length : null;
    const srcs = historicalMode ? [...new Set(events.map(e => e.src))].sort().join('+') : '';
    return { n, aktif, liste: activeHistWindows.map(w => w.key), tarihsel: historicalMode, srcs };
  }, adimlar);
}
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch(), E98 = 'h:.tbtn[data-hist="1998"]', I00 = 'h:.tbtn[data-hist="1900"]', I71 = 'h:.tbtn[data-hist="1971"]', AY = 'c:720';
  const SEN = {
    'A: EMSC 1998 → 1 Ay → ISC 1900': [E98, AY, I00],
    'B: ISC 1900 → 1 Ay → ISC 1900': [I00, AY, I00],
    'C: ISC 1900 + 1971 → 1 Ay': [I00, I71, AY],
    'R1: ISC 1900': [I00], 'R2: ISC 1900 + 1971': [I00, I71], 'R3: EMSC 1998 + ISC 1900 − EMSC 1998': [E98, I00, E98]
  };
  const sonuc = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    sonuc[ad] = {};
    for (const [k, a] of Object.entries(SEN)) { const { p, hatalar } = await sayfa(br, yol); sonuc[ad][k] = { ...(await senaryo(p, a)), hatalar: hatalar.length }; await p.close(); }
  }
  const O = sonuc.once, S = sonuc.sonra, A = 'A: EMSC 1998 → 1 Ay → ISC 1900', B = 'B: ISC 1900 → 1 Ay → ISC 1900', C = 'C: ISC 1900 + 1971 → 1 Ay';
  ok(O[A].n !== O['R1: ISC 1900'].n && O[A].liste.length === 2, `Hata önce yeniden üretildi (A): görünen düğme ${JSON.stringify(O[A].aktif)}, liste ${O[A].liste.length} pencere, N ${O[A].n}, kaynak ${O[A].srcs}`);
  ok(S[A].n === S['R1: ISC 1900'].n && S[A].liste.length === 1 && JSON.stringify(S[A].aktif) === '["1900"]' && S[A].srcs === O['R1: ISC 1900'].srcs,
    `Sonra (A): yalnız ISC 1900 — N ${S[A].n}, düğme ${JSON.stringify(S[A].aktif)}, kaynak ${S[A].srcs}`);
  ok(!O[B].tarihsel, `Hata önce (B): ikinci basış pencereyi açmadı (tarihsel mod ${O[B].tarihsel})`);
  ok(S[B].tarihsel && S[B].n === S['R1: ISC 1900'].n && JSON.stringify(S[B].aktif) === '["1900"]', `Sonra (B): ikinci basış pencereyi açtı (N ${S[B].n})`);
  ok(O[C].liste.length === 2 && S[C].liste.length === 0 && !S[C].tarihsel && !S[C].aktif.length, `C: 1 Ay sonrası liste önce ${O[C].liste.length}, sonra ${S[C].liste.length}; tarihsel mod kapalı, vurgulu düğme yok`);
  for (const k of ['R1: ISC 1900', 'R2: ISC 1900 + 1971', 'R3: EMSC 1998 + ISC 1900 − EMSC 1998'])
    ok(JSON.stringify(O[k]) === JSON.stringify(S[k]), `Gerileme ${k}: önce = sonra (N ${S[k].n}, düğme ${JSON.stringify(S[k].aktif)})`);
  ok(Object.values(O).every(x => !x.hatalar) && Object.values(S).every(x => !x.hatalar), 'Sayfa hatası yok');
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify({ senaryolar: SEN, sonuc, denetimler: kayit, ozet: { pass, fail } }, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
