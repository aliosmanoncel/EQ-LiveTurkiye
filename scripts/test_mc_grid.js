// Birim testi: Mc–ızgara düzeltmesi (2026-10-18). Dönüştürülmüş büyüklüklerde Mc kaynak ölçeğinde bulunur, Mc ve ΔM aynı
// bağıntıyla taşınır (computeMcScale / mcScale), Aki b'si ΔM_Mw ile hesaplanır. Fonksiyonlar index.html'den okunur.
// Denetlenen iddialar:
//   1. Dönüşüm yokken computeMc ve computeBvalue eski tanımla birebir aynıdır (MAXC + 0,2; ΔM/2 = 0,05).
//   2. Tek doğrusal bağıntıda (Mw = s·M + c): Mc_Mw = s·Mc + c, ΔM_Mw = s·ΔM; eşik aynı olayları seçer; b_Mw = b_kaynak / s (tam).
//   3. Eski hesap (Mw'nin 0,1 bin'lerinden Mc, ΔM/2 = 0,05) bu sentetik durumda b'yi belirgin biçimde düşük verir.
//   4. b(t) serisi (computeBvalueTimeSeries) aynı düzeltmeyi taşır: her pencerede b_Mw = b_kaynak / s.
//   5. Eşik çevresinde baskın bağıntı seçilir; dönüştürülen olaylar azınlıktaysa eşleme yapılmaz.
// Kullanım (depo kökünde): node scripts/test_mc_grid.js [index.html]
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); if (i < 0 || j < 0) throw new Error('bulunamadı: ' + a); return src.slice(i, j); };
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); if (i < 0) throw new Error('bulunamadı: ' + name);
  const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const ctx = {}; vm.createContext(ctx);
// Sınama bağıntıları: Çıvgın & Scordilis (2019) biçiminde doğrusal (0,93·ML + 0,29) ve ikinci bir doğrusal bağıntı (0,85·mb + 1,03)
vm.runInContext(`var bTimeAnchor = 'mean'; var MAG_CONVERSIONS = { lin: { convert(e) { return 0.93 * e.mag + 0.29; } }, mbx: { convert(e) { return 0.85 * e.mag + 1.03; } } };\n`
  + cut('const MC_DM = 0.1;', '// Aki (1965) MLE b-değeri').replace('const MC_DM', 'var MC_DM')
  + ['computeBvalue', 'bConfidence95', 'bWinStart', 'bWinTime', 'computeBvalueTimeSeries'].map(fn).join('\n')
  + '\nglobalThis.__x = { computeMc, computeMcScale, computeBvalue, computeBvalueTimeSeries, fmtM };', ctx);
const X = ctx.__x;
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL', msg); } };
const near = (a, b, t = 1e-9) => Math.abs(a - b) <= t;
// Eski tanımlar (2026-10-17 sürümü, karşılaştırma için kopya)
const oldMc = L => { const m = L.map(e => e.mw ?? e.mag).filter(v => v > 0); if (m.length < 10) return null; const b = {};
  m.forEach(v => { const k = (Math.round(v * 10) / 10).toFixed(1); b[k] = (b[k] || 0) + 1; });
  let mx = -1, mb = null; for (const k in b) if (b[k] > mx) { mx = b[k]; mb = parseFloat(k); } return +(mb + 0.2).toFixed(1); };
const oldB = (m, Mc) => { const s = m.filter(v => v >= Mc); if (s.length < 10) return null; const mu = s.reduce((a, v) => a + v, 0) / s.length, d = mu - Mc + 0.05; return d > 0 ? Math.LOG10E / d : null; };
// Sentetik katalog (YAPAY VERİ): G-R b = 1, M ≥ 1,0, 0,1 ızgarası; M < 1,6'da tamsızlık (algılama olasılığı azalır)
function cat(n, seed, b = 1) { let s = seed; const r = () => (s = (s * 16807) % 2147483647) / 2147483647, ev = [];
  for (let i = 0; i < n; i++) { const m = Math.round((1.0 - Math.log10(1 - r()) / b) * 10) / 10; if (m < 1.6 && r() > (m - 0.9) / 0.7) continue;
    ev.push({ time: new Date(Date.UTC(2000, 0, 1) + r() * 8e11), mag: m, mw: m, mtype: 'ml' }); } return ev; }
