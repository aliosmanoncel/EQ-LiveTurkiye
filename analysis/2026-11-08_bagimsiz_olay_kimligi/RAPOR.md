# Bağımsız Olay Kimliği Belirsizliği — GK74 ve Reasenberg

**Tarih:** 2026-11-08 · **Dal:** `research/bagimsiz-olay-kimligi` · **Durum:** araştırma; site ve `main` değişmedi; PR #8 ve #9 taslak.
**Betik:** `bok_analiz.py` (ayrıca `--mwauth`) · **Veriler:** `sonuc.json`, `sonuc_otoriter_mw.json`, `bagimsiz_olaylar.csv`, `buyuk_farklar.csv`, `doublet_adaylari.csv`, `fig_gr.png`

**Araştırma sorusu:** GK74 ve Reasenberg ile aynı ham katalogdan elde edilen alternatif bağımsız olay katalogları, tekrarlanma sürelerini ve Poisson aşılma olasılıklarını ne ölçüde değiştirir?

**Koşullar.**
- Ham katalog değişmez: EMSC 1998–2026, M ≥ 3,0, 80,929 olay, T = 28.70 yıl. Sınırlar 33–45°K, 23–48°D; İran, Irak sınırı ve Yunanistan/Ege dahildir.
- İki katalog **birleştirilmez**; her parametre her biri için ayrı hesaplanır.
- Kimlik farkları ayrı raporlanır.
- "Bağımsız" algoritmik bir sınıftır, fiziksel ana şok iddiası değildir. GK74 burada yalnız artçı ayıklar (öncüler bağımsız kalır); Reasenberg'de bağımsız = tekil + temsilci (zmap, xmeff 3,0, dondurulmuş v0.3.0).
- Yöntemler arası fark **yöntem duyarlılığıdır, güven aralığı değildir.**

## 1. Kimlik karşılaştırması (tüm olaylar)

| Grup | Olay | % |
|---|---|---|
| Ortak bağımsız | 34,966 | %43.2 |
| Yalnız GK74 bağımsız | 334 | %0.4 |
| Yalnız Reasenberg bağımsız | 30,976 | %38.3 |
| İkisi de bağımlı | 14,653 | %18.1 |

Olay bazında liste: `bagimsiz_olaylar.csv`. Bu sayılar statik site ürünüyle aynıdır (aynı kod, aynı katalog).

## 2. M ≥ 6 kimlik farkları (EMSC büyüklüğüyle)

| Zaman (UTC) | M | Yer | GK74 | Reasenberg | Bağlam |
|---|---|---|---|---|---|
| 2018-08-25T22:13 | 6.1 mw | WESTERN IRAN | artçı | representative | 2017-11-12T18:18 M7.3 IRAN-IRAQ BORDER REGION |
| 2018-11-25T16:37 | 6.3 mb | IRAN-IRAQ BORDER REGION | artçı | representative | 2017-11-12T18:18 M7.3 IRAN-IRAQ BORDER REGION |
| 2023-02-06T10:24 | 7.5 mw | CENTRAL TURKEY | bağımsız | dependent | RB temsilcisi: 2023-02-06T01:17 M7.8 CENTRAL TURKEY — 105.5 km, 9.12 sa |

M ≥ 7'de tek fark **6 Şubat 2023 Elbistan Mw 7,5**. GK74 onu bağımsız sayıyor, çünkü Pazarcık M 7,8'den daha küçük ama penceresinin uzaklık sınırının (D(7,8) ≈ 89 km) dışında kalıyor. Reasenberg ise onu Pazarcık kümesine bağlıyor: 105,5 km, 9,1 saat; temsilci Pazarcık. İki yöntem de kendi kuralına göre tutarlı; fark, kuralların farklı olmasından doğuyor.

## 3. DOUBLET adayları

İşlevsel tanım (yalnız aday): iki olay da M ≥ 6, |ΔM| ≤ 0,5, Δt ≤ 365 gün, Δd ≤ 150 km. 100–150 km bandı ayrıca işaretlidir; Elbistan 100 km eşiğiyle **kaçırılırdı**, yani eşik seçimi sonucun bir parçası.

| 1. olay | 2. olay | Δt (gün) | Δd (km) | 2. olay GK74 | 2. olay RB | Yöntemler ayrışıyor |
|---|---|---|---|---|---|---|
| 1999-08-17T00:01 M6.3 WESTERN TURKEY | 1999-11-12T16:57 M6.0 WESTERN TURKEY | 87.70 | 103.6 | bağımsız | representative | hayır |
| 2012-08-11T12:23 M6.4 NORTHWESTERN IRAN | 2012-08-11T12:34 M6.3 NORTHWESTERN IRAN | 0.01 | 9.4 | artçı | dependent | hayır |
| 2018-08-25T22:13 M6.1 WESTERN IRAN | 2018-11-25T16:37 M6.3 IRAN-IRAQ BORDER REGION | 91.77 | 60.8 | artçı | representative | **evet** |
| 2021-09-27T06:17 M6.0 CRETE, GREECE | 2021-10-12T09:24 M6.4 CRETE, GREECE | 15.13 | 95.9 | bağımsız | representative | hayır |
| 2023-02-06T01:17 M7.8 CENTRAL TURKEY | 2023-02-06T10:24 M7.5 CENTRAL TURKEY | 0.38 | 105.5 | bağımsız | dependent | **evet** |
| 2023-02-06T01:28 M6.7 CENTRAL TURKEY | 2023-02-20T17:04 M6.3 TURKEY-SYRIA BORDER REGION | 14.65 | 128.8 | bağımsız | representative | hayır |
| 2023-02-06T10:26 M6.0 CENTRAL TURKEY | 2023-02-06T12:02 M6.0 CENTRAL TURKEY | 0.07 | 130.5 | artçı | dependent | hayır |
| 2025-05-13T22:51 M6.0 DODECANESE ISLANDS, GREECE | 2025-05-22T03:19 M6.2 CRETE, GREECE | 8.19 | 115.9 | bağımsız | representative | hayır |
| 2025-08-10T16:53 M6.1 WESTERN TURKEY | 2025-10-27T19:48 M6.0 WESTERN TURKEY | 78.12 | 17.5 | artçı | dependent | hayır |

Not: İzmit 1999 ve Düzce 1999 EMSC'de **mb 6,3 ve mb 6,0** olarak geçiyor (otoriter Mw 7,6 ve 7,2). Bu nedenle M ≥ 7 listesinde yoklar (§5).

## 4. b ve a değerleri (her katalog ayrı)

