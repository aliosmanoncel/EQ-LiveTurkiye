# Poisson aşılma olasılığı — doğrulama raporu (2026-10-27)

Dal: `bolge-karsilastirma-a-etiketi` (main'e birleştirilmedi; canlıya yayımlanmadı).

## 1. Ne eklendi

G–R panelinin altına, iki yolda da, bir Poisson satırı eklendi:

| Öğe | Tek Mc (Aki–Utsu) | Tamlık basamakları (Weichert 1980) |
|---|---|---|
| Denklem | log₁₀[N(≥M)/T] = a_T − b·M | log₁₀λ(≥M) = a − b·M; Mx girildiyse kesik G–R (Eş. 14) |
| λ(≥M) | N(≥Mc)/T · 10^(−b(M−Mc)) | panelin en iyi tahmin eğrisi (`rateGE` + `curveFn`), aynı fonksiyon |
| P(t), Tr | P = 1 − e^(−λt) (`expm1`), Tr = 1/λ | aynı |
| Mx | uygulanmaz (kesilmesiz) | panel girdisi; M ≥ Mx → λ = 0 |
| %95 aralık | parametrik bootstrap: n* ~ Poisson(n), büyüklükler β̂ ile, b* = Aki–Utsu | n_i* ~ Poisson(beklenen n_i), Weichert yeniden fit |

- Girdiler: M ≥ (varsayılan 7,0) ve t (varsayılan 50 yıl). İkisi de URL'ye yazılır (`pm`, `pt`).
- Bootstrap: B = 1000, tohum 20261027, tekrarlanabilir.

**Uyarılar:**
- GK74 kapalı.
- M gözlenen en büyük büyüklüğün üstünde: ekstrapolasyon.
- M ≥ Mx.
- M fit aralığının altında (Weichert).
- Tek Mc'de tamlık denetimi: tek yönlü binom, M ≥ Mc olaylarının dönemin ilk yarısında az olması, p < 0,01.

**Metinde açıkça yazanlar:**
- Belirsizlik kapsamı: Poisson sayımı ve b birlikte.
- Kapsam dışı: Mc/tamlık seçimi, Mx, büyüklük hataları ve dönüşüm, artçı ayıklama yöntemi.
- Değerler seçili bölgenin tamamı içindir; bir noktanın tehlikesi ya da bir depremin zamanı değildir.

**Başka değişiklikler:**
- Tek Mc panelinde `a`, gösterim moduna göre tanımıyla yazılıyor (Ham modda değer aynı).
- Sayısal değerler `lastGrPois` değişkeninde tutuluyor (doğrulama için; gösterimi etkilemez).
- Hesap yöntemlerine (b, Weichert, Mc, GK74) dokunulmadı.

## 2. Testler

**Birim testleri** (`scripts/test_*.js`): 15/15 geçti. 14 eski test ve 1 yeni test (`test_poisson_prob.js`, 15 denetim).

| Denetim | Sonuç |
|---|---|
| Analitik: λ = 0,01, t = 50 → P = 0,393469 = 1 − e^−0,5; λ = 1e−12'de P ≈ λt (expm1); t = Tr → P = 0,632 | geçti |
| Tek Mc λ = 10^(a−bM)/T (panel a ile) | göreli fark 1,3e−15 |
| Weichert λ = panel eğrisi (kesilmesiz ve Mx = 7,5) | fark 0 |
| Sentetik, tek Mc (λ₀ = 2/yıl, b = 1, T = 60 yıl, 200 katalog): log₁₀λ(≥6) ortalaması | −2,722 (gerçek −2,699) |
| Aynı katalog: bootstrap %95 kapsaması, λ ve P | %94,0 / %94,0 |
| Sentetik, Weichert (3 tamlık basamağı, 200 katalog): log₁₀λ(≥6,5) ortalaması | −2,788 (gerçek −2,801) |
| Aynı katalog: bootstrap %95 kapsaması | %95,5 |
| Yalnız b'nin ±1,96σ aralığı: M = 6'da / M = Mc'de | %96 / **%3** |
| Aynı karşılaştırmada ortak bootstrap, M = Mc'de | %96,5 |
| Binom tamlık denetimi: kesin değer 1/1024; tekdüze katalog → uyarı yok; başı eksik katalog → uyarı | geçti |

Yalnız b aralığıyla ilgili satırın anlamı: Mc'den uzakta b belirsizliği baskın olduğu için yalnız b aralığı yeterli kapsıyor. Mc yakınında ise sayım belirsizliği baskındır ve yalnız b aralığı bunu kaçırır. ChatGPT'nin "b aralığı tek başına yetmez" notu nicel olarak doğrulandı.

**Tarayıcı kabul testi** (`kabul_poisson.js`): 30/30 geçti.
- Senaryo: Türkiye modu, ISC 1971–1997, dikdörtgen bölge 36–42° K / 26–45° D.
- Önce = `main` 543ac56, sonra = bu dal.

| Koşul | Sonuç |
|---|---|
| (1) G–R grafiği (SVG) önce = sonra, 8 senaryoda | aynı |
| (1) Poisson satırı ve a tanımı dışındaki metin önce = sonra (tek Mc / Weichert; GK74 açık/kapalı; Mx boş/7,5) | aynı |
| (2) λ bağımsız yeniden hesapla aynı; ekrandaki P yüzdesi 1 − e^(−λt) ile aynı | tek Mc fark ≤ 1e−16; Weichert = `lastGrFit.fnBest` |
| (3) Varsayılan M = 7, t = 50; girdi değişince güncelleniyor ve URL'ye yazılıyor | geçti |
| (4) GK74 uyarısı kapalıyken var, açıkken yok; M = 8,5 ekstrapolasyon; Mx = 7,5 ve M = 8 → λ = 0, P = %0,0 | geçti |
| (5) Bölge bütünü / tahmin değildir notu ve belirsizlik kapsamı iki yolda da var | geçti |
| Sayfa hatası | 0 |

Ekran görüntüleri:
- `poisson_tekMc_gk74kapali.png`
- `poisson_tekMc_gk74acik.png`
- `poisson_weichert.png`
- `poisson_weichert_mx.png`

## 3. Bulunan mevcut hata — tarihsel modda analiz penceresi (bu dalda düzeltilmedi; onay gerekir)

### Sorun

Tarihsel katalog modunda bölge sorgusu analiz penceresini tüm katalogdan alıyor (`index.html` ~8724):
`regionWindowStart/End = historicalCache.starttime/endtime`, yani 1900-01-01 → 2026-09-14.
Seçili pencere ise ISC 1971–1997.

Bu hata main'de de var. Etkilediği yerler:
- Weichert basamaklarının son dönem sonu (`csBuild` tEnd, ~5058);
- Oran/Yoğunluk modu T'si (~3540);
- Bölge karşılaştırması T'si (~3341);
- bölge bilgi satırındaki yıllık oran (~8446) ve pencere etiketi.

### Ölçülen etki (yukarıdaki senaryo)

| Çıktı | Mevcut (pencere 1900–2026) | Doğru pencere (1971–1998) |
|---|---|---|
| Weichert son dönem | 1985 → 2026-09-14, M ≥ 4,0 | 1985 → 1998 |
| Weichert b | 0,805 | **0,947** |
| Weichert λ(≥4) | 25,2/yıl | **67,3/yıl** |
| Weichert λ(≥7), P(50 yıl) | 0,0967/yıl, %99,2 | 0,0969/yıl, %99,2 (b ve oranın etkileri burada rastlantısal olarak dengeleniyor) |
| Tek Mc T | 126,7 yıl | 27,0 yıl |
| Tek Mc λ(≥7) | 0,049/yıl | 0,228/yıl |

Yeni tamlık denetimi bu durumu kendiliğinden yakalıyor: "ilk yarıda 0 / 2200, p ≈ 0" uyarısı (`poisson_tekMc_gk74kapali.png`).

### Önerilen düzeltme

- `rebuildHistoricalView` içinde seçili pencerenin `overallStart`/`endRef` değerleri saklanır.
- Bölge sorgusunda `regionWindowStart/End` bu değerlerden alınır.

Bu, mevcut Weichert/oran çıktılarını değiştirir. Ayrı bir dalda, önce/sonra kabul testiyle ve onayınızla yapılmalı.

## 4. Literatür ile karşılaştırma

### Michael & Llenos (2026), BSSA 116(2), 786–809, doi:10.1785/0120240245

Yöntemleri:
- Dönem başına oranı Poisson olabilirliğinden L(λ|N) = e^(−λ)λ^N/N! çekiyorlar.
- b'yi N(b, σ_b)'den çekiyorlar (3σ'da kırpılmış, 0 < b < 1,5).
- Mc'yi tek yönlü normal gürültüyle örnekliyorlar (σ = 0,2, yalnız artış).
- Büyüklük hatalarını Rhoades yöntemiyle ekliyorlar: M* = M_est − βσ_m²/2, sonra N(M*, σ_m).

EQ-Live ile ilişkisi:
- EQ-Live'ın sayım + b bootstrap'ı ilk iki bileşenle aynı mantıkta.
- Mc ve büyüklük hatası bileşenleri bizde "dahil değil" olarak yazıldı. Sıradaki doğal genişleme bunlar.

İki önemli not:
- **(a)** Dönem birleştirmede süre ağırlığı öneriyorlar (Felzer 2008). Weichert'in düşük Mc'li yakın dönemlere yüksek ağırlık verdiğini belirtiyorlar (s. 806). ChatGPT koşulu 2 (değişken tamlıkta λ'yı Weichert'ten al) geçerli bir seçim, ama tek seçenek değil.
- **(b)** Oranı artçılar dahil tam katalogdan alıyorlar. GK74'ün b'yi düşürdüğünü (Llenos & Michael 2020) ve Poisson varsayımının her iki seçenekte de yüksek olasılıklarda tehlikeyi abartabileceğini belirtiyorlar (s. 788, 807).

Buna göre GK74 uyarısının metni "kapalı = yanlış" değil, "iki seçeneğin de yanlılığı var" biçiminde yumuşatılabilir. Bu bir metin kararıdır; onayınıza bırakıldı.

### Dutilleul, Genest & Peng (2024), GJI 236, 1601–1608, doi:10.1093/gji/ggae003

ETAS parametreleri için parametrik bootstrap: dar pencerelerde asimptotik (Hessian) aralıklar yanıltıcı olabiliyor, bootstrap güvenilir alternatif. Model farklı (ETAS, G–R değil). Yöntem gerekçesi ve kapsama denetimi yaklaşımı için atıf olarak uygun.

Not: ChatGPT notundaki "Holschneider ve diğerleri" yanlış. PDF'teki yazarlar Dutilleul, Genest & Peng.

### van der Elst (2021), JGR 126, e2020JB021027, doi:10.1029/2020JB021027

b-positive, ardışık olayların pozitif büyüklük farklarını kullanır ve değişken tamlığa dayanıklıdır. Michael & Llenos b'yi bununla da hesaplıyor. EQ-Live'da b için bağımsız bir çapraz denetim olarak eklenebilir (öneri, kapsam dışı).

## 5. Kapsam ve sınırlar

- Poisson (zamandan bağımsız) varsayımı; artçı kümelenmesi ihlal eder.
- Değerler bölge bütünü içindir; nokta tehlikesi, yer sarsıntısı ya da deprem tahmini değildir.
- Tek Mc yolu kesilmesizdir; büyük M'de oranı abartabilir. Panelde ekstrapolasyon uyarısı var.
- Tarihsel modda T, §3'teki hata düzeltilene kadar seçili pencereyi değil, tüm kataloğu kullanır.
