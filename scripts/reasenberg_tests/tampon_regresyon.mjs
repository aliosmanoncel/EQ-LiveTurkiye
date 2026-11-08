// tampon_regresyon.mjs — Dinamik Reasenberg 90 günlük geri tampon regresyon testi (Kahramanmaraş senaryosu).
//
// Senaryo, 2026-11-08 canlı testiyle aynı bölge ve pencere; veri DONDURULMUŞ fikstürden gelir
// (canlı EMSC verisi zamanla revize edilebildiği için canlı sayılar test edilmez; bkz.
// analysis/2026-11-08_pyodide_reasenberg/CANLI_TEST.md):
//   daire 37,5 K 37,2 D, 100 km · pencere 2023-03-01 – 2023-12-31 (İstanbul yerel gece yarısı = 2023-02-28T21:00Z)
//   tampon: pencere başından önceki 90 gün · kaynak: data/eq_historical.json, src = EMSC (M ≥ 3,0) · xmeff 3,0
// Ölçütler (hepsi BİREBİR):
//   T1 tamponlu hesapta raporlanan olaylar = pencere olayları (tampon olayı raporda yok, windowOnly)
//   T2 tamponlu ve tamponsuz sonuçlar (bağımlı sayısı, küme sayısı, sınıf değişen, ilk 30 günde değişen) = fikstürdeki beklenen
//   T3 tampon bağımlı sayısını azaltmaz (sınır etkisinin bilinen yönü)
// Kullanım (depo kökünden):
//   PYODIDE_DIR=vendor/pyodide/0.27.7 node scripts/reasenberg_tests/tampon_regresyon.mjs           # sına
//   PYODIDE_DIR=vendor/pyodide/0.27.7 node scripts/reasenberg_tests/tampon_regresyon.mjs --build   # fikstürü üret

import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { initReasenberg, runReasenberg, windowOnly, PY_FILES } from '../../lab/reasenberg-pyodide/rb_core.mjs';

const FIX = 'scripts/fixtures/reasenberg_tampon_kahramanmaras.json';
const SC = { lat: 37.5, lon: 37.2, rKm: 100, windowStart: '2023-02-28T21:00:00Z', windowEnd: '2023-12-31T20:59:59Z', bufferDays: 90, xmeff: 3.0 };
const dir = process.env.PYODIDE_DIR;
if (!dir) { console.error('PYODIDE_DIR tanımlı değil'); process.exit(2); }
const build = process.argv.includes('--build');

const km = (a, b, c, d) => { const R = 6371, r = Math.PI / 180, x = Math.sin((c - a) * r / 2) ** 2 + Math.cos(a * r) * Math.cos(c * r) * Math.sin((d - b) * r / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(x)); };

let fx;
if (build) {
  const ws = Date.parse(SC.windowStart), we = Date.parse(SC.windowEnd), bs = ws - SC.bufferDays * 864e5;
  const all = JSON.parse(readFileSync('data/eq_historical.json', 'utf8')).events.filter(e => e.src === 'EMSC' && km(SC.lat, SC.lon, e.lat, e.lon) <= SC.rKm);
  const pick = e => ({ time: e.time, lat: e.lat, lon: e.lon, dep: e.dep, mag: e.mag, mtype: e.mtype });
  const win = all.filter(e => { const t = Date.parse(e.time); return t >= ws && t <= we; }).map((e, i) => ({ id: `r${i}`, ...pick(e) }));
  const buf = all.filter(e => { const t = Date.parse(e.time); return t >= bs && t < ws; }).map((e, i) => ({ id: `b${i}`, ...pick(e) }));
  fx = { senaryo: SC, kaynak: 'data/eq_historical.json (src = EMSC), fikstür üretimi 2026-11-08', pencere: win, tampon: buf, beklenen: null };
} else {
  fx = JSON.parse(readFileSync(FIX, 'utf8'));
}

const { loadPyodide } = await import(path.resolve(dir, 'pyodide.mjs'));
const py = await loadPyodide({ indexURL: path.resolve(dir) + '/' });
await py.loadPackage('numpy');
await initReasenberg(py, Object.fromEntries(PY_FILES.map(f => [f, new Uint8Array(readFileSync(`scripts/${f}`))])));

const xm = fx.senaryo.xmeff, ws = Date.parse(fx.senaryo.windowStart);
const withBuf = windowOnly(runReasenberg(py, fx.tampon.concat(fx.pencere), xm));
const noBuf = windowOnly(runReasenberg(py, fx.pencere, xm));
const dep = r => r.event_class.filter(c => c === 'dependent').length;
const cls = new Map(noBuf.ids.map((id, k) => [id, noBuf.event_class[k] === 'dependent']));
const byId = new Map(fx.pencere.map(e => [e.id, e]));
let changed = 0, first30 = 0, first30chg = 0;
withBuf.ids.forEach((id, k) => {
  const d30 = (Date.parse(byId.get(id).time) - ws) / 864e5 < 30, chg = (withBuf.event_class[k] === 'dependent') !== cls.get(id);
  if (d30) first30++; if (chg) { changed++; if (d30) first30chg++; }
});
const got = { n_pencere: fx.pencere.length, n_tampon: fx.tampon.length, n_girdi: withBuf.n_input,
  tamponlu: { bagimli: dep(withBuf), kume: withBuf.n_clusters }, tamponsuz: { bagimli: dep(noBuf), kume: noBuf.n_clusters },
  sinif_degisen: changed, ilk30_olay: first30, ilk30_degisen: first30chg };

if (build) {
  fx.beklenen = got;
  writeFileSync(FIX, JSON.stringify(fx));
  console.log('[build] fikstür yazıldı:', FIX, JSON.stringify(got));
  process.exit(0);
}

const fails = [];
const ok = (c, m) => { console.log(`[${c ? 'OK' : 'HATA'}] ${m}`); if (!c) fails.push(m); };
ok(withBuf.ids.length === fx.pencere.length && withBuf.ids.every(id => id.startsWith('r')) && withBuf.n_input === fx.pencere.length + fx.tampon.length,
   `T1 raporda yalnız pencere olayları: ${withBuf.ids.length}/${fx.pencere.length} (girdi ${withBuf.n_input})`);
ok(JSON.stringify(got) === JSON.stringify(fx.beklenen), `T2 beklenen sonuç: ${JSON.stringify(got)}`);
ok(got.tamponlu.bagimli >= got.tamponsuz.bagimli, `T3 tampon bağımlı sayısını azaltmıyor: ${got.tamponsuz.bagimli} → ${got.tamponlu.bagimli}`);
if (fails.length) { console.error(`${fails.length} ölçüt sağlanmadı`); process.exit(1); }
console.log('[OK] Tampon regresyon ölçütleri sağlandı.');
