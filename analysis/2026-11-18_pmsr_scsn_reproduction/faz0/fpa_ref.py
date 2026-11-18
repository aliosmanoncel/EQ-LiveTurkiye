"""FPA Faz 0 — bağımsız ESR uygulaması (Khan vd. 2025 yöntem tanımından) ve statseis köprüsü.

Bağımsız uygulama yalnızca makaledeki tanıma dayanır:
  öncü penceresi W=20 gün, kalibrasyon 365→20 gün, 0,01 gün adımlı kayan pencere,
  p = (sayısı >= N_obs olan pencere oranı), p < 0,01 -> anlamlı.
"""
from collections import namedtuple
import datetime as dt
import numpy as np
import pandas as pd

W, C, STEP = 20.0, 365, 100  # gün, gün, 1/adım

def esr_independent(days_before, W=W, cut_off_day=C):
    """days_before: ana şoktan önceki olayların gün cinsinden uzaklıkları (>0), zaten R ve Mc filtreli."""
    d = np.sort(np.asarray(days_before, float))
    d = d[(d > 0) & (d < cut_off_day + W)]
    reg = d[d >= W]                       # kalibrasyon olayları
    n_obs = int(np.sum(d < W))            # öncü penceresi
    cut = min(int(cut_off_day), C)
    # pencere başlangıçları: W, W+0.01, ..., cut-W  (tamsayı/STEP ile tam)
    k = np.arange(int(W * STEP), int((cut - W) * STEP) + 1)
    pts = k / STEP
    # sayım: pts < d <= pts+W
    hi = np.searchsorted(reg, pts + W, side='right')
    lo = np.searchsorted(reg, pts, side='right')
    counts = hi - lo
    if counts.size == 0:
        p = 0.0 if n_obs > 0 else 1.0
        q99 = np.nan
    else:
        p = float(np.mean(counts >= n_obs))
        q99 = float(np.percentile(counts, 99))
    return dict(n_obs=n_obs, p=p, q99=q99, n_windows=int(counts.size),
                max_window=int(counts.max()) if counts.size else np.nan,
                median=float(np.median(counts)) if counts.size else np.nan,
                n_regular=int(reg.size))

MS = namedtuple('MS', 'ID LON LAT DATETIME Mc MAGNITUDE DEPTH')
T0 = dt.datetime(2020, 1, 1)

def to_statseis(days_before, dist_km=None, cat_start_days=800.0, t_ms=None):
    """Sentetik bir 'gün önce' listesini statseis ESR_model girdilerine çevirir."""
    t_ms = t_ms or T0 + dt.timedelta(days=cat_start_days)
    d = np.asarray(days_before, float)
    dist = np.full(d.size, 1.0) if dist_km is None else np.asarray(dist_km, float)
    local = pd.DataFrame({'ID': [f'e{i}' for i in range(d.size)],
                          'DATETIME': [t_ms - dt.timedelta(days=float(x)) for x in d],
                          'DAYS_TO_MAINSHOCK': d, 'DISTANCE_TO_MAINSHOCK': dist,
                          'MAGNITUDE': 2.0, 'LON': 0.0, 'LAT': 0.0, 'DEPTH': 10.0})
    cat = pd.DataFrame({'DATETIME': [T0]})
    ms = MS('MS', 0.0, 0.0, t_ms, 1.0, 5.0, 10.0)
    return ms, cat, local

def esr_statseis(days_before, **kw):
    from statseis.foreshocks import ESR_model
    ms, cat, local = to_statseis(days_before, **kw)
    r, _, _ = ESR_model(ms, cat, local)
    return dict(n_obs=r['n_events_in_foreshock_window'], p=r['ESR'], q99=r['ESR_99CI'],
                max_window=r['max_20day_rate'], median=r['ESR_median'],
                n_regular=r['n_regular_seismicity_events'])
