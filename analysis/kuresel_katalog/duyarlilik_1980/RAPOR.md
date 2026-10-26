# Duyarlılık analizi: vekil Mw'nin b-değerine etkisi, ISC-GEM v12.1, 1980–2021 (2026-10-26)

**Amaç:** Önerilen varsayılan küme (tüm ISC-GEM Mw) ile "yalnız doğrudan Mw" kümesinin b-değeri açısından ne ölçüde ayrıştığını görmek. Ayrışmanın Mc farkından mı yoksa örneklem bileşiminden mi geldiği ayrılmaya çalışıldı. Bu analiz evrensel bir doğrulama değildir.
**Kapsam:** 1980–2021, küresel, `uretim/iscgem_global.json` (SHA-256 `sonuc.json` içinde). Yeni katalog birleştirmesi yok. Arayüz, `main` ve Türkiye kataloğu değişmedi.

**Yöntem:** EQ-Live'ın varsayılan yolu; fonksiyonlar `index.html`'den değiştirilmeden okundu.
- Büyüklük 0,1 sınıfına yuvarlandı (`bGridRound`).
- Mc = maksimum eğrilik + 0,2 (Wiemer ve Wyss 2000; Woessner ve Wiemer 2005).
- b: Aki–Utsu, ΔM = 0,1.
- %95 aralık: Tinti ve Mulargia (1987).

**Örneklemler:**
- **T:** tüm Mw.
- **D:** doğrudan Mw; `Mw_yontem = dogrudan` ve M0 kaynağı gcmt veya bibliog.
- **V:** yalnız vekil; yalnız tanı amaçlı.

T ve D iç içe kümeler (D ⊂ T). Bu yüzden bağımsız örneklem testi (ör. Utsu) uygulanamaz; yalnız aralıklar verildi.

## 1. Her örneklem kendi Mc'siyle

| Örneklem | N (toplam) | Mc | N (≥ Mc) | M aralığı | b | %95 aralık |
|---|---|---|---|---|---|---|
| T (tüm Mw) | 53 085 | 5,4 | 26 025 | 5,4–9,3 | 1,024 | 1,017–1,042 |
| D (doğrudan) | 48 002 | 5,3 | 28 858 | 5,3–9,3 | 0,984 | 0,977–1,000 |
| V (vekil) | 5 082 | 5,4 | 2 894 | 5,4–7,7 | 1,403 | 1,364–1,468 |

Mc'ler 0,1 farklı. Doğrudan kümenin histogram tepesi bir sınıf daha düşükte (5,1'e karşı 5,2).

## 2. Ortak Mc'de (Mc farkı giderildiğinde)

| Mc | T: N, b [%95] | D: N, b [%95] | T − D |
|---|---|---|---|
| 5,3 | 32 383; 1,008 [1,001–1,024] | 28 858; 0,984 [0,977–1,000] | +0,024 |
| 5,4 | 26 025; 1,024 [1,017–1,042] | 23 131; 0,991 [0,983–1,008] | +0,033 |
| 5,5 | 20 806; 1,040 [1,030–1,059] | 18 284; 0,984 [0,974–1,003] | +0,056 |
| 5,6 | 16 556; 1,054 [1,043–1,075] | 14 782; 1,001 [0,989–1,022] | +0,053 |
| 5,8 | 10 093; 1,041 [1,026–1,067] | 9 376; 1,010 [0,994–1,035] | +0,031 |
| 6,0 | 6 184; 1,032 [1,011–1,063] | 5 877; 1,012 [0,991–1,043] | +0,020 |
| 6,2 | 3 823; 1,024 [0,997–1,062] | 3 674; 1,008 [0,980–1,045] | +0,016 |
| 6,5 | 1 887; 1,041 [0,999–1,094] | 1 839; 1,028 [0,986–1,081] | +0,013 |

Tam b(Mc) eğrisi (4,8–6,5; V dahil): `sonuc.json`.

## 3. Bulgular
1. **Fark Mc farkından gelmiyor.** Aynı Mc'de de T'nin b-değeri D'ninkinden 0,013–0,056 yüksek. Fark yalnız Mc tahmini farkıyla açıklanamaz.
2. **Fark örneklem bileşimiyle tutarlı.** 1980 sonrası vekiller küçük büyüklüklerde yoğunlaşıyor (V'nin histogramı 5,1–5,6'da; b(V) = 1,4–1,9). Vekillerin dışarıda bırakılması küçük büyüklüklerde olay eksiltiyor ve D'nin b-değerini düşürüyor.
   - Fark, vekil payının düştüğü yüksek Mc'lerde küçülüyor: 5,5'te +0,056, 6,5'te +0,013.
   - Bu desen, 1976 öncesi için öngörülen seçim yanlılığının daha zayıf bir biçimi.
3. **V tek başına anlamlı bir b-değeri değil.** Vekil kümesi tam bir örneklem değil; GCMT çözümü olmayan olaylardan oluşan bir seçim. 1,4–1,9 değerleri bir fiziksel b-değeri olarak yorumlanmamalı.
4. **Hangi kümenin "doğru" olduğu bu analizle kanıtlanamaz.** T'nin daha yüksek b-değeri iki şekilde açıklanabilir:
   - (a) D'nin seçim yanlılığı;
   - (b) vekil Mw değerlerinin sistematik bir sapması.

   İkisi ancak vekil olaylar için bağımsız bir Mw kaynağıyla ayrılabilir. Bu analiz yapılmadı.
5. **Mc uyarısı:**
   - Maksimum eğrilikle bulunan küresel Mc (5,3–5,4), ISC-GEM'in 2019 öncesinde bölgeye göre tekdüze olmadığını belirttiği Mw 5,0–5,5 aralığında (Di Giacomo vd. 2018). Bu Mc'ler küresel tamlık olarak kabul edilmemeli.
   - Mc ≥ 5,5'te T'nin b-değeri 1,02–1,05, D'ninki 0,98–1,03. Fark 0,013–0,056.

## 4. Karara etkisi
- **b-değeri:** Önceki öneri (varsayılan b-değerinde tüm ISC-GEM Mw; vekil oranı gösterilerek) değişmez.
  - 1980 sonrasında "yalnız doğrudan Mw" seçeneği b-değerini 0,01–0,06 düşürüyor.
  - Bu fark %95 aralık genişliğiyle aynı büyüklükte ya da ondan büyük. Seçenek kullanılırsa bu etki uyarıda belirtilmeli.
- **Bağıntı sınaması:** Dönüşüm bağıntılarının sınanmasında referans küme yine yalnız doğrudan Mw. Bu analiz o kullanımı etkilemez.
