# a(t) paneli — pencere olay hızı (2026-10-31, güncelleme 5)

Panel `main`'de (fbe343a, 31 Ekim). Güncelleme 4–5 (öz-ilişki düzeltmesi) `a-neff` dalında geliştirildi ve **`main`'e birleştirildi: 54fbd0b (31 Ekim 23:44)**; canlıda doğrulandı (§8).

**Güncelleme 5'te eklenenler** (ChatGPT incelemesi, 31 Ekim 23:15):
- n_eff yönteminin sağlamlığı farklı öz-ilişki yapılarında ve kısa serilerde sınandı (§4.3).
- Uzun bellek ve ortak eğilimde düzeltmenin yetersiz kaldığı panel açıklamasına eklendi (yalnızca metin).
- Birinci fark (Δa–Δb) araştırması planlandı (§4.4); panelde uygulanmadı.
- Taban denetimi: `a-neff`, güncel `main` 5274c46 üzerinde (5274c46, fbe343a'dan sonraki eq-bot veri commit'i). Kabul testleri bu tabana karşı yeniden çalıştırıldı.

**Güncelleme 4'te eklenenler** (`a-neff` dalı; ChatGPT önerisi 1):
- Panelde ham r ve ham p korunuyor; yanlarına öz-ilişki (ρ_a, ρ_b), etkin örneklem n_eff ve düzeltilmiş p eklendi. Hepsi "keşifsel" etiketli.
- Yöntem, varsayımlar, hata oranı ve güç §4.2'de.

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

**Nokta değeri:** Yayındaki tanıma uymak için n/T kullanılır. T ~ Gamma(n−1, λ) için en çok olabilirlik kestiricisi (n−1)/T, λ'nın yansız kestiricisi (n−2)/T'dir (E[1/T] = λ/(n−2)). log₁₀(n/T)'nin beklenen yanlılığı (ln n − ψ(n−1))/ln 10'dur; n = 100'de 0,0066 log birimi, yani %95 aralığın yarı genişliğinin (±0,087) yaklaşık %8'i. *(Denetim düzeltmesi, 31 Ekim: önceki sürümde "yansız kestirici (n−1)/T" ve beklenen yanlılık 0,0044 yazıyordu; ikisi de yanlıştı. Hesap değişmedi.)*

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
| 2. Yanlılık ve kapsama | λ = 20/yıl, b = 1, Mc = 3, 300 yıl; **40 katalog (tohum 11), 2387 örtüşmeyen pencere** | a − log₁₀λ = 0,0075 (beklenen 0,0066); **kapsama %95,3 [%94,4–%96,1]** |
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

Paneldeki p bu yüzden keşifseldir. Düzeltilmiş p (0,075) de kesin bir bağımsızlık düzeltmesi değildir; AR(1) varsayımına bağlıdır ve ortak eğilimde iyimser kalabilir (§4.3).

**Güncelleme 4:** n_eff ve düzeltilmiş p panele eklendi (§4.2). Eğilimi çıkarılmış (birinci fark) serilerde korelasyon hâlâ öneri olarak duruyor.

### 4.2 Öz-ilişki düzeltmesi: yöntem, varsayımlar, güvenilirlik (güncelleme 4)

**Tanım:**
1. Örtüşmeyen pencereler: her ⌈n_pencere/adım⌉'ıncı pencere, yalnızca aynı Mc segmenti içinde.
2. Bu pencerelerin a ve b serilerinden r = Pearson(b, a); ham p, n pencereyle Fisher z: z = atanh(r)·√(n − 3).
3. Gecikme-1 öz-ilişki ρ_a ve ρ_b: aynı segmentteki ardışık çiftler (a_i, a_{i+1}) üzerinden Pearson; segmentler arası çift kurulmaz; en az 5 çift.
4. Etkin örneklem (Bartlett 1935; iki öz-ilişkili seri arasındaki korelasyonun varyansı için):

