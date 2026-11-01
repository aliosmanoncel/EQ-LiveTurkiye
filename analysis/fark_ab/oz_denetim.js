// Öz-denetim (2026-11-01): Δa–Δb yönteminin sentetik kataloglarla sınanması (analiz.js'in senaryo() fonksiyonu; büyüklük karıştırma sıfır modeli).
// T1 Durağan Poisson + G–R (b = 1): yanlış alarm oranı (beklenen ≈ %5).
// T2 Güç: rejimler — A (hız λ, b = 1,0) ve B (hız 2λ, b = 0,8) bloklar halinde rastgele sırayla: Δa–Δb negatif bağ beklenir.
// T3 Tamlık dalgalanması: gerçek b = 1, durağan hız; algılama eşiği Mc_t her yıl 3,0–3,4 arasında rastgele (kesim 3,0). Mc 3,2'de analiz → tamlık
//    dalgalanması pozitif Δa–Δb üretir mi? Mc 3,5'te (Mc_t'nin üstü) yanlış alarm oranı ≈ %5 mi?
// Kullanım (depo kökünde): node analysis/fark_ab/oz_denetim.js
'use strict';
const A = require('./analiz.js');
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const YIL = 365.25 * 864e5, T0 = Date.UTC(2000, 0, 1);
const grM = (r, b, Mmin) => Math.round((Mmin - 0.05 - Math.log(1 - r()) / (b * Math.LN10)) * 10) / 10;   // 0,1 ızgarası, Mmin bininden başlar
function katalog(r, parcalar) { const o = []; let t = T0; for (const [nOlay, lam, b, Mmin] of parcalar) for (let i = 0; i < nOlay; i++) { t += -Math.log(1 - r()) / lam * YIL; o.push({ t, m: grM(r, b, Mmin) }); } return o; }
const KAT = 200, PERM = 199, N = 100, NW = 31;
const say = (ad, sonuclar) => { const g = sonuclar.filter(s => !s.yetersiz && s.pPerm !== null), red = g.filter(s => s.pPerm < 0.05).length, redN = g.filter(s => s.neff && s.neff.p !== null && s.neff.p < 0.05).length, nN = g.filter(s => s.neff && s.neff.p !== null).length;
  const rOrt = g.reduce((a, s) => a + s.r, 0) / g.length; console.log(`${ad}: ${g.length} katalog; r ortalama ${rOrt.toFixed(3)}; karıştırma p < 0,05: %${(100 * red / g.length).toFixed(1)}; n_eff p < 0,05: %${(100 * redN / Math.max(1, nN)).toFixed(1)} (${nN} test edilebilir)`);
  return { n: g.length, rOrt, red: red / g.length, redNeff: redN / Math.max(1, nN) }; };
const R = {};
{ const r = rng(11), s = []; for (let k = 0; k < KAT; k++) s.push(A.senaryo(katalog(r, [[N * NW, 200, 1.0, 3.0]]), N, 3.0, PERM, 100 + k)); R.T1 = say('T1 durağan (b = 1, Mc 3,0)', s); }
{ const r = rng(12), s = []; for (let k = 0; k < KAT; k++) { const p = []; for (let j = 0; j < 12; j++) p.push(r() < 0.5 ? [250, 200, 1.0, 3.0] : [250, 400, 0.8, 3.0]); s.push(A.senaryo(katalog(r, p), N, 3.0, PERM, 300 + k)); }
  R.T2 = say('T2 rejimler (yüksek hız ↔ düşük b)', s); }
{ const r = rng(13), s32 = [], s35 = [];
  for (let k = 0; k < KAT; k++) { const ham = katalog(r, [[60000, 2000, 1.0, 2.5]]), mct = {}; const o = ham.filter(e => { const y = new Date(e.t).getUTCFullYear(); if (mct[y] === undefined) mct[y] = 3.0 + Math.floor(r() * 5) / 10; return e.m >= Math.max(3.0, mct[y]) - 1e-9; });
    s32.push(A.senaryo(o.filter(e => e.m >= 3.2 - 1e-9), N, 3.2, PERM, 500 + k)); s35.push(A.senaryo(o.filter(e => e.m >= 3.5 - 1e-9), N, 3.5, PERM, 700 + k)); }
  R.T3_Mc32 = say('T3 tamlık dalgalanması, Mc 3,2 (Mc_t 3,0–3,4)', s32); R.T3_Mc35 = say('T3 tamlık dalgalanması, Mc 3,5 (Mc_t üstü)', s35); }
let pass = 0, fail = 0; const ok = (c, m) => { c ? pass++ : fail++; console.log((c ? '  ok  ' : '  !!  ') + m); };
ok(R.T1.red >= 0.02 && R.T1.red <= 0.09, `T1: yanlış alarm %${(100 * R.T1.red).toFixed(1)} (beklenen ≈ %5; 200 katalogda %2–9 kabul)`);
ok(Math.abs(R.T1.rOrt) < 0.05, `T1: r ortalaması ${R.T1.rOrt.toFixed(3)} ≈ 0 (pencere içi örnekleme ortak bileşen üretmiyor)`);
ok(R.T2.rOrt < -0.15 && R.T2.red > 0.5, `T2: ortak değişim yakalanıyor (r ortalama ${R.T2.rOrt.toFixed(2)}, güç %${(100 * R.T2.red).toFixed(0)})`);
ok(R.T3_Mc32.rOrt > 0.1 && R.T3_Mc32.red > 0.2, `T3: tamlık dalgalanması Mc 3,2'de POZİTİF Δa–Δb üretiyor (r ortalama ${R.T3_Mc32.rOrt.toFixed(2)}, p < 0,05 %${(100 * R.T3_Mc32.red).toFixed(0)})`);
ok(R.T3_Mc35.red <= 0.09, `T3: Mc_t'nin üstünde (Mc 3,5) yanlış alarm %${(100 * R.T3_Mc35.red).toFixed(1)} (≈ %5)`);
require('fs').writeFileSync(require('path').join(__dirname, 'oz_denetim.json'), JSON.stringify(R, null, 1));
console.log(`\n${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`); process.exit(fail ? 1 : 0);
