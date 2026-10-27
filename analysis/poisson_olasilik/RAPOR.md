# Poisson aşılma olasılığı — doğrulama raporu (2026-10-27, güncelleme 2)

**Dal:** `bolge-karsilastirma-a-etiketi`. Bu dal, tarihsel pencere düzeltmesini (`tarihsel-pencere-T`, 17ca240) içerir. `main`'e birleştirilmedi, canlıya yayımlanmadı.

**Güncelleme 2'de değişenler:**
- Tarihsel pencere düzeltmesi dala birleştirildi.
- GK74 uyarı metni nötr hale getirildi.
- Kapsama oranlarına Wilson %95 aralığı ve test parametreleri eklendi.
- Kabul testinin "önce" sayfası artık `tarihsel-pencere-T`. Böylece yalnızca Poisson değişikliği karşılaştırılıyor.
- Gözlenen ve öngörülen sayılar karşılaştırıldı (§4).

## 1. Ne eklendi

| Öğe | Tek Mc (Aki–Utsu) | Tamlık basamakları (Weichert 1980) |
|---|---|---|
| Denklem | log₁₀[N(≥M)/T] = a_T − b·M | log₁₀λ(≥M) = a − b·M; Mx girildiyse kesik G–R (Eş. 14) |
| λ(≥M) | N(≥Mc)/T · 10^(−b(M−Mc)) | panelin en iyi tahmin eğrisi (`rateGE` + `curveFn`) |
| P(t), Tr | P = 1 − e^(−λt) (`expm1`), Tr = 1/λ | aynı |
| T | seçili analiz penceresi; tarihsel modda seçili tarihsel pencere(ler) | tamlık dönemleri (aynı pencere sonuyla) |
| %95 aralık | parametrik bootstrap: n* ~ Poisson(n); büyüklükler β̂ ile; b* Aki–Utsu ile | n_i* ~ Poisson(beklenen n_i); Weichert yeniden fit |

**Ayarlar ve girdiler:**
- Bootstrap: B = 1000, tohum 20261027, tekrarlanabilir.
- Girdiler: M ≥ (varsayılan 7,0) ve t (varsayılan 50 yıl). İkisi de URL'ye yazılır (`pm`, `pt`).

**Uyarılar:**
- GK74 kapalı. Yeni metin: "Poisson modelinin bağımsız olay varsayımı daha az uygun olabilir; ayıklamanın oran ve b üzerindeki etkisi veri kümesine göre değişir (ikisi birlikte değişir, olasılığın yönü önceden belli değildir)".
- Ekstrapolasyon: M gözlenen en büyük büyüklüğün üstünde.
- M ≥ Mx.
- M fit aralığının altında.
- Tek Mc tamlık denetimi: dönemin ilk yarısında M ≥ Mc olayları az (tek yönlü binom testi, p < 0,01).

**Metinde açıkça yazanlar:**
- Belirsizlik kapsamı: Poisson sayımı ve b birlikte.
- Kapsam dışı: Mc/tamlık seçimi, Mx, büyüklük hataları ve dönüşüm, artçı ayıklama yöntemi.
- Değerler seçili bölgenin tamamı içindir; bir noktanın tehlikesi ya da bir depremin zamanı değildir.

## 2. Birim testleri: `scripts/test_*.js`, 15/15

Yeni test `test_poisson_prob.js` (15 denetim).

**Analitik ve tutarlılık:**
- λ = 0,01 ve t = 50 → P = 0,393469 (= 1 − e^−0,5).
- λ = 1e−12 → P ≈ λt.
- t = Tr → P = 0,632.
- Tek Mc'de λ = 10^(a−bM)/T (göreli fark 1e−15).
- Weichert'te λ = panel eğrisi, kesilmesiz ve Mx = 7,5 iken (fark 0).

**Sentetik katalog parametreleri:**

| Deney | Gerçek model | Katalog | Hedef |
|---|---|---|---|
| A: tek Mc | λ(≥3,0) = 2/yıl, b = 1, ΔM = 0,1 | T = 60 yıl, 200 katalog, her biri B = 400 | λ(≥6), P(50 yıl) |
| B: Weichert | λ(≥3,0) = 5/yıl, b = 1, ΔM = 0,1; tamlık M ≥ 3 son 30 yıl, M ≥ 4 80 yıl, M ≥ 5 200 yıl | 200 katalog, B = 400 | λ(≥6,5), P(50 yıl) |