```
n_eff = n · (1 − ρ_a·ρ_b) / (1 + ρ_a·ρ_b)
```

   ρ_a·ρ_b < 0 ise 0 alınır; n_eff hiçbir zaman n'yi aşmaz.
5. Düzeltilmiş p: aynı Fisher z ile, √(n_eff − 3) kullanılarak. n_eff < 5 ise verilmez ("test edilemez").

**Gecikme sınırı:** Yalnızca gecikme 1 (k = 1) kullanılır. Bartlett'in genel biçimi n_eff = n / (1 + 2 Σ_k ρ_a(k)·ρ_b(k)) tüm gecikmeleri toplar; burada seri kısa olduğu için (n = 6–22) yüksek gecikmeler güvenilir kestirilemez. Bu yüzden AR(1) varsayılır: ρ(k) = ρ^k ise toplam (1 − ρ_aρ_b)/(1 + ρ_aρ_b) biçimini verir.

**Varsayımlar:**
- İki seri de AR(1) benzeri öz-ilişki taşır; yalnızca gecikme-1 kullanılır. Daha uzun bellek varsa n_eff yüksek kalır ve p iyimser olur.
- Seriler durağandır. Ortak eğilim (ör. tamlık değişimi) varsa ρ yüksek çıkar ve düzeltme bunu kısmen yakalar, ama eğilimin nedenini ayırmaz.
- Fisher z normal yaklaşımıdır. Benzetimde t testiyle farkı ≤ 0,2 puan; ham p ile tutarlı olsun diye Fisher z seçildi.
- ρ kısa serilerden kestirilir ve aşağı yanlıdır. Yanlılık düzeltmesi (ρ + (1+4ρ)/n) denendi; testi gereksiz tutucu yaptığı için uygulanmadı (hata oranı %0,4–2,5).

**Hata oranı** (`test_a_window.js` test 8): iki bağımsız AR(1) serisi, yani gerçek korelasyon 0; 3000 tekrar, α = 0,05.

| n | φ | ham test | düzeltilmiş test | test edilebilen |
|---|---|---|---|---|
| 13 | 0 | %5,1 | %4,2 | %100 |
| 13 | 0,8 | %21,8 | %3,1 | %81 |
| 22 | 0 | %5,6 | %5,1 | %100 |
| 22 | 0,8 | %26,9 | %2,5 | %92 |
| 50 | 0,8 | %31,7 | %3,2 | %100 |

Düzeltilmiş test nominal düzeyi aşmıyor; ham test öz-ilişkide %32'ye kadar sahte anlamlılık üretiyor.

**Güç** (gerçek korelasyon var; `neff_guc.js` benzetimi, 3000 tekrar):

| n | φ | gerçek korelasyon | ham | düzeltilmiş |
|---|---|---|---|---|
| 13 | 0,5 | 0,5 | %45 | %32 |
| 22 | 0,5 | 0,5 | %65 | %52 |
| 22 | 0,8 | 0,5 | %64 | **%22** |
| 22 | 0,8 | 0,8 | %97 | %70 |
| 50 | 0,8 | 0,5 | %84 | %50 |

(Ham testin "gücü", aynı zamanda yüksek sahte anlamlılık oranı demektir; doğrudan karşılaştırılamaz.)

