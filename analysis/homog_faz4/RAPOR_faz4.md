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

---

# 21 ISC-GEM olayının incelemesi (2026-10-21) — ekleme yapılmadı

Kapsam: 1963–2021'de mevcut katalogda karşılığı olmayan ISC-GEM v12.1 ana katalog olayları. Yalnız yerel veriyle (yeni sorgu yok). Betik `inceleme_21.py`, olay bazında sonuç `out/inceleme_21.json` (zaman, konum, derinlik, Mw, kaynak/kalite, kutu sınırına uzaklık, ±1 gün / 300 km içinde mevcut katalogdaki en yakın aday).

| Grup | Olay | Bulgu | Kanıt düzeyi | Öneri |
|---|---|---|---|---|
| **S1 Kutu sınırı** | 3 | 1972-06-23 (sınıra 1 km), 1997-02-28 Mw 6,1 (2 km), 2019-02-17 (4 km). Mevcut katalogdaki konum kutunun dışında kalıyor olabilir | Güçlü kanıt (konum sınırda) | Eklenmesin; sınır etkisi |
| **S2 ISC-GEM'de yakın çift** | 5 | 1964-10-06 (Mw 5,49; Manyas ana şoku Mw 6,8'den 84 s önce), 1965-03-13, 1969-03-25, 1971-05-12, 1999-08-11. Her birinde mevcut katalogdaki aday, 11–84 s sonraki **başka bir ISC-GEM olayıyla zaten doğru eşleşmiş** | Doğrulandı (eşleşme); olayın ayrı bir deprem mi ISC-GEM içi tekrar mı olduğu **belirsiz** | Eklenmesin; ayrı doğrulama gerekir |
| **S3 1963–1964, katalogda yok** | 13 | Mw 5,15–5,83; ±1 gün ve 300 km içinde mevcut katalogda hiç olay yok. Mevcut merdivenin 1900–1965 basamağı (ISC, `minmagnitude=5.5`) bu dönemi de kapsıyor | Faz 1b'deki süzgeç bulgusuyla **tutarlı**, olay bazında **doğrulanmadı** | Yalnız Faz 1b yöntemiyle (iki ISC sorgusu) doğrulanırsa değerlendirilsin |

**Merdivene etkisi:** S3'teki 13 olayın 8'i M 5,5–6,0 sınıfında. Doğrulanıp eklenirlerse 1960'lar dilimindeki bulunma oranı %82'den %98'e çıkar; K1 ölçütüne göre M 5,5–6,0 başlangıcı 1970'ten 1904'e çekilir (K2 ile uyumlu). Eklenmezlerse 1970 kalır.

## Karar tablosu (öneri; uygulanmadı)
| Sınıf | Karar |
|---|---|
| M ≥ 6,0 | 1904'ten itibaren |
| M 5,5–6,0 | Koşullu: S3 doğrulanırsa 1904, doğrulanmazsa 1970 |
| M 5,0–5,5 | 1979'dan itibaren |
| M < 5,0 | Mevcut basamaklar **geçici olarak korunur** — doğrulandıkları için değil, yeni kanıt gelene kadar değiştirilmedikleri için |

Üretime geçiş onaylanmadı; `main` ve korunan dosyalar değişmedi.

---

# S3 doğrulaması — 13 olay, 1963–1964 (2026-10-21) — ekleme yapılmadı

Yöntem: Faz 1b'deki iki ISC FDSN sorgusunun aynısı (±5 dk, ±3°; B1 süzgeçsiz, B2 `minmagnitude=5.5`). Betik `dogrulama_13.py`, GitHub Actions (başarılı); sorgu adresleri ve yanıtlar `out/dogrulama_13.json`.

**Sonuç: 13 olayın 13'ü doğrulandı — "ISC'de var, `minmagnitude=5.5` süzgecinde yok".**

| Değerlendirme | Bulgu | Kanıt düzeyi |
|---|---|---|
| Olay kimliği | Her olayda ISC'nin döndürdüğü olay kimliği, ISC-GEM olay kimliğiyle **birebir aynı** (ör. 871958, 868626, 864481); zaman farkı 0–3 s | Doğrulandı |
| Eksiklik nedeni | ISC'nin tercih ettiği büyüklük süzgeç eşiğinin altında: 12 olayda ISC mb 4,69–5,30, 1 olayda ISC Ms 5,44 | Doğrulandı |
| Büyüklük kaynağı | ISC-GEM Mw 5,15–5,83, hepsi **vekil**; kalite 5 olayda B, 8 olayda C. ISC-GEM Mw ile ISC mb farkı +0,3 ile +0,9 | Doğrulandı (değerler); vekil Mw'nin doğruluğu bu veriyle sınanamaz |

**Karar (kullanıcı, önceden):** doğrulansalar da otomatik eklenmezler; önce olay kimliği ve büyüklük kaynağı değerlendirilir. Değerlendirme yukarıda: kimlik kesin, büyüklük tamamen vekil (B/C). Eklenip eklenmeyeceği ayrı karar konusudur.

**Merdiven:** M 5,5–6,0 tamlık başlangıcı **1970 olarak kalıyor** (karar). 8 olay (M 5,5–6,0) eklenirse K1 ölçütüne göre başlangıç 1904'e çekilir.

Üretim, `main`, korunan dosyalar ve mevcut tamlık merdiveni değişmedi.
