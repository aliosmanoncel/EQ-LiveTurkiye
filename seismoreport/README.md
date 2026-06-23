# EQ-LiveTürkiye — Sismik Analiz Yazılım Arşivi

**Geliştirici:** Ali Osman Öncel  
**Kurum:** İstanbul Üniversitesi-Cerrahpaşa, Jeofizik Mühendisliği  
**Proje:** https://aliosmanoncel.github.io/EQ-LiveTurkiye/  
**Tarih:** Haziran 2026

---

## Yazılım Kataloğu

### 1. Veri Çekme

#### `eq_fetch_turkey.py`
Çok kaynaklı deprem kataloğu indiricisi.

| Parametre | Açıklama |
|-----------|----------|
| `--source` | `emsc` / `afad` / `usgs` / `koeri` |
| `--hours`  | Geriye dönük saat sayısı |
| `--minmag` | Minimum büyüklük |
| `--output` | Çıktı JSON dosyası |

**Kaynaklar:**
- **EMSC** (Euro-Akdeniz, 10-75°N, 45°W-120°E) — FDSN standart
- **AFAD** (Türkiye yerel ağı) — custom REST API, il/ilçe bilgisi
- **USGS** (küresel) — FDSN standart
- **KOERI** (Kandilli, Türkiye) — FDSN standart

**Büyüklük homojenizasyonu:** Scordilis (2006) ML/MD→Mw dönüşümü

---

#### `fetch_historical.py`
EMSC'den uzun dönem tarihsel katalog indirir (1998–günümüz).  
Yıllık parçalar halinde çeker, `data/eq_historical.json`'a yazar.

#### `fetch_combined_catalog.py`
Birden fazla kaynak kataloğunu birleştirir, duplikatları temizler.

---

### 2. Declustering (Artçı Sarsıntı Temizleme)

#### `decluster_gk74.py`
**Gardner-Knopoff (1974)** zaman-mesafe penceresi yöntemi.

**Referans:** Gardner & Knopoff (1974) BSSA 64(5): 1363-1367  
**ZMAP7 eşdeğeri:** `+declustering/calc_decluster_gardKnop.m`

| Büyüklük M | Zaman T | Mesafe D |
|------------|---------|----------|
| 3.0 | ~6 gün | ~30 km |
| 5.0 | ~40 gün | ~55 km |
| 6.0 | ~120 gün | ~70 km |
| 7.4 (İzmit) | ~500 gün | ~93 km |

**Giriş:** `data/eq_marmara_catalog.json`  
**Çıktı:** `data/eq_marmara_declustered.json`

---

### 3. b-Değeri Hesaplama

#### `build_bvalue_grid.py`
Gutenberg-Richter b-değeri spatial grid haritası.

**Yöntem A — Fixed Circle (FC):**  
Öncel & Wyss (2000), R=sabit, N≥N_min koşulu  
`python build_bvalue_grid.py --method fc --r 20 --n 50 --mc 2.6`

**Yöntem B — Fixed Number (FN):**  
ZMAP Wiemer (2001), N=sabit, R adaptif  
`python build_bvalue_grid.py --method fn --n 50`

**b-değeri tahmini:** Aki (1965) MLE + Utsu (1966) binom düzeltmesi  
`b = log10(e) / (mean(M) - Mc + 0.05)`

**Parametreler:**

| Flag | Açıklama | Default |
|------|----------|---------|
| `--method` | `fc` veya `fn` | `fc` |
| `--r` | FC yarıçapı (km) | 100 |
| `--n` | Min olay sayısı | 50 |
| `--mc` | Tamamlılık büyüklüğü | 3.0 |
| `--step` | Grid adımı (derece) | 0.09° (~10km) |
| `--minlat/maxlat/minlon/maxlon` | Bölge sınırları | Türkiye |
| `--year_start/year_end` | Dönem filtresi | 1998-2100 |
| `--src` | Kaynak filtresi | EMSC |

**Marmara pilot parametreleri (Öncel & Wyss 2000):**  
`--r 20 --n 50 --mc 2.6 --step 0.045 --minlat 39.5 --maxlat 41.5 --minlon 26.0 --maxlon 32.0`