**Panelde gösterim (ChatGPT'nin üç güvencesi):**
1. Formül, gecikme sınırı ve benzetim sonuçları, düzeltilmiş p'nin üzerine gelindiğinde açıklamada yazar.
2. 5 ≤ n_eff < 10 ise turuncu uyarı çıkar: "küçük n_eff (< 10): testin gücü düşük — p > 0,05 ilişkinin yokluğunu göstermez". n_eff < 5 ise p verilmez ("test edilemez").
3. Ham p ve düzeltilmiş p ayrı yazılır. Düzeltilmiş p ayrı renkte (gri-mavi), "öz-ilişki (gecikme 1)" etiketiyle gösterilir; hiçbiri kalın değil. Ham p'nin açıklamasında "düzeltilmiş p onun yerine geçmez; ikisi birlikte okunmalıdır" yazar.

**Yorum:** Küçük n_eff'te düzeltilmiş test tutucu ve düşük güçlüdür. Türkiye 1971–1997'deki koşullarda (n = 22, ρ ≈ 0,75) orta düzey bir gerçek korelasyonu (0,5) yakalama olasılığı yaklaşık %22. Bu yüzden düzeltilmiş p'nin anlamlı çıkmaması (0,075) ilişkinin **olmadığını göstermez**; yalnızca bu veriyle **gösterilemediğini** söyler. Sonuç "keşifsel" etiketiyle sunulur.

**Kabul testi** (`kabul_a.js`, önce = main 5274c46): **27/27**.
- a(t) grafiği ve değerleri önce = sonra; b(t) ve G–R metni önce = sonra.
- ρ_a, ρ_b ve n_eff bağımsız hesapla aynı.

| Senaryo | r | ham p | ρ_a | ρ_b | n_eff | düzeltilmiş p |
|---|---|---|---|---|---|---|
| Türkiye 1971–1997, tek Mc | 0,79 | 3,1e−6 | 0,73 | 0,80 | 5,8 | **0,075** |
| Aynı, basamaklı | 0,65 | 0,083 | 0,60 | 0,62 | 3,7 | test edilemez |
| Marmara, GK74 kapalı | −0,05 | 0,86 | 0,51 | 0,62 | 6,8 | 0,92 |
| Marmara, GK74 açık | 0,71 | 0,13 | 0,84 | 0,44 | 2,8 | test edilemez |

### 4.3 n_eff düzeltmesinin sağlamlığı (`neff_saglamlik.js`, sonuç `neff_saglamlik.json`)

H0: iki seri bağımsız. Her durumda 2000 tekrar, α = 0,05. "Test edilebilen": n_eff ≥ 5. ρ̂: ortalama kestirilen gecikme-1 öz-ilişki.

| Yapı | n | Ham | Düzeltilmiş | Test edilebilen | ort. ρ̂ |
|---|---|---|---|---|---|
| AR(1), φ = 0,2 | 6 / 22 / 50 | %5,0 / 5,1 / 5,5 | %2,4 / 4,4 / 4,8 | %79 / 100 / 100 | −0,07 / 0,13 / 0,17 |
| AR(1), φ = 0,5 | 6 / 22 / 50 | %7,0 / 11,8 / 11,3 | %2,7 / 5,5 / 4,5 | %76 / 100 / 100 | 0,06 / 0,39 / 0,45 |
| AR(1), φ = 0,8 | 6 / 13 / 22 / 50 | %11,8 / 22,6 / 26,8 / 33,0 | %2,4 / 2,6 / 2,8 / 4,3 | %65 / 80 / 93 / 100 | 0,24 / 0,52 / 0,62 / 0,73 |
| AR(1), φ = 0,95 | 6 / 22 / 50 | %14,5 / 43,0 / 54,5 | %1,9 / 1,2 / 1,4 | %56 / 62 / 78 | 0,31 / 0,75 / 0,86 |
| MA(1), θ = 0,8 | 13 / 22 / 50 | %11,3 / 10,8 / 10,8 | %5,1 / 4,2 / 4,5 | %99–100 | 0,36–0,46 |
| **AR(2) uzun bellek** (φ₁ 0,5, φ₂ 0,4) | 13 / 22 / 50 | %18,4 / 28,9 / 45,8 | **%5,3 / 8,9 / 16,7** | %94–100 | 0,32 / 0,48 / 0,67 |
| Rastgele yürüyüş (durağan değil) | 13 / 22 / 50 | %36,1 / 44,8 / 66,3 | %1,9 / 0,8 / 0,5 | %48–55 | 0,63 / 0,77 / 0,90 |
| **Ortak yönde eğilim** + AR(1) 0,5 | 13 / 22 / 50 | %17,5 / 24,7 / 37,5 | **%3,6 / 6,2 / 14,3** | %92–100 | 0,42 / 0,49 / 0,55 |

Tüm satırlar (AR(1) için n = 6, 8, 10, 13, 22, 50 ve φ = 0,2, 0,5, 0,8, 0,9, 0,95) JSON dosyasında.

**Sonuçlar:**
1. **AR(1) ve MA(1)'de** düzeltilmiş test hiçbir koşulda %5,5'i aşmıyor; φ büyüdükçe tutucu oluyor (φ = 0,95'te %1–2).
2. **Kısa serilerde ρ̂ aşağı yanlı:** φ = 0,8 iken n = 13'te 0,52, n = 6'da 0,24. Yine de düzeltilmiş test tutucu kalıyor, çünkü n_eff < 5 durumları "test edilemez" olarak ayrılıyor (φ ≥ 0,8 ve n ≤ 13'te serilerin %20–45'i).
3. **Uzun bellek (AR(2)):** Gecikme-1 bağımlılığın tamamını yakalayamıyor; hata oranı n = 22'de %8,9, n = 50'de %16,7.
4. **Ortak yönde eğilim:** Deterministik eğilim gecikme-1 öz-ilişkiye tam yansımıyor; hata oranı n = 22'de %6,2, n = 50'de %14,3. **Türkiye 1971–1997'de şüphelenilen durum (tamlık kaynaklı ortak eğilim) tam olarak budur.** Bu yüzden o örnekteki düzeltilmiş p = 0,075 bile iyimser olabilir.
5. **Durağan olmayan seriler (rastgele yürüyüş):** Düzeltme çok tutucu; yaklaşık yarı serilerde test edilemiyor.

Bu sınırlar panel açıklamasına eklendi: "AR(1) dışındaki yapılarda düzeltme yetersiz kalabilir: uzun bellek ve ortak eğilimde %6–17". p keşifsel olarak kalıyor. Monte Carlo sonuçları (§4.2, test 8) değişmeden korunuyor.

### 4.4 Birinci fark (Δa–Δb) araştırması: plan (uygulanmadı)

**Soru:** Ardışık örtüşmeyen pencerelerdeki değişimler birlikte hareket ediyor mu? Mevcut a–b korelasyonu ise uzun dönemli birlikte değişimi ölçer. İkisi aynı soruyu yanıtlamaz.

**Tanım:**
- Aynı Mc segmentindeki ardışık örtüşmeyen pencerelerde Δa_i = a_i − a_{i−1}, Δb_i = b_i − b_{i−1}.
- r(Δb, Δa); segmentler arası fark alınmaz.

**Beklenen istatistik davranışı:**
- Fark almak deterministik eğilimi ve rastgele yürüyüşü giderir.
- Ama beyaz gürültüde fark serisinde ρ ≈ −0,5 olan MA(1) yapısı oluşur. Bu yapı §4.3'te sorunsuz çıktı; aynı n_eff düzeltmesi uygulanabilir.
- Bir gözlem kaybedilir (n − 1).
- a ve b aynı pencerelerden gelir; pencere içi örnekleme hatası fark serisinde ortak bileşen oluşturabilir. Benzetimle denetlenmeli.

**Doğrulama planı:**
- §4.3'teki yapılar (özellikle ortak eğilim ve AR(2)) için Δ testinin hata oranı.
- Gerçek bağlantılı seriler için güç.
- Türkiye 1971–1997 ve Marmara örneklerinde ham ve Δ sonuçlarının yan yana raporlanması.

**Sunum:** Mevcut hesapların üzerine yazılmaz. Ayrı bir araştırma dalında hesaplanır; panele eklenip eklenmeyeceği sonuçlara göre ayrıca karar verilir. Δ korelasyonu da nedensellik ya da fiziksel ilişki kanıtı değildir.

## 5. a–b ilişkisini karıştırabilecek etkenler

| Etken | Etkisi | Panelde nasıl ele alınıyor |
|---|---|---|
| Aynı olaylardan hesaplama | a ve b aynı 100 olaydan gelir. Sabit n'de G–R kesişimi a_GR yapısal olarak b'ye bağlıdır (test 4). | Çizilen a = log₁₀(n/T), b'den yapısal olarak bağımsız (test 4: r = 0,00); a_GR yalnızca açıklamada |
| Örtüşen pencereler | Ardışık pencereler 90 olay paylaşır; bağımsız sayılırsa sahte anlamlılık çıkar (test 5: %46) | p yalnızca örtüşmeyen pencerelerle |
| Tamlık değişimi | Mc'nin altında kalan dönemde kaydedilen hız ve b birlikte düşer; yapay pozitif korelasyon oluşur | Uyarı metni; tamlık basamaklarıyla segmentlere bölme; Türkiye 1971–1997'de r 0,79 → 0,65 (anlamlı değil) |
| Mc basamakları | Farklı eşiklerin hızları karşılaştırılamaz | Karışık pencere çizilmez; korelasyon segment içinde |
| Artçı dizileri | Hız tepeleri oluşur; aralık dar kalır (test 7) | GK74 uyarısı; Marmara'da GK74 açılınca İzmit tepesi 3,76 → 1,50 |
| Örtüşmeyen pencerelerin öz-ilişkisi | Eğilimler p'yi iyimser yapar (§4.1: Türkiye 3e−6 → 0,075) | Ham p ile birlikte n_eff ve düzeltilmiş p; "keşifsel" (§4.2) |
| Büyüklük ölçeği / dönüşüm değişimi (ör. ISC → EMSC, Scordilis dönüşümü) | Ölçek değişirse Mc'deki hız ve b kayar; a(t) ve b(t) değişimleri doğrudan fiziksel değişim olarak yorumlanamaz | İleriki çalışma; Mc(t) şeridi ve büyüklük türü tanısıyla birlikte değerlendirilmeli |

## 6. Gözlemler (yorum değil)

1. **Marmara 1999 İzmit:** GK74 kapalıyken belirgin bir hız tepesi görünüyor (a = 3,76; 18 Ağustos 1999). GK74 açıkken 1999–2000'deki en yüksek a 1,50; tepe büyük ölçüde artçılardan oluşuyor.
2. **Türkiye 1971–1997:** Tek Mc'deki güçlü b–a korelasyonu (r = 0,79; panelde p = 3e−6), öz-ilişki düzeltmesiyle anlamlılığını yitiriyor (n_eff ≈ 6, p ≈ 0,07). Tamlık basamaklarıyla da zayıflıyor (0,65; test edilemez). İstatistiksel olarak anlamlı görünen bir ilişki katalog özelliklerinden ve ortak eğilimden kaynaklanabilir.
3. **Marmara, GK74 açık:** a, 2000'de yaklaşık 1,5'ten 2020'de yaklaşık 1,2'ye yavaşça iniyor. Nedeni bu çalışmada araştırılmadı. Olası nedenler: Mc(t) değişimi, GK74'ün büyük deprem sonrası uzun zaman pencereleri, büyüklük dönüşümü. Fiziksel bir sonuç olarak yorumlanmamalı.

**Temel ilke:** a(t) üretim hızındaki değişimi, b(t) büyüklük dağılımındaki değişimi gösterir. İkisi aynı pencerelerden gelir; birlikte okunurken §5'teki etkenler ayrılmalıdır. İkisinin birlikte değişmesi, tek başına deprem tehlikesinin arttığı anlamına gelmez.

## 7. `a-neff` birleştirme öncesi son kontrol (2026-10-31)

| Kontrol (ChatGPT listesi) | Sonuç |
|---|---|
| 1. Güncel `main` ile karşılaştırma | Güncel `main` = 5274c46 = `a-neff`'in tabanı. fbe343a (a(t) birleştirmesi) 5274c46'nın atası. Dal güncel, taşıma gerekmedi; `git merge-tree` çakışma yok. |
| 2. n_eff'in farklı öz-ilişki yapılarında ve kısa serilerde davranışı | §4.3. AR(1)/MA(1)'de ≤ %5,5; AR(2) uzun bellekte %8,9–16,7, ortak eğilimde %6,2–14,3 (yetersiz). Sınır panel açıklamasında. Mevcut Monte Carlo sonuçları korundu (§4.2). |
| 3. Birinci fark analizi | §4.4'te ayrı araştırma olarak planlandı; mevcut hesaplar değişmedi. |
| 4. Ham r, ham p, n_eff ve düzeltilmiş p ayrı ayrı | Panelde dördü ayrı yazılıyor; `lastAts.corr` alanları {r, pHam, rhoA, rhoB, neff, pDuz} ayrı. Kabul (6) denetliyor. |
| 5. a(t), b(t), G–R ve katalog hesapları güncel `main`'e göre değişmedi | Kabul `kabul_a.js` (önce = origin/main 5274c46): **31/31**. Dört senaryoda a(t) grafiği ve değerleri, b(t) grafiği ve metni, G–R metni önce = sonra. Birim testleri 15/15. `data/` `main` ile aynı. `index.html` farkı +20/−2 satır, yalnızca `renderAvalueTS`'in korelasyon bölümü ve yeni yardımcı fonksiyonlar (`aLag1`, `aNeffTest`). |

Bu bölüm birleştirme öncesi durumu kaydeder. Birleştirme sonrası durum §8'dedir.

## 8. Birleştirme sonrası durum (2026-10-31 23:44)

| Konu | Durum |
|---|---|
| Birleştirme | `a-neff` → `main`: **54fbd0b** (önceki `main` 5274c46). Değişiklikler artık `main`'de. |
| Değişen dosyalar | 12: `index.html` (+20/−2, yalnızca a(t) korelasyon bölümü ve `aLag1`, `aNeffTest`), `scripts/test_a_window.js`, `analysis/a_zaman/*` |
| `data/` | Değişmedi (`git diff origin/main..54fbd0b -- data` boş) |
| Birleştirme öncesi testler (güncel `main` 5274c46'ya karşı) | Kabul `kabul_a.js` 31/31; birim 15/15 |
| GitHub otomatik testleri (54fbd0b) | GK74 eşleşmesi (Python = JS), b güven aralığı, ISC-GEM katmanı: başarılı |
| Pages yayını | Başarılı |
| Canlı kontrol (Türkiye, ISC 1971–1997, dikdörtgen 36–42° K / 26–45° D) | a(t) 211 pencere = b(t) 211 pencere; r = 0,79 (örtüşmeyen 22); ham p = 3,1e−6; ρ_a = 0,73, ρ_b = 0,80; n_eff = 5,8; düzeltilmiş p = 0,075; "küçük n_eff" uyarısı görünüyor. Kabul testiyle birebir aynı. |

**Yorum ilkesi (değişmedi):** Türkiye 1971–1997 için düzeltilmiş p = 0,075, keşifsel ve varsayımlara bağlı bir değerlendirmedir:
- AR(1) varsayımına dayanır.
- Uzun bellek ya da ortak eğilim varsa iyimser kalabilir (§4.3).
- Testin gücü düşüktür (§4.2); p > 0,05 ilişkinin yokluğunu göstermez.

**Sonraki işler** (ayrı dallarda, mevcut a(t), b(t), GK74 ve katalog hesapları değişmeden):
1. Mc uyumsuzluğu uyarısı.
2. Birinci fark (Δa–Δb) analizi.
3. Poisson bağımsız dönem sınaması.
4. ISC–EMSC araştırması: araştırma dalında.
