# EQ-LiveTurkiye — Live Seismic Heat Map

**Interactive earthquake heat map for the Euro-Mediterranean region, powered by EMSC data.**

🔴 **Live demo:** [aliosmanoncel.github.io/EQ-LiveTurkiye](https://aliosmanoncel.github.io/EQ-LiveTurkiye/)

---

## Features

- **Seismic heat map** — magnitude-weighted density visualization (EMSC does not currently provide this)
- **Active fault overlay** — MTA 2013 Turkey active fault database (14,565 fault segments), color-coded by fault type (strike-slip / normal / thrust)
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
| [MTA Active Fault Map 2013](https://github.com/aliosmanoncel/fay-yolu-aricilik-veri-bankasi) | Turkey active fault GeoJSON |

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
