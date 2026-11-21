# EQ-LiveTürkiye — SAF ve NAF Karşılaştırmalı Sismolojik Araştırma Tasarımları
## Tasarım 1 — SCEDC–SAF (San Andreas Fayı)

**Çalışma başlığı (taslak):** *Seismicity Characteristics and Gutenberg–Richter b-Value Variations Along the San Andreas Fault System (2008–2026)*
**Sürüm:** tasarım v0.2 · 2026-11-21 · Durum: **onaylandı** (danışman kararları §10'a işlendi; kod yazılmadı)
**Karar kaydı:** `KARAR_2026-11-21.md` · **Eş belge:** `TASARIM_EMSC_NAF.md`

> Bu belge bir çerçevedir; sonuç içermez. Her iş paketi (İP) başlamadan önce kendi **ön kaydını** (hipotez, parametreler, kabul ölçütleri) ayrı bir dosya olarak commit eder; sonuçlar ancak ondan sonra hesaplanır. PMSR 2018–2026 çalışmasında uygulanan düzen budur (`analysis/2026-11-19_pmsr_scsn_2018_2026/ON_KAYIT.md`).

---

## 1. Amaç

Güney Kaliforniya'da San Andreas Fayı (SAF) boyunca, 2008–2026 SCEDC SCSN kataloğuyla:
1. kataloğun kendisini (tamamlanma, büyüklük türleri, işleme kırılmaları) nicel olarak tanımlamak,
2. b-değerinin fay boyunca ve zamanla değişimini, katalog kaynaklı etkilerden ayrılmış biçimde ölçmek,
3. kümelenme ayıklama yöntemi seçiminin (GK74, Reasenberg, Zaliapin) bu sonuçlara etkisini göstermek,
4. ana şok öncesi oran artışlarını (PMSR) segment bazında betimlemek,
5. NAF çalışmasıyla aynı yöntemleri uygulayarak SAF–NAF karşılaştırmasına girdi üretmek.

Ana fikir: **farkın tektonikten mi yoksa katalogdan/yöntemden mi geldiğini** her adımda ayırmak.

## 2. Araştırma soruları (RQ)

| RQ | Soru | İlgili İP |
|---|---|---|
| RQ1 | SCEDC kataloğunda Mc zaman ve konuma göre nasıl değişiyor; bilinen işleme değişiklikleri (2015-01, 2015-12, 2023-11) Mc ve büyüklük dağılımında ölçülebilir kırılma yaratıyor mu? | İP1 |
| RQ2 | SAF segmentleri arasında b-değeri istatistiksel olarak anlamlı biçimde farklı mı; fark, faya uzaklık şeridine (10/20/30 km) göre değişiyor mu? | İP2 |
| RQ3 | b-değerinde zamansal değişim var mı; varsa katalog kırılma tarihleriyle mi, büyük depremlerle mi çakışıyor? | İP1, İP2 |
| RQ4 | Ayıklama yöntemi seçimi arka plan oranını ve b-değerini ne kadar değiştiriyor; segmentler arası sıralama yöntemden bağımsız mı? | İP3 |
| RQ5 | Segmentlerde ana şok öncesi anlamlı oran artışı oranı, bölge kutusu sonucundan (%24,5; 12/49) farklı mı? | İP4 |

Hipotezler ve sınama ölçütleri her İP'nin ön kaydında sayısal olarak yazılır (ör. "segmentler arası b farkı Utsu testiyle, FDR q = 0,05").

## 3. Veri

| Öğe | Değer |
|---|---|
| Katalog | SCEDC SCSN, `data/scedc/` anlık görüntü **2026-11-18** (415 080 olay, 2008-01-01 – 2026-11-17; 2026 kısmi) |
| Atıf | SCEDC (2013), doi:10.7909/C3WD3XH1; Hutton vd. (2010) |
| Alan | 32–37° K, 122–114° B (SCEDC dosya alanı) |
| Olay türü | Birincil: `event_type = eq`; `qb` (patlama) ve diğerleri çıkarılır, çıkarılan sayı raporlanır |
| Büyüklük | `mag` (SCEDC tercih edilen); **dönüşüm yapılmaz** (OUT 6). Türler (`l`, `w`, `h`, `lr`) her analizde ayrı raporlanır |
| Derinlik | Birincil: tümü; duyarlılık: ≤ 20 km (sismojenik kabuk) |
| Güncel veri | SCEDC FDSN API (ayrı geliştirme, Uygulama sırası 3). API sonuçları ayrı etiketlenir ve dondurulmadan arşiv sonuçlarıyla karıştırılmaz |

**Bilinen katalog değişiklikleri** (`data/scedc/manifest.json`): 2008-01-01 yeni ML; 2013 otomatik işleme; 2015-01-01 M < 2,5'te elle zamanlamanın bırakılması; 2015-12 Mlr; 2019-07 Ridgecrest M < 2,5 büyük ölçüde gözden geçirilmemiş; 2023-11-06 M < 3 için PhaseNet; 2024-11 PhaseNet + GaMMA.

**Büyük diziler** (b ve Mc'yi yerel ve geçici olarak bozar; ayrı işaretlenir): 2010 El Mayor–Cucapah Mw 7,2; 2019 Ridgecrest Mw 6,4/7,1. İkisi de SAF ana izinin dışında, ama 30 km şeritlerle ve bölgesel zaman serileriyle etkileşebilir.

## 4. Çalışma alanı: SAF ve segmentler

**Fay izi kaynağı — Karar (2026-11-21): UCERF3 fay bölümleri** (Field vd., 2014) — segment adları ve sınırları yayımlanmış ve sabit; kaynak dosyası sürümüyle birlikte arşive alınır. SCEC Community Fault Model (Plesch vd., 2007) veya USGS Kuvaterner Fay ve Kıvrım Veritabanı yalnız duyarlılık için ikinci model olabilir (açık konu, §10).

**Ön segment listesi** (SCEDC alanı içinde, kuzeyden güneye; sınırlar seçilen fay modelinden alınır):

| Segment | Not |
|---|---|
| Sürünen kesim (güney ucu) | 37° K sınırında kısmen kapsamda; kapsam yeterliliği İP1'de denetlenir |
| Parkfield | Yoğun mikrosismisite; b-değeri literatürü zengin |
| Cholame | |
| Carrizo | 1857 Fort Tejon kırığı; çok düşük mikrosismisite beklenir |
| Big Bend / Mojave (kuzey, güney) | |
| San Bernardino | San Jacinto ve Banning ile karmaşık geometri |
| Coachella | Salton Gölü'ne kadar |

**Uzaklık şeritleri:** fay izine yatay uzaklık ≤ 10, ≤ 20, ≤ 30 km (iç içe) ve halkalar (0–10, 10–20, 20–30 km). Mesafe: WGS84 jeodezik (PMSR'deki Vincenty ile aynı). Bir olay birden çok segmente yakınsa en yakın segmente atanır; segment uçlarında ±10 km tampon duyarlılığı.

**Fay sistemi bağlamı:** San Jacinto, Elsinore, Garlock ve Doğu Kaliforniya Kesme Zonu aynı katalogda. Ana analiz SAF şeritleriyle sınırlıdır; **Karar (2026-11-21): üç kontrol bölgesi ana tasarımdadır — San Jacinto Fayı, Elsinore Fayı ve Doğu Kaliforniya Kesme Zonu (ECSZ).** Kontrol bölgelerine SAF ile aynı şerit, yeterlilik ve Mc kuralları uygulanır. Böylece SAF'a özgü sonuç ile bölgesel katalog etkisi ayrılabilir (Garlock bağlam olarak işaretlenir, kontrol bölgesi değildir).

Yeterlilik kuralı: bir segment × şerit × dönem hücresi, Mc üstünde **N ≥ 100** olay yoksa b raporlanmaz (duyarlılık: N ≥ 50, açıkça işaretli).

## 5. İş paketleri

### İP1 — Katalog karakterizasyonu (RQ1, RQ3) · makale P1
- **Mc(t):** tüm alan ve her segment için kayan pencerelerle (ör. 500 olay veya 1 yıl; ön kayıtta sabitlenir).
- **Mc(x):** ızgara veya segment bazında.
- **Yöntemler:** MAXC (+0,2 düzeltmesi), MBS (Cao & Gao, 2002; PMSR'deki uygulamayla aynı ΔM 0,4), EMR (Woessner & Wiemer, 2005). **Karar (2026-11-21): birincil yöntem MBS** (PMSR'deki doğrulanmış uygulamayla tutarlı); MAXC+0,2 ve EMR ikincil olarak raporlanır. Yöntemler arası fark > 0,2 olan hücreler işaretlenir.
- **Büyüklük türü dağılımı:** yıl × büyüklük aralığı tablosu (ör. M ≥ 3'te `l`/`w`/`h`/`lr` oranları).
- **Kırılma testleri:** her bilinen tarihte önce/sonra karşılaştırması: Mc farkı, GR uyumu, ve (Mc üstünde) b farkı (Utsu testi). Büyük dizilerin etkisini dışlamak için kontrol bölgeleri. Kırılma tarihleri **önceden bilindiği** için hipotez testi uygundur; veri güdümlü değişim noktası arama yalnızca keşifsel.
- **Çıktı:** Mc(t, x) tabloları, büyüklük türü tablosu, kırılma testleri; İP2–İP4 için **dönem başına önerilen Mc**.

### İP2 — b-değerinin uzay-zaman değişimi (RQ2, RQ3) · makale P2
- **b tahmini:** Aki (1965) / Utsu (1965) en çok olabilirlik (bin düzeltmeli); belirsizlik Shi & Bolt (1982) ve bootstrap (1000).
- **Karşılaştırma:** segmentler ve şeritler arası Utsu (1992) testi; çoklu karşılaştırma için Benjamini–Hochberg FDR.
- **Haritalama:** fay boyunca, sabit olay sayılı kayan pencere (N = 100–200, ön kayıtta sabit) ve en büyük yarıçap sınırı.
- **Tamamlanmaya dayanıklı kontrol:** b-positive (van der Elst, 2021); klasik b ile uyumsuzluk tamamlanma sorununa işaret olarak raporlanır.
- **Uyarılar:** Marzocchi vd. (2020) — anlamsız b "değişimleri" bulmanın tipik yolları (küçük N, Mc hatası, çoklu test, pencere seçimi) açıkça önlenir.
- **Çıktı:** segment × şerit × dönem b tablosu, güven aralıkları, testler, fay boyunca profil.

### İP3 — Kümelenme ayıklama karşılaştırması (RQ4) · makale P3
| Yöntem | Uygulama | Not |
|---|---|---|
| GK74 (Gardner & Knopoff, 1974) | EQ-Live'daki doğrulanmış uygulama, **değiştirilmeden** (OUT 2) | Pencere parametreleri ön kayıtta |
| Reasenberg (1985) | EQ-Live'daki doğrulanmış uygulama, **değiştirilmeden** (OUT 3) | Varsayılan parametreler + duyarlılık |
| Zaliapin & Ben-Zion (2013) en yakın komşu | **Yeni** bağımsız uygulama (ayrı dalda, kendi testleriyle) | b, d_f, q parametreleri ve eşik (iki bileşenli karışım) ön kayıtta |

- **Ölçütler:** arka plan oranı, ayıklanmış kataloğun b'si, segment sıralamasının yöntemler arasında korunup korunmadığı (Kendall τ), kümelenmiş/arka plan olay örtüşmesi.
- **Uyarı:** ayıklama b'yi sistematik olarak değiştirebilir (Mizrahi vd., 2021); bu yüzden b her zaman hem tüm katalog hem ayıklanmış katalog için raporlanır.

### İP4 — Segmentlerde PMSR (RQ5) · makale P4 (NAF ile ortak)
- **Kod:** `lab/premainshock-rate/core.mjs` **değiştirilmeden** (OUT 4), varsayılan parametrelerle; yalnız ana şok kümesi segment/şerit ile sınırlanır.
- **Beklenen sorun:** segment başına ana şok sayısı küçük (bölge kutusunda 9 yılda 52). Sonuçlar Wilson aralıklarıyla betimleyici; segmentler arası test yalnızca toplam N yeterliyse.
- **Etiket:** "ana şok öncesi anlamlı oran artışı"; "öncü" veya tahmin dili yok (OUT 7).

### İP5 — SAF–NAF karşılaştırmasına girdi · makale P5
`TASARIM_EMSC_NAF.md` ile **aynı** ölçüm protokolü uygulanır. Karşılaştırma iki düzeyde yapılır:
1. **Doğal Mc:** her katalog kendi ölçülen Mc'siyle.
2. **Ortak eşik:** M_ortak = max(Mc_SAF, Mc_NAF) (+ duyarlılık +0,2, +0,5). Bunun için SCEDC kataloğu, büyüklük türü dağılımı NAF'a yakın olacak biçimde de alt örneklenebilir (açık konu, §10).

**Veri–yöntem ayrımı (ilke 3):** aynı SCEDC verisi EMSC'nin göreceği biçimde de incelenir: SCEDC'yi EMSC'nin Kaliforniya kaydıyla (aynı dönem, aynı alan) karşılaştırmak, "toplayıcı katalog" etkisinin SAF'ta ne kadar olduğunu ölçer. Bu fark bilinirse NAF'ta EMSC kullanmanın etkisi yorumlanabilir.

**Sınırlılık — tam faktöriyel tasarım değildir.** Bu 2 × 2 düzen, katalog etkisinin büyüklüğünü kestirmeye yardım eder; ancak katalog ve tektonik etkilerini **tamamen ayrıştırmaz**. Nedenleri: (i) iki bölgedeki "bölgesel birincil" kataloglar farklı ürünlerdir (SCEDC ↔ AFAD: farklı ağ yoğunluğu, işleme ve büyüklük ölçekleri); (ii) EMSC iki bölgede aynı ürün gibi davranmaz (katkı veren kurumlar ve ağ geometrisi farklıdır); (iii) ağ yoğunluğu ile tektonik ortam bölge düzeyinde iç içedir ve aynı bölgede birbirinden bağımsız değiştirilemez. Sonuçlar bu nedenle "katalog türünden bağımsız kalan farklar" ve "katalog etkisinin tahmini büyüklüğü" olarak raporlanır; artık karışıklık (confounding) açıkça belirtilir ve kesin nedensel ayrıştırma iddia edilmez.

## 6. Tekrarlanabilirlik (ilke 4)

Her analiz çıktısı bir **çalıştırma kaydı** (JSON) taşır: katalog anlık görüntü kimliği ve kullanılan dosyaların `sha256_gz` değerleri; fay modeli dosyası ve SHA-256; kod commit kimliği ve sürümler (`pmsr-core-0.1.0` gibi); tüm parametreler; rastgele tohum (bootstrap). İki bağımsız çalıştırma bayt bayt aynı çıktı vermelidir (PMSR 2018–2026'daki doğrulama düzeni). Yeni kod (Zaliapin, Mc/b araçları) yayımlanmış bir referans uygulamayla ya da sentetik GR kataloğuyla parite testi geçmeden kullanılmaz.

## 7. Yayın planı

| Makale | İçerik | Bağımlılık |
|---|---|---|
| P1 | SCEDC 2008–2026 katalog karakterizasyonu: Mc(t, x), büyüklük türleri, işleme kırılmaları | — |
| P2 | SAF boyunca b-değerinin uzay-zaman değişimi | P1 |
| P3 | Ayıklama yöntemine duyarlılık: GK74, Reasenberg, Zaliapin | P1 |
| P4 | Segment bazında ana şok öncesi oran artışları (SAF ve NAF) | P1, NAF-P1 |
| P5 | SAF–NAF: katalog ve tamamlanma etkisinin tektonik yorumdan ayrılması | P1–P3, NAF tasarımı |

## 8. Riskler ve sınırlılıklar
- **Carrizo gibi sessiz segmentlerde N yetersiz:** b raporlanmaz; yalnız oran ve Mc betimlenir.
- **Büyüklük türü karışımı** (büyük olaylarda Mw, küçüklerde ML): GR eğimi M ~3,5 üstünde tür değişiminden etkilenebilir; b, ML-baskın aralıkla sınırlı da hesaplanır.
- **Ridgecrest dizisinin gözden geçirilmemiş kısmı:** 2019-07 – 2020 dönemi ayrı işaretlenir.
- **2026 kısmi:** yıllık sonuçlarda ayrıca etiketlenir.
- **Fay modeli seçimi** segment sonuçlarını değiştirebilir: ikinci bir modelle duyarlılık (açık konu, §10).

## 9. Aşamalar (tarih yok; sıralı)
1. Tasarım onayı (2026-11-21, tamam) → 2. İP1 ön kaydı → 3. İP1 → 4. İP2 ve İP3 ön kayıtları → 5. İP2, İP3 → 6. İP4 → 7. İP5 (NAF İP'leriyle birlikte) → 8. Yayın.
SCEDC API entegrasyonu (Uygulama sırası 3) İP1'i engellemez: İP1–İP3 dondurulmuş arşivle yapılır.

## 10. Danışman kararları
**Verilen kararlar (2026-11-21):**
| Konu | Karar |
|---|---|
| Fay izi kaynağı | UCERF3 fay bölümleri (Field vd., 2014) |
| Birincil Mc yöntemi | MBS (MAXC+0,2 ve EMR ikincil) |
| Kontrol bölgeleri | San Jacinto, Elsinore, Doğu Kaliforniya Kesme Zonu — ana tasarımda |

**Açık konular (ilgili İP ön kaydında karara bağlanacak):**
1. İkinci fay modeliyle duyarlılık (SCEC CFM veya USGS Qfaults).
2. Derinlik sınırı: tümü (öneri; ≤ 20 km duyarlılık) / ≤ 20 km birincil.
3. Ortak eşik deneyinde büyüklük türüne göre alt örnekleme.

## Kaynaklar
- Aki, K. (1965). Bull. Earthq. Res. Inst. Univ. Tokyo 43, 237–239.
- Cao, A., Gao, S. S. (2002). GRL 29(9).
- Field, E. H. vd. (2014). Uniform California Earthquake Rupture Forecast, Version 3 (UCERF3) — The time-independent model. BSSA 104(3), 1122–1180.
- Gardner, J. K., Knopoff, L. (1974). BSSA 64(5), 1363–1367.
- Hutton, K., Woessner, J., Hauksson, E. (2010). BSSA 100(2), 423–446.
- Khan, A. vd. (Azad Khan, Werner, Biggs, Fagereng) (2025). JGR Solid Earth 130(7), e2024JB030733.
- Marzocchi, W., Spassiani, I., Stallone, A., Taroni, M. (2020). How to be fooled searching for significant variations of the b-value. GJI 220(3), 1845–1856.
- Mizrahi, L., Nandan, S., Wiemer, S. (2021). The effect of declustering on the size distribution of mainshocks. SRL 92(4), 2333–2342.
- Plesch, A. vd. (2007). Community Fault Model (CFM) for Southern California. BSSA 97(6), 1793–1802.
- Reasenberg, P. (1985). JGR 90(B7), 5479–5495.
- SCEDC (2013). Southern California Earthquake Data Center. Caltech. doi:10.7909/C3WD3XH1.
- Shi, Y., Bolt, B. A. (1982). BSSA 72(5), 1677–1687.
- Utsu, T. (1965). Geophys. Bull. Hokkaido Univ. 13, 99–103.
- Utsu, T. (1992). On seismicity. Report of the Joint Research Institute for Statistical Mathematics, 139–157.
- van der Elst, N. J. (2021). B-positive: A robust estimator of aftershock magnitude distribution in transiently incomplete catalogs. JGR Solid Earth 126, e2020JB021027.
- Wiemer, S., Wyss, M. (2000). BSSA 90(4), 859–869.
- Woessner, J., Wiemer, S. (2005). BSSA 95(2), 684–698.
- Zaliapin, I., Ben-Zion, Y. (2013). Earthquake clusters in southern California I. JGR Solid Earth 118, 2847–2864.

*Kaynak künyeleri kod aşamasından önce DOI ile tek tek doğrulanacaktır.*
