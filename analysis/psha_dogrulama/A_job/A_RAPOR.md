# Mindanao PSHA – Aşama A: Hesaplama Motorunun Sayısal Doğrulanması

**Dondurulmuş belge (2026-11-02).** Kullanıcı kararıyla Aşama A tamamlandı ve bu rapor değiştirilmeyecek doğrulama belgesi olarak saklanıyor.
- İçerdiği dosyaların SHA-256 değerleri `MANIFEST_A.txt`'te.
- Aşama B (bilimsel model değerlendirmesi) bundan bağımsız raporlanır (`../B2_gmpe/`, …).
- Bu belge yalnız şu soruyu yanıtlar: hesaplama algoritması doğru çalışıyor mu? Kullanılan modellerin güvenilirliği ve sonuçların gerçek tehlikeyi temsil edip etmediği bu belgenin kapsamı dışındadır.

## Karar tablosu

| Kontrol | Sonuç |
|---|---|
| Ortak girdiler | Başarılı |
| GMPE eşleştirmesi (özel GMPE, birebir kopya) | Başarılı |
| Tekil kaynak hesapları | Başarılı |
| Kaynakların toplanması | Başarılı |
| Mantık ağacı (27 dal) | Başarılı |
| Tam OpenQuake motor akışı | Başarılı |
| Ortalama ve yüzdelik tanımı | Yöntem farkı belirlendi; iki tanım da korunur (aşağıda) |
| Modelin bilimsel doğruluğu | Bu aşamanın kapsamı dışında, doğrulanmadı |

---


Tarih: 2026-11-02. Dal: `psha-dogrulama`. Bu rapor yalnız hesap doğrulamasıdır; model değerlendirmesi Aşama B'dedir. Hiçbir PGA değeri doğrulanmış tehlike değeri olarak sunulmaz.

## Sonuç

Aşama A tamamlandı. Kullanıcının üç koşulu sağlandı:

1. **Aynı girdi dosyaları kullanıldı.**
   - Geometri `karsilastirma_sonuc.json`'daki eşitlenmiş site ve kaynak konumlarından, MFD oranları kodun aritmetiğinden üretildi (`girdi_uret.py`, `oranlar.json`).
   - Bağımsız yeniden hesapla birebir aynı: `girdi_denetimi`: `c1_med_s1` doğru, `lt_dallari` doğru.
   - GMPE, aynı `kod_gmpe.MindanaoKodGMPE` sınıfı; OpenQuake GMPE paketine kayıtlı kopya.
2. **Tam motor akışı başarıyla tamamlandı.** Altı hesap `oq engine --run job.ini` ile, `classical` kipinde çalıştı (calc 8–13). Mantık ağacı motorda 9 kaynak modeli dalı × 3 GMPE dalı = 27 gerçekleşme olarak kuruldu; ağırlıklar kodla aynı.
3. **İki bağımsız referansla karşılaştırıldı:** mevcut kod (`referans_kod.npz`) ve önceki `calc_hazard_curves` sonucu (`oq_egriler.npz`).

## Tekil eğriler

Karşılaştırma aralığı 50 yıllık PoE 10⁻⁵–0,999.

| Eğri | En büyük göreli λ farkı: motor / kod | Motor / calc_hazard_curves | %10/50 PGA (g): motor · kod · chc | %2/50 PGA (g): motor · kod · chc |
|---|---|---|---|---|
| Cotabato medyan | 5,2·10⁻⁶ | 3,8·10⁻⁴ | 0,70338 · 0,70338 · 0,70338 | 1,04229 · 1,04229 · 1,04229 |
| Cotabato +1σ kayma | 4,2·10⁻⁶ | 1,1·10⁻⁵ | 1,64713 · 1,64712 · 1,64712 | 2,44324 · 2,44324 · 2,44324 |
| Davao | 3,3·10⁻⁶ | 2,4·10⁻³ | 0,25910 · 0,25910 · 0,25910 | 0,40016 · 0,40016 · 0,40016 |
| İki kaynak toplam | 5,1·10⁻⁶ | 7,0·10⁻⁴ | 0,70615 · 0,70615 · 0,70615 | 1,04481 · 1,04481 · 1,04481 |
| FTLS | 5,1·10⁻⁶ | 1,0·10⁻⁵ | 1,89803 · 1,89803 · 1,89803 | 2,55403 · 2,55402 · 2,55402 |

Tam motor akışı mevcut koda `calc_hazard_curves`'tan daha yakın. Olası açıklama: motor sonuçları oran haritası (RateMap) olarak tutup sonradan olasılığa çeviriyor. `calc_hazard_curves` ise doğrudan 32 bit PoE dizisi döndürüyor. Bu farkın kaynağı kod düzeyinde ayrıca incelenmedi; iki yol da tasarım düzeylerinde aynı sonucu veriyor.

## Mantık ağacı (27 gerçekleşme)

- Dallar kodla eşleşiyor: en büyük göreli λ farkı 5,5·10⁻⁶. OpenQuake GMPE dal kimliklerini gA0/gB0/gC0 olarak yeniden adlandırdığı için eşleme GMPE parametrelerinden (Zt, eps) yapıldı.
- %10/50 yıl PGA (g):

| İstatistik | Mevcut kod | OpenQuake motoru (hcurves-stats) | Motor gerçekleşmelerinden λ ortalaması |
|---|---|---|---|
| 5. | 0,65551 | 0,65551 | — |
| 16. | 0,68606 | 0,68602 | — |
| 50. | 0,75905 | 0,75905 | — |
| 84. | 1,13981 | 1,13981 | — |
| 95. | 1,23599 | 1,23557 | — |
| Ortalama | **0,92838** | **0,91473** | 0,92838 |

