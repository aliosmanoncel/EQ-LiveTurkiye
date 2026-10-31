# Poisson bağımsız dönem sınaması ve dağılım testi — araştırma raporu (2026-11-01)

**Dal:** `poisson-donem-sinamasi`, `main` bfc3c6d'den açıldı. Yalnızca araştırma dosyaları eklendi; `index.html`, `data/`, a(t), b(t), GK74 ve katalog hesapları değişmedi. Ham veri yalnızca okundu.

**İki ayrı soru:**
1. **Öngörü başarısı:** Bir dönemde kurulan sabit hızlı Poisson modeli, bağımsız bir sonraki dönemin olay sayılarını öngörebiliyor mu?
2. **Poisson varsayımı:** Yıllık sayılar Poisson dağılımına uyuyor mu (varyans ≈ ortalama)?

Birinci sınama yalnızca öngörü başarısını değerlendirir; ikinci soruyu yanıtlamaz.

**Betikler:**
- `disa_aktar.js`: uygulamanın kendi koduyla (bölge, GK74, dönüşüm, computeMc) olay listesini çıkarır. Çıktısı depoya eklenmez.
- `analiz.js` → `sonuc.json`.
- `oz_denetim.js`: istatistik fonksiyonlarının denetimi, 6/6.
- `sonradan_2023.js`: sonradan yapılan duyarlılık hesabı (§4).

## 1. Tasarım ve önceden sabitlenen kurallar

**Kurallar (sınama dönemine bakılmadan, `analiz.js` başlığında):**
- Mc yalnızca kurma döneminden (K) alınır; sınama döneminin (S) Mc'si yalnızca tamlık denetimi için raporlanır.
- Eşikler: Mc, 4,0, 4,5, 5,0, 5,5, 6,0.
- Büyüklük ham (dönüşüm yok); Scordilis (2006) yalnızca duyarlılık için.
- GK74 kapalı ve açık.

**Modeller:**
- **Model 1 — sabit hız, ampirik:** λ̂ = N_K/T_K. Sınama, koşullu binom testiyle yapılır: N_S | N_K + N_S ~ Bin(N, T_S/(T_K + T_S)). Bu test λ̂'nın kendi belirsizliğini de içerir. Ayrıca hız oranı R = (N_S/T_S)/(N_K/T_K) ve %95 aralığı verilir.
- **Model 2 — sabit hız, G–R uzatması:** λ(≥M) = N_K(≥Mc)/T_K·10^(−b̂(M−Mc)). Öngörü aralığı parametrik bootstrap ile (20 000 çekiliş, tohum 2026).
- **Model 3 — zamanla değişen hız:** yıllık sayılarda log-doğrusal Poisson regresyonu. "Gerekçeli" sayılması için K içinde eğilim testi p < 0,05 olmalı. Başarı ölçütü: S'nin yıllık sayılarının Poisson log-skoru, Model 1 ile karşılaştırılarak.
- **Dağılım testi:** tam yıllık sayılar, D = Σ(x − x̄)²/x̄ ~ χ²(n − 1). Ayrıca log-doğrusal eğilim çıkarılmış Pearson χ²/sd.

**Bölgeler:** Türkiye kutusu (36–42° K / 26–45° D) ve Marmara (40–41,5° K / 26–31° D).

### 1.1 Tasarım düzeltmesi: EMSC içinde MD → ML geçişi

Önceden seçilen ana bölünme 1998–2011 → 2012–2026'ydı. Sınama sonuçlarına bakılmadan yapılan tür bileşimi denetimi, EMSC'nin kendi içinde de homojen olmadığını gösterdi. Türkiye M ≥ 3,2 verisinde baskın tür yıllara göre:

| Yıl | 1998–2009 | 2010 | 2011 | 2012– |
|---|---|---|---|---|
| MD payı | %73–94 | %64 | %15 | %0 |
| ML payı | %2–22 | %30 | %75 | %85–93 |

