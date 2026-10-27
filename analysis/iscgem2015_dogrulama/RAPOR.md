# `iscgem2015` bağıntısının kaynak makaleyle doğrulanması (2026-10-27)

**Kaynak:** Di Giacomo, D., Bondár, I., Storchak, D. A., Engdahl, E. R., Bormann, P. & Harris, J. (2015). ISC-GEM: Global Instrumental Earthquake Catalogue (1900–2009), III. Re-computed MS and mb, proxy MW, final magnitude composition and completeness assessment. *Phys. Earth Planet. Inter.* 239, 33–47. doi:10.1016/j.pepi.2014.06.005.
- Tam metin kullanıcının Zotero arşivinden alındı.
- Metin çıkarımında eksi işaretleri bozuluyordu (yazı tipi eşlemesi). Bu yüzden eşitlikler sayfa görüntüsünden okundu: `es1_s40.png`, `es2_s42.png`.

**İncelenen kod:** `index.html`, `MAG_CONVERSIONS.iscgem2015` ve `MS_DEPTH_LIMIT.iscgem2015`. Kodda değişiklik yapılmadı.

## Sonuç
**Katsayılar ve işaretler doğru; hesaplama hatası yok.** Düzeltilmesi gereken yalnız iki metin ayrıntısı var (§2).

## 1. Doğrulananlar

| Konu | Makale | EQ-Live | Sonuç |
|---|---|---|---|
| Eş. (1) Ms → Mw | Mw = e^(−0,222 + 0,233·Ms) + 2,863 (s. 40) | `Math.exp(-0.222 + 0.233*m) + 2.863` | ✔ birebir |
| Eş. (2) mb → Mw | Mw = exp(−4,664 + 0,859·mb) + 4,555 (s. 42) | `Math.exp(-4.664 + 0.859*m) + 4.555` | ✔ birebir |
| Model biçimi | Üstel, My = e^(a + b·Mx) + c, doğrusal olmayan en küçük kareler; GCMT Mw'ye karşı (s. 40) | Aynı biçim | ✔ |
| Ms derinlik koşulu | Ms yalnız derinlik − derinlik belirsizliği ≤ 60 km için yeniden hesaplandı (s. 36) | h ≤ 60 km (σh yok; daha katı) | ✔ (kodda doğru belgelenmiş) |
| mb derinlik | mb derin depremler için de kullanılır; Ms yoksa vekil kaynağı mb'dir (s. 42) | mb tüm derinlikler | ✔ |
| Öncelik | Vekil yalnız doğrudan Mw yoksa (s. 41); mb yalnız Ms yoksa (s. 42) | Mw türündeki olaylar dönüştürülmez | ✔ |
| Ms üst sınırı | Ms 8–8,5 arasında yalnız 4 olay kullanıldı; Ms doygunluğu, 1960 Valdivia'nın vekili belirgin biçimde düşük (s. 41) | Ms ≤ 8,5 | ✔ |
| mb üst sınırı | Şekil 14: üstel model ile medyan eğrisi 4,6 < mb < 6,5 aralığında iyi uyumlu (s. 42); mb Mw 6 üstünde doygun | mb ≤ 6,5 | ✔ |

**Ek bilgi (kodda yok, kayda değer):**
- Katsayıların standart hataları: Eş. (1) için a, b, c = 0,043, 0,004, 0,056; Eş. (2) için 0,085, 0,012, 0,017.
- Doğrulama kümesinde gerçek Mw − vekil ortancası 0,01; SMAD 0,13 (üstel, Ms).

**Örnek değerler:**
- Ms 5 → 5,43; Ms 6 → 6,10; Ms 7 → 6,95; Ms 8 → 8,03.
- mb 4,6 → 5,05; mb 5 → 5,25; mb 6 → 6,19; mb 6,5 → 7,06.

## 2. Düzeltilmesi gereken metin ayrıntıları (öneri; uygulanmadı)
1. **Sayfa atfı.** Kodda "(s. 41–42)" yazıyor. Doğrusu: Eş. (1) **s. 40**, Eş. (2) **s. 42**.
2. **Alt sınırların kaynağı.** `validRange` metni "mb: 3,5–6,5 · Ms: 3,0–8,5" aralıklarını geçerlilik aralığı gibi veriyor. Oysa:
   - **Ms 3,0 ve mb 3,5 alt sınırları makalede yok.** Bunlar EQ-Live'ın tercihi; gerekçesi kodda yazılı: yalnız M ≥ 5 dönüştürülürse 4,95–5,2 arasında boşluk oluşuyor.
   - **Makaledeki "M < 5 için dikkat" uyarısı** Ms modeli için yazılmış (s. 41).
   - **mb için makalenin verdiği aralık** iyi uyum aralığı 4,6 < mb < 6,5 (Şekil 14).
   - **Önerilen metin:** "Makale: Ms modeli M < 5'te dikkatle kullanılmalı (s. 41); mb modeli 4,6 < mb < 6,5'te medyana iyi uyumlu (Şekil 14). Alt sınırlar Ms 3,0 / mb 3,5 EQ-Live tercihidir (makalede yok)."

Bu iki düzeltme yalnız açıklama metnini değiştirir; hiçbir hesap sonucunu değiştirmez.

## 3. Sınırlar
- Vekil Mw'nin olay başına bağımsız sınaması yapılamadı: ISC-GEM CSV'si olayların yeniden hesaplanmış Ms ve mb değerlerini vermiyor.
- Bağıntıların ISC-GEM dışı ajans büyüklüklerine (USGS, EMSC, Türkiye ajansları) aktarımı bu doğrulamanın kapsamı dışında. Bu bir varsayım olarak kalıyor (kodda da belirtilmiş).
