"""Stage-2 tests: boundary cases and the cluster2000x linking rule.

Geometry: Cartesian km, all depths 10 km unless stated. Link radii used below
(r = 0.011 * 10**(0.4 M) km):
    M2.5: r = 0.110, 10r = 1.10     M3.0: r = 0.175, 10r = 1.75
    M3.5: r = 0.276, 10r = 2.76     M4.5: r = 0.694, 10r = 6.94
    M5.0: r = 1.100, 10r = 11.0     M6.0: r = 2.765, 10r = 27.65
    M7.0: r = 6.945, 10r = 69.45
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reasenberg import (  # noqa: E402
    CLUSTER2000X_DEFAULTS, DEPENDENT, REPRESENTATIVE, SINGLE,
    equivalent_events, look_ahead_time_days, reasenberg,
)
from synthetic import simulate_branching  # noqa: E402

RULES = ["zmap", "cluster2000x"]
# common timing so that both rules see the same windows
TIMING = dict(tau0=2.0, tau_min=2.0, tau_max=10.0, p=0.99)


def run(t, x, y, m, z=None, **kw):
    n = len(t)
    z = np.full(n, 10.0) if z is None else np.asarray(z, float)
    kw.setdefault("xmeff", 2.0)
    return reasenberg(np.asarray(t, float), np.asarray(x, float), np.asarray(y, float),
                      z, np.asarray(m, float), coords="cartesian", **kw)


# ============================================================ 1. converging clusters
def converging_clusters():
    # X = {A, C} forms first, Y = {B, D} second; C links D -> X and Y merge
    t = [0.00, 0.01, 0.02, 0.03]
    x = [0.0, 10.0, 2.0, 3.6]
    m = [3.5, 4.5, 3.0, 3.0]
    return t, x, [0, 0, 0, 0], m


@pytest.mark.parametrize("rule", RULES)
def test_converging_clusters_merge_and_keep_largest(rule):
    r = run(*converging_clusters(), rule=rule)
    assert r.n_clusters == 1 and r.n_merges == 1
    assert r.cluster_id.tolist() == [0, 0, 0, 0]
    assert r.representative.tolist() == [1]          # B, M4.5, from the LATER cluster


# ============================================================ 2. one event, several clusters
def three_clusters_bridged():
    # pairs P (x=-5), Q (x=+5), R (y=+5) form first; each has a later member;
    # E (M4.5, origin) occurs between and links all three later members (5 km < 6.94)
    t = [0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.10, 0.20, 0.21, 0.22]
    x = [-5, -5.5, 5, 5.5, 0, 0, 0, -5, 5, 0]
    y = [0, 0, 0, 0, 5, 5.5, 0, 0, 0, 5]
    m = [3.0] * 6 + [4.5] + [3.0] * 3
    return t, x, y, m


@pytest.mark.parametrize("rule", RULES)
def test_event_linking_three_clusters(rule):
    r = run(*three_clusters_bridged(), rule=rule)
    assert r.n_clusters == 1
    assert r.n_merges == 2
    assert np.all(r.cluster_id == 0)
    assert r.representative.tolist() == [6]          # E


@pytest.mark.parametrize("rule", RULES)
def test_bridging_event_absent_keeps_clusters_separate(rule):
    t, x, y, m = map(np.asarray, three_clusters_bridged())
    keep = np.arange(10) != 6
    r = run(t[keep], x[keep], y[keep], m[keep], rule=rule)
    assert r.n_clusters == 3 and r.n_merges == 0


def joint_link_case():
    t = [0.00, 0.02, 0.05, 0.10]
    x = [0.0, 6.5, 7.5, 5.5]
    y = [0.0, 1.0, 1.0, 0.0]
    m = [4.3, 2.9, 3.0, 2.9]
    return t, x, y, m


def test_cluster2000x_sequential_links_give_same_membership_as_joint():
    rz = run(*joint_link_case(), rule="zmap")
    rc = run(*joint_link_case(), rule="cluster2000x")
    assert rz.n_merges == 0 and rc.n_merges == 1       # different path ...
    assert np.array_equal(rz.cluster_id, rc.cluster_id)  # ... same membership
    assert rc.representative.tolist() == [0]           # correct merge keeps A


# ============================================================ 3. equal-magnitude candidates
@pytest.mark.parametrize("rule", RULES)
@pytest.mark.parametrize("tie,expected", [("first", 0), ("last", 1)])
def test_tie_rule_both_rules(rule, tie, expected):
    r = run([0.0, 0.1], [0.0, 0.5], [0, 0], [3.0, 3.0], rule=rule, tie=tie)
    assert r.representative.tolist() == [expected]


@pytest.mark.parametrize("tie,expected", [("first", 0), ("last", 1)])
def test_tie_between_merged_clusters(tie, expected):
    # converging clusters with equal maxima (A and B both M4.5).
    # A links C (6 <= 6.94); after that A's rtest = 6.94 + r(4.5) = 7.63 < A-D = 8.
    # B links D (6 <= 6.94) but not C (8). C links D: 2 <= 1.75 + 0.69 -> merge.
    t = [0.00, 0.01, 0.02, 0.03]
    x = [0.0, 14.0, 6.0, 8.0]
    m = [4.5, 4.5, 3.0, 3.0]
    r = run(t, x, [0] * 4, m, rule="cluster2000x", tie=tie)
    assert r.n_clusters == 1 and r.n_merges == 1
    assert r.representative.tolist() == [expected]


# ============================================================ 4. time-window boundaries
def test_zmap_window_upper_bound_strict():
    assert run([0.0, 2.0], [0, 0.1], [0, 0], [3, 3], rule="zmap", **TIMING).n_clusters == 0


def test_cluster2000x_window_upper_bound_inclusive():
    # Fortran: 'if (dif .gt. tau) goto 400'  ->  dif == tau is inside
    assert run([0.0, 2.0], [0, 0.1], [0, 0], [3, 3], rule="cluster2000x",
               **TIMING).n_clusters == 1
    assert run([0.0, 2.001], [0, 0.1], [0, 0], [3, 3], rule="cluster2000x",
               **TIMING).n_clusters == 0


@pytest.mark.parametrize("dt_j,linked", [(10.0, True), (10.001, False)])
def test_clustered_window_at_tau_max(dt_j, linked):
    # big M5 at t=0; a1 at t=2 (edge of big's tau0 window, linked);
    # a1: dt=2 d, tau formula = 19.8 d -> clipped to tau_max = 10 d
    t = [0.0, 2.0, 2.0 + dt_j]
    x = [0.0, 0.1, 0.2]
    m = [5.0, 3.0, 3.0]
    r = run(t, x, [0, 0, 0], m, rule="cluster2000x", **TIMING)
    assert bool(r.cluster_id[2] == 0) == linked
    assert r.cluster_id[1] == 0


# ============================================================ 5. location uncertainties
@pytest.mark.parametrize("erh,linked", [([1.0, 0.95], True), ([1.0, 0.85], False)])
def test_cluster2000x_horizontal_error_correction(erh, linked):
    # two M2.5, 3 km apart horizontally: d = 3 - erh_i - erh_j
    # vs rtest = 10 r(2.5) + r(cmag1(0)=0) = 1.100 + 0.011 = 1.111
    r = run([0.0, 0.1], [0.0, 3.0], [0, 0], [2.5, 2.5], xmeff=2.5,
            rule="cluster2000x", err=erh, derr=[0.0, 0.0])
    assert bool(r.n_clusters == 1) == linked


def test_cluster2000x_vertical_pair_alpha_is_45_degrees():
    # cluster2000x.f line 885 makes r hypocentral BEFORE line 916:
    #   alpha = atan2(z, r_hypo) -> 45 deg for a purely vertical pair (not 90 deg).
    # Stage-2 version of this test assumed 90 deg (misreading) and was replaced.
    kw = dict(xmeff=2.5, rule="cluster2000x")
    t, x, y, m, z = [0.0, 0.1], [0, 0], [0, 0], [2.5, 2.5], [10.0, 13.0]
    # erh only: e = 5*sqrt(0.5) = 3.54 each -> d = 3 - 7.07 < 1.111 -> linked
    assert run(t, x, y, m, z=z, err=[5.0, 5.0], derr=[0.0, 0.0], **kw).n_clusters == 1
    # erz only: e = 0.707 + 0.672 -> d = 1.621 > 1.111 -> not linked
    assert run(t, x, y, m, z=z, err=[0.0, 0.0], derr=[1.0, 0.95], **kw).n_clusters == 0


def test_zmap_error_correction_uses_larger_of_pair():
    # 3 - 1.5 * max(1.5, 0) = 0.75 <= 1.10
    r = run([0.0, 0.1], [0.0, 3.0], [0, 0], [2.5, 2.5], xmeff=2.5, rule="zmap",
            err=[1.5, 0.0])
    assert r.n_clusters == 1


# ============================================================ 6. magnitude thresholds
def test_look_ahead_increases_with_xmeff():
    taus = [look_ahead_time_days(5.0, 1.0, 0.5, xm, 0.99) for xm in (1.5, 2.0, 2.5, 3.0)]
    assert all(b >= a for a, b in zip(taus, taus[1:]))


@pytest.mark.parametrize("rule", RULES)
@pytest.mark.parametrize("xmeff,linked", [(2.5, True), (1.5, False)])
def test_xmeff_controls_late_link(rule, xmeff, linked):
    # big M5 t=0; i (M3, t=0.3) clustered; j (M3) 4 d after i, 0.5 km from i.
    # xmeff 2.5: tau_i = 4.605*0.3/10**(-2/3) = 6.4 d  -> j inside
    # xmeff 1.5: tau_i = 4.605*0.3 = 1.38 -> clipped to 2 d -> j outside
    r = run([0.0, 0.3, 4.3], [0.0, 0.5, 1.0], [0, 0, 0], [5.0, 3.0, 3.0],
            xmeff=xmeff, rule=rule, **TIMING)
    assert bool(r.cluster_id[2] == 0) == linked


@pytest.mark.parametrize("rule", RULES)
def test_catalog_cut_at_xmeff_raises_no_warning(rule, recwarn):
    cat = simulate_branching(seed=5)
    keep = cat["mag"] >= 3.0
    reasenberg(cat["t"][keep], cat["lat"][keep], cat["lon"][keep], cat["depth"][keep],
               cat["mag"][keep], xmeff=3.0, rule=rule)
    assert not [w for w in recwarn if issubclass(w.category, UserWarning)]


# ============================================================ 7. distance rule and 30 km cap
@pytest.mark.parametrize("dist_km,zmap_link,c2k_link", [(25.0, True, True), (35.0, True, False)])
def test_interaction_distance_cap(dist_km, zmap_link, c2k_link):
    t, x, m = [0.0, 0.5], [0.0, dist_km], [7.0, 3.0]
    assert bool(run(t, x, [0, 0], m, rule="zmap").n_clusters == 1) == zmap_link
    assert bool(run(t, x, [0, 0], m, rule="cluster2000x").n_clusters == 1) == c2k_link


def test_cap_can_be_disabled():
    r = run([0.0, 0.5], [0.0, 35.0], [0, 0], [7.0, 3.0], rule="cluster2000x", r_max=np.inf)
    assert r.n_clusters == 1


@pytest.mark.parametrize("rule,linked", [("zmap", False), ("cluster2000x", True)])
def test_rmain_term_for_clustered_events(rule, linked):
    # big M6 at origin; i (M3, t=1, x=20) linked by big; j (M3, t=2.5, x=22.5)
    # outside big's 2-day window. d(i,j) = 2.5 km:
    #   zmap:  2.5 > 10 r(3) = 1.75 and d(big,j) = 22.5 > r(6) = 2.77  -> no link
    #   c2k:   2.5 <= 10 r(3) + r(6) = 4.52                            -> link
    r = run([0.0, 1.0, 2.5], [0.0, 20.0, 22.5], [0, 0, 0], [6.0, 3.0, 3.0],
            rule=rule, **TIMING)
    assert bool(r.cluster_id[2] == 0) == linked


# ============================================================ 8. equivalent events
def test_equivalent_event_definition():
    t, x, y, m = [0.0, 0.1], [0.0, 1.0], [0.0, 0.0], [4.0, 4.0]
    r = run(t, x, y, m, rule="cluster2000x")
    eq = equivalent_events(r, t, x, y, np.full(2, 10.0), m)
    assert eq["magnitude"][0] == pytest.approx(4.0 + np.log10(2) / 1.2)
    assert eq["a"][0] == pytest.approx(0.5) and eq["n"][0] == 2
    assert eq["time"][0] == 0.0                       # representative (tie first)


# ============================================================ 9. defaults and parameters
def test_cluster2000x_defaults_dict():
    assert CLUSTER2000X_DEFAULTS["tau0"] == 2.0 and CLUSTER2000X_DEFAULTS["p"] == 0.99
    assert "xmeff" not in CLUSTER2000X_DEFAULTS
    r = run([0, 1], [0, 0.1], [0, 0], [3, 3], **CLUSTER2000X_DEFAULTS)
    assert r.params.r_max == 30.0 and r.params.rule == "cluster2000x"


def test_rule_validation():
    with pytest.raises(ValueError):
        run([0, 1], [0, 0], [0, 0], [3, 3], rule="fortran")


# ============================================================ 10. invariants on synthetic catalogs
@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_cluster2000x_invariants(seed):
    cat = simulate_branching(seed=seed)
    r = reasenberg(cat["t"], cat["lat"], cat["lon"], cat["depth"], cat["mag"],
                   xmeff=2.5, **CLUSTER2000X_DEFAULTS)
    m = cat["mag"]
    assert np.all((r.cluster_id == -1) == (r.event_class == SINGLE))
    assert np.all(r.cluster_sizes >= 2)
    assert np.sum(r.event_class == REPRESENTATIVE) == r.n_clusters
    for k, rep in enumerate(r.representative):
        assert m[rep] == m[r.cluster_id == k].max()
    assert np.sum(r.event_class == DEPENDENT) == r.n_events - r.independent.sum()