### İstatistik tanımları (iki seçenek de korunur)

Mantık ağacı istatistikleri iki uzayda tanımlanabilir. **Hiçbiri diğerine dönüştürülmez; raporlarda hangi uzayın kullanıldığı her zaman belirtilir.**

| Tanım | Ortalama | Yüzdelik | Kullanan |
|---|---|---|---|
| λ uzayı | λ̄ = Σ wᵢ λᵢ (yıllık aşılma oranı) | Her IM düzeyinde λᵢ değerleri üzerinde | Mevcut kod |
| PoE uzayı | P̄(T) = Σ wᵢ Pᵢ(T), Pᵢ = 1 − e^(−λᵢT), T = 50 yıl | Her IM düzeyinde Pᵢ(T) üzerinde | OpenQuake `hcurves-stats` |

**Yüzdelik algoritması iki yazılımda aynı.** Kaynaklar: `openquake.hazardlib.stats.quantile_curve` ve `mindanao_logic_tree.py` §4. Her IM düzeyinde:
1. **Sıralama:** dal değerleri artan sırada dizilir; her değer kendi ağırlığını taşır.
2. **Kümülatif ağırlık:** sıralı ağırlıkların kümülatif toplamı (cumsum) alınır; toplam 1.
3. **Ara değer:** `numpy.interp(q, kümülatif ağırlık, sıralı değer)`, yani kümülatif ağırlığa göre doğrusal ara değer. q ilk kümülatif ağırlıktan küçükse en küçük değer, son ağırlıktan büyükse en büyük değer alınır.
4. **PGA'ya dönüşüm:** hedef aşılma düzeyindeki PGA, eğri üzerinde log–log doğrusal ara değerle bulunur (kodun `loglog_interp` fonksiyonu).

Fark yalnız 3. adımın hangi uzayda yapıldığından gelir. P = 1 − e^(−λT) dönüşümü monoton olduğundan sıralama değişmez; ama doğrusal ara değer ve ortalama doğrusal olmayan dönüşüm nedeniyle farklı sonuç verir.

`istatistik_tanim.py` bunu sayısal olarak gösteriyor (`istatistik_tanim.json`). Aynı algoritma (OpenQuake `quantile_curve`) motorun 27 gerçekleşmesine:
- λ uzayında uygulanınca kodun değerlerini,
- PoE uzayında uygulanınca motorun istatistiklerini

her senaryo ve her yüzdelikte beş anlamlı basamakta birebir veriyor. Örnek, %10/50 yıl (g):

| | λ uzayı (= kod) | PoE uzayı (= OpenQuake motoru) |
|---|---|---|
| Ortalama | 0,92838 | 0,91473 |
| 16. | 0,68606 | 0,68602 |
| 50. | 0,75905 | 0,75905 |
| 95. | 1,23599 | 1,23557 |

%50/50 yılda ortalama 0,5426 / 0,5017 g; fark yüksek olasılıkta büyür.

### Tanım farkının ayrıntısı

Ortalama tehlike eğrisi iki farklı biçimde tanımlanabiliyor:
- **OpenQuake:** dalların 50 yıllık aşılma olasılıklarının ağırlıklı ortalaması.
- **Mevcut kod:** dalların yıllık aşılma oranlarının (λ) ağırlıklı ortalaması.

Poisson modelinde P = 1 − e^(−λt) doğrusal olmadığından iki ortalama yüksek olasılıklarda ayrışır:
- %10/50 yıl: 0,928 / 0,915 g (fark %1,5).
- %50/50 yıl: 0,543 / 0,502 g (fark %8).

Motorun gerçekleşmelerinden λ uzayında hesaplanan ortalama, kodla 6·10⁻⁴ göreli farkla aynı. Yani fark hesaptan değil tanımdan geliyor.

Raporlarda hangi tanımın kullanıldığı yazılmalı. Bu, Aşama B'de yöntem seçimi olarak değerlendirilecek.

95. yüzdelikteki %0,03'lük fark da algoritma farkı değil, ara değerin yapıldığı uzayın (λ / PoE) farkıdır; yukarıdaki tablo ve `istatistik_tanim.py` bunu gösteriyor.

## Kapsam ve sınırlar

Doğrulanan:
- oran ayrıklaştırması;
- aşılma integrali (kesilmemiş σ);
- kaynakların toplanması;
- mantık ağacı ağırlıkları ve yüzdelikleri.

Doğrulanmayan (Aşama B):
- GMPE'nin yayımlanmış kaynağa uygunluğu (B1);
- nokta kaynak geometrisi;
- oranlar, Mmax ve FTLS kaynağı;
- epistemik dal tasarımı.

## Yeniden çalıştırma

Ortam: Python 3.13; openquake.engine 3.26.2 (GDAL olmadan); NumPy 2.x.

1. `kod_gmpe.py` dosyasını `openquake/hazardlib/gsim/mindanao_kod_gmpe.py` olarak kopyala (GMPE kaydı).
2. `python girdi_uret.py`
3. `PATH=<oqenv>/bin:$PATH python calistir.py` → `asamaA_sonuc.json`, `*/lam_job.npy`, `lt/lam_job.npz`.
4. `python istatistik_tanim.py` → `istatistik_tanim.json`.
5. Bütünlük denetimi: `sha256sum -c MANIFEST_A.txt` (A_job klasöründe).
