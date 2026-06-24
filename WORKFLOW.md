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
- - **Durum:** ✅ TAMAMLANDI (2026-06-24) — Mw bazlı versiyon hesaplanıyor (bkz. 2B-Mw)
- **Yeniden çalıştırma kriteri:** Katalog güncellenmesi VEYA R/Mc parametresi değişikliği.

### 2B-Mw · Türkiye Adaptif R — Mw Bazlı (Nihai Versiyon)
- **Script:** `scripts/build_bvalue_adaptive.py --input data/eq_historical_dc.json --output data/bvalue_grid_adaptive_mw.json`
- **Yöntem:** Aynı adaptif R modeli; `mw` alanı kullanılır; `mag`(ML) fallback
- **Mc Kalibrasyonu (Scordilis Kuadratik Düzeltmesi):**
  - Scordilis (2006) kuadratik form: `Mw = 0.0376×ML² + 0.646×ML − 0.269`
  - ML 3.0 → Mw 2.007 (fiziksel eşdeğer, hatalı değil)
  - Bu nedenle: **Mc = 2.0 (Mw) ≡ Mc = 3.0 (ML)** — aynı olay seti, farklı birim
  - Mc=2.5(Mw) denendi → 246 nokta, b̄=0.38 (N<50 kısıtı, ISC boşlukları)
  - Mc=3.0(Mw) denendi → 17 nokta (sadece büyük depremler dahil)
  - **Karar: Mc=2.0(Mw)** — 37.705 olay, ML bazlı ile eşdeğer
