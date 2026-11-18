# Doğrulama — SCEDC 2017–2026 katalog işleme ve PMSR tekrarlanabilirliği

Sonuçlardan bağımsız, veri işleme ve tekrarlanabilirlik kontrolleri (2026-11-19).

## 1. Yıllık olay sayıları (ham dosya ↔ dosya altbilgisi ↔ işlenen katalog)

| Yıl | Ham veri satırı | SCEDC altbilgisi ("Number of rows returned") | Bölge kutusunda |
|---|--:|--:|--:|
| 2017 | 16 344 | 16 344 | 15 508 |
| 2018 | 20 730 | 20 730 | 19 924 |
| 2019 | 66 341 | 66 341 | 64 987 |
| 2020 | 37 285 | 37 285 | 34 738 |
| 2021 | 23 201 | 23 201 | 21 955 |
| 2022 | 16 884 | 16 884 | 15 678 |
| 2023 | 13 680 | 13 680 | 12 471 |
| 2024 | 17 266 | 17 266 | 14 808 |
| 2025 | 16 844 | 16 844 | 15 602 |
| 2026 (kısmi, son olay 2026-11-17) | 16 441 | 16 441 | 15 283 |

Tüm satırlar okundu (245 016 = altbilgi toplamı; tarih ayrıştırılamayan satır 0). Her dosyadaki tüm olaylar kendi yılına ait. 2017 dosyasının SHA-256'sı, 2008–2017 çalışmasında kullanılan dosyayla aynı.

## 2. Alanlar

Okuma, 2008–2017 çalışmasıyla aynı kod mantığını kullanır (`step1.py` ↔ `build_catalog.py`): sütunlar D, T, ET, GT, MAG, M, LAT, LON, DEPTH, Q, EVID, NPH, NGRM; zaman UTC; büyüklük = `MAG` (SCEDC'nin tercih ettiği büyüklük). Kutu sınırları ve olay türü (filtre yok) değişmedi. Örnek kontrol: Ridgecrest Mw 7,1 (EVID 38457511) 2019-07-06 03:19:53.04, 35,770 K −117,599 B, M 7,10 (w) — SCEDC değeriyle aynı.

## 3. Tekrarlanabilirlik

`node run_pmsr.mjs` iki kez çalıştırıldı; çıktılar bayt bayt aynı.

| Dosya | SHA-256 |
|---|---|
| scsn_box_2017_2026.csv.gz | 29bdf42ca39019b4ea05d1c7b8a85648f88965457bb821debc3c062bd392a638 |
| sonuclar_2018_2026.csv | af81ef4dad1759be323aade62789fffc1267641da20e3a0c8c902d0993c57852 |
| ozet.json | 9ee8626431e890bb333cbe6497ebcb14251678299f2b62d13c10b12ed34db91c |

2008–2017 parite testi (`scripts/validate_pmsr_parity.mjs`): BİREBİR AYNI. Fisher p değerleri scipy ile bağımsız olarak doğrulandı.

## 4. Bulunan karşılaştırılabilirlik sorunu: ana şokların büyüklük türü (ön kayıtta öngörülmemişti)

| Dönem | Combined ana şoklarda tercih edilen büyüklük türü |
|---|---|
| 2008–2017 | Mw 32, ML 27, Mh 2 |
| 2018–2026 | Mw 50, ML 1 |

M ≥ 4 eşiği iki dönemde farklı büyüklük türlerine uygulanmış oluyor. 2008–2017'de ML ile seçilen ana şoklar 2009–2012'de yoğunlaşıyor. SCEDC kayıtlarına göre ML yöntemi 1 Ocak 2008'de değişti; 2015 sonunda Mlr eklendi; 2023 Kasım'dan itibaren M < 3 olaylar PhaseNet ile işleniyor.

**Keşifsel kontrol (ön kayıt dışı; birincil sonucu değiştirmez):** yalnızca Mw ile seçilen ana şoklar — 2008–2017: 7/31 (%22,6); 2018–2026: 8/48 (%16,7); Fisher p = 0,56. Büyüklük türü homojenleştirildiğinde iki dönem arasındaki fark daha da küçülüyor. Birincil sonucun yorumu değişmez: anlamlı fark yok.

## 5. Sonuç

Katalog doğru ve eksiksiz okundu; analiz tekrarlanabilir. Dönem karşılaştırmasının sınırlılığı büyüklük türü değişimi olarak belgelendi. Bu çalışma tamamlanmadan EQ-Live'a yeni katalog kaynağı eklenmeyecek.
