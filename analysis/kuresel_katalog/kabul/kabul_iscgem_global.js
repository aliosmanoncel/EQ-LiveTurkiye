// Kabul testi (2026-10-26): küresel ISC-GEM v12.1 penceresi (hazırlık). Yalnız kuresel-katalog-olcum dalı.
// Aynı tıklama dizisi iki sayfada çalıştırılır: ÖNCE (değişiklik öncesi index.html kopyası) ve SONRA (güncel index.html).
// Denetimler: (1) Türkiye modundaki tüm tarihsel pencereler ve TR ISC-GEM katmanı önce/sonra birebir aynı (olay sayısı, olay içeriği
// özeti, durum ve ipucu metni, Mc ve b); (2) yeni satır Türkiye modunda gizli, Global modda görünür, varsayılan kapalı ve sayfa
// açılışında data/iscgem_global.json indirilmez; (3) küresel pencere 74 159 olay, doğrudan/vekil oranı ve kapsam uyarısı;
// (4) Türkiye moduna dönülünce küresel pencere kapanır; (5) tarayıcı konsolunda sayfa hatası yok.
// Dış istekler (karo, canlı API, WebSocket) engellenir; Leaflet/leaflet.heat yerel kopyadan (LEAFLET_DIR) verilir.
// Kullanım (depo kökünde): LEAFLET_DIR=<node_modules> node analysis/kuresel_katalog/kabul/kabul_iscgem_global.js <önceki_index.html>
'use strict';
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..', '..'), ONCE = process.argv[2], LD = process.env.LEAFLET_DIR;
if (!ONCE || !LD) { console.error('kullanım: LEAFLET_DIR=... node kabul_iscgem_global.js <önceki_index.html>'); process.exit(2); }
const MIME = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.js': 'text/javascript', '.png': 'image/png', '.css': 'text/css', '.txt': 'text/plain; charset=utf-8' };
const istekler = [];
const srv = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split('?')[0]); istekler.push(u);
  const f = u === '/__once.html' ? ONCE : path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT) && f !== ONCE) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); r.end(b); });
});
let pass = 0, fail = 0; const sonuc = { denetimler: [] };
const ok = (c, m) => { (c ? pass++ : fail++); sonuc.denetimler.push((c ? 'GEÇTİ ' : 'KALDI ') + m); console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); };