const conv = (L, k, lo = -Infinity) => L.map(e => e.mag >= lo ? { ...e, mw: ctx.MAG_CONVERSIONS[k].convert(e), mcv: k } : e);

// 1. Dönüşüm yokken eski tanımla birebir
for (const seed of [3, 11, 29, 101]) { const L = cat(20000, seed);
  ok(X.computeMc(L) === oldMc(L), `seed ${seed}: computeMc eski tanımla aynı (${X.computeMc(L)} / ${oldMc(L)})`);
  const mags = L.map(e => e.mw), mc = oldMc(L);
  ok(X.computeBvalue(mags, mc) === oldB(mags, mc), `seed ${seed}: computeBvalue eski tanımla aynı`);
  const sc = X.computeMcScale(L); ok(!sc.mapped && sc.dm === 0.1, `seed ${seed}: dönüşüm yokken eşleme yok, ΔM = 0,1`); }

// 2–3. Tek doğrusal bağıntı
for (const seed of [3, 11, 29, 101]) { const L = cat(40000, seed), W = conv(L, 'lin', 1.0), sc = X.computeMcScale(W), mc0 = oldMc(L);
  ok(sc.mapped && sc.mcSrc === mc0, `seed ${seed}: kaynak Mc dönüşümsüz Mc ile aynı (${sc.mcSrc})`);
  ok(near(sc.mc, 0.93 * mc0 + 0.29) && near(sc.dm, 0.093), `seed ${seed}: Mc_Mw = s·Mc + c (${sc.mc}), ΔM_Mw = s·ΔM (${sc.dm})`);
  ok(W.filter(e => e.mw >= sc.mc - 1e-9).length === L.filter(e => e.mag >= mc0).length, `seed ${seed}: eşik aynı olayları seçer`);
  const b0 = X.computeBvalue(L.map(e => e.mag), mc0), b1 = X.computeBvalue(W.map(e => e.mw), sc.mc, sc.dm);
  ok(near(b1, b0 / 0.93, 1e-9), `seed ${seed}: b_Mw = b/s (${b1.toFixed(4)} = ${(b0 / 0.93).toFixed(4)})`);
  const bOld = oldB(W.map(e => e.mw), oldMc(W));
  ok(Math.abs(bOld - b0 / 0.93) > 0.05, `seed ${seed}: eski hesap yanlı (${bOld.toFixed(3)} ≠ ${(b0 / 0.93).toFixed(3)})`);
  // 4. b(t)
  const s0 = X.computeBvalueTimeSeries(L, mc0, 10).series, s1 = X.computeBvalueTimeSeries(W, sc.mc, 10, sc.dm).series;
  ok(s0.length === s1.length && s0.length > 50 && s0.every((p, i) => near(s1[i].b, p.b / 0.93, 1e-9) && p.t === s1[i].t), `seed ${seed}: b(t) her pencerede b/s (${s1.length} pencere)`);
}
// 5. Baskın bağıntı ve azınlık durumu
{ const L = cat(40000, 7), A = L.map((e, i) => i % 4 === 0 ? { ...e, mw: 0.85 * e.mag + 1.03, mcv: 'mbx' } : { ...e, mw: 0.93 * e.mag + 0.29, mcv: 'lin' });
  const sc = X.computeMcScale(A); ok(sc.mapped && near(sc.dm, 0.093) && sc.share > 0.7, `karışık: baskın bağıntı (%75 lin) seçildi (pay ${sc.share.toFixed(2)})`);
  const B = L.map((e, i) => i % 5 === 0 ? { ...e, mw: 0.93 * e.mag + 0.29, mcv: 'lin' } : e), sb = X.computeMcScale(B);
  ok(!sb.mapped && sb.dm === 0.1, 'dönüştürülen olaylar azınlıkta (%20): eşleme yapılmaz'); }
ok(X.fmtM(1.8) === '1.8' && X.fmtM(0.93 * 1.8 + 0.29) === '1.96' && X.fmtM(null) === '—', 'fmtM biçimi');
console.log(`${fail ? '!! ' : ''}${fail ? 'FAIL' : 'PASS'}: ${pass} geçti, ${fail} kaldı`);
process.exit(fail ? 1 : 0);
