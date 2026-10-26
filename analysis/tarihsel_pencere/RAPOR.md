# Düzeltme: tarihsel pencere seçim listesi canlı zaman düğmesiyle temizlenmiyordu (2026-10-26)

**Dal:** `tarihsel-pencere-secimi` (`main`'den, küresel ISC-GEM işinden bağımsız). `main`'e birleştirilmedi.

## Hata
Bir canlı zaman düğmesine (1s, 24s, 1 Hafta, 1 Ay, 90 Gün, 1 Yıl) basılınca tarihsel düğmelerin vurgusu kalkıyordu, ama seçim listesi (`activeHistWindows`) temizlenmiyordu. İki sonucu vardı:
- **A — görünmeyen pencere birleşime giriyordu.** Sıra: EMSC 1998 → 1 Ay → ISC 1900. Ekranda yalnız "ISC 1900–1970" vurguluyken 81 591 olay (EMSC+ISC) gösteriliyordu; doğrusu 662 olay (ISC).
- **B — yeniden basış pencereyi kapatıyordu.** Sıra: ISC 1900 → 1 Ay → ISC 1900. İkinci basış pencereyi açmak yerine listeden çıkarıyordu ve tarihsel mod açılmıyordu.

## Düzeltme
`index.html`, canlı zaman düğmesi işleyicisinde tek satır: `activeHistWindows = [];`. Bu satır, vurgu kaldırma satırının hemen ardından gelir.

## Testler
**Tarayıcı kabul testi** `kabul_pencere_secimi.js` (Playwright; sonuç `kabul_sonuc.json`): 9/9 geçti.
- **Yöntem:** Aynı senaryolar düzeltme öncesi (`main`) ve sonrası sayfada çalıştırıldı.
- **Hata önce yeniden üretildi:** A'da N 81 591, liste 2 pencere; B'de pencere açılmadı.
- **Sonra:**
  - A'da N 662, yalnız ISC.
  - B'de pencere açıldı (N 662).
  - "1 Ay" sonrasında liste boş, tarihsel mod kapalı.
- **Gerileme:** Tek pencere, çoklu seçim ve aç-kapa senaryoları önce ve sonra birebir aynı (N 662, 7 404, 662).
- **Sayfa hatası:** Yok.

**Birim testleri** (`scripts/test_*.js`): `test_fit_range.js` dışında hepsi geçti. `test_fit_range.js` düzeltmeden önce de çalışmıyordu: depoda bulunmayan `csBvalueTimeSeries` fonksiyonunu arıyor. Bu düzeltmeyle ve küresel ISC-GEM değişikliğiyle ilgisi yok.

**Kapsam dışı:** Canlı veri akışı ve harita karoları sınanmadı (test ortamında ağ engelli). Düzeltme bu yollara dokunmuyor.
