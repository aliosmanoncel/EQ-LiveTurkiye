// worker.mjs — PMSR hesapları arayüzü dondurmadan çalıştırır.
import { selectMainshocks, analyzeEvent, DEFAULTS, PMSR_VERSION } from './core.mjs';

const DAY = 86400;

// msg: { cat (zamana göre sıralı), opts, inner: {s,n,w,e} | null, t1, t2 }
self.onmessage = ({ data }) => {
  try {
    const { cat, opts = {}, inner, t1 = -Infinity, t2 = Infinity, onlyIds, t0 } = data;
    const o = { ...DEFAULTS, ...opts, ...(isFinite(t0) ? { catalogStart: t0 } : {}) };
    const sel = selectMainshocks(cat, o);
    const inBox = e => !inner || (e.lat >= inner.s && e.lat <= inner.n && e.lon >= inner.w && e.lon <= inner.e);
    // Ana şok adayı: iç kutuda, istenen dönemde ve katalog başlangıcından en az kalibrasyon+pencere kadar sonra
    const tStart = isFinite(t0) ? t0 : (cat.length ? cat[0].t : 0);
    const cand = sel.filter(s => {
      const e = cat[s.i];
      return inBox(e) && e.t >= t1 && e.t <= t2 && (!onlyIds || onlyIds.includes(String(e.id)));
    });
    const results = [];
    let k = 0;
    for (const s of cand) {
      const e = cat[s.i];
      const shortHistory = (e.t - tStart) / DAY < o.calibDays + o.windowDays;
      if (!s.combined) {
        results.push({ id: e.id, t: e.t, m: e.m, lat: e.lat, lon: e.lon, fixed: s.fixed, magdep: s.magdep, combined: false, label: 'notMain' });
      } else {
        const a = analyzeEvent(cat, s.i, o);
        // ayrıntı grafiği için ana şok öncesi günler (Mc filtreli, R içinde)
        results.push({ ...a, fixed: s.fixed, magdep: s.magdep, combined: true, shortHistory });
      }
      k++;
      if (k % 5 === 0) self.postMessage({ type: 'progress', done: k, total: cand.length });
    }
    self.postMessage({ type: 'done', version: PMSR_VERSION, nCandidates: cand.length,
      counts: { fixed: cand.filter(s => s.fixed).length, magdep: cand.filter(s => s.magdep).length, combined: cand.filter(s => s.combined).length },
      results });
  } catch (err) {
    self.postMessage({ type: 'error', message: String(err && err.message || err) });
  }
};
