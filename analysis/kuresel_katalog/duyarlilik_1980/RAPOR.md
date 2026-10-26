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

## 4. İç tutarlılık denetimi (`sonuc.json` → `tutarlilik`; hepsi geçti, aksi hâlde betik durur)
- **Alt küme ilişkileri:** D ⊂ T ve V ⊂ T; D ile V ayrık; T = D + V + belirsiz (1 olay, `iscgem:7704315`).
- **Kapsam:** Üç örneklemde yıl aralığı 1980–2021. Coğrafi filtre yok; üçü de küresel.
- **N değerleri:** §1'deki N'ler her örneklemin kendi Mc'siyle sayıldı: T, Mc 5,4'te 26 025; D, Mc 5,3'te 28 858.
  - N(D) > N(T) görünmesinin nedeni eşiklerin farklı olması.
  - Aynı Mc'de, 4,8–6,5 aralığındaki her değerde N(D) ≤ N(T).

## 5. b farkının belirsizliği: eşleştirilmiş bootstrap
**Neden ayrı aralıkları karşılaştırmak yetmez:** T ve D iç içe kümeler. İki aralığın örtüşüp örtüşmemesi farkın belirsizliğini göstermez.

**Yöntem** (`sonuc.json` → `bootstrap`):
- 2 000 tekrar, tohum 20261026.
- Her tekrarda T'nin olayları yerine koyarak çekildi. D'nin karşılığı, çekilen olaylardan doğrudan Mw'li olanlardır. Böylece aynı olay iki örneklemde birlikte değişiyor.

| Kip | b_T − b_D ortanca | %95 bootstrap aralığı | Fark ≤ 0 olan tekrar | Mc dağılımı |
|---|---|---|---|---|
| Mc her tekrarda iki örneklem için ayrı kestirilir | +0,040 | +0,034 – +0,046 | 0 / 2 000 | T: 5,4 (2 000); D: 5,3 (1 932), 5,4 (66), 5,2 (2) |
| Mc = 5,5 sabit | +0,055 | +0,052 – +0,059 | 0 / 2 000 | — |
| Mc = 6,0 sabit | +0,020 | +0,016 – +0,024 | 0 / 2 000 | — |

**Teknik ayrıntı (yeniden üretilebilirlik):**
- **Yeniden örnekleme birimi:** Tek tek olaylar. Her tekrarda T'nin 53 085 olayından, yerine koyarak 53 085 olay çekildi. Küme, bölge ya da zaman bloğu kullanılmadı. Olaylar arası bağımlılık (artçı şoklar, zamansal kümelenme) bu yüzden modellenmedi; aralık bu varsayım altında geçerli.
- **D'nin karşılığı:** Çekilen olaylardan doğrudan Mw'li olanlar (`Mw_yontem = dogrudan` ve M0 kaynağı gcmt veya bibliog).
- **Büyüklükler:** Bir kez 0,1 sınıfına yuvarlandı (`bGridRound`); tekrarlarda yeniden yuvarlama yok.
- **Mc kuralı ("ayrı kestirim" kipi):** Her tekrarda T ve D için ayrı ayrı `computeMcSrc` ile hesaplandı: 0,1'lik sınıflarda en kalabalık sınıf + 0,2 (maksimum eğrilik + Woessner ve Wiemer 2005 düzeltmesi). Sabit kiplerde Mc = 5,5 veya 6,0.
- **b:** `computeBvalue`, Aki–Utsu, ΔM = 0,1.
- **Aralık:** 2,5 ve 97,5 yüzdelikleri (yüzdelik bootstrap).
- **Rastgele sayı üreteci:** mulberry32, tohum 20261026.
- **Yeniden üretim:** Depo kökünde `node analysis/kuresel_katalog/duyarlilik_1980/b_vekil_1980.js` (yaklaşık 4 dk). Aynı girdi dosyasıyla `sonuc.json` aynen yeniden üretilir; girdi SHA-256'sı dosyada.

**Yorum:**
- **Fark, bu tasarım ve bu Mc eşikleri altında istatistiksel olarak kararlı.** İki b-değerinin kendi aralıkları geniş olsa da fark dar bir aralıkta kalıyor; aynı olaylar iki örneklemde ortak.
- **Mc kestirimi kararlı.** D'nin Mc'si tekrarların %97'sinde 5,3. Bu yüzden fark Mc kestirimindeki oynamadan gelmiyor.
- **Bootstrap neyi ölçmez:** Bu aralık yalnız örnekleme belirsizliğidir. Vekil Mw değerlerinde sistematik bir sapma varsa bu aralığa yansımaz. Seçim yanlılığı ile vekil sapması bu analizle ayrılamaz (§3, madde 4).

