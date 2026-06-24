# EQ-LiveTürkiye · Metodoloji Bölüm 12–13
**Öncel (2026) — Adaptif b-Değeri ve T_L Asperite Modeli**  
Tarih: 2026-06-25 | Yazar: A. O. Öncel

---

## Bölüm 12: Katalog Kalibrasyonu ve Mc Paradoksu

### 12.1 Büyüklük Dönüşümü: Scordilis (2006) Kuadratik Formülü

Türkiye sismik kataloğu, farklı dönemlerde farklı büyüklük ölçekleri kullanan ağların (ISC 1900–1997, EMSC 1998–2026) birleşiminden oluşmaktadır. b-değeri hesabında enerji tutarlılığı zorunlu olduğundan, tüm ML ve mb büyüklükleri Moment Magnitüdü (Mw) ölçeğine dönüştürülmüştür.

Küçük büyüklükler (ML ≤ 3.5) için Scordilis (2006) kuadratik formu uygulanmıştır:

```
Mw = 0.0376 × ML² + 0.646 × ML − 0.269
```

Bu formülün kritik kalibrasyon noktası:

```
ML = 3.0  →  Mw = 0.0376 × 9 + 0.646 × 3 − 0.269 ≈ 2.007
```

Görünürde paradoksal olan bu ilişki — ML 3.0'ın Mw 2.0'a karşılık gelmesi — aslında küçük depremlerde sismik momentin (M₀) yerel büyüklüğe göre daha yavaş arttığını yansıtan fiziksel bir gerçekliktir. Mw ölçeği, kaynak fiziğini (fay alanı × ortalama kayma × rijidite) doğrudan temsil ettiğinden, ML→Mw dönüşümünde enerji kaybı değil, ölçek farkının düzeltilmesi söz konusudur.

**Sonuç:** ML = 3.0 eşiği ile Mw = 2.0 eşiği sismolojik olarak tam eşdeğerdir; aynı 37.709 artçısız ana şok kümesini temsil eder.

### 12.2 Mc Paradoksu: Neden Mw 2.5 Değil, Mw 2.0?

Aki (1965) MLE b-değeri tahmini istatistiksel güvenilirlik için her grid hücresinde N ≥ 50 deprem zorunlu kılar:

```
b = log₁₀(e) / (mean(Mw) − Mc_eff)
Mc_eff = Mc − 0.05   [Utsu 1966 binom düzeltmesi]
```

Tamamlılık büyüklüğü (Mc) seçiminin model üzerindeki etkisi sistematik olarak test edilmiştir:

| Mc (Mw) | Hesaplanan Grid Noktası | Durum |
|---------|------------------------|-------|
| 3.0 (Mw) | 17 nokta | BAŞARISIZ — Mw ölçeğinde çok büyük eşik |
| 2.5 (Mw) | 246 nokta | BAŞARISIZ — ISC veri boşlukları N<50 |
| **2.0 (Mw)** | **2451 nokta** | **BAŞARILI — optimal kalibrasyon** |

**Paradoksun mekanizması:**  
ISC kataloğunda (1900–1997) tamamlılık eşiği ML ≥ 4.5 (1960 sonrası) ve ML ≥ 5.5 (1960 öncesi) düzeyindedir. Mw ≥ 2.5 filtresi uygulandığında, bu dönemin grid hücrelerinde N < 50 kısıtı aşılamaz; b-değeri hesaplamak için yeterli veri bulunmaz.

**Çözüm:**  
Mw = 2.0 eşiği, EMSC (1998–2026) modern ağının sağladığı yüksek veri yoğunluğuyla N ≥ 50 kriterini karşılar. ISC döneminin katkısı ise sismisite yoğunluk haritasında (R zonlarının belirlenmesinde) kullanılır; b-değeri hesabından değil, adaptif yarıçap seçiminden sorumludur.

### 12.3 Kumburgaz Anomalisinin Kalibrasyona Bağlılığı

ML ölçeğinde Mc = 3.0 (ML) ile yapılan hesaplamada Marmara'daki Kumburgaz segmenti (40.5°N, 28.8°E) için b = 0.863 elde edilmekteydi. Mw ölçeğine geçilip Mc = 2.0 (Mw) uygulandığında aynı segmentte b = 0.618 saptanmıştır:

