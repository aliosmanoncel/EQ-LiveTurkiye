"""Unit and property tests for reasenberg.py (run: pytest -q)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reasenberg import (  # noqa: E402
    DEPENDENT, REPRESENTATIVE, SINGLE, _Distance,
    interaction_radius_km, look_ahead_time_days, reasenberg,
)
from synthetic import simulate_branching  # noqa: E402

CART = dict(coords="cartesian", xmeff=2.0)


def run_cart(t, x, m, **kw):
    n = len(t)
    opts = {**CART, **kw}
    t = np.asarray(t)
    t = t if np.issubdtype(t.dtype, np.datetime64) else t.astype(float)
    return reasenberg(t, np.asarray(x, float), np.zeros(n),
                      np.full(n, 10.0), np.asarray(m, float), **opts)


# ---------------------------------------------------------------- formulas
def test_interaction_radius():
    # log10 r = 0.4 M - 1.959  ->  r(5) = 10**0.041 = 1.099 km
    assert interaction_radius_km(5.0) == pytest.approx(0.011 * 10 ** 2.0, rel=1e-12)
    assert interaction_radius_km(5.0) == pytest.approx(10 ** (0.4 * 5 - 1.959), rel=2e-3)


def test_look_ahead_time():
    # dM = 0.5*5 - 2 = 0.5 ; tau = -ln(0.05) * 2 / 10**(-1/3)
    expected = -np.log(0.05) * 2.0 / 10 ** (2 * (0.5 - 1) / 3)
    assert look_ahead_time_days(5.0, 2.0, 0.5, 2.0, 0.95) == pytest.approx(expected)
    # dM floored at 0
    assert look_ahead_time_days(3.0, 1.0, 0.5, 2.0, 0.95) == pytest.approx(
        -np.log(0.05) / 10 ** (-2 / 3))


# ---------------------------------------------------------------- distances
def test_geographic_distance_no_projection_artifact():
    # same 0.1 deg longitude separation at lat 39 in western and eastern Turkey
    lat = np.array([39.0, 39.0, 39.0, 39.0])
    lon = np.array([27.0, 27.1, 44.0, 44.1])
    d = _Distance(lat, lon, np.zeros(4), None, None, 1.5, "geographic")
    d_west, d_east = d(0, np.array([1]))[0], d(2, np.array([3]))[0]
    assert d_west == pytest.approx(d_east, rel=1e-12)
    assert d_west == pytest.approx(0.1 * 111.195 * np.cos(np.radians(39)), rel=1e-3)


def test_location_error_correction():
    # two M2.5 events 3 km apart: link radius rfact*r = 1.10 km
    t, x, m = [0.0, 0.1], [0.0, 3.0], [2.5, 2.5]
    assert run_cart(t, x, m, xmeff=2.5).n_clusters == 0
    # 3 - 1.5*1.5 = 0.75 km <= 1.10 km
    assert run_cart(t, x, m, xmeff=2.5, err=1.5).n_clusters == 1


# ---------------------------------------------------------------- algorithm cases
def test_isolated_events_are_single():
    r = run_cart([0, 0.5, 1.0], [0, 50, 100], [3.0, 3.0, 3.0])
    assert r.n_clusters == 0
    assert np.all(r.event_class == SINGLE)
    assert np.all(r.cluster_id == -1)


def test_doublet_with_single_event_in_window_is_linked():
    # Regression for ZMAP7 timediff(): window with exactly one event returned []
    r = run_cart([0.0, 0.5], [0.0, 0.5], [3.0, 3.0])
    assert r.n_clusters == 1
    assert r.event_class.tolist() == [REPRESENTATIVE, DEPENDENT]


def test_time_window_upper_bound_is_strict():
    # unclustered event: tau = tau_min = 1 day; event exactly at +1 day is outside
    assert run_cart([0.0, 1.0], [0.0, 0.1], [3.0, 3.0]).n_clusters == 0
    assert run_cart([0.0, 0.999], [0.0, 0.1], [3.0, 3.0]).n_clusters == 1


@pytest.mark.parametrize("tie,expected_rep", [("first", 0), ("last", 1)])
def test_tie_rule(tie, expected_rep):
    r = run_cart([0.0, 0.1], [0.0, 0.5], [3.0, 3.0], tie=tie)
    assert r.representative.tolist() == [expected_rep]


def merge_case():
    """Two clusters bridged by a later link; the larger event is in the
    cluster formed SECOND.

        A t=0.00 M3.5 x=0    -> links C            cluster X = {A, C}
        B t=0.01 M4.5 x=10   -> links D            cluster Y = {B, D}
        C t=0.02 M3.0 x=2    -> links D (1.6 km)   X and Y must merge
        D t=0.03 M3.0 x=3.6
    Link radii: A 2.76 km, B 6.94 km, C 1.75 km.
    """
    return [0.00, 0.01, 0.02, 0.03], [0.0, 10.0, 2.0, 3.6], [3.5, 4.5, 3.0, 3.0]


def test_merge_keeps_largest_event_as_representative():
    # Regression for: bruces 0.5.0 keeps A (M3.5); ZMAP7 GUI does not merge.
    r = run_cart(*merge_case())
    assert r.n_merges == 1
    assert r.n_clusters == 1
    assert r.cluster_id.tolist() == [0, 0, 0, 0]
    assert r.representative.tolist() == [1]  # B, M4.5
    assert r.event_class.tolist() == [DEPENDENT, REPRESENTATIVE, DEPENDENT, DEPENDENT]


def joint_link_case():
    """Unclustered event C links to an unclustered D and to E (already in A's cluster).

        A t=0.00 M4.3 (0,0)     link r 5.77 km -> links E (5.5 km)
        C t=0.02 M2.9 (6.5,1)   link r 1.59 km -> links D (1.0) and E (1.41)
        D t=0.05 M3.0 (7.5,1)
        E t=0.10 M2.9 (5.5,0)
    Correct: one cluster {A,C,D,E}, representative A, no merge needed.
    """
    t = [0.00, 0.02, 0.05, 0.10]
    x = [0.0, 6.5, 7.5, 5.5]
    y = [0.0, 1.0, 1.0, 0.0]
    m = [4.3, 2.9, 3.0, 2.9]
    return t, x, y, m


def test_joint_evaluation_of_links_avoids_spurious_merge():
    t, x, y, m = map(np.asarray, joint_link_case())
    r = reasenberg(t, x, y, np.full(4, 10.0), m, xmeff=2.0, coords="cartesian")
    assert r.n_merges == 0
    assert r.cluster_id.tolist() == [0, 0, 0, 0]
    assert r.representative.tolist() == [0]


def test_bruces_joint_link_behaviour_documented():
    bruces = pytest.importorskip("bruces")
    t, x, y, m = map(np.asarray, joint_link_case())
    cat = bruces.Catalog(origin_times=2020 + t / 365.25, eastings=x, northings=y,
                         depths=np.full(4, 10.0), magnitudes=m)
    idx = cat.decluster("reasenberg", return_indices=True, xmeff=2.0)
    # bruces 0.5.0 opens {C, D}, merges with {A, E}, and keeps D (M3.0) instead of A (M4.3)
    assert idx.tolist() == [2]


def test_input_order_invariance():
    t, x, m = map(np.asarray, merge_case())
    perm = np.array([2, 0, 3, 1])
    r0 = run_cart(t, x, m)
    r1 = run_cart(t[perm], x[perm], m[perm])
    assert np.array_equal(r1.event_class, r0.event_class[perm])
    assert np.array_equal(r1.cluster_id, r0.cluster_id[perm])
    assert perm[r1.representative[0]] == r0.representative[0]


def test_datetime_input_equals_days_input():
    t, x, m = merge_case()
    t64 = np.datetime64("2023-02-06T01:17") + (np.asarray(t) * 86400e3).astype("timedelta64[ms]")
    r_days = run_cart(t, x, m)
    r_dt = run_cart(t64, x, m)
    assert np.array_equal(r_days.cluster_id, r_dt.cluster_id)


def test_xmeff_is_required():
    with pytest.raises(TypeError):
        reasenberg([0, 1], [0, 0], [0, 0], [10, 10], [3, 3])


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        run_cart([0, 1], [0, 0], [3, 3], p=1.0)
    with pytest.raises(ValueError):
        run_cart([0, 1], [0, 0], [3, 3], tau_min=5, tau_max=1)
    with pytest.raises(ValueError):
        run_cart([0, np.nan], [0, 0], [3, 3])


def test_warns_when_events_below_xmeff():
    with pytest.warns(UserWarning):
        run_cart([0, 1], [0, 50], [2.0, 3.0], xmeff=2.5)


# ---------------------------------------------------------------- properties on synthetic catalogs
@pytest.fixture(scope="module", params=[0, 1, 2, 3])
def synthetic_result(request):
    cat = simulate_branching(seed=request.param)
    res = reasenberg(cat["t"], cat["lat"], cat["lon"], cat["depth"], cat["mag"],
                     xmeff=cat["m_min"])
    return cat, res


def test_invariants(synthetic_result):
    cat, r = synthetic_result
    m = cat["mag"]
    # classes consistent with cluster ids
    assert np.all((r.cluster_id == -1) == (r.event_class == SINGLE))
    # cluster ids contiguous, every cluster has >= 2 members
    assert set(np.unique(r.cluster_id[r.cluster_id >= 0])) == set(range(r.n_clusters))
    assert np.all(r.cluster_sizes >= 2)
    # exactly one representative per cluster, and it is the largest event
    assert np.sum(r.event_class == REPRESENTATIVE) == r.n_clusters
    for k, rep in enumerate(r.representative):
        assert r.cluster_id[rep] == k
        assert m[rep] == m[r.cluster_id == k].max()
    # bookkeeping
    assert r.independent.sum() == np.sum(r.event_class == SINGLE) + r.n_clusters


def test_deterministic(synthetic_result):
    cat, r = synthetic_result
    r2 = reasenberg(cat["t"], cat["lat"], cat["lon"], cat["depth"], cat["mag"],
                    xmeff=cat["m_min"])
    assert np.array_equal(r.cluster_id, r2.cluster_id)


def test_background_mostly_independent(synthetic_result):
    # Most true background events must be classified as independent.
    # Threshold is a sanity bound, not a performance claim (see validate.py).
    cat, r = synthetic_result
    assert r.independent[cat["is_background"]].mean() > 0.9


# ---------------------------------------------------------------- documented third-party behaviour
def test_bruces_merge_behaviour_documented():
    bruces = pytest.importorskip("bruces")
    t, x, m = map(np.asarray, merge_case())
    cat = bruces.Catalog(origin_times=2020 + t / 365.25, eastings=x, northings=np.zeros(4),
                         depths=np.full(4, 10.0), magnitudes=m)
    idx = cat.decluster("reasenberg", return_indices=True, xmeff=2.0)
    # bruces 0.5.0 keeps A (M3.5), not B (M4.5), after merging X and Y
    assert idx.tolist() == [0]
