# Aşama B2: modern GMPE duyarlılığı (model değerlendirmesi)

Tarih: 2026-11-02. Dal: `psha-dogrulama`.

**Bu bir model duyarlılık çalışmasıdır, doğrulama değildir.** Buradaki hiçbir PGA değeri doğrulanmış tehlike değeri değildir.
- Kaynak modeli Aşama A ile aynıdır: Cotabato ve Davao nokta kaynakları, aynı MFD, medyan dal. Değişen yalnız GMPE, site Vs30'u ve σ kesmesi.
- Sonuçlar nokta kaynak varsayımını taşır; B3'te kaynak geometrisiyle tekrarlanacak.

## 0. Önceki rapora düzeltme (ÖNEMLİ)

RAPOR.md §5'te ve 2026-11-02 sabahki yazışmada Youngs (1997) hesabı "kaya koşulu, büyütmesiz" olarak tanımlanmıştı. **Bu yanlıştı.**
- OpenQuake'in `YoungsEtAl1997SInter` sınıfı Vs30 < 760 m/s olduğunda **zemin** katsayılarını kullanıyor (`ROCK_VS30 = 760`).
- Site Vs30 = 360 m/s olduğu için 0,993 g sonucu Youngs (1997) **zemin** denklemiyle hesaplandı. B2'deki 0,994 g değeri bunu doğruluyor.
- Dolayısıyla 0,703 → 0,993 g farkı "kaya ile zemin" farkı değil. İki farklı zemin gösterimi arasındaki farktır:
  - koddaki 0,35·ln(760/Vs30) terimi;
  - Youngs (1997)'nin ayrı zemin katsayıları.
- Doğru adlandırma: **"GMPE + zemin formülasyonu birleşik duyarlılığı"**. Bu raporun §2 tablosu iki etkiyi aynı Vs30'ta ayırıyor.

RAPOR.md §5 bu doğrultuda güncellendi.

## 1. Modeller ve Mindanao'ya uygulanabilirlik

| Model (OpenQuake sınıfı) | Veri / bölgesel kalibrasyon | Filipinler / Mindanao | Zemin terimi |
|---|---|---|---|
| Koddaki bağıntı (`MindanaoKodGMPE`; "Youngs 1988" etiketli) | Birincil kaynakla doğrulanmadı (B1) | Bilinmiyor | 0,35·ln(760/Vs30); yayından doğrulanmadı |
| Youngs vd. 1997 (`YoungsEtAl1997SInter`) | Alaska, Şili, Cascadia, Japonya, Meksika, Peru, Solomon Adaları; 1940–1992; 5,0 < M < 8,2; 8,5–550 km; 19 deprem, 271 kayıt | Veri setinde yok | İki sınıf: kaya (Vs30 ≥ 760) ve zemin |
| BC Hydro, Abrahamson vd. 2016 (`AbrahamsonEtAl2015SInter`) | Küresel subdüksiyon verisi. 2018 güncellemesi altı bölge: Cascadia, Orta Amerika, Japonya, Yeni Zelanda, Güney Amerika, Tayvan | İncelenen kaynaklarda bölgesel terim yok | Sürekli Vs30, doğrusal olmayan |
| Parker vd. 2022 (`ParkerEtAl2020SInter`) | NGA-Sub. Bölgesel ayarlar: Japonya, Tayvan, Meksika, Orta Amerika, Güney Amerika, Alaska, Aleut, Cascadia. Arayüz M 5–9,1, 15–1000 km | Bölgesel ayar yok → küresel sürüm kullanıldı | Sürekli Vs30 |
| Kuehn vd. 2023 (`KuehnEtAl2020SInter`) | NGA-Sub. Yedi bölge: Alaska, Orta Amerika–Meksika, Cascadia, Japonya, Yeni Zelanda, Güney Amerika, Tayvan | Bölge yok → küresel ("GLO") sürüm; OpenQuake'te **deneysel** işaretli | Sürekli Vs30 |

**Bir modelin OpenQuake kataloğunda bulunması Mindanao için doğrulandığı anlamına gelmez.** Hiçbir modelde Filipinler'e özgü bir kalibrasyon yok.

## 2. Sonuçlar

Kaynak: Cotabato + Davao, medyan dal. Değerler g cinsinden. "Kesilmemiş" sütunu Aşama A ile karşılaştırılabilirlik içindir; modern uygulamada σ sıkça 3'te kesilir.

