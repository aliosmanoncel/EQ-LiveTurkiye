"""Stage-3 tests derived line by line from cluster2000x.f (user-supplied copy,
sha256 77d95ad9e4cdf33bc140d0419566f8def3d3f3a8de510edf77f256f13f1807a1)."""

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reasenberg import QUALITY_ERRORS_KM, delaz_km, reasenberg  # noqa: E402

warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*")


def run(t, x, m, **kw):
    n = len(t)
    kw.setdefault("xmeff", 2.5)
    return reasenberg(np.asarray(t, float), np.asarray(x, float), np.zeros(n),
                      np.full(n, 10.0), np.asarray(m, float), coords="cartesian",
                      rule="cluster2000x", **kw)


# ---------------------------------------------------------------- DELAZ (1027-1072)
def test_delaz_identical_points_zero():
    assert delaz_km(38.0, 35.0, 38.0, 35.0) == 0.0


def test_delaz_symmetric_and_close_to_haversine():
    d1 = delaz_km(38.0, 27.0, 38.1, 27.2)
    d2 = delaz_km(38.1, 27.2, 38.0, 27.0)
    assert d1 == pytest.approx(d2, rel=1e-9)
    lat1, lon1, lat2, lon2 = map(np.radians, (38.0, 27.0, 38.1, 27.2))
    h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    hav = 2 * 6371.0 * np.arcsin(np.sqrt(h))
    assert d1 == pytest.approx(hav, rel=5e-3)


def test_geographic_cluster2000x_uses_delaz():
    # two events 0.01 deg apart in latitude; link decided at a distance set
    # between the delaz and haversine values would differ -> just check use
    lat = np.array([38.0, 38.0 + 0.0158])
    d = delaz_km(lat[0], 35.0, lat[1], 35.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = reasenberg([0.0, 0.1], lat, [35.0, 35.0], [10.0, 10.0], [3.0, 3.0],
                       xmeff=2.5, rule="cluster2000x")
    rtest = 10 * 0.011 * 10 ** 1.2 + 0.011
    assert bool(r.n_clusters == 1) == (d <= rtest)


# ---------------------------------------------------------------- cmag1(0) term (385, 928)
@pytest.mark.parametrize("cmag0,linked", [(0.0, True), (-10.0, False)])
def test_unclustered_rmain_term(cmag0, linked):
    # M3 pair 1.750 km apart: 10 r(3) = 1.7434 < 1.750 <= 1.7434 + 0.011 = 1.7544
    r = run([0.0, 0.1], [0.0, 1.750], [3.0, 3.0], cmag_unclustered=cmag0)
    assert bool(r.n_clusters == 1) == linked


# ---------------------------------------------------------------- dM has no floor (349-352)
def test_look_ahead_floor_switch():
    from reasenberg import look_ahead_time_days
    # M_max 2.6, xmeff 1.5 -> dM = -0.2
    with_floor = look_ahead_time_days(2.6, 0.3, 0.5, 1.5, 0.99)
    no_floor = look_ahead_time_days(2.6, 0.3, 0.5, 1.5, 0.99, floor_dm=False)
    assert no_floor == pytest.approx(-np.log(0.01) * 0.3 / 10 ** (2 * (-0.2 - 1) / 3))
    assert no_floor > with_floor


@pytest.mark.parametrize("rule,linked", [("cluster2000x", True), ("zmap", False)])
def test_negative_dm_extends_window_only_in_cluster2000x(rule, linked):
    # largest M2.6; i at +0.3 d (0.2 km); j 7.5 d after i (0.3 km from i).
    # tau_i: no floor 8.72 d (cluster2000x) vs floor 6.41 d (zmap).
    # Regression: found by the transliteration cross-check (stage 3).
    t, x, m = [0.0, 0.3, 7.8], [0.0, 0.2, 0.5], [2.6, 2.5, 2.5]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = reasenberg(t, x, [0, 0, 0], [10, 10, 10], m, coords="cartesian", rule=rule,
                       xmeff=1.5, p=0.99, tau0=2.0, tau_min=2.0, tau_max=10.0)
    assert bool(r.cluster_id[2] == r.cluster_id[0] >= 0) == linked


# ---------------------------------------------------------------- quality codes (889-910)
def test_quality_table_values():
    assert QUALITY_ERRORS_KM["A"] == (0.5, 1.0) and QUALITY_ERRORS_KM["D"] == (5.0, 10.0)


def test_quality_code_of_first_event_triggers_table_for_both():
    # 3 km horizontal, M2.5 (rtest 1.111). i='A' -> erh_i 0.5; j blank -> 'D' -> erh_j 5
    # d = 3 - 0.5 - 5 < 1.111 -> linked
    assert run([0.0, 0.1], [0.0, 3.0], [2.5, 2.5], quality=["A", " "]).n_clusters == 1


def test_blank_quality_of_first_event_leaves_errors_unchanged():
    # line 889 tests only q1: i blank -> no table, input errors (0) -> d = 3 -> not linked
    assert run([0.0, 0.1], [0.0, 3.0], [2.5, 2.5], quality=[" ", "A"]).n_clusters == 0
