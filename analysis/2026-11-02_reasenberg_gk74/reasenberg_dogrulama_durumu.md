# Stage 3 — reasenberg.py v0.3.0 against the verbatim cluster2000x.f source

Source: user-supplied `cluster2000x.f` (1108 lines, sha256 `77d95ad9e4cdf33bc140d0419566f8def3d3f3a8de510edf77f256f13f1807a1`).
Line numbers below refer to that file. Stage 2 relied on a fetch tool that
returned fragments; this stage reads the full text.

**Status of D1 (compiled Fortran vs module): still open.** No Fortran compiler
is available in the analysis environment. v0.3 must not be described as
"validated against the original Fortran" until `fortran_kit` has been run.

## 1. Stage-2 inferences now confirmed from the full text (B → A)

| Stage-2 item | Confirmed by |
|---|---|
| rtest re-evaluated per j with the current cluster state | `ctest` called inside the j loop with `cmag1(list(i))` (383–385); `list(i)` changes when i joins/creates a cluster (403, 449) |
| Unclustered i passes `cmag1(0)` | 385 with `list(i)=0`; `dimension cmag1(9000)` (89) — index 0 is outside the array |
| erh/erz from quality class | 856–860 tables, 889–910 assignment |
| τ in minutes | `tdif` returns minutes (940–975); DATA 2880/14400 (109) |

## 2. Differences found in stage 3 and corrected in v0.3.0 (`rule="cluster2000x"` only)

| # | Source | v0.2 | v0.3 | Found by |
|---|---|---|---|---|
| 1 | **ΔM has no floor**: `deltam = (1.-xk)*cmag1 - xmeff` (349); negative ΔM lengthens τ | max(ΔM, 0) (ZMAP/bruces) | no floor | transliteration cross-check (targeted case) |
| 2 | **α uses the hypocentral distance**: r made hypocentral at 885, then `alpha = atan2(z,r)` (916) → 45° for a vertical pair | atan2(dz, epicentral) → 90° | atan2(dz, hypocentral) | full-text reading |
| 3 | No error correction when z < 0.01 and r < 0.01 (886) | always | as source | full-text reading |
| 4 | Unclustered rmain term = r(cmag1(0)) | 0 | r(`cmag_unclustered`), default 0.0 → 0.011 km | full-text reading |
| 5 | Epicentral distance = DELAZ (geocentric latitude, ellipsoid radius, REAL*4 constants) | haversine | `delaz_km` | full-text reading |
| 6 | Quality codes: if event i has a code, both events get table errors; blank/unknown → 'D'; only q1 is tested (889) | not implemented | `quality=` (post-1970 tables) | full-text reading |

Stage-2 statements superseded: row 6 of the stage-2 table (error formula: angle
definition), row 7 (“τ formula ✔ same” — the ΔM floor differs), row 3 (cmag1(0)
now A-level), and the stage-2 test `test_cluster2000x_vertical_pair_uses_depth_error_only`
(replaced by `test_cluster2000x_vertical_pair_alpha_is_45_degrees`).
The stage-2 report reflects v0.2 and is kept unchanged as a record.

## 3. Separate-implementation comparison (bağımsız uygulama karşılaştırması): transliteration

`fortran_kit/translit.py` re-implements lines 305–552, 835–936, 940–975 and
1027–1072 keeping the GOTO flow, 1-based arrays, minute times and REAL*4 stores.
Module vs transliteration, inputs written to and re-read from HYPO71 files:

| case | events | clusters (both) | events with different membership | largest M agrees | max abs ΔM_eq |
|---|---|---|---|---|---|
| syn_s0 | 2152 | 163 | 0 | 163/163 | 0.0 |
| syn_s1 | 2499 | 203 | 0 | 203/203 | 0.0 |
| syn_s2 | 2078 | 150 | 0 | 150/150 | 0.0 |
| syn_s3 | 2263 | 182 | 0 | 182/182 | 0.0 |
| syn_s4 | 2658 | 202 | 0 | 202/202 | 0.0 |
| big_m74 (30 km cap) | 3310 | 240 | 0 | 240/240 | 0.0 |
| err_s1 (ierradj = 2) | 2499 | 319 | 0 | 319/319 | 0.0 |
| rfact5_s2 | 2078 | 44 | 0 | 44/44 | 0.0 |
| quality_s3 | 2263 | 277 | 0 | 277/277 | 0.0 |

Plus 9 targeted edge cases (negative ΔM, inclusive window, 1 min outside the
window, 30 km cap, same-minute events, equal magnitudes, converging clusters,
vertical errors, quality codes): all identical.

Limit: the transliteration and the module were written by the same analyst from
the same source; agreement shows consistency with *this reading* of the code,
not with the compiled program's behaviour (compiler, REAL*4 arithmetic details,
cmag1(0) memory content).

## 4. Program properties relevant to EQ-LiveTürkiye

* **Calendar valid only 1969–1999** (two-digit years, century ignored, 1–14):
  the program cannot process post-2000 Turkish catalogs unmodified.
* **Minute resolution** (seconds not read; 219, 940).
* **xmeff = 1.5 hard-coded** (110), not prompted: published runs of
  cluster2000x used 1.5 unless the source was edited. With xmeff = Mc (our
  requirement) ΔM is negative for small clusters and τ becomes longer (item 1).
