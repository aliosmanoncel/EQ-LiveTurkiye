# a(t) paneli — pencere olay hızı (2026-10-31, güncelleme 3)

Dal: `a-zaman-paneli`, `main` 89cacdb'den açıldı. `main`'e birleştirilmedi; bilimsel inceleme bekliyor.

**Güncelleme 3'te eklenenler** (ChatGPT incelemesinin üç noktası):
- **Aralık ifadesi:** "Kesin %95" yalnızca Poisson varsayımı altında geçerli. GK74 açıkken de kalan olayların bağımsız olduğu garanti edilmiyor (§1.2).
- **Korelasyon:** p panelde "keşifsel" olarak etiketlendi. Örtüşmeyen pencerelerin gecikme-1 öz-ilişkisi ölçüldü ve Bartlett etkin örneklem düzeltmesi hesaplandı (§4.1). Bu yalnızca metin değişikliği; hesaplar aynı.
- **Büyüklük ölçeği:** ileriki çalışmaya bırakıldı (§5).

**Güncelleme 2'de eklenenler:**
- %95 aralık yönteminin türetimi ve varsayımı (§1.2).
- Sentetik testlerin tekrar sayıları ve kapsama oranlarının kendi aralıkları (§3).
- Kümelenmenin aralık kapsamasına etkisi (test 7).
- Marmara'da GK74 açık/kapalı karşılaştırması (§4).
- a–b ilişkisini karıştırabilecek etkenler tablosu (§5).
- Panelin aralık açıklamasına "bağımsız olay varsayımı — artçı kümelenmesinde dar kalır" eklendi.

## 1. Tanım ve yöntem

### 1.1 a(t)

Panel, b(t)'nin altında yer alır ve b(t) ile aynı pencereleri kullanır: n = 100 olay (M ≥ Mc), aynı adım, aynı zaman damgası.

Öncel & Wilson (2007, GJI 169, s. 262, Eş. 3):

```
N = n/T = 10^a      →      a = log₁₀(n/T)
```

- T: pencerenin ilk ile son olayı arasındaki süre (yıl).
- a, **Mc'deki yıllık olay hızıdır** (log₁₀ λ(≥Mc)); G–R bağıntısının M = 0'daki kesişimi değildir.
- Bütün katalog için hesaplanan G–R a değeriyle doğrudan karşılaştırılmaz; o değer seçilen döneme ve Mc'ye bağlıdır.

G–R kesişimi a_GR = a + b·Mc yalnızca nokta açıklamasında verilir; ayrı eğri olarak çizilmez (§3, test 4). Öncel & Wilson (2007) Şekil 10'daki a değerleri (7,32; 7,09; 7,94) sayıya dayalı kesişimlerdir: log₁₀ n + b·Mc. Örneğin log₁₀ 170 + 1,75 × 2,9 = 7,31.

### 1.2 %95 güven aralığı

**Varsayım:** Pencere içinde olaylar sabit hızlı bir Poisson süreci oluşturur; yani olaylar bağımsızdır.

**Türetim:**
1. Penceredeki n olay arasında n−1 bekleme süresi vardır. Bunlar bağımsızdır ve her biri Üstel(λ) dağılır.
2. Toplamları T ~ Gamma(n−1, λ), dolayısıyla 2λT ~ χ²(2(n−1)).
3. Buradan, Poisson varsayımı altında, λ için kesin %95 aralığı:

```
λ ∈ [ χ²₀,₀₂₅(2(n−1)) / (2T) ,  χ²₀,₉₇₅(2(n−1)) / (2T) ]
```

a için aralık bu iki sınırın log₁₀'udur. n = 100'de aralığın yarı genişliği yaklaşık ±0,087 log birimidir.

**Hesap:** χ² nicelikleri Wilson–Hilferty (1931) yaklaşımıyla hesaplanır: χ²_p(k) ≈ k·(1 − 2/(9k) + z_p·√(2/(9k)))³. n = 20–200 aralığında kesin değerlere göre en büyük göreli hata 4,6e−4'tür (test 1).

