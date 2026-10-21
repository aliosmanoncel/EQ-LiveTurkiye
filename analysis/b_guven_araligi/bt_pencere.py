"""b(t) için N = 100 / N = 50 pencerelerinin karşılaştırılması (yalnız analiz).
Tek pencerede, gerçek b ile referans b0 = 1,0 arasındaki farkın %95 χ² aralığıyla ayırt edilme olasılığı (güç)
ve b = b0 iken yanlış ayırt etme oranı. ΔM = 0,1, EQ-Live kestiricisi. Kullanım: python3 bt_pencere.py"""
import json, math, numpy as np
from scipy import stats
L = math.log10(math.e); rng = np.random.default_rng(20261023); REPS = 20000; dm = 0.1; out = []
for N in (50, 100):
    ql, qu = stats.chi2.ppf(.025, 2 * N) / (2 * N), stats.chi2.ppf(.975, 2 * N) / (2 * N)
    for b in (0.6, 0.7, 0.8, 0.9, 1.0, 1.2):
        k = np.floor(rng.exponential(1 / (b / L), (REPS, N)) / dm)
        bh = L / (dm * (k.mean(1) + 0.5)); lo, hi = ql * bh, qu * bh
        excl = float(((hi < 1.0) | (lo > 1.0)).mean())
        out.append({'N': N, 'b_gercek': b, 'b0_disarida': excl, 'yari_genislik_ortanca': float(np.median((hi - lo) / 2)), 'bhat_sd': float(bh.std())})
json.dump({'meta': {'tekrar': REPS, 'tohum': 20261023, 'dM': dm, 'b0': 1.0, 'aralik': 'chi2 %95'}, 'sonuc': out}, open('out/bt_pencere.json', 'w'), indent=1)
for r in out: print(f"N={r['N']:>3} b={r['b_gercek']}: b0=1 aralık dışında {r['b0_disarida']*100:5.1f}% | yarı genişlik {r['yari_genislik_ortanca']:.3f} | sd(b̂) {r['bhat_sd']:.3f}")
