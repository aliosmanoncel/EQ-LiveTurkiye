# GK74 ile Reasenberg arasındaki sınıflandırma farkları — ilk bilimsel inceleme

**Statü:** koşullu algoritmik karşılaştırma (1998–2026 EMSC, M ≥ 3,0, karışık büyüklük ölçeği ML/MD/mb/Mw). Katalog tamlık doğrulaması, deprem tehlikesi değerlendirmesi ya da tahmin değildir.
**Referans:** `main` @ `be61bae` (PR #3); katalog sha256 `bd303aa3…545b`; betik `rb_gk74_differences.py` (sha256 `9375294d…7bb9`). Araştırma dalı `research/rb-gk74-differences`; `main` ve canlı site değişmedi.

Araştırma sorusu: *İki algoritma arasındaki sınıflandırma farkları hangi bölgelerde, hangi zaman aralıklarında ve hangi sismik koşullarda yoğunlaşıyor?*

## 1. Fark gruplarının tanımı (yön önemli)

| Grup | GK74 | Reasenberg (zmap) | Olay |
|---|---|---|---|
| **R_only** | artçı (çıkarılır) | bağımsız | **30 976** — 29 893 tekil, 1 083 küme temsilcisi |
| **GK_only** | bağımsız | bağımlı | **334** — 235 öncü, 99 artçı |

Önceki yorum notunda geçen "Reasenberg'in kümeye aldığı, GK74'ün bağımsız bıraktığı 30 976 olay" ifadesi **ters**tir. 30 976 olay GK74'ün artçı saydığı, Reasenberg'in hiçbir kümeye bağlamadığı (çoğu tekil) olaylardır. Bu olaylar öncü değildir; GK74 tanımı gereği hepsi daha büyük bir olayın **sonrasında** ve onun penceresinde yer alır. Reasenberg'in öncü sınıfı küçük grupta (GK_only) görünür.

Denetimler: projedeki `decluster_gk74.py` döngüsü aynen tekrarlanarak her GK74 artçısı için pencereyi açan olay ("GK74 ebeveyni") kaydedildi; bayraklar projeyle birebir aynı. Grup sayıları site ürünüyle (`data/reasenberg_gk74_emsc.json`) birebir aynı.

## 2. Mekanizma (tanısal)

Her R_only olayı, GK74 ebeveyninden Reasenberg'in **doğrudan** bağlantı ölçütüne göre sınıflandı (zincirleme bağlantı yok sayıldı):

| Mekanizma | Tanım | Olay | Pay |
|---|---|---|---|
| far | uzaklık > 10·r(M_ebeveyn) — Reasenberg etkileşim yarıçapı dışı | 20 430 | %66 |
| late | yarıçap içinde, ama ebeveynden 10 günden (τ_max) sonra | 7 967 | %26 |
| window | yarıçap ve 10 gün içinde, ama ileri bakış süresi τ yetmedi | 2 579 | %8 |

Ebeveyn büyüklüğüne göre (`fig_mekanizma.png`):

| GK74 ebeveyni | far | late | window |
|---|---|---|---|
| M 3,0–3,9 | 8 467 | 347 | 752 |
| M 4,0–4,9 | 7 765 | 1 489 | 715 |
| M 5,0–5,9 | 3 168 | 1 997 | 443 |
| M ≥ 6,0 | 1 030 | 4 134 | 669 |

**Yorum:**
- **Küçük ve orta büyüklükte ebeveynlerde fark mekânsaldır.** M3 için GK74 D(M) ≈ 22 km, Reasenberg 10·r(M) ≈ 1,7 km; M5 için 40 km ile 11 km. GK74 penceresi Reasenberg yarıçapından 3–13 kat geniştir. R_only olaylarının ortanca uzaklığı 15,9 km'dir.
- **Büyük ebeveynlerde (M ≥ 6) fark zamansaldır.** Yarıçaplar M ≈ 7'de eşitlenir (`fig_mekanizma.png`, sağ). Ama GK74'ün zaman penceresi M7 için ≈ 900 gündür; Reasenberg'in ileri bakış süresi ise en çok 10 gün ve araya 10 günden uzun boşluk giren artçı dizileri kümeden kopar. R_only olaylarının ortanca zaman farkı 22 gün, %90'ı 189 güne kadardır.
- R_only olaylarının %18,8'i M ≥ 6 ebeveynlerden gelir; geri kalanı toplam 7 472 farklı GK74 ebeveyninin küçük pencerelerine dağılmıştır. Fark tek tek büyük dizilerin değil, **bütün kataloğa yayılmış bir pencere-tanımı farkının** sonucudur.

## 3. Mekânsal dağılım (`fig_mekansal.png`)

- **Sayıca** en yoğun hücreler büyük dizilerin bulunduğu yerlerdir: Van (2011), Kahramanmaraş (2023), Elazığ–Bingöl, Ege adaları ve Girit–Helen yayı.
- **Pay olarak** en yüksek değerler (hücrede %50–70) Helen yayı ve Girit güneyi, Güneybatı Anadolu–Rodos, Kahramanmaraş–Hatay zonu ve Düzce–Bolu kesimindedir. Batı Anadolu iç kesimi ve Orta Anadolu'da pay düşüktür.
- Katalog sınırına yakınlık belirgin bir etki göstermez: sınıra < 25 km olaylarda pay %32,3, > 100 km'de %38,5 (site ürünü).

## 4. Zamansal dağılım (`fig_zamansal.png`)

- R_only payı yıllara göre %20–50 arasında değişir.
- Pay, büyük dizilerin hemen ardından yükselir: 1999–2000 (İzmit–Düzce, %49), 2012 (Van 2011 sonrası, %45), 2023–2024 (Kahramanmaraş, %50 ve %44).
- 2011'de pay düşüktür (%29): Van ana şokunun ilk aylarındaki yoğun artçılar Reasenberg'de de kümeye bağlanır; GK74 ile Reasenberg'in ayrılması dizinin **sonraki aylarında** olur.
- 2025'te pay en düşük değerdedir (%20). Bu yılın yoğun etkinliğinin büyük kısmını iki yöntem birlikte kümeliyor; nedeni ayrıca incelenmeli.

## 5. En çok R_only olayı üreten GK74 pencereleri

| Ebeveyn (UTC) | M (tür) | R_only | Baskın mekanizma | GK74 D / T | Reasenberg 10·r |
|---|---|---|---|---|---|
| 2011-10-23 Van | 7,3 (Ms) | 1 129 | late 981 | 77 km / 939 g | 92 km |
| 2023-02-06 10:24 Elbistan | 7,5 (Mw) | 600 | late 575 | 82 km / 953 g | 110 km |
| 2023-02-06 01:17 Pazarcık | 7,8 (Mw) | 450 | late 359 | 89 km / 974 g | 145 km |
| 2009-07-01 Girit güneyi | 6,1 (mb) | 311 | far 126 / late 139 | 55 km / 566 g | 30 km |
| 2020-10-30 Sisam | 7,0 (Mw) | 285 | late 227 | 71 km / 918 g | 69 km |
| 1999-08-17 İzmit | **6,3 (mb)** | 280 | far 166 | 58 km / 726 g | 36 km |
| 2008-07-15 Rodos | 6,4 (mb) | 237 | far 135 | 60 km / 822 g | 40 km |
| 2003-05-01 Bingöl | 5,6 (mb) | 214 | late 104 | 48 km / 303 g | 19 km |
| 2017-11-12 İran–Irak sınırı | 7,3 (Mw) | 209 | late 188 | 77 km / 939 g | 92 km |
| 2020-05-02 Girit güneyi | 6,6 (Mw) | 203 | late 139 | 63 km / 892 g | 48 km |

## 6. Büyüklük ölçeğinin etkisi (önemli sınırlılık)

1999 İzmit depremi katalogda **mb 6,3** olarak yer alır; Mw ≈ 7,6'dır. mb büyük depremlerde doyduğu için her iki yöntemin penceresi de küçülür. Reasenberg'in yarıçapı 10·r(6,3) = 36 km olur; Mw 7,6 için bu değer ≈ 120 km'dir. Bu yüzden İzmit artçılarının çoğu "far" mekanizmasıyla R_only grubuna düşer. 2008 Rodos ve 2009 Girit (mb) için de aynı durum geçerlidir.

Dolayısıyla farkların bir bölümü algoritmadan değil, **büyüklük ölçeğinden** kaynaklanır. Bu bulgu, EQ-Live'daki otoriter Mw tablosunun (WORKFLOW 1E, `data/mw_authority.json`) Reasenberg karşılaştırmasında da kullanılmasının değerlendirilmesini gerektirir. Bu bir yöntem kararıdır ve burada uygulanmadı.

## 7. Sınırlılıklar

- Mekanizma sınıflaması tanısaldır: yalnız GK74 ebeveyni ile olay arasındaki doğrudan bağlantıyı değerlendirir; Reasenberg'in zincirleme bağlantıları ve nedensel τ hesabı kaba biçimde temsil edilir.
- "GK74 ebeveyni" GK74 pencere kuralının kaydıdır; fiziksel bir ana şok–artçı ilişkisi iddiası değildir.
- Derinlikler kayıtlı haliyle kullanıldı (Reasenberg hiposantral mesafe kullanır, GK74 episantral); `err = derr = 0`.
- Tek eşik (M ≥ 3,0) ve karışık büyüklük ölçeği kullanıldı. Mc duyarlılığı ayrı bir çalışmadır.

## 8. Sonraki adımlar (öneri, karar sizde)

1. Otoriter Mw'nin (1E) büyük olaylarda Reasenberg ve GK74 girdisine uygulanmasıyla farkın ne kadar değiştiğinin ölçülmesi.
2. 2025 düşük payının nedeninin incelenmesi.
3. Mc duyarlılığı (M ≥ 3,5 / 4,0) — ayrı PR.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `rb_gk74_differences.py` | Analiz betiği (yeniden üretilebilir; depo kökünden çalıştırılır) |
| `differences_events.csv` | 31 310 olay: grup, sınıflar, GK74 ebeveyni, uzaklık, zaman farkı, mekanizma |
| `summary.json` | Tüm sayılar ve dağılımlar |
| `fig_mekansal.png`, `fig_zamansal.png`, `fig_mekanizma.png` | Şekiller |
