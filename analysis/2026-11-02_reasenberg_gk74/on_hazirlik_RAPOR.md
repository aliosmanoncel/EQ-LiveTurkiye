# EQ-LiveTürkiye — three pre-start outputs for the GK74–Reasenberg comparison (revision 2)

Read-only analysis; the EQ-LiveTürkiye repository was not modified.
**Revision 2 supersedes revision 1**, whose completeness (GFT) values and old-file
overlap logic must not be used (see "Corrections").

| Item | Value |
|---|---|
| Repository commit | `4d109710acfc6f1c7aa4977045aefcd6ff97fc67` (2026-11-02) |
| Catalog | `data/eq_historical.json`, sha256 `bd303aa30a17ae590073cfe664fd58c87cf93ed643cdb8374aa33c27a6d7545b` |
| Subset | `src == "EMSC"` → 80 929 events (1998–2026, M ≥ 3.0; magnitudes in 0.1 steps); id list sha256 `b1300aace58a4a797c968059692434a67424d543eb611a463a191a8358901512` |
| Analysis script | `prep_analysis.py`, sha256 `5116d81775e3a2eec3d32ec0262be36cc536b8acfcf9afc452b47c5caaef3214` |
| Results | `prep_results.json`, sha256 `14ab8646ab45e61597e389b317b2ad294cbef7f06aace2d285eb88bbe3d382f6` |
| GK74 reference ids | `gk74_reference_main_ids.json`, sha256 `7d04e689fe596eb9eb8556d72f1d05a75806939ece9f8083123ea9dd9cba5549` |

## Corrections (revision 1 → 2)

1. **GFT definition.** Revision 1 compared per-bin (non-cumulative) counts and called it
   GFT. Wiemer & Wyss (2000) compare observed and predicted **cumulative** FMDs
   (B_i, S_i = N(≥ M_i)). Revision 2 uses the cumulative form; the per-bin version is
   reported only as `binwise_R` (diagnostic). Note: ZMAP's `mcperc_ca3.m` also builds
   the observed side cumulatively (its synthetic side is normalised differently).
   Before that, revision 1 also had an a-value bin-edge error (fixed earlier the same day).
2. **Behaviour on synthetic G-R samples** (Δm = 0.1): complete catalogs R_cum = 97.9–99.4;
   catalog incomplete below 3.4: R_cum(3.0) = 82.9, R_cum(3.4) = 99.4.
3. **Old declustered file.** The filter `src == "EMSC" or year ≥ 1998` was wrong; the old file
   keeps `src`, so only `src == "EMSC"` is used. The count happens to be unchanged (33 551).
4. **Reference ids** are now stored, not only hashed (`gk74_reference_main_ids.json`).

## 1. Magnitude types and completeness (1998–2026 EMSC)

| mtype (case-folded) | n | share | median M | 90th pct | max |
|---|---|---|---|---|---|
| ml | 39 033 | 48.2 % | 3.2 | 3.8 | 5.2 |
| md | 32 997 | 40.8 % | 3.2 | 3.6 | 4.9 |
| mb | 6 908 | 8.5 % | 4.2 | 4.7 | 6.5 |
| mw | 1 374 | 1.7 % | 3.9 | 5.2 | 7.8 |
| m / mc / ms | 424 / 115 / 78 | 0.8 % | | | |

MD dominates 1998–2012 and practically vanishes from 2013; ML takes over. `mw` is present for
1 374 events, all `native`.

**Completeness.** The catalog is cut at 3.0, so Mc below 3.0 cannot be assessed; a value of
3.0 below means "complete from the cut", not "Mc = 3.0". MAXC = bin with the highest
non-cumulative count, no correction term.

| Subset | n (M ≥ 3.0) | MAXC | R_cum at 3.0 | Mc (R ≥ 90) | Mc (R ≥ 95) | n at Mc(R95) | b at 3.0 → 3.5 → 4.0 |
|---|---|---|---|---|---|---|---|
| All EMSC, mixed types *(diagnostic only)* | 80 929 | 3.0 | 98.4 | 3.0 | 3.0 | 80 929 | 1.03 → 1.02 → 1.10 |
| ml 2013–2026 | 26 535 | 3.0 | 92 | 3.0 | **3.8** | 3 241 | 1.13 → 1.46 → 2.00 |
| ml 1998–2012 | 12 498 | 3.0 | 91 | 3.0 | 4.2 | — | 1.13 → 1.50 → 2.21 |
| md 1998–2012 | 32 995 | 3.0 | 93 | 3.0 | **3.8** | 1 264 | 1.57 → 2.14 → 2.99 |
| mb (all) | 6 908 | 4.2 | 60 | — | — | — | 0.37 → 0.57 |
| mw native | 1 374 | 3.1 | 84 | not reached | not reached | — | 0.39 → 0.43 → 0.50 |

Reading:

* ML and MD pass R ≥ 90 from the cut, R ≥ 95 only from 3.8. The R curves are not monotone
  (ML 2013–2026 dips to 89 at 3.3).
* GFT accepts a cutoff; it does not test that b is constant above it. For ML and MD the
  b-value keeps rising with the cutoff (to 2–3), i.e. the FMD is curved. These thresholds
  are **working thresholds supported by this analysis, not proven completeness limits**.
* The mixed catalog fits better than any component; this reflects the mixture, not homogeneity.
* mb and native Mw are not usable as complete catalogs at these magnitudes.

## 2. Events recorded with depth 10 km

The catalog has no flag showing that a depth was fixed; the wording is "recorded as".

* 13 646 of 80 929 events (16.9 %) are recorded at 10.0 km; 383 at 0 km.
* Most frequent depth values: 10 (13 646), 2 (12 703), 5 (11 804), 7 (4 130), 8 (3 930),
  15, 20, 12 km. Frequency alone does not prove that these are default values.
* 10 km share by year 6–34 % (highest 1999–2002 and 2018–2020; lowest 2024–2026);
  by magnitude 15 % (3.0–3.4) → 35 % (M ≥ 5.0); by type mb 30 %, ms 37 %, mw 20 %, md 18 %,
  ml 14 %; by region highest at the network edges (34–36°N/46–48°E 45 %), lowest in
  western/central Anatolia (≈ 8 %).

## 3. GK74 reference with the current script

| Item | Value |
|---|---|
| Script | `scripts/decluster_gk74.py` (unchanged), sha256 `d196b6dfdcd2eb0cd4945e78e17ed4caa98ae63ada750a45f1a2981c509135dc` |
| Rule | GK74 Table 1: T = 10^(0.032M+2.7389) d for M ≥ 6.5, else 10^(0.5409M−0.547) d; D = 10^(0.1238M+0.983) km; aftershocks only, forward window, epicentral distance, UTC ms |
| Parameters | `mag_field = "mag"`; EMSC subset declustered on its own |
| Input → main | 80 929 → **35 300** (45 629 removed, 56.4 %) |
| Main ids | stored in `gk74_reference_main_ids.json`; sha256 of the sorted list `af50235202a72a23ff02360a035bfe6df1629d0c8493b98e08b3f9b618886b39` |
| Re-run identical | yes |
| TZ = Europe/Istanbul identical | yes — `parse_time_ms()` reads 'Z'/offset times as given and treats naive (ISC) times as UTC, never the local zone; the test is a regression check of that property (cf. the 2026-09-28 fix), not an independent validation |

Old `data/eq_historical_dc.json` (historical record only): generated 2026-06-24 from a
different catalog version (83 918 events); `src` present; 33 551 EMSC main events, 33 463 of
them also main events in the new reference. The difference mixes catalog version and method.
