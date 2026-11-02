# Mindanao PSHA: mevcut kod ile OpenQuake karşılaştırması (doğrulama raporu)

Tarih: 2026-11-02. Dal: `psha-dogrulama`. Yalnız inceleme ve kavram kanıtıdır.
- EQ-Live (`index.html`), `main`, canlı site, seismo-report kodu ve yayımlanmış rapor değiştirilmedi.

**Amaç.** Aynı girdiler altında iki hesap motorunun sayısal olarak ne ölçüde uyuştuğunu sınamak:
- seismo-report'taki NumPy/SciPy kodu;
- OpenQuake hazardlib 3.26.2'nin klasik PSHA çekirdeği.

Motorların uyuşması kaynak modelinin ya da GMPE'nin bilimsel doğruluğunu kanıtlamaz. Bilimsel değerlendirme §6'da ayrı tutuldu.

## 1. Dondurulmuş kaynak

| Dosya | SHA-1 | Kaynak |
|---|---|---|
| `mindanao_psha.py` | 43342f92f5fa659e178ef216c5f2b341f8657c1b | seismo-report `cac09bf` (2026-06-10); çalışma ağacı temiz |
| `mindanao_logic_tree.py` | 3c12c798b3f50e195068bfdd583888fdc5543295 | aynı commit |

- Dosyaların salt-okunur kopyaları `kaynak_kod/` klasöründe.
- `referans_kod.py` bu kopyaları değiştirmeden geçici bir klasörde çalıştırır ve dizileri `referans_kod.npz`'ye kaydeder.
- Kod, rapordaki değerleri birebir üretiyor: %10/50 yıl medyan 0,759 g, 84. yüzdelik 1,140 g, ortalama 0,928 g.

## 2. Ortak girdi seti (`ortak_girdi.json`)

| Bileşen | Değer (iki hesapta aynı) |
|---|---|
| Site | General Santos City, Vs30 = 360 m/s |
| Kaynak 1: Cotabato megathrust | Episantral 46 km, derinlik 35,5 km → R = 58,11 km; b = 0,90; λ(M ≥ 5) = 3,0/yıl; Mmax 8,5 |
| Kaynak 2: Davao fay zonu | Episantral 120 km, derinlik 25 km → R = 122,58 km; b = 0,90; λ(M ≥ 5) = 1,0/yıl; Mmax 7,5 |
| FTLS kaynağı | Kaynak 1 geometrisi; b = 0,635; λ(M ≥ 5) = 500·10^(−0,635·1,5)·365/90 /yıl; Mmax 7,8 |
| MFD | Kesik G–R, ΔM = 0,2. Sınıf merkezleri ve oranları kodun `gr_occur` / `hazard_one` aritmetiğiyle aynı; OpenQuake'e `EvenlyDiscretizedMFD` olarak aynen verildi |
| GMPE | Koddaki bağıntı, OpenQuake'e özel GMPE olarak birebir taşındı (`kod_gmpe.py`, §3) |
| σ | Kesilmemiş normal; OpenQuake'te truncation_level = 99 |
| Mantık ağacı | 27 dal: b {0,635; 0,90; 1,12} × GMPE {Zt = 0; +0,5σ; Zt = 1} × Mmax {7,8; 8,0; 8,2}. Ağırlıklar ve yüzdelik yöntemi kodla aynı |
| IM | PGA, 0,005–3 g arasında logaritmik 200 düzey |
| Zaman | Poisson; karşılaştırma 50 yıllık PoE ile; λ = −ln(1 − PoE)/50 |

## 3. GMPE eşdeğerliği

