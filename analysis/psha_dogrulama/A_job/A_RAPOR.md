# Aşama A: hesap doğrulaması, tam OpenQuake motor akışı (`job.ini`)

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

### Tanım farkı (hata değil)

Ortalama tehlike eğrisi iki farklı biçimde tanımlanabiliyor:
- **OpenQuake:** dalların 50 yıllık aşılma olasılıklarının ağırlıklı ortalaması.
- **Mevcut kod:** dalların yıllık aşılma oranlarının (λ) ağırlıklı ortalaması.

Poisson modelinde P = 1 − e^(−λt) doğrusal olmadığından iki ortalama yüksek olasılıklarda ayrışır:
- %10/50 yıl: 0,928 / 0,915 g (fark %1,5).
- %50/50 yıl: 0,543 / 0,502 g (fark %8).

Motorun gerçekleşmelerinden λ uzayında hesaplanan ortalama, kodla 6·10⁻⁴ göreli farkla aynı. Yani fark hesaptan değil tanımdan geliyor.

Raporlarda hangi tanımın kullanıldığı yazılmalı. Bu, Aşama B'de yöntem seçimi olarak değerlendirilecek.

95. yüzdelikteki %0,03'lük fark da iki yazılımın ağırlıklı yüzdelik ara değer yönteminin farklı olmasından kaynaklanıyor.

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