---

### 4. Spatial İnterpolasyon

#### `build_bvalue_triangulation.py`
**Delaunay Triangülasyonu + Lineer İnterpolasyon**  
scipy.interpolate.LinearNDInterpolator  
*Surfer "Triangulation with Linear Interpolation" eşdeğeri*

- Yalnızca veri noktaları arasında interpolasyon
- Veri dışı alanlar şeffaf (NaN → alpha=0)
- Renk skalası: P10-P90 adaptif

#### `build_bvalue_kriging.py`
**Ordinary Kriging — Gaussian Variogram**  
pykrige.ok.OrdinaryKriging (Matheron 1963, Cressie 1993)

- Tüm alana yayılır (extrapolation dahil)
- Bölge ortalamasına yakınsama
- Variogram parametreleri: sill=veri_varyansı, range=0.5°, nugget=0.01
- **ZMAP7 eşdeğeri:** Kriging modülü

---

### 5. Sismik Tehlike

#### `build_hazard_grid.py`
Campbell (1981) GMPE ile PGA (g) grid haritası.

`ln(PGA) = C1 + C2·Mw + C3·ln(R + C4·exp(C5·Mw))`

**Giriş:** Deprem kataloğu  
**Çıktı:** `data/hazard_grid.json` (her grid noktasında max PGA)

#### `build_hazard_triangulation.py`
Tehlike grid'ini → Delaunay PNG'ye dönüştürür.  
Renk skalası: mavi (0g) → sarı (0.22g) → koyu kırmızı (≥0.4g)

---

### 6. Öngörü (Forecast)

#### `build_forecast_test.py`
**Türkiye geneli prospektif forecast test**

- Eğitim: 1998-2019 b-value haritası
- Test: 2020-2030, M≥5.0 depremleri
- Yöntem: Wiemer & Wyss (2002) b-value forecasting

#### `build_marmara_test.py`
**Marmara pilot prospektif forecast**

- Eğitim: 1998-2018, GK74 declustered, Mc=2.6
- Test: 2019-2030, M≥5.0
- Retrospektif: 2019 M5.7, 2022 M6.1, 2025 M6.2 (doğrulama)
- Prospektif: 2026-06-23 → 2030-06-23 (açık pencere)

---

### 7. Fraktal Boyut

#### `build_fractal_grid.py`
Grassberger-Procaccia (1983) korelasyon boyutu D_c

`C(r) ~ r^D_c`

D_c küçük → sismisitenin düşük boyutlu (fay üzerinde kümelenmiş)  
D_c büyük → sismisitenin dağınık/homojen

---

## Referanslar

| Yöntem | Referans |
|--------|----------|
| b-değeri MLE | Aki (1965) J. Phys. Earth 13: 1-12 |
| Binom düzeltme | Utsu (1966) Geophys. Bull. Hokkaido Univ. 13 |
| Fixed Circle | Öncel & Wyss (2000) Geophys. J. Int. 142: 501-516 |
| Fixed Number (ZMAP) | Wiemer (2001) Seismol. Res. Lett. 72: 373-382 |
| Declustering | Gardner & Knopoff (1974) BSSA 64: 1363-1367 |
| Magnitude conv. | Scordilis (2006) J. Seismol. 10: 225-236 |
| b-value forecast | Wiemer & Wyss (2002) Seismol. Res. Lett. 73: 843-848 |
| Kriging | Matheron (1963) Econ. Geology 58: 1246-1266 |
| Kriging (stats) | Cressie (1993) Statistics for Spatial Data |
| Seismic hazard | Campbell (1981) BSSA 71: 2039-2070 |
| Fraktal boyut | Grassberger & Procaccia (1983) Phys. Rev. Lett. 50: 346 |
| pykrige | Murphy (2014) github.com/GeoStat-Framework/PyKrige |

---

## Kurulum

```bash
pip install scipy numpy matplotlib pillow pykrige
```

## Lisans
MIT — Ali Osman Öncel, İÜC Jeofizik 2026