**Sonuçlar** (köşeli parantez: kapsama oranının Wilson %95 aralığı, 200 katalog):

| Ölçüt | Sonuç |
|---|---|
| A: log₁₀λ(≥6) ortalaması | −2,722 (gerçek −2,699) |
| A: bootstrap kapsaması, λ ve P | %94,0 [%89,8–%96,5] |
| B: log₁₀λ(≥6,5) ortalaması | −2,788 (gerçek −2,801) |
| B: bootstrap kapsaması, λ ve P | %95,5 [%91,7–%97,6] |
| A: yalnız b ±1,96σ aralığı, M = 6 | %96,0 [%92,3–%98,0] |
| A: yalnız b ±1,96σ aralığı, M = Mc | **%3,0 [%1,4–%6,4]** |
| A: ortak bootstrap, M = Mc | %96,5 [%93,0–%98,3] |

Üç bootstrap kapsamasının da aralığı %95'i içeriyor. Yalnız b'ye dayalı aralık Mc'den uzakta yeterli, ama Mc yakınında sayım belirsizliğini kaçırıyor.

Kapsam sınırı: Bu deneylerde model doğrudur. Yani G–R, Poisson, bilinen tamlık ve hatasız büyüklük varsayılıyor. Gerçek kataloglardaki tamlık hatası, büyüklük hatası ve kümelenme bu kapsamaya dahil değildir (§4).

## 3. Tarayıcı kabul testi: `kabul_poisson.js`, 32/32

- Senaryo: Türkiye modu, ISC 1971–1997, dikdörtgen 36–42° K / 26–45° D.
- Önce: `tarihsel-pencere-T` (main + pencere düzeltmesi). Sonra: bu dal.

