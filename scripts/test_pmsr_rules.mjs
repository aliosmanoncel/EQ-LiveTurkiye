// test_pmsr_rules.mjs — kabul kuralları (sentetik): artçı seçimi ve yetersiz veri
import { selectMainshocks, analyzeEvent, esr } from '../lab/premainshock-rate/core.mjs';
import { filterDominantMagType } from '../lab/premainshock-rate/sources.mjs';
const D = 86400; let fail = 0; const ok = (c, m) => { console.log((c ? 'GEÇTİ ' : 'KALDI ') + m); if (!c) fail++; };
// Bol arka plan (Mc için ≥275 olay) + M5.5 ana şok + 2 gün sonra 10 km'de M4.2 artçı
let s = 12345; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
const cat = [];
for (let i = 0; i < 3000; i++) cat.push({ id: 'b' + i, t: rnd() * 800 * D, lat: 40.8 + (rnd() - .5) * .3, lon: 31 + (rnd() - .5) * .4, m: +(1 - Math.log10(1 - rnd() * .999)).toFixed(1) });
cat.push({ id: 'MS', t: 700 * D, lat: 40.8, lon: 31.0, m: 5.5 }, { id: 'AS', t: 702 * D, lat: 40.85, lon: 31.05, m: 4.2 });
// Seyrek bölge: uzakta yalnız 40 olay + M4.5
for (let i = 0; i < 40; i++) cat.push({ id: 's' + i, t: rnd() * 800 * D, lat: 30 + (rnd() - .5) * .2, lon: 20 + (rnd() - .5) * .2, m: 1.5 + rnd() * 2 });
cat.push({ id: 'SP', t: 750 * D, lat: 30, lon: 20, m: 4.5 });
cat.sort((a, b) => a.t - b.t);
const sel = new Map(selectMainshocks(cat).map(x => [x.id, x]));
ok(sel.get('MS')?.combined === true, 'Ana şok (M5,5) Combined seçildi');
ok(sel.get('AS') && sel.get('AS').combined === false && sel.get('AS').magdep === false, 'Artçı (M4,2, 2 gün sonra) Mag-Dep ile dışlandı → test uygulanmaz');
const sp = analyzeEvent(cat, cat.findIndex(e => e.id === 'SP'));
ok(sp.label === 'na' && sp.esr === null && sp.mc.n < 275, `Seyrek bölge: "Analiz için yeterli veri yok" (50 km içinde ${sp.mc.n} olay)`);
const ms = analyzeEvent(cat, cat.findIndex(e => e.id === 'MS'));
ok(ms.label === 'sig' || ms.label === 'ns', `Yeterli veri: test çalıştı (etiket ${ms.label}, Mc ${ms.mc.mc}, n ${ms.mc.n})`);
// Büyüklük türü filtresi: ml baskın katalogda Mw ana şok korunmalı (Ridgecrest 2019 hatası)
const mix = [...Array(50)].map((_, i) => ({ id: 'l' + i, t: i, lat: 0, lon: 0, m: 1 + (i % 20) / 10, magType: 'ml' }))
  .concat([{ id: 'w6', t: 99, lat: 0, lon: 0, m: 6.4, magType: 'mw' }, { id: 'w2', t: 98, lat: 0, lon: 0, m: 2.5, magType: 'mw' }]);
const f = filterDominantMagType(mix, 4);
ok(f.dominant === 'ml' && f.cat.some(e => e.id === 'w6'), 'Baskın tür filtresi Mw 6,4 ana şoku korudu');
ok(!f.cat.some(e => e.id === 'w2'), 'Baskın tür filtresi eşik altındaki Mw 2,5 olayını çıkardı');
// p = 0 durumunda muhafazakâr p tek yılda ≥ 1/(n+1)
const e0 = esr([1, 2, 3, 4, 5, 6, 7, 8, 100, 250]);
ok(e0.p === 0 && e0.nIndependent === 17 && Math.abs(e0.pConservative - 1 / 18) < 1e-12, `p = 0 iken muhafazakâr p = 1/18 (n = ${e0.nIndependent})`);
process.exit(fail ? 1 : 0);
