// b(t) pencere boyutu N = 20 … 500: düzleşme (zamansal çözünürlük) Monte Carlo — üretim kodu (computeBvalueTimeSeries, bCiFields,
// btClassOf; kopya yok). YAPAY katalog: 5000 olay (M ≥ Mc, 0,1 ızgarası), arka plan b = 1,0; ortada L olay süren düşük-b bölümü
// (b = 0,6; L = 100 / 200 / 400 / 1000); L = 0 durağan seri. Adım N/10, zaman damgası ortalama.
// Ölçütler: (i) bölümle örtüşen pencerelerden en az biri "düşük b" sınıfında (aralığın tamamı < 0,7) → yakalama;
// (ii) serinin en düşük b̂'si (ortanca) — eğrinin bölüme ne kadar inebildiği; (iii) L = 0'da seride en az bir yanlış sınıflı
// (düşük ya da yüksek) pencere — çok pencereli serilerde rastlantısal boyanma; (iv) L = 0'da pencere başına kapsama.
// Kullanım: node mc_btbuyuk.js [tekrar=300] [tohum=20261028]
'use strict';
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const fn = name => { const i = src.indexOf('\nfunction ' + name + '('); const j = src.slice(i + 1).search(/\n(?=[^\s}])/); return src.slice(i + 1, i + 2 + j); };
const cut = (a, b) => { const i = src.indexOf(a), j = src.indexOf(b, i); return src.slice(i, j); };
global.location = { search: '' };
(0, eval)(['var bTimeAnchor = "mean";', src.match(/^const BT_CLASS = [^\n]*$/m)[0].replace('const ', 'var '), 'var BT_WIN_N = 100;',
  ...['computeBvalue', 'bWinStart', 'bWinTime', 'computeBvalueTimeSeries', 'btClassOf'].map(fn), cut('function bConfidence95(b, n)', '// Kayan pencere b-değeri'),
  'global.__x = { computeBvalueTimeSeries, btClassOf };'].join('\n'));
const X = global.__x, REPS = +(process.argv[2] || 300), SEED = +(process.argv[3] || 20261028); let s = SEED;
const rnd = () => (s = (s * 48271) % 2147483647) / 2147483647, Mc = 3.0, T0 = Date.parse('2000-01-01'), DAY = 864e5, NEV = 5000;
const mag = b => +(Mc + Math.floor(-Math.log(1 - rnd()) / (b * Math.LN10) / 0.1) * 0.1).toFixed(1);
const NS = [20, 30, 50, 100, 200, 300, 500], LS = [0, 100, 200, 400, 1000], out = [], t0 = Date.now();
const med = a => { const q = a.slice().sort((x, y) => x - y); return q[Math.floor(q.length / 2)]; };
for (const L of LS) {
  const a0 = Math.floor((NEV - L) / 2), a1 = a0 + L;   // bölüm olay indeksleri [a0, a1)
  const acc = Object.fromEntries(NS.map(N => [N, { cat: 0, minb: [], anyCls: 0, cov: 0, nw: 0, wins: 0 }]));
  for (let r = 0; r < REPS; r++) {
    const ev = Array.from({ length: NEV }, (_, k) => ({ time: new Date(T0 + k * DAY), mag: mag(k >= a0 && k < a1 ? 0.6 : 1.0) }));
    for (const N of NS) {
      const st = Math.max(1, Math.round(N / 10)), ser = X.computeBvalueTimeSeries(ev, Mc, st, 0.1, N).series, A = acc[N];
      let caught = false, anyC = false, mn = Infinity;
      ser.forEach((q, k) => { const i0 = k * st, i1 = i0 + N, c = X.btClassOf(q.b, q.err, q.lo, q.hi); if (q.b < mn) mn = q.b;
        if (L && i0 < a1 && i1 > a0 && c === 'low') caught = true;
        if (!L) { if (c === 'low' || c === 'high') anyC = true; A.cov += q.lo <= 1 && 1 <= q.hi; A.nw++; } });
      A.cat += caught; A.anyCls += anyC; A.minb.push(mn); A.wins = ser.length;
    }
  }
  for (const N of NS) { const A = acc[N]; out.push({ L, N, adim: Math.max(1, Math.round(N / 10)), pencere: A.wins,
    yakalama: L ? A.cat / REPS : null, en_dusuk_b_ortanca: med(A.minb), durgun_yanlis_sinifli_seri: L ? null : A.anyCls / REPS, durgun_kapsama: L ? null : A.cov / A.nw }); }
}
fs.writeFileSync(path.join(__dirname, 'out', 'mc_btbuyuk.json'), JSON.stringify({ meta: { tekrar: REPS, tohum: SEED, olay: NEV, b_arka: 1.0, b_bolum: 0.6, sure_s: (Date.now() - t0) / 1000, kaynak: 'index.html' }, sonuc: out }, null, 1));
console.log('süre', (Date.now() - t0) / 1000, 's');
