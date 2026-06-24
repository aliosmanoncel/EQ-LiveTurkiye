# EQ-LiveTürkiye · İş Akışı Kontrol Listesi
**Güncelleme:** 2026-06-24  
**Prensip:** Her adım bir kez yapılır. Girdi/çıktı değişmedikçe yeniden çalıştırılmaz.

---

## AŞAMA 0 — Veri Kaynakları (Değişmez)

| # | Kaynak | Kapsam | Dosya | Durum |
|---|--------|--------|-------|-------|
| 0a | ISC API | Tüm Türkiye 1900-1997, M≥3.0 | `data/eq_historical.json` içinde birleşik | ✅ |
| 0b | EMSC API | Tüm Türkiye 1998-2026, M≥3.0 | `data/eq_historical.json` içinde birleşik | ✅ |
| 0c | EMSC API | Marmara 1998-2025, M≥2.0 | `data/eq_marmara_catalog.json` | ✅ |
| 0d | EPICA v1.1 | Avrupa 1005-1899 | `data/epica_europe_historical.json` | ✅ |

---

## AŞAMA 1 — Katalog Hazırlık

### 1A · Türkiye Birleşik Katalog
- **Script:** `scripts/fetch_combined_catalog.py`
- **Girdi:** ISC + EMSC API
- **İşlem:** ISC + EMSC birleştirme, Scordilis (2006) Mw dönüşümü (ML/mb→Mw)
- **Çıktı:** `data/eq_historical.json` — 83.918 olay, `mag` (ML) + `mw` (Scordilis) alanları
- **Durum:** ✅ TAMAMLANDI
- **Not:** `mag` = ham ML/mb alanı; `mw` = Scordilis dönüşümü. b hesabında hangisinin kullanılacağı → bkz. Açık Sorular.

### 1B · Türkiye GK74 Declustering
- **Script:** `scripts/build_bvalue_adaptive.py` içi (satır içi GK74, ayrı script değil)
- **Girdi:** `data/eq_historical.json`
- **İşlem:** Gardner-Knopoff (1974) zaman-mesafe pencereleri — artçı/öncüler kaldırıldı
- **Çıktı:** `data/eq_historical_dc.json` — 37.709 mainshock (%55 azalma)
  - Kahramanmaraş 2023: 3.947 → 233 (3.714 artçı silindi)
  - Van 2011: 1.929 → 40 (1.889 artçı silindi)
- **Durum:** ✅ TAMAMLANDI (2026-06-24)
- **⚠ DİKKAT:** Windows'ta `calendar.timegm()` kullan; `datetime.timestamp()` 1970 öncesi olaylar için hata verir.

### 1C · Marmara GK74 Declustering
- **Script:** `scripts/decluster_gk74.py`
- **Girdi:** `data/eq_marmara_catalog.json` (25.206 olay, 1998-2025)
- **İşlem:** GK74, eğitim dönemi 1998-2019 ile sınırlı
- **Çıktı:** `data/eq_marmara_declustered.json` — 9.744 mainshock
- **Durum:** ✅ TAMAMLANDI
- **NOT:** Bu Marmara'ya özgüdür. Türkiye geneli için 1B'yi kullan, bunu değil.

---

## AŞAMA 2 — b-Değeri Hesabı

### 2A · Türkiye Sabit R=100km (ZMAP/FN tarzı)
- **Script:** `scripts/build_bvalue_grid.py`
- **Girdi:** `data/eq_historical.json` (ham, declustered değil — özellik karşılaştırması için)
- **Yöntem:** FC R=100km, Aki (1965) MLE, Mc=3.0, N_min=50
- **Çıktı:** `data/bvalue_grid.json` — 19.719 nokta
- **Durum:** ✅ TAMAMLANDI
- **NOT:** Bu katman declustered değil. Karşılaştırma referansı olarak tutulur.

