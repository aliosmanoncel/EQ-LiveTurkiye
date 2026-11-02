# Aşama B3: kaynak geometrisi duyarlılık analizi (model değerlendirmesi)

Tarih: 2026-11-02. Dal: `psha-dogrulama`.

**Bu bir model duyarlılık çalışmasıdır, doğrulama değildir.** Hiçbir PGA değeri doğrulanmış tehlike değeri değildir. Bir sonlu fay modelinin nokta kaynaktan farklı PGA üretmesi, onun daha doğru olduğunu göstermez. Geometrik gerçekçilik, kaynak parametrelerinin güvenilirliği ve GMPE'nin bölgesel uygulanabilirliği ayrıca değerlendirilmelidir.

**Bilimsel soru.** General Santos için hesaplanan tehlike düzeyleri, kaynak geometrisinin nokta kaynaktan sonlu fay ya da alan kaynağına dönüştürülmesine ne ölçüde duyarlı?

## 1. Tasarım

**Sabit tutulanlar** (B2 ile aynı):
- beş GMPE;
- Vs30 = 360 ve 760 m/s;
- MFD sınıf oranları (`A_job/oranlar.json`, kodun aritmetiği);
- Mmax, toplam oranlar ve Poisson modeli;
- σ kesilmemiş (3σ sonuçları `b3_sonuc.json`'da).

**Değişen yalnız geometri.** Fay kaynağının toplam yıllık oranı nokta kaynağınkiyle aynı (göreli fark 0).

**Konum verisi** raporun olay kaydından alındı:
- W-faz santroidi 5,68°K 125,06°D, derinlik 35,5 km;
- düğüm düzlemleri 359°/47°/103° ve 161°/45°/77°;
- site General Santos, 6,1164°K 125,1716°D (santroide episantral uzaklık 50,1 km).

| Kaynak | Geometri | Tanım |
|---|---|---|
| Cotabato | P0 | B2 nokta kaynağı, göreli geometri, rrup = 58,1 km. **Yüzde değişimlerin tabanı.** |
| Cotabato | P1 | Aynı nokta kaynak, gerçek koordinatta; rrup = 61,3 km |
| Cotabato | F | Sonlu fay: doğrultu 359°, doğuya eğim 47° (NP2; doğuya dalan Cotabato arayüzüyle uyumlu), santroidden geçiyor; derinlik 10–60 km; doğrultu boyunca 300 km. Strasser vd. (2010) arayüz büyüklük–alan bağıntısı (MSR), en-boy oranı 2; kırıklar düzlem boyunca kayar. Kırık sayısı 47 373; rrup en az 33,8 km, oran ağırlıklı medyan 77,9 km, oran ağırlıklı ortalama 89,5 km |
| Cotabato | F2 | Aynı düzlem, eğim 30° (arayüzler için daha tipik eğim). Duyarlılık senaryosu |
| Davao | P0 | B2 nokta kaynağı (120 km, 25 km derinlik) |
| Davao | Görüş hattına dik fay | Düşey, doğrultu atımlı, 100 km, merkezi 120 km'de, site–kaynak görüş hattına dik; WC1994 MSR |
| Davao | Görüş hattına paralel fay | Aynı fay, görüş hattına paralel |
| Davao | Alan | Alan kaynağı, merkez 120 km, yarıçap 40 km, odak derinliği 25 km; WC1994 MSR |

Davao kaynağının kodda konumu ya da mekanizması tanımlı değil, yalnız bir uzaklığı var (R = √(120² + 25²)). Bu yüzden iki fay yönelimi alt ve üst sınır olarak, alan kaynağı da ayrı bir alternatif olarak hesaplandı. **Üç Davao alternatifi birleştirilmedi.**

## 2. Geometri etkisi: %10/50 ve %2/50 yıl

Şekil: `b3_sekil.png` / `.svg`.

**Cotabato, Vs30 = 360 m/s** — hücre: %10/50 · %2/50 PGA (g) [P0'a göre %10/50 değişimi]

| Model | P0 nokta (B2) | P1 nokta, gerçek konum | F fay, eğim 47° | F2 fay, eğim 30° |
|---|---|---|---|---|
| Kod bağıntısı | 0,703 · 1,042 | 0,679 · 1,007 [−3%] | 0,714 · 1,080 [+1%] | 0,685 · 1,036 [−3%] |
| Youngs (1997) | 0,993 · 1,475 | 0,931 · 1,385 [−6%] | 1,176 · 1,796 [+18%] | 1,086 · 1,661 [+9%] |
| BC Hydro (2016) | 0,539 · 0,940 | 0,511 · 0,895 [−5%] | 0,772 · 1,380 [+43%] | 0,714 · 1,280 [+33%] |
| Parker (2022) küresel | 0,429 · 0,720 | 0,404 · 0,679 [−6%] | 0,633 · 1,105 [+48%] | 0,579 · 1,014 [+35%] |
| Kuehn (2023) küresel | 0,917 · 1,587 | 0,857 · 1,488 [−7%] | 1,010 · 1,730 [+10%] | 1,007 · 1,736 [+10%] |

**Cotabato, Vs30 = 760 m/s** — hücre: %10/50 · %2/50 PGA (g) [P0'a göre %10/50 değişimi]

| Model | P0 nokta (B2) | P1 nokta, gerçek konum | F fay, eğim 47° | F2 fay, eğim 30° |
|---|---|---|---|---|
| Kod bağıntısı | 0,542 · 0,802 | 0,523 · 0,775 [−3%] | 0,549 · 0,831 [+1%] | 0,527 · 0,797 [−3%] |
| Youngs (1997) | 0,662 · 0,981 | 0,617 · 0,916 [−7%] | 0,795 · 1,215 [+20%] | 0,729 · 1,114 [+10%] |
| BC Hydro (2016) | 0,444 · 0,792 | 0,420 · 0,749 [−6%] | 0,683 · 1,253 [+54%] | 0,624 · 1,147 [+40%] |
| Parker (2022) küresel | 0,380 · 0,664 | 0,356 · 0,623 [−6%] | 0,599 · 1,095 [+57%] | 0,541 · 0,992 [+42%] |
| Kuehn (2023) küresel | 0,729 · 1,292 | 0,675 · 1,200 [−7%] | 0,811 · 1,415 [+11%] | 0,812 · 1,425 [+11%] |

**Davao, Vs30 = 360 m/s** — hücre: %10/50 · %2/50 PGA (g) [P0'a göre %10/50 değişimi]

| Model | P0 nokta (B2) | fay ⊥ görüş hattı | fay ∥ görüş hattı | alan, r = 40 km |
|---|---|---|---|---|
| Kod bağıntısı | 0,259 · 0,400 | 0,260 · 0,401 [+0%] | 0,315 · 0,495 [+22%] | 0,293 · 0,459 [+13%] |
| Youngs (1997) | 0,229 · 0,363 | 0,214 · 0,341 [−6%] | 0,304 · 0,493 [+33%] | 0,292 · 0,478 [+28%] |
| BC Hydro (2016) | 0,097 · 0,169 | 0,099 · 0,173 [+2%] | 0,137 · 0,247 [+42%] | 0,128 · 0,235 [+33%] |
| Parker (2022) küresel | 0,080 · 0,135 | 0,082 · 0,139 [+2%] | 0,120 · 0,211 [+51%] | 0,111 · 0,198 [+39%] |
| Kuehn (2023) küresel | 0,101 · 0,179 | 0,061 · 0,104 [−40%] | 0,097 · 0,174 [−4%] | 0,115 · 0,211 [+14%] |

**Davao, Vs30 = 760 m/s** — hücre: %10/50 · %2/50 PGA (g) [P0'a göre %10/50 değişimi]

| Model | P0 nokta (B2) | fay ⊥ görüş hattı | fay ∥ görüş hattı | alan, r = 40 km |
|---|---|---|---|---|
| Kod bağıntısı | 0,199 · 0,308 | 0,200 · 0,309 [+0%] | 0,242 · 0,381 [+22%] | 0,225 · 0,353 [+13%] |
| Youngs (1997) | 0,143 · 0,225 | 0,134 · 0,212 [−6%] | 0,197 · 0,319 [+38%] | 0,186 · 0,303 [+30%] |
| BC Hydro (2016) | 0,072 · 0,127 | 0,074 · 0,130 [+2%] | 0,103 · 0,188 [+43%] | 0,097 · 0,179 [+34%] |
| Parker (2022) küresel | 0,062 · 0,108 | 0,064 · 0,111 [+2%] | 0,096 · 0,173 [+54%] | 0,088 · 0,162 [+41%] |
| Kuehn (2023) küresel | 0,070 · 0,125 | 0,042 · 0,072 [−41%] | 0,067 · 0,121 [−4%] | 0,080 · 0,148 [+14%] |

### Gözlemler

1. **P1 (gerçek konum).** Uzaklık 58,1 → 61,3 km; bütün modellerde −3 ile −7 %. Göreli geometri ile gerçek koordinat arasındaki fark küçük.
2. **Cotabato sonlu fay (F).** Geometri etkisi büyük ölçüde GMPE'ye bağlı:
   - kod bağıntısı +1 %;
   - Kuehn +10–11 %;
   - Youngs (1997) +18–20 %;
   - BC Hydro +43–54 %;
   - Parker +48–57 %.
   
   Eğim 30° olunca artış azalıyor (Parker +35–42 %); site bu durumda düzlemin daha derin kısmının üstünde kalıyor.
3. **Davao.**
   - Görüş hattına paralel fay ve alan kaynağı, sitenin yakınına da kırık yerleştirdiği için PGA'yı artırıyor (+13 ile +54 %). Görüş hattına dik fay nokta kaynağa yakın sonuç veriyor.
   - Kuehn'de dik fay −40 % veriyor. Bu bir model–geometri uyumsuzluğu: Kuehn kırık üst derinliğine (ztor) duyarlı, düşey fayın ztor değeri 0 km, nokta kaynağınki 25 km. Ayrıca Davao'ya bir subdüksiyon **arayüz** GMPE'si uygulanıyor (koddan devralındı). Bu sonuç geometri etkisi olarak yorumlanmamalı.
4. **%10/50 yılda tehlikeye katkı.** Davao'nun katkısı Cotabato'dan çok küçük: Vs30 360'ta Davao 0,06–0,32 g, Cotabato 0,40–1,18 g.

## 3. Geometri etkisi neden GMPE'ye bağlı: uzaklık ölçeklenmesi

**Uzaklık ölçeklenmesi (Vs30 760, ztor 35 km): medyan PGA (g) rrup 30 / 60 / 90 / 120 km ve 30→120 km oranı**

| Model | M 6,0 | oran | M 7,8 | oran |
|---|---|---|---|---|
| Kod bağıntısı | 0,054 / 0,038 / 0,028 / 0,020 | 2,6 | 0,163 / 0,122 / 0,092 / 0,071 | 2,3 |
| Youngs (1997) | 0,108 / 0,048 / 0,026 / 0,016 | 6,9 | 0,216 / 0,141 / 0,098 / 0,071 | 3,1 |
| BC Hydro (2016) | 0,039 / 0,016 / 0,009 / 0,006 | 6,7 | 0,317 / 0,165 / 0,104 / 0,073 | 4,3 |
| Parker (2022) küresel | 0,043 / 0,017 / 0,009 / 0,005 | 7,8 | 0,245 / 0,117 / 0,069 / 0,044 | 5,6 |
| Kuehn (2023) küresel | 0,085 / 0,027 / 0,013 / 0,007 | 11,8 | 0,591 / 0,250 / 0,136 / 0,084 | 7,0 |

- Kod bağıntısının medyanı 30 km'den 120 km'ye yalnız 2,3–2,6 kat azalıyor; modern modellerde bu oran 4,3–11,8.
- Bunun nedeni denklemdeki 205,5·e^(0,0968M) teriminin çok büyük olması: M 5–8 için yaklaşık 340–450 km. Bu yüzden uzaklık 34 ile 90 km arasında değişse de PGA az değişiyor ve sonlu fay, nokta kaynakla hemen hemen aynı sonucu veriyor.
- Modern modellerde yakın kırıklar baskın olduğu için fay geometrisi tehlikeyi belirgin biçimde artırıyor.
- **B1 için not.** Bu kadar zayıf bir yakın alan uzaklık bağımlılığı, koddaki katsayıların özgün Youngs (1988) denklemine uygunluğunun birincil kaynakla sınanması gerektiğini bir kez daha gösteriyor. Bu bir bulgudur, hüküm değildir.

## 4. Vs30 etkisi (kaynak geometrisinden ayrı bulgu)

### 4.1 GMPE zemin tepkisi uygunluk tablosu

Kaynak: OpenQuake 3.26.2 kaynak kodu.

| Model | Zemin terimi | Doğrusal olmayan zemin | Modelin referans kayası | 360 m/s'nin dayanağı | Sınıf |
|---|---|---|---|---|---|
| Kod bağıntısı | 0,35·ln(760/Vs30), doğrusal | Yok | Tanımsız; terim denkleme sonradan eklenmiş | Kaynağı doğrulanmadı (B1) | Harici düzeltmeye benzer, kaynağı belirsiz |
| Youngs (1997) | Sürekli Vs30 yok; kaya ve zemin için iki ayrı denklem | Yok | Kaya sınıfı | 760 m/s eşiği OpenQuake'in uzlaşımı; yayında Vs30 tanımı yok | Ayrık sınıflı zemin modeli |
| BC Hydro (2016) | Vs30'a bağlı doğrusal terim (vlin) | Var, PGA₁₀₀₀'e bağlı | Vs30 = 1000 m/s | Modelin kendi zemin modeli | Modelin kendi zemin modeli |
| Parker (2022) | Vs30'a bağlı doğrusal terim | Var | Vs30 = 760 m/s | Modelin kendi zemin modeli | Modelin kendi zemin modeli |
| Kuehn (2023) | Vs30'a bağlı doğrusal terim | Var, PGA₁₁₀₀'e bağlı | Vs30 = 1100 m/s | Modelin kendi zemin modeli | Modelin kendi zemin modeli |

**760 m/s her modelin referans kayası değil.** Yalnız Parker'da referans koşul. BC Hydro ve Kuehn için 760 m/s de kendi referans kayalarına göre büyütülmüş bir zemin koşuludur. Youngs (1997)'de 360 m/s ile 760 m/s iki ayrı denklemden hesaplanır. Bu yüzden aşağıdaki farklar beş modelde aynı fiziksel büyüklüğü ölçmez.

Harici bir zemin büyütme modeli (kaya hareketi × büyütme katsayısı) uygulanmadı. Uygulanırsa ayrı bir model varsayımı olarak raporlanmalı.

### 4.2 Mutlak ve yüzde fark

**Vs30 etkisi: PGA(360) − PGA(760) (g) ve ΔPGA(%) = (PGA₃₆₀ − PGA₇₆₀)/PGA₇₆₀ × 100, %10/50 yıl** (hücre: mutlak fark [yüzde])


Cotabato:

| Model | P0 nokta (B2) | P1 nokta, gerçek konum | F fay, eğim 47° | F2 fay, eğim 30° |
|---|---|---|---|---|
| Kod bağıntısı | +0,162 [+30%] | +0,156 [+30%] | +0,164 [+30%] | +0,158 [+30%] |
| Youngs (1997) | +0,332 [+50%] | +0,314 [+51%] | +0,381 [+48%] | +0,357 [+49%] |
| BC Hydro (2016) | +0,094 [+21%] | +0,092 [+22%] | +0,089 [+13%] | +0,090 [+15%] |
| Parker (2022) küresel | +0,049 [+13%] | +0,048 [+14%] | +0,034 [+6%] | +0,038 [+7%] |
| Kuehn (2023) küresel | +0,188 [+26%] | +0,181 [+27%] | +0,199 [+25%] | +0,195 [+24%] |

Davao:

| Model | P0 nokta (B2) | fay ⊥ görüş hattı | fay ∥ görüş hattı | alan, r = 40 km |
|---|---|---|---|---|
| Kod bağıntısı | +0,060 [+30%] | +0,060 [+30%] | +0,072 [+30%] | +0,067 [+30%] |
| Youngs (1997) | +0,086 [+61%] | +0,080 [+60%] | +0,107 [+54%] | +0,106 [+57%] |
| BC Hydro (2016) | +0,024 [+34%] | +0,025 [+34%] | +0,033 [+32%] | +0,031 [+32%] |
| Parker (2022) küresel | +0,018 [+28%] | +0,018 [+28%] | +0,024 [+26%] | +0,023 [+26%] |
| Kuehn (2023) küresel | +0,031 [+44%] | +0,019 [+45%] | +0,030 [+44%] | +0,035 [+43%] |

**%2/50 yıl ΔPGA(%)** (Cotabato P0 → F; Davao P0 → paralel fay):

| Model | Cotabato P0 | Cotabato F | Davao P0 | Davao paralel fay |
|---|---|---|---|---|
| Kod bağıntısı | +30% | +30% | +30% | +30% |
| Youngs (1997) | +50% | +48% | +61% | +55% |
| BC Hydro (2016) | +19% | +10% | +33% | +31% |
| Parker (2022) küresel | +8% | +1% | +25% | +22% |
| Kuehn (2023) küresel | +23% | +22% | +44% | +43% |

### 4.3 Vs30 etkisi geometriye göre değişiyor mu?

- **Doğrusal ya da ayrık zemin terimli modellerde neredeyse değişmiyor.**
  - Kod bağıntısında her geometride +30 %. Terim doğrusal ve sabit olduğu için bu bir modelleme sonucudur, fiziksel bir bulgu değildir.
  - Youngs (1997)'de +48 ile +61 %. Değer kaynağa göre değişiyor (Cotabato yaklaşık +50 %, Davao yaklaşık +57 %), çünkü kaya ve zemin denklemlerinin büyüklük ve uzaklık ölçeklenmesi farklı.
- **Doğrusal olmayan zemin terimli modellerde değişiyor.**
  - BC Hydro ve Parker'da büyütme, sarsıntı düzeyi arttıkça azalıyor. Cotabato'da P0'dan F'ye geçişte BC Hydro +21 → +13 %, Parker +13 → +6 % (%2/50'de Parker +8 → +1 %). Davao'nun daha zayıf sarsıntısında +26 ile +34 %.
  - Kuehn'de Cotabato yaklaşık +25 %, Davao yaklaşık +44 %.
  - Yani Vs30 etkisi geometriye bağlıdır, ama bunun nedeni geometrinin kendisi değil, geometrinin değiştirdiği sarsıntı düzeyidir.
- **Soruya yanıt.** 760 m/s yerine 360 m/s kullanmak %10/50 PGA'yı modele, kaynağa ve geometriye göre +6 ile +61 % (+0,02 ile +0,38 g) artırıyor.
- **Hangi Vs30 sahayı temsil ediyor?** Ölçülmüş yerel Vs30 verisi olmadan söylenemez. 360 m/s, raporun kendi varsayımıdır ("Sarangani kıyı dolgusu").

## 5. Mantık ağacı: P0 ve sonlu fay

27 dal, kod bağıntısı, Vs30 360 m/s. Ortalama λ ve PoE uzaylarında ayrı ayrı verildi (Aşama A kararı).

**Mantık ağacı (27 dal, kod bağıntısı, Vs30 360): P0 ve F** (g)

| Senaryo | Geometri | Ortalama, λ uzayı | Ortalama, PoE uzayı | 16. (λ / PoE) | 50. (λ / PoE) | 84. (λ / PoE) |
|---|---|---|---|---|---|---|
| %10/50 | P0 | 0,928 | 0,915 | 0,686 / 0,686 | 0,759 / 0,759 | 1,140 / 1,140 |
| %10/50 | F | 0,948 | 0,934 | 0,677 / 0,677 | 0,789 / 0,789 | 1,158 / 1,158 |
| %2/50 | P0 | 1,387 | 1,383 | 1,019 / 1,019 | 1,112 / 1,112 | 1,674 / 1,674 |
| %2/50 | F | 1,442 | 1,437 | 1,026 / 1,026 | 1,174 / 1,174 | 1,728 / 1,728 |

Kod bağıntısıyla sonlu fay mantık ağacı sonucunu yalnız %2–6 değiştiriyor. Bunun nedeni §3'teki zayıf uzaklık bağımlılığı. Modern GMPE'lerle kurulacak bir mantık ağacında geometri etkisi çok daha büyük olur.

## 6. Yorum ve sınırlar

1. **Soruya yanıt.**
   - Duyarlılık GMPE'ye bağlı. Kod bağıntısıyla Cotabato'da ≤ ±3 %; modern GMPE'lerle +10 ile +57 %.
   - Davao'da alternatiflere göre −6 ile +54 % (Kuehn'in dik fay sonucu bir model uyumsuzluğu, §2).
   - Nokta kaynak varsayımı, modern GMPE'lerle tehlikeyi %10/50 yılda 1,4–1,6 kata kadar düşük tahmin edebilir.
2. **Bu sonuç sonlu fayın doğru olduğunu göstermez.** Fay boyutları (300 km, 10–60 km), eğim (47° ya da 30°) ve MSR seçimi kaynaklarla sınanmadı. Megathrust geometrisi için Slab2 ve PHIVOLCS aktif fay verisi kullanılmadı.
3. **Davao kaynağının konumu ve mekanizması tanımsız.** Sonuçlar alternatifler arası aralık olarak okunmalı. Davao'ya arayüz GMPE'si uygulanması da ayrı bir model sorunu.
4. **Sabit tutulanlar, B4'te ayrıca incelenecek konular:**
   - M ≥ 5 için yılda 3 deprem;
   - FTLS dalı;
   - Mmax'ın gözlenen değere eşit olması.
5. **GMPE ağırlıklandırması yapılmadı.**

## Dosyalar

- `b3_geometri.py` → `b3_sonuc.json` ve `egri_*.npy`.
- `b3_vs30_tani.py` → `b3_vs30_tani.json`.
- `b3_sekil.py` → `b3_sekil.png` / `.svg`.

Ortam: openquake.engine 3.26.2. Sağlama: P0, kod bağıntısı ve Vs30 360 için 0,70338 g; mantık ağacı λ ortalaması 0,92838 g. İkisi de Aşama A ile aynı.
