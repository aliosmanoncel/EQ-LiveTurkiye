// PMSR 2018–2026 örneklem dışı test — ON_KAYIT.md'ye göre (pmsr-core-0.1.0, varsayılanlar)
// Çalıştır: node run_pmsr.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { selectMainshocks, analyzeEvent, wilson, PMSR_VERSION } from '../../lab/premainshock-rate/core.mjs';

const lines = gunzipSync(readFileSync(new URL('scsn_box_2017_2026.csv.gz', import.meta.url))).toString().trim().split('\n');
const H = lines[0].split(',');
const ix = k => H.indexOf(k);
const cat = lines.slice(1).map(l => { const f = l.split(','); return { id: +f[ix('id')], time: f[ix('time_utc')], t: +f[ix('t')], lat: +f[ix('lat')], lon: +f[ix('lon')], m: +f[ix('mag')] }; })
  .sort((a, b) => a.t - b.t);
const T0 = Date.UTC(2017, 0, 1) / 1000, TS = Date.UTC(2018, 0, 1) / 1000, TE = Date.UTC(2026, 10, 18) / 1000;

const sel = selectMainshocks(cat).filter(s => cat[s.i].t >= TS && cat[s.i].t < TE);
const comb = sel.filter(s => s.combined);

// Ridgecrest Mw 7.1 (SCSN id 38457511)
const rc = cat.find(e => e.id === 38457511);
const RC_T1 = Date.UTC(2019, 6, 4) / 1000, RC_T2 = Date.UTC(2020, 6, 4) / 1000;
const hav = (a, b, c, d) => { const R = Math.PI / 180, x = Math.sin((c - a) * R / 2) ** 2 + Math.cos(a * R) * Math.cos(c * R) * Math.sin((d - b) * R / 2) ** 2; return 12742 * Math.asin(Math.sqrt(x)); };

const rows = [];
for (const s of comb) {
  const e = cat[s.i];
  const a = analyzeEvent(cat, s.i, { catalogStart: T0 });
  const c = analyzeEvent(cat, s.i, { catalogStart: T0, mcCausal: true });
  rows.push({
    id: e.id, time: e.time, m: e.m, lat: e.lat, lon: e.lon,
    mc: a.mc.enough ? +a.mc.mc.toFixed(2) : '', n_mc: a.mc.n, r_mc: a.mc.radiusKm,
    n_obs: a.esr?.nObs ?? '', n_calib: a.esr?.nCalib ?? '', p: a.esr ? a.esr.p : '', p_cons: a.esr ? a.esr.pConservative : '',
    typeA: a.typeA, label: a.label,
    causal_mc: c.mc.enough ? +c.mc.mc.toFixed(2) : '', causal_label: c.label,
    ridgecrest_zone: e.t >= RC_T1 && e.t < RC_T2 && hav(e.lat, e.lon, rc.lat, rc.lon) <= 50,
  });
}
const count = (rs, lab) => { const an = rs.filter(r => r[lab] !== 'na'); return { analyzed: an.length, sig: an.filter(r => r[lab] === 'sig').length, na: rs.length - an.length }; };

// Fisher iki yönlü
const lf = n => { let s = 0; for (let i = 2; i <= n; i++) s += Math.log(i); return s; };
function fisher(a, b, c, d) {
  const r1 = a + b, r2 = c + d, c1 = a + c, n = r1 + r2;
  const P = x => Math.exp(lf(r1) + lf(r2) + lf(c1) + lf(n - c1) - lf(n) - lf(x) - lf(r1 - x) - lf(c1 - x) - lf(r2 - c1 + x));
  const p0 = P(a); let p = 0;
  for (let x = Math.max(0, c1 - r2); x <= Math.min(r1, c1); x++) { const px = P(x); if (px <= p0 * (1 + 1e-9)) p += px; }
  return Math.min(1, p);
}
const REF = { sig: 15, analyzed: 58 };
const summ = (name, k) => {
  const w = wilson(k.sig, k.analyzed);
  return { name, ...k, rate: k.analyzed ? +(k.sig / k.analyzed).toFixed(3) : null, wilson95: w.map(x => +x.toFixed(3)),
    fisher_vs_2008_2017: +fisher(k.sig, k.analyzed - k.sig, REF.sig, REF.analyzed - REF.sig).toFixed(4) };
};
const prim = count(rows, 'label');
const out = {
  version: PMSR_VERSION, period: '2018-01-01 – 2026-11-17',
  selection: { candidates: sel.length, fixed: sel.filter(s => s.fixed).length, magdep: sel.filter(s => s.magdep).length, combined: comb.length },
  primary: summ('birincil (Mc tüm dönem)', prim),
  reference_2008_2017: { ...REF, rate: +(REF.sig / REF.analyzed).toFixed(3), wilson95: wilson(REF.sig, REF.analyzed).map(x => +x.toFixed(3)) },
  typeA: { n: rows.length, typeA_ge1: rows.filter(r => r.typeA > 0).length, ref_2008_2017: '24/61' },
  sensitivity: {
    causal_mc: summ('nedensel Mc', count(rows, 'causal_label')),
    ridgecrest_excluded: summ('Ridgecrest hariç', count(rows.filter(r => !r.ridgecrest_zone), 'label')),
    ridgecrest_zone_n: rows.filter(r => r.ridgecrest_zone).length,
    conservative_p_sig: rows.filter(r => r.p_cons !== '' && r.p_cons < 0.01).length,
  },
};
writeFileSync(new URL('sonuclar_2018_2026.csv', import.meta.url),
  [Object.keys(rows[0]).join(','), ...rows.map(r => Object.values(r).join(','))].join('\n') + '\n');
writeFileSync(new URL('ozet.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(JSON.stringify(out, null, 1));