### 2B · Türkiye Adaptif R (Öncel 2026 Modeli) — Declustered
- **Script:** `scripts/build_bvalue_adaptive.py --input data/eq_historical_dc.json`
- **Girdi:** `data/eq_historical_dc.json` (GK74 declustered)
- **Yöntem:** 3 zon: R=20km (yoğun), R=50km (orta), R=100km (seyrek), Gaussian yumuşatma σ=0.5R
- **Çıktı:** `data/bvalue_grid_adaptive.json` — 2.451 nokta
  - b̄ = 0.910 (ham 1.009'dan düşük → artçılar temizlendi)
  - Yüksek stres (b<0.7): 571 nokta
- **Durum:** ✅ TAMAMLANDI (2026-06-24)
- **Yeniden çalıştırma kriteri:** Katalog güncellenmesi VEYA R/Mc parametresi değişikliği.

### 2C · Marmara FC R=20km (Öncel & Wyss 2000)
- **Script:** `scripts/build_bvalue_grid.py` (Marmara parametreleri)
- **Girdi:** `data/eq_marmara_declustered.json`
- **Yöntem:** FC R=20km, Mc=2.6, N_min=50
- **Çıktı:** `data/bvalue_grid_marmara_mc26.json` — 2.811 nokta
- **Durum:** ✅ TAMAMLANDI

---

## AŞAMA 3 — Görselleştirme

### 3A · Kriging PNG (Türkiye sabit R)
- **Script:** `scripts/build_bvalue_kriging.py`
- **Girdi:** `data/bvalue_grid.json`
- **Çıktı:** `data/bvalue_kriging.png` + `bvalue_kriging_meta.json`
- **Durum:** ✅ TAMAMLANDI

### 3B · Marmara Kriging PNG
- **Script:** `scripts/build_bvalue_kriging.py --input data/bvalue_grid_marmara_mc26.json --output data/bvalue_marmara_mc26.png`
- **Çıktı:** `data/bvalue_marmara_mc26.png`
- **Durum:** ✅ TAMAMLANDI

### 3C · Adaptif Kriging PNG — ÖNERİLMEZ
- **Not:** Adaptif grid seyrek (2.451 nokta) → Kriging aşırı düzleştirir (b aralığı 0.676-1.010 → düz bej).
- **Karar:** Adaptif katman için Kriging değil, `circleMarker` kullan (index.html'de halihazırda uygulandı).
- **Durum:** ⛔ YAPILMAYACAK

### 3D · Forecast Testi (Marmara + Türkiye)
- **Script:** `scripts/build_marmara_test.py`, `scripts/build_forecast_test.py`
- **Çıktı:** `data/forecast_marmara_test_events.json`
- **Durum:** ✅ TAMAMLANDI

---

## AŞAMA 4 — Platform (index.html) Katmanları

| Katman | Veri | Görsel | Durum |
|--------|------|--------|-------|
| Deprem noktaları (canlı) | EMSC/AFAD API | circleMarker | ✅ |
| Tarihsel depremler | `eq_historical.json` | circleMarker | ✅ |
| EPICA tarihsel | `epica_europe_historical.json` | circleMarker | ✅ |
| b-value (sabit R) | `bvalue_kriging.png` | imageOverlay | ✅ |
| b-Adaptif (Öncel 2026) | `bvalue_grid_adaptive.json` | circleMarker + triyaj | ✅ |
| Marmara FC | `bvalue_grid_marmara_mc26.json` | circleMarker | ✅ |
| Fraktal Dc | `fractal_grid.json` | circleMarker | ✅ |
| ESHM20 WMS | Harici URL | WMS tile | ✅ |
| ESRM20 WMS | Harici URL | WMS tile | ✅ |
| AFAD TSTH WMS | Harici URL | WMS tile | ✅ |
| Forecast overlay | `forecast_marmara_test_events.json` | circleMarker | ✅ |

---

## AÇIK SORULAR (Yapılacaklar)

| # | Konu | Öncelik | Not |
|---|------|---------|-----|
| A | **mag → mw:** b hesabında `mag`(ML) değil `mw` alanı kullanılmalı | Yüksek | Mc=3.0(ML) → Mc≈2.5(Mw) olur; bvalue_grid.json ve bvalue_grid_adaptive.json yeniden üretilmeli |
| B | **TL katmanı:** b + a → Yerel Yineleme Süresi haritası | Orta | Öncel & Wyss (2001) formülü; yeni script gerekli |
| C | **Turuncu zon (R=50km) boş:** N_min=50 ile 0 nokta üretiliyor | Düşük | N_min=30 dene veya THR_MID'i ayarla |
| D | **Marmara DC'yi Türkiye geneline entegre:** `eq_marmara_declustered.json` zaten var; Türkiye DC bunu kapsar, çakışma yok | Bilgi |  |

---

## KURAL: Yeniden Çalıştırma Kriterleri

Bir adımı yeniden çalıştırmadan önce sor:
1. **Girdi değişti mi?** (yeni katalog, farklı tarih aralığı)
2. **Parametre değişti mi?** (Mc, R, N_min)
3. **Çıktı dosyası bozuk/eksik mi?**

Eğer üçü de hayırsa → yeniden çalıştırma **gerekmez**.