| Ölçek | Mc | Kumburgaz b | Yorum |
|-------|-----|-------------|-------|
| ML | 3.0 (ML) | 0.863 | Stres sinyali maskelenmiş |
| **Mw** | **2.0 (Mw)** | **0.618** | Gerçek kilitlenme imzası |

%28'lik bu fark rastlantı değildir. Mw kalibrasyonu, ML ölçeğinin aynı enerji eşiğinde daha az olay sayması nedeniyle oluşan istatistiksel önyargıyı giderir ve Kumburgaz'daki gerçek stres kilitlenmesini (asperite imzasını) açığa çıkarır.

### 12.4 Epistemik Dürüstlük: Boşlukların Sismometrik Anlamı

Haritadaki beyaz/boş alanlar eksiklik değil, **doğruluk filtresidir.**

| Boşluk Tipi | Kaynak | Sismolojik Yorum |
|-------------|--------|-----------------|
| Sismik sessizlik | Tamamen kilitli segment — mikrosismisite üretmiyor | Yüksek stres birikimi / asperite adayı |
| Ağ hassasiyeti | Yerel istasyon kapsama dışı, yüksek Mc | İstasyon kurulum rehberi |
| İstatistiksel eşik | N < 50 (Aki 1965 kriteri karşılanmıyor) | O noktada b güvenilmez → boş bırakılır |

Bu yaklaşım SHARP çerçevesindeki Epistemik Şeffaflık ilkesiyle tam uyumludur: model, yalnızca verinin sağlam konuştuğu alanlarda sonuç üretir.

---

## Bölüm 13: Retrospektif Validasyon ve Asperite Sabitliği

### 13.1 Hipotez: T_L Minima = Kalıcı Nucleation Zonu

Öncel ve Wyss (2000, 2001), T_L (Yerel Yineleme Süresi) minimalarının büyük depremler için çekirdeklenme (nucleation) bölgelerini temsil ettiğini göstermiştir:

```
T_L = 10^(b × M_target − a_ann)   [yıl]
a_ann = log₁₀(N/ΔT) + b × Mc      [yıllık normalize G-R a-değeri]
```

Schwartz ve Coppersmith (1984) karakteristik deprem modelinde asperiteler, fay üzerindeki kalıcı yapısal pürüzlerdir ve her deprem döngüsünde aynı nucleation noktasından kırılır. Bu iki önerme birleştirildiğinde test edilebilir bir hipotez ortaya çıkar:

> *Modern mikrosismisite tabanlı T_L minima haritaları, tarihsel büyük depremlerin nucleation bölgelerini tutarlı biçimde işaret etmelidir.*

### 13.2 Yöntem: İki Aşamalı Mekânsal Eşleştirme

Her tarihsel epicenter için ilgili T_L büyüklük bandındaki en yakın T_L minimumu aranmıştır:

```
Magnitude bantları (Triple-Target):
  Mw 6.5–7.0  →  T_L(Mw 6.8)
  Mw 7.0–7.6  →  T_L(Mw 7.4)
  Mw 7.6+     →  T_L(Mw 7.8)

Arama algoritması:
  1. Epicenter R ≤ 50 km içindeki en düşük T_L noktası (coğrafi yakın + istatistiksel minimum)
  2. Bulunamazsa R ≤ 150 km içindeki en düşük T_L (fallback)
```

**Veri kümeleri:**
- Modern validasyon: EMSC 1998–2026, Mw ≥ 6.5, Türkiye (n = 6)
- Tarihsel test: EPICA v1.1, Mw ≥ 6.5, Türkiye bölgesi (n = 59)

### 13.3 Sonuçlar

| Küme | n | R < 50 km | Ort. Ofset | Medyan |
|------|---|-----------|-----------|--------|
| Modern EMSC (1998–2026) | 6 | **%100** | 33 km | 48 km |
| Tarihsel EPICA | 59 | **%96** | 43 km | 45 km |

**Kritik eşleşmeler:**

