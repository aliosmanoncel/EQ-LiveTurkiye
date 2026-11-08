// rb_worker.mjs — Dinamik Reasenberg'i ana iş parçacığından ayıran Web Worker (modül worker).
//
// Yeni algoritma yok: rb_core.mjs (dondurulmuş reasenberg.py, sha256 denetimli) aynen kullanılır.
// Amaç yalnız arayüzün donmamasıdır (Node ölçümü: 20 000 olay ≈ 1,3 s; tamponla girdi ~40 000'e çıkabilir).
// Mesajlar: { id, type: 'init' } → { id, ok, meta, selfTest }
//           { id, type: 'run', events, xmeff } → { id, ok, res, ms }

import { initReasenberg, runReasenberg, runSelfTest, PY_FILES } from './rb_core.mjs';

const BASE = new URL('../../', import.meta.url).href;
const PYODIDE = new URL('vendor/pyodide/0.27.7/', BASE).href;
let state = null;   // { py, meta, selfTest } — oturumda bir kez

async function getJson(p) { const r = await fetch(new URL(p, BASE)); if (!r.ok) throw new Error(`${p}: ${r.status}`); return r.json(); }
async function getBytes(p) { const r = await fetch(new URL(p, BASE)); if (!r.ok) throw new Error(`${p}: ${r.status}`); return new Uint8Array(await r.arrayBuffer()); }

let pending = null;
function ensure() {
  if (state) return Promise.resolve(state);
  if (pending) return pending;
  pending = (async () => {
    const { loadPyodide } = await import(PYODIDE + 'pyodide.mjs');
    const py = await loadPyodide({ indexURL: PYODIDE });
    await py.loadPackage('numpy');
    const src = {}; for (const f of PY_FILES) src[f] = await getBytes('scripts/' + f);
    const meta = await initReasenberg(py, src);          // sha256 tutmazsa hata
    const selfTest = await runSelfTest(py, getJson);       // K0
    state = { py, meta, selfTest };
    return state;
  })();
  pending.catch(() => { pending = null; });
  return pending;
}

self.onmessage = async ({ data }) => {
  const { id, type } = data;
  try {
    const s = await ensure();
    if (type === 'init') { self.postMessage({ id, ok: true, meta: s.meta, selfTest: s.selfTest }); return; }
    if (type === 'run') {
      const t0 = performance.now();
      const res = runReasenberg(s.py, data.events, data.xmeff);
      self.postMessage({ id, ok: true, res, ms: performance.now() - t0 });
      return;
    }
    throw new Error('bilinmeyen istek: ' + type);
  } catch (e) {
    self.postMessage({ id, ok: false, error: e && e.message ? e.message : String(e) });
  }
};
