// Denetim testi: ISC-GEM v12.1 Mw katmanı (DENEYSEL, varsayılan kapalı) ve aday tamlık merdiveni (2026-10-21).
// Fonksiyonlar index.html'den doğrudan okunur (kopya yok); index.html ve veri dosyaları DEĞİŞTİRİLMEZ.
// Referans: scripts/fixtures/iscgem_overlay_ref.json (homog-faz0 sabitlenmiş prototipinden üretildi).
// Kullanım (depo kökünde): node scripts/test_iscgem_overlay.js [--no-gk74]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto'), cp = require('child_process'), os = require('os');
const ROOT = path.join(__dirname, '..');
const src = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
const J = p => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const REF = J('scripts/fixtures/iscgem_overlay_ref.json');
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else fail++; console.log((c ? '  ok  ' : '  !!  ') + msg); };

const ctx = { document: { getElementById: () => ({ value: '', checked: false }) }, console }; vm.createContext(ctx);
vm.runInContext(cut('function gk74BuildMwOverride(', 'const GK74_CTX = '), ctx);
vm.runInContext(cut('function iscgemWanted()', 'async function loadIscgem()'), ctx);
vm.runInContext(src.match(/^const CS_PRESETS = [^\n]*$/m)[0].replace('const CS_PRESETS', 'var CS_PRESETS'), ctx);
// Weichert zinciri (test_weichert_chain.js ile aynı yöntem)
vm.runInContext(src.match(/^const CS_QC = \{[^\n]*\};$/m)[0].replace('const CS_QC', 'var CS_QC'), ctx);
vm.runInContext('var MAG_CONVERSIONS = {};\n' + cut('const MC_DM = 0.1;', '// Aki (1965) MLE b-değeri').replace('const MC_DM', 'var MC_DM'), ctx);
vm.runInContext('var regionRect=null, regionWindowStart=null, regionWindowEnd=null, regionCapped=false, regionOrderUsed=null;', ctx);
vm.runInContext(cut('let csEnabled = false;', 'let lastGrFit = null;').replace('let csEnabled', 'var csEnabled').replace('let csSteps', 'var csSteps'), ctx);
vm.runInContext(`function __classify(items, cs, DM) {\n${cut('  const idx = m => Math.floor((m + 1e-9) / DM);', '  const wf = weichertFit(clsBest);')}\n return { clsBest }; }`, ctx);
const run = c => vm.runInContext(c, ctx);

const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, p))).digest('hex');
const cat = J('data/eq_historical.json'), OV = J('data/mw_iscgem.json'), EK = J('data/iscgem_ek_1904_1962.json'), AUTH = J('data/mw_authority.json');
const authEntries = AUTH.entries.filter(x => x.status === 'verified').map(x => ({ ...x, _t: Date.parse(x.time_utc) }));
const utc = t => Date.parse(/Z$|[+-]\d\d:\d\d$/.test(t) ? t : t + 'Z');
const apply = auth => { ctx.__a = [cat, OV.aktarim, EK.events, auth]; return run('iscgemApply(...__a)'); };