- **OpenQuake'te karşılığı yok.** OpenQuake 3.26.2'deki 967 GMPE arasında Youngs vd. (1988) yok; yalnız Youngs vd. (1997) sürümleri var (`YoungsEtAl1997SInter`, `SSlab`, …).
- **Çözüm.** Koddaki bağıntı aynen kodlanıp OpenQuake'e özel bir GMPE sınıfı olarak verildi (`MindanaoKodGMPE`). Bu OpenQuake'in yerleşik bir modeli değil. Karşılaştırma (A) yalnız hesap motorlarını sınar.
- **Birincil kaynakla tutarlılık doğrulanamadı.**
  - Makale (Youngs, Day & Stevens 1988, ASCE GSP 20, s. 445–462) Zotero'da yok. Erişilen derlemeler katsayıları vermiyor.
  - Koddaki σ = 1,45 − 0,1M, OpenQuake'teki Youngs (1997) kaya PGA σ'sıyla (C4 = 1,45; C5 = −0,1) aynı. 1988 ortalamasının 1997 σ'sı ile birleştirilmiş olma olasılığı var; makale olmadan karar verilemez.
  - Zemin terimi 0,35·ln(760/Vs30) da yayının parçası olarak doğrulanamadı.
- **(B) eşdeğer değil.** Youngs (1997) ile koddaki bağıntı farklı modellerdir. (B) yalnız GMPE seçiminin etkisini gösterir; eşdeğer doğrulama olarak sunulmaz.

## 4. Sonuçlar (A): eşit model

Ayrıntılar `karsilastirma_sonuc.json` ve `karsilastirma_sekil.png` / `.svg` dosyalarında.

**Uzaklık eşitlemesi.**
- İlk denemede site episantral 46 km'ye konduğunda OpenQuake'in nokta kırıktan hesapladığı rrup 58,0008 km çıktı; kodda 58,1055 km.
- Site ve kaynak 2 konumu ikiye bölme yöntemiyle ayarlandı. Son durumda OpenQuake rrup = 58,1055 / 122,5765 km, koddaki R ile aynı.

**Eşitlemeden önceki etki** (50 yıllık PoE kuyruklarında 32 bit sınırı dahil): %10/50 yıl PGA farkı ≈ %0,1 (0,7034 / 0,7042 g).

| Eğri | %10/50 yıl PGA (g), kod / OpenQuake | %2/50 yıl PGA (g), kod / OpenQuake | En büyük göreli λ farkı |
|---|---|---|---|
| Cotabato medyan | 0,7034 / 0,7034 | 1,0423 / 1,0423 | %0,04 |
| Cotabato +1σ kayma | 1,6471 / 1,6471 | 2,4432 / 2,4432 | %0,0007 |
| Davao | 0,2591 / 0,2591 | 0,4002 / 0,4002 | %0,24 |
| İki kaynak toplam | 0,7062 / 0,7062 | 1,0448 / 1,0448 | %0,07 |
| FTLS | 1,8980 / 1,8980 | 2,5540 / 2,5540 | %0,001 |

**Mantık ağacı.**
- 27 dalın en büyük göreli λ farkı %0,08; ağırlıklı ortalamada %0,06.
- Rapordaki tablonun yeniden üretimi (PGA, g; kod / OpenQuake):

| Senaryo | 5. | 16. | 50. | 84. | 95. | Ortalama |
|---|---|---|---|---|---|---|
| %50/50 yıl | 0,3845 / 0,3845 | 0,4050 / 0,4050 | 0,4552 / 0,4552 | 0,6825 / 0,6825 | 0,7340 / 0,7340 | 0,5426 / 0,5426 |
| %10/50 yıl | 0,6555 / 0,6555 | 0,6861 / 0,6861 | 0,7590 / 0,7590 | 1,1398 / 1,1398 | 1,2360 / 1,2360 | 0,9284 / 0,9284 |
| %2/50 yıl | 0,9801 / 0,9801 | 1,0193 / 1,0193 | 1,1119 / 1,1119 | 1,6741 / 1,6741 | 1,8244 / 1,8244 | 1,3872 / 1,3872 |

