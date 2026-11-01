# Birinci fark (Δa–Δb) araştırması — rapor (2026-11-01)

**Dal:** `fark-ab`, `main` 108c14a'dan açıldı. Yalnızca `analysis/fark_ab/` eklendi. `index.html`, `data/` (`eq_historical.json` dahil), GK74 kodu ve uygulama hesapları değişmedi. Uygulama fonksiyonları (`aWinValue`, `aPearson`, `aLag1`, `aNeffTest`, `computeBvalue`, `computeMcSrc`) `index.html`'den **okunarak** kullanıldı; sonuçlar paneldeki tanımlarla aynı.

**Amaç ve sınır:** Bu çalışma sismisite rejiminin zamansal değişimini **betimler**. Bir tahmin ya da öncül araştırması değildir. Δa–Δb ilişkisi fiziksel bir mekanizma ya da deprem habercisi olarak yorumlanmaz.

**Betikler:**
- `analiz.js` → `sonuc.json`: tasarım, sonuçlardan önce betiğin başlığında sabitlendi.
- `oz_denetim.js` → `oz_denetim.json`: yöntemin sentetik kataloglarla doğrulanması, 5/5.
- Girdi: `analysis/tur_gecisi/disa_aktar.js` çıktısı (uygulamanın kendi bölge sorgusu ve GK74'ü; depoya eklenmez).

## Özet

1. **Birincil test** (GK74, Mc 3,5, n = 100, Türkiye) anlamlı değil. MD döneminde r(Δa, Δb) = 0,18 (p = 0,44). ML döneminde r = −0,51; karıştırma p = 0,041, **Holm sonrası 0,083**. ML sonucu büyük ölçüde Şubat 2023 Kahramanmaraş pencerelerine dayanıyor: GK74 sonrasında da yüksek hız, düşük b ve yükselmiş pencere Mc'si var. Bu pencereler çıkarılınca r = −0,25 (sonradan hesap).
2. **Mc 3,2'de MD dönemindeki pozitif bağ** (r = 0,38, p = 0,006) **tamlık dalgalanmasının imzasıyla** uyumlu. Sentetik kataloglarda dalgalanan algılama eşiği aynı işaretli bağı üretiyor (ortalama r = 0,33) ve eşiğin üstündeki Mc'de kayboluyor. Gerçek veride de Mc 3,5'te kayboluyor (r = 0,18, p = 0,44).
3. **Ham katalogdaki yapılar artçı dizilerinden geliyor; GK74 ile kayboluyor.** Ham katalogda düzey korelasyonu 21 senaryonun 11'inde anlamlı ve negatif (yüksek hız, düşük b). Gecikme −1'deki negatif bağ ham katalogda 21 senaryonun 8'inde anlamlı, GK74 ile 17 senaryonun hiçbirinde değil.
4. **Marmara bu yöntemle değerlendirilemiyor.** GK74 ile 18 senaryonun 17'sinde 6'dan az örtüşmeyen pencere var. Türkiye–Marmara karşılaştırması yapılamadı.
5. **Bulunmayan sonuç:** Homojen tür dönemleri içinde, yüksek Mc'de ve artçılar ayıklandığında, Δa ile Δb arasında çoklu teste dayanıklı bir bağ bulunmadı. Bu, bağın olmadığını göstermez. Örnek küçük: 21–25 fark, pencere süresinin medyanı 0,47–0,63 yıl.

## 1. ChatGPT'nin önerdiği aşamalarla eşleme

| Aşama | Bu raporda |
|---|---|
| 1–2. Δa ve Δb değişimi | §2 tanım; pencere serileri `sonuc.json`'da (`pencereler`) |
| 3. Δa–Δb ilişkisi | §4 birincil test, §5 keşifsel sonuçlar |
| 4. Zamansal gecikmeler | §5.3 (gecikme −2…+2 pencere) |
| 5. Türkiye–Marmara | §6: Marmara'da örnek yetersiz |
| 6. GK74 açık / kapalı | §5.2 |
| Aynı Mc ve gözlem aralığı | Mc 3,2 / 3,5 / 4,0 sabit; aynı tür dönemleri |
| Örneklem büyüklüğü | n = 50 / 100 / 200; en az 6 pencere şartı |
| Güven aralıkları | Sıfır modeline göre %95 aralık; pencere a'larının Gamma aralığı uygulamada |

## 2. Tasarım (önceden sabitlendi)

- **Pencereler:** Aynı Mc'deki olaylar zamana göre sıralanır ve baştan başlayarak ardışık, **örtüşmeyen** n'lik pencerelere bölünür.
  - a_i = log₁₀(n/T_i): T_i, pencerenin ilk ve son olayı arasındaki süre (uygulamanın `aWinValue`'su).
  - b_i: Aki, ΔM = 0,1 (uygulamanın `computeBvalue`'su).
  - Δa_i = a_i − a_{i−1}, Δb_i = b_i − b_{i−1}.
  - Paneldeki 10 olay adımlı örtüşen pencereler kullanılmadı; onların farkı büyük ölçüde ortak olayları ölçer.
- **Tür dönemleri:** MD 1998–2010 ve ML 2012–, tür geçişi analizinden. 2011 (geçiş yılı) dışarıda; dönemler arasında fark alınmadı.
- **Kapsam:** Bölgeler Türkiye (36–42° K / 26–45° D) ve Marmara (40–41,5° K / 26–31° D). GK74 açık (ana) ve kapalı. Mc 3,2, 3,5 ve 4,0. Pencere boyu n = 50, 100 ve 200. En az 6 pencere (5 fark) yoksa senaryo "yetersiz" sayıldı.
- **Sıfır modeli: büyüklük karıştırma** (2000 kez). Olay zamanları korunur, büyüklükler dönem içinde rastgele karıştırılır. Böylece a serisi ve öz-ilişkisi **aynen** kalır; yalnızca büyüklük ile zaman arasındaki bağ yok edilir. Karşılaştırma için Bartlett n_eff düzeltmeli p da verildi (uygulamanın `aNeffTest`'i).
- **Ölçüler:**
  - Pearson r(Δa, Δb) (ana ölçü) ve Spearman.
  - Gecikmeli r(Δa_i, Δb_{i+L}), L = −2…+2.
  - Dört bölge sayıları (Δa ±, Δb ±) ve sıfır modelinde beklenen değerleri.
  - Düzey korelasyonu r(a, b), karşılaştırma için.
- **Tamlık tanısı:** Pencere Mc'si (uygulamanın `computeMcSrc`'si) Mc + 0,2'yi aşan pencereler "eksik kuşkulu" sayıldı. Duyarlılık için bu pencerelere dokunan farklar çıkarıldı.
- **Birincil aile:** GK74, Mc 3,5, n = 100, Türkiye MD ve ML; 2 test, Holm düzeltmesi. Marmara olay sayısı nedeniyle ikincil. Diğer bütün birleşimler keşifsel.

## 3. Yöntemin doğrulanması (`oz_denetim.js`, 5/5)

200 sentetik katalog, 199 karıştırma, n = 100, 31 pencere:

| Sınama | Yapı | r ortalaması | p < 0,05 (karıştırma / n_eff) |
|---|---|---|---|
| T1 durağan | Poisson, b = 1 | −0,010 | %6,0 / %5,0 (beklenen %5) |
| T2 güç | Rejimler: hız λ ve b = 1,0 ↔ hız 2λ ve b = 0,8 | −0,43 | %68 / %68 |
| T3 tamlık dalgalanması, Mc 3,2 | Gerçek b = 1, durağan hız; algılama eşiği yıldan yıla 3,0–3,4 | **+0,33** | **%82** / %84 |
| T3, Mc 3,5 (eşiğin üstü) | Aynı katalog | 0,003 | %3,5 / %3,5 |

**Sonuçlar:**
- Pencere içi örnekleme ortak bir bileşen üretmiyor (T1).
- Sıfır modeli doğru düzeyde çalışıyor ve gerçek bir ortak değişimi yakalıyor (T2).
- **Tamlık dalgalanması tek başına güçlü bir pozitif Δa–Δb bağı üretiyor** (T3). Algılama eşiği düştüğünde küçük olaylar eklenir; bu, hızı (a) ve küçük olayların payını (b) birlikte artırır. Bu imza, Mc dalgalanmanın üstüne çıkınca kayboluyor.

## 4. Birincil sonuç (GK74, Mc 3,5, n = 100, Türkiye)

| Dönem | Pencere (medyan süre) | r(Δa, Δb) | Spearman | Karıştırma p | Sıfır %95 | n_eff p | Holm |
|---|---|---|---|---|---|---|---|
| MD 1998–2010 | 26 (0,47 yıl) | 0,18 | 0,12 | 0,44 | −0,47, 0,45 | 0,53 | 0,44 |
| ML 2012– | 22 (0,63 yıl) | **−0,51** | −0,52 | 0,041 | −0,49, 0,50 | 0,036 | **0,083** |

**ML döneminin ayrıntısı:**
- **Birer çıkarma:** r −0,57 ile −0,34 arasında kalıyor. En etkili pencereler 2022-09-04 → 2023-02-09 (a = 2,36, b = 0,58, pencere Mc'si 3,7) ve 2023-02-09 → 2023-07-13 (a = 2,38, b = 0,75, pencere Mc'si 3,8). Bunlar Kahramanmaraş dizisini içeren pencereler.
- **2023 pencereleri çıkarılınca** (sonradan hesap, kanıt değil): r = −0,25.
- **Gecikmeler:** L = 0'da −0,51, L = +1'de +0,52. Aynı büyüklükte zıt işaretli bu ikili, tek bir aykırı pencerenin farklarda bıraktığı tipik iz: pencereye giriş ve pencereden çıkış.
- **Dört bölge:** (+, −) 7 ve (−, +) 10 kez; sıfır modelinde beklenen 4 ve 6,5.
- **Eksik kuşkulu pencereler** (8 pencere) çıkarılınca r = −0,82 (9 fark, p = 0,018). Ancak 2022–2023 penceresi pencere Mc'si 3,7 olduğu için eşiği (3,7) aşmıyor ve maskede kalıyor. Bu duyarlılık analizi, 2023 etkisini ayırmıyor.

**Okuma:** ML dönemindeki negatif bağ çoklu test düzeltmesine dayanıklı değil. Kaynağı da büyük ölçüde tek bir büyük dizi: GK74'ün tam ayıklayamadığı artçılar ve artçı döneminde kısa süreli tamlık eksikliği. Poisson raporundaki "GK74 2023 dizisini tam ayıklayamıyor" bulgusuyla tutarlı. **Sismisite rejimi değişimi olarak yorumlanmamalı.**

## 5. Keşifsel sonuçlar

38 senaryo değerlendirilebildi (72 senaryonun 34'ünde örnek yetersiz). Gecikme testlerinin toplamı 190; şansla beklenen yanlış alarm yaklaşık 9,5, gözlenen 20. Fazlanın çoğu ham katalogdaki gecikme −1 örüntüsünden geliyor (§5.3).

### 5.1 Mc 3,2: tamlık dalgalanmasının imzası

| Senaryo (GK74, MD) | r(Δa, Δb) | Karıştırma p | Düzey r(a, b) |
|---|---|---|---|
| Mc 3,2, n = 100 | **0,38** | 0,006 | **0,80** (p < 0,001) |
| Mc 3,5, n = 100 | 0,18 | 0,44 | 0,32 (p = 0,11) |

- Birer çıkarma aralığı 0,31–0,44: tek bir pencereye dayanmıyor.
- Eksik kuşkulu pencereler çıkarılınca r = 0,48, yani sürüyor.
- Ama bu imza T3'ün öngördüğü örüntüyle birebir aynı: Mc 3,2'de pozitif, Mc 3,5'te kayboluyor. Katalog M 3,0'da kesilmiş ve Mc ayrıca belirlenemiyor (tür geçişi raporu §2). MD döneminde ağın algılama eşiği yıldan yıla değişti (Poisson raporu §2: MD döneminde M ≥ 3,2 sayısı 1,92 katına çıktı).
- **Yorum:** Mc 3,2'deki pozitif bağ, büyük olasılıkla **tamlık dalgalanmasından** geliyor. Düzey korelasyonunun 0,80 olması da aynı nedene bağlanabilir: a ve b birlikte artan algılamayı izliyor. Panelde varsayılan Mc 3,2 ile görülen a–b birlikte değişimi de bu etkiyi taşıyabilir.

### 5.2 GK74 açık ve kapalı

| | GK74 açık (17 senaryo) | GK74 kapalı (21 senaryo) |
|---|---|---|
| r(Δa, Δb) p < 0,05 | 2 | 2 |
| Gecikme −1, p < 0,05 | **0** | **8** (hepsi negatif, r −0,16 ile −0,50) |
| Düzey r(a, b), p < 0,05 | 4 (hepsi pozitif) | 14 (11 negatif, 3 pozitif) |

- **Ham katalogda negatif düzey bağı** (yüksek hız ve düşük b) artçı dizilerinin bilinen etkisi: dizide hem hız yüksek, hem de ana şoktan hemen sonraki kısa süreli tamlık eksikliği nedeniyle b düşük. GK74 bu bağı kaldırıyor: ML döneminde ham katalogda −0,27 ile −0,43 arası (9 senaryonun 8'i anlamlı), GK74 ile −0,37 ile 0,33 arası (hiçbiri anlamlı değil).
- **GK74 ile kalan pozitif düzey bağları** yalnızca Mc 3,2–3,5'te ve MD döneminde (§5.1).

### 5.3 Gecikmeler

- **Ham katalogda gecikme −1, yani r(Δa_i, Δb_{i−1}), 21 senaryonun 8'inde anlamlı ve hep negatif;** GK74 ile hiçbirinde anlamlı değil. Bu, artçı dizilerinin pencerelere dağılımından gelen bir yapıyla uyumlu.
- **Uyarı:** Biçimsel olarak "b değişimi, a değişiminden bir pencere önce" gibi okunabilir, ama **bir öncül olarak yorumlanamaz.** GK74 ile tamamen kayboluyor ve pencere sınırlarının artçı dizilerine göre konumuna bağlı.
- GK74 açık senaryolarda gecikme testlerinden anlamlı çıkan tek tutarlı örüntü, ML birincil senaryosundaki L = 0 / L = +1 ikilisi; bu da tek aykırı pencerenin izi (§4).

### 5.4 Geçişi kesen seri (gösterim; yorumlanmaz)

Türkiye, GK74, Mc 3,5, n = 100, 1998–son: b, 2009–2011 pencerelerinde 1,45 → 1,27 → 1,00 → 0,98 → 0,89'a düşüyor. MD dönemi b ortalaması 1,18, ML dönemi 0,88. Bu fark tür geçişi raporundaki ölçek farkıyla tutarlı (MD dağılımı M < 4'te daha dik). Dönemleri ayırmasaydık, tek seferlik bu yapay düşüş Δb serisine girerdi.

## 6. Marmara

| GK74 | Değerlendirilebilen senaryo |
|---|---|
| Açık | 18 senaryonun 1'i (Mc 3,2, n = 50, MD: 6 pencere, r = −0,65, p = 0,26) |
| Kapalı | 18 senaryonun 4'ü (en çok 16 pencere; hiçbirinde p < 0,05) |

Marmara'da GK74 sonrası M ≥ 3,5 olay sayısı MD döneminde 131, ML döneminde 150. n = 100'lük pencerelerle dönem başına 1–2 pencere çıkıyor. **Türkiye–Marmara karşılaştırması bu yöntemle yapılamıyor.** Pencereyi küçültmek (örneğin n = 20) b'nin belirsizliğini ±0,22'ye çıkarır ve fark serisini büyük ölçüde gürültüye çevirir. Bu yüzden denenmedi.

## 7. Sonuçlar

1. **Yöntem çalışıyor** (doğrulama 5/5): gerçek bir ortak değişimi yakalıyor, durağan katalogda yanlış alarm oranı doğru.
2. **Türkiye'de, homojen tür dönemleri içinde, GK74 ile ve Mc 3,5'te, Δa ile Δb arasında çoklu teste dayanıklı bir bağ yok.** ML dönemindeki sınırda negatif bağ, 2023 Kahramanmaraş dizisinin GK74 sonrası kalıntısına dayanıyor.
3. **Gözlenen bağların açıklaması büyük olasılıkla katalog kaynaklı:**
   - Düşük Mc'de tamlık dalgalanması, pozitif bağ üretiyor.
   - Artçı dizileri ve kısa süreli tamlık eksikliği, negatif düzey bağı ve gecikme −1 örüntüsü üretiyor.
   - Tür geçişi, dönemler arası b sıçraması üretiyor.
   Bunların hiçbiri sismotektonik bir rejim değişimi olarak yorumlanmamalı.
4. **Marmara bu çözünürlükte değerlendirilemiyor.**
5. **Pratik sonuç:** a(t) panelindeki a–b korelasyonu (düzey), varsayılan Mc'de (3,2) tamlık dalgalanmasını, GK74 kapalıyken de artçı dizilerini yansıtabilir. Panel bunu kısmen söylüyor (n_eff ve Mc uyarıları). İstenirse panelin korelasyon notuna bir cümle eklenebilir: "Düşük Mc'de tamlık dalgalanması a ve b'yi birlikte değiştirir." Bu bir öneri; uygulanmadı.

## 8. Sınırlar

- **Örnek küçük:** 21–25 fark, medyan pencere süresi 0,47–0,63 yıl. Testin gücü sınırlı (T2'de %68, gerçek veride daha az fark). Bağ bulunmaması, bağın olmadığını göstermez.
- **Karıştırma sıfır modeli** zaman yapısını korur. Ancak büyüklüklerin dönem içinde aynı dağılımdan geldiğini varsayar; tamlık değişirse bu varsayım zaten bozulur. T3 bunun sonucunu gösteriyor.
- **Tamlık tanısı** pencere Mc'sine (en büyük eğrilik) dayanıyor; katalog kesimi nedeniyle bu değer 3,2'nin altına inemez.
- **Sonradan seçimler:** 2023 çıkarma hesabı ve birer çıkarma analizi sonradan yapıldı; yalnızca yorum içindir.
- **GK74** uzun kırılmalı büyük depremlerde yetersiz (Poisson raporu). Başka ayıklama yöntemleri (Reasenberg, ETAS) bu çalışmanın kapsamı dışında.
- **Kapsam:** Pencereler olay sayısıyla tanımlı. Zamana dayalı pencereler (örneğin yıllık) farklı sonuç verebilir; denenmedi.
