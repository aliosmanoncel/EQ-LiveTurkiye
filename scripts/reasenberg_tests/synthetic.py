"""
synthetic.py
============

Synthetic catalogs with KNOWN clustering structure, for validating
declustering codes.

simulate_branching(...) generates a simple space-time branching
(ETAS-like) catalog:
  * background: homogeneous Poisson in time and in a lat/lon box
  * magnitudes: Gutenberg-Richter, b-value b, above m_min (continuous)
  * productivity: Poisson(K * 10**(alpha * (M - m_min))) direct offspring
  * offspring times: modified Omori, pdf ~ (t + c)**-p_omori, truncated at t_max_days
  * offspring locations: isotropic Gaussian, sigma = s0 * 10**(0.5 * (M - m_min)) km
  * depths: background U(dmin, dmax); offspring = parent depth + N(0, 2 km), clipped

Ground truth returned for every event:
  parent  : index of direct parent (-1 for background)
  family  : index of the background ancestor of the event's family
  is_background

Branching ratio n = K * b / (b - alpha) must be < 1 (checked).
This is a validation tool, not a physical model of Turkish seismicity.
"""

from __future__ import annotations

import numpy as np

KM_PER_DEG = 111.195


def _omori_times(rng, size, c, p, t_max):
    # inverse-CDF sampling of (t + c)^-p on [0, t_max], p != 1
    u = rng.uniform(size=size)
    q = 1.0 - p
    lo, hi = c ** q, (t_max + c) ** q
    return (lo + u * (hi - lo)) ** (1.0 / q) - c


def simulate_branching(
    seed=0,
    duration_days=3650.0,
    n_background=1500,
    lat_range=(37.0, 41.0),
    lon_range=(27.0, 43.0),
    depth_range=(5.0, 20.0),
    m_min=2.5,
    b=1.0,
    K=0.08,
    alpha=0.8,
    c=0.01,
    p_omori=1.2,
    t_max_days=365.0,
    s0=0.5,
    max_generations=20,
    forced_events=None,
):
    """forced_events: optional list of (t_days, lat, lon, depth, M) added as
    background events (e.g. one large earthquake); triggering applies to them."""
    rng = np.random.default_rng(seed)
    if K * b / (b - alpha) >= 1.0:
        raise ValueError("Supercritical branching (n >= 1).")
    beta = b * np.log(10.0)

    def gr(size):
        return m_min + rng.exponential(1.0 / beta, size)

    t = list(rng.uniform(0, duration_days, n_background))
    lat = list(rng.uniform(*lat_range, n_background))
    lon = list(rng.uniform(*lon_range, n_background))
    dep = list(rng.uniform(*depth_range, n_background))
    mag = list(gr(n_background))
    for ev in forced_events or []:
        for lst, v in zip((t, lat, lon, dep, mag), ev):
            lst.append(float(v))
    n_background = len(t)
    parent = [-1] * n_background
    family = list(range(n_background))

    gen_start, gen_end = 0, n_background
    for _ in range(max_generations):
        new = 0
        for k in range(gen_start, gen_end):
            nk = rng.poisson(K * 10.0 ** (alpha * (mag[k] - m_min)))
            if nk == 0:
                continue
            dt = _omori_times(rng, nk, c, p_omori, t_max_days)
            sigma = s0 * 10.0 ** (0.5 * (mag[k] - m_min))
            dx, dy = rng.normal(0, sigma, nk), rng.normal(0, sigma, nk)
            for q in range(nk):
                tq = t[k] + dt[q]
                if tq > duration_days:
                    continue
                t.append(tq)
                lat.append(lat[k] + dy[q] / KM_PER_DEG)
                lon.append(lon[k] + dx[q] / (KM_PER_DEG * np.cos(np.radians(lat[k]))))
                dep.append(float(np.clip(dep[k] + rng.normal(0, 2.0), 0.5, 40.0)))
                mag.append(float(gr(1)[0]))
                parent.append(k)
                family.append(family[k])
                new += 1
        if new == 0:
            break
        gen_start, gen_end = gen_end, gen_end + new

    t, lat, lon, dep, mag = map(np.asarray, (t, lat, lon, dep, mag))
    parent, family = np.asarray(parent), np.asarray(family)
    order = np.argsort(t, kind="stable")
    inv = np.empty_like(order)
    inv[order] = np.arange(order.size)
    parent_s = np.where(parent[order] >= 0, inv[np.maximum(parent[order], 0)], -1)
    family_s = inv[family[order]]
    return {
        "t": t[order], "lat": lat[order], "lon": lon[order],
        "depth": dep[order], "mag": mag[order],
        "parent": parent_s, "family": family_s,
        "is_background": parent_s < 0,
        "m_min": m_min, "b": b,
    }


def b_value_mle(mags, m_c, dm=0.0):
    """Aki (1965) / Utsu (1966) MLE with Shi & Bolt (1982) standard error.

    dm = magnitude bin width (0 for continuous magnitudes).
    """
    x = np.asarray(mags, float)
    x = x[x >= m_c - 1e-9]
    nn = x.size
    if nn < 2:
        return np.nan, np.nan, nn
    b = np.log10(np.e) / (x.mean() - (m_c - dm / 2.0))
    se = 2.30 * b ** 2 * np.sqrt(np.sum((x - x.mean()) ** 2) / (nn * (nn - 1)))
    return b, se, nn
