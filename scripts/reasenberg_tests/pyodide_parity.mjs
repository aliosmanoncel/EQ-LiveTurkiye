// pyodide_parity.mjs — Pyodide'de çalışan DONDURULMUŞ Reasenberg ile yerel Python'un birebir eşleşme testi.
//
// Ölçütler (hepsi BİREBİR; tolerans yok):
//  P1  4 dondurulmuş regresyon referansı (scripts/fixtures/reasenberg_zmap_*_ref.json):
//      olay sırası, küme kimliği ve sınıf, referansla aynı.
//  P2  Tam EMSC kataloğu (src == EMSC): Pyodide üyeliği, aynı anda yerel CPython ile
//      üretilen üyelikle aynı; toplamlar data/reasenberg_gk74_emsc.json ile aynı.
//  P3  reasenberg.py sha256 = dondurulmuş değer (aksi halde hesap hiç başlamaz).
// Ayrıca süre ölçülür (başlatma; N = 500, 2000, 5000, 20000, tümü).
//
// Kullanım (depo kökünden):
//   PYODIDE_DIR=/yol/pyodide node scripts/reasenberg_tests/pyodide_parity.mjs [--out sonuc.json]
// PYODIDE_DIR: Pyodide 0.27.7 dağıtımı (pyodide.mjs, pyodide.asm.wasm, python_stdlib.zip,
// pyodide-lock.json ve numpy-2.0.2 tekerleği).

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import path from 'node:path';
import { initReasenberg, runReasenberg, PY_FILES } from '../../lab/reasenberg-pyodide/rb_core.mjs';

const dir = process.env.PYODIDE_DIR;
if (!dir) { console.error('PYODIDE_DIR tanımlı değil'); process.exit(2); }
const outArg = process.argv.indexOf('--out');
const outPath = outArg > 0 ? process.argv[outArg + 1] : null;

const t0 = performance.now();
const { loadPyodide } = await import(path.resolve(dir, 'pyodide.mjs'));
const py = await loadPyodide({ indexURL: path.resolve(dir) + '/' });
await py.loadPackage('numpy');
const tLoad = performance.now() - t0;
const sources = Object.fromEntries(PY_FILES.map(f => [f, new Uint8Array(readFileSync(`scripts/${f}`))]));
const meta = await initReasenberg(py, sources);
const tInit = performance.now() - t0;
console.log(`[*] Pyodide ${py.version} | Python ${meta.python} | numpy ${meta.numpy} | modül ${meta.module_version} | yükleme ${(tLoad / 1000).toFixed(2)} s, hazır ${(tInit / 1000).toFixed(2)} s`);

const fails = [];
const result = { pyodide: py.version, python: meta.python, numpy: meta.numpy, module_version: meta.module_version,
  module_sha256: meta.sha256, adapter_version: meta.adapter_version, load_s: +(tLoad / 1000).toFixed(3),
  ready_s: +(tInit / 1000).toFixed(3), fixtures: [], full_catalog: null, timing: [] };

// --- P1: dondurulmuş regresyon referansları
for (const f of readdirSync('scripts/fixtures').filter(f => /^reasenberg_zmap_.*_ref\.json$/.test(f)).sort()) {
  const ref = JSON.parse(readFileSync(`scripts/fixtures/${f}`, 'utf8'));
  const cat = JSON.parse(readFileSync(ref.catalog, 'utf8')).events;
  const r = runReasenberg(py, cat, ref.params.xmeff, { rule: ref.params.rule, magField: ref.params.mag_field });
  const got = r.ids.map((id, i) => [id, r.cluster_id[i], r.event_class[i]]);
  const same = JSON.stringify(got) === JSON.stringify(ref.membership);
  const indep = r.ids.filter((_, i) => r.event_class[i] !== 'dependent').sort();
  const sameIndep = JSON.stringify(indep) === JSON.stringify(ref.independent_ids);
  result.fixtures.push({ fixture: f, n: got.length, membership_identical: same, independent_identical: sameIndep });
  console.log(`[${same && sameIndep ? 'OK' : 'FARK'}] P1 ${f}: n ${got.length}, bağımsız ${indep.length}`);
  if (!(same && sameIndep)) fails.push(`P1 ${f}`);
}

// --- P2: tam EMSC kataloğu, Pyodide vs yerel CPython (aynı dosyalar)
const all = JSON.parse(readFileSync('data/eq_historical.json', 'utf8')).events.filter(e => e.src === 'EMSC');
const native = JSON.parse(execFileSync('python3', ['-c', `
import sys, json; sys.path.insert(0, 'scripts'); import decluster_reasenberg as D
ev = [e for e in json.load(open('data/eq_historical.json', encoding='utf-8'))['events'] if e.get('src') == 'EMSC']
evs, o = D.decluster(ev, 3.0, 'zmap', 'mag')
print(json.dumps([[e.get('id'), c, k] for e, c, k in zip(evs, o['cluster_id'], o['event_class'])]))
`], { maxBuffer: 1 << 30 }).toString());
let t = performance.now();
const full = runReasenberg(py, all, 3.0);
const tFull = performance.now() - t;
const gotFull = full.ids.map((id, i) => [id, full.cluster_id[i], full.event_class[i]]);
const sameFull = JSON.stringify(gotFull) === JSON.stringify(native);
const cnt = k => full.event_class.filter(c => c === k).length;
const prod = JSON.parse(readFileSync('data/reasenberg_gk74_emsc.json', 'utf8')).totals.reasenberg;
const totals = { n: gotFull.length, single: cnt('single'), representative: cnt('representative'),
  dependent: cnt('dependent'), clusters: full.n_clusters };
const sameProd = totals.single === prod.single && totals.representative === prod.representative
  && totals.dependent === prod.dependent && totals.clusters === prod.clusters;
result.full_catalog = { n: gotFull.length, membership_identical_to_cpython: sameFull,
  totals, totals_identical_to_site_product: sameProd, seconds: +(tFull / 1000).toFixed(3) };
console.log(`[${sameFull ? 'OK' : 'FARK'}] P2 tam EMSC (${gotFull.length} olay): CPython ile üyelik birebir`);
console.log(`[${sameProd ? 'OK' : 'FARK'}] P2 toplamlar site ürünüyle aynı: ${JSON.stringify(totals)}`);
if (!sameFull) fails.push('P2 üyelik');
if (!sameProd) fails.push('P2 toplamlar');

// --- süre (son N olay; tarayıcıdaki bölge sorgularına benzer boyutlar)
for (const n of [500, 2000, 5000, 20000, all.length]) {
  const sub = all.slice(-n);
  t = performance.now();
  runReasenberg(py, sub, 3.0);
  const s = (performance.now() - t) / 1000;
  result.timing.push({ n: sub.length, seconds: +s.toFixed(3) });
  console.log(`[*] süre N=${sub.length}: ${s.toFixed(2)} s`);
}

result.pass = fails.length === 0;
result.failures = fails;
if (outPath) writeFileSync(outPath, JSON.stringify(result, null, 1) + '\n');
console.log(result.pass ? '[OK] Tüm eşleşme ölçütleri sağlandı.' : `[FARK] ${fails.join(', ')}`);
process.exit(result.pass ? 0 : 1);