**Farkların nedeni.**
- OpenQuake olasılık matrislerini 32 bit kayan noktada tutuyor (`hazardlib/map_array.py`, `F32`).
- Bu yüzden çok küçük PoE değerlerinde (kuyruk) ve 1'e çok yakın PoE değerlerinde göreli hassasiyet düşüyor.
- Karşılaştırma bu nedenle 50 yıllık PoE 10⁻⁵–0,999 aralığıyla sınırlandı.
- 1 yıllık ve 0,001 yıllık zaman aralıklarıyla yapılan ön denemeler de aynı yorumu destekledi: PoE küçüldükçe fark büyüyor.
- Model ya da integrasyon kaynaklı bir fark bulunmadı.

**Sonuç.** Aynı model ve geometri altında iki motor tasarım düzeylerinde dört ondalık basamağa kadar aynı sonucu veriyor. Mevcut kodun hesap motoru (oran ayrıklaştırması, aşılma integrali, mantık ağacı ortalaması ve yüzdelikleri) OpenQuake çekirdeğiyle tutarlı.

**Bu karşılaştırmanın kapsamı.** Kullanılan, OpenQuake'in klasik hesap fonksiyonu (`calc_hazard_curves`) oldu; `job.ini` ile tam motor akışı çalıştırılmadı.

## 5. Model duyarlılığı (B): EŞDEĞER DEĞİL

Aynı kaynaklar OpenQuake'in yerleşik `YoungsEtAl1997SInter` modeliyle hesaplandı: kaya koşulu, Vs30 terimi yok, odak derinliği terimi var.

| Hesap | %10/50 yıl PGA (g) | %2/50 yıl PGA (g) |
|---|---|---|
| Cotabato medyan, koddaki bağıntı | 0,703 | 1,042 |
| Cotabato medyan, Youngs (1997) | 0,993 | 1,475 |
| Mantık ağacı ortalaması, koddaki bağıntı (27 dal) | 0,928 | 1,387 |
| b × Mmax dalları ortalaması, Youngs (1997) (9 dal) | 1,066 | 1,571 |

- Son iki satır aynı mantık ağacı değil: (B)'de epistemik GMPE dalları yok. Doğrudan karşılaştırılamaz.
- Bu tablo **GMPE + zemin koşulu birleşik duyarlılığını** gösterir (2026-11-02 düzeltmesi): koddaki bağıntı Vs30 = 360 m/s için ≈ ×1,30 zemin büyütmesi içeriyor, Youngs (1997) hesabı kaya koşulunda ve büyütmesiz. 0,703 → 0,993 g (≈ %41) farkı yalnız GMPE etkisi olarak sunulamaz; aynı zemin koşulunda fark daha büyük olurdu. Saf GMPE duyarlılığı Aşama B2'de Vs30'u doğrudan alan modellerle ölçülür. Her durumda bu duyarlılık, iki hesap motoru arasındaki farktan dört basamak büyüktür.

## 6. Bilimsel değerlendirme (ayrı konu; motor karşılaştırmasından bağımsız)

%10/50 yıl PGA ≈ 0,76 g (medyan) / 0,93 g (ortalama) bu karşılaştırmayla doğrulanmış sayılmamalıdır; raporun mevcut sonucu olarak kalır.

1. **Kaynak geometrisi.**
   - Megathrust ve Davao fayı tek, sabit uzaklıkta nokta kaynak olarak modellenmiş.
   - Gerçek PSHA'da kırıklar kaynak alanı ya da fay düzlemi boyunca dağıtılır, büyüklüğe göre kırık boyutu ve uzaklık dağılımı integre edilir. Sabit R = 58 km varsayımı, yakın ve uzak kırıkların katkısını temsil etmez.