| Olay | Mw | En Yakın T_L Minima | Ofset | Anlam |
|------|----|--------------------|----|-------|
| 1509 İstanbul | 7.2 | 40.6°N 28.9°E b=0.685 | 48 km | Kumburgaz asperitesi yakını |
| 1855 Proussa (Bursa) | 7.0 | **40.5°N 28.8°E b=0.618** | 42 km | Kumburgaz minimumu |
| 1845 Manisa | 6.7 | 38.6°N 27.6°E | **9 km** | En yakın eşleşme |
| 1493 Kos | 6.9 | 36.6°N 27.0°E | 21 km | Ege asperitesi |
| 2023 Kahramanmaraş | 7.8 | 37.2°N 36.9°E b=0.726 | **16 km** | DAFZ doğrulaması |
| 2011 Van | 7.4 | 38.6°N 43.3°E b=0.605 | 23 km | Doğu Anadolu |

### 13.4 Sismolojik Yorum

**%96 oranında R < 50 km uyumu**, tarihsel epicenter belirsizliği (Ambraseys 2002, Parsons 2004: ±50 km) ile tam örtüşmektedir. Bu sonucun üç kritik anlamı vardır:

**1. Asperite Sabitliği Doğrulandı**  
T_L minimalarının tarihsel kırılma noktalarıyla örtüşmesi, Schwartz ve Coppersmith (1984) karakteristik deprem modelini ampirik olarak destekler. Kumburgaz (b=0.618), 1509 ve 1855 depremlerinde de aktif olan bir asperite olarak, son 500+ yıldır Marmara'nın "ana stres düğümü" vasfını korumaktadır.

**2. Tarihsel Epicenter Düzeltmesi Mümkün**  
Modern b-değeri haritaları, tarihsel raporların (yoğunluk haritaları, MMI) veremediği koordinat hassasiyetini sağlamak için "modern mercek" olarak kullanılabilir. Ortalama 43 km'lik ofset, tarihsel yer belirsizliği (±50 km) sınırı içinde kaldığından, T_L minimına yakınsatma istatistiksel olarak anlamlı bir düzeltme sağlar.

**3. Metodolojik Özgün Katkı**  
Modern mikrosismisite tabanlı asperite haritalarının tarihsel epicenter belirsizliğini azaltmak amacıyla kullanılması literatürde yeni bir yaklaşımdır. Bu çalışma, Öncel ve Wyss (2000, 2001) metodolojisine zamansal bir validasyon boyutu kazandırmaktadır.

### 13.5 Kumburgaz Asperitesi: 517 Yıllık Kalıcılık

Marmara Denizi altındaki Kumburgaz segmenti (40.5°N, 28.8°E) bu çalışmada üç bağımsız kanıtla öne çıkmıştır:

| Kanıt | Değer | Yöntem |
|-------|-------|--------|
| Güncel b-değeri | **0.618** | Adaptif MLE, Mc=2.0(Mw), N=62 |
| T_L (Mw 7.4) | 4.734 yıl | Marmara minimumu |
| 1509 İstanbul ofseti | 48 km | EPICA retrospektif eşleşme |
| 1855 Bursa ofseti | 42 km | EPICA retrospektif eşleşme |

Bu segment, Marmara altında biriken 3.7 metrelik sismik borcun (Ergintav vd. 2014) en olası tahsilat noktasıdır. Ergintav ve diğ. (2014) GPS verilerinde Kumburgaz bölgesini "yüksek kilitlenme" (high locking) zonu olarak saptamıştır; mikrosismisite tabanlı b=0.618 bulgusu bu jeodezik tespiti bağımsız ve tamamlayıcı biçimde desteklemektedir.

---

## Bölüm 14: Raw Katalog ve Declustered Katalog — Tanım ve Kullanım Amacı

### 14.1 Tanımlar

**Raw Catalogue (Ham Katalog):**  
Sismik ağlardan (KOERI, AFAD, ISC, EMSC) geldiği haliyle, hiçbir ayıklama yapılmamış veri setidir. Ana şoklar (mainshocks), öncü şoklar (foreshocks) ve artçı şoklar (aftershocks) bir arada bulunur. Büyük bir deprem öncesindeki sismik aktivite artışlarını, çekirdeklenme (nucleation) süreçlerini ve sismik yığılmaları (clustering) analiz etmek için kullanılır. Örneğin, 1999 İzmit depremi öncesindeki 2.5 yıllık aktivite artışı ham katalog üzerinden incelenmiştir.