**Nokta değeri:** Yayındaki tanıma uymak için n/T kullanılır. Yansız kestirici (n−1)/T'dir; n = 100'de fark 0,0044 log birimi, aralık genişliğinin yaklaşık %5'i.

**Geçerlilik sınırı:** Artçı kümelenmesinde olaylar bağımsız değildir. Pencereden pencereye değişim Poisson'dan büyük olur ve aralık dar kalır (test 7: orta kümelenmede kapsama %78, güçlü kümelenmede %58). Panel bunu yazar. GK74 açıkken artçıların büyük kısmı çıkar ve aralık varsayıma daha yakın olur. Ancak GK74 kalan olayların bağımsız olduğunu garanti etmez (arka plan kümelenmesi, ayıklama pencerelerinin sınırları). Bu yüzden aralık hiçbir durumda koşulsuz "kesin %95" olarak sunulmaz; her zaman "Poisson varsayımı altında" anlamında okunmalıdır.

### 1.3 Diğer kurallar

- **Tamlık basamakları:** Mc'si karışık pencere (bir basamak geçişini içeren) çizilmez; eksende turuncu çentikle işaretlenir. Çizgi her Mc segmentinde kesilir ve segment Mc ile etiketlenir. Farklı Mc segmentlerinin a düzeyleri karşılaştırılamaz.
- **b–a korelasyonu:** Yalnızca örtüşmeyen pencerelerle (her ⌈n/adım⌉'ıncı) Pearson r ve iki yönlü p (Fisher z) verilir; basamaklarda yalnızca aynı Mc segmenti içinde. Tüm örtüşen pencerelerin r'si bilgi olarak gösterilir, p verilmez (test 5). p panelde **keşifsel** olarak etiketlenir: örtüşmeyen pencereler de zamanda bağımlı olabilir (§4.1).
- **Metindeki uyarılar:** GK74 kapalıysa artçı tepeleri; tamlık değişirse yapay b–a korelasyonu; tahmin ya da öncü kanıtı değildir.

## 2. Değişiklik

- `index.html`'de yaklaşık 96 satır değişti.
- Yeni fonksiyonlar: `aWinFields`, `aChi2Q`, `aWinValue`, `aPearson`, `aSeriesFrom`, `renderAvalueTS`.
- Yeni panel: `#aTsBox`.
- `csBvalueTimeSeries` serisine yeni alanlar eklendi (`w0`, `w1`, `mcLo`, `mcHi`). Mevcut `t0/t1` ve b hesapları değişmedi.
- `scripts/test_fit_range.js`: yeni yardımcı fonksiyon, kesilecekler listesine eklendi.

## 3. Birim testleri (`scripts/test_a_window.js`): 11/11

Hepsi tohumlu üreteçle yapıldı, yani tekrarlanabilir. Köşeli parantezler, kapsama oranının kendi %95 aralığıdır (binom).

| Test | Kurgu ve tekrar sayısı | Sonuç |
|---|---|---|
| 1. χ² nicelikleri | n = 20, 50, 100, 200; p = 0,025 ve 0,975; kesin değer seri ile | en büyük göreli hata 4,6e−4 |
| 2. Yanlılık ve kapsama | λ = 20/yıl, b = 1, Mc = 3, 300 yıl; **40 katalog (tohum 11), 2387 örtüşmeyen pencere** | a − log₁₀λ = 0,0075 (beklenen 0,0044); **kapsama %95,3 [%94,4–%96,1]** |
| 3. Hız değişimi | 100 yıl λ = 10, sonra 100 yıl λ = 20; 1 katalog (tohum 12), adım 10 | a sıçraması 0,276 (beklenen 0,301; tolerans 0,05) |
| 4. a_GR ile b'nin bağı | sabit hız ve sabit b; 400 yıl, 1 katalog (tohum 13), adım 10 | r(b, a_GR) = 0,99; r(b, a) = 0,00 |
| 5. Korelasyon testinin boyutu | H0: sabit hız, sabit b; **300 katalog (tohum 14)**, her biri ≈ 23 örtüşmeyen pencere | p < 0,05 oranı: örtüşmeyen %2,3; örtüşenler bağımsız sayılırsa %46 |
| 6. Karışık Mc penceresi | yapay pencereler | işaretleniyor, a_GR hesaplanmıyor |
| 7. Kümelenme | uzun dönem λ = 20/yıl, 300 yıl, **her durumda 40 katalog (tohum 15), ≈ 2380 pencere**; ana olay Poisson(μ), artçı sayısı Poisson(m), gecikme üstel (≈ 7 gün) | kapsama: m = 0 %95,1; m = 1 **%77,8**; m = 4 **%58,2** |

Diğer birim testleri: 15/15 geçti (`test_fit_range.js` 37/37).

## 4. Kabul testi (`kabul_a.js`, önce = main 89cacdb): 23/23 (p etiketinde "keşifsel" denetimi dahil)

| Senaryo | Pencere | r(b, a), örtüşmeyen | a aralığı |
|---|---|---|---|
| Türkiye, ISC 1971–1997, tek Mc (3,7) | 211 | 0,79 (22 pencere, p = 3e−6) | 1,34–3,83 |
| Aynı bölge, basamaklar 1971 M ≥ 5,0 / 1990 M ≥ 3,9 | 74 (10 karışık, çizilmedi) | 0,65 (8 pencere, p = 0,083) | 0,74–3,14 |
| Marmara, EMSC 1998–2026, tek Mc, GK74 kapalı | 124 | −0,05 (13 pencere, p = 0,86) | 1,36–3,76 |
| Marmara, aynı, **GK74 açık** | 53 | 0,71 (6 pencere, p = 0,13) | 1,18–1,50 |

- Dört senaryoda b(t) grafiği, b(t) metni ve G–R metni önce = sonra.
- a(t) değerleri bağımsız yeniden hesapla aynı (fark ≤ 4e−16).
- Sayfa hatası 0.

Ekran görüntüleri:
- `a_tekMc.png`
- `a_basamak.png`
- `a_marmara.png`
- `a_marmara_gk74.png`

### 4.1 Örtüşmeyen pencerelerin bağımsızlığı

ChatGPT'nin ikinci noktasını denetlemek için, aynı Mc segmentindeki ardışık örtüşmeyen pencerelerin a ve b serilerinde gecikme-1 öz-ilişkisi (ρ) ölçüldü (`kabul_a.js`, kabul_sonuc.json).

Etkin örneklem: n_eff = n(1 − ρ_a·ρ_b)/(1 + ρ_a·ρ_b) (Bartlett 1935; iki öz-ilişkili seri arasındaki korelasyon için). Düzeltilmiş p, Fisher z ile n_eff kullanılarak hesaplandı.

| Senaryo | n | ρ_a | ρ_b | r(b, a) | panel p (bağımsızlık varsayımı) | n_eff | düzeltilmiş p |
|---|---|---|---|---|---|---|---|
| Türkiye 1971–1997, tek Mc | 22 | 0,73 | 0,80 | 0,79 | 3e−6 | 5,8 | **≈ 0,07** |
| Aynı, tamlık basamaklı | 8 | 0,60 | 0,62 | 0,65 | 0,083 | 3,7 | test edilemez (n_eff < 5) |
| Marmara, GK74 kapalı | 13 | 0,51 | 0,62 | −0,05 | 0,86 | 6,8 | ≈ 0,92 |
| Marmara, GK74 açık | 6 | 0,84 | 0,44 | 0,71 | 0,13 | 2,8 | test edilemez |

**Sonuç:** Örtüşmeyen pencereler de belirgin biçimde öz-ilişkili; ρ = 0,44–0,84, yani yavaş değişen eğilimler var. Bağımsızlık varsayımıyla hesaplanan p iyimser kalıyor. Türkiye 1971–1997'deki p = 3e−6, düzeltmeyle ≈ 0,07'ye çıkıyor. Bu, §6'daki "tamlık kaynaklı yapay korelasyon" yorumuyla da tutarlı: iki seri birlikte bir eğilim izliyor.

Paneldeki p bu yüzden keşifseldir.

**Öneri (ayrı iş):** Panelde n_eff'i ve düzeltilmiş p'yi doğrudan göstermek ya da eğilimi çıkarılmış (birinci fark) serilerde korelasyon vermek. Bu bir hesap değişikliği olduğundan bu dala katılmadı.

## 5. a–b ilişkisini karıştırabilecek etkenler

| Etken | Etkisi | Panelde nasıl ele alınıyor |
|---|---|---|
| Aynı olaylardan hesaplama | a ve b aynı 100 olaydan gelir. Sabit n'de G–R kesişimi a_GR yapısal olarak b'ye bağlıdır (test 4). | Çizilen a = log₁₀(n/T), b'den yapısal olarak bağımsız (test 4: r = 0,00); a_GR yalnızca açıklamada |
| Örtüşen pencereler | Ardışık pencereler 90 olay paylaşır; bağımsız sayılırsa sahte anlamlılık çıkar (test 5: %46) | p yalnızca örtüşmeyen pencerelerle |
| Tamlık değişimi | Mc'nin altında kalan dönemde kaydedilen hız ve b birlikte düşer; yapay pozitif korelasyon oluşur | Uyarı metni; tamlık basamaklarıyla segmentlere bölme; Türkiye 1971–1997'de r 0,79 → 0,65 (anlamlı değil) |
| Mc basamakları | Farklı eşiklerin hızları karşılaştırılamaz | Karışık pencere çizilmez; korelasyon segment içinde |
| Artçı dizileri | Hız tepeleri oluşur; aralık dar kalır (test 7) | GK74 uyarısı; Marmara'da GK74 açılınca İzmit tepesi 3,76 → 1,50 |
| Örtüşmeyen pencerelerin öz-ilişkisi | Eğilimler p'yi iyimser yapar (§4.1: Türkiye 3e−6 → ≈ 0,07) | p "keşifsel" etiketli; n_eff düzeltmesi önerildi |
| Büyüklük ölçeği / dönüşüm değişimi (ör. ISC → EMSC, Scordilis dönüşümü) | Ölçek değişirse Mc'deki hız ve b kayar; a(t) ve b(t) değişimleri doğrudan fiziksel değişim olarak yorumlanamaz | İleriki çalışma; Mc(t) şeridi ve büyüklük türü tanısıyla birlikte değerlendirilmeli |

## 6. Gözlemler (yorum değil)

1. **Marmara 1999 İzmit:** GK74 kapalıyken belirgin bir hız tepesi görünüyor (a = 3,76; 18 Ağustos 1999). GK74 açıkken 1999–2000'deki en yüksek a 1,50; tepe büyük ölçüde artçılardan oluşuyor.
2. **Türkiye 1971–1997:** Tek Mc'deki güçlü b–a korelasyonu (r = 0,79; panelde p = 3e−6), öz-ilişki düzeltmesiyle anlamlılığını yitiriyor (n_eff ≈ 6, p ≈ 0,07). Tamlık basamaklarıyla da zayıflıyor (0,65; test edilemez). İstatistiksel olarak anlamlı görünen bir ilişki katalog özelliklerinden ve ortak eğilimden kaynaklanabilir.
3. **Marmara, GK74 açık:** a, 2000'de yaklaşık 1,5'ten 2020'de yaklaşık 1,2'ye yavaşça iniyor. Nedeni bu çalışmada araştırılmadı. Olası nedenler: Mc(t) değişimi, GK74'ün büyük deprem sonrası uzun zaman pencereleri, büyüklük dönüşümü. Fiziksel bir sonuç olarak yorumlanmamalı.

**Temel ilke:** a(t) üretim hızındaki değişimi, b(t) büyüklük dağılımındaki değişimi gösterir. İkisi aynı pencerelerden gelir; birlikte okunurken §5'teki etkenler ayrılmalıdır. İkisinin birlikte değişmesi, tek başına deprem tehlikesinin arttığı anlamına gelmez.