## 6. Desteklenen karar ve sınırı
- **b-değeri ve Mc:** Varsayılan örneklem ISC-GEM'in tüm Mw değerleri olur; doğrudan ve vekil Mw oranları raporlanır.
- **Bağıntı sınaması:** Dönüşüm bağıntılarının performans değerlendirmesinde doğrudan moment kaynaklı Mw ayrı referans grubudur.
- **Yalnız doğrudan Mw ile b-değeri:** Duyarlılık analizi olarak sunulur. Seçim yanlılığı açıklanır; 1980–2021'de b'yi 0,02–0,06 düşürüyor.
- **Sınır:** Bu sonuçlar tüm Mw değerlerinin her durumda daha doğru b-değeri verdiğini kanıtlamaz. Vekil Mw'deki olası sistematik sapma ile doğrudan alt kümedeki seçim yanlılığı birbirinden ayrılmış değildir.

## 7. Bağıntı sorusu: Di Giacomo vd. (2015) EQ-Live'a eklenmeli mi?
- **İletilen PDF bağıntı içermiyor.** Dosya ISC-GEM dizisinin I. makalesi: Di Giacomo vd. (2015b), PEPI 239:14–24, doi:10.1016/j.pepi.2014.06.003, erken bültenlerden veri toplama. Bu makalede vekil Mw bağıntısı verilmiyor. Bağıntıdan yalnız bir yerde söz ediliyor: ön seçimde (kesme büyüklüğü) Bormann vd. (2009) bağıntılarının kullanıldığı belirtiliyor.
- **Asıl bağıntılar III. makalede ve EQ-Live'da zaten var.** III. makale: Di Giacomo vd. (2015a), PEPI 239:33–47, doi:10.1016/j.pepi.2014.06.005. Üstel Ms → Mw ve mb → Mw bağıntıları 2026-10-11'den beri `MAG_CONVERSIONS.iscgem2015` olarak "duyarlılık analizi" etiketiyle seçilebiliyor. Kayıtlı katsayılar:
  - Ms: Mw = exp(−0,222 + 0,233 Ms) + 2,863
  - mb: Mw = exp(−4,664 + 0,859 mb) + 4,555
  - Kaynak: s. 41–42.
- **Döngüsellik uyarısı:** ISC-GEM'in vekil Mw'leri bu bağıntılarla hesaplanmıştır. `iscgem2015` bağıntısının (ya da benzer Ms/mb bağıntılarının) başarımı ISC-GEM'in vekil Mw'sine karşı ölçülürse sonuç kendini doğrular. Bağıntı sınamasında yalnız doğrudan Mw grubu kullanılmalı (bkz. ASAMA_2_RAPOR §4).
- **Arayüzde bulunmak doğrulanmış olmak demek değil:** `iscgem2015`, `lolli2014` ve `scordilis2006` gibi bağıntıların EQ-Live'da seçilebilir olması, bunların bağımsız olarak doğrulandığını göstermez.
- **Ajans farkı:** Bağıntılar ISC-GEM'in yeniden hesapladığı (IASPEI standardı) Ms/mb için türetilmiştir. USGS, EMSC ya da Türkiye ajanslarının mb/Ms'sine uygulanması bir varsayımdır (`index.html`'deki not ile aynı). Bu aktarım varsayımı ayrıca ve bağımsız olarak sınanmalıdır; burada sınanmadı.

## 8. Karara etkisi
- **b-değeri:** Önceki öneri (varsayılan b-değerinde tüm ISC-GEM Mw; vekil oranı gösterilerek) değişmez.
  - 1980 sonrasında "yalnız doğrudan Mw" seçeneği b-değerini 0,01–0,06 düşürüyor.
  - Bu fark %95 aralık genişliğiyle aynı büyüklükte ya da ondan büyük. Seçenek kullanılırsa bu etki uyarıda belirtilmeli.
- **Bağıntı sınaması:** Dönüşüm bağıntılarının sınanmasında referans küme yine yalnız doğrudan Mw. Bu analiz o kullanımı etkilemez.

## 9. Durum
**Duyarlılık analizi tamamlandı ve kapatıldı (2026-10-26).**
- Yeni hesaplama ya da arayüz değişikliği önerilmiyor.
- `main`, canlı site, `data/mw_iscgem.json` ve Türkiye kataloğu değişmedi.