Aki–Utsu (ΔM = 0,1) ile b ± σ (Shi & Bolt), a = log N(≥Mc) + b·Mc; Weichert (1980) tek tamlık dönemi (EMSC'de tek dönem; çok dönemli Weichert için uzun katalog gerekir).

| Katalog | Mc 3,2: b(Aki) | a | b(Weichert) | λ(≥Mc)/yıl |
|---|---|---|---|---|
| Ham | 1.021 ± 0.004 | 7.97 | 1.026 ± 0.005 | 1743 |
| GK74 | 0.946 ± 0.006 | 7.38 | 0.950 ± 0.006 | 783 |
| Reasenberg | 1.052 ± 0.005 | 7.97 | 1.058 ± 0.005 | 1393 |

| Katalog | Mc 3,5: b(Aki) | a | b(Weichert) | λ(≥Mc)/yıl |
|---|---|---|---|---|
| Ham | 1.023 ± 0.006 | 7.97 | 1.027 ± 0.007 | 862 |
| GK74 | 0.959 ± 0.008 | 7.43 | 0.963 ± 0.009 | 411 |
| Reasenberg | 1.054 ± 0.007 | 7.97 | 1.059 ± 0.008 | 674 |

**Bulgu:** GK74 ile Reasenberg arasındaki b farkı (~0,10), örnekleme belirsizliğinin (σ ≈ 0,005–0,009) **10–20 katı**. b için yöntem seçimi, istatistiksel belirsizlikten çok daha büyük bir etki. Yönü: GK74 daha düşük b veriyor. Bunun olası nedeni, GK74'ün geniş pencerelerinin küçük olayları orantısız biçimde ayıklaması; bu bir yorum, ayrıca sınanmalı. Mc 3,2 ve 3,5 sonuçları tutarlı. Weichert ile Aki–Utsu tek dönemde beklendiği gibi çok yakın (iç denetim).

## 5. Poisson oranları ve belirsizlikleri (her katalog ayrı)

λ = sayı / T; %95 aralık kesin Poisson (Garwood). P(t) = 1 − e^(−λt).

| Büyüklük | Eşik | Katalog | Sayı | λ /yıl [%95] | Ort. tekrarlanma (yıl) | P(1 yıl) [%95] | P(50 yıl) |
|---|---|---|---|---|---|---|---|
| EMSC büyüklüğü | M ≥ 6 | ham | 41 | 1.428 [1.025–1.938] | 0.7 | %76.0 [64.1–85.6] | %100.00 |
| EMSC büyüklüğü | M ≥ 6 | gk74 | 34 | 1.185 [0.820–1.655] | 0.8 | %69.4 [56.0–80.9] | %100.00 |
| EMSC büyüklüğü | M ≥ 6 | reasenberg | 35 | 1.219 [0.849–1.696] | 0.8 | %70.5 [57.2–81.7] | %100.00 |
| EMSC büyüklüğü | M ≥ 7 | ham | 5 | 0.174 [0.057–0.407] | 5.7 | %16.0 [5.5–33.4] | %99.98 |
| EMSC büyüklüğü | M ≥ 7 | gk74 | 5 | 0.174 [0.057–0.407] | 5.7 | %16.0 [5.5–33.4] | %99.98 |
| EMSC büyüklüğü | M ≥ 7 | reasenberg | 4 | 0.139 [0.038–0.357] | 7.2 | %13.0 [3.7–30.0] | %99.91 |
| Otoriter Mw | M ≥ 6 | ham | 41 | 1.428 [1.025–1.938] | 0.7 | %76.0 [64.1–85.6] | %100.00 |
| Otoriter Mw | M ≥ 6 | gk74 | 34 | 1.185 [0.820–1.655] | 0.8 | %69.4 [56.0–80.9] | %100.00 |
| Otoriter Mw | M ≥ 6 | reasenberg | 35 | 1.219 [0.849–1.696] | 0.8 | %70.5 [57.2–81.7] | %100.00 |
| Otoriter Mw | M ≥ 7 | ham | 7 | 0.244 [0.098–0.503] | 4.1 | %21.6 [9.3–39.5] | %100.00 |
| Otoriter Mw | M ≥ 7 | gk74 | 7 | 0.244 [0.098–0.503] | 4.1 | %21.6 [9.3–39.5] | %100.00 |
| Otoriter Mw | M ≥ 7 | reasenberg | 6 | 0.209 [0.077–0.455] | 4.8 | %18.9 [7.4–36.6] | %100.00 |

Otoriter Mw duyarlılığı (`data/mw_authority.json`, yalnız doğrulanmış 9 olay; eşleşme ±60 s, 50 km): İzmit mb 6,3 → Mw 7,6, Düzce mb 6,0 → Mw 7,2, Van Ms 7,3 → Mw 7,1, Kythira mb 6,5 → Mw 6,7. İki algoritma bu katalogda **yeniden** çalıştırıldı. M ≥ 7'de yine tek fark Elbistan.

## 6. Üç belirsizlik kaynağı yan yana (M ≥ 7, yıllık λ)

| Kaynak | Etki |
|---|---|
| Büyüklük ölçeği (EMSC ↔ otoriter Mw), GK74 kataloğu | 5 → 7 olay; λ 0,174 → 0,244 |
| Bağımsız olay kimliği (GK74 ↔ Reasenberg), otoriter Mw ile | 7 ↔ 6 olay; λ 0,244 ↔ 0,209 (tek olay: Elbistan) |
| Örnekleme (Poisson %95), 7 olay | λ 0,098–0,503 (≈ 5 kat genişlik) |

**Sonuç (bu katalog ve tanımlar için):**
- **M ≥ 7 oranlarında** örnekleme belirsizliği baskın. Yöntem farkı (1 olay) aralığın içinde kalıyor, büyüklük ölçeği farkı (2 olay) ondan büyük. 50 yıllık olasılık her durumda ≈ %100; ayırt edici değil. 1 yıllık olasılık %18,9 ile %21,6 arasında, aralıklar geniş.
- **b değerinde** tersi geçerli: yöntem farkı örnekleme belirsizliğinden çok büyük. G–R dışdeğerlemesiyle yapılan tekrarlanma tahminleri, doğrudan sayımdan daha yönteme duyarlıdır.
- Kimlik farkı az ama **anlamlı olaylarda** yoğunlaşıyor: Elbistan 2023 ve Sarpol-e Zahab 2018 dizisi. Bu olaylar, tekrarlanma tartışmasında "bir mi, iki mi" sorusunun cevabını değiştiriyor.

## 7. Sınırlamalar

- **Tek katalog, kısa süre:** 28,7 yıl; M ≥ 7 için yalnız 5–7 olay. Çok dönemli Weichert ve uzun dönem tekrarlanma için tarihsel katalog (ISC 1900–1997 + tarihsel) gerekir. Bu sonraki adımdır ve kaynak birleştirme kuralı gerektirir.
- **Karışık büyüklük ölçeği (ML/mb/Ms/Mw):** Mc, b ve eşik sayıları buna koşulludur. Otoriter Mw yalnız 9 büyük olay için var.
- **Bölge tanımı:** Türkiye'ye özgü değil; İran ve Yunanistan dahil. Türkiye alt kümesi ayrıca incelenmeli.
- **Tanımlar:** GK74 yalnız artçı ayıklar. DOUBLET tanımı işlevseldir; eşikler (özellikle 100/150 km) sonucu değiştirir.
- **Sonuçlar tehlike değerlendirmesi değildir;** yöntem duyarlılığını gösterir.

## 8. Sonraki adımlar (önerilen)

1. Türkiye alt kümesi (sınır poligonu) ile aynı analiz.
2. Uzun katalogla çok dönemli Weichert (tamlık dönemleri) ve M ≥ 6,5 / 7 için tekrarlanma.
3. b farkının kaynağı: büyüklük sınıflarına göre ayıklanan olay oranları (GK74 ↔ Reasenberg).
4. DOUBLET adaylarının literatürle karşılaştırılması: Elbistan–Pazarcık, Girit 2021, Sarpol-e Zahab 2017–2018.

## 9. İndirilebilir veri ürünleri (`urunler/`, `bok_analiz.py --urunler`)

Yöntem başına **ayrı** ürünler; birleştirilmezler. Ham katalog kimliği (`event_id`) her dosyada korunur.

| Dosya | Satır | İçerik |
|---|---|---|
| `gk74_bagimsiz.csv.gz` | 35 300 | GK74 bağımsız |
| `gk74_bagimli.csv.gz` | 45 629 | GK74 bağımlı; `representative_event_id` = olayı bağımlı kılan daha büyük bağımsız olay (GK74 kuralıyla; tüm bağımlılar için bulundu) |
| `reasenberg_bagimsiz.csv.gz` | 65 942 | Reasenberg tekil + temsilci |
| `reasenberg_bagimli.csv.gz` | 14 987 | Reasenberg bağımlı; temsilci kimliği, `cluster_id` |
| `yontem_farklari.csv.gz` | 31 310 | İki yöntemin farklı sınıfladığı olaylar; iki sınıf yan yana |
| `metadata.json` | — | Katalog sha256, yöntem sürümleri, parametreler, alanlar, uyarılar, dosya karmaları |

Alanlar: `event_id, origin_time, latitude, longitude, depth, magnitude, magnitude_type, place, method, classification, cluster_id, representative_event_id, dependent_role` (+ Reasenberg için `reasenberg_class`).

**Bağımlı ≠ artçı.** `dependent_role` yalnız zaman sırasını gösterir, fiziksel nedensellik iddiası değildir: `aftershock_candidate` temsilciden/bastırandan sonra, `foreshock_candidate` ondan önce. Reasenberg'de 13 457 artçı adayı ve 1 530 öncü adayı var; bu sayılar statik ürünle aynı. Bu uygulamada GK74 yalnız ileri pencere kullandığı için bütün GK74 bağımlıları artçı adayıdır.

GeoJSON ve JSON için `--urunler --format=csv,geojson,json` kullanılır. Bu biçimler depoya konmadı (boyut).

## 10. Gelen yorum (veri ürünleri, Coulomb) — IN / OUT

| Öneri | Karar |
|---|---|
| Bağımsız / bağımlı / artçı adayı ayrımı | **IN** (`dependent_role`). Düzeltme: buradaki GK74 öncüleri bağımlı saymaz (yalnız ileri pencere). |
| 5 ayrı indirilebilir ürün, `event_id` korunur, metadata | **IN** (§9). CSV depoda; GeoJSON/JSON betikle üretilir. |
| GK74 ve Reasenberg tek bir artçı kataloğunda asla birleştirilmez | **IN**; `metadata.json` uyarılarında. |
| Omori–Utsu (p, c) yöntem duyarlılığı; mekânsal göç; bağımlı ↔ bağımsız b | **IN, sonraki araştırma adımları** (ürünler bunlara hazır) |
| Coulomb gerilme karşılaştırması | **OUT (şimdilik)**: fay geometrisi, kayma modeli ve alıcı fay varsayımları gerekir; ayrı bilimsel aşama. Ürünler Coulomb'un yerine geçmez, onu gözlemsel olarak sınamak için kullanılabilir. |
| Ürünlerin sitede indirilebilir olması | **OUT (şimdilik)**: karar gereği araştırma tamamlanmadan siteye özellik eklenmiyor. |

---

# 2. tur — Türkiye alt kümesi (`turkiye_sinir.py`, `turkiye_alt_kume.py`, `turkiye_sonuc.json`)

**Sınır tanımı (tekrarlanabilir):**
- Kaynak: Natural Earth 1:10m Admin-0 v5.1.2 (sha256 `239eec57…`, betik denetler).
- Tanım: Türkiye kara alanı + **B km deniz payı**. Payın içindeki boşluklar doldurulur (Marmara); komşu ülkelerin kara alanları çıkarılır.
- B = **30 km (ana tanım)**; duyarlılık için 0 ve 50 km.
- Yalnız kara (0 km) İzmit Körfezi ve Marmara'yı dışarıda bırakıyor; bu yüzden ana tanım olarak uygun değil.
- Halabja, Atina, Midilli ve Kıbrıs dışarıda; Samos 2020 (denizde) içeride.
- Poligonlar: `turkiye_sinir_{0,30,50}km.geojson`. Deniz payı siyasi yetki alanı değildir.

**İki uygulama:**
- **(i) yeniden:** yöntemler yalnız alt küme olaylarıyla çalıştırılır.
- **(ii) tam:** tüm katalogdaki sınıf alt kümeye süzülür.

Ayrıca **Türkiye dışı** (30 km tanımının tümleyeni) aynı ölçülerle hesaplandı. Sonuçlar birleştirilmedi.

## Merkez soru: ~0,10'luk b farkı Türkiye'de sürüyor mu?

Aki–Utsu b ± σ (Shi & Bolt), her katalog ayrı; Δb = b(RB) − b(GK74), "oran" = Δb / √(σ²GK + σ²RB).

| Kapsam | N | Mc 3,2: b GK74 | b RB | Δb (oran) | Mc 3,5: b GK74 | b RB | Δb (oran) |
|---|---|---|---|---|---|---|---|
| Tüm bölge | 80 929 | 0,946 ± 0,006 | 1,052 ± 0,005 | +0,106 (13σ) | 0,959 ± 0,008 | 1,054 ± 0,007 | +0,095 (8σ) |
| **Türkiye 30 km, yeniden** | 44 697 | 1,097 ± 0,012 | 1,227 ± 0,010 | **+0,130 (8σ)** | 1,000 ± 0,016 | 1,114 ± 0,013 | **+0,114 (6σ)** |
| Türkiye 30 km, tam | 44 697 | 1,097 | 1,227 | +0,130 | 0,998 | 1,114 | +0,116 |
| Türkiye 30 km, yeniden, otoriter Mw | 44 697 | 1,098 | 1,231 | +0,133 | 1,002 | 1,119 | +0,117 |
| Türkiye 0 km, yeniden | 36 798 | 1,107 | 1,224 | +0,116 (7σ) | 0,989 | 1,103 | +0,114 (5σ) |
| Türkiye 50 km, yeniden | 47 075 | 1,089 | 1,220 | +0,130 (9σ) | 1,001 | 1,118 | +0,117 (6σ) |
| **Türkiye dışı (30 km tümleyeni)** | 36 232 | 0,861 ± 0,007 | 0,940 ± 0,006 | **+0,080 (9σ)** | 0,940 ± 0,010 | 1,019 ± 0,009 | +0,079 (6σ) |

**Cevap:**
- Fark Türkiye'de **sürüyor, hatta daha büyük**: +0,11–0,13; dışarıda +0,08.
- Bu nedenle tüm bölgedeki farkın Türkiye dışı olaylardan geldiği **söylenemez**. Tam tersine, Türkiye dışı olaylar farkı bir miktar küçültüyor.
- Sonuç sağlam: sınır tanımına (0/30/50 km), uygulamaya (yeniden / tam), Mc'ye (3,2 / 3,5) ve büyüklük kaynağına (EMSC / otoriter Mw) göre değişmiyor.
- Yön her yerde aynı: GK74 daha düşük b veriyor.

**Ek bulgular:**
- **Mutlak b, bölgeye göre belirgin farklı.** Türkiye'de b ≈ 1,10 (GK74) ve 1,23 (RB); dışarıda 0,86 ve 0,94 (Mc 3,2). Tüm bölge değerleri iki farklı nüfusun karışımı; Türkiye için temsil edici değil.
- **Türkiye'de b, Mc'ye duyarlı:** 3,2'den 3,5'e geçince b yaklaşık 0,1 düşüyor. Muhtemel nedenler büyüklük ölçeği karışımı ve bölgesel tamlık farkları. Bu konu dönemsel Mc analizine (sıradaki adım) taşınmalı. Δb ise Mc'den bağımsız olarak sabit kalıyor.
- **"Yeniden" ile "tam" arasındaki sınıf farkı küçük:** 30 km'de GK74'te 204, Reasenberg'de 35 olay (44 697 olay içinde). b üzerinde etkisi yok.

## Türkiye'de büyük depremler (30 km)

| | Büyüklük | Ham | GK74 | RB | Kimlik farkı | λ GK74 /yıl [%95] | λ RB /yıl |
|---|---|---|---|---|---|---|---|
| M ≥ 6 | EMSC | 19 | 15 | 14 | Elbistan | 0,523 [0,293–0,862] | 0,488 |
| M ≥ 7 | EMSC | 4 | 4 | 3 | Elbistan | 0,139 [0,038–0,357] | 0,105 |
| M ≥ 7 | otoriter Mw | 6 | 6 | 5 | Elbistan | 0,209 [0,077–0,455] | 0,174 |

- Türkiye'de M ≥ 6'da bile **tek kimlik farkı Elbistan**. Tüm bölgedeki diğer iki fark (Batı İran 2018, Sarpol-e Zahab 2018) Türkiye dışında.
- M ≥ 7'de belirsizlik sıralaması aynı kalıyor: örnekleme (6 olay → %95 aralık ≈ 6 kat) > büyüklük ölçeği (4 → 6 olay) > yöntem (6 ↔ 5).

## 2. tur sonucu

- **b ve G–R tabanlı analizlerde** declustering yöntemi Türkiye'de de baskın bir belirsizlik kaynağı: Δb ≈ 0,11–0,13, örnekleme belirsizliğinin 6–9 katı.
- **Doğrudan M ≥ 7 sayımlarında** yöntem etkisi tek bir olaya indirgeniyor: Elbistan–Pazarcık. Ama o olay, "bağımsız iki deprem mi, tek dizi mi" sorusunun ta kendisi.
- Sıradaki adımlar (sırayla): dönemsel Mc ve Weichert; b farkının büyüklük sınıflarına göre ayrıştırılması; DOUBLET adaylarının literatürle karşılaştırılması.

---

# 3. tur (ikinci aşama) — Dönemsel Mc(t) ve Weichert (`donemsel_mc_weichert.py`, `donemsel_sonuc.json`, `fig_donemsel.png`)

**Soru:** Türkiye'de GK74 ile Reasenberg arasındaki b farkı, dönemsel tamlık hesaba katıldığında da istatistiksel olarak anlamlı mı?

## Yöntem

- **Kapsam:** Türkiye 30 km, EMSC 1998–2026,7, M ≥ 3,0, 44 697 olay, EMSC büyüklüğü (aynı ölçek). Kataloglar ayrı tutuldu: iki yöntem alt kümede ayrı çalıştırıldı ("yeniden").
- **Mc(t):** Her dönem için **ham** katalogda tahmin edildi (tamlık kataloğun özelliğidir). Aynı Mc iki kataloğa uygulandı.
- **Mc tahmincileri:**
  - MAXC+0,2 (sitenin kuralı).
  - Kümülatif GFT (R ≥ %95, olmazsa %90).
  - MAXC bootstrap (500 yeniden örnekleme).
  - max(GFT, MAXC).
  - Sabit 3,5.
- **Dönem başına:** N(≥Mc); b (Aki–Utsu, ΔM = 0,1) ± σ (Shi & Bolt) ve %95 aralık; yıllık a = log₁₀(N/Tₚ) + b·Mc; Δb, σ_Δb ve z.
- **Birleşik Δb:** Dönemlerin ters-varyans ağırlıklı ortalaması; heterojenlik için Cochran Q ve χ².
- **Weichert (1980), çok dönemli:** Her 0,1 büyüklük sınıfı yalnız Mc(dönem) ≤ sınıf olan dönemlerde sayıldı. Her katalog için ayrı hesaplandı.
- **Duyarlılık:** Dönem uzunluğu 4 / 5 / 7 yıl, başlangıç +2 yıl kaydırma, tahminci değişimi, Mc + 0,1.

## Önemli yöntem bulgusu: bu katalogda MAXC tamlığı ölçmüyor

EMSC dosyası **M ≥ 3,0'da kesilmiş**. Bu yüzden en kalabalık sınıf her dönemde 3,0 oluyor; MAXC+0,2 de her dönemde 3,2 veriyor ve bootstrap ile değişmiyor. MAXC burada tamlığı değil, kesim eşiğini ölçüyor. **GFT ise dönemsel değişim gösteriyor:** 2003–2008'de 3,8, 2008–2013'te 3,4, diğer dönemlerde 3,0. Bu nedenle sonuçlar GFT'li ve "max(GFT, MAXC)" varyantlarıyla da verildi. Aynı durum sitenin bu dosyayla hesapladığı Mc için de geçerlidir; ayrıca not edilmeli.

## Dönem tablosu (ihtiyatlı varyant: Mc = max(GFT, MAXC+0,2))

| Dönem | Mc | Baskın ölçek | N GK74 | b GK74 ± σ | N RB | b RB ± σ | Δb | z |
|---|---|---|---|---|---|---|---|---|
| 1998–2003 | 3,2 | md %92 | 1 495 | 0,984 ± 0,024 | 2 766 | 1,113 ± 0,021 | +0,129 | 4,1 |
| 2003–2008 | 3,8 | md %93 | 338 | 0,931 ± 0,048 | 490 | 1,036 ± 0,046 | +0,104 | 1,6 |
| 2008–2013 | 3,4 | md %57 / ml %40 | 1 172 | 1,204 ± 0,038 | 1 929 | 1,298 ± 0,032 | +0,093 | 1,9 |
| 2013–2018 | 3,2 | ml %93 | 1 234 | 0,933 ± 0,025 | 1 923 | 1,050 ± 0,023 | +0,117 | 3,5 |
| 2018–2023 | 3,2 | ml %92 | 918 | 0,822 ± 0,026 | 1 625 | 0,932 ± 0,023 | +0,110 | 3,2 |
| 2023–2026,7 | 3,2 | ml %90 | 898 | 0,761 ± 0,025 | 2 873 | 0,989 ± 0,018 | **+0,228** | 7,5 |

Yıllık a değerleri ve her varyantın tam tablosu `donemsel_sonuc.json`'da.

## Birleşik sonuç ve duyarlılık

| Varyant | Mc(t) | Birleşik Δb ± σ | z | Heterojenlik p | Weichert Δb (z) |
|---|---|---|---|---|---|
| 5 yıl, MAXC+0,2 (ana) | 3,2 hepsi | +0,148 ± 0,014 | 10,5 | 0,05 | +0,133 (9,1) |
| 5 yıl, GFT | 3,0 / 3,8 / 3,4 / 3,0 / 3,0 / 3,0 | +0,141 ± 0,013 | 11,0 | 0,08 | +0,139 (11,8) |
| **5 yıl, max(GFT, MAXC)** | 3,2 / 3,8 / 3,4 / 3,2 / 3,2 / 3,2 | **+0,143 ± 0,015** | **9,5** | 0,05 | **+0,142 (9,6)** |
| 5 yıl, Mc = 3,5 sabit | 3,5 hepsi | +0,132 ± 0,020 | 6,7 | 0,09 | +0,116 (5,7) |
| 5 yıl, MAXC+0,2 + 0,1 | 3,3 hepsi | +0,140 ± 0,016 | 9,0 | 0,11 | +0,123 (7,6) |
| 4 yıl, MAXC+0,2 | 3,2 hepsi | +0,153 ± 0,014 | 10,8 | 0,17 | +0,133 (9,1) |
| 7 yıl, MAXC+0,2 | 3,2 hepsi | +0,157 ± 0,014 | 11,1 | 0,43 | +0,133 (9,1) |
| 5 yıl, +2 kaydırılmış | 3,2 hepsi | +0,159 ± 0,014 | 11,2 | 0,25 | +0,133 (9,1) |

Çok dönemli Weichert, max(GFT, MAXC) tamlık tablosuyla: **GK74 b = 0,922, yıllık a = 4,64 · Reasenberg b = 1,063, a = 5,44** (a, M_ref = 3,8 için). Δb = +0,142 (z 9,6). Tek Mc'li (3,2) varyantta GK74 1,103 ↔ RB 1,235 (Δb +0,133). Mutlak b tamlık tablosuna duyarlı, Δb değil.

## Cevap

- **Evet.** Dönemsel tamlık hesaba katıldığında Δb, **her dönemde ve her varyantta pozitif**.
- **Birleşik Δb +0,13 ile +0,16 arasında; z 6,7–11,8** (p ≪ 0,001).
- Çok dönemli Weichert aynı sonucu veriyor: **Δb +0,12 ile +0,14, z 5,7–11,8.** Türkiye için 2. turda bulunan ~0,13 korunuyor.
- **Tek tek dönemlerde** ihtiyatlı Mc (3,4–3,8) olay sayısını düşürüyor; bazı dönemlerde z 1,6–2,5'e iniyor. Anlamlılık esas olarak **dönemlerin birleşiminden** geliyor; tek bir dönemin sonucu tek başına yorumlanmamalı.
- **Heterojenlik sınırda** (p 0,05–0,43). Ayrışan dönem **2023–2026**: Δb +0,23. Kahramanmaraş dizisi, iki yöntemin en çok ayrıştığı dönem; GK74 geniş pencereleriyle çok daha fazla olay ayıklıyor (N 898 ↔ 2 873). **2023–2026 dışarıda bırakıldığında birleşik Δb +0,115 ± 0,017, z 6,7**; yani fark o diziden kaynaklanmıyor. Diğer dönemlerde Δb +0,09 ile +0,18 arasında.

## Ek bulgu: büyüklük ölçeği değişimi b'nin mutlak değerini sürüklüyor

- 1998–2013 arası **md** ağırlıklı, 2013 sonrası **ml** ağırlıklı. Muhtemelen veri sağlayıcının büyüklük türü değişti.
- **Mutlak b** dönemler arasında 0,76 ile 1,58 arasında geziniyor; bu sürüklenme büyük ölçüde ölçek ve Mc değişimini yansıtıyor.
- **Δb ise ölçek değişiminden büyük ölçüde etkilenmiyor:** md döneminde +0,09…+0,13, ml döneminde +0,11…+0,23.
- Sonuç: **mutlak b değerleri dönemler arası karşılaştırılamaz; yöntem farkı (Δb) karşılaştırılabilir.**

## Sınırlılıklar

- Katalog M ≥ 3,0'da kesik olduğu için gerçek tamlık 3,0'ın altındaysa ölçülemez; MAXC bu dosyada bilgisizdir.
- GFT'nin %95 eşiği bazı dönemlerde ancak 3,8'de sağlanıyor. Bu, karışık ölçek (md/ml/mb) altında tek bir G–R doğrusunun uymamasından da kaynaklanabilir; tamlıktan ayırt edilemiyor.
- Büyüklük ölçeği karışık; dönemler arası homojenleştirme (ml/md → Mw) yapılmadı. Bu, sitenin büyüklük dönüştürme seçenekleriyle ayrıca sınanmalı.
- Aki–Utsu σ, olayların bağımsız olduğunu varsayar. Ayrıştırılmış kataloglarda bile tam bağımsızlık garanti değildir; z değerleri iyimser olabilir.
- 2023–2026 dönemi tek bir büyük dizinin baskısı altında.
- Bulgular tehlike değerlendirmesi değildir.

## Sonraki adımlar (önerilen sırayla)

1. **b farkının kaynağı:** büyüklük sınıflarına göre iki yöntemin ayıkladığı olay oranları. GK74'ün küçük olayları orantısız biçimde ayıklayıp ayıklamadığına bakılacak.
2. **Ölçek homojenleştirmesi:** sitenin dönüştürme bağıntılarıyla aynı analiz.
3. **DOUBLET adaylarının literatürle karşılaştırılması.**

---

# 4. tur (üçüncü aşama) — Δb'nin kaynağı: büyüklük sınıflarına göre ayıklama (`buyukluk_sinifi_ayiklama.py`, `buyukluk_sonuc.json`, `fig_ayiklama.png`)

**Soru:** Hangi büyüklük sınıfında hangi yöntem ne kadar olay ayıklıyor ve bu, Türkiye'deki Δb ≈ +0,13'ü açıklıyor mu?
Veri: Türkiye 30 km alt kümesi, "yeniden" sınıflar (2. tur ile aynı), EMSC büyüklüğü. Ham katalog değiştirilmedi; GK74 ve Reasenberg katalogları ayrı tutuldu.

## Yöntem

- Kalan oran f(M) = N_ayrıştırılmış(M) / N_ham(M).
- f(M) ∝ 10^(k·M) ise ayrıştırılmış katalogda **b_d = b_ham − k**. Büyüklükten bağımsız ayıklama (k = 0) b'yi değiştirmez. f'nin M ile artması (k > 0) b'yi düşürür, azalması (k < 0) b'yi yükseltir.
- Buradan **Δb = b_RB − b_GK ≈ k_GK − k_RB**.
- k: log10 f'nin M'ye ağırlıklı doğrusal eğimi (binom varyansı, delta yöntemi; M ≥ Mc, N_ham ≥ 5 olan 0,1 kutuları).
- Sınıf katkısı: GK74 sayımlarında yalnız o sınıf RB sayımıyla değiştirilince b'nin değişimi (gruplanmış Aki–Utsu). **Katkılar toplanabilir değildir**; yalnız yön ve görece büyüklük için okunmalı.

## Sınıflara göre ayıklama (tümü 1998–2026)

| Sınıf | N ham | GK74 ayıkladı | RB ayıkladı | ikisi de | yalnız GK74 | yalnız RB | kalan GK74 | kalan RB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 3,0–3,2 | 19 882 | 11 941 | 3 594 | 3 547 | 8 394 | 47 | 0,399 | 0,819 |
| 3,2–3,5 | 14 268 | 8 852 | 3 373 | 3 324 | 5 528 | 49 | 0,380 | 0,764 |
| 3,5–4,0 | 7 397 | 4 474 | 2 086 | 2 056 | 2 418 | 30 | 0,395 | 0,718 |
| 4,0–4,5 | 2 204 | 1 316 | 757 | 734 | 582 | 23 | 0,403 | 0,657 |
| 4,5–5,0 | 722 | 401 | 269 | 252 | 149 | 17 | 0,445 | 0,627 |
| 5,0–6,0 | 205 | 86 | 68 | 56 | 30 | 12 | 0,580 | 0,668 |
| ≥ 6,0 | 19 | 4 | 5 | 4 | 0 | 1 | 0,789 | 0,737 |

- RB'nin ayıkladığı olayların neredeyse tamamını GK74 de ayıklıyor ("yalnız RB" sınıf başına 1–49).
- GK74, M < 4,5'te her sınıfta olayların ~%60'ını ayıklıyor; M ≥ 5'te daha az.
- RB'nin ayıklama oranı ise M ile **artıyor** (%18 → %34–37).

## Eğim ve Δb

| Alt küme | Mc | b ham | b GK74 | b RB | Δb gözlenen | k_GK74 | k_RB | Δb (eğimden) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| tümü 1998–2026 | 3,2 | 1,161 | 1,097 | 1,227 | **+0,130** | +0,067 ± 0,008 | −0,061 ± 0,005 | **+0,127** |
| tümü 1998–2026 | 3,5 | 1,069 | 1,000 | 1,114 | +0,114 | +0,082 ± 0,011 | −0,046 ± 0,008 | +0,128 |
| md dönemi 1998–2013 | 3,2 | 1,358 | 1,273 | 1,409 | +0,136 | +0,087 ± 0,010 | −0,039 ± 0,006 | +0,127 |
| ml dönemi 2013–2026 | 3,2 | 0,944 | 0,843 | 0,991 | +0,148 | +0,121 ± 0,013 | −0,054 ± 0,008 | +0,176 |
| ml dönemi, 2023+ hariç | 3,2 | 0,972 | 0,882 | 0,993 | +0,110 | +0,109 ± 0,015 | −0,025 ± 0,010 | +0,134 |
| tümü, 2023+ hariç | 3,2 | 1,239 | 1,149 | 1,285 | +0,136 | +0,086 ± 0,008 | −0,042 ± 0,005 | +0,128 |

Sınıf katkıları (tümü, Mc 3,2): 3,2–3,5 **+0,361**; 3,5–4,0 −0,047; 4,0–4,5 −0,084; 4,5–5,0 −0,039; 5,0–6,0 −0,008; ≥ 6 +0,001. md ve ml dönemlerinde de aynı desen (3,2–3,5 sınıfı +0,33…+0,38, üst sınıflar küçük ve negatif).

## Cevap

- **Δb, iki yöntemin büyüklüğe bağlı ayıklama eğimlerinin farkıyla nicel olarak açıklanıyor:** gözlenen +0,130, eğimden öngörülen +0,127. Bu, md ve ml dönemlerinde ve 2023+ hariç tutulduğunda da geçerli (öngörülen +0,13…+0,18, gözlenen +0,11…+0,15).
- **İki yöntem zıt yönlerde seçici:**
  - GK74'ün kalan oranı M ile **artıyor** (k > 0): büyük olaylar daha sık "bağımsız" kalıyor → b düşüyor.
  - Reasenberg'in kalan oranı M ile **azalıyor** (k < 0): büyük olaylar daha sık bir kümeye bağlanıyor → b yükseliyor.
  - İki etki yaklaşık eşit büyüklükte (+0,067 ve −0,061). Yani fark yalnızca "GK74 küçük olayları daha çok ayıklıyor" değil; Reasenberg'in büyük olayları daha çok ayıklaması da yarı yarıya katkı veriyor.
- **Sınıf düzeyinde:** etkinin en büyük kaynağı Mc'nin hemen üstündeki 3,2–3,5 sınıfı. Bu sınıfta GK74, RB'nin bıraktığı olayların yarısından fazlasını ayıklıyor (5 528 olay yalnız GK74'te ayıklandı).
- **Yorum:** +0,13, ayrıştırma algoritmalarının büyüklüğe bağlı katalog seçiminin **istatistiksel sonucudur**; fiziksel bir sismisite değişiminin kanıtı olarak yorumlanmamalıdır. Hangi yöntemin "doğru" olduğu bu analizle belirlenemez.
- **md/ml:** ölçek değişimi mutlak b'yi kaydırıyor (b ham 1,36 → 0,94), ancak eğim farkı ve Δb her iki dönemde de korunuyor. ml döneminde k_GK daha büyük (+0,12); bunun bir kısmı 2023 dizisinden geliyor (2023+ hariç +0,11).

## Sınırlılıklar

- Büyüklük ölçeği karışık (md/ml/mb); homojenleştirme yapılmadı (sonraki aşama).
- Üstel f(M) modeli bir yaklaşım; M ≥ 5'te kutular seyrek ve f gürültülü (şekilde görülüyor). Eğimler M 3,2–5 aralığındaki kalabalık kutular tarafından belirleniyor.
- Binom ağırlıkları olayları bağımsız varsayar; σ_k iyimser olabilir.
- Sınıf katkıları birbirini etkiler ve toplanmaz (toplam +0,184 ≠ +0,130).
- Bulgular tehlike değerlendirmesi değildir.

## Sonraki adımlar (onay sonrası)

1. **Ölçek homojenleştirmesi:** sitenin dönüştürme bağıntılarıyla (md/ml → Mw) aynı analiz.
2. **DOUBLET adaylarının literatürle karşılaştırılması.**

---

# 5. tur (dördüncü aşama) — md/ml → Mw ölçek homojenleştirmesi (`olcek_homojenlestirme.py`, `site_donusum_parite.mjs`, `olcek_sonuc.json`, `fig_olcek.png`)

**Soru:** 3.–4. turdaki Δb ≈ +0,13 ve büyüklüğe bağlı ayıklama eğimleri, büyüklükler sitenin kendi dönüşüm bağıntılarıyla Mw'ye çevrilince korunuyor mu? M ≥ 5'te kalan oranlar ve gürültü nasıl değişiyor?

## Gelen yorum (Gemini, 4. tur değerlendirmesi) — IN / OUT

- **IN:** 4. tur sonucunun (`5f9dc4d`) kabulü; 4. aşamaya geçiş; M ≥ 5,0 aralığının ayrıca izlenmesi.
- **IN:** 3,0–3,5 aralığında GK74'ün tek başına ayıkladığı olay hacminin (ör. 8 394 ↔ 47) sınıf baskınlığını gösterdiği.
- **OUT (düzeltme):** "GK74 küçük olayları baskın şekilde ayıklıyor (k_GK > 0)" ifadesi tam doğru değil. GK74, M < 4,5'te her sınıfta ~%60 oranında **eşit** ayıklıyor. k_GK > 0, büyük olayları **daha az** ayıklamasından geliyor.
- **OUT (düzeltme):** md/ml dönemlerinde Δb'nin korunması etkinin ölçekten bağımsız olduğunu "kanıtlamıyordu"; yalnızca tutarlıydı. Bunu sınamak bu turun konusu (sonuç aşağıda: Δb korunuyor, eğim mekanizmasının dağılımı ise ölçek seçimine bağlı).
- **OUT (beklenti):** Homojenleştirme M ≥ 5'teki gürültüyü azaltmaz. Gürültü sayım sınırlıdır (binom); dönüşüm yalnızca olayları sınıflar arasında kaydırır.

## Yöntem

- **Bağıntılar:** `index.html` `MAG_CONVERSIONS` kayıtlarının Python kopyası; yeni bağıntı eklenmedi.
  - **H0:** ham EMSC.
  - **H1** `combined_dispatch`: mb/Ms → Scordilis (2006); ML → Çıvgın & Scordilis (2019); Md ham kalır.
  - **H2** `combined_dispatch_md_eqml`: H1 + Md < 4,0 için MD = ML varsayımı.
  - **H3** `combined_dispatch_md`: H1 + Md < 4,0 için KOERI zinciri (Cambaz vd. 2019 Md→ML + Çıvgın & Scordilis).
  - **H2+A:** H2 + otoriter Mw (`data/mw_authority.json`).
  - **H3\* (tanı, site bağıntısı değil):** zincir Md ≥ 4,0'a da uygulanır; H3'ün Md < 4 sınırının yarattığı boşluğu ayırmak için.
- **Parite:** `site_donusum_parite.mjs`, `index.html` bloğunu Node'da değiştirmeden çalıştırır. Üç site dispatch'i için 80 929 olayın tamamı Python kopyasıyla birebir aynı.
- **Ayrıştırma:** İki yöntem her varyantta dönüştürülmüş büyüklüklerle Türkiye 30 km alt kümesinde yeniden çalıştırıldı; xmeff 3,0 sabit. Varyant başına sınıf değiştiren olay: GK74 1 127–2 095, RB 861–1 592 (44 697 olayın %2–5'i).
- **Mc:** dönem başına max(GFT R≥95/90, MAXC+0,2, **tür tabanı**). Tür tabanı, ham dosya her türde M ≥ 3,0 ile kesik olduğu için gerekli: dönüşüm sonrası türlerin alt sınırları ayrışıyor (ör. H3'te Md → Mw ≥ 2,45, ML → Mw ≥ 3,08). Bu sınırın altında katalog tür karışımı bakımından eksik. Yalnız dosya kesmesiyle kesilmiş türler (ham en küçük = 3,0, pay ≥ %1) tabana katılır.
  - **İlk çalıştırmada bu sınır yoktu:** H3 md döneminde Mc 2,7 seçildi ve b ham 0,75 çıktı. Bu, yapay bir tür karışımı sonucuydu.

## Sonuç

**Δb = b_RB − b_GK74** (95% için ×1,96σ):

| Varyant | md 1998–2013: Mc | md Δb (z) | md k_GK / k_RB | ml 2013–2026: Mc | ml Δb (z) | ml k_GK / k_RB | **Birleşik Δb (z), Q** |
|---|---|---|---|---|---|---|---|
| H0 ham | 3,2 | +0,136 (6,1) | +0,087 / −0,039 | 3,2 | +0,148 (7,8) | +0,121 / −0,054 | **+0,143 ± 0,014 (9,9)**, 0,19 |
| H1 | 3,2 | +0,149 (6,5) | +0,078 / −0,034 | 3,3 | +0,176 (7,8) | +0,108 / −0,047 | **+0,163 ± 0,016 (10,2)**, 0,71 |
| H2 | 3,3 | +0,167 (6,2) | +0,079 / −0,034 | 3,3 | +0,176 (7,8) | +0,108 / −0,047 | **+0,172 ± 0,017 (10,0)**, 0,07 |
| H3 | 3,1 | +0,137 (7,1) | +0,131 / **+0,008** | 3,3 | +0,176 (7,8) | +0,108 / −0,047 | **+0,153 ± 0,015 (10,5)**, 1,77 |
| H3\* (tanı) | 3,1 | +0,146 (7,1) | +0,125 / **−0,000** | 3,3 | +0,176 (7,8) | +0,108 / −0,047 | +0,160 ± 0,015 (10,5), 0,98 |
| H2+A | 3,3 | +0,174 (6,4) | +0,076 / −0,042 | 3,3 | +0,176 (7,8) | +0,108 / −0,047 | **+0,175 ± 0,017 (10,1)**, 0,00 |

- **ml dönemi, 2023+ hariç:** Mw varyantlarında Δb +0,131 ± 0,029 (z 4,5); H0'da +0,110.
- **Mutlak b, md dönemi:** H2'de 1,42, H3'te 0,86. İki Md bağıntısı (MD ≈ ML ↔ Cambaz zinciri, Md − ML ≈ +0,7) md döneminin mutlak b'sini ~0,5–0,6 değiştiriyor.

**M ≥ 5 kalan oranlar** (tüm dönem, Wilson %95):

| Sınıf | H0: N | f_GK74 | f_RB | Mw varyantları (H1–H3): N | f_GK74 | f_RB |
|---|---:|---|---|---:|---|---|
| 5,0–5,5 | 162 | 0,59 [0,51–0,66] | 0,68 [0,60–0,75] | 354 | 0,49 [0,43–0,54] | 0,62 [0,57–0,67] |
| 5,5–6,0 | 43 | 0,56 [0,41–0,70] | 0,63 [0,48–0,76] | 76 | 0,63 [0,52–0,73] | 0,68 [0,57–0,78] |
| ≥ 6,0 | 19 | 0,79 [0,57–0,91] | 0,74 [0,51–0,88] | 23 | 0,74 [0,54–0,87] | 0,74 [0,54–0,87] |

## Cevap

- **Δb ölçek homojenleştirmesinde korunuyor:**
  - Birleşik Δb tüm varyantlarda +0,14 ile +0,18 arasında, z ≈ 10.
  - md ve ml dönemleri arasında heterojenlik yok (Q 0,00–1,77; 1 sd).
  - Mw ölçeğinde Δb biraz büyüyor (H0 +0,143 → H2 +0,172). Bunun bir kısmı ölçek gerilmesi: ML → Mw eğimi 0,93 olduğu için Mw'de b ≈ b_ML / 0,93.
  - Homojenleştirmeden sonra md ve ml dönemlerinin Δb'leri daha yakın (H2: +0,167 ↔ +0,176).
- **Eğim mekanizması — korunan yön:** k_GK74 tüm varyant ve dönemlerde pozitif (+0,08…+0,13). Eğimden öngörülen Δb (k_GK − k_RB), gözleneni her varyantta ±0,05 içinde izliyor.
- **Eğim mekanizması — ölçeğe bağlı kısım (4. tur bulgusunu sınırlayan sonuç):** Reasenberg'in negatif eğimi (büyük olayları daha çok kümeye bağlaması) **ölçek seçimine bağlı.**
  - H0, H1, H2 ve ml döneminde k_RB −0,03…−0,05.
  - KOERI zinciriyle (H3, H3\*) md döneminde k_RB ≈ 0; Δb tümüyle GK74'ün eğiminden geliyor.
  - Bu nedenle 4. turdaki "iki yöntem yarı yarıya katkı veriyor" ifadesi **H0 ölçeğine özgüdür.** Ölçekten bağımsız olan, Δb'nin varlığı ve GK74'ün pozitif eğimi.
- **M ≥ 5:**
  - Dönüşüm M ≥ 5 olay sayısını ikiye katlıyor (224 → 453). Başlıca neden mb → Mw'nin (Scordilis 2006) mb 4,6–5,0 olaylarını 5,0 üstüne taşıması.
  - Fark yalnız 5,0–5,5 sınıfında anlamlı: f_GK74 0,49 ↔ f_RB 0,62, güven aralıkları ayrık.
  - M ≥ 5,5'te güven aralıkları örtüşüyor; M ≥ 6'da iki yöntem aynı (0,74).
  - Gürültü sayım sınırlı (aralık yarı genişliği ±0,10–0,17); homojenleştirme bunu azaltmıyor.
- **Yorum:** Δb, büyüklük ölçeği seçiminden bağımsız olarak var olan, ayrıştırma algoritmalarının **istatistiksel katalog seçimi** etkisidir; fiziksel sismisite değişimi kanıtı değildir. Mutlak b (özellikle md döneminde) Md bağıntısı seçimine ~0,5 düzeyinde duyarlı. Mutlak b, yalnız tek bir dönüşüm seçeneğiyle ve bu duyarlılık belirtilerek raporlanmalı.

## Sınırlılıklar

- **H3 (site bağıntısı):** Md ≥ 4,0 olayları ham bıraktığı için md döneminde Mw 3,4–3,9 aralığında Md kaynaklı olay yok (0 olay). H3\* tanı varyantı boşluğu doldurunca sonuç değişmiyor (Δb +0,137 → +0,146). Yine de boşluk, sitenin KOERI Md zinciri seçeneğinde b analizlerini etkileyebilecek bir **site bulgusu**; ayrıca not edilmeli. Site değiştirilmedi.
- **Yuvarlama:** Dönüştürülmüş büyüklükler 0,1'e yuvarlandı. 0,93 eğimi bazı kutularda yığılma ve boşluk yaratır; f(M) kutularında ek gürültü kaynağıdır.
- **xmeff:** 3,0 sabit tutuldu. Mw ölçeğinde (özellikle H3'te Md → Mw 2,45) yeniden seçilmesi ayrıca sınanabilir.
- **Tür tabanı ve Mc:** Bu kural Mc'yi en fazla 0,1 yükseltti. Gerçek tamlık 3,0 altındaysa dosya kesmesi nedeniyle ölçülemez.
- **Bağıntı sınırları:** ML ve mb bağıntıları ajans ve bölge farkı içerir (Çıvgın & Scordilis 2019 KOERI ağı için türetildi; EMSC ML'si birden çok ajanstan gelir).
- Bulgular tehlike değerlendirmesi değildir.

## Sonraki adım (onay sonrası)

- **DOUBLET adaylarının literatürle karşılaştırılması** (5. aşama).
