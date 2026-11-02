# Aki–Utsu ve Bender (1983) b kestiricileri: karşılaştırma

Tarih: 2026-11-01. Bu ayrı bir analizdir. Uygulama (`index.html`) değiştirilmedi; Aki–Utsu referans yöntem olarak kalıyor.

- Betik: `bender_karsilastirma.js`
- Çıktılar: `bender_karsilastirma.json`, `bender_karsilastirma_cikti.txt`
- Girdi: `analysis/poisson_olasilik/cmp_yeniden_uretim.json`. Katalog `data/eq_historical.json` (git blob 879a89b9, üretim 2026-09-14), EMSC 1998–, Mc 3,2, ΔM 0,1.

## 1. Yöntem (kaynağa göre)

Kaynak: Bender, B. (1983), *BSSA* 73(3), 831–851 (Zotero DVM4CQ9X).

Bender ilk sınıfın **alt sınırını** m_min olarak alır. Ek Denklem (A7): m̄ = m_min + (Δm/2)·(1 + q)/(1 − q), q = e^(−βΔm).

Uygulamada Mc ilk sınıfın **merkezidir**, yani Mc = m_min + Δm/2. Tanımlar:
- K̄ = (m̄ − Mc)/Δm.
- Bender (Mmax = ∞): q/(1 − q) = K̄, buradan b_B = log₁₀(1 + Δm/(m̄ − Mc)) / Δm.
- Aki–Utsu (uygulama): b_AU = log₁₀e / (m̄ − Mc + Δm/2).

Δm → 0 limitinde iki kestirici aynı değere iner. Δm > 0 için:
- Bender, gruplanmış geometrik modelin kesin en çok olabilirlik kestiricisidir.
- Aki–Utsu'daki Δm/2 düzeltmesi yalnız yaklaşıktır (Bender, Ek s. 848–849).

Sonlu Mmax (Bender Denklem 10) yalnız duyarlılık için hesaplandı. Mmax olarak gözlenen en büyük sınıf alındı. Bender'in de belirttiği gibi bu değer olası en büyük büyüklük değildir; konu aşama 5'te (kesik G–R) ayrıca ele alınacak.

**Büyüklük tanımı uyumu.** Analiz uygulamanın büyüklüklerini kullanır: e.mw ?? e.mag, bGridVals ile 0,1 ızgarasına alınmış.
- Üç bölgede de Mc üstündeki bütün olaylar Mc + kΔM ızgarasında; ızgara dışı olay sayısı 0.
- b_AU, kayıttaki b ile birebir aynı.
- Bootstrap çekilişleri uygulamanın `grBootDraws` akışıyla birebir aynı (denetim 0).

## 2. Gerçek bölgeler

Bootstrap: B = 2000, tohum 20261027. Her kestirici kendi b değerinden üretir. "Nokta yüzdeliği", nokta kestiriminin bootstrap dağılımındaki yeridir; 0,50 değeri aralıkla tam uyum demektir.

| Bölge | N(≥Mc) | b_AU [%95] | Nokta yüzdeliği AU | b_Bender [%95] | Nokta yüzdeliği Bender | Bender − AU |
|---|---|---|---|---|---|---|
| Türkiye | 27 346 | 1,1368 [1,1164–1,1436] | 0,83 | 1,1434 [1,1290–1,1569] | 0,51 | +0,0066 |
| Marmara | 624 | 1,0007 [0,9200–1,0819] | 0,53 | 1,0052 [0,9299–1,0925] | 0,50 | +0,0045 |
| Doğu Anadolu | 5 007 | 0,9904 [0,9594–1,0140] | 0,63 | 0,9947 [0,9675–1,0227] | 0,50 | +0,0043 |

- **Moment uyumu:** Bender'in öngördüğü ortalama sınıf (K̄) gözlenenle aynıdır. Aki–Utsu'da öngörülen K̄ sistematik olarak büyüktür (Türkiye 3,342 / gözlenen 3,320).
- **Sonlu Mmax duyarlılığı:** Bender sonlu Mmax ile Türkiye 1,1433, Marmara 1,0005, Doğu Anadolu 0,9945 verir. Etki ≤ 0,005.

**P(≥7; t) üzerindeki etki** (%, [%95]):

