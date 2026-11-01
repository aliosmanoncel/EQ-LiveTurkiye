// SONRADAN (post hoc) duyarlılık (2026-11-01): Türkiye ML dönemi sınamasındaki uyumsuzluk 2023 Kahramanmaraş dizisinden mi?
// Sınama dönemi 2019–son, 2023 yılı çıkarılarak (T_S'den 1 yıl düşülür). Önceden sabitlenen kurallara dahil değildir; yalnız yorum içindir.
// Kullanım: node analysis/poisson_donem/sonradan_2023.js <disa_aktar çıktısı.json>
'use strict';
const A = require('./analiz.js'), V = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8')), Y = y => Date.UTC(y, 0, 1), YIL = 365.25 * 864e5;
const s = V.senaryolar.tr_emsc, son = s.pencereSon, out = [];
for (const gk of [0, 1]) { const ev = gk ? s.olaylar.filter(e => e.gk) : s.olaylar;
  for (const M of [4.0, 4.5, 5.0, 5.5]) {
    const NK = ev.filter(e => e.t >= Y(2012) && e.t < Y(2019) && e.m >= M - 1e-9).length, TK = 7;
    const S = ev.filter(e => e.t >= Y(2019) && e.t < son && e.m >= M - 1e-9 && !(e.t >= Y(2023) && e.t < Y(2024))), TS = (son - Y(2019)) / YIL - 1;
    const NS = S.length, p = A.binom2(NS, NK + NS, TS / (TK + TS));
    out.push({ gk: gk ? 'gk74' : 'ham', M, NK, NS, beklenen: NK / TK * TS, oran: (NS / TS) / (NK / TK), p });
    console.log(`${gk ? 'gk74' : 'ham '} M≥${M.toFixed(1)}: 2023 hariç — beklenen ${(NK / TK * TS).toFixed(1)}, gözlenen ${NS}, oran ${((NS / TS) / (NK / TK)).toFixed(2)}, p = ${p < 1e-4 ? p.toExponential(1) : p.toFixed(3)}`); } }
require('fs').writeFileSync(require('path').join(__dirname, 'sonradan_2023.json'), JSON.stringify(out, null, 1));