| Koşul | Sonuç |
|---|---|
| (1) G–R grafiği ve Poisson satırı dışındaki metin önce = sonra (8 senaryo) | aynı; tek fark a'nın tanımı (değeri aynı) |
| (2) Tek Mc λ = N(≥Mc)/T·10^(−b(M−Mc)) | göreli fark ≤ 2e−16; T = 27,001 yıl (seçili pencere) |
| (2) Weichert λ = `lastGrFit.fnBest` | birebir; Mx = 7,5 ve M = 8 → λ = 0 |
| (2) Ekrandaki P yüzdesi 1 − e^(−λt) ile aynı | aynı |
| (2) Pencerenin ilk yarısı boşken tamlık uyarısı | "0 / 2200; p = 0" (benzetim: T 1900'den) |
| (3) Varsayılan M = 7, t = 50; girdi URL'ye yazılıyor | geçti |
| (4) GK74 uyarısı kapalıyken var, açıkken yok; ekstrapolasyon; M ≥ Mx | geçti |
| (5) Bölge bütünü / tahmin değildir notu ve belirsizlik kapsamı | iki yolda da var |
| Sayfa hatası | 0 |

Ekran görüntüleri:
- `poisson_tekMc_gk74kapali.png`
- `poisson_tekMc_gk74acik.png`
- `poisson_weichert.png`
- `poisson_weichert_mx.png`

## 4. Gözlenen ve öngörülen sayılar (aynı senaryo, T = 27 yıl)

| | Gözlenen (1971–1997) | Tek Mc (Mc = 3,7, b = 0,77) | Weichert (b = 0,947) |
|---|---|---|---|
| N(M ≥ 6) / yıl | 13 olay → 0,48 | 1,36 | — |
| N(M ≥ 7) / yıl | 1 olay (1976 Çaldıran, Mw 7,0) → 0,037 [Poisson %95: 0,0009–0,21] | 0,23 [0,18–0,29] | 0,097 |
| P(50 yıl, M ≥ 7) | — | %100,0 | %99,2 |

**Tek Mc yolu bu katalogda büyük M oranını açıkça abartıyor.** M ≥ 6 için öngörü gözlenenin yaklaşık 2,8 katı. Nedenleri:
- Katalog Mc = 3,7'de 1971–1997 boyunca tam değil. Tamlık uyarısı bunu gösteriyor: ilk yarıda 498 / 1702 olay, p = 1,6e−153.
- Bu yüzden b = 0,77 düşük çıkıyor.

Panel bu durumda uyarı verip Weichert'i öneriyor. Ancak öngörülen değer yine de ekranda görünüyor.

Weichert öngörüsü (0,097/yıl) tek olayın Poisson aralığı içinde kalıyor. Yine de bu aralık çok geniş; 27 yıllık bir pencere M ≥ 7 oranını sınamaya yetmez.

Öneri (karar sizde): Poisson satırına "gözlenen N(≥M) ile öngörülen λT" karşılaştırmasını ve bunun Poisson p değerini eklemek. Ayrıca tek Mc tamlık uyarısı varken P değerini soluk göstermek ya da gizlemek. Bu, ChatGPT'nin "yanlış oranı doğruymuş gibi sunmamalı" koşulunu veri düzeyinde de karşılar.

## 5. Literatür ile karşılaştırma

### Michael & Llenos (2026), BSSA 116(2), 786–809, doi:10.1785/0120240245

Yöntemleri:
- Dönem başına oranı Poisson olabilirliğinden çekiyorlar.
- b'yi N(b, σ_b)'den çekiyorlar (3σ'da kırpılmış, 0 < b < 1,5).
- Mc'yi tek yönlü normal gürültüyle örnekliyorlar (σ = 0,2).
- Büyüklük hatalarını Rhoades yöntemiyle ekliyorlar: M* = M_est − βσ_m²/2.

EQ-Live ile ilişkisi:
- EQ-Live'ın sayım + b bootstrap'ı ilk iki bileşenle aynı mantıkta.
- Mc ve büyüklük hatası bileşenleri bizde "dahil değil" olarak yazıldı; sıradaki genişleme bunlar.

Diğer notlar:
- Dönem birleştirmede Weichert yerine süre ağırlığını tartışıyorlar (s. 806).
- Oranı artçılar dahil tam katalogdan alıyorlar; GK74'ün b'yi düşürdüğünü belirtiyorlar (s. 788, 807).
- GK74 metninin nötr hale getirilmesi bununla ve kendi verimizle tutarlı. Türkiye senaryosunda GK74 açılınca λ(≥7) 0,228'den 0,227'ye iniyor: N yarıya düşüyor, ama b de 0,77'den 0,69'a düşüyor.

### Dutilleul, P., Genest, C. & Peng, R. (2024), GJI 236(3), 1601–1608, doi:10.1093/gji/ggae003

- Konu: ETAS parametreleri için parametrik bootstrap. Dar pencerelerde asimptotik (Hessian) aralıklar yanıltıcı olabiliyor.
- Uygunluk: model farklı (ETAS, G–R/Weichert değil). Ortak olan yöntem: uydurulan modelden katalog benzetimi, yeniden kestirim ve kapsamanın sentetik deneyle sınanması (§2).
- EQ-Live'daki bootstrap bağımsız olaylar varsayar; ETAS'taki kümelenme bileşeni yoktur.
- Not: önceki ChatGPT notundaki "Holschneider ve diğerleri" atfı yanlış; yazarlar burada yazıldığı gibidir.

### van der Elst (2021), JGR Solid Earth 126, e2020JB021027, doi:10.1029/2020JB021027

b-positive yöntemi değişken tamlığa dayanıklıdır. §4'teki tamlık sorunu için b'ye bağımsız bir çapraz denetim olabilir. Öneri; kapsam dışı.

## 6. Kapsam ve sınırlar

- Poisson (zamandan bağımsız) varsayımı kullanılıyor; artçı kümelenmesi bu varsayımı bozar.
- Değerler bölge bütünü içindir; nokta tehlikesi, yer sarsıntısı ya da deprem tahmini değildir.
- Tek Mc yolu kesilmesizdir. Katalog Mc'de tam değilse büyük M oranını abartabilir (§4); panel bu durumda uyarır.
- Bitişik olmayan tarihsel pencerelerde T aradaki boşluğu da içerir. Durum satırı bunu uyarır.
