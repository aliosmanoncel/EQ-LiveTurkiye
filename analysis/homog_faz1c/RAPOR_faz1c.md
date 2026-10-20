# Faz 1c — Stepp (1972) tamlık testi, ön sonuçlar (2026-10-21)

**Durum:** prototip; nihai tamlık eşiği önerilmiyor. ISC sorgu sonuçları (Faz 1b) gelmeden eksikliğin nedeni hakkında karar verilmez. Üretim kodu, `eq_historical.json`, GK74 kodu (`scripts/decluster_gk74.py` yalnız içe aktarıldı), `mw_authority.json` ve mevcut merdiven değiştirilmedi. Girdilerin SHA-256 özetleri `out/stepp_sonuc.json → meta.inputs`.

## Kurulum
- Seriler: **A** = `eq_historical.json` (büyüklük `mw ?? mag`), **B** = ISC-GEM v12.1 ana katalog (Mw; ayrıca doğrudan / vekil ayrı). Her biri ham ve GK74 sonrası. **Ana seri önceden belirlendi: A_GK74 ve B_GK74**; ham seriler duyarlılık.
- Ortak bitiş 2021-12-31 (ISC-GEM'in son yılı). Sınıflar: 4,5–5,0 · 5,0–5,5 · 5,5–6,0 · ≥ 6,0.
- λ(T) = N/T, σ(T) = √(λ/T) (Stepp 1972, eş. 2–4), T = 1…118 yıl, bitişten geriye.
- Stepp başlangıç yılını grafikten gözle seçer. Burada iki nesnel ölçüt **bizim uyarlamamızdır**: (i) log σ – log T'de eğimi −0,5'e sabit ilk parçalı kırılma noktası; (ii) Poisson düşüşü: λ(T) < λ_ref − 2√(λ_ref/T) olduğu ilk T. λ_ref seçimi sonucu belirgin değiştirdiği için T_ref = 20/30/40 yıl duyarlılığı da verildi.

## Sonuçlar — tamlık başlangıç yılı (Poisson ölçütü; parantez: T_ref = 20 / 30 / 40 yıl)

| Seri | 4,5–5,0 | 5,0–5,5 | 5,5–6,0 | ≥ 6,0 | Mevcut merdiven |
|---|---|---|---|---|---|
| A_GK74 | 1965 (1994 / 1965 / 1965) | 2002 (1983 / 1965 / 1963) | 2002 (1985 / 1962 / 1915) | 1905 (1905 / 1905 / 1905) | 4,5–5,5: 1965 · ≥ 5,5: 1900 |
| B_GK74 (ISC-GEM) | — (N = 20) | 1984 (1988 / 1962 / 1958) | **1905 (1905 / 1905 / 1905)** | **1904 (1904 / 1904 / 1904)** | |

- **Kararlı olan:** ISC-GEM'de M ≥ 5,5 her ölçütle 1904–1905'ten beri tam görünüyor. A'da M ≥ 6,0 da 1905'ten beri "tam" görünüyor.
- **Kararsız olan:** M 5,0–6,0 sınıflarında başlangıç yılı referans penceresine göre 1915 ile 2002 arasında değişiyor; bu sınıflar için Stepp sonucu belirsiz.
- Kırılma noktası ölçütü (i) son 10–20 yıla düşüyor (artçı dizileri ve büyüklük türü geçişleri kısa T'de σ'yı bozuyor); bu ölçüt bu veride güvenilir değil.
- Yeterlilik: bütün sınıflarda tamlık süresi ≥ 5τ ve N ≥ 5 (M ≥ 6'da τ ≈ 0,8 yıl). 5τ yeterlilik kanıtı değildir.

## Stepp testinin tek başına yetmediğinin kanıtı (A ile B'nin doğrudan sayım karşılaştırması)

| Sınıf · dönem | A (EQ-Live) | B (ISC-GEM) |
|---|---|---|
| 5,5–6,0 · 1904–1939 | 41 | 132 |
| 5,5–6,0 · 1940–1962 | 36 | 119 |
| 5,5–6,0 · 1963–1997 | 63 | 132 |
| 5,5–6,0 · 1998–2021 | 69 | 89 |
| ≥ 6,0 · 1904–1939 | 46 | 62 |
| ≥ 6,0 · 1940–1962 | 40 | 40 |

A'da M ≥ 6 Stepp testinde 1905'ten beri "tam" çıkıyor, oysa Faz 1'de 1963 öncesi ISC-GEM M ≥ 6 olaylarının 35'inin A'da bulunmadığı gösterildi. Sayıların yakın olmasının nedeni A'nın 1963 öncesinde çoğunlukla Ms kullanması (M ≥ 6'nın 69/86'sı Ms) ve farklı olayların sınıfa girmesi olabilir — **doğrulanmadı**. Ayrıca 1998–2021'de bile A'nın 5,5–6 sınıfı B'den az: mb'nin Mw'den ≈ 0,2–0,3 küçük olması olayları alt sınıfa kaydırıyor (sınıf göçü). Sonuç: büyüklük ölçeği homojen olmayan bir katalogda Stepp eğrisi "kararlı" görünse bile olaylar eksik olabilir; **kaynak kapsamı Stepp testiyle değil, bağımsız katalogla karşılaştırmayla sınanmalıdır.**

## Açık konular
1. ISC sorgu sonuçları (Faz 1b) ile birleştirme: eksik olayların kaynak kapsamı / büyüklük süzgeci / veri çekimi ayrımı.
2. A için Stepp testini homojen bir büyüklükle (ör. referans Mw'li alt küme) tekrarlamak.
3. λ_ref seçimi için önceden tanımlı tek bir kural belirlemek (şu an duyarlılık olarak raporlandı).
