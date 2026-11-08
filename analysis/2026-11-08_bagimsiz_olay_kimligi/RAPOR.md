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
