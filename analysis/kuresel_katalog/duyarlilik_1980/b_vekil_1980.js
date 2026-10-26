// Duyarlılık analizi (2026-10-26; kullanıcı onayı): ISC-GEM v12.1 ana katalog, 1980–2021, küresel.
// Tüm Mw (T) ile yalnız doğrudan Mw (D; s = d ve M0 kaynağı gcmt/bibliog) örneklemlerinde Mc ve b ayrı ayrı.
// V (yalnız vekil) yalnız tanı içindir. Fonksiyonlar index.html'den okunur (EQ-Live'ın varsayılan yolu):
//   büyüklük 0,1 sınıfına yuvarlanır (bGridRound), Mc = maksimum eğrilik + 0,2 (computeMcSrc), b = Aki–Utsu (computeBvalue, ΔM = 0,1),
//   %95 aralık = bCiFields (ızgaradaki veride Tinti & Mulargia 1987).
// T ve D iç içe kümelerdir (D ⊂ T); bağımsız örneklem testleri (ör. Utsu) uygulanamaz, yalnız aralıklar verilir.
// Kullanım (depo kökünde): node analysis/kuresel_katalog/duyarlilik_1980/b_vekil_1980.js
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto');
const root = path.join(__dirname, '..', '..', '..');
const src = fs.readFileSync(path.join(root, 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
const ctx = { URLSearchParams, location: { search: '' } }; vm.createContext(ctx);
vm.runInContext([fn('bGridRound'), 'var MC_DM = 0.1;', fn('mcSrcMag'), fn('computeMcSrc'), fn('computeBvalue'),
  cut('function bConfidence95(b, n)', '// Kayan pencere b-değeri'),
  'globalThis.__x = { bGridRound, computeMcSrc, computeBvalue, bCiFields, get ci() { return B_CI_METHOD; } };'].join('\n'), ctx);
const X = ctx.__x;

const dosya = path.join(root, 'data', 'iscgem_global.json');
const ham = fs.readFileSync(dosya), G = JSON.parse(ham), A = Object.fromEntries(G.alanlar.map((a, i) => [a, i]));
const ev = G.olaylar.filter(o => +o[A.t].slice(0, 4) >= 1980 && +o[A.t].slice(0, 4) <= 2021);
const grup = o => o[A.Mw_yontem] === 'vekil' ? 'V' : (o[A.Mw_yontem] === 'dogrudan' && o[A.Mw_M0_kaynak]) ? 'D' : 'belirsiz';
const S = { T: ev, D: ev.filter(o => grup(o) === 'D'), V: ev.filter(o => grup(o) === 'V') };
const mags = L => L.map(o => X.bGridRound(o[A.M], 0, 0.1));
const r3 = x => x === null || !Number.isFinite(x) ? x : +x.toFixed(3);

function bAt(m, Mc) {
  const sub = m.filter(x => x >= Mc - 1e-9); if (sub.length < 10) return { Mc, N: sub.length, b: null };
  const b = X.computeBvalue(m, Mc, 0.1), ci = X.bCiFields(b, sub.length, sub.map(x => +(x - Mc).toFixed(10)), 0.1);
  return { Mc: +Mc.toFixed(1), N: sub.length, M_aralik: [Math.min(...sub), Math.max(...sub)], b: r3(b), ci95: [r3(ci.lo), r3(ci.hi)], ci_yontem: ci.ciM };
}
const out = { girdi: { dosya: 'data/iscgem_global.json', sha256: crypto.createHash('sha256').update(ham).digest('hex') },
  yontem: { donem: '1980–2021', kapsam: 'küresel (ISC-GEM ana katalog)', yuvarlama: 'bGridRound 0,1', Mc: 'maksimum eğrilik + 0,2 (computeMcSrc)', b: 'Aki–Utsu, ΔM = 0,1', aralik: X.ci,
    not: 'T ⊃ D (iç içe); bağımsız örneklem testi uygulanamaz.' }, orneklem: {}, ortak_Mc: {}, b_Mc_egrisi: {}, histogram: {} };
for (const [k, L] of Object.entries(S)) {
  const m = mags(L), Mc = X.computeMcSrc(m.map(x => ({ mag: x })));
  out.orneklem[k] = { N_toplam: L.length, ...bAt(m, Mc) };
  const h = {}; m.forEach(x => { const b = x.toFixed(1); h[b] = (h[b] || 0) + 1; }); out.histogram[k] = Object.fromEntries(Object.entries(h).sort((a, b) => +a[0] - +b[0]).filter(([b]) => +b <= 6.5));
}
const Mcs = [...new Set([out.orneklem.T.Mc, out.orneklem.D.Mc, Math.max(out.orneklem.T.Mc, out.orneklem.D.Mc)])].sort();
for (const Mc of Mcs) out.ortak_Mc[Mc.toFixed(1)] = { T: bAt(mags(S.T), Mc), D: bAt(mags(S.D), Mc) };
for (let k = 48; k <= 65; k++) { const Mc = k / 10; out.b_Mc_egrisi[Mc.toFixed(1)] = Object.fromEntries(['T', 'D', 'V'].map(s => { const r = bAt(mags(S[s]), Mc); return [s, { N: r.N, b: r.b, ci95: r.ci95 }]; })); }
out.belirsiz_grup = ev.filter(o => grup(o) === 'belirsiz').map(o => o[A.id]);
// ── İç tutarlılık denetimleri (2026-10-26, ChatGPT önerisi 1) ──
{ const idT = new Set(S.T.map(o => o[A.id])), yil = L => [Math.min(...L.map(o => +o[A.t].slice(0, 4))), Math.max(...L.map(o => +o[A.t].slice(0, 4)))];
  const nAt = (L, Mc) => mags(L).filter(x => x >= Mc - 1e-9).length, oT = out.orneklem.T, oD = out.orneklem.D;
  out.tutarlilik = {
    D_alt_kume_T: S.D.every(o => idT.has(o[A.id])), V_alt_kume_T: S.V.every(o => idT.has(o[A.id])),
    D_V_ayrik: !S.D.some(o => o[A.Mw_yontem] === 'vekil'), T_eq_D_V_belirsiz: S.T.length === S.D.length + S.V.length + out.belirsiz_grup.length,
    yil_araliklari: { T: yil(S.T), D: yil(S.D), V: yil(S.V) }, cografi_filtre: 'yok (küresel; üç örneklemde aynı)',
    N_kendi_Mc: { T: [oT.Mc, oT.N, nAt(S.T, oT.Mc)], D: [oD.Mc, oD.N, nAt(S.D, oD.Mc)] },
    her_Mc_icin_N_D_le_N_T: Object.values(out.b_Mc_egrisi).every(r => r.D.N <= r.T.N),
    aciklama: "N(D, Mc 5,3) = 28 858 > N(T, Mc 5,4) = 26 025, çünkü eşikler farklı; aynı Mc'de her zaman N(D) ≤ N(T)." };
  if (!Object.entries(out.tutarlilik).every(([k, v]) => typeof v !== 'boolean' || v)) throw new Error('tutarlılık denetimi KALDI: ' + JSON.stringify(out.tutarlilik)); }

// ── Eşleştirilmiş bootstrap: b_T − b_D farkının belirsizliği (ChatGPT önerisi 2) ──
// Her tekrarda T'den olaylar yerine koyarak çekilir; D_rep = çekilen olaylardan doğrudan olanlar. Aynı olaylar iki örneklemde
// birlikte değiştiği için iç içe yapı korunur. Mc ya sabit tutulur ya da her tekrarda iki örneklem için ayrı ayrı yeniden kestirilir.
{ let st = 20261026 >>> 0; const rnd = () => { st = (st + 0x6D2B79F5) >>> 0; let t = st; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };   // mulberry32
  const mT = mags(S.T), isD = S.T.map(o => grup(o) === 'D'), n = mT.length, B = 2000;
  const kip = { 'Mc ayrı ayrı yeniden kestirilir': null, 'Mc = 5,5 sabit': 5.5, 'Mc = 6,0 sabit': 6.0 }, R = {};
  for (const k in kip) R[k] = { dT: [], bT: [], bD: [], McT: [], McD: [] };
  for (let r = 0; r < B; r++) {
    const xt = new Array(n), xd = []; for (let i = 0; i < n; i++) { const j = (rnd() * n) | 0; xt[i] = mT[j]; if (isD[j]) xd.push(mT[j]); }
    const mcT = X.computeMcSrc(xt.map(x => ({ mag: x }))), mcD = X.computeMcSrc(xd.map(x => ({ mag: x })));
    for (const [k, f] of Object.entries(kip)) { const a = f ?? mcT, c = f ?? mcD, bt = X.computeBvalue(xt, a, 0.1), bd = X.computeBvalue(xd, c, 0.1);
      R[k].dT.push(bt - bd); R[k].bT.push(bt); R[k].bD.push(bd); R[k].McT.push(a); R[k].McD.push(c); } }
  const q = (v, p) => { const s = [...v].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
  const sikl = v => Object.fromEntries(Object.entries(v.reduce((m, x) => (m[x.toFixed(1)] = (m[x.toFixed(1)] || 0) + 1, m), {})).sort());
  out.bootstrap = { tekrar: B, tohum: 20261026, yontem: 'olay düzeyinde yerine koyarak; D_rep ⊂ T_rep', sonuc: {} };
  for (const [k, v] of Object.entries(R)) out.bootstrap.sonuc[k] = { fark_ortanca: r3(q(v.dT, 0.5)), fark_95: [r3(q(v.dT, 0.025)), r3(q(v.dT, 0.975))],
    fark_sifir_alti_orani: +(v.dT.filter(x => x <= 0).length / B).toFixed(4), bT_95: [r3(q(v.bT, 0.025)), r3(q(v.bT, 0.975))], bD_95: [r3(q(v.bD, 0.025)), r3(q(v.bD, 0.975))],
    McT_dagilim: sikl(v.McT), McD_dagilim: sikl(v.McD) }; }
fs.writeFileSync(path.join(__dirname, 'sonuc.json'), JSON.stringify(out, null, 1));
console.log(JSON.stringify({ tutarlilik: out.tutarlilik, bootstrap: out.bootstrap }, null, 1));
console.log('b(Mc):'); for (const [Mc, r] of Object.entries(out.b_Mc_egrisi)) console.log(Mc, ['T', 'D', 'V'].map(s => `${s} N=${r[s].N} b=${r[s].b} [${r[s].ci95 || ''}]`).join(' | '));
console.log('hist:', JSON.stringify(out.histogram));
