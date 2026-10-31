# a(t) paneli — pencere olay hızı (2026-10-31)

Dal: `a-zaman-paneli`, `main` 89cacdb'den açıldı. `main`'e birleştirilmedi.

## 1. Tanım

Panel, b(t)'nin hemen altında yer alır ve b(t) ile aynı pencereleri kullanır: n = 100 olay, aynı adım, aynı zaman damgası.

Öncel & Wilson (2007, GJI 169, s. 262, Eş. 3):

```
N = n/T = 10^a      →      a = log₁₀(n/T)
```

- n: pencerenin olay sayısı (M ≥ Mc).
- T: pencerenin ilk ile son olayı arasındaki süre (yıl).
- Bu a, **Mc'deki yıllık olay hızıdır**, yani log₁₀ λ(≥Mc).
- G–R bağıntısının M = 0'daki kesişimi değildir.
- Bütün katalog için hesaplanan G–R a değeriyle doğrudan karşılaştırılmaz, çünkü o değer seçilen döneme ve Mc'ye bağlıdır.

**%95 aralık:** Poisson sürecinde n olay arasındaki n−1 bekleme süresinin toplamı T ~ Gamma(n−1, λ) dağılır. Buradan:

```
λ ∈ [χ²₀,₀₂₅(2(n−1)), χ²₀,₉₇₅(2(n−1))] / (2T)
```

χ² nicelikleri Wilson–Hilferty (1931) yaklaşımıyla hesaplanır; göreli hata < 5e−4. Nokta değeri yayındaki tanıma uyar ve n/T'dir. n = 100'de bu, (n−1)/T'den 0,0044 log birimi yüksektir.

**G–R kesişimi a_GR = a + b·Mc:** Yalnızca nokta açıklamasında verilir. Ayrı bir eğri olarak çizilmez, çünkü sabit n'de yapısal olarak b'ye bağlıdır (§3, test 4). Öncel & Wilson (2007) Şekil 10'daki a değerleri (7,32; 7,09; 7,94) sayıya dayalı kesişimlerdir: log₁₀ n + b·Mc. Örneğin log₁₀ 170 + 1,75 × 2,9 = 7,31.

**Tamlık basamakları etkinken:**
- Her pencerenin olay eşikleri karşılaştırılır.
- Mc'si karışık olan pencere (bir basamak geçişini içeren) çizilmez; eksende turuncu çentikle işaretlenir.
- Çizgi her Mc segmentinde kesilir ve segment Mc ile etiketlenir.
- Farklı Mc segmentlerinin a düzeyleri karşılaştırılamaz.

**b–a korelasyonu:**
- Yalnızca örtüşmeyen pencerelerle (her ⌈n/adım⌉'ıncı pencere) Pearson r ve p (Fisher z) verilir.
- Tamlık basamaklarında korelasyon yalnızca aynı Mc segmenti içinde hesaplanır.
- Tüm örtüşen pencerelerin r'si bilgi olarak gösterilir, ama p verilmez (§3, test 5).

**Metinde yazan uyarılar:**
- GK74 kapalıysa artçı dizileri kısa süreli hız tepeleri olarak görünür.
- Tamlık zamanla değişiyorsa b–a korelasyonu yapay olabilir.
- a(t)'deki değişim tek başına deprem tahmini ya da öncü kanıtı değildir.

## 2. Değişiklik

- `index.html`'de 96 satır değişti.
- Yeni fonksiyonlar: `aWinFields`, `aChi2Q`, `aWinValue`, `aPearson`, `aSeriesFrom`, `renderAvalueTS`.
- Yeni panel: `#aTsBox`.
- `csBvalueTimeSeries` serisine pencere sınırları ve Mc aralığı eklendi (`w0`, `w1`, `mcLo`, `mcHi`; yeni alan adları). Mevcut `t0/t1` ve b hesapları değişmedi.
- `scripts/test_fit_range.js`: yeni yardımcı fonksiyon, `csBvalueTimeSeries`'in yanında kesilecekler listesine eklendi.

## 3. Birim testleri (`scripts/test_a_window.js`): 10/10

| Denetim | Sonuç |
|---|---|
| 1. χ² nicelikleri (n = 20–200) | en büyük göreli hata 4,6e−4 |
| 2. Sabit hız (λ = 20/yıl; 2387 örtüşmeyen pencere): a − log₁₀λ | 0,0075 (beklenen 0,0044) |
| 2. Aynı deney: %95 kapsama | %95,3 (± 0,9) |
| 3. Hızın iki katına çıkması | a sıçraması 0,276 (beklenen 0,301) |
| 4. Sabit hız ve sabit b'de r(b, a_GR) | 0,99: yapısal bağ |
| 4. Aynı deneyde r(b, a) | 0,00 |
| 5. H0 altında p < 0,05 oranı: örtüşmeyen pencerelerle | %2,3 |
| 5. Aynı, örtüşen pencereler bağımsızmış gibi sayılırsa | %46: sahte anlamlılık |
| 6. Karışık Mc penceresinin işaretlenmesi | geçti |

Diğer birim testleri: 15/15 geçti (`test_fit_range.js` 37/37).

## 4. Kabul testi (`kabul_a.js`, önce = main 89cacdb): 17/17

| Senaryo | Pencere | r(b, a), örtüşmeyen | a aralığı |
|---|---|---|---|
| Türkiye, ISC 1971–1997, tek Mc (3,7) | 211 | 0,79 (22 pencere, p = 3e−6) | 1,34–3,83 |
| Aynı bölge, basamaklar 1971 M ≥ 5,0 / 1990 M ≥ 3,9 | 74 (10 karışık, çizilmedi) | 0,65 (8 pencere, p = 0,083) | 0,74–3,14 |
| Marmara, EMSC 1998–2026, tek Mc | 124 | −0,05 (13 pencere, p = 0,86) | 1,36–3,76 |

- b(t) grafiği, b(t) metni ve G–R metni üç senaryoda da önce = sonra.
- a(t) değerleri bağımsız yeniden hesapla aynı (fark ≤ 4e−16).
- Sayfa hatası 0.

**Yorum notları:**
- **Türkiye 1971–1997 tek Mc:** Güçlü pozitif korelasyon (0,79) büyük olasılıkla tamlıktan kaynaklanıyor. Mc = 3,7 dönemin başında tam değil; ağ geliştikçe hem kaydedilen hız hem b birlikte artar. Basamaklı seride korelasyon zayıflıyor ve anlamlı değil (8 pencere). Bu nedenle panele "yapay korelasyon" uyarısı eklendi.
- **Marmara:** 1999 İzmit artçı dizisi belirgin bir hız tepesi olarak görünüyor (a = 3,76; 18 Ağustos 1999; GK74 kapalı).
- Öncel & Wilson (2007) b ile log N korelasyonunu örtüşen 8 noktalık pencerelerde raporlamıştı (r = −0,62 ve +0,85, s. 263). Burada ise p yalnızca örtüşmeyen pencerelerle veriliyor; test 5 bunun gerekçesi.

Ekran görüntüleri:
- `a_tekMc.png`
- `a_basamak.png`
- `a_marmara.png`