Önceden seçilen bölünme tam bu geçişi kesiyor. Bu yüzden ana sınama tek bir tür döneminin içine taşındı:
- **ML dönemi (ana):** K = 2012–2018 (7,0 yıl), S = 2019–2026 (7,7 yıl).
- **MD dönemi (ikinci denetim):** K = 1998–2003, S = 2004–2009 (6'şar yıl).

Önceden seçilen bölünmenin sonuçları "karışık" etiketiyle `sonuc.json`'da duruyor (§5).

Tür bileşimi homojen dönemler içinde büyük ölçüde sabit. ML dönemi, Türkiye M ≥ Mc: ML %89 → %86. MD dönemi: MD %87 → %84. M ≥ 4,0'da ise MD döneminde ML payı %8'den %21'e çıkıyor.

### 1.2 Mc notu

Uygulamanın Mc'si (en büyük eğrilik + 0,2) her dönemde 3,2. Bu değer büyük olasılıkla katalogun alt kesim sınırını (M ≈ 3,0) yansıtıyor, gerçek tamlığı değil. M ≥ 3,2'deki sonuçlar algılama değişimlerinden etkileniyor (§2, §3). Bu yüzden yorum M ≥ 4,0'a dayanıyor.

## 2. Öngörü başarısı (Model 1, GK74 açık, ham büyüklük)

Hücrelerde: gözlenen / beklenen, hız oranı [%95], p.

| Eşik | Türkiye ML (2012–18 → 2019–) | Marmara ML | Türkiye MD (1998–2003 → 2004–09) | Marmara MD |
|---|---|---|---|---|
| M ≥ 3,2 | 1985 / 2273; 0,87 [0,82–0,93]; p = 2e−5 | 119 / 152; 0,78; p = 0,053 | 4030 / 2101; 1,92; p = 4e−136 | 160 / 164; 0,98; p = 0,82 |
| M ≥ 4,0 | **526 / 430; 1,22 [1,07–1,40]; p = 0,003** | 36 / 30; 1,21; p = 0,53 | 317 / 306; 1,04 [0,88–1,22]; p = 0,69 | 14 / 23; 0,61; p = 0,14 |
| M ≥ 4,5 | **178 / 127; 1,41; p = 0,004** | 10 / 10; 1,01; p = 1,00 | 106 / 103; 1,03; p = 0,89 | 5 / 14; 0,36; p = 0,041 |
| M ≥ 5,0 | **62 / 37; 1,66; p = 0,018** | 4 / 2; 1,82; p = 0,69 | 26 / 23; 1,13; p = 0,78 | 0 / 4; p = 0,062 |
| M ≥ 5,5 | **24 / 4; 5,45; p = 0,0003** | 3 / 0; p = 0,25 | 5 / 8; 0,62; p = 0,42 | 0 / 1; p = 0,50 |
| M ≥ 6,0 | 10 / 2; 4,54; p = 0,041 | 2 / 0; p = 0,50 | 0 / 2; p = 0,25 | 0 / 1; p = 0,50 |

**Okuma:**
- **M ≥ 4,0 ve üstü, üç bölge–dönem birleşiminde** (Marmara ML, Türkiye MD, Marmara MD): 15 testin 14'ünde p > 0,05. Tek istisna Marmara MD, M ≥ 4,5 (p = 0,041). On beş testte beklenen yanlış alarm sayısı ≈ 0,75, yani bu sonuç şansla uyumlu. Sabit hızlı Poisson modeli bu üç durumda bağımsız dönemin sayılarını belirsizlik sınırları içinde öngörüyor.
- **Türkiye ML döneminde** model M ≥ 4,0–5,5'te gözlenenin altında kalıyor (oran 1,2–5,5). Sınama dönemi Şubat 2023 Kahramanmaraş dizisini (Mw 7,8 ve 7,5) içeriyor.
- **Sonradan yapılan duyarlılık hesabı** (`sonradan_2023.js`, önceden sabitlenmedi): 2023 yılı çıkarılınca GK74 ile M ≥ 4,0 / 4,5 / 5,0'da oran 1,08 / 1,14 / 1,35, p = 0,30 / 0,30 / 0,21, yani uyumlu. M ≥ 5,5'te uyumsuzluk sürüyor (3,8 beklenen, 18 gözlenen; p = 0,002); kurma döneminde yalnızca 4 olay var. Bu sonuç, 2023 dizisinin GK74 ile tam ayıklanamadığını (uzun kırılma) düşündürüyor, ama sonradan seçildiği için kanıt değil, yorumdur.
- **M ≥ 3,2'de** her yerde büyük sapmalar var. Örneğin Türkiye MD'de sayı 1,92 katına çıkıyor ve dağılım testi de bu dönemde artan bir eğilim gösteriyor (§3). Bunlar ağın algılama değişimiyle uyumlu; Mc = 3,2 sınama için güvenilir bir eşik değil.
- **Scordilis dönüşümü** sonuçları değiştirmiyor (ML Türkiye GK74 M ≥ 4,0: 1,22, p = 0,002). Homojen tür dönemleri içinde ölçek dönüşümü ikincil kalıyor.

**Model 2 (G–R uzatması):**
- Marmara'da ve Türkiye MD'de GK74 ile çoğunlukla uyumlu (p 0,05–0,96).
- Türkiye ML'de ve karışık bölünmede sık sık başarısız. Başarısızlığın önemli bir kısmı kurma döneminin kendi içinde de görülüyor: tek b'li G–R, karma türlü büyüklük dağılımını (MD/ML küçük, mb/Mw büyük) iyi temsil etmiyor. Örneğin karışık bölünmede, GK74 + Scordilis ile M ≥ 4,5 için G–R kurma döneminde gözlenenin yaklaşık yarısını veriyor. Bu bir zamansal değişimden çok model yanlış belirlemesi.

## 3. Poisson varsayımı: yıllık sayıların dağılımı

Varyans/ortalama oranı ve p (χ², üst kuyruk). Yıl sayıları: ML dönemlerinde 7, MD dönemlerinde 6. **Bu kadar az yılla testin gücü düşük:** "Poisson'la uyumlu" sonucu, varsayımın doğru olduğunu göstermez.

| Bölge, katalog | Dönem | M ≥ 4,0 | M ≥ 4,5 |
|---|---|---|---|
| Türkiye, GK74 | 2012–2018 | 1,88 (p = 0,080) | 1,92 (p = 0,073) |
| Türkiye, GK74 | 2019–2025 | **7,94 (p = 1e−8)** | **6,50 (p = 7e−7)** |
| Türkiye, GK74 | 1998–2003 | 2,21 (p = 0,050) | 0,64 (p = 0,67) |
| Türkiye, GK74 | 2004–2009 | 1,65 (p = 0,14) | 1,76 (p = 0,12) |
| Marmara, GK74 | 2012–2018 / 2019–2025 | 0,73 / 1,19 (p = 0,63 / 0,31) | 1,48 / 1,13 |
| Marmara, GK74 | 1998–2003 | **4,95 (p = 0,0004)** | **8,00 (p = 2e−7)** |
| Marmara, GK74 | 2004–2009 | 0,97 (p = 0,43) | 2,12 (p = 0,060) |
| Türkiye, ham (karşılaştırma) | 2012–2018 / 2019–2025 | 18,6 / 186 | 9,0 / 71 |

**Okuma:**
- **GK74 kapalıyken** her yerde güçlü aşırı saçılma var (varyans/ortalama 4–700). Bunun nedenleri artçı kümelenmesi, eğilim ve algılama değişimidir; yalnızca biri değil.
- **GK74 açıkken, M ≥ 4,0–4,5'te**, büyük bir dizi içermeyen dönemlerde oran 0,6–2,2 ve p çoğunlukla > 0,05. Düşük güç sınırı içinde Poisson'la çelişmiyor.
- **Büyük dizi içeren dönemlerde** GK74 sonrasında da güçlü aşırı saçılma kalıyor: Türkiye 2019–2025 (2023 Kahramanmaraş) ve Marmara 1998–2003 (1999 İzmit ve Düzce). GK74'ün sabit uzay–zaman pencereleri, uzun kırılmalı büyük depremlerin artçılarını tam ayıklayamıyor. Kalan olayların bağımsız olduğu garanti edilmez.
- **Eğilim çıkarılmış Pearson χ²/sd** çoğu durumda ham orana yakın. Aşırı saçılmanın çoğu doğrusal eğilimle değil, tek yıllardaki sıçramalarla (diziler) açıklanıyor.

## 4. Zamanla değişen hız modeli (Model 3)

Kurma dönemi içinde anlamlı eğilim ("gerekçeli") bulunan 13 durumun 8'inde, eğilimli model sınama döneminde sabit modelden **daha kötü** öngörüyor (log-skor daha düşük). Örnekler:
- Türkiye ML, GK74, M ≥ 4,0: eğim −%5,2/yıl (K içinde p = 0,034); log-skor −127'ye karşı sabit model −55.
- Türkiye ML, ham, M ≥ 3,2: eğim −%8,3/yıl.

Eğilimli modelin daha iyi olduğu beş durum:
- **Marmara MD, ham, üç eşik:** İzmit artçı sönümü sürüyor.
- **Türkiye MD, M ≥ 3,2, ham ve GK74:** algılama artışı sürüyor.

Yani kurma dönemindeki eğilimler çoğunlukla geçici süreçlerden (artçı sönümü, ağ değişimi) geliyor. Bu süreçler sınama döneminde de sürüyorsa eğilimli model kazanıyor, ama bu ileriye güvenle taşınabilecek bir hız modeli sağlamıyor. GK74 açıkken M ≥ 4,0'da eğilim yalnızca Türkiye ML'de gerekçeli ve orada sabit modelden belirgin biçimde kötü. Model 3'ü tercih etmek için bir gerekçe bulunmadı.

## 5. İkincil sınamalar

**Önceden seçilen karışık bölünme (EMSC 1998–2011 → 2012–2026, MD → ML geçişini kesiyor)**, Türkiye:
- M ≥ 3,2'de sayı düşüyor (oran 0,74; GK74 ile 0,54).
- M ≥ 4,0'da sayı artıyor (1,57; GK74 ile 1,18).

Büyüklüğe göre zıt yönlü değişim, tür ve ölçek geçişiyle uyumlu; fiziksel bir yorum yapılamaz.

**Katalog sınırı (ISC → EMSC, 1998)**, Türkiye, GK74:

| Kurma → sınama | Eşik | Ham büyüklük | Scordilis |
|---|---|---|---|
| ISC 1990–1997 → EMSC 1998– | M ≥ 4,0 | 1,59; p = 2e−14 | 1,26; p = 2e−5 |
| ISC 1990–1997 → EMSC 1998– | M ≥ 4,5 | 1,82; p = 9e−8 | 1,36; p = 6e−5 |
| ISC 1971–1997 → EMSC 1998– | M ≥ 5,0 | 1,56; p = 0,001 | 1,06; p = 0,54 |
| ISC 1971–1997 → EMSC 1998– | M ≥ 5,5 | 1,38; p = 0,20 | 1,45; p = 0,080 |

Sınırı kesen sınamada artış dönüşüme çok duyarlı. M ≥ 5,0'da Scordilis ile kayboluyor; M ≥ 4,0–4,5'te azalıyor ama sürüyor. Bu, ISC–EMSC araştırmasındaki bulguyla tutarlı: öngörü hatası model başarısızlığının kanıtı sayılamaz; büyüklük ölçeği ve algılama farkı olası açıklamalardır.

## 6. Sonuçlar

1. **Öngörü:** Homojen bir büyüklük türü dönemi içinde, GK74 açık ve M ≥ 4,0 iken sabit hızlı Poisson modeli, büyük dizi içermeyen bağımsız dönemlerin sayılarını belirsizlik sınırları içinde öngörüyor (üç bölge–dönemde 15 testin 14'ü). Sınama dönemi 2023 Kahramanmaraş gibi büyük bir dizi içerdiğinde model gözlenenin altında kalıyor; büyük bir kısmı GK74'ün bu diziyi tam ayıklayamamasıyla açıklanabiliyor (sonradan duyarlılık).
2. **Poisson varsayımı:** GK74 açıkken M ≥ 4,0'da, büyük dizi içermeyen dönemlerde yıllık sayılar Poisson'la çelişmiyor (düşük güç: 6–7 yıl). Büyük dizi içeren dönemlerde GK74 sonrasında da aşırı saçılma var. Bu, a(t) raporundaki "kümelenmede güven aralıkları dar kalır" bulgusuyla tutarlı. EQ-Live'daki Poisson olasılıkları büyük dizi dönemlerini kapsayan pencerelerde iyimser kalabilir.
3. **Katalog homojenliği:** EMSC'nin kendi içinde de 2010–2012'de MD → ML geçişi var. Dönemler arası karşılaştırmalarda (a(t), b(t), Poisson) bu geçiş, 1998 ISC → EMSC sınırı kadar önemli bir sınırlama. Mc uyarısı tür geçişini yakalamaz; ayrı bir "büyüklük türü geçişi" uyarısı düşünülebilir (öneri).
4. **Model seçimi:** Kurma dönemindeki eğilimler ileriye taşınamıyor; zamanla değişen hız modelini tercih etmek için gerekçe yok. Tek b'li G–R uzatması karma türlü katalogda kendi kurma döneminde bile uymayabiliyor.

## 7. Sınırlar

- Yalnızca iki bölge ve iki homojen dönem incelendi. ML dönemi bölünmesi (7 + 7,7 yıl) ve MD dönemi (6 + 6 yıl) kısa; büyük eşiklerde olay sayıları çok az.
- Çoklu test: tüm tablolarda onlarca p değeri var. Tek tek anlamlılıklar keşifseldir; düzeltme uygulanmadı, yorum örüntülere dayanıyor.
- Mc = 3,2 katalogun kesim sınırı olabilir; M ≥ 3,2 sonuçları algılama değişimine duyarlı.
- 2023 duyarlılık hesabı sonradan yapıldı ve yalnızca yorum içindir.
- GK74 tek ayıklama yöntemi olarak kullanıldı; uzun kırılmalı depremlerde yetersiz kaldığı görülüyor. Başka yöntemlerle (ör. Reasenberg, ETAS tabanlı) karşılaştırma bu çalışmanın kapsamı dışında.