**Declustered Catalogue (Arındırılmış Katalog / Main Shock Catalog):**  
Ham katalogdaki birbirine bağımlı depremlerin (öncü ve artçı şokların) istatistiksel algoritmalarla temizlenmesiyle elde edilen veri setidir. İdeal olarak yalnızca birbirinden bağımsız ana şokları (independent events) barındırır. Asperiteleri ve sismotektonik bölgeleri karakterize etmek için kullanılır.

### 14.2 Declustering'in b-Değerine Etkisi

Katalog declustered edilmezse, artçı şok yığılmaları o bölgedeki b-değerini (stres eğimi) yapay olarak yükseltir veya a-değerini (üretkenlik) saptırır. Artçı şoklar düşük-b bir küme oluştururken, bu yığılmalar istatistiksel ortalamalarda b'yi yüksek gösterir — gerçek asperite sinyalini maskeler.

Kumburgaz segmenti için saptanan b = 0.618 değeri, GK74 declustered Main Shock Catalog kullanılarak elde edilmiştir. Raw katalogda aynı noktada b değeri yapay olarak daha yüksek hesaplanmaktadır; gerçek kilitlenme imzası ancak bağımsız olaylardan oluşan temiz katalogda görünür hale gelmektedir.

### 14.3 Declustering'in Bedeli: Veri Kaybı ve Haritadaki Boşluklar

Gardner-Knopoff (1974) declustering algoritmasının N≥50 Aki (1965) kriteri ile birleşimi, haritada sistematik boşluklar üretir:

| Bölge | Raw katalog | GK74 sonrası | Kayıp |
|-------|------------|--------------|-------|
| DAFZ (2023 Kahramanmaraş artçıları) | ~50.000+ | ~200–300 | %99+ |
| İzmit 1999 bölgesi | ~10.000+ | ~50–100 | %99+ |
| Kuzey Anadolu orta segmentleri | Zaten az | N < 50 | b hesaplanamaz |

Bu boşluklar iki farklı anlama gelebilir:

- **Sismik sessizlik:** Segment tamamen kilitli, mikrosismisite üretmiyor → asperite adayı (bilgi taşır)
- **Veri yetersizliği:** İstasyon kapsama sorunu veya GK74 kaybı → b hesaplanamaz (boşluk epistemik)

### 14.4 Platform Tasarım İlkesi

EQ-LiveTürkiye'de bu ayrım şöyle uygulanmaktadır:

| Katman | Katalog türü | Amaç |
|--------|-------------|-------|
| Canlı deprem noktaları | Raw Catalog (EMSC/AFAD anlık) | Son aktiviteyi göster |
| b-Adaptif grid | Main Shock Catalog (GK74 declustered) | Uzun dönem stres birikimi |
| T_L Asperite (T_L) | Main Shock Catalog | Yineleme süresi hesabı |
| Tarihsel katman | EPICA (tarihsel ham) | Tarihsel büyük olaylar |

**Temel ilke:** Raw = sismik fırtınanın tüm bilgisini taşır. Declustered (Main Shock Catalog) = fayın üzerindeki uzun dönemli stres birikimini ve asperite konumlarını gösteren temiz aynadır. Bu ayrım, T_L anomali haritalarının fiziksel rasyonalitesinin temel taşıdır. Declustered katalog kullanmak, Marmara altındaki 3.7 metrelik sismik borcun tahsil edileceği gerçek "ana saatleri" (mainshock recurrence) hesaplamaya olanak tanımaktadır.

---

## Bölüm 15: Δb İndeksi ve Sismik Karakterin Saflığı

### 15.1 b(main) ≈ b(all): "Ana Deprem Karakterli" Bölgelerin Sismometrik Anlamı

Türkiye genelinde hesaplanan Δb = b(main) - b(all) dağılımı:

| Kategori | Nokta | % | Fiziksel Anlam |
|----------|-------|---|----------------|
| Δb < -0.10 (artçı baskısı) | 576 | %9 | b(all) > b(main) — artçılar b'yi şişiriyordu, declustering zorunlu |
| Δb ≈ 0 (ana deprem karakterli) | 4671 | **%78** | b(main) ≈ b(all) — Poissonian arka plan sismisitesi baskın |
| Δb > +0.10 (stres artçısı) | 734 | %12 | Artçılar düşük-b taşıyor — yüksek stres artçı dizisi |

