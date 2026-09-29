# Katmanlı b-değeri duyarlılık sonuçları — 2026-09-29

Kahramanmaraş–Şanlıurfa bölgesi (daire, merkez 37.42°, 38.87°, R = 75 km), EMSC canlı sorgu.
Hesaplar Chrome'daki **donmuş tek olay kümesinde** yapıldı (sekme yeniden sorgulanmadı).

## Veri kümesi (dondurulmuş)

| Alan | Değer |
|---|---|
| Ham olay sayısı | 2673 (FNV-1a parmak izi `9e0ee193`, sıralı `zaman|enlem|boylam|mag|mtype`) |
| Zaman aralığı | 1998-01-25T00:55:05Z – 2026-09-28T04:51:20Z |
| Yinelenen kayıt | 1 |
| Analiz penceresi | `regionWindowStart` 883605600000, `regionWindowEnd` 1790715599000 (ms) |
| GK74 sonrası | 1469 olay (MD 571, dönüştürülmemiş ML<1,7 174) |
| Dönüşüm | Birleşik Dispatch (Scordilis 2006 mb/Ms + Çıvgın & Scordilis 2019 ML) |
| Ham mtype sayımları | ml 1643, MD 901, ML 83, md 27, mw 7, mb 6, Mc 2, m 1, mc 1, Ms 1, Mw 1 |

Poster (2026-09-24 kataloğu) ile fark: ham 2657 → 2673, b 0.499 → 0.426. Poster değeri bu kümeden
yeniden üretilemez; aşağıdaki "mevcut yöntem" satırı bugünkü kümenin karşılığıdır.

## T_i (Weichert gözlem süresi, yıl) — mevcut basamaklar 3.5 / 2.2 / 2.1 / 0.0

| Sınıf | 0.0–2.0 | 2.1 | 2.2–3.4 | ≥ 3.5 |
|---|---|---|---|---|
| T_i | 3.032 | 12.744 | 21.247 | 27.744 |

Dönem süreleri: 6.497 / 8.504 / 9.711 / 3.032 yıl. Birikimli T_i ile birebir tutarlı.
Dönem başına veri Mc'si (MAXC + 0,2): 3.3 / 3.1 / 2.4 / 1.6.

## Dört katman (her satırda tek etken değişir; zaman penceresi hep 1999–2026)

b: Weichert (1980), tüm sınıflar; D/sd: Poisson sapması / (K − 2); "öneri": b(M_min) kararlılık ölçütü.

| Katman | Basamaklar | N | b ± σ (tüm sınıflar) | D/sd | b(t) ort. / 2023+ | Önerilen M_min → b ± σ (N) | b(t) @ öneri |
|---|---|---|---|---|---|---|---|
| **L0 mevcut katalog (arşiv)** | 3.5/2.2/2.1/0.0 | 1371 | **0.426 ± 0.010** | 20.35 | 0.63 / 0.27 | plato yok | — |
| L0 | veri: 3.5/3.1/2.4/1.6 | 483 | 0.650 ± 0.024 | 5.26 | 1.06 / 0.70 | 2.9 → 1.07 ± 0.07 (215) | 1.45 [0.92–1.80] |
| L0b yalnız ML<1,7 hariç | 3.5/2.2/2.1/0.0 | 1199 | 0.670 ± 0.019 | 13.82 | 0.69 / 0.24 | — | — |
| **L1 MD hariç** | 3.5/2.2/2.1/0.0 | 845 | 0.510 ± 0.014 | 9.64 | 0.64 / 0.26 | **2.4 → 0.97 ± 0.05 (389)** | 0.97 [0.72–1.16] |
| L1 | veri: 3.5/2.4/2.4/1.6 | 484 | 0.746 ± 0.028 | 4.49 | 0.90 / 0.70 | 2.4 → 0.97 ± 0.05 (389) | 0.97 [0.72–1.16] |
| **L2 MD + ML<1,7 hariç** | 3.5/2.2/2.1/0.0 | 673 | 0.852 ± 0.030 | 2.77 | 0.75 / 0.23 | 2.4 → 0.97 ± 0.05 (389) | 0.97 [0.72–1.16] |
| L2 | veri: 3.5/2.4/2.4/2.2 | 404 | 0.933 ± 0.044 | 2.71 | 0.96 / — | 2.4 → 0.97 ± 0.05 (389) | 0.97 [0.72–1.16] |
| L3 doğrulanmış MD→Mw | — | — | **beklemede** | — | — | — | — |

L3: yayımlanmış, bölge ve katalogla uyumlu bir MD→Mw bağıntısı kaynak doğrulamasıyla seçilene kadar uygulanmaz.

## Mevcut basamaklarla M_min taraması (L0, tüm tipler)

| M_min | 1.5 | 2.0 | 2.2 | 2.5 | 2.8 | 3.0 | 3.2 | 3.5 | 3.8 |
|---|---|---|---|---|---|---|---|---|---|
| b | 0.60 | 0.70 | 0.74 | 1.02 | 1.47 | 1.51 | 1.14 | 0.87 | 0.50 |
| N | 1239 | 1166 | 1079 | 840 | 543 | 289 | 125 | 57 | 25 |
| D/sd | 15.7 | 13.8 | 13.8 | 7.6 | 2.5 | 2.6 | 1.9 | 1.7 | 1.6 |

M ≈ 3.0'daki tümsek MD olaylarından: MD alt kümesinde b = 1.5–2.0 (M_min 2.8–3.3); MD sayımları 2.8–2.9'da tepe yapar
(2005–2014 dönemindeki 698 olayın 513'ü MD, 1999–2012).

## Yorum sınırları

- L1/L2'deki b ≈ 0.97 platosu (M_min 2.4–2.5) zaman penceresi değiştirilmeden, yalnız MD çıkarılarak elde edildi;
  yine de "doğru b = 1" olarak değil, **teşhis sinyali** olarak raporlanmalı.
- D/sd hiçbir katmanda ≈ 1'e inmiyor (en düşük ≈ 2.1–2.7): kalan uyumsuzluk için GK74 ve 2023 dizisi test edilmedi.
- MD hariç kümede M_min ≥ 2.9 için b yeniden düşüyor (N < 120); açık konu.
- Senaryo hesapları yama çekirdek fonksiyonlarının canlı sayfaya salt okunur enjeksiyonuyla yapıldı; L0 satırı canlı sitenin
  kendi çıktısıyla birebir eşleşti (b = 0.4256).