| Model | Vs30 (m/s) | %10/50: kesilmemiş σ / σ 3'te kesik | %2/50: kesilmemiş σ / σ 3'te kesik | Medyan PGA, M 7,8, rrup 58 km | σ_ln |
|---|---|---|---|---|---|
| Kod bağıntısı | 360 | **0,706** / 0,551 | 1,045 / 0,724 | 0,161 | 0,67 |
| Kod bağıntısı | 760 | 0,544 / 0,424 | 0,804 / 0,557 | 0,124 | 0,67 |
| Youngs (1997) | 360 (zemin) | 0,994 / 0,824 | 1,476 / 1,095 | 0,228 | 0,67 |
| Youngs (1997) | 760 (kaya) | 0,662 / 0,539 | 0,981 / 0,708 | 0,145 | 0,67 |
| BC Hydro (2016) | 360 | 0,539 / 0,523 | 0,941 / 0,898 | 0,203 | 0,74 |
| BC Hydro (2016) | 760 | 0,445 / 0,433 | 0,792 / 0,760 | 0,171 | 0,74 |
| Parker (2022), küresel | 360 | 0,429 / 0,411 | 0,720 / 0,672 | 0,144 | 0,75 |
| Parker (2022), küresel | 760 | 0,381 / 0,364 | 0,664 / 0,621 | 0,122 | 0,79 |
| Kuehn (2023), küresel | 360 | 0,917 / 0,885 | 1,587 / 1,496 | 0,322 | 0,77 |
| Kuehn (2023), küresel | 760 | 0,729 / 0,706 | 1,292 / 1,229 | 0,265 | 0,77 |

**Sağlama:** Kod bağıntısı, Vs30 = 360 için %10/50 değeri 0,70615 g. Bu, Aşama A'daki iki kaynaklı toplam eğrisiyle aynı.

## 3. Gözlemler

1. **Saf GMPE etkisi (aynı Vs30).**
   - Vs30 = 360 m/s'de %10/50 PGA 0,43 g (Parker) ile 0,99 g (Youngs 1997) arasında; yaklaşık 2,3 kat.
   - Vs30 = 760 m/s'de 0,38–0,73 g.
   - Koddaki bağıntı (0,71 g) bu aralığın ortasında. Üç modern modelden ikisinin (BC Hydro, Parker) üstünde, Kuehn küresel sürümünün altında.
2. **Zemin etkisi (aynı model, 760 → 360 m/s).** Büyütme oranları:
   - Parker ×1,13
   - BC Hydro ×1,21
   - Kuehn ×1,26
   - kod bağıntısı ×1,30
   - Youngs (1997) ×1,50 (kaya ve zemin ayrı denklemler)
   
   Koddaki terim modern modellerin üst kesimine yakın.
3. **σ kesmesi.**
   - Kod bağıntısında ve Youngs (1997)'de σ'yı 3'te kesmek %10/50 değerini %17–22 düşürüyor. Modern modellerde düşüş yalnız %2–4.
   - Bu, kod ve Youngs (1997) sonuçlarının büyük ölçüde σ dağılımının uzak kuyruğuna (ε > 3) dayandığını gösteriyor.
   - Kaynak modeli M ≥ 5 için yılda 3 depremi tek ve sabit bir 58 km uzaklığa yerleştiriyor. Medyan yer hareketi düşük olduğu hâlde tasarım düzeyine yüksek ε'lu kuyruktan ulaşılıyor.
   - Bu doğrudan kaynak modeline bağlı ve B3–B4'te incelenecek.
4. **σ biçimi.** Kod bağıntısının σ'sı M 7,8'de Youngs (1997) ile birebir aynı (0,67). B1'deki şüpheyle tutarlı; makale görülmeden kesin karar verilmez.
5. **Kuehn küresel sürümü** M 7,8 ve 58 km için en yüksek medyanı (0,32 g) veriyor. Bölgesel kalibrasyonu olmayan, OpenQuake'te deneysel işaretli bir sürüm; ağırlık verilmeden önce ayrıca değerlendirilmeli.

## 4. Sınırlar ve sonraki adım

- Nokta kaynak, sabit uzaklık ve aynı MFD korundu; modern modellerin kırık geometrisine bağlı girdileri (ztor, odak derinliği) nokta kırıktan türetildi.
- **B3 (sonraki adım):** megathrust için fay düzlemi, Davao için fay ya da alan kaynağı. Aynı beş model ve iki Vs30 değeri. Geometrinin etkisi B2'den ayrı ölçülecek.
- **İstatistik tanımı:** B2'de mantık ağacı yok, her satır tek bir eğridir. Mantık ağacı kurulan sonraki aşamalarda (B3–B4) ortalama ve yüzdelikler **hem λ hem PoE uzayında** raporlanacak (Aşama A kararı; `A_job/A_RAPOR.md`).
- **GMPE ağırlıklandırması yapılmadı.** Ağırlıklar uygulanabilirlik gerekçesiyle ayrıca belirlenmeli (kullanıcı koşulu).

## Kaynaklar

- [IISEE GMPE başvurusu (Youngs vd. 1997 veri ve uygulama aralığı)](https://iisee.kenken.go.jp/eqflow/reference/1_5.htm)
- [Parker vd. (2022), Earthquake Spectra](https://journals.sagepub.com/doi/10.1177/87552930211034889)
- [Kuehn vd., PEER 2020/04](https://peer.berkeley.edu/sites/default/files/publications/2020_04_kuehn_final.pdf)
- [BC Hydro güncellemesi, PEER 2018/02](https://peer.berkeley.edu/node/1328)

## Yeniden çalıştırma

1. `python b2_duyarlilik.py` → `b2_sonuc.json`, `b2_egriler.npz`
2. `python b2_sekil.py` → `b2_sekil.png` / `.svg`

Ortam: openquake.engine 3.26.2.