* Hemisphere letters ignored (879–882); ≤ 250 000 events, ≤ 9 000 clusters.
* Declustered output `cluster.dec`: unclustered events first, then equivalent
  events appended (not time-sorted) (598–633, 770–815).

## 5. Tests

`pytest -q`: **102 passed** = 30 (stage 1, unchanged) + 40 (stage 2, one test
replaced, see §2) + 6 (decisions D2/D3) + 11 (source-derived, `test_stage3_source.py`)
+ 15 (module vs transliteration, `test_translit.py`).

## 6. Decision

**Source-level correspondence established; full validation not yet possible with
current resources.** The module's `cluster2000x` rule now follows the verbatim
source (six corrections, all with regression tests) and agrees event by event
with a separate transliteration on 9 catalogs and 9 edge cases (not an independent validation: same analyst, same reading of the source). The
event-level comparison with the compiled program (D1) remains open; the kit
(`fortran_kit/`, self-test passing) is ready to run on a machine with gfortran.
`rule="cluster2000x"` stays experimental (D3).


## 7. Addendum after review (kit only; reasenberg.py v0.3.0 unchanged, frozen until D1)

Adopted from the review:

* **Source record**: `run_fortran.py` now writes `cluster2000x_original.f` (byte copy,
  SHA-256 checked), `cluster2000x_gfortran.f` (only line 387 changed), the unified
  diff and `source_manifest.json`.
* **cmag1(0)**: a probe catalog (depth-separated M3.00 pairs) measures, without
  touching the source, the interval of the value the compiled program reads at
  line 385; repeated for three builds (`-O0`, `-O2`, `-O0 -fno-automatic`). Reported
  as an observation per compiler/build, not as an algorithm parameter.
  The mock self-test showed that the probe yields an interval and that a value
  inside it can still change borderline links (2 events in one catalog when the
  midpoint was used instead of the true value); the comparison therefore tries
  integers inside the interval first, then a 21-point grid, and reports all values tried.
* **Seven criteria per case and build**: cluster count, event membership
  (primary), representative event (time + magnitude), time of largest event at
  minute resolution, equivalent magnitude, equivalent location (horizontal and
  depth), cmag1(0). Module vs transliteration on the 9 catalogs: all identical;
  equivalent location difference ≤ 0.0009 km (REAL*4 vs float64 means).
* **Terminology**: the transliteration comparison is a separate-implementation
  comparison, not an independent validation.
* **xmeff**: the program hard-codes xmeff = 1.5. The comparison uses 1.5; using
  xmeff = Mc in EQ-LiveTürkiye is a deliberate methodological departure, not the
  program's parametrisation.
* **Dates**: `hypo71.to_fortran_date` maps 2000–2027 to 1972–1999 (−28 years, same
  leap cycle; minute differences preserved, tested across 29 Feb 2024).
* **Execution options**: local (MSYS2/WSL) or GitHub Actions (`ci/github-actions-d1.yml`).

Not adopted: relabelling the transliteration comparison as "S" (S already means
"synthetic-only" in the stage-2 evidence table; it remains "T").

Tests: **111 passed** (102 + 9 kit tests in `tests/test_kit.py`).
Self-test with two mock builds (cmag1(0) = 0 and 1): pipeline PASSED — this checks
the kit only.


## 8. Addendum: observation vs fitting for cmag1(0) (kit only)

Review point adopted: choosing the cmag1(0) value that maximises agreement is
parameter fitting, not validation. `compare_fortran.py` previously stopped at the
first value with zero differences; this was removed.

* **Q1 (primary)**: one module value per build from a pre-registered rule
  (R1–R5) that uses the probe only.
* **Q2 (sensitivity)**: all candidate values (fixed set −99, −1, 0, 0.5, 1, 1.5,
  2, 3 plus 5 points inside the probe interval and the primary value), all
  cases, membership match rate per value; labelled as fitting.
* **Q3 (builds)**: probe intervals per build and Fortran-vs-Fortran membership
  differences per case.

Mock self-test (two mock builds, cmag1(0) = 0 and 1): build 0 → R2, all cases
identical; build 1 → R3 midpoint 1.1325, primary shows 2 differing events,
sensitivity shows 1.0 reproduces all cases, Q3 detects the build difference.
Pipeline checks PASSED; not a Fortran validation.

Tests: **116 passed** (module 102 + kit 14). These show internal consistency of
the module and the kit only; D1 remains open until compiled output is compared.

## 9. Chronology of the cmag1(0) rule (recorded 2026-11-02)

* R1–R5 were defined **after** the transliteration and mock-build results had been seen.
* They were frozen (16:32 +03:00; `compare_fortran.py` sha256
  `002367227043e88fb1743aa0a4ed5d6c95ef698e0211985825d3f9d67045767d`) **before** any
  compiled USGS `cluster2000x` output existed.
* Therefore no retrospective tuning to the USGS output took place. It is **not**
  claimed that the rules were fully pre-specified or uninfluenced by any
  intermediate result.

D1 review order (fixed): (1) verify SHA-256 of the frozen files; (2) Q1 primary
results, case by case, event membership first; (3) Q2 sensitivity, separately
from the primary result; (4) Q3 Fortran–Fortran differences between builds;
(5) only then decide whether D1 can be closed. Test success and hash matches
show the integrity of the frozen implementation and the internal consistency
of the kit; they do not by themselves establish equivalence with the Fortran.
