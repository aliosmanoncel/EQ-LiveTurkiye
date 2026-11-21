# Kaynak karşılaştırması: statik arşiv ↔ SCEDC FDSN API ↔ USGS ComCat (`catalog=ci`)

Test tarihi: 2026-11-21. Tarayıcıdan, EQ-Live'ın kendi adresinden (aliosmanoncel.github.io) yapıldı. Alan: 32–37° K, 122–114° B.
Eşleştirme olay kimliğiyle (SCEDC EventID = ComCat `ci` + EventID). Eşikler: zaman 15 ms, büyüklük 0,005, konum 0,002°, derinlik 0,06 km.

## 1. Erişim (tarayıcı)
| | SCEDC FDSN API | USGS ComCat |
|---|---|---|
| Tarayıcıdan erişim (CORS) | Çalışıyor | Çalışıyor |
| Sorgu üst sınırı | Görülmedi: 2019 yılı tek sorguda 67 654 olay (63 s); 2021 yılı 23 567 olay (22 s) | 20 000 olay; 2021 yılı (23 548) tek sorguda **HTTP 400** → parçalı sorgu gerekir |

## 2. Olay düzeyinde karşılaştırma (arşiv = anlık görüntü 2026-11-18)
| Ay | Arşiv | SCEDC API | Ortak (API) | USGS ci | Ortak (USGS) | Arşivde var, USGS ci'de yok |
|---|--:|--:|--:|--:|--:|--:|
| 2009-06 | 1 347 | 1 350 | 1 347 | 1 350 | 1 347 | 0 |
| 2021-03 | 1 577 | 1 600 | 1 577 | 1 599 | 1 575 | 2 |
| 2024-08 | 2 601 | 2 616 | 2 601 | 2 608 | 2 593 | 8 |

- **Arşiv ↔ SCEDC API:** ortak olayların tümünde zaman, konum, derinlik ve büyüklük **aynı**. API'nin fazlası yalnızca **negatif büyüklüklü** (M −0,54 … −0,01) olaylar ve `ex` (patlama) türü olaylar; yıllık dosyalar bunları içermiyor.
- **Arşiv ↔ USGS ci:** ortak olayların çoğunda değerler aynı; 2024-08'de 2 olayda farklı çözüm sürümü (ör. derinlik 16,1 → 15,27 km). Arşivdeki bazı olaylar `catalog=ci` sorgusunda **yok**. Örnek: 2024-08-14 M 4,4 (SCEDC 40701191, Nevada sınırı, `GT = r`) ComCat'te Nevada ağının çözümüyle (`nn00882322`) tutuluyor; `ci` kimliği bağlı değil.

## 3. Sonuç
- **USGS ComCat `ci`, SCEDC SCSN kataloğunun birebir karşılığı değildir:** sınır/bölgesel olaylarda başka ağın çözümü yetkili olabilir, çözüm sürümleri farklı olabilir ve 20 000 sınırı vardır.
- **SCEDC FDSN API**, statik arşivle olay olay aynı değerleri veriyor (ek olarak M < 0 ve patlamalar). Tarayıcıdan sınırsız ama büyük yıllarda yavaş (≈1 dk).
- **Statik arşiv** tekrarlanabilirlik için gerekli: API her zaman SCEDC'nin *güncel* sürümünü döndürür; geçmiş kayıtlar değişebilir. Anlık görüntü ise dondurulmuştur.
