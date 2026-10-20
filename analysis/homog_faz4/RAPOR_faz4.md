# Faz 4 — Tamlık merdiveninin değerlendirilmesi (2026-10-21)

**Durum:** değerlendirme; merdiven değiştirilmedi, üretime geçilmedi. Girdi: sabitlenmiş prototip (`homog-faz0` @ `f09b26c`), GK74 sonrası, bitiş 2021-12-31. Betik `faz4_merdiven.py`, sonuç `out/merdiven_degerlendirme.json`.

## Önceden tanımlı ölçütler
- **K1 — bağımsız katalog:** o yıldan itibaren her 10 yıllık dilimde ISC-GEM olaylarının ≥ %90'ı prototipte bulunur (yalnız M ≥ 5,0).
- **K2 — Stepp (1972), Poisson ölçütü:** T_ref = 20 / 30 / 40 yıl için bulunan başlangıçların en geç olanı (tutucu).
- **Kabul edilen başlangıç = max(K1, K2).** M < 5'te K1 uygulanamaz → "bağımsız doğrulama yok".

## Sonuçlar

| Sınıf | K1 | K2 (20 / 30 / 40) | Kabul | Doğrulama | Mevcut merdiven |
|---|---|---|---|---|---|
| 3,0–3,5 | — | 2002 / 1992 / — | 2002 | yalnız K2 | 1998 |
| 3,5–4,0 | — | 1993 / 1991 / 1982 | 1993 | yalnız K2 | 1990 |
| 4,0–4,5 | — | 1995 / 1990 / 1980 | 1995 | yalnız K2 | 1980 |
| 4,5–5,0 | — | 1995 / 1965 / 1971 | 1995 | yalnız K2 | 1965 |
| 5,0–5,5 | 1970 | 1979 / 1959 / 1958 | 1979 | K1 + K2 | 1965 |
| 5,5–6,0 | 1970 | 1905 / 1905 / 1905 | 1970 | K1 + K2 | 1900 |
| ≥ 6,0 | 1900 | 1904 / 1904 / 1904 | 1904 | K1 + K2 | 1900 |

## Yorum ve sınırlılıklar
1. **M ≥ 6,0: 1904'ten beri tam** — iki ölçüt uyumlu; mevcut merdivenle (1900) tutarlı.
2. **M 5,5–6,0: K2 1905, K1 1970.** K1'in 1970 çıkmasının nedeni 1960'lı yıllar dilimi (%82): 1963–1969'da mevcut katalogda karşılığı olmayan ISC-GEM olayları prototipe **kural gereği eklenmedi**. Yani bu bir katalog kuralı sonucudur. O olaylar eklenirse beklenen başlangıç 1904–1905; eklenmezse 1970. Ayrı karar konusu.
3. **M 5,0–5,5: 1979** (en tutucu); başlangıç T_ref'e göre 1958–1979 arasında değişiyor. Mevcut 1965 basamağı bu sınıf için iyimser olabilir.
4. **M < 5,0: yalnız Stepp, bağımsız doğrulama yok.** Faz 1c'de gösterildiği gibi bu sınıflarda büyüklük türü karışık (mb / ML / MD) ve EMSC'de 2011–2013 tür geçişi var; Stepp sonucu T_ref'e duyarlı (4,5–5,0: 1965–1995). Bu sınıflar için kesin bir basamak önerilmiyor.
5. **K1 1963 öncesinde kısmen döngüseldir:** prototip 1963 öncesi ISC-GEM'e dayandığı için K1 orada ISC-GEM'in kendi tamlığını sınamaz; 1963 öncesi tamlık kanıtı esas olarak K2'dir.

## Karar için aday merdiven (uygulanmadı)
| Dönem başlangıcı | Mc | Kanıt |
|---|---|---|
| 1904 | 6,0 | K1 + K2 |
| 1904 (koşullu) / 1970 | 5,5 | K2; K1 için 1963–1969 ISC-GEM olaylarının eklenmesi gerekir |
| 1979 | 5,0 | K1 + K2 (tutucu) |
| — | < 5,0 | Belirsiz; homojen büyüklük olmadan önerilmiyor |

Açık kararlar: (i) 1963–2021'de mevcut katalogda karşılığı olmayan 21 ISC-GEM olayının eklenip eklenmeyeceği; (ii) M < 5 için homojen büyüklük sağlanana kadar mevcut basamakların korunması; (iii) üretime geçiş (onaylanmadı).
