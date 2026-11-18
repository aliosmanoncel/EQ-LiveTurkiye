// validate_pmsr_parity.mjs — Pre-mainshock Seismicity Rate Test: SCSN bölge kutusu regresyon testi
// Çalıştır: node scripts/validate_pmsr_parity.mjs
// Bağımsız JS çekirdeği (lab/premainshock-rate/core.mjs), donmuş referansla karşılaştırılır.
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { selectMainshocks, localMc, analyzeEvent, PMSR_VERSION } from '../lab/premainshock-rate/core.mjs';

const here = new URL('.', import.meta.url);
const ref = JSON.parse(readFileSync(new URL('fixtures/pmsr_scsn_box_ref.json', here)));
const csv = gunzipSync(readFileSync(new URL('fixtures/pmsr_scsn_box_catalog.csv.gz', here))).toString().trim().split('\n');
const cat = csv.slice(1).map(l => { const [id, t, lat, lon, m] = l.split(','); return { id: +id, t: +t, lat: +lat, lon: +lon, m: +m }; })
  .sort((a, b) => a.t - b.t);
const idx = new Map(cat.map((e, i) => [e.id, i]));
const T2009 = Date.UTC(2009, 0, 1) / 1000;

const sel = selectMainshocks(cat).filter(s => cat[s.i].t >= T2009);
const rmap = new Map(ref.candidates.map(c => [c.id, c]));
const cnt = { candidates: sel.length, fixed: sel.filter(s => s.fixed).length, magdep: sel.filter(s => s.magdep).length, combined: sel.filter(s => s.combined).length };
const selDiff = sel.filter(s => { const r = rmap.get(s.id); return !r || r.fixed !== s.fixed || r.magdep !== s.magdep; })
  .map(s => ({ id: s.id, js: [s.fixed, s.magdep], ref: rmap.has(s.id) ? [rmap.get(s.id).fixed, rmap.get(s.id).magdep] : null }));

let mcEq = 0, nEq = 0, escEq = 0, pMax = 0, sigJs = 0, sigRef = 0, typeAEq = 0;
const diffs = [];
for (const r of ref.results) {
  const a = analyzeEvent(cat, idx.get(r.id));
  if (a.mc.n === r.n_mc && a.mc.radiusKm === r.r_mc) nEq++;
  if (r.enough && Math.abs(a.mc.mc - r.mc) < 1e-6) mcEq++;
  if (a.typeA === r.typeA) typeAEq++;
  if (r.enough) {
    if (r.p < 0.01) sigRef++;
    if (a.esr && a.esr.significant) sigJs++;
    if (a.esr && Math.abs(a.mc.mc - r.mc) < 1e-6) {
      const dp = Math.abs(a.esr.p - r.p); pMax = Math.max(pMax, dp);
      if (a.esr.nObs === r.n_obs && a.esr.nCalib === r.n_calib && dp < 1e-12) escEq++;
    }
  }
  if (r.enough && Math.abs(a.mc.mc - r.mc) >= 1e-6) diffs.push({ id: r.id, mc_js: a.mc.mc, mc_ref: r.mc, n: a.mc.n });
}
const nEnough = ref.results.filter(r => r.enough).length;
const report = {
  version: PMSR_VERSION, reference: ref.version,
  selection: { js: cnt, ref: ref.expected, per_event_diffs: selDiff.length, diffs: selDiff.slice(0, 10) },
  mc: { n_radius_equal: `${nEq}/${ref.results.length}`, mc_equal: `${mcEq}/${nEnough}`, diffs: diffs.slice(0, 10) },
  esr_given_same_mc: { equal: `${escEq}/${mcEq}`, max_abs_dp: pMax },
  typeA_equal: `${typeAEq}/${ref.results.length}`,
  significant: { js: sigJs, ref: sigRef },
};
console.log(JSON.stringify(report, null, 1));
const pass = selDiff.length === 0 && cnt.combined === ref.expected.combined && mcEq === nEnough && escEq === mcEq && typeAEq === ref.results.length;
console.log(pass ? 'SONUÇ: BİREBİR AYNI' : 'SONUÇ: FARK VAR');
process.exit(pass ? 0 : 1);
