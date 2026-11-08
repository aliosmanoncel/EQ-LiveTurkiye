// rb_core.mjs — Pyodide üzerinde DONDURULMUŞ Reasenberg modülünü çalıştırma katmanı (DENEME).
//
// İlke: Pyodide yalnız çalıştırma ortamıdır. Algoritma kodu yazılmaz/çevrilmez;
// depodaki üç Python dosyası (reasenberg.py v0.3.0, decluster_gk74.py,
// decluster_reasenberg.py) BAYT BAYT aynı biçimde Pyodide dosya sistemine yazılır
// ve sunucudaki Python ile aynı fonksiyon (decluster_reasenberg.decluster) çağrılır.
// reasenberg.py'nin sha256'sı dondurulmuş değerle eşleşmezse hiçbir hesap yapılmaz.
//
// Tarayıcıda ve Node'da (CI eşleşme testi) aynı dosya kullanılır.

export const FROZEN_SHA256 = 'c5b1248af557f29b4f04bf7c6ed9adfefd97c4153975a8989804b872ccf99bc9';
export const PY_FILES = ['reasenberg.py', 'decluster_gk74.py', 'decluster_reasenberg.py'];
const PY_DIR = '/home/pyodide/rb';

export async function sha256Hex(bytes) {
  const h = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}

// sources: { 'reasenberg.py': Uint8Array, 'decluster_gk74.py': Uint8Array, 'decluster_reasenberg.py': Uint8Array }
export async function initReasenberg(pyodide, sources) {
  const sha = await sha256Hex(sources['reasenberg.py']);
  if (sha !== FROZEN_SHA256) {
    throw new Error(`reasenberg.py dondurulmuş v0.3.0 değil (sha256 ${sha.slice(0, 12)}…). Hesap yapılmadı.`);
  }
  pyodide.FS.mkdirTree(PY_DIR);
  for (const f of PY_FILES) pyodide.FS.writeFile(`${PY_DIR}/${f}`, sources[f]);
  const info = pyodide.runPython(`
import sys, json
if ${JSON.stringify(PY_DIR)} not in sys.path:
    sys.path.insert(0, ${JSON.stringify(PY_DIR)})
import decluster_reasenberg as D
ok = D.module_sha256() == D.MODULE_SHA256_FROZEN
json.dumps(dict(ok=ok, module_version=D.R.__version__, adapter_version=D.ADAPTER_VERSION,
                module_sha256=D.module_sha256(), python=sys.version.split()[0],
                numpy=__import__('numpy').__version__))
`);
  const meta = JSON.parse(info);
  if (!meta.ok) throw new Error('Adaptörün kendi sha256 denetimi başarısız. Hesap yapılmadı.');
  return { ...meta, sha256: sha };
}

// events: EQ-Live olay nesneleri (id, time, lat, lon, dep, mag[, mw]).
// Dönüş: sunucudaki decluster_reasenberg.decluster ile aynı sırada üyelik.
export function runReasenberg(pyodide, events, xmeff, { rule = 'zmap', magField = 'mag' } = {}) {
  pyodide.globals.set('_rb_in', JSON.stringify(events));
  const out = pyodide.runPython(`
import json, decluster_reasenberg as D
_evs, _o = D.decluster(json.loads(_rb_in), ${Number(xmeff)}, ${JSON.stringify(rule)}, ${JSON.stringify(magField)})
_r = _o['res']
json.dumps(dict(
    ids=[e.get('id') for e in _evs],
    cluster_id=_o['cluster_id'],
    event_class=_o['event_class'],
    n_clusters=(_r.n_clusters if _r is not None else 0),
    params=(D.json_safe(dict(_r.params.__dict__)) if _r is not None else None)))
`);
  pyodide.globals.delete('_rb_in');
  return JSON.parse(out);
}

// Öz-sınama (K0): 4 dondurulmuş referansla birebir karşılaştırma. getJson(path) depo kökünden okur.
export const SELFTEST_NAMES = ['adiyaman', 'izmit_dogu', 'saimbeyli', 'van_bati'];
export async function runSelfTest(pyodide, getJson) {
  const rows = [];
  for (const nm of SELFTEST_NAMES) {
    const ref = await getJson(`scripts/fixtures/reasenberg_zmap_${nm}_ref.json`);
    const cat = (await getJson(ref.catalog)).events;
    const r = runReasenberg(pyodide, cat, ref.params.xmeff, { rule: ref.params.rule, magField: ref.params.mag_field });
    const got = r.ids.map((id, i) => [id, r.cluster_id[i], r.event_class[i]]);
    rows.push({ name: nm, n: got.length, same: JSON.stringify(got) === JSON.stringify(ref.membership) });
  }
  return { passed: rows.every(r => r.same), rows };
}
