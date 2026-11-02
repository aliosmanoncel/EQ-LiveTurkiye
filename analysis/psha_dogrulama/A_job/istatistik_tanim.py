"""Aşama A ek denetimi: mantık ağacı istatistiklerinin TANIMI. Ortalama ve yüzdelik iki uzayda hesaplanır ve ikisi de korunur:
  λ uzayı  : λ̄ = Σ wᵢ λᵢ ; yüzdelik λ değerleri üzerinde        (mevcut kod)
  PoE uzayı: P̄(T) = Σ wᵢ Pᵢ(T), Pᵢ = 1 − e^(−λᵢT) ; yüzdelik PoE üzerinde, T = 50 yıl   (OpenQuake hcurves-stats)
Yüzdelik algoritması iki yazılımda AYNI (openquake.hazardlib.stats.quantile_curve ile kodun döngüsü): her IM düzeyinde dalları değere göre
artan sırala → ağırlıkların kümülatif toplamı (cumsum) → numpy.interp(q, kümülatif ağırlık, sıralı değer), yani kümülatif ağırlığa göre
doğrusal ara değer; uç kural: q ilk kümülatif ağırlıktan küçükse en küçük değer. Fark yalnız ara değerin hangi uzayda yapıldığından gelir.
Girdi: lt/lam_job.npz (motor gerçekleşmeleri), referans_kod.npz, asamaA_sonuc.json. Çıktı: istatistik_tanim.json."""
import os, json, math, numpy as np
from openquake.hazardlib.stats import quantile_curve
from openquake.commonlib import datastore
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
R = np.load(os.path.join(P, 'referans_kod.npz')); J = np.load(os.path.join(H, 'lt', 'lam_job.npz')); A = json.load(open(os.path.join(H, 'asamaA_sonuc.json')))
x = R['psha_x_im']; T = 50.0
ds = datastore.read(A['joblar']['lt']['calc_id']); w = np.array([float(r.weight[0]) for r in ds['full_lt'].get_realizations()]); ds.close()
lam = J['rlz']; Pp = -np.expm1(-lam * T); toL = lambda p: -np.log1p(-np.minimum(p, 1 - 1e-16)) / T
def pga(lt, c):
    v = c > 1e-12
    if lt < c[v][-1] or lt > c[v][0]: return float('nan')
    return float(np.exp(np.interp(np.log(lt), np.log(c[v][::-1]), np.log(x[v][::-1]))))
out = {'tanim': __doc__.split('Girdi:')[0].strip(), 'senaryo': {}}
for ad, p in (('%50/50', 0.50), ('%10/50', 0.10), ('%2/50', 0.02)):
    lt = -math.log(1 - p) / T; r = {'ortalama': {'lambda_uzayi': pga(lt, w @ lam), 'poe_uzayi': pga(lt, toL(w @ Pp)), 'kod': pga(lt, R['lt_lam_mean']), 'motor_istatistik': pga(lt, J['mean'])}}
    for i, q in enumerate((0.05, 0.16, 0.50, 0.84, 0.95)):
        r[f'q{q}'] = {'lambda_uzayi': pga(lt, quantile_curve(q, lam, w)), 'poe_uzayi': pga(lt, toL(quantile_curve(q, Pp, w))), 'kod': pga(lt, R['lt_frac_curves'][i]), 'motor_istatistik': pga(lt, J['q'][i])}
    out['senaryo'][ad] = r
json.dump(out, open(os.path.join(H, 'istatistik_tanim.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for ad, r in out['senaryo'].items():
    print(ad, ' | '.join(f"{k}: λ {v['lambda_uzayi']:.5f} / PoE {v['poe_uzayi']:.5f} (kod {v['kod']:.5f}, motor {v['motor_istatistik']:.5f})" for k, v in r.items()))
