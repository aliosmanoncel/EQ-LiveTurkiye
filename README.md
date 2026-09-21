# EQ-LiveTurkiye — Live Seismic Heat Map

**Interactive earthquake heat map for the Euro-Mediterranean region, powered by EMSC data.**

🔴 **Live demo:** [aliosmanoncel.github.io/EQ-LiveTurkiye](https://aliosmanoncel.github.io/EQ-LiveTurkiye/)

---

## Features

- **Seismic heat map** — magnitude-weighted density visualization (EMSC does not currently provide this)
- **Active fault overlay** — MTA 2026 Turkey active fault database (12,963 fault segments; Elmacı et al., Özel Yayın Serisi-60), color-coded by fault type (strike-slip / normal / thrust)
- **Magnitude-scaled circles** — color and size by magnitude class (Minor → Major)
- **EMSC WebSocket live stream** — real-time earthquake events as they are reported
- **Time windows** — Last 1h / 24h / 48h / 1 week
- **Auto-refresh** — GitHub Actions fetches EMSC FDSN data every hour and updates the repository

## Coverage

Follows EMSC monitoring area: **10–75°N, 45°W–120°E** (Euro-Mediterranean + Middle East + Central Asia)

## Data Sources

| Source | Usage |
|--------|-------|
| [EMSC SeismicPortal FDSN](https://www.seismicportal.eu/fdsnws/event/1/) | Historical earthquake catalog (M≥2.0, auto-updated hourly) |
| [EMSC WebSocket](wss://www.seismicportal.eu/standing_order/websocket) | Real-time live event stream |
| [MTA Active Fault Map 2026](https://github.com/aliosmanoncel/fay-yolu-aricilik-veri-bankasi) | Turkey active fault GeoJSON — Elmacı et al., Özel Yayın Serisi-60 |

## Large/Excluded Data Files

Some source data files are intentionally **excluded from git** (see `.gitignore`) — this is a deliberate data-management decision, not a missing or forgotten file. If a file below isn't present locally, regenerate it with its download script.

| File | Source | Produced by | Role | Git policy |
|------|--------|-------------|------|------------|
| `data/eshm20_catalogue_declustered.dbf` | ESHM20 Unified Declustered Catalogue v02a — Danciu et al. (2021), EFEHR Technical Report 001 | `scripts/_download_eshm20_cat.py` | Source/intermediate data — full pan-European catalog (~59,599 events, 113MB). `index.html` never reads this file directly. | Excluded — exceeds GitHub's 100MB limit; regenerate locally if needed. |

**Source vs. derived output:** the `.dbf` above is EFEHR's original data, not ours. `data/eshm20_turkey_historical.json` — this project's own filtered subset (Turkey + surroundings, M≥4.0), produced from that `.dbf` by the same script — **is** committed (small, git-friendly). Keep this distinction when adding similar large source datasets: the raw/source file stays out of git, the processed/derived output goes in.

## How it works

```
GitHub Actions (every hour)
  └── scripts/eq_fetch_turkey.py
        └── EMSC FDSN → data/turkey_eq.json (committed to repo)
              └── index.html reads via raw.githubusercontent.com (no CORS)
```

## Author

**Prof. Dr. Ali Osman Öncel**  
Istanbul University–Cerrahpaşa, Department of Geophysics  
ali.oncel@iuc.edu.tr

*Contribution to EMSC open seismological data visualization.*
