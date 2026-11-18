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

## 3. Tekrarlanabilirlik ve bulunan hata

**Hata (düzeltildi):** ilk sürümde `build_catalog.py`, CSV'yi `float_format='%.6g'` ile yazdığı için Unix zaman sütunu `t` 6 anlamlı basamağa yuvarlanıyordu (ör. 1.56238e+09; yaklaşık 10 000 s ≈ 3 saat çözünürlük). `run_pmsr.mjs` zamanı bu sütundan okuduğundan ana şok seçimi, 20 günlük pencere ve kalibrasyon sayıları etkilendi; a8776c1'deki sonuçlar (8/48) geçersizdir. Düzeltme: `run_pmsr.mjs` zamanı `time_utc` metninden okur; `t` tam (0,01 s) yazılır. Kontrol: 230 954 olayın tümünde |t − time_utc| = 0 s.

Düzeltilmiş `node run_pmsr.mjs` iki kez çalıştırıldı; çıktılar bayt bayt aynı.

| Dosya | SHA-256 |
|---|---|
| scsn_box_2017_2026.csv.gz | 64997395f50fdac2536033ace2ab576767155eba720a6dca312fa27c7e14a4d5 |
| sonuclar_2018_2026.csv | 54b30c4610aad2c4db2ae19590e9c43143558a6b1ced96ce51cd22e683016660 |
| ozet.json | cc23b4f178fd74ada0e0866602a4e60fe81c772329af5d7ba62df0197a1591b2 |

2008–2017 parite testi (`scripts/validate_pmsr_parity.mjs`): BİREBİR AYNI (o testin donmuş kataloğu bu hatadan etkilenmez). Fisher p değerleri scipy ile bağımsız olarak doğrulandı. Bağımsız tutarlılık: Ridgecrest Mw 6,4 için SCSN sonucu (N₂₀ = 8, p = 0) canlı USGS sonucuyla aynı.

## 4. Bulunan karşılaştırılabilirlik sorunu: ana şokların büyüklük türü (ön kayıtta öngörülmemişti)

| Dönem | Combined ana şoklarda tercih edilen büyüklük türü |
|---|---|
| 2008–2017 | Mw 32, ML 27, Mh 2 |
| 2018–2026 | Mw 51, ML 1 |

M ≥ 4 eşiği iki dönemde farklı büyüklük türlerine uygulanmış oluyor. 2008–2017'de ML ile seçilen ana şoklar 2009–2012'de yoğunlaşıyor. SCEDC kayıtlarına göre ML yöntemi 1 Ocak 2008'de değişti; 2015 sonunda Mlr eklendi; 2023 Kasım'dan itibaren M < 3 olaylar PhaseNet ile işleniyor.

**Keşifsel kontrol (ön kayıt dışı; birincil sonucu değiştirmez):** yalnızca Mw ile seçilen ana şoklar — 2008–2017: 7/31 (%22,6); 2018–2026: 12/49 (%24,5); Fisher p = 1,00. Büyüklük türü homojenleştirildiğinde de iki dönem benzer. Birincil sonucun yorumu değişmez.

## 5. Sonuç

Katalog doğru ve eksiksiz okundu; analiz tekrarlanabilir. Dönem karşılaştırmasının sınırlılığı büyüklük türü değişimi olarak belgelendi. Bu çalışma tamamlanmadan EQ-Live'a yeni katalog kaynağı eklenmeyecek.
