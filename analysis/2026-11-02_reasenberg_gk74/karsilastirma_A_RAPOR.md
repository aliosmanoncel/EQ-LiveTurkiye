# Design A — GK74 vs Reasenberg (`zmap`), event by event (steps 1–2)

**Conditional on a heterogeneous magnitude scale** (mixed ML/MD/mb/Mw `mag`, M ≥ 3.0).
Event-level differences on identical input are algorithmic by construction; their
physical meaning, the aftershock fractions and any b-value change are not interpreted here.
Read-only: EQ-LiveTürkiye unchanged; `reasenberg.py` v0.3.0 unchanged
(sha256 `c5b1248af557f29b4f04bf7c6ed9adfefd97c4153975a8989804b872ccf99bc9`).

## Input and settings

| Item | Value |
|---|---|
| Input | 80 929 EMSC events of `eq_historical.json` (sha256 `bd303aa3…545b`), same set for both methods |
| GK74 | reference from prep revision 2: 35 300 main events (`gk74_reference_main_ids.json`) |
| Reasenberg | `rule="zmap"`, xmeff = 3.0, rfact = 10, xk = 0.5, τmin = 1 d, τmax = 10 d, P = 0.95, tie = first |
| Assumptions | depths as recorded; err = derr = 0 (no errors in the catalog; documented assumption, not "errors are zero") |
| Files | `compare_A.py` (`1e7a1336…2b54`), `compare_A_results.json` (`1cc35eeb…7a40`), `compare_A_differing_events.csv` (31 310 events, `839a421e…63cb`) |

## Step 1 — memberships

| | GK74 | Reasenberg |
|---|---|---|
| Independent events | 35 300 | 65 942 (63 862 single + 2 080 cluster representatives) |
| Removed fraction | 56.4 % | 18.5 % |

| Category | Events |
|---|---|
| Independent in both | 34 966 |
| Dependent in both | 14 653 |
| Independent only in Reasenberg (GK74 aftershock) | **30 976** — 29 893 Reasenberg singles, 1 083 representatives |
| Independent only in GK74 | **334** — all Reasenberg dependents, 235 of them Reasenberg **foreshocks** |

Agreement rate 61.3 %; Jaccard index of the independent sets 0.528.
The GK74 independent set is almost entirely contained in the Reasenberg independent set:
the disagreement is one-directional. The 334 GK74-only events are mostly explained by
the GK74 variant used in EQ-Live removing aftershocks only (foreshocks kept), whereas
Reasenberg clusters include foreshocks.

## Step 2 — where the differing events are

Fraction of events in each group that are independent only in Reasenberg (R-only):

* **Magnitude:** 41.4 % (M 3.0–3.4), 34.2 % (3.5–3.9), 25.7 % (4.0–4.9), 12.9 % (M ≥ 5.0).
  GK74-only rises with magnitude: 0.3 % → 5.0 % (M ≥ 5.0: 25 of 498 events).
* **Magnitude type:** md 42.2 %, ml 37.4 %, mb 26.8 %, mw 23.9 % (types overlap with magnitude).
* **Time:** 19.5 % (2025) to 50.0 % (2023, Kahramanmaraş sequence year); no single trend.
* **Region (2° cells, n ≥ 500):** highest in the southern Aegean / Hellenic arc
  (34–36°N 26–28°E 55.6 %, 34–36°N 24–26°E 50.2 %) and 40–42°N 30–32°E (51.1 %);
  lowest 36–38°N 24–26°E (13.6 %), 40–42°N 34–36°E (21.1 %).
* **Depth recorded as 10 km:** 37.3 % vs 38.5 % for other depths — no marked difference
  in this breakdown.

## Diagnostic: what drives the gap (not a substitute for steps 3–4)

| Reasenberg variant | Removed | R-only | GK-only | Jaccard |
|---|---|---|---|---|
| Primary (recorded depths, err = 0) | 18.5 % | 30 976 | 334 | 0.528 |
| Epicentral (all depths set equal), err = 0 | 24.8 % | 26 145 | 622 | 0.564 |
| Recorded depths, ZMAP errors (err 1.5, derr 2 km) | 27.1 % | 24 529 | 802 | 0.577 |
| Epicentral + err 1.5 km | 31.1 % | 21 541 | 1 111 | 0.602 |
| *GK74* | *56.4 %* | | | |

(`diag_drivers.py` `2fc8344e…4d96`, `diag_drivers.json` `98eb7205…9c08`.)

Reading: the depth and location-error assumptions each change Reasenberg's result
substantially (+6 and +9 percentage points removed), but even together they close only
about a third of the gap. Most of the difference is intrinsic to the method definitions
at these magnitudes: for an M 3.0 event GK74 uses ≈ 23 km and ≈ 12 days; Reasenberg links
within 10·r(3.0) ≈ 1.7 km (plus error terms) and 1–10 days. The "epicentral" variant sets
all depths equal; it is a diagnostic of depth influence, not the planned step-4 treatment
of suspicious depths.

## Not yet done (approved order)

3. Design B subsets (thresholds to be confirmed after the GFT correction).
4. Depth sensitivity with suspicious depths identified from evidence.
5. b-values from representatives; equivalent events as a separate sensitivity output.
6. Combined report.