%78 oranında b(main) ≈ b(all) çıkması şu anlama gelir: Türkiye'nin büyük çoğunluğunda mevcut sismisitenin büyük bir ana şokun artçısı değil, bağımsız arka plan olaylarından (background seismicity) oluştuğu anlamına gelir. Bu, yakın tarihte artçı dizisi yaratacak büyüklükte bir enerji boşalımının gerçekleşmediğinin matematiksel mühürüdür.

### 15.2 İç Anadolu'nun Δb Profili: Stabil Poissonian Bölge

İç Anadolu'da b(main) ≈ b(all) çıkması şu zinciri kanıtlar:

1. Bölgede artçı dizisi yaratacak büyüklükte son dönem ana şok yok
2. Mevcut küçük depremler birbirinden bağımsız (Poisson süreci)
3. Declustering işlemi bu bölgede veri kaybı yaratmaz — zaten temizlenecek artçı gürültüsü yok
4. "Ana deprem karakterli" tanımı büyük deprem varlığını değil, küçük olayların bile bağımsız davranmasını ifade eder

Bu bölgeler "Sismik Karakterin Saflığı" açısından kendi içinde homojen alanlardır.

### 15.3 Kumburgaz Asperitesinde Beklenen Δb Profili

Kumburgaz (40.5°N, 28.8°E, b_main=0.618) için Δb analizinden beklenti:

- b(all): Mikro-çatırdamalar ve yığılmalar ham katalogda b'yi yukarı çekebilir → b(all) > b(main) beklenir
- Δb < 0 → artçı baskısı kategorisi → declustering'in Kumburgaz'daki gerçek stres imzasını (b=0.618) açığa çıkardığının kanıtı

Bu nokta için Δb popup değeri platforma tıklanarak doğrulanabilir.

---

## Bölüm 16: Krip vs. Kilitlenme — Marmara'nın Dinamik Dengesi

### 16.1 Tartışmanın Sismolojik Çerçevesi

Marmara Denizi altındaki fay segmentlerinin kilitlenme durumu literatürde aktif tartışma konusudur. İki karşıt görüş:

**Krip (Aseismik Kayma) Görüşü:**
- Ergintav vd. (2014): GPS verileri Orta Marmara segmentinin kısmi krip yapıyor olabileceğini öne sürmektedir
- Batı Marmara'da saptanan M~2.8 "repeater" depremler kısmi kripin sismik kanıtıdır
- İsmetpaşa segmenti (KAFZ): Kilitli ve krip yapan alanların aynı fay üzerinde bir arada bulunabileceğinin klasik örneği

**Kilitlenme (Locking) Görüşü:**
- Sakic vd. (2016): Deniz tabanı akustik ölçümleri Marmara'da belirgin krip saptayamadığını raporlamıştır
- Meghraoui (2021): Moment hız açığı hâlâ Mw 7.4–7.5 üretecek kapasitede
- Bu çalışma (Öncel 2026): b=0.618 (Kumburgaz) tam kilitlenme imzası — kripin b değerini bu kadar düşüremeyeceği argümanı

### 16.2 Mikrosismisite Tabanlı Ayrım: b-Değeri Kripi Maskeler mi?

Krip yapan bir segment mikrosismisite üretir (repeaterlar) ama b-değeri üzerindeki etkisi farklıdır:

| Segment tipi | b-değeri beklentisi | Mikrosismisite | T_L |
|-------------|--------------------|-----------------|----|
| Tam kilitli (locked) | Düşük (b < 0.7) | Az — sessizlik | Uzun |
| Kısmi krip | Orta (b ~ 0.8–1.0) | Orta — repeaterlar | Orta |
| Tam krip | Yüksek (b > 1.2) | Yok veya çok az | Anlamsız |

Kumburgaz'daki b=0.618, kısmi krip senaryosuyla dahi açıklanamaz — bu değer yalnızca **tam kilitlenme** ile tutarlıdır.

### 16.3 Sismik Borç ve Krip Paradoksu

1766'dan beri biriken ~3.7 metrelik sismik borç (Ergintav vd. 2014) hesabı:

```
Kayma hızı (GPS): ~20 mm/yıl (Marmara segmenti)
Geçen süre: 260 yıl (1766–2026)
Beklenen birikim: 0.020 × 260 = 5.2 m
Gözlenen sismisite ile açıklanan: ~1.5 m
Açıklanamayan borç: ~3.7 m
```

Eğer Marmara'da yaygın krip olsaydı bu borcun önemli kısmı sessizce ödenmiş olurdu. Sakic vd. (2016)'nın krip saptayamaması ve Kumburgaz'daki b=0.618 imzası birlikte değerlendirildiğinde, 3.7 metrelik borcun Kumburgaz ve Adalar asperitelerinde depolandığı ve tek seferlik bir Mw ≥ 7.4 kırılmasıyla tahsil edileceği hipotezi fiziksel tutarlılığını korumaktadır.

### 16.4 Bu Çalışmanın Katkısı

Mevcut literatürde GPS (jeodezi) ve repeater sismisitesi iki ayrı veri seti olarak değerlendirilmekteydi. Bu çalışma, adaptif b-değeri haritalaması ve T_L anomali analizi yoluyla üçüncü bir bağımsız kanıt zinciri sunmaktadır:

- b=0.618 (mikrosismisite) → tam kilitlenme
- T_L=4734 yıl (Mw7.4) → aşırı vade anomalisi
- %96 retrospektif eşleşme (EPICA) → asperite kalıcılığı
- Ergintav (2014) GPS → yüksek kilitlenme zonu

Dört bağımsız yöntemin aynı coğrafi noktada (Kumburgaz, 40.5°N 28.8°E) örtüşmesi, krip hipotezini bu segment için olası dışlamaktadır.

---

## Referanslar

- Aki, K. (1965). Maximum likelihood estimate of b in the formula log N = a − bM. *Bull. Earthq. Res. Inst.*, 43, 237–239.
- Ambraseys, N. N. (2002). The seismic activity of the Marmara Sea region over the last 2000 years. *Bull. Seismol. Soc. Am.*, 92(1), 1–18.
- Ergintav, S., et al. (2014). Istanbul's earthquake hot spots: Geodetic constraints on strain accumulation along faults in the Marmara Seismic Gap. *Geophys. Res. Lett.*, 41, 5783–5788.
- Gardner, J. K., & Knopoff, L. (1974). Is the sequence of earthquakes in Southern California, with aftershocks removed, Poissonian? *Bull. Seismol. Soc. Am.*, 64(5), 1363–1367.
- Öncel, A. O., & Wyss, M. (2000). The major asperities of the 1999 Mw 7.4 Izmit earthquake defined by the microseismicity of the two decades before it. *Geophys. J. Int.*, 143(2), 501–506.
- Öncel, A. O., & Wyss, M. (2001). The major asperities of the 1999 Mw 7.1 Düzce, Turkey, earthquake defined by the microseismicity of the decade before it. *Geophys. J. Int.*, 147(2), 499–510.
- Parsons, T. (2004). Recalculated probability of M ≥ 7 earthquakes beneath the Sea of Marmara, Turkey. *J. Geophys. Res.*, 109, B05304.
- Scordilis, E. M. (2006). Empirical global relations converting Ms and mb to moment magnitude. *J. Seismol.*, 10(2), 225–236.
- Schwartz, D. P., & Coppersmith, K. J. (1984). Fault behavior and characteristic earthquakes: Examples from the Wasatch and San Andreas fault zones. *J. Geophys. Res.*, 89(B7), 5681–5698.
- Utsu, T. (1966). A statistical significance test of the difference in b-value between two earthquake groups. *J. Phys. Earth*, 14(2), 37–40.
- Wiemer, S. (2001). A software package to analyze seismicity: ZMAP. *Seismol. Res. Lett.*, 72(3), 373–382.
- Meghraoui, M., et al. (2021). Earthquake hazard in the Marmara region. *Comptes Rendus Géoscience*, 353(S1), 1–24.
- Sakic, P., et al. (2016). No significant shallow seismic slip across the North Anatolian Fault zone in the Sea of Marmara. *Geophys. Res. Lett.*, 43(7), 3148–3155.