console.log('\n1. Kapalı seçenek: mevcut davranış birebir korunur');
ok(sha('data/eq_historical.json') === REF.korunan_sha256['data/eq_historical.json'], 'eq_historical.json SHA-256 değişmemiş');
ok(sha('data/mw_authority.json') === REF.korunan_sha256['data/mw_authority.json'], 'mw_authority.json SHA-256 değişmemiş');
ok(run('iscgemWanted()') === false, 'işaret kutusu yokken / işaretsizken katman kapalı');
ok(/<input type="checkbox" id="histIscgem" onchange="onHistIscgemChange\(\)">/.test(src), 'HTML: #histIscgem varsayılan işaretsiz (checked yok)');
ok(src.includes('const cat = iscgemWanted() ? await iscgemCatalog(historicalCache) : historicalCache;'), 'rebuildHistoricalView: kapalıyken aynı nesne (historicalCache) kullanılır');
ok(!/\b(iscgemApply|iscgemCatalog|loadIscgem)\(/.test(src.replace(/function (iscgemApply|iscgemCatalog|loadIscgem)\(/g, '').replace(/iscgemWanted\(\) \? await iscgemCatalog\(historicalCache\)/, '').replace(/const d = await loadIscgem\(\)/, '').replace(/const cat = iscgemApply\(base/, '')),
   'katman fonksiyonları başka hiçbir yerden çağrılmıyor');
{ const before = JSON.stringify(cat.events.slice(0, 2000)); apply(authEntries); ok(JSON.stringify(cat.events.slice(0, 2000)) === before, 'iscgemApply girdiyi değiştirmez (yan etkisiz)'); }

console.log('\n2. Açık seçenek: sabitlenmiş prototipi yeniden üretir (mw_authority önceliği dışarıda)');
const O = apply(null);
const lines = O.events.map(e => [e, e.mw ?? e.mag]).filter(([, m]) => m !== null && m !== undefined)
  .map(([e, m]) => `${utc(e.time)}|${(+e.lat).toFixed(4)}|${(+e.lon).toFixed(4)}|${(+m).toFixed(3)}`).sort();
ok(O.iscgem.nTransfer === 1144 && O.iscgem.nPosition === 133 && O.iscgem.nAdded === 273, `sayılar: ${O.iscgem.nTransfer} aktarım, ${O.iscgem.nPosition} konum, ${O.iscgem.nAdded} ek`);
ok(lines.length === REF.n, `olay sayısı ${lines.length} = ${REF.n}`);
ok(crypto.createHash('sha256').update(lines.join('\n')).digest('hex') === REF.ozet_sha256, 'katalog özeti (zaman|konum|M) prototiple birebir aynı');
{ // Weichert (üretim zinciri), aday merdiven, 1900–2021, ham
  ctx.csSteps = REF.L1.map(([y, mc]) => ({ start: `${y}-01-01`, mc: String(mc) })); ctx.csEnabled = true;
  ctx.regionRect = {}; ctx.regionWindowStart = new Date('1900-01-01T00:00:00Z'); ctx.regionWindowEnd = new Date('2021-12-31T23:59:59Z');
  // etki_weichert.js ile aynı girdi: yalnız M ve zaman (ISC zamanları UTC sayılır)
  ctx.__ev = O.events.filter(e => (e.mw ?? e.mag) != null && e.time.slice(0, 4) >= '1900' && e.time.slice(0, 4) <= '2021')
    .map(e => ({ time: new Date(utc(e.time)), mag: +(+(e.mw ?? e.mag)).toFixed(3) }));
  const cs = run('csBuild(__ev)'); ctx.__cs = cs; const { clsBest } = run('__classify(__cs.kept, __cs, 0.1)');
  for (const [fn, lo] of [['tum_siniflar', null], ['M_ge_4_5', 4.5], ['M_ge_5_0', 5.0]]) {
    ctx.__C = lo === null ? clsBest : clsBest.filter(c => c.m - 0.05 >= lo - 1e-9); const wf = run('weichertFit(__C)'), R = REF.weichert_C1_ham_L1[fn];
    ok(wf.N === R.N && Math.abs(wf.b - R.b) < 5e-5, `Weichert ${fn}: N = ${wf.N}, b = ${wf.b.toFixed(4)} (referans ${R.N}, ${R.b})`);
  }
}

console.log('\n3. Kaynak önceliği: mw_authority → ISC-GEM → katalog');
const OA = apply(authEntries);
const idx = new Map(OA.events.map(e => [e.id, e]));
ok(OA.iscgem.authHits.every(h => idx.get(h.id).mw === h.auth_mw && idx.get(h.id).msrc === 'mw_authority'), `${OA.iscgem.nAuth} çakışmada mw_authority Mw kullanıldı: ${OA.iscgem.authHits.map(h => `${h.name} ${h.iscgem_mw}→${h.auth_mw}`).join('; ') || '—'}`);
{ const tr = new Set(OV.aktarim.map(r => r.A_id)); let same = 0, n = 0;
  cat.events.forEach((e, i) => { if (!tr.has(e.id)) { n++; if (OA.events[i] === e) same++; } });
  ok(same === n, `ISC-GEM karşılığı olmayan ${n} olay aynı nesne (değişmedi)`); }
{ // sentetik: aktarılan + otorite eşleşen → otorite; aktarılmayan + otorite eşleşen → değişmez
  const c = { events: [{ id: 'a', time: '2000-01-01T00:00:00Z', lat: 40, lon: 30, mag: 5.0, mtype: 'mb', mw: null },
                       { id: 'b', time: '2001-01-01T00:00:00Z', lat: 40, lon: 30, mag: 5.0, mtype: 'mb', mw: null }] };
  const ents = [{ name: 'X', mw: 7.1, lat: 40.1, lon: 30, _t: Date.parse('2000-01-01T00:00:30Z') }, { name: 'Y', mw: 6.9, lat: 40, lon: 30, _t: Date.parse('2001-01-01T00:00:10Z') }];
  ctx.__a = [c, [{ A_id: 'a', Mw: 6.5, mw_src: 'iscgem_direct', gem_id: 'g', konum: null }], [], ents]; const r = run('iscgemApply(...__a)');
  ok(r.events[0].mw === 7.1 && r.events[0].msrc === 'mw_authority', 'sentetik: aktarılan olayda otorite önce gelir (6,5 → 7,1)');
  ok(r.events[1] === c.events[1] && r.events[1].mag === 5.0, 'sentetik: ISC-GEM karşılığı olmayan olaya otorite büyüklüğü yazılmaz');
  ctx.__a = [c, [{ A_id: 'a', Mw: 6.5, mw_src: 'iscgem_direct', gem_id: 'g', konum: null }], [], null]; const r2 = run('iscgemApply(...__a)');
  ok(r2.events[0].mw === 6.5 && r2.events[0].mtype === 'mw' && r2.events[0].mag_orig === 5.0 && r2.events[0].mtype_orig === 'mb', 'sentetik: otorite yokken ISC-GEM Mw; özgün büyüklük ve tür saklanır'); }

console.log('\n4. Aday merdiven: yalnız doğrulanmış üç basamak (karar 2026-10-21)');
{ const P = ctx.CS_PRESETS.iscgem2026.map(([s, m]) => [s, +m]);
  ok(JSON.stringify(P) === JSON.stringify([['1904-01-01', 6.0], ['1970-01-01', 5.5], ['1979-01-01', 5.0]]), 'hazır basamaklar: 1904 6,0 · 1970 5,5 · 1979 5,0');
  ok(P.every(([, m]) => m >= 5.0), 'M < 5,0 için hazır basamak yok');
  ok(P.every((x, i) => i === 0 || (x[0] > P[i - 1][0] && x[1] <= P[i - 1][1])), 'tekdüze: başlangıçlar artan, Mc artmayan');
  const start = M => { const s = P.find(([, mc]) => mc <= M + 1e-9); return s ? +s[0].slice(0, 4) : null; };
  for (const [M, y] of [[6.0, 1904], [5.5, 1970], [5.0, 1979], [4.9, null]]) ok(start(M) === y, `M ${M.toFixed(1)} sınıfı: ${start(M) ?? 'hazır basamakta tam sayılmaz'} (karar: ${y ?? 'yok'})`);
  const btn = src.slice(src.indexOf("csApplyPreset('iscgem2026')\" style"), src.indexOf('>Aday merdiven</button>'));
  ok(/BAĞIMSIZ OLARAK DOĞRULANMADI/.test(btn) && /4,5–5,0 → 1995/.test(btn) && /4,0–4,5 → 1995/.test(btn) && /3,5–4,0 → 1993/.test(btn) && /3,0–3,5 → 2002/.test(btn), 'düğme açıklaması: M < 5 Stepp sonuçları ve bağımsız doğrulama eksikliği');
  // tarayıcı yolu: hazır basamaklarla csBuild, 1979 sonrası M < 5 olayları dışarıda
  ctx.csSteps = ctx.CS_PRESETS.iscgem2026.map(([start, mc]) => ({ start, mc })); ctx.csEnabled = true;
  ctx.__ev = [{ time: new Date('1990-01-01T00:00:00Z'), mag: 4.9 }, { time: new Date('1990-01-01T00:00:00Z'), mag: 5.0 }, { time: new Date('1975-01-01T00:00:00Z'), mag: 5.4 }, { time: new Date('1903-06-01T00:00:00Z'), mag: 7.0 }];
  ctx.regionRect = {}; ctx.regionWindowStart = new Date('1900-01-01T00:00:00Z'); ctx.regionWindowEnd = new Date('2021-12-31T23:59:59Z');
  const k = run('csBuild(__ev)').kept.map(x => x.m); ok(JSON.stringify(k) === JSON.stringify([5.0]), `csBuild: yalnız 1990 M 5,0 tutulur (4,9 / 1975 M 5,4 / 1903 öncesi dışarıda) → [${k}]`); }

console.log('\n5. 1910-02-18 (id 914191)');
{ const e = OA.events.find(e => e.id === '914191'); ok(e && e.mag === 7.0 && !e.msrc, 'M 7,0 korunur, aktarım yok');
  ok(!OA.events.some(e => e.id === 'iscgem:16958073'), 'ISC-GEM 16958073 ek olay olarak eklenmez');
  ok(OV.alternatif.some(a => a.id === '914191' && a.alt_mw === 5.85), 'Mw 5,85 yalnız alternatif kaydında'); }

console.log('\n6. Lisans ve atıf');
for (const [n, d] of [['mw_iscgem.json', OV], ['iscgem_ek_1904_1962.json', EK]])
  ok(/CC BY-SA 3\.0/.test(d.meta.lisans) && /10\.31905\/d808b825/i.test(d.meta.atif) && /International Seismological Centre and GEM Foundation/.test(d.meta.telif), `${n}: lisans, DOI'li atıf, telif`);
{ const L = fs.readFileSync(path.join(ROOT, 'data/LISANS_ISC-GEM.txt'), 'utf8');
  ok(/mw_iscgem\.json/.test(L) && /iscgem_ek_1904_1962\.json/.test(L) && /CC BY-SA 3\.0/.test(L) && /değişiklikler/i.test(L), 'LISANS_ISC-GEM.txt: iki dosya, lisans, değişiklik bildirimi');
  ok(EK.events.every(e => e.src === 'ISC-GEM'), 'ek olayların kaynağı ISC-GEM olarak etiketli');
  { const u = src.slice(src.indexOf('id="histIscgemRow"'), src.indexOf('id="histIscgemRow"') + 900); ok(/CC BY-SA 3\.0/.test(u) && /GEM Vakfı/.test(u) && /d808b825/.test(u), 'arayüz açıklamasında lisans, telif sahipleri ve DOI'); } }

if (!process.argv.includes('--no-gk74')) {
  console.log('\n7. GK74 eşdeğerliği katman açıkken (Python == tarayıcı JS)');
  const td = fs.mkdtempSync(path.join(os.tmpdir(), 'iscgem-')), cf = path.join(td, 'cat.json');
  fs.writeFileSync(cf, JSON.stringify({ events: OA.events }));
  for (const mf of ['mag', 'mw']) {
    const r = cp.spawnSync('python3', ['scripts/validate_gk74_parity.py', '--catalog', cf, '--mag-field', mf], { cwd: ROOT, encoding: 'utf8' });
    const out = (r.stdout || '') + (r.stderr || ''); ok(/SONUC: BIREBIR AYNI/.test(out), `--mag-field ${mf}: ${out.trim().split('\n').slice(-3).join(' | ')}`);
  }
}
console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
