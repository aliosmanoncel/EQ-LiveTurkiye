// Tür içi b (2026-10-31): 1998 sınırındaki b sıçraması tür bileşiminden mi? Türkiye kutusu 36–42° K / 26–45° D, ham büyüklük (dönüşüm yok, GK74 yok),
// P1 = 1990–1997 (ISC), P2 = 1998–2005 (EMSC). Aki–Utsu b = log₁₀e / (ort(M) − (Mc − ΔM/2)), ΔM = 0,1; %95 ≈ ±1,96·b/√n. Ham veri yalnız okunur.
// Kullanım (depo kökünde): node analysis/olcek_isc_emsc/tur_ici_b.js
const d = require('../../data/eq_historical.json');
const tur = e => { const t = (e.mtype || '?').toLowerCase(); return t === 'mb' ? 'mb' : t === 'ms' ? 'Ms' : t === 'ml' ? 'ML' : t === 'md' ? 'MD' : /^mw/.test(t) ? 'Mw' : 'diğer'; };
const ev = d.events.filter(e => e.lat >= 36 && e.lat <= 42 && e.lon >= 26 && e.lon <= 45 && e.mag > 0);
const P = { P1: ['1990-01-01', '1998-01-01'], P2: ['1998-01-01', '2006-01-01'] };
const b = (ms, Mc) => { const v = ms.filter(m => m >= Mc - 1e-9); if (v.length < 30) return { n: v.length }; const m = v.reduce((a, x) => a + x, 0) / v.length, bb = Math.LOG10E / (m - (Mc - 0.05)); return { n: v.length, b: bb, ci: 1.96 * bb / Math.sqrt(v.length) }; };
const out = {};
for (const Mc of [3.7, 4.0]) for (const [ad, [t0, t1]] of Object.entries(P)) { const sub = ev.filter(e => e.time >= t0 && e.time < t1);
  const k = {}; sub.forEach(e => (k[tur(e)] = k[tur(e)] || []).push(e.mag)); k['tümü'] = sub.map(e => e.mag);
  for (const [t, ms] of Object.entries(k)) { const r = b(ms, Mc); out[`Mc ${Mc}|${t}|${ad}`] = r; } }
const f = r => r && r.b ? `${r.b.toFixed(2)} ± ${r.ci.toFixed(2)} (n = ${r.n})` : `— (n = ${r ? r.n : 0})`;
for (const Mc of [3.7, 4.0]) { console.log(`Mc = ${Mc}`); for (const t of ['tümü', 'MD', 'ML', 'mb', 'Ms', 'Mw']) console.log(`  ${t.padEnd(5)} P1 ${f(out[`Mc ${Mc}|${t}|P1`]).padEnd(26)} P2 ${f(out[`Mc ${Mc}|${t}|P2`])}`); }
require('fs').writeFileSync(require('path').join(__dirname, 'tur_ici_b.json'), JSON.stringify(out, null, 1));