2. **Zemin (Vs30) terimi.** 0,35·ln(760/Vs30) yayımlanmış GMPE'nin parçası olarak doğrulanamadı. Youngs vd. kaya ve zemin için ayrı katsayılar verir, sürekli bir Vs30 terimi vermez.
3. **σ'nın kaynağı.** σ = 1,45 − 0,1M, Youngs (1997) kaya PGA formuyla aynı (§3). 1988 ortalaması ile 1997 σ'sının karışmış olma olasılığı birincil kaynakla sınanmalı.
4. **Epistemik belirsizlik.** "+0,5σ" ve "+1σ / +2σ" eğrileri medyanı σ kadar kaydırıp aleatorik σ'yı yeniden integre ediyor. Bu, aleatorik belirsizliğin epistemik dal olarak ikinci kez sayılmasına yakın. Standart yaklaşım, alternatif GMPE'leri ağırlıklandırmak ya da medyan ölçekleme belirsizliğini ayrı (σ_μ) modellemektir.
5. **FTLS kaynağı ve b = 0,635 dalı.**
   - Artçı dizisinin 90 günlük oranı yıllığa çevrilip uzun dönem kaynağı gibi kullanılmış. Mantık ağacında da artçı dizisi b'si (0,635) 0,60 ağırlıkla yer alıyor.
   - Zamandan bağımsız PSHA ayıklanmış, durağan bir Poisson oranı varsayar. Artçı dizisi etkisi zamana bağlı (ör. ETAS / Omori) bir modelle ayrıca ele alınmalı.
6. **Mmax.**
   - Mmax = 7,8 "gözlenen" etiketiyle 0,50 ağırlık alıyor. Bu, Mmax'ı gözlenen en büyük büyüklüğe eşitleme anlamına gelir; aşama 5'te kabul ettiğiniz ilkeyle çelişir.
   - Ayrıca mantık ağacı şeklindeki dal ve panel etiketleri (Mmax 8,0/8,5/9,0; "Mmax = 8,5 sabit") kodla (7,8/8,0/8,2; 8,0) uyumsuz.
7. **GMPE seçimi.** Tek GMPE ailesi kullanılmış. (B), modern subdüksiyon modelleriyle önemli fark olabileceğini gösteriyor. Örnekler: BC Hydro (Abrahamson vd. 2016; `AbrahamsonEtAl2015SInter`), Parker vd. (2022; `ParkerEtAl2020SInter`), Kuehn vd. (2023; `KuehnEtAl2020SInter`); üçü de OpenQuake 3.26.2'de mevcut (doğrulandı).

## 6b. Aşama A tamamlandı (2026-11-02)

`job.ini` ile tam OpenQuake motor akışı çalıştırıldı: `A_job/A_RAPOR.md`.
- Motor sonuçları mevcut koda göre en büyük göreli λ farkı ≈ 5·10⁻⁶; tasarım düzeyleri beş anlamlı basamakta aynı.
- Tanım farkı belgelendi: mantık ağacı ortalaması OpenQuake'te PoE üzerinden, kodda λ üzerinden alınıyor (%10/50: 0,915 / 0,928 g).

## 7. Sonraki adım seçenekleri (karar sizin)

- **(i)** Youngs vd. (1988) makalesini Zotero'ya eklemek; §3'ün denklem ve σ doğrulamasını tamamlamak.
- **(ii)** `job.ini` ile tam OpenQuake motor akışını çalıştırmak (özel GMPE'yi kayıtlı modül olarak). Böylece sonuç, hesap fonksiyonunun ötesinde tam motor akışıyla da doğrulanmış olur.
- **(iii)** Gerçekçi model için ayrı bir duyarlılık çalışması. Bu, motor doğrulaması değil, model incelemesidir:
  - alan ve fay kaynağı geometrisi;
  - modern GMPE mantık ağacı;
  - ayıklanmış oranlar;
  - Mmax senaryoları.

## Dosyalar

- `referans_kod.py`: dondurulmuş kodu çalıştırır.
- `kod_gmpe.py`: özel GMPE.
- `oq_karsilastirma.py`: (A) ve (B) hesapları.
- `sekiller.py`: grafikler.
- `ortak_girdi.json`: ortak girdi seti.
- `karsilastirma_sonuc.json`: sonuç sayıları.
- `referans_kod.npz` ve `oq_egriler.npz`: eğri dizileri.

**Ortam.** Python 3.13 sanal ortamı, openquake.engine 3.26.2. GDAL kurulamadı; OpenQuake hesap çekirdeği GDAL gerektirmiyor.

**Yeniden çalıştırma:** `python referans_kod.py && python oq_karsilastirma.py && python sekiller.py`.
