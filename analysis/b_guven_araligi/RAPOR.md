# b-değeri güven aralığı yöntemlerinin karşılaştırılması (2026-10-21)

**Durum:** yalnız analiz. `main`, üretim kodu ve canlı site değişmedi. b kestiricisi her yöntemde EQ-Live'daki ile aynıdır; yalnız güven aralıkları karşılaştırılır. b(t) pencereleri ve Weichert belirsizliği kapsam dışındadır.

## 1. Karşılaştırılan yöntemler

Ortak kestirici (EQ-Live `computeBvalue`): b̂ = log₁₀e / (M̄ − M_c + ΔM/2). Sürekli büyüklüklerde ΔM = 0 alınır.

| Kod | Yöntem | Formül | Kaynak |
|---|---|---|---|
| `normal` | EQ-Live'daki mevcut hesap | b̂ ± 1,96·b̂/√N | `bConfidence95`; Aki (1965) |
| `chi2` | Kesin χ² aralığı | [q_l/(2N)·b̂, q_u/(2N)·b̂], q: χ²₂ₙ'nin %2,5 ve %97,5 yüzdelikleri | Utsu (1966); Shi & Bolt (1982); Tinti & Mulargia (1987) Eş. 4a–4b |
| `tm` | Tinti–Mulargia, gruplanmış büyüklükler | z = (M̄ − M_c)/ΔM, r = N·z; I_{p_l}(r, N) = α/2 (r = 0 → p_l = 0); I_{q_u}(N, r+1) = α/2, p_u = 1 − q_u; β = −ln p / ΔM | Tinti & Mulargia (1987) Eş. 9–21, 19 |
| `tm_ml` | Aynı makalenin asimptotik yaklaşımı (yalnız karşılaştırma) | p̂ ± 1,96·(1 − p̂)√(p̂/N) | Eş. 23 |

`tm` aralığı b̂'ye değil, yalnız N ve r'ye bağlıdır. r = 0 olduğunda (bütün olaylar en küçük sınıfta) üst uç sonsuzdur; bu bir hata değil, verinin bilgi taşımadığını gösterir.

## 2. Uygulamanın doğrulanması (`test_bci.py`, 15/0)

1. **İki bağımsız yol:** Eş. 21'deki eksik beta fonksiyonuyla bulunan uçlar, Eş. 18'deki negatif binom dağılımından doğrudan kök bularak bulunanlarla aynıdır (49 (N, r) çifti; en büyük fark 4,9·10⁻¹³).
2. **N = 1 kapalı biçimi:** p_l = (α/2)^(1/r), p_u = (1 − α/2)^(1/(r+1)). Üç r için birebir.
3. **Büyük N:** Kesin uçlar Eş. 23'e yakınsar (N = 20.000'de fark < 0,001).
4. **Şekil 2a (N = 10, ΔM = 0,1):** Hesaplanan β uçları, şekilden gözle okunan değerlerle okuma hassasiyeti içinde uyumludur: z = 3 için 1,36–5,00 (şekil ≈ 1,3–4,85), z = 10 için 0,45–1,64 (≈ 0,5–1,68). Uçlar z ile tekdüze azalır ve kesin uçlar ML uçlarının üstündedir; ikisi de şekildeki gibidir. Bu denetim nicel değil, görseldir.
5. **χ² denetimi:** P(q_l ≤ χ²₂₀ ≤ q_u) = 0,95.
6. **EQ-Live ile birebirlik:** Python'daki `normal` yöntemi ve kestirici, `index.html`'deki `computeBvalue` ve `bConfidence95` fonksiyonlarıyla (node ile çalıştırıldı) birebir aynı sonucu verir (4 örnek).

## 3. Monte Carlo tasarımı (`mc_kapsama.py`)

