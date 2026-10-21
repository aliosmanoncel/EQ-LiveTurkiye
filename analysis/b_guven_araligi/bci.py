"""
b-değeri güven aralığı yöntemleri (yalnız analiz; EQ-Live üretim kodu DEĞİŞMEZ).
Kestirici her yöntemde EQ-Live ile aynıdır (index.html computeBvalue):
    b̂ = log10(e) / (M̄ − Mc + ΔM/2)    (Aki 1965 + Utsu 1966 ΔM/2; sürekli veride ΔM = 0)
Mc: en küçük sınıfın değeri (sınıf merkezi); m0 = Mc − ΔM/2 sınıfın alt sınırı.
Yöntemler:
  normal : b̂ ± 1,96·b̂/√N  (EQ-Live, index.html bConfidence95)
  chi2   : Utsu (1966) / Shi & Bolt (1982); Tinti & Mulargia (1987) Eş. 4a–4b:
           q_l/(2N)·b̂ ≤ b ≤ q_u/(2N)·b̂,  q: χ²_{2N} yüzdelikleri. Sürekli büyüklükler için kesin.
  tm     : Tinti & Mulargia (1987) Eş. 9–21, 19: gruplanmış büyüklükler (geometrik dağılım).
           z = (M̄ − m0)/ΔM − 0,5 ; r = N·z (tam sayı) ; p = exp(−βΔM)
           I_{p_l}(r, N) = α/2 (r ≥ 1; r = 0 → p_l = 0) ; I_{q_u}(N, r+1) = α/2, p_u = 1 − q_u
           β_l = −ln(p_u)/ΔM ; β_u = −ln(p_l)/ΔM ; b = β·log10(e)
  tm_ml  : aynı makalenin Eş. 23 asimptotik (ML) yaklaşımı — yalnız karşılaştırma için.
"""
import math
import numpy as np
from scipy import stats, special

LOG10E = math.log10(math.e)

def b_eqlive(mags, Mc, dm):
    m = np.asarray(mags, float); m = m[m >= Mc - 1e-9]
    den = m.mean() - Mc + dm / 2
    return (LOG10E / den if den > 0 else float('nan')), len(m), m.mean()

def ci_normal(b, N, alpha=0.05):
    k = 1.96 if alpha == 0.05 else stats.norm.ppf(1 - alpha / 2)   # EQ-Live sabiti 1.96 (bConfidence95)
    s = b / math.sqrt(N)
    return b - k * s, b + k * s

def ci_chi2(b, N, alpha=0.05):
    ql, qu = stats.chi2.ppf(alpha / 2, 2 * N), stats.chi2.ppf(1 - alpha / 2, 2 * N)
    return ql / (2 * N) * b, qu / (2 * N) * b

def tm_r(mbar, Mc, dm, N):
    """r = N·z, z = (M̄ − m0)/ΔM − 0,5, m0 = Mc − ΔM/2 → z = (M̄ − Mc)/ΔM. Tam sayıya yuvarlanır (sınıf indeksi toplamı)."""
    z = (mbar - Mc) / dm
    return int(round(N * z))

def ci_tm(N, r, dm, alpha=0.05):
    """Tinti & Mulargia (1987) Eş. 21 → 19. Dönüş: (b_l, b_u); r = 0 ise b_u = +inf."""
    p_l = 0.0 if r == 0 else special.betaincinv(r, N, alpha / 2)
    q_u = special.betaincinv(N, r + 1, alpha / 2); p_u = 1 - q_u
    b_l = -math.log(p_u) / dm * LOG10E
    b_u = math.inf if p_l <= 0 else -math.log(p_l) / dm * LOG10E
    return b_l, b_u

def ci_tm_ml(N, r, dm, alpha=0.05):
    """Eş. 23: p̂ ± k·(1−p̂)√(p̂/N); p̂ = z/(z+1)."""
    k = stats.norm.ppf(1 - alpha / 2); z = r / N; p = z / (z + 1); d = (1 - p) * math.sqrt(p / N)
    pl, pu = p - k * d, p + k * d
    b_l = -math.log(pu) / dm * LOG10E if pu < 1 else 0.0
    b_u = -math.log(pl) / dm * LOG10E if pl > 0 else math.inf
    return b_l, b_u
