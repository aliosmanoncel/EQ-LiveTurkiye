// Faz 5 — etki analizi: üretim Weichert zinciri (csBuild → sınıflama → weichertFit), index.html'den
// test_weichert_chain.js ile aynı yöntemle birebir okunur (kopya yok). index.html DEĞİŞTİRİLMEZ.
// Kullanım: node analysis/homog_faz5/etki_weichert.js <main index.html> <katalog dizini> <çıktı.json>
'use strict';
const fs = require('fs'), vm = require('vm');
const [htmlP, katDir, outP] = process.argv.slice(2);
const src = fs.readFileSync(htmlP, 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
const ctx = { document: { getElementById: () => ({ value: '' }) }, console }; vm.createContext(ctx);
vm.runInContext(src.match(/^const CS_QC = \{[^\n]*\};$/m)[0].replace('const CS_QC', 'var CS_QC'), ctx);
vm.runInContext('var MAG_CONVERSIONS = {};\n' + cut('const MC_DM = 0.1;', '// Aki (1965) MLE b-değeri').replace('const MC_DM', 'var MC_DM'), ctx);
vm.runInContext('var regionRect=null, regionWindowStart=null, regionWindowEnd=null, regionCapped=false, regionOrderUsed=null;', ctx);
vm.runInContext(cut('let csEnabled = false;', 'let lastGrFit = null;').replace('let csEnabled', 'var csEnabled').replace('let csSteps', 'var csSteps'), ctx);
const binBlock = cut('  const idx = m => Math.floor((m + 1e-9) / DM);', '  const wf = weichertFit(clsBest);');
vm.runInContext(`function __classify(items, cs, DM) {\n${binBlock}\n return { clsBest }; }`, ctx);
const run = c => vm.runInContext(c, ctx);
const W0 = Date.parse('1900-01-01T00:00:00Z'), W1 = Date.parse('2021-12-31T23:59:59Z');
const LADDERS = {
  L0_mevcut: [['1900', 5.5], ['1965', 4.5], ['1980', 4.0], ['1990', 3.5], ['1998', 3.0]],
  // Aday (Faz 4 kararı) + M<5 mevcut eşikler; tekdüzelik gereği 4,5 basamağı 1965 → 1979 (5,0 sınıfı 1979'dan önce tam değilse 4,5 de olamaz)
  L1_aday: [['1904', 6.0], ['1970', 5.5], ['1979', 4.5], ['1980', 4.0], ['1990', 3.5], ['1998', 3.0]],
};
const FITS = { tum_siniflar: null, M_ge_4_5: 4.5, M_ge_5_0: 5.0 };
const res = [];
for (const cat of ['C0_ham', 'C0_gk74', 'C1_ham', 'C1_gk74']) {
  const evs = JSON.parse(fs.readFileSync(`${katDir}/${cat}.json`, 'utf8')).map(([t, m]) => ({ time: new Date(t.length <= 19 ? t + 'Z' : t), mag: m }));
  for (const [ln, L] of Object.entries(LADDERS)) {
    ctx.csSteps = L.map(([y, mc]) => ({ start: `${y}-01-01`, mc: String(mc) })); ctx.csEnabled = true;
    ctx.regionRect = {}; ctx.regionWindowStart = new Date(W0); ctx.regionWindowEnd = new Date(W1);
    ctx.__ev = evs; const cs = run('csBuild(__ev)'); ctx.__cs = cs;
    const { clsBest } = run('__classify(__cs.kept, __cs, 0.1)');
    for (const [fn, lo] of Object.entries(FITS)) {
      const C = lo === null ? clsBest : clsBest.filter(c => c.m - 0.05 >= lo - 1e-9); ctx.__C = C;
      const wf = run('weichertFit(__C)'); if (!wf) { res.push({ cat, ln, fn, err: 'fit yok' }); continue; }
      const m0 = C[0].m - 0.05, lam = M => wf.rate0 * Math.exp(-wf.beta * (M - m0));
      const obs = M => C.filter(c => c.m - 0.05 >= M - 1e-9).reduce((s, c) => s + c.n / c.T, 0);
      const nObs = M => C.filter(c => c.m - 0.05 >= M - 1e-9).reduce((s, c) => s + c.n, 0);
      res.push({ cat, ln, fn, N: wf.N, K: C.length, m0: +m0.toFixed(2), b: +wf.b.toFixed(4), sigma: wf.sigma === null ? null : +wf.sigma.toFixed(4),
        rate_m0: +wf.rate0.toPrecision(5),
        model: Object.fromEntries([5.0, 5.5, 6.0, 6.5].map(M => [`lam_ge_${M}`, +lam(M).toPrecision(4)])),
        gozlenen: Object.fromEntries([5.0, 5.5, 6.0].map(M => [`ge_${M}`, { n: nObs(M), oran: +obs(M).toPrecision(4) }])),
        T: Object.fromEntries([3.0, 4.0, 4.5, 5.0, 5.5, 6.0].map(M => { const c = C.find(c => Math.abs(c.m - 0.05 - M) < 1e-6); return [M, c ? +c.T.toFixed(2) : null]; })) });
    }
  }
}
fs.writeFileSync(outP, JSON.stringify({ meta: { index_html: htmlP, pencere: ['1900-01-01', '2021-12-31'], DM: 0.1, Mx: null, ladders: LADDERS }, sonuc: res }, null, 1));
console.log('katalog  merdiven  fit           N      b ± σ            λ(≥5,0)  λ(≥5,5)  λ(≥6,0)  | gözlenen ≥5,0 / ≥5,5 / ≥6,0 (n/T)');
for (const r of res) if (!r.err) console.log(r.cat.padEnd(8), r.ln.padEnd(9), r.fn.padEnd(12), String(r.N).padStart(6), `${r.b.toFixed(3)} ± ${r.sigma.toFixed(3)}`.padStart(15),
  ...[5.0, 5.5, 6.0].map(M => String(r.model[`lam_ge_${M}`]).padStart(8)), ' |', ...[5.0, 5.5, 6.0].map(M => `${r.gozlenen[`ge_${M}`].oran}`.padStart(7)));