- Örneklemler: gerçek b'si bilinen ideal G–R örneklemleri, m = m₀ + Üstel(β), β = b·ln 10.
- Senaryolar: sürekli (yuvarlama yok), ΔM = 0,1 ve ΔM = 0,5. Gruplanmış senaryoda büyüklük = M_c + kΔM, k = ⌊(m − m₀)/ΔM⌋.
- Parametreler: b ∈ {0,7; 1,0; 1,5}; N ∈ {4, 10, 20, 30, 40, 49, 100}.
- Her hücrede 20.000 tekrar, tohum 20261021. Kapsamanın Monte Carlo standart hatası ≈ 0,0015 (Wilson %95 aralıkları JSON'da).
- Tekrarlanabilirlik: ikinci tohumla (777) 210 hücrenin yalnız 1'inde fark 3 standart hatayı aştı; o hücre de karar için kullanılmayan `tm_ml` yöntemine ait.
- Ölçütler:
  - kapsama;
  - iki yönlü kaçırma: gerçek b aralığın altında / üstünde kalma (her biri ideal olarak %2,5);
  - göreli genişlik (ortanca, b'ye bölünmüş);
  - asimetri (ortanca üst kol / alt kol);
  - sonsuz üst uç sayısı;
  - kestirici yanlılığı.

## 4. Sonuçlar (b = 1,0; parantez içinde gerçek b'nin aralığın altında / üstünde kaldığı oran, %)

**ΔM = 0,1 (EQ-Live'ın olağan büyüklük ızgarası)**

| N | normal | chi2 | tm | göreli genişlik (chi2) | tm üst uç ∞ (%) |
|---|---|---|---|---|---|
| 4 | 0,957 (0,0 / 4,3) | 0,957 (2,0 / 2,3) | 0,957 (2,0 / 2,3) | 2,08 | 0,2 |
| 10 | 0,955 (0,5 / 4,0) | 0,954 (2,2 / 2,4) | 0,954 (2,2 / 2,4) | 1,27 | 0 |
| 20 | 0,951 (0,9 / 4,0) | 0,948 (2,4 / 2,8) | 0,951 (2,4 / 2,5) | 0,88 | 0 |
| 30 | 0,952 (1,1 / 3,7) | 0,951 (2,1 / 2,8) | 0,950 (2,4 / 2,6) | 0,72 | 0 |
| 40 | 0,952 (1,4 / 3,4) | 0,948 (2,5 / 2,7) | 0,950 (2,5 / 2,5) | 0,62 | 0 |
| 49 | 0,953 (1,4 / 3,3) | 0,953 (2,1 / 2,6) | 0,954 (2,3 / 2,3) | 0,56 | 0 |
| 100 | 0,951 (1,6 / 3,3) | 0,951 (2,2 / 2,8) | 0,952 (2,3 / 2,5) | 0,39 | 0 |

**Sürekli büyüklükler:** `normal` 0,949–0,957; kaçırmalar 0,0–2,0 / 3,0–4,7. `chi2` 0,947–0,953; kaçırmalar 2,3–2,6 / 2,3–2,8. Sonuçlar b = 0,7–1,5 aralığında benzerdir.

**ΔM = 0,5 (kaba gruplama)**

| N | normal | chi2 | tm | tm üst uç ∞ (%) |
|---|---|---|---|---|
| 4 | 0,931 (0,0 / 6,9) | 0,967 (0,0 / 3,3) | 0,985 (0,0 / 1,5) | 22,5 |
| 10 | 0,953 (0,0 / 4,7) | 0,953 (0,0 / 4,7) | 0,963 (2,3 / 1,5) | 2,3 |
| 20 | 0,915 (0,0 / 8,5) | 0,942 (0,1 / 5,7) | 0,962 (1,5 / 2,3) | 0,1 |
| 49 | 0,877 (0,0 / 12,2) | 0,907 (0,0 / 9,3) | 0,965 (1,6 / 1,9) | 0 |
| 100 | 0,816 (0,0 / 18,4) | 0,844 (0,0 / 15,6) | 0,957 (2,0 / 2,3) | 0 |

ΔM = 0,5'te bütün b değerleri ve N < 50 üzerinden kapsama: `normal` 0,62–0,96, `chi2` 0,72–0,98, `tm` 0,95–0,99. b = 1,5 ve N = 100'de `normal` ile `chi2` 0,35'e düşer.

## 5. Bulgular

1. **Toplam kapsama yanıltıcı olabilir.** ΔM = 0,1'de üç yöntemin toplam kapsaması da nominal %95'e yakındır (0,946–0,966). Ancak `normal` aralık simetrik olduğu için hataları tek yönde yığar: gerçek b'nin aralığın üstünde kalma oranı %3,2–5,0, altında kalma oranı %0–1,8'dir. Yani mevcut hesap, gerçek b'nin tahminden **büyük** olma olasılığını sistematik olarak küçük gösterir. Bu dengesizlik N = 100'de de sürer (%1,6 / %3,3), N küçüldükçe büyür.
2. **ΔM = 0,1'de χ² yeterlidir; Tinti–Mulargia ek bir kazanç sağlamaz.** İkisi de hataları iki yöne dengeli dağıtır (%2–2,8). Kapsamaları Monte Carlo belirsizliği içinde aynıdır; `tm` ortanca genişlikte en fazla %8 daha geniştir ve N = 4'te en çok %0,8 olasılıkla sonsuz üst uç verir. Önceden öngörülen "β·ΔM küçükken iki yöntem yakın çıkar" beklentisi doğrulandı.
3. **ΔM = 0,5'te yalnız Tinti–Mulargia güvenilirdir.** `tm` bütün N ve b için 0,95–0,99 kapsar; biraz tutucudur, çünkü r tam sayıdır. `normal` ve `chi2` ise N arttıkça kötüleşir. Bunun nedeni aralık yöntemi değil, kestiricidir: Utsu'nun ΔM/2 düzeltmesi kaba gruplamada yetersiz kalır. Ortalama b̂/b, N = 100'de b = 1,0 için 0,91, b = 1,5 için 0,81'dir. `tm` aralığı b̂'ye dayanmadığı için bu yanlılıktan etkilenmez.
4. **Çok küçük N'de hiçbir yöntem bilgi üretmez.** N = 4'te %95 aralığının genişliği b'nin yaklaşık 2 katıdır. ΔM = 0,5'te `tm` üst ucu olayların %22'sinde sonsuzdur. Doğru yöntem belirsizliği gidermez, ama küçük görünmesini engeller.
5. **Eş. 23 (`tm_ml`) küçük N ve kaba ΔM'de kullanılmamalıdır.** Kapsaması 0,54'e kadar düşer.
6. **Kestirici yanlılığı (bilgi amaçlı).** ΔM ≤ 0,1'de b̂/b, N = 4'te 1,29–1,34, N = 20'de 1,04–1,05, N = 100'de 1,00–1,01'dir (Aki kestiricisinin bilinen küçük örneklem yanlılığı; yaklaşık N/(N−1)). Kestirici bu çalışmada değiştirilmedi.

## 5a. Sonuçların EQ-Live açısından anlamı: hatanın yönü

`normal` aralığın hatası rastgele değildir. Gerçek b, aralığın **üstünde** kalır; bu da çoğunlukla b̂'nin düşük çıktığı örneklemlerde olur. Aralık simetrik olduğu ve genişliği b̂ ile orantılı olduğu için, düşük b̂'de aralık hem aşağı kayar hem daralır. Sonuç: mevcut hesap, düşük b anomalilerini olduğundan **daha kesin** gösterir. EQ-Live'da düşük b değerleri olası yüksek gerilimle ilişkilendirilerek yorumlandığı için, hatanın yönü tam da yorumun hassas olduğu yöne düşer. χ² aralığı üst kolu uzatarak (asimetri 1,1–1,6) bunu düzeltir.

## 5b. "İyi koşulda değiştirme, kötü koşulda daha güvenilir olanı kullan, yetersizse gizleme" ilkesinin bu sonuçlara uygulanması

İlke yerindedir. Ancak simülasyon, iyi ve kötü koşulların nerede olduğu konusundaki iki çalışma hipotezini düzeltmektedir:

1. **Belirleyici eksen yalnız N değil; asıl eksen gruplama (ΔM) ve hatanın yönüdür.** ΔM = 0,1'de `normal` yöntemin toplam kapsaması N = 4'te bile nominaldir (0,957). Buna karşılık ΔM = 0,5'te N büyüdükçe kötüleşir (N = 100'de 0,82; b = 1,5'te 0,35). "N > 50 iyi, N < 10 kötü" ayrımı bu verilerle desteklenmez.
2. **ΔM = 0,1'de "iyi koşul" tam olarak sağlanmıyor.** Toplam kapsama iyi, ama hatalar tek yönde (5a). Bu dengesizlik N = 100'de de vardır (%1,6 / %3,3) ve N küçüldükçe büyür.

İlkeyi bu bulgulara uygularsak:
- **İyi koşul** (ΔM ≤ 0,1, toplam kapsama yeterli): Değişiklik zorunlu değildir. χ²'ye geçmek kapsamayı artırmaz, yalnız hata yönünü dengeler; bedeli tek satırlık bir formül değişikliğidir. Bu bir tercih konusudur, can simidi değildir.
- **Kötü koşul** (ΔM ≥ 0,5): Daha güvenilir bir seçenek vardır (`tm`, kapsama 0,95–0,99). Kullanılmalıdır.
- **Yetersiz koşul** (r = 0 ya da çok küçük N): `tm` üst ucu sonsuz çıkar, genişlik b'nin 1,3–2 katıdır. Bu gizlenmemeli, "üst sınır yok / çok az olay" olarak gösterilmelidir.

N'ye bağlı bir geçiş (örneğin 50'de) bu veride gerekmez. ΔM'ye bağlı bir seçim gerekir. Süreksiz geçiş de, eşik çevresinde aynı veriye iki farklı aralık verme sorununu doğurur.

## 6. Karar için öneri (üretim onayı ayrıca gerekir)

| Koşul | Öneri | Gerekçe |
|---|---|---|
| ΔM ≤ 0,1 (EQ-Live varsayılanı), bütün N | `normal` yerine `chi2` | Kapsama aynı, hatalar iki yöne dengeli; kapalı biçimli tek satırlık hesap. 50'de bir geçiş eşiği gerekmez; bu süreksizliği de önler |
| ΔM ≥ 0,5 ya da kaba ızgara | `tm` | `normal` ve `chi2` kapsaması 0,35'e kadar düşer |
| r = 0 (bütün olaylar en küçük sınıfta) | Üst uç "yok (sınırsız)" olarak gösterilsin | Sessizce `normal`'e dönülmesin |
| N çok küçük (ör. N < 10) | Aralık gösterilsin, ayrıca "çok az olay" uyarısı | Genişlik ≈ 1,3–2 × b |
| ΔM ≥ 0,5'te b̂ | Ayrı iş: kestiricinin kendisi yanlı (Tinti & Mulargia Eş. 14 kestiricisi değerlendirilebilir) | Bu çalışmanın kapsamı dışında |

## 7. Sınırlar

- Sentetik örneklemler ideal G–R dağılımındadır: eksik tamlık, büyüklük ölçüm hatası, ölçek karışımı ve artçı kümelenmesi yoktur. Gerçek kataloglarda bütün yöntemlerin kapsaması daha düşük olabilir; bu test yalnız aralık formülünün kendisini sınar.
- Kapsama yalnız α = 0,05 için ölçüldü.
- Şekil 2a karşılaştırması görseldir.
- EQ-Live'da dönüştürülmüş büyüklüklerde ΔM, `mcScale` ile ızgara dışı bir değer alabilir (Mc–ızgara düzeltmesi). Bu durum ayrıca sınanmadı.

## 8. Yeniden üretim

```
python3 analysis/b_guven_araligi/test_bci.py           # 15/0
python3 analysis/b_guven_araligi/mc_kapsama.py 20000 20261021   # out/mc_kapsama.json (≈ 3 s)
```

Ortam: Python 3, NumPy 2.5.3, SciPy 1.18.1. Normal yöntemin denetimi için Node.js ve depo kökündeki `index.html` gerekir.

## 9. Ek: ΔM = 0,2 ve 0,3 (eşik gerekip gerekmediğinin sınanması)

Aynı tasarım, tohum 20261022, çıktı `out/mc_kapsama_dM02_03.json` (komut: `python3 mc_kapsama.py 20000 20261022 0.2,0.3 out/mc_kapsama_dM02_03.json`).

χ² aralığının bozulması ΔM'ye tek başına değil, **β·ΔM çarpımına** bağlıdır (β = b·ln 10). Bunun kanıtı şudur: aynı β·ΔM değerini veren iki farklı (ΔM, b) çifti aynı sonucu verir. β·ΔM = 0,69'da (ΔM = 0,3 ile b = 1,0 ve ΔM = 0,2 ile b = 1,5) gerçek b'nin aralığın üstünde kalma oranı ikisinde de en çok %4,9'dur.

| β·ΔM | Örnek (ΔM, b) | chi2 kapsama (en düşük) | chi2: gerçek b aralığın üstünde (en çok) | tm kapsama (en düşük) | tm üst uç ∞, N ≥ 10 (en çok) |
|---|---|---|---|---|---|
| 0,16–0,35 | (0,1; 0,7–1,5), (0,2; 0,7) | 0,946–0,950 | %2,8–3,0 | 0,950 | %0 |
| 0,46–0,48 | (0,2; 1,0), (0,3; 0,7) | 0,947–0,952 | %3,4–3,5 | 0,951–0,953 | %0 |
| 0,69 | (0,3; 1,0), (0,2; 1,5) | 0,945 | %4,9 | 0,953–0,955 | %0,1 |
| 0,81 | (0,5; 0,7) | 0,932 | %6,6 | 0,950 | %0,3 |
| 1,04 | (0,3; 1,5) | 0,887 | %11,2 | 0,953 | %1,2 |
| 1,15 | (0,5; 1,0) | 0,844 | %15,6 | 0,957 | %2,3 |
| 1,73 | (0,5; 1,5) | 0,354 | %64,6 | 0,955 | %14,3 |

**Sonuç:**
- χ² aralığı β·ΔM ≲ 0,5 için yeterlidir. EQ-Live'ın olağan ızgarasında (ΔM = 0,1) bu koşul b ≲ 2,2'ye kadar sağlanır; yani pratikte her zaman. **Düzeltme (§12):** Bu sonuç N ≤ 100 için geçerlidir; N ≳ 2000'de ΔM = 0,1'de de geçerli değildir.
- Tinti–Mulargia bütün denenen koşullarda 0,95–0,99 kapsar.
- Bir yöntem seçimi gerekirse, ölçüt sabit bir ΔM eşiği değil, veriden hesaplanan b̂·ln10·ΔM olmalıdır. Bu da bir tahmindir; sınırda duyarlılık analizi gerekir.
- Uygulama notu: Tinti–Mulargia, büyüklüklerin tam olarak ΔM ızgarasında olmasını gerektirir (r tam sayı). EQ-Live'da dönüştürülmüş büyüklükler ızgara dışıdır (`mcScale`). Bu durumda χ² doğrudan uygulanabilir, Tinti–Mulargia ise yeniden sınıflama gerektirir.

## 10. Ek: b(t) için N = 50 penceresi (iki kademeli öneri için ön bilgi)

Bugün EQ-Live'da M ≥ Mc olay sayısı 100'ün altındaysa b(t) hiç hesaplanmaz ("N < 100 — kayan pencere b-değeri hesaplanamıyor"). N = 50 penceresinin ne kaybettirdiğini ölçmek için tek bir pencerede şu soru sınandı: %95 χ² aralığı, b₀ = 1,0 referansını ne sıklıkla dışarıda bırakır? (ΔM = 0,1; 20.000 tekrar; tohum 20261023; `bt_pencere.py`, `out/bt_pencere.json`.)

| Gerçek b | N = 50 | N = 100 |
|---|---|---|
| 0,6 | %95 | %100 |
| 0,7 | %74 | %95 |
| 0,8 | %39 | %64 |
| 0,9 | %13 | %21 |
| 1,0 (yanlış alarm) | %5,2 | %4,9 |
| 1,2 | %22 | %39 |
| %95 aralığın yarı genişliği (b = 1,0) | ±0,28 | ±0,20 |

**Yorum:**
- N = 50 penceresi tek başına yanlış alarm üretmez (%5).
- Ancak orta büyüklükteki değişimleri belirgin biçimde daha seyrek ayırt eder: b = 0,8'i yakalama oranı %39'dur (N = 100'de %64).
- Kayan pencere boyunca çok sayıda pencere incelendiğinde, rastlantısal "anomali" sayısı pencere sayısıyla artar. 5 olaylık adım, bilgi eklemeden pencere sayısını iki katına çıkarır.
- Bu nedenle ikinci kademe ancak ayrı etiketle, daha geniş aralıklarla ve yalnız N = 100'ün sağlanamadığı durumda gösterilmelidir.
- Bu bir üretim değişikliğidir; ayrı onay gerekir.

## 11. Üretim uygulaması (dal `b-ci-chi2`, 2026-10-25; `main`'e birleştirme ayrı onaya bağlı)

> **Not (aynı gün, §12):** Aşağıdaki seçim kuralı (varsayılan χ², β̂·ΔM > 0,5'te T–M) birleşik kural simülasyonunda başarısız oldu ve değiştirildi. Güncel kural §12'dedir; bu bölüm kayıt olarak korunur.

Karar (2026-10-21, kullanıcı onayı): bütün b aralıkları birlikte χ²'ye geçer; N = 50'de geçiş eşiği yok; kestirici değişmez; kaba gruplama için Tinti–Mulargia.

**Uygulama (`index.html`):**
- Tek giriş noktası `bCiFields(b, N, ex, ΔM)` → `{err, lo, hi, ciM}`. `ex`: (m − Mc) farkları (olay başına Mc'de m_i − Mc_i).
- Yöntem seçimi: varsayılan `chi2` (Gamma(N,1) yüzdelikleri, ters eksik gamma; önbellekli). β̂·ΔM > 0,5 **ve** bütün büyüklükler ΔM ızgarasındaysa `tm` (Eş. 19–21, ters eksik beta). Izgara dışı (ör. dönüştürülmüş Mw) → `chi2`. r = 0 → üst uç sınırsız, "[alt–∞]" olarak gösterilir.
- `?bci=normal` eski ±1,96·b/√N hesabını seçer.
- Çift kesik (fit aralığı M_max) b(t): Fisher SE simetrik kalır (χ² orada kesin değildir); metin "±" olarak sürer.
- Tüketiciler asimetrik uçlara geçirildi: b(t) bandı ve çubukları, yakınlaştırma paneli, b(t) sınıflama şeridi (`btClassOf` uçları kullanır), Mc–dönem tablosu, G–R b_GR, bölge satırı, artçı dizisi tablosu, grafiği ve dizi b(t) şeridi, poster metinleri ve ilk–son pencere karşılaştırması (`bCiDiffSig`: büyük tahminin alt kolu ile küçük tahminin üst kolu).
- Metin biçimi: "b = 1,02 [0,81–1,28]"; T–M kullanılan yerler açıkça etiketlenir (b(t) lejantında pencere sayısı, tabloda "TM").

**Doğrulama:**
- JS çekirdeği ↔ `bci.py` (scipy): χ² 36 durumda en büyük göreli fark 6·10⁻¹⁴ (N = 1–50 000); T–M 128 durumda 5·10⁻¹¹; r = 0'da sonsuz üst uç 16/16.
- `scripts/test_b_ci.js` (yeni, 30/0): gömülü scipy referansları, seçim kuralı, `normal` kipte birebirlik, sınıflama/anlamlılık, tohumlu kapsama (ΔM = 0,1 N = 10: χ² ve T–M nominal; ΔM = 0,5 b = 1,5 N = 49: χ² düşer, T–M nominal).
- Mevcut testler: 11 testin 10'u dalda geçer (`test_bt_adaptive` ve `test_mc_grid` aralık bloğunu okuyacak biçimde güncellendi; `BCI=normal` ile eski kip). `test_fit_range.js` main'de de çalışmıyor (2026-10-17'den beri bilinen TODO; bu işle ilgisi yok).
- Tarayıcı (Chromium, başsız, sabit saat): `?bci=normal` kipinde dalın ürettiği 45 SVG/metin öğesi ve poster PNG'si (SHA-256) main ile bayt bayt aynı. Fark yalnız durum nesnelerine eklenen `lo/hi/ciM` alanları ve Mc tablosu başlığındaki statik "±1.96·b/√N" → "%95 aralık" etiketi.
- Sentetik katalogla (yapay veri) tarayıcıda: T–M dalı 47 pencerede tetiklendi, uçları `bci.py` ile 3 ondalıkta aynı; SVG'lerde NaN/∞ yok; dizi paneli ve dizi b(t) şeridi hatasız.

**Açık kalanlar:** yöntem belgesi (eqlive-turkey-methodology.html, depo dışında) birleştirme onayından sonra güncellenecek; `test_b_ci.js` henüz bir CI iş akışına bağlı değil.

## 12. Birleştirme öncesi denetim ve kural değişikliği (2026-10-25)

Amaç: üretimdeki **birleşik** kuralı (yalnız bileşenleri değil) üretim kodunun kendisiyle sınamak, büyük N'yi kapsamak ve kod–rapor–yöntem belgesi tutarlılığını sağlamak.

### 12.1 Birleşik kural simülasyonu (`mc_secim.js`, üretim `bCiFields`, kopya yok)

İdeal G–R, büyüklükler ızgarada; 4000 tekrar, tohum 20261025; ΔM ∈ {0,1; 0,2; 0,3; 0,5}, b ∈ {0,5 … 3,0}, N ∈ {10, 20, 49, 100, 500} (100 hücre). Çıktı `out/mc_secim.json` (yeni kural); eski kuralın sonucu bu bölümdeki tabloda.

**Eski kural (χ², β̂·ΔM > 0,5 ise T–M):** 11 hücrede kapsama < 0,935, en düşük 0,903 (ΔM = 0,1, b = 2,2, N = 500). Birleşik kural eşik çevresinde **her iki bileşeninden de kötüdür**:

| ΔM | b | N | birleşik (eski) | yalnız χ² | yalnız T–M |
|---|---|---|---|---|---|
| 0,1 | 2,2 | 500 | 0,903 | 0,918 | 0,954 |
| 0,1 | 2,1 | 500 | 0,921 | 0,936 | 0,953 |
| 0,2 | 1,1 | 500 | 0,921 | 0,936 | 0,962 |
| 0,3 | 0,7 | 500 | 0,923 | 0,940 | 0,956 |

Nedenleri: (i) seçim b̂'ye bağlıdır; b̂ rastlantısal olarak düşük çıktığında χ² seçilir ve o örneklemlerde χ² aralığı da aşağı kaymıştır (gerçek b üstte kalır); (ii) 0,5 eşiği N ≤ 100 verisinden türetilmişti.

### 12.2 Büyük N'de χ² (ΔM = 0,1, EQ-Live'ın olağan ızgarası)

| b | β·ΔM | N | tekrar | χ² kapsama (gerçek b üstte) | T–M kapsama |
|---|---|---|---|---|---|
| 0,8 | 0,18 | 2000 | 1500 | 0,931 (%4,5) | 0,939 |
| 1,0 | 0,23 | 2000 | 1500 | 0,945 (%4,4) | 0,952 |
| 1,0 | 0,23 | 10 000 | 600 | 0,933 (%6,0) | 0,952 |
| 1,2 | 0,28 | 10 000 | 600 | 0,895 (%10,3) | 0,947 |
| 1,5 | 0,35 | 10 000 | 600 | 0,830 (%17,0) | 0,942 |

Utsu'nun ΔM/2 düzeltmesi gruplamanın etkisini tam gidermez; kalan yanlılık sabit kalırken standart hata 1/√N ile küçüldüğü için büyük N'de belirleyici olur. χ² aralığı b̂'ye bağlı olduğundan bu yanlılığı taşır; T–M aralığı b̂'ye değil N ve r'ye bağlıdır. (b = 0,8, N = 2000'deki 0,939, 1500 tekrarda Monte Carlo standart hatası ≈ 0,006 içinde nominalin biraz altındadır.)

### 12.3 Yeni kural

- Bütün büyüklükler ΔM ızgarasındaysa (|(m − Mc)/ΔM − tam sayı| ≤ 10⁻⁶): **her zaman T–M**. b̂'ye bağlı eşik yok.
- Izgara dışı en az bir büyüklük varsa ya da fark dizisi verilmemişse: χ²₂N (sürekli büyüklükte kesin, gruplanmışta yaklaşık).
- Çift kesik fit aralığı: Fisher SE (değişmedi). `?bci=normal`: eski ±1,96·b/√N (değişmedi).

Sonuç (aynı 100 hücre): kapsama 0,944–0,984; birleşik kural 100/100 hücrede yalnız T–M ile özdeş; tek yönlü kaçırma en çok %2,8. N = 10'da tek uç sınırsız olma oranı en çok %13,9 (ΔM = 0,5, b = 1,5; veri üst sınır taşımıyor).

### 12.4 Yan bulgular

- **Gerçek kataloglarda hangi yol çalışıyor (tarayıcı, 2026-10-25 verisi):** güncel katalog → T–M (b(t) 2/2 pencere, G–R); tarihsel katalog (`eq_historical.json`) → χ² (34/34 pencere, G–R). Tarihsel katalogda büyüklüklerin %3,7'si (3285/88 333) iki ondalıklı; tek bir ızgara dışı değer örneklemin tamamını χ²'ye düşürür. Bu, kullanıcı kararı gerektirir (aşağıda).
- **Kestirici:** b̂ (Aki–Utsu) gruplamadan dolayı hafifçe düşüktür (β·ΔM = 0,35'te ≈ %1). T–M aralığı bunu taşımadığı için b̂ büyük N'de aralığın alt kısmına yakın durur; çok büyük N'de (b ≈ 1,5, N ≳ 10⁵) aralığın dışına düşebilir. Kestiricinin T&M Eş. 14 ile değiştirilmesi ayrı bir karardır; bu çalışmada kestirici değişmedi.
- **Performans:** T–M çekirdeği tarayıcıda/Node'da ~0,06 ms/çağrı (önceki 5 ms ölçümü Node `vm` ortamının yüküydü); sonuçlar (N, r, ΔM) anahtarıyla önbelleğe alınır.
- **Atlanan tüketici bulundu ve düzeltildi:** bölge karşılaştırma tablosu `b ± σ` (1σ) gösteriyordu; artık `b [%95]` (normal kipte eski gösterim). CSV dışa aktarımı eski sütunları korur, sona `b_alt95, b_ust95, b_aralik_yontemi` ekler.

### 12.5 Doğrulama (bu bölümdeki kod durumu)

- `test_b_ci.js` 32/0 (seçim kuralı güncellendi; N = 10 000 büyük-N kontrolü eklendi). Mevcut testler değişmedi.
- Tarayıcı, `?bci=normal`: 45 öğe ve poster PNG'si main ile bayt bayt aynı (fark yalnız durum nesnelerindeki yeni alanlar ve Mc tablosu başlığındaki statik etiket). Sentetik katalogda (yapay veri) main ile dalın normal kipi bölge karşılaştırma tablosu dahil birebir aynı; yeni kuralda 167/167 pencere T–M, SVG'lerde NaN/∞ yok, sayfa hatası yok.

### 12.6 Sınırlar (geçerlilik iddiasının kapsamı)

Bütün kapsama sonuçları **ideal** G–R örneklemlerine aittir: tam tamlık, hatasız büyüklük, tek ölçek, bağımsız olaylar. Aralıklar yalnız örnekleme belirsizliğini temsil eder. Gerçek kataloglarda tamlık hatası, büyüklük ölçüm hatası (Tinti & Mulargia 1985), ölçek karışımı ve artçı kümelenmesi kapsamayı düşürebilir; bunlar sınanmadı. b(t) pencereleri örtüştüğü için ardışık pencerelerin aralıkları bağımsız değildir. Sentetik katalog görüntüleri (ör. `cmp_sens.png`) tek gerçekleşmedir ve kapsama kanıtı değildir.

### 12.7 Karar bekleyenler

1. Yeni kural (ızgarada her zaman T–M) — 2026-10-21 onayındaki "varsayılan χ²" kararının yerine geçer.
2. Kısmen ızgara dışı kataloglar (tarihsel katalog %3,7): (a) bugünkü katı kural (χ²), (b) büyüklükleri sınıf merkezine yuvarlayıp T–M (G–R panelindeki sınıflamayla ve kestiricinin ΔM/2 varsayımıyla tutarlı), (c) ızgara dışı oranına bağlı eşik (önerilmez: yeni bir veri bağımlı seçim).
3. Kestirici (T&M Eş. 14) — ayrı iş.

## 13. Küçük örneklem (N < 50) test grubu ve doğrudan fark testi (2026-10-25)

Bağlam: Tinti–Mulargia'nın EQ-Live'daki amacı, Hong Kong gibi az deprem üreten bölgelerde N = 50/100 koşulunu sağlamayan pencere ve bölgelerde b'nin zamansal ve bölgesel değişimini, belirsizliği gizlemeden incelenebilir kılmaktır. Bu bölüm, bunun hangi koşulda mümkün olduğunu ölçer. Betik `mc_kucukN.js` (üretim `computeBvalue` + `bCiFields`, kopya yok), çıktı `out/mc_kucukN.json`; tek örneklemde 20 000, iki örneklemde 5000 tekrar; tohum 20261026; ideal G–R, büyüklükler ızgarada.

**A) Tek örneklem, N = 10–49** (ΔM ∈ {0,1; 0,2}, b ∈ {0,7; 1,0; 1,3; 1,6}; 56 hücre):

| | kapsama | tek yönlü kaçırma (en çok) |
|---|---|---|
| T–M (üretim kuralı) | 0,949–0,973 | %2,7 |
| eski ±1,96·b/√N | 0,941–0,960 | %5,4 (hep üst tarafta) |

ΔM = 0,1, b = 1,0'da göreli genişlik (ortanca, (üst − alt)/b): N = 10'da 1,31; N = 20'de 0,90; N = 30'da 0,73; N = 49'da 0,57. Kestirici yanlılığı (ortalama b̂/b): N = 10'da 1,09–1,11; N = 20'de 1,04–1,05; N = 49'da 1,01–1,02 (Aki kestiricisinin bilinen küçük örneklem yanlılığı; kestirici bu çalışmada değiştirilmedi; aynı N'li iki pencere karşılaştırıldığında büyük ölçüde birbirini götürür).

**B) İki bağımsız örneklem (her biri N olay, b₁ = 1,0), b farkının saptanma olasılığı:**

| N | ölçüt | b₂ = 1,0 (yanlış alarm) | 0,8 | 0,7 | 0,5 | 1,3 |
|---|---|---|---|---|---|---|
| 10 | %95 aralıklar örtüşmez | 0,003 | 0,008 | 0,019 | 0,089 | 0,013 |
| 10 | Utsu P < 0,05 | 0,046 | 0,070 | 0,111 | 0,320 | 0,079 |
| 20 | aralıklar örtüşmez | 0,006 | 0,019 | 0,046 | 0,261 | 0,023 |
| 20 | Utsu P < 0,05 | 0,047 | 0,104 | 0,178 | 0,564 | 0,124 |
| 30 | aralıklar örtüşmez | 0,007 | 0,027 | 0,077 | 0,448 | 0,032 |
| 30 | Utsu P < 0,05 | 0,044 | 0,125 | 0,263 | 0,751 | 0,160 |
| 49 | aralıklar örtüşmez | 0,006 | 0,042 | 0,149 | 0,729 | 0,065 |
| 49 | Utsu P < 0,05 | 0,042 | 0,184 | 0,409 | 0,919 | 0,240 |

**Sonuçlar:**
1. Küçük N, aralık hesabı için engel değildir: T–M N = 10'da da nominal kapsar. Engel, **ayırt etme gücüdür**.
2. "İki %95 aralık örtüşmüyor" ölçütü çok tutucudur (yanlış alarm ≈ %0,5); b farkı için uygun test değildir. Utsu (1992) testi doğru kalibre (%4–5) ve 2–4 kat daha güçlüdür.
3. N ≤ 49'da yalnız büyük farklar (Δb ≈ 0,5) makul olasılıkla saptanır (N = 30'da %75). Δb ≈ 0,2–0,3 için anlamsız sonuç "fark yok" anlamına gelmez.
4. Bu sonuçlar ideal koşullara aittir (§12.6); gerçek küçük kataloglarda Mc belirsizliği küçük N'de görece daha etkilidir.

**Uygulananlar (dal `b-ci-chi2`):** `bUtsuP` (Utsu 1992; Schorlemmer vd. 2004 biçimi); bölge karşılaştırma tablosuna "b farkı, 1. bölgeye göre (Utsu 1992, P)" satırı (yalnız varsayılan kipte; `?bci=normal` çıktısı main ile aynı kalır); "N(≥Mc) < 50 olan bölgede b güvenilmez" notu "aralık geniş; farkları Utsu testiyle değerlendirin" olarak değiştirildi. `test_b_ci.js` 35/0 (Utsu: özdeşte e⁻¹, simetri, N = 30 yanlış alarm).

**Uygulanmayan (karar gerektirir):** b(t) penceresi bugün sabit N = 100'dür; bu, az olaylı bölgelerde zamansal analizin asıl engelidir. Seçilebilir küçük pencere (ör. N = 50/30/20) ve ardışık bağımsız dönemler arasında Utsu testi ayrı bir üretim işidir. §10'daki güç sonuçları ile bu bölümün B tablosu bu kararın dayanağıdır.

## 14. Seçilebilir b(t) penceresi (N = 100 / 50 / 30 / 20) ve tarihsel katalogda çözünürlük (2026-10-25)

### 14.1 Uygulama

- `BT_WIN_N` (varsayılan 100; Öncel & Wilson 2007). b(t) panelinde "pencere N" seçicisi; URL `?btn=50`, seçim tarayıcıda hatırlanır. Adım N/10 (100 → 10, 50 → 5, 30 → 3, 20 → 2); ince adım 1.
- `computeBvalueTimeSeries` ve `csBvalueTimeSeries` `nWin` alır; b(t) metinleri, yöntem satırı, örtüşme sayısı ("ardışık pencereler N − adım olayı paylaşır") ve poster yazıları seçili N'yi kullanır.
- N < 100'de istatistik satırında ve posterde açık uyarı: "küçük örneklem penceresi … aralıklar geniş, b değişimini saptama gücü düşük"; N = 20 "keşif amaçlı" ve "sınıf şeridi tek tük pencereleri rastlantısal olarak boyayabilir". Yetersiz veri iletisi küçük pencere seçilebileceğini söyler.
- Artçı dizisi panelinin pencereleri (`pbwN`) ayrıdır, değişmedi.
- `scripts/test_bt_window.js` (yeni, 14/0) CI iş akışına eklendi. Varsayılan N = 100'de, `?bci=normal` kipinde tarayıcı çıktısı ve poster PNG'si main ile aynı; `tmPanel`'deki fark yalnız eklenen seçici ve iki etiket (bunlar çıkarılınca bayt bayt aynı).

### 14.2 Monte Carlo (`mc_btpencere.js`, üretim kodu; 2000 tekrar, tohum 20261027)

600 olaylık YAPAY katalog (ideal G–R, 0,1 ızgarası). S0: durağan b = 1. S1/S2: ilk 300 olay b = 1,0, son 300 olay b = 0,8 / 0,6. "İlk–son Utsu" ilk ve son pencere (örtüşmüyor, bağımsız) arasındaki testtir.

| N (adım) | pencere kapsaması | b̂/b | S0: en az bir yanlış sınıf içeren seri | S0: ilk–son Utsu P < 0,05 | S1: ilk–son Utsu (1,0 → 0,8) | S2: ilk–son Utsu (1,0 → 0,6) | S2: yeni dönem pencerelerinin "düşük b" sınıfı |
|---|---|---|---|---|---|---|---|
| 100 (10) | 0,948–0,950 | 1,00–1,01 | %0 | %4,8 | %35 | %94 | %35 |
| 50 (5) | 0,949–0,952 | 1,02 | %0 | %4,7 | %19 | %71 | %20 |
| 30 (3) | 0,949–0,953 | 1,03 | %3 | %5,1 | %14 | %48 | %14 |
| 20 (2) | 0,950–0,952 | 1,05 | %12 | %4,5 | %10 | %34 | %12 |

**Yorum:** Pencere başına aralık her N'de nominaldir; küçük pencere ölçümü geçersiz kılmaz. Bedel güçtür: N = 30'da büyük bir düşüş (1,0 → 0,6) bile ancak yarı yarıya saptanır, orta büyüklükte bir değişim (1,0 → 0,8) neredeyse hiç. N = 20'de durağan serilerin %12'sinde sınıf şeridi en az bir pencereyi boyar (çoğu tek tük, yüksek b; Aki'nin yukarı yanlılığı ve geniş aralık). Örtüşen pencereler bağımsız olmadığından komşu pencerelerin "anlamlı" görünmesi bağımsız kanıt değildir; fark için örtüşmeyen dönemler Utsu testiyle karşılaştırılmalıdır.

**Tarayıcı (gerçek veri):** tarihsel 1900–1970 penceresinde N = 30 b(t)'yi ≈ 1918'den başlatır (N = 100'de ≈ 1929); güncel katalogda 112 olayla N = 100'de 2, N = 30'da 28 pencere. Görüntü: `tarayici/pencere_goruntu.js`.

### 14.3 Tarihsel katalogda büyüklük çözünürlüğü (karar ertelendi)

Tarihsel katalog üretimde kullanılır: "1900–1970" ve "1971–1997" ISC düğmeleri `eq_historical.json`'ı doğrudan b(t) ve G–R'ye verir. Izgara dışı değerler ISC'nin iki ondalıklı mb (%83), MS (%78) ve MW (%75) değerleridir; ağırlıkla 1960–1997. Yani sorun ondalık sayısı değil, karışık ölçüm çözünürlüğüdür (0,1 ve 0,01). Bu, aralık yönteminden önce kestiriciyi etkiler (ΔM/2 = 0,05 düzeltmesi 0,01 çözünürlüklü değerlere de uygulanıyor):

| ISC penceresi | N(≥Mc) | ızgara dışı | bugünkü b̂ | sürekli varsayım (ΔM = 0) | 0,1'e yuvarlanmış |
|---|---|---|---|---|---|
| 1900–1970 (Mc 4,7) | 430 | %57 | 0,526 | 0,560 | 0,565 |
| 1971–1997 (Mc 3,7) | 4808 | %56 | 0,718 | 0,782 | 0,723 |

Hangi tutarlı düzeltmenin (yuvarlama ya da çözünürlüğe göre ΔM) seçileceği bir yöntem kararıdır; ertelendi. Bugün bu pencerelerde aralık χ²'dir (ızgara dışı).

## 15. Büyük pencereler (N = 200 / 300 / 500) ve düzleşme (2026-10-25)

**Uygulama:** Seçenekler 20, 30, 50, 100 (varsayılan), 200, 300, 500; adım N/10; `?btn=` yalnız bu değerleri kabul eder. N > 100'de uyarı: "aralıklar dar, ancak yaklaşık N olaydan kısa süren değişimler düzleşir; ardışık pencereler N − adım olayı paylaşır". Seçicide M ≥ Mc olay sayısının yetmediği seçenekler "— yetersiz (N = …)" olarak işaretlenir (devre dışı bırakılmaz). N ≤ 30 uyarısına uzun serilerde rastlantısal sınıflama ve en düşük pencere b'sinin aşağı sapması eklendi. `test_bt_window.js` 18/0.

**Monte Carlo (`mc_btbuyuk.js`, üretim kodu; 300 tekrar, tohum 20261028):** 5000 olaylık YAPAY katalog (ideal G–R, 0,1 ızgarası), arka plan b = 1,0; ortada L olay süren b = 0,6 bölümü. "Yakalama": bölümle örtüşen pencerelerden en az biri "düşük b" sınıfında (aralığın tamamı < 0,7). Hücrelerde: yakalama olasılığı, serinin en düşük b̂'si (ortanca).

| N | durağan: pencere kapsaması | durağan: en az bir yanlış sınıflı pencere içeren seri | durağan: en düşük b̂ | L = 100 | L = 200 | L = 400 | L = 1000 |
|---|---|---|---|---|---|---|---|
| 20 | 0,951 | %67 | 0,53 | 0,76 / 0,43 | 0,93 / 0,40 | 0,99 / 0,38 | 1,00 / 0,35 |
| 30 | 0,951 | %21 | 0,60 | 0,64 / 0,48 | 0,86 / 0,44 | 0,99 / 0,42 | 1,00 / 0,40 |
| 50 | 0,952 | %2 | 0,68 | 0,54 / 0,53 | 0,81 / 0,49 | 0,97 / 0,47 | 1,00 / 0,44 |
| 100 | 0,951 | %0 | 0,77 | 0,37 / 0,60 | 0,73 / 0,55 | 0,95 / 0,52 | 1,00 / 0,49 |
| 200 | 0,950 | %0 | 0,84 | 0,01 / 0,73 | 0,60 / 0,60 | 0,91 / 0,56 | 1,00 / 0,54 |
| 300 | 0,949 | %0 | 0,88 | 0,00 / 0,79 | 0,09 / 0,68 | 0,87 / 0,59 | 1,00 / 0,56 |
| 500 | 0,952 | %0 | 0,91 | 0,00 / 0,85 | 0,00 / 0,77 | 0,46 / 0,64 | 1,00 / 0,58 |

**Sonuçlar:**
1. Pencere başına aralık her N'de nominaldir; büyük pencere geçerliliği bozmaz, aralığı daraltır.
2. Bir b anomalisi ancak süresi pencereden uzunsa (L ≳ N olay) güvenilir biçimde yakalanır: N = 500, 200 olaylık bir bölümü hiç yakalamaz; N = 200, 100 olaylık bölümü %1 olasılıkla yakalar. Büyük pencerede eğrinin inebildiği en düşük değer de yükselir (L = 200'de N = 500 için 0,77; gerçek 0,6).
3. Küçük pencerenin bedeli rastlantısal anomalidir ve seri uzadıkça artar: durağan 5000 olayda N = 20'de serilerin %67'si en az bir yanlış sınıflı pencere içerir (§14'teki 600 olaylık seride %12). Serinin en düşük b̂'si, çok sayıda pencere arasından seçildiği için aşağı yanlıdır (N = 20'de 0,53, gerçek 1,0). Küçük N'de yakalanan "düşük b" dolayısıyla tek başına kanıt değildir; örtüşmeyen dönemler Utsu testiyle karşılaştırılmalıdır (§13).
4. Pratik kural: beklenen değişimin süresinden (olay sayısı olarak) daha kısa bir pencere seçilmeli; N ≤ 30 yalnız kısa ya da az olaylı serilerde keşif için kullanılmalıdır.