| Bölge | t (yıl) | Aki–Utsu | Bender |
|---|---|---|---|
| Türkiye | 10 | 36,6 [34,9–42,1] | 35,0 [31,8–38,7] |
| Türkiye | 50 | 89,8 [88,3–93,5] | 88,4 [85,2–91,3] |
| Marmara | 50 | 15,7 [8,1–29,2] | 15,2 [7,4–27,4] |
| Doğu Anadolu | 50 | 77,8 [70,7–86,2] | 76,5 [67,9–84,2] |

Bender'de nokta kestirimi her bölgede aralığın ortasına oturuyor. Aki–Utsu'da Türkiye'nin nokta kestirimi aralığın alt ucuna yakın kalıyor. Olasılıklardaki fark büyük n'de ≈ 1,5 yüzde puan, Marmara'da ≈ 0,5 yüzde puan.

## 3. Benzetim

Benzetim koşulları:
- 16 senaryo: b ∈ {0,8; 1,0; 1,14; 1,3} × n ∈ {100; 624; 5 000; 27 346}.
- Her senaryoda 400 katalog, olay olay üretildi.
- Bootstrap B = 500.

Tam tablo `bender_karsilastirma_cikti.txt` dosyasında. Özet (Aki–Utsu / Bender):

| n | Yanlılık (b = 1,14) | RMSE (b = 1,14) | b'nin %95 kapsaması (b = 0,8–1,3) |
|---|---|---|---|
| 100 | +0,010 / +0,017 | 0,122 / 0,125 | %93–95 / %93–94 |
| 624 | −0,003 / +0,003 | 0,046 / 0,047 | %94–96 / %94–96 |
| 5 000 | −0,005 / +0,002 | 0,017 / 0,016 | %80–92 / %93–95 |
| 27 346 | −0,007 / −0,000 | 0,010 / 0,007 | **%28–84** / %92–94 |

- **Aki–Utsu:** yanlılığı sistematiktir ve b ile artar (b = 1,3'te −0,010). n büyüdükçe aralık daralır ama yanlılık kalır. Bu yüzden büyük n'de kapsama çöker: n = 27 346, b = 1,14 için b'de %48,8, P(≥7; 50 yıl)'da %49,5.
- **Bender:** büyük n'de yanlılığı istatistik gürültüsü düzeyindedir; kapsama tüm senaryolarda %92–96.
- **Küçük n (100):** Bender'in küçük örneklem yanlılığı biraz daha büyük (+0,017), ama RMSE farkı ihmal edilebilir.
- **P(≥7; 50 yıl) kapsaması:** b kapsamasını izliyor. b = 0,8 ve n = 27 346 için %100 çıkıyor, çünkü olasılık doyuyor (≈ %100).

## 4. Ek bulgu (kestiriciden bağımsız)

Sınıf sayılarının geometrik modele χ² uyumu Türkiye'de zayıf: 220/31 serbestlik derecesi, iki kestiricide de aynı. Marmara 37/19, Doğu Anadolu 55/29.

Bu fark kestirici seçiminden değil, büyüklük–sıklık dağılımının tek eğimli G–R'den sapmasından kaynaklanıyor. Olası nedenler: büyüklük türü geçişi (MD → ML) ve tamlık. Bunu ayrı bir inceleme konusu olarak öneriyorum.

## 5. Sonuç ve öneri (karar sizin)

1. İki kestiricinin farkı küçük (0,004–0,007), ama büyük katalogda b'nin standart hatasıyla karşılaştırılabilir (Türkiye ≈ 0,9 sd). Aki–Utsu'nun %95 aralığı büyük n'de anlamlı biçimde eksik kapsıyor.
2. Önerilen ilkeye uygun olarak Bender, Aki–Utsu'nun **yerine değil yanına** eklenebilir. G–R paneli ve bölge karşılaştırmasında "b kestiricisi: Aki–Utsu (referans) / Bender (1983)" seçimi ve iki sonucun yan yana gösterimi mümkün. Bu, uygulama değişikliğidir ve ayrı onay gerektirir.
3. Varsayılan hâlâ Aki–Utsu olur. Bender seçildiğinde yeniden üretim kaydı (aşama 4) kullanılan kestiriciyi yazmalıdır.
