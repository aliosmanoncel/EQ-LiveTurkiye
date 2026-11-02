"""
reasenberg.py
=============

Independent implementation of the Reasenberg (1985) cluster-identification
("declustering") algorithm, written for method-sensitivity studies in which
the *membership* of every cluster must be traceable event by event.

Reference
---------
Reasenberg, P. (1985). Second-order moment of central California seismicity,
1969-1982. J. Geophys. Res., 90(B7), 5479-5495.

Design decisions (all deliberate, all documented)
-------------------------------------------------
1. Output is a classification, not a "mainshock catalog".
   Every event receives one of three classes:
       SINGLE (0)          -- never linked to any other event
       REPRESENTATIVE (1)  -- the event chosen to represent its cluster
                              (largest magnitude; tie rule configurable)
       DEPENDENT (2)       -- member of a cluster, not its representative
   "Independent" events = SINGLE + REPRESENTATIVE. Whether these are
   physical mainshocks is an interpretation, not an algorithm output.

2. Causal "largest event so far".
   The look-ahead time tau and the second spatial test use the largest
   event of the cluster *among events already processed* (index <= i),
   i.e. the information available at time t_i. This follows the loop
   logic of ZMAP and cluster2000-type codes.

3. The final representative is recomputed after the loop from the full
   cluster membership (argmax of magnitude). This removes, by
   construction, the merge-related representative errors found in
   bruces 0.5.0 (smaller event kept after a merge) and ZMAP7 (largest
   event not updated after a merge).

4. Merging. When event i links to events belonging to other clusters,
   all involved clusters are merged into the earliest-formed one.
   (ZMAP7 GUI code fails to merge in this situation -- see audit notes.)

5. Time window: later events j with t_j - t_i < tau are tested
   (events with identical origin time are ordered by input order),
   including the case of exactly one event in the window
   (ZMAP7 returns an empty window in that case).

6. Distances: great-circle (haversine, R = 6371 km) plus depth
   difference -- no map projection, so no UTM-zone distortion across
   Turkey (bruces projects all events into the UTM zone of the first
   input event). A Cartesian mode (x, y in km) is provided for tests
   and for comparison with planar implementations.

7. Location-error correction (as in ZMAP / Reasenberg-type codes):
       r_h = max(r_epi - err_factor * err, 0)
       r_z = max(|dz| - derr, 0)
       r   = sqrt(r_h**2 + r_z**2)
   Default err = derr = 0 (no correction). ZMAP defaults are
   err = 1.5 km, derr = 2 km, err_factor = 1.5.

8. xmeff has no default. The look-ahead time depends on it directly,
   and defaulting to the catalog minimum magnitude (bruces) silently
   ties the result to the incompleteness of the catalog.

Algorithm (per event i, in time order)
--------------------------------------
    r_main(M) = 0.011 * 10**(0.4 M)  km      (log r = 0.4M - 1.959)
    if i unclustered:              tau = tau_min
    elif M_i >= M_largest(cluster): M_largest <- M_i ; tau = tau_min
    else:
        dM  = max((1 - xk) * M_largest - xmeff, 0)
        tau = -ln(1 - p) * (t_i - t_largest) / 10**(2 (dM - 1) / 3)
        tau = clip(tau, tau_min, tau_max)
    candidates j: t_i < t_j < t_i + tau, not already in i's cluster
    link j if  d(i, j) <= rfact * r_main(M_i)
           or  (tau > tau_min and d(largest, j) <= r_main(M_largest))

The block above describes rule="zmap" (default, v0.1 behaviour).
v0.2 adds rule="cluster2000x", which follows the USGS cluster2000x Fortran
as read from its source (single test d(i,j) <= rfact*r(M_i) + r(M_max),
30 km cap, inclusive window, tau0, eager largest-event update, sequential
links, Fortran error correction); see _loop_cluster2000x and
stage2_report.md. The Fortran has not been compiled or run against this
module (open item).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, asdict
from typing import Optional

import numpy as np

__all__ = [
    "SINGLE",
    "REPRESENTATIVE",
    "DEPENDENT",
    "CLASS_NAMES",
    "ReasenbergParams",
    "ReasenbergResult",
    "interaction_radius_km",
    "look_ahead_time_days",
    "reasenberg",
    "equivalent_events",
    "CLUSTER2000X_DEFAULTS",
    "ExperimentalRuleWarning",
]

__version__ = "0.3.0"


class ExperimentalRuleWarning(Warning):
    """Issued when rule='cluster2000x' is used before event-level validation
    against the compiled USGS Fortran (approved decision, 2026-11-02)."""

# Parameter values hard-coded in USGS cluster2000x.f (DATA statements; times
# converted from minutes to days). Use as reasenberg(..., **CLUSTER2000X_DEFAULTS).
# xmeff (1.5 in the Fortran) is deliberately excluded: it must be set to Mc.
CLUSTER2000X_DEFAULTS = dict(
    rule="cluster2000x", rfact=10.0, xk=0.5,
    tau0=2.0, tau_min=2.0, tau_max=10.0, p=0.99, r_max=30.0,
)

SINGLE, REPRESENTATIVE, DEPENDENT = 0, 1, 2
CLASS_NAMES = {SINGLE: "single", REPRESENTATIVE: "representative", DEPENDENT: "dependent"}

EARTH_RADIUS_KM = 6371.0


# ----------------------------------------------------------------------------
# Physical relations
# ----------------------------------------------------------------------------
def interaction_radius_km(magnitude):
    """Reasenberg (1985) crack-radius relation, log10 r = 0.4 M - 1.959 (km)."""
    return 0.011 * 10.0 ** (0.4 * np.asarray(magnitude, dtype=float))


def look_ahead_time_days(mag_largest, dt_since_largest_days, xk, xmeff, p, floor_dm=True):
    """Unclipped Reasenberg look-ahead time tau (days).

    floor_dm=True : dM = max((1-xk) M - xmeff, 0)  (ZMAP / bruces)
    floor_dm=False: dM may be negative               (cluster2000x.f lines 349-352)
    """
    dm = (1.0 - xk) * mag_largest - xmeff
    if floor_dm:
        dm = max(dm, 0.0)
    return -np.log(1.0 - p) * dt_since_largest_days / 10.0 ** (2.0 * (dm - 1.0) / 3.0)


# ----------------------------------------------------------------------------
# Parameters and result containers
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class ReasenbergParams:
    xmeff: float
    rfact: float = 10.0
    xk: float = 0.5
    tau_min: float = 1.0
    tau_max: float = 10.0
    p: float = 0.95
    err: float = 0.0
    derr: float = 0.0
    err_factor: float = 1.5
    tie: str = "first"
    coords: str = "geographic"
    rule: str = "zmap"
    r_max: float = float("inf")
    tau0: float = 1.0
    cmag_unclustered: float = 0.0

    def validate(self):
        if self.rule not in ("zmap", "cluster2000x"):
            raise ValueError("rule must be 'zmap' or 'cluster2000x'.")
        if not self.r_max > 0:
            raise ValueError("r_max must be positive (use inf for no cap).")
        if not 0.0 < self.tau0:
            raise ValueError("tau0 must be positive.")
        if not np.isfinite(self.xmeff):
            raise ValueError("xmeff must be a finite magnitude (typically Mc).")
        if not 0.0 < self.p < 1.0:
            raise ValueError("p must be in (0, 1).")
        if not 0.0 < self.tau_min <= self.tau_max:
            raise ValueError("Require 0 < tau_min <= tau_max.")
        if self.rfact <= 0:
            raise ValueError("rfact must be positive.")
        if min(self.err, self.derr, self.err_factor) < 0:
            raise ValueError("err, derr, err_factor must be non-negative.")
        if self.tie not in ("first", "last"):
            raise ValueError("tie must be 'first' or 'last'.")
        if self.coords not in ("geographic", "cartesian"):
            raise ValueError("coords must be 'geographic' or 'cartesian'.")


@dataclass
class ReasenbergResult:
    """All arrays are in the ORIGINAL input order.

    cluster_id      : int array, -1 for SINGLE events, 0..K-1 otherwise
                      (clusters numbered by time of their first event)
    event_class     : int array of SINGLE / REPRESENTATIVE / DEPENDENT
    representative  : int array (length K), input index of each cluster's
                      representative event
    n_merges        : number of cluster-merge operations during the run
    params          : ReasenbergParams used
    """

    cluster_id: np.ndarray
    event_class: np.ndarray
    representative: np.ndarray
    n_merges: int
    params: ReasenbergParams

    @property
    def n_events(self) -> int:
        return int(self.cluster_id.size)

    @property
    def n_clusters(self) -> int:
        return int(self.representative.size)

    @property
    def independent(self) -> np.ndarray:
        """Boolean mask: SINGLE or REPRESENTATIVE events."""
        return self.event_class != DEPENDENT

    @property
    def cluster_sizes(self) -> np.ndarray:
        if self.n_clusters == 0:
            return np.zeros(0, dtype=int)
        return np.bincount(self.cluster_id[self.cluster_id >= 0], minlength=self.n_clusters)

    def summary(self) -> dict:
        sizes = self.cluster_sizes
        return {
            "n_events": self.n_events,
            "n_single": int(np.sum(self.event_class == SINGLE)),
            "n_clusters": self.n_clusters,
            "n_dependent": int(np.sum(self.event_class == DEPENDENT)),
            "n_independent": int(self.independent.sum()),
            "largest_cluster": int(sizes.max()) if sizes.size else 0,
            "n_merges": self.n_merges,
            "module_version": __version__,
            "rule": self.params.rule,
            "rule_status": "experimental" if self.params.rule == "cluster2000x" else "default",
            "output": "representative (largest event); equivalent events via equivalent_events()",
            "params": asdict(self.params),
        }

    def to_records(self):
        """List of dicts (one per event) for CSV export without pandas."""
        return [
            {
                "index": k,
                "cluster_id": int(self.cluster_id[k]),
                "event_class": CLASS_NAMES[int(self.event_class[k])],
            }
            for k in range(self.n_events)
        ]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _to_days(times) -> np.ndarray:
    arr = np.asarray(times)
    if np.issubdtype(arr.dtype, np.datetime64):
        ns = arr.astype("datetime64[ns]").astype(np.int64)
        return (ns - ns.min()) / 86400e9
    if arr.dtype == object:  # e.g. list of datetime.datetime
        arr = np.asarray(arr, dtype="datetime64[ns]")
        return _to_days(arr)
    return arr.astype(float)


def _broadcast(value, n, name):
    a = np.asarray(value, dtype=float)
    if a.ndim == 0:
        return np.full(n, float(a))
    if a.shape != (n,):
        raise ValueError(f"{name} must be scalar or length-{n} array.")
    return a


def delaz_km(alat, alon, blat, blon):
    """Epicentral distance (km) exactly as subroutine DELAZ in cluster2000x.f
    (lines 1027-1072): geocentric latitudes (flat = 0.993231), spherical law
    of cosines, ellipsoid-corrected radius at the mean colatitude. The
    truncated constants pi2 = 1.570796 and rad = 1.745329e-2 are kept."""
    if alat == blat and alon == blon:
        return 0.0
    pi2, rad, flat = 1.570796, 1.745329e-02, 0.993231
    alatr, alonr, blatr, blonr = alat * rad, alon * rad, blat * rad, blon * rad
    acol = pi2 - np.arctan(flat * np.tan(alatr))
    bcol = pi2 - np.arctan(flat * np.tan(blatr))
    diflon = blonr - alonr
    cosdel = np.sin(acol) * np.sin(bcol) * np.cos(diflon) + np.cos(acol) * np.cos(bcol)
    delr = np.arccos(np.clip(cosdel, -1.0, 1.0))
    colat = pi2 - (alatr + blatr) / 2.0
    radius = 6371.227 * (1.0 + 3.37853e-3 * (1.0 / 3.0 - np.cos(colat) ** 2))
    return float(delr * radius)


# Quality-class location errors (cluster2000x.f lines 856-860, post-1970 tables)
QUALITY_ERRORS_KM = {"A": (0.5, 1.0), "B": (1.0, 2.0), "C": (2.5, 5.0), "D": (5.0, 10.0)}


class _Distance:
    """Hypocentral distance with optional location-error correction."""

    def __init__(self, a, b, depth, err, derr, err_factor, coords):
        self.depth = depth
        self.err = err
        self.derr = derr
        self.err_factor = err_factor
        self.geo = coords == "geographic"
        self.a_deg, self.b_deg = a, b
        if self.geo:
            self.lat = np.radians(a)
            self.lon = np.radians(b)
            self.coslat = np.cos(self.lat)
        else:
            self.x = a
            self.y = b

    def raw(self, i, js):
        """Uncorrected epicentral and vertical separations (km)."""
        if self.geo:
            dlat = self.lat[js] - self.lat[i]
            dlon = self.lon[js] - self.lon[i]
            h = np.sin(dlat / 2) ** 2 + self.coslat[i] * self.coslat[js] * np.sin(dlon / 2) ** 2
            rh = 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(h, 0.0, 1.0)))
        else:
            rh = np.hypot(self.x[js] - self.x[i], self.y[js] - self.y[i])
        return rh, np.abs(self.depth[js] - self.depth[i])

    def __call__(self, i, js):
        if self.geo:
            dlat = self.lat[js] - self.lat[i]
            dlon = self.lon[js] - self.lon[i]
            h = np.sin(dlat / 2) ** 2 + self.coslat[i] * self.coslat[js] * np.sin(dlon / 2) ** 2
            rh = 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(h, 0.0, 1.0)))
        else:
            rh = np.hypot(self.x[js] - self.x[i], self.y[js] - self.y[i])
        rz = np.abs(self.depth[js] - self.depth[i])
        if self.err is not None:
            rh = np.maximum(rh - self.err_factor * np.maximum(self.err[i], self.err[js]), 0.0)
            rz = np.maximum(rz - np.maximum(self.derr[i], self.derr[js]), 0.0)
        return np.hypot(rh, rz)


# ----------------------------------------------------------------------------
# Main routine
# ----------------------------------------------------------------------------
def reasenberg(
    times,
    a,
    b,
    depths,
    magnitudes,
    *,
    xmeff: float,
    rfact: float = 10.0,
    xk: float = 0.5,
    tau_min: float = 1.0,
    tau_max: float = 10.0,
    p: float = 0.95,
    err=0.0,
    derr=0.0,
    err_factor: float = 1.5,
    tie: str = "first",
    coords: str = "geographic",
    rule: str = "zmap",
    r_max: Optional[float] = None,
    tau0: Optional[float] = None,
    cmag_unclustered: float = 0.0,
    quality=None,
) -> ReasenbergResult:
    """Reasenberg (1985) cluster identification.

    Parameters
    ----------
    times : array of datetime64 / datetime, or float (days)
    a, b  : latitude, longitude (deg) if coords='geographic';
            x, y (km) if coords='cartesian'
    depths : km
    magnitudes : array
    xmeff : effective minimum magnitude (normally Mc). REQUIRED.
    rfact, xk, tau_min, tau_max, p : Reasenberg parameters
        (tau_min, tau_max in days).
    err, derr : horizontal / depth location error (km), scalar or per event.
        Per-pair correction uses the larger error of the two events.
    err_factor : multiplier on err (ZMAP uses 1.5).
    tie : 'first' -> earliest of equal-magnitude largest events is the
          representative; 'last' -> latest (ZMAP-compatible).
    coords : 'geographic' or 'cartesian'.
    rule : linking rule.
        'zmap' (default, unchanged from v0.1): two tests,
            d(i,j) <= rfact*r(M_i)  OR  d(largest,j) <= r(M_largest);
            strict time window; causal largest; ZMAP-type error correction
            (err_factor*err horizontally, derr vertically); no distance cap.
        'cluster2000x': USGS cluster2000x linking (see _loop_cluster2000x);
            err / derr are then per-event horizontal / vertical errors
            (erh, erz) and err_factor is ignored.
    r_max : cap on the interaction distance (km). Default: 30 km for
        'cluster2000x' (crustal thickness, as in the Fortran), none for 'zmap'.
    cmag_unclustered : 'cluster2000x' only. Magnitude used for the rmain
        term when event i is unclustered (the Fortran reads cmag1(0), outside
        the array). Default 0.0 -> rmain = 0.011 km.
    quality : 'cluster2000x' only. Optional per-event quality codes
        ('A'-'D' or ' '); when event i has a code, both events' errors are
        taken from the cluster2000x tables. Giving codes implies ierradj = 2.
        Pre-1970 tables are not implemented.
    In 'cluster2000x' the epicentral distance for geographic coordinates is
    computed with delaz_km (the Fortran DELAZ routine).
    tau0 : look-ahead time (days) for unclustered events. Default = tau_min.
        cluster2000x defaults: tau0 = tau_min = 2 d, tau_max = 10 d, p = 0.99
        (see CLUSTER2000X_DEFAULTS); they are NOT applied automatically.
    """
    if rule == "cluster2000x":
        warnings.warn(
            "rule='cluster2000x' is EXPERIMENTAL: reconstructed from the USGS source, "
            "not yet validated event by event against the compiled Fortran.",
            ExperimentalRuleWarning, stacklevel=2,
        )
    if r_max is None:
        r_max = 30.0 if rule == "cluster2000x" else float("inf")
    params = ReasenbergParams(
        xmeff=float(xmeff), rfact=float(rfact), xk=float(xk),
        tau_min=float(tau_min), tau_max=float(tau_max), p=float(p),
        err=float(np.max(err)) if np.ndim(err) else float(err),
        derr=float(np.max(derr)) if np.ndim(derr) else float(derr),
        err_factor=float(err_factor), tie=tie, coords=coords,
        rule=rule, r_max=float(r_max),
        tau0=float(tau_min if tau0 is None else tau0),
        cmag_unclustered=float(cmag_unclustered),
    )
    params.validate()

    t_all = _to_days(times)
    n = t_all.size
    a = _broadcast(a, n, "a")
    b = _broadcast(b, n, "b")
    z = _broadcast(depths, n, "depths")
    m = _broadcast(magnitudes, n, "magnitudes")
    err_arr = _broadcast(err, n, "err")
    derr_arr = _broadcast(derr, n, "derr")

    for name, arr in (("times", t_all), ("a", a), ("b", b), ("depths", z), ("magnitudes", m)):
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"{name} contains NaN or inf.")
    if np.any(m < params.xmeff - 1e-9):
        warnings.warn(
            f"{int(np.sum(m < params.xmeff - 1e-9))} events have M < xmeff; "
            "Reasenberg is normally applied to a catalog cut at xmeff.",
            stacklevel=2,
        )

    # Sort by time (stable: simultaneous events keep input order)
    order = np.argsort(t_all, kind="stable")
    t, a, b, z, m = t_all[order], a[order], b[order], z[order], m[order]
    err_arr, derr_arr = err_arr[order], derr_arr[order]

    use_err = np.any(err_arr > 0) or np.any(derr_arr > 0)
    dist = _Distance(a, b, z,
                     err_arr if use_err else None,
                     derr_arr if use_err else None,
                     params.err_factor, params.coords)

    if params.rule == "cluster2000x":
        q_sorted = None
        if quality is not None:
            q_all = np.asarray([str(q)[:1].upper() if str(q).strip() else " " for q in quality])
            if q_all.shape != (n,):
                raise ValueError(f"quality must have length {n}.")
            q_sorted = q_all[order]
        lab, n_merges = _loop_cluster2000x(
            t, m, dist, err_arr if use_err else None, derr_arr if use_err else None, params,
            quality=q_sorted)
    else:
        lab, n_merges = _loop_zmap(t, m, dist, params)
    return _finalise(lab, m, order, n_merges, params)


def _loop_zmap(t, m, dist, params):
    """Two-test linking (ZMAP / bruces structure), causal largest event."""
    n = t.size
    r_main = interaction_radius_km(m)
    r_link = params.rfact * r_main

    lab = np.full(n, -1, dtype=np.int64)  # working cluster labels
    cmax: dict[int, float] = {}            # causal largest magnitude per cluster
    cbig: dict[int, int] = {}              # causal largest event (sorted index)
    next_id = 0
    n_merges = 0

    for i in range(n - 1):
        c = int(lab[i])
        big = -1
        if c < 0:
            tau = params.tau_min
        else:
            if m[i] >= cmax[c]:
                cmax[c] = m[i]
                cbig[c] = i
                tau = params.tau_min
            else:
                tau = look_ahead_time_days(cmax[c], t[i] - t[cbig[c]],
                                           params.xk, params.xmeff, params.p)
                tau = min(max(tau, params.tau_min), params.tau_max)
            big = cbig[c]

        hi = int(np.searchsorted(t, t[i] + tau, side="left"))  # t_j < t_i + tau
        if hi <= i + 1:
            continue
        js = np.arange(i + 1, hi)  # includes simultaneous later-listed events
        if c >= 0:
            js = js[lab[js] != c]
        if js.size == 0:
            continue

        linked = dist(i, js) <= r_link[i]
        if c >= 0 and tau > params.tau_min:
            linked |= dist(big, js) <= r_main[big]
        js = js[linked]
        if js.size == 0:
            continue

        involved = set(int(v) for v in np.unique(lab[js]) if v >= 0)
        if c >= 0:
            involved.add(c)

        if not involved:
            target = next_id
            next_id += 1
            lab[i] = target
            cmax[target] = m[i]
            cbig[target] = i
        else:
            target = min(involved)  # earliest-formed cluster survives
            for other in sorted(involved - {target}):
                lab[lab == other] = target
                n_merges += 1
                if cmax[other] > cmax[target] or (
                    cmax[other] == cmax[target] and cbig[other] > cbig[target]
                ):
                    cmax[target] = cmax[other]
                    cbig[target] = cbig[other]
                del cmax[other], cbig[other]
            if lab[i] < 0:
                lab[i] = target
                if m[i] >= cmax[target]:
                    cmax[target] = m[i]
                    cbig[target] = i
        lab[js[lab[js] < 0]] = target
    return lab, n_merges


def _loop_cluster2000x(t, m, dist, erh, erz, params, quality=None):
    """Linking logic of USGS cluster2000x.f (line numbers refer to that file).

    Per event i (time order), tau computed once (338-357):
      * i unclustered, or time since cluster's largest event <= 0 : tau = tau0
      * otherwise tau = clip(Reasenberg formula, tau_min, tau_max)
    Later j are read one at a time (360-387); j in i's current cluster are
    skipped (365); the loop ends at the first j with t_j - t_i > tau (380).
    ctest (835-936):
      r     = hypocentral distance, epicentral part from DELAZ (883-885)
      if quality code of i is non-blank: erh/erz of BOTH events from the
            quality tables, blank/unknown -> 'D' (889-910)
      if errors used and not (dz < 0.01 and r < 0.01):           (886, 915-922)
            alpha = atan2(dz, r)   <- r is the HYPOCENTRAL distance here
            r -= sqrt(erh_i^2 cos^2 + erz_i^2 sin^2) + same for j
      rtest = rfact*r(M_i) + r(cmag1(list(i)))                   (927-929)
      rtest = min(rtest, 30)                                     (931)
      link if r <= rtest                                         (934)
    Unclustered i: list(i)=0 and the Fortran passes cmag1(0), outside the
    declared array (lower bound 1). params.cmag_unclustered is the magnitude
    used for that term (default 0.0, i.e. a zero-filled word: rmain = 0.011 km).
    Joining (320-474): largest updated with strict '>' (458).
    Merging (375-542): into the lower cluster number; '.ge.' keeps the lower
    cluster's largest event on ties (499).
    """
    n = t.size
    r_main = interaction_radius_km(m)
    r_unclustered = float(interaction_radius_km(params.cmag_unclustered))
    lab = np.full(n, -1, dtype=np.int64)
    cmax: dict[int, float] = {}
    cbig: dict[int, int] = {}
    next_id = 0
    n_merges = 0
    use_err = erh is not None or quality is not None   # = ierradj 2
    if quality is not None and erh is None:
        erh, erz = np.zeros(n), np.zeros(n)

    def errors(i, j):
        q_i = quality[i] if quality is not None else " "
        if q_i != " ":
            ehi, ezi = QUALITY_ERRORS_KM.get(q_i, QUALITY_ERRORS_KM["D"])
            ehj, ezj = QUALITY_ERRORS_KM.get(quality[j], QUALITY_ERRORS_KM["D"])
            return ehi, ezi, ehj, ezj
        return erh[i], erz[i], erh[j], erz[j]

    for i in range(n - 1):
        c = int(lab[i])
        if c < 0:
            tau = params.tau0
        else:
            dt = t[i] - t[cbig[c]]
            if dt <= 0:
                tau = params.tau0
            else:
                tau = look_ahead_time_days(cmax[c], dt, params.xk, params.xmeff, params.p,
                                           floor_dm=False)       # lines 349-352: no floor
                tau = min(max(tau, params.tau_min), params.tau_max)

        hi = int(np.searchsorted(t, t[i] + tau, side="right"))  # t_j - t_i <= tau
        for j in range(i + 1, hi):
            ci, cj = int(lab[i]), int(lab[j])
            if ci >= 0 and cj == ci:
                continue
            rtest = params.rfact * r_main[i]
            rtest += float(interaction_radius_km(cmax[ci])) if ci >= 0 else r_unclustered
            rtest = min(rtest, params.r_max)

            if dist.geo:
                rh = delaz_km(dist.a_deg[i], dist.b_deg[i], dist.a_deg[j], dist.b_deg[j])
            else:
                rh = float(np.hypot(dist.a_deg[j] - dist.a_deg[i], dist.b_deg[j] - dist.b_deg[i]))
            rz = abs(float(dist.depth[j] - dist.depth[i]))
            d = float(np.hypot(rh, rz))
            if use_err and not (rz < 0.01 and d < 0.01):
                ehi, ezi, ehj, ezj = errors(i, j)
                alpha = np.arctan2(rz, d)          # Fortran: atan2(z, r) with hypocentral r
                ca2, sa2 = np.cos(alpha) ** 2, np.sin(alpha) ** 2
                d -= np.sqrt(ehi ** 2 * ca2 + ezi ** 2 * sa2)
                d -= np.sqrt(ehj ** 2 * ca2 + ezj ** 2 * sa2)
            if d > rtest:
                continue

            if ci >= 0 and cj >= 0:                       # merge
                k, l = min(ci, cj), max(ci, cj)
                lab[lab == l] = k
                n_merges += 1
                if not cmax[k] >= cmax[l]:
                    cmax[k], cbig[k] = cmax[l], cbig[l]
                del cmax[l], cbig[l]
            elif ci >= 0:                                 # j joins i's cluster
                lab[j] = ci
                if m[j] > cmax[ci]:
                    cmax[ci], cbig[ci] = m[j], j
            elif cj >= 0:                                 # i joins j's cluster
                lab[i] = cj
                if m[i] > cmax[cj]:
                    cmax[cj], cbig[cj] = m[i], i
            else:                                         # new cluster
                lab[i] = lab[j] = next_id
                cmax[next_id], cbig[next_id] = m[i], i
                if m[j] > m[i]:
                    cmax[next_id], cbig[next_id] = m[j], j
                next_id += 1
    return lab, n_merges


def _finalise(lab, m, order, n_merges, params):
    n = lab.size
    cid_sorted = np.full(n, -1, dtype=np.int64)
    cls_sorted = np.full(n, SINGLE, dtype=np.int8)
    reps_sorted = []
    if np.any(lab >= 0):
        live = lab >= 0
        first_index = {}
        for k in np.flatnonzero(live):
            first_index.setdefault(int(lab[k]), int(k))
        ordered = sorted(first_index, key=first_index.get)
        remap = {old: new for new, old in enumerate(ordered)}
        cid_sorted[live] = [remap[int(v)] for v in lab[live]]
        cls_sorted[live] = DEPENDENT
        for k_new in range(len(ordered)):
            members = np.flatnonzero(cid_sorted == k_new)
            mm = m[members]
            winners = members[mm == mm.max()]
            rep = int(winners[0] if params.tie == "first" else winners[-1])
            reps_sorted.append(rep)
            cls_sorted[rep] = REPRESENTATIVE

    # ---- back to input order ----------------------------------------------
    cluster_id = np.empty(n, dtype=np.int64)
    event_class = np.empty(n, dtype=np.int8)
    cluster_id[order] = cid_sorted
    event_class[order] = cls_sorted
    representative = order[np.asarray(reps_sorted, dtype=np.int64)] if reps_sorted \
        else np.zeros(0, dtype=np.int64)

    return ReasenbergResult(cluster_id, event_class, representative, n_merges, params)


def equivalent_events(result, times, a, b, depths, magnitudes):
    """Equivalent event per cluster, as written by cluster2000x to cluster.dec.

    time      : origin time of the cluster's representative (largest) event
    a, b      : unweighted mean of members' coordinates (lat/lon or x/y)
    depth     : unweighted mean depth
    magnitude : log10(sum 10**(1.2 M)) / 1.2   (summed "moment")
    n         : number of members

    Returns a dict of arrays of length result.n_clusters (cluster order).
    The magnitude is >= the largest member's magnitude, so a declustered
    catalog built from equivalent events has a different magnitude
    distribution from one built from representatives.
    """
    times = np.asarray(times)
    a, b = np.asarray(a, float), np.asarray(b, float)
    z, m = np.asarray(depths, float), np.asarray(magnitudes, float)
    K = result.n_clusters
    out = {"time": times[result.representative] if K else times[:0],
           "a": np.empty(K), "b": np.empty(K), "depth": np.empty(K),
           "magnitude": np.empty(K), "n": np.empty(K, dtype=int)}
    for k in range(K):
        mem = result.cluster_id == k
        out["a"][k], out["b"][k], out["depth"][k] = a[mem].mean(), b[mem].mean(), z[mem].mean()
        out["magnitude"][k] = np.log10(np.sum(10.0 ** (1.2 * m[mem]))) / 1.2
        out["n"][k] = int(mem.sum())
    return out
