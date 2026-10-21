"""
Monte Carlo kapsama testi: b güven aralığı yöntemleri (yalnız analiz).
Gerçek b bilinen sentetik G–R örneklemleri: m = m0 + Üstel(β), β = b·ln10.
  sürekli   : yuvarlama yok (ΔM = 0); kestirici b̂ = log10e/(M̄ − m0)
  ΔM = 0,1 / 0,5 : sınıf indeksi k = ⌊(m − m0)/ΔM⌋, büyüklük = Mc + kΔM, Mc = m0 + ΔM/2;
                   kestirici EQ-Live: b̂ = log10e/(M̄ − Mc + ΔM/2); T–M için r = Σk (tam sayı)
Ölçütler: kapsama (Wilson %95 MC aralığı), alttan/üstten kaçırma, genişlik, asimetri, sonsuz/başarısız uç sayısı.
Kullanım: python3 mc_kapsama.py [tekrar=20000] [tohum=20261021]
"""
import sys, json, math, time
import numpy as np
from scipy import stats, special
LOG10E = math.log10(math.e)
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20261021
NS = [4, 10, 20, 30, 40, 49, 100]; BS = [0.7, 1.0, 1.5]; DMS = [0.0, 0.1, 0.5]; ALPHA = 0.05

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

def methods(bhat, N, dm, r):
    out = {}
    s = bhat / np.sqrt(N); out['normal'] = (bhat - 1.96 * s, bhat + 1.96 * s)
    ql, qu = stats.chi2.ppf(ALPHA / 2, 2 * N), stats.chi2.ppf(1 - ALPHA / 2, 2 * N)
    out['chi2'] = (ql / (2 * N) * bhat, qu / (2 * N) * bhat)
    if dm > 0:
        pl = np.where(r > 0, special.betaincinv(np.maximum(r, 1), N, ALPHA / 2), 0.0)
        pu = 1 - special.betaincinv(N, r + 1, ALPHA / 2)
        with np.errstate(divide='ignore'):
            out['tm'] = (-np.log(pu) / dm * LOG10E, np.where(pl > 0, -np.log(pl) / dm * LOG10E, np.inf))
        k = 1.96; z = r / N; p = z / (z + 1); d = (1 - p) * np.sqrt(p / N); a, c = p - k * d, p + k * d
        with np.errstate(divide='ignore', invalid='ignore'):
            out['tm_ml'] = (np.where(c < 1, -np.log(np.minimum(c, 1 - 1e-300)) / dm * LOG10E, 0.0), np.where(a > 0, -np.log(np.maximum(a, 1e-300)) / dm * LOG10E, np.inf))
    return out

def run():
    rng = np.random.default_rng(SEED); res = []; t0 = time.time()
    for dm in DMS:
        for b in BS:
            beta = b / LOG10E
            for N in NS:
                x = rng.exponential(1 / beta, size=(REPS, N))      # m − m0
                if dm == 0:
                    bhat = LOG10E / x.mean(1); r = None
                else:
                    k = np.floor(x / dm); r = k.sum(1).astype(np.int64)
                    bhat = LOG10E / (dm * (k.mean(1) + 0.5))       # = log10e/(M̄ − Mc + ΔM/2)
                for name, (lo, hi) in methods(bhat, N, dm, r).items():
                    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
                    nan = ~(np.isfinite(lo)) | np.isnan(hi)
                    cov = (lo <= b) & (b <= hi) & ~nan; n_cov = int(cov.sum())
                    fin = np.isfinite(hi) & ~nan
                    dlo, dhi = bhat - lo, hi - bhat
                    asym = np.where(fin & (dlo > 0), dhi / np.where(dlo > 0, dlo, 1), np.nan)
                    wl, wu = wilson(n_cov, REPS)
                    res.append({'dM': dm, 'b': b, 'N': N, 'yontem': name, 'kapsama': n_cov / REPS, 'kapsama_mc95': [round(wl, 4), round(wu, 4)],
                                'alttan_kacirma': float((b < lo).mean()), 'ustten_kacirma': float((b > hi).mean()),
                                'genislik_ort': float(np.mean((hi - lo)[fin])) if fin.any() else None, 'genislik_ortanca': float(np.median((hi - lo)[fin])) if fin.any() else None,
                                'genislik_gorece_ortanca': float(np.median(((hi - lo) / b)[fin])) if fin.any() else None,
                                'asimetri_ortanca': float(np.nanmedian(asym)) if np.isfinite(asym).any() else None,
                                'ust_sonsuz': int((~np.isfinite(hi)).sum()), 'alt_negatif': int((lo < 0).sum()), 'hesaplanamayan': int(nan.sum()),
                                'bhat_ort_oran': float(bhat.mean() / b), 'bhat_ortanca_oran': float(np.median(bhat) / b)})
    meta = {'tekrar': REPS, 'tohum': SEED, 'alpha': ALPHA, 'N': NS, 'b': BS, 'dM': DMS, 'sure_s': round(time.time() - t0, 1),
            'not': 'Kestirici tüm yöntemlerde EQ-Live ile aynı; yalnız aralıklar karşılaştırılır. MC standart hatası ≈ √(0,95·0,05/tekrar).'}
    return meta, res

if __name__ == '__main__':
    meta, res = run()
    json.dump({'meta': meta, 'sonuc': res}, open('out/mc_kapsama.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(meta, ensure_ascii=False))
    for dm in DMS:
        print(f'\n=== ΔM = {dm}  (b = 1,0)   kapsama [MC %95]  | alttan/üstten kaçırma | göreli genişlik (ortanca) | asimetri | üst ∞')
        for N in NS:
            row = [r for r in res if r['dM'] == dm and r['b'] == 1.0 and r['N'] == N]
            print(f'N={N:>3} ' + ' || '.join(f"{r['yontem']}: {r['kapsama']:.3f} [{r['kapsama_mc95'][0]:.3f},{r['kapsama_mc95'][1]:.3f}] {r['alttan_kacirma']:.3f}/{r['ustten_kacirma']:.3f} w{r['genislik_gorece_ortanca'] if r['genislik_gorece_ortanca'] is None else round(r['genislik_gorece_ortanca'],2)} a{r['asimetri_ortanca'] if r['asimetri_ortanca'] is None else round(r['asimetri_ortanca'],2)} ∞{r['ust_sonsuz']}" for r in row))
