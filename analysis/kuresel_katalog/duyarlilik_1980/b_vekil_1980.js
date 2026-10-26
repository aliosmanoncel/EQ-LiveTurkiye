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

const dosya = path.join(root, 'analysis', 'kuresel_katalog', 'uretim', 'iscgem_global.json');
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
const out = { girdi: { dosya: 'analysis/kuresel_katalog/uretim/iscgem_global.json', sha256: crypto.createHash('sha256').update(ham).digest('hex') },
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
fs.writeFileSync(path.join(__dirname, 'sonuc.json'), JSON.stringify(out, null, 1));
console.log(JSON.stringify({ orneklem: out.orneklem, ortak_Mc: out.ortak_Mc }, null, 1));
console.log('b(Mc):'); for (const [Mc, r] of Object.entries(out.b_Mc_egrisi)) console.log(Mc, ['T', 'D', 'V'].map(s => `${s} N=${r[s].N} b=${r[s].b} [${r[s].ci95 || ''}]`).join(' | '));
console.log('hist:', JSON.stringify(out.histogram));