- **Çıktı:** `data/bvalue_grid_adaptive_mw.json` → `data/bvalue_grid_adaptive.json` (platform dosyası)
  - 2451 nokta | b̄ = 0.737 | b aralığı: 0.215 – 4.270
  - Yüksek stres (b<0.7): **1136 nokta** (ML bazlı 571'den +%99 artış)
  - Marmara b̄: 1.046 (ML) → **0.855 (Mw)** | min-b: 0.863 → **0.618 @ (40.5°N, 28.8°E)**
  - DAFZ b̄: 0.988 (ML) → **0.823 (Mw)**
- **Durum:** ✅ TAMAMLANDI (2026-06-24) — platform güncellendi

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

## Mc KALİBRASYON TABLOSU (Sabit Referans)

> Kaynak: Öncel & Wyss (2000, 2001), MARNET katalog analizleri, ZMAP zaman bazlı hesaplar

| Bölge | Dönem | Mc | Yöntem | Not |
|-------|-------|----|--------|-----|
| Türkiye geneli (ISC) | 1900–1960 | ≥ 5.5 | Tarihsel | Büyük deprem tamamlılığı |
| Türkiye geneli (ISC) | 1960–1997 | ≥ 4.5 | Aletsel | Orta büyüklük tamamlılığı |
| Türkiye geneli (EMSC) | 1998–2026 | 3.0 | Modern ağ | b hesabında kullanılan eşik |
| Marmara (MARNET) | 1981–1989 | **2.6** | ZMAP | En güvenilir mikrosismisite dönemi |
| Marmara (MARNET) | 1990–1998 | **2.9** | ZMAP | 0.3 mag kayması sonrası eşik |
| Marmara (MARNET) | 1991–1999 dinamik | 2.5–2.8 | ZMAP | Muhafazakâr sınır: 2.9 kullanıldı |
| Doğu-Batı gradyanı | Marmara içi | 2.6→3.0+ | Mekânsal | Batıdan doğuya sistematik artış |

**Karar:** b hesabı eşikleri — Marmara: `Mc=2.6`, Türkiye adaptif: `Mc=3.0(ML)` → Açık Soru A'dan sonra `Mc≈2.5(Mw)`.

---

## HİBRİT KATALOG STRATEJİSİ (Onaylandı 2026-06-24)

> Kaynak: NotebookLM değerlendirmesi + Öncel metodolojisi

| Kaynak | Kullanım | Büyüklük Eşiği | Gerekçe |
|--------|----------|----------------|---------|
| ISC (1900-1997) | Tarihsel hafıza, sismik boşluk | **M ≥ 4.5** (1960+), **M ≥ 5.5** (1900-1960) | 2000 yıllık Mw>6 tamamlılığı |
| EMSC (1998-2026) | Mikrosismisite, asperite | **M ≥ 3.0** (Türkiye), **M ≥ 2.6** (Marmara) | Modern ağ hassasiyeti |
| Dönüşüm | Her iki kaynak | ML/mb/Ms → **Mw** (Scordilis 2006) | Ortak enerji ölçeği |

**Durum:** `fetch_combined_catalog.py` zaten ISC+EMSC birleşimini yapıyor (✅). Eksik: Mc'nin döneme göre dinamik uygulanması → Açık Soru A.

---

## AÇIK SORULAR (Yapılacaklar)

| # | Konu | Öncelik | Not |
|---|------|---------|-----|
| A | **mag → mw geçişi:** TAMAMLANDI — Mc=2.0(Mw)≡Mc=3.0(ML). `bvalue_grid_adaptive_mw.json` hesaplanıyor | **Yüksek** → 🔄 | Scordilis kuadratik: ML3.0→Mw2.0. 37.705 olay korundu. Sonuç onaylanınca `bvalue_grid_adaptive.json` → mw versiyonuyla değiştirilecek |
| B | **TL katmanı:** b + a → Yerel Yineleme Süresi haritası | ✅ TAMAMLANDI | `build_tl_adaptive.py` + Triple-Target (6.8/7.4/7.8) + `tl_grid_adaptive.json` (2026-06-24) |
| C | **Turuncu zon (R=50km) boş:** N_min=50 ile 0 nokta üretiliyor | Düşük | N_min=30 dene veya THR_MID=5 → 3'e düşür |
| D | **Marmara DC'yi Türkiye geneline entegre:** `eq_marmara_declustered.json` zaten var; Türkiye DC bunu kapsar, çakışma yok | Bilgi | Yeniden yapılmaz |
| E | **Tarihsel Derinlik Güven Endeksi** katmanı: Marmara=yeşil(2000yr), KAFZ=sarı(500yr), DAFZ=kırmızı(200yr) | ✅ TAMAMLANDI | `historical_confidence_index.json` + `🛡 Veri Güveni` butonu (2026-06-24) |
| F | **SeismoReport Bölüm 12:** Katalog Kalibrasyonu — Mc paradoksu, Scordilis kuadratik düzeltmesi, N<50 kısıtı kanıtları | ✅ TAMAMLANDI | WORKFLOW.md Bölüm 12 olarak dokümante edildi (2026-06-24) |

---

## TARİHSEL TAMAMLILIK KARAR TABLOSU (Onaylandı 2026-06-24)

> Kaynak: Meghraoui vd. (2021), Ambraseys (2002), Parsons (2004), NotebookLM değerlendirmesi

| Bölge | Güvenli Pencere | Mc (tamamlık) | Gerekçe |
|-------|----------------|---------------|---------|
| Marmara | **son 2000 yıl** | Mw > 6.0 | Bizans-Osmanlı arşivi + Ayasofya "sismometre" + paleosismoloji (sismoturbiditler) |
| Batı Anadolu | ~1000 yıl | Mw > 6.5 | Antik kentler (Efes, Bergama) kısmi kayıt sağlar |
| KAFZ (Doğu Marmara) | ~500 yıl | Mw > 6.0 | 1509, 1766, 1894 kayıtları güvenilir |
| DAFZ (Doğu Anadolu) | ~200 yıl | Mw > 6.5 | Tarihsel boşluklar; Türkoğlu seg. ancak modern çalışmalarla netleşti |
| İç Anadolu platosu | ~1900 (aletsel) | Mw > 5.5 | Yazılı kayıt seyrekligi |
| **Türkiye geneli (bizim model)** | **1900–2026** | **Mw ≥ 3.0** | ISC+EMSC birleşik aletsel dönem — muhafazakâr & izlenebilir |

**Karar:** b-Adaptif modeli için 1900-2026 aletsel dönem esas. Marmara'ya özgü 3.7m sismik borç hesabında tarihsel derinlik (1766 miladı) ayrıca kullanılır.

**Platform önerisi:** "Tarihsel Derinlik Güven Endeksi" katmanı — bölgeye göre renk kodlu güvenilirlik (yeşil=Marmara/2000yr, sarı=KAFZ/500yr, kırmızı=DAFZ/200yr). → Açık Soru E olarak eklendi.

---

## BÖLÜM 12 — Katalog Kalibrasyonu ve Mc Paradoksu (Onaylandı 2026-06-24)

> Kaynak: NotebookLM değerlendirmesi (2026-06-24) + Öncel & Wyss (2000) metodolojisi

### 12.1 Scordilis (2006) Kuadratik Dönüşümü

Türkiye birleşik kataloğunda büyüklük homojenizasyonu için **Scordilis (2006)** denklemi kullanılmıştır:

**Küçük büyüklükler (ML ≤ 3.5):**  
`Mw = 0.0376 × ML² + 0.646 × ML − 0.269`

**Kritik kalibrasyon noktası:**  
`ML = 3.0 → Mw = 0.0376×9 + 0.646×3 − 0.269 ≈ 2.007`

Bu **doğrusal olmayan** (kuadratik) form, küçük depremlerde sismik momentin yerel büyüklüğe göre daha yavaş arttığını yansıtır. ML 3.0 ≡ Mw 2.0 fiziksel eşdeğerliktir — veri kaybı değil, doğru ölçek dönüşümüdür.

### 12.2 Mc Paradoksu ve Çözümü

| Deneme | Mc (Mw) | Hesaplanan Nokta | Sonuç |
|--------|---------|-----------------|-------|
| 1. deneme | Mc = 3.0 (Mw) | 17 nokta | ❌ Mw ölçeğinde çok büyük — sadece M>7 olayları filtreler |
| 2. deneme | Mc = 2.5 (Mw) | 246 nokta | ❌ ISC (1900-1997) veri boşlukları → N<50 kısıtı aşılamıyor |
| **Çözüm** | **Mc = 2.0 (Mw)** | **2451 nokta** | ✅ ML=3.0 eşdeğeri — 37.709 olay, Aki (1965) kriteri sağlandı |

**Paradoksun kaynağı:** ISC kataloğunda 1900-1997 dönemi için tamamlılık eşiği ML≥4.5 (1960 öncesi ML≥5.5). Bu döneme ait grid hücrelerinde Mw≥2.5 filtresi uygulandığında çoğu hücrede N<50 kalıyor → b hesabı yapılamıyor.

**Çözümün gerekçesi:** Mw=2.0 (≡ ML=3.0) eşiği, EMSC (1998-2026) dönemi için yeterli veri yoğunluğu sağlıyor. ISC dönemi tarihsel hafıza olarak yoğunluk haritasında kalıyor (Aşama 1 — sismisite yoğunluk).

### 12.3 Aki (1965) MLE b-Değeri Kriteri

```
b = log10(e) / (mean(Mw) - Mc_eff)
Mc_eff = Mc - 0.05   [Utsu 1966 binom düzeltmesi]
N_min = 50           [Aki 1965 istatistiksel güvenilirlik eşiği]
```

N<50 olan grid noktaları hesaplanmadan atlanır. Mw=2.0 ile 2451/18291 (%13.4) noktada N≥50 sağlandı.

### 12.4 Kumburgaz Anomalisinin Kalibrasyona Bağlılığı

| Kalibrasyon | Kumburgaz (40.5°N, 28.8°E) b-değeri |
|-------------|--------------------------------------|
| ML ölçeği (Mc=3.0 ML) | b = 0.863 |
| **Mw ölçeği (Mc=2.0 Mw)** | **b = 0.618** ← doğru kalibrasyon |

Mw kalibrasyonu, Kumburgaz'daki gerçek stres kilitlenmesini ortaya çıkardı. ML ölçeğinde b=0.863 görünen sinyal, Mw ölçeğinde b=0.618'e indi → **%28 daha düşük b = %28 daha yüksek stres yoğunluğu.**

Bu anomali, Marmara'nın 3.7 m sismik borcunun tahsil edileceği "çekirdeklenme odağını" işaret eder (Öncel & Wyss 2000, GJI 143).

### 12.5 Metodolojik Özet

```
Scordilis (2006):  ML 3.0 → Mw 2.0   [fiziksel eşdeğerlik]
Mc kalibrasyonu:   Mw 2.0             [optimum: N≥50 + veri bütünlüğü]
Katalog:           37.709 mainshock   [GK74 declustered, 1900-2026]
Grid:              2451 nokta         [%13.4 kapsam — sadece yeterli veri]
b̄ (Türkiye):      0.737              [Mw ölçeğinde]
Kumburgaz:         b = 0.618          [Marmara T_L minimumu, Mw 7.4 → 4.734 yr]
```

**Açık Soru F → TAMAMLANDI** ✅

---

## KURAL: Yeniden Çalıştırma Kriterleri

Bir adımı yeniden çalıştırmadan önce sor:
1. **Girdi değişti mi?** (yeni katalog, farklı tarih aralığı)
2. **Parametre değişti mi?** (Mc, R, N_min)
3. **Çıktı dosyası bozuk/eksik mi?**

Eğer üçü de hayırsa → yeniden çalıştırma **gerekmez**.