async function sayfa(br, yol) {
  const ctx = await br.newContext(), p = await ctx.newPage(), hatalar = [];
  p.on('pageerror', e => hatalar.push(String(e)));
  await ctx.route('**/*', rt => {
    const u = rt.request().url();
    if (u.startsWith('http://127.0.0.1')) return rt.continue();
    if (/unpkg\.com\/leaflet@1\.9\.4\/dist\/leaflet\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.js'), contentType: 'text/javascript' });
    if (/unpkg\.com\/leaflet@1\.9\.4\/dist\/leaflet\.css/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet/dist/leaflet.css'), contentType: 'text/css' });
    if (/leaflet\.heat\/0\.2\.0\/leaflet-heat\.js/.test(u)) return rt.fulfill({ path: path.join(LD, 'leaflet.heat/dist/leaflet-heat.js'), contentType: 'text/javascript' });
    return rt.abort();
  });
  await p.routeWebSocket(/.*/, ws => ws.close()).catch(() => {});
  await p.goto(`http://127.0.0.1:${srv.address().port}${yol}`, { waitUntil: 'load' });
  await p.waitForFunction(() => typeof toggleHistoricalWindow === 'function' && typeof map !== 'undefined');
  return { p, ctx, hatalar };
}
// Pencereyi aç/kapat ve sonucu özetle (olay sayısı, içerik özeti, metinler, Mc, b)
async function pencere(p, sec) {
  return p.evaluate(async sec => {
    const b = document.querySelector(sec);
    await toggleHistoricalWindow(b, +b.dataset.hist, b.dataset.histEnd ? +b.dataset.histEnd : undefined, b.dataset.histSrc || undefined);
    const ev = events.map(e => [e.id || '', +e.time, e.lat, e.lon, e.dep, e.mag, e.mw, e.mtype, e.src].join('|')).sort();
    const mags = events.map(e => e.mw ?? e.mag), Mc = computeMc(events), bv = Mc == null ? null : computeBvalue(mags, Mc, 0.1);
    return { n: events.length, ozet: ev.join('\n'), durum: document.getElementById('statusTxt').textContent, ipucu: document.getElementById('histHint').textContent,
             Mc, b: bv == null ? null : +bv.toFixed(6), aktif: b.classList.contains('active'), tarihsel: historicalMode };
  }, sec);
}
const h = s => crypto.createHash('sha256').update(s).digest('hex').slice(0, 16);

(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const br = await chromium.launch();
  const TR = ['.tbtn[data-hist="1998"]', '.tbtn[data-hist="1900"]', '.tbtn[data-hist="1971"]', '.tbtn[data-hist-src="EPICA"]', '.tbtn[data-hist-src="SHARE-CET"]'];
  const kosu = {};
  for (const [ad, yol] of [['once', '/__once.html'], ['sonra', '/']]) {
    const { p, ctx, hatalar } = await sayfa(br, yol), r = { pencereler: {}, iscgem_tr: null };
    for (const s of TR) { const a = await pencere(p, s); await pencere(p, s); r.pencereler[s] = a; }   // aç, özetle, kapat
    await p.evaluate(() => { document.getElementById('histIscgem').checked = true; });   // TR ISC-GEM katmanı açık + ISC 1900–1970
    r.iscgem_tr = await pencere(p, '.tbtn[data-hist="1900"]'); await pencere(p, '.tbtn[data-hist="1900"]');
    await p.evaluate(() => { document.getElementById('histIscgem').checked = false; });
    r.cok = await (async () => { await pencere(p, TR[1]); const x = await pencere(p, TR[2]); await pencere(p, TR[1]); await pencere(p, TR[2]); return x; })();   // çoklu seçim
    r.hatalar = hatalar; kosu[ad] = { r, p, ctx };
  }
  const O = kosu.once.r, S = kosu.sonra.r;
  // (1) Türkiye davranışı birebir aynı
  for (const s of TR) { const a = O.pencereler[s], b = S.pencereler[s];
    ok(a.n === b.n && a.ozet === b.ozet && a.durum === b.durum && a.ipucu === b.ipucu && a.Mc === b.Mc && a.b === b.b && a.n > 0,
      `TR pencere ${s}: önce/sonra aynı (N = ${b.n}, özet ${h(b.ozet)}, Mc ${b.Mc}, b ${b.b})`); }
  ok(O.iscgem_tr.n === S.iscgem_tr.n && O.iscgem_tr.ozet === S.iscgem_tr.ozet && O.iscgem_tr.ipucu === S.iscgem_tr.ipucu && O.iscgem_tr.b === S.iscgem_tr.b && /ISC-GEM v12\.1 katmanı AÇIK/.test(S.iscgem_tr.ipucu),
    `TR ISC-GEM katmanı (ISC 1900–1970): önce/sonra aynı (N = ${S.iscgem_tr.n}, özet ${h(S.iscgem_tr.ozet)}, b ${S.iscgem_tr.b})`);
  ok(O.cok.n === S.cok.n && O.cok.ozet === S.cok.ozet && O.cok.durum === S.cok.durum, `TR çoklu seçim (ISC 1900–1970 + 1971–1997): önce/sonra aynı (N = ${S.cok.n})`);
  // (2)–(4) yeni seçenek
  const p = kosu.sonra.p, gsec = '.tbtn[data-hist-src="ISCGEM-GLOBAL"]';
  const gor = () => p.evaluate(() => { const r = document.getElementById('histIscgemGlobalRow'); return r ? getComputedStyle(r).display : 'yok'; });
  ok(await gor() === 'none', 'Türkiye modunda küresel satır gizli');
  ok(!istekler.includes('/data/iscgem_global.json'), 'Sayfa açılışında ve Türkiye testlerinde data/iscgem_global.json indirilmedi');
  await p.evaluate(() => setScope('global'));
  ok(await gor() !== 'none', 'Global modda küresel satır görünür');
  ok(await p.evaluate(s => !document.querySelector(s).classList.contains('active') && !activeHistWindows.length && !historicalMode, gsec), 'Varsayılan kapalı (düğme etkin değil, tarihsel mod kapalı)');
  ok(await kosu.once.p.evaluate(() => !document.getElementById('histIscgemGlobalRow')), 'Önceki sürümde küresel satır yok (karşılaştırma tabanı)');
  const g = await pencere(p, gsec);
  const ayr = await p.evaluate(() => ({ d: events.filter(e => e.msrc === 'iscgem_direct' && e.mw_m0).length, v: events.filter(e => e.msrc === 'iscgem_proxy').length,
    mt: [...new Set(events.map(e => e.mtype))], src: [...new Set(events.map(e => e.src))], ilk: events.reduce((a, e) => e.time < a ? e.time : a, events[0].time).toISOString(),
    yer: { bos: events.filter(e => !e.place).length, turkiye: events.filter(e => /Türkiye/.test(e.place)).length, ornek: events.find(e => e.id === 'iscgem:879136')?.place || null,
      kart: (() => { const t = document.getElementById('lcPlace'); return t ? t.textContent : null; })() },
    son: events.reduce((a, e) => e.time > a ? e.time : a, events[0].time).toISOString(), mmin: Math.min(...events.map(e => e.mag)) }));
  ok(g.n === 74159 && g.aktif && g.tarihsel, `Küresel pencere: ${g.n} olay (beklenen 74 159), düğme etkin, tarihsel mod açık`);
  ok(ayr.d === 51227 && ayr.v === 22931 && g.n - ayr.d - ayr.v === 1, `Doğrudan/vekil/belirsiz: ${ayr.d}/${ayr.v}/${g.n - ayr.d - ayr.v} (beklenen 51 227/22 931/1)`);
  ok(ayr.mt.join() === 'mw' && ayr.src.join() === 'ISC-GEM', `Büyüklük türü yalnız 'mw' (dönüşüm uygulanmaz), kaynak 'ISC-GEM'`);
  ok(ayr.ilk.startsWith('1904-04-04') && ayr.son.startsWith('2021-12-31'), `Kapsam ${ayr.ilk.slice(0, 10)} – ${ayr.son.slice(0, 10)}`);
  ok(/doğrudan 51227 \(%69\), vekil 22931 \(%31\), yöntemi belirsiz 1/.test(g.ipucu) && /büyük depremler kataloğu/.test(g.ipucu) && /tam bir katalog değildir/.test(g.ipucu) && /CC BY-SA 3\.0/.test(g.ipucu) && /D808B825/.test(g.ipucu),
    'İpucu: doğrudan/vekil oranı, kapsam uyarısı (tam katalog değil), lisans ve atıf');
  ok(ayr.yer.bos === 0 && ayr.yer.turkiye === 0 && ayr.yer.kart !== 'Türkiye', `Yer etiketi: boş 0, 'Türkiye' 0; en büyük deprem kartı "${ayr.yer.kart}"; örnek 1960 Şili: "${ayr.yer.ornek}"`);
  ok(/ISC-GEM/.test(g.durum) && /1904–2021/.test(g.durum), `Durum satırı: "${g.durum}"`);
  sonuc.kuresel = { n: g.n, Mc: g.Mc, b: g.b, ipucu: g.ipucu, durum: g.durum, ...ayr };
  await p.evaluate(() => setScope('tr')); await p.waitForTimeout(300);
  ok(await p.evaluate(s => !document.querySelector(s).classList.contains('active') && !activeHistWindows.length && !historicalMode && events.length === 0, gsec), 'Türkiye moduna dönünce küresel pencere kapandı, olaylar temizlendi');
  ok(!kosu.once.r.hatalar.length && !kosu.sonra.r.hatalar.length && !(await p.evaluate(() => 0)), `Sayfa hatası yok (önce ${kosu.once.r.hatalar.length}, sonra ${kosu.sonra.r.hatalar.length})` + (kosu.sonra.r.hatalar.length ? ': ' + kosu.sonra.r.hatalar.join(' | ') : ''));
  sonuc.tr = Object.fromEntries(TR.map(s => [s, { n: S.pencereler[s].n, ozet_sha16: h(S.pencereler[s].ozet), Mc: S.pencereler[s].Mc, b: S.pencereler[s].b }]));
  sonuc.tr_iscgem = { n: S.iscgem_tr.n, ozet_sha16: h(S.iscgem_tr.ozet), b: S.iscgem_tr.b }; sonuc.ozet = { pass, fail };
  fs.writeFileSync(path.join(__dirname, 'kabul_sonuc.json'), JSON.stringify(sonuc, null, 1));
  console.log(`\n${fail ? 'KALDI' : 'GEÇTİ'}: ${pass} geçti, ${fail} kaldı`);
  await br.close(); srv.close(); process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
