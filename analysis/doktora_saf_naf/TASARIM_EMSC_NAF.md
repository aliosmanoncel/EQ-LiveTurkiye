# Araştırma tasarımı 2 — EMSC–NAF

**Çalışma başlığı (taslak):** *Seismicity Characteristics and b-Value Variations Along the North Anatolian Fault (2008–2026): Catalog Effects and Comparison with the San Andreas Fault*
**Sürüm:** tasarım v0.1 · 2026-11-21 · Durum: **danışman onayı bekliyor** (kod yazılmadı)
**Karar kaydı:** `KARAR_2026-11-21.md` · **Eş belge:** `TASARIM_SCEDC_SAF.md` (yöntem protokolü ortak)

> SAF tasarımındaki iş paketleri (İP1–İP4) burada **aynı protokolle** uygulanır. Bu belge yalnızca NAF'a ve EMSC kataloğuna özgü farkları ayrıntılandırır. Her İP başlamadan önce kendi ön kaydını commit eder.

---

## 1. Amaç

Kuzey Anadolu Fayı (NAF) boyunca, 2008–2026 EMSC kataloğuyla:
1. EMSC'nin Türkiye kaydını nicel olarak tanımlamak (tamamlanma, büyüklük türleri, kaynak kurumlar),
2. b-değerinin segmentler ve faya uzaklık şeritleri boyunca değişimini ölçmek,
3. ayıklama yöntemlerinin (GK74, Reasenberg, Zaliapin) etkisini göstermek,
4. ana şok öncesi oran artışlarını (PMSR) mümkün olan segmentlerde betimlemek,
5. SAF ile **yöntemsel** karşılaştırma yapmak: farkın tektonikten mi, katalogdan mı geldiğini ayırmak.

## 2. Araştırma soruları

| RQ | Soru | İP |
|---|---|---|
| RQ-N1 | EMSC'nin NAF kaydında Mc zaman ve konuma göre nasıl değişiyor; kaynak kurum (Origin/Magnitude Agency) ve büyüklük türü karışımı nasıl? | İP-N1 |
| RQ-N2 | EMSC ile birincil ulusal katalog (AFAD) aynı bölge ve dönemde olay, büyüklük ve Mc bakımından ne kadar örtüşüyor? | İP-N1 |
| RQ-N3 | NAF segmentleri arasında b-değeri anlamlı biçimde farklı mı; doğal Mc ve ortak eşikte sonuç değişiyor mu? | İP-N2 |
| RQ-N4 | Ayıklama yöntemi seçimi NAF'ta SAF'takiyle aynı yönde mi etki ediyor? | İP-N3 |
| RQ-N5 | SAF ve NAF arasındaki farkların ne kadarı katalog özelliklerinden (Mc, tür karışımı, toplayıcı etkisi) kaynaklanıyor? | İP-N5 |

## 3. Veri

| Öğe | Değer |
|---|---|
| Birincil katalog | **EMSC** (Euro-Mediterranean Seismological Centre), FDSN olay servisi; EQ-Live'ın canlı kaynağıyla aynı servis |
| Dönem | 2008-01-01 – sabitleme tarihi (SAF ile aynı başlangıç) |
| Alan | NAF şeritlerini kapsayan dikdörtgen (yaklaşık 39,5–41,5° K, 26–41,5° D); kesin sınırlar fay modelinden |
| Alanlar | zaman, konum, derinlik, büyüklük, **büyüklük türü**, **Origin Agency (Author)**, **Magnitude Agency (MagAuthor)**, olay türü |
| Büyüklük | Tercih edilen büyüklük; **dönüşüm yok** (OUT 6). Tür ve kurum dağılımları her analizde raporlanır |
| Duyarlılık kataloğu | **AFAD** (ulusal ağ) — yalnız İP-N1'de karşılaştırma ve gerekirse İP-N4 için; birincil kaynak EMSC kalır |

### 3.1 Tekrarlanabilirlik için dondurulmuş anlık görüntü (karar gerekli)
EMSC sorgusu her zaman güncel sürümü döndürür; geçmiş kayıtlar ve kurum çözümleri değişebilir. İlke 4 gereği, SCEDC arşivindeki düzenin aynısı önerilir: `data/emsc_naf/` altında **ham sorgu yanıtları + işlenmiş CSV + manifest (sorgu URL'leri, tarih, SHA-256)**, değiştirilemez anlık görüntüler ve CI doğrulaması. Bu yeni bir veri eklemesidir; SCEDC gibi ayrı onayla ve ayrı dalda yapılır. Sorgular parçalı yapılır (aylık), satır sayıları ve kimlik tekilliği denetlenir.

### 3.2 EMSC'ye özgü bilinen sorunlar
- **Toplayıcı katalog:** EMSC, AFAD (EMSC'de `DDA`), KOERI ve diğer kurumların çözümlerini birleştirir. Bir olayın konumu bir kurumdan, büyüklüğü başka kurumdan gelebilir. SCEDC ↔ USGS ComCat karşılaştırmasında görülen toplayıcı etkisi (eksik olay, farklı çözüm sürümü; `data/scedc/KAYNAK_KARSILASTIRMA.md`) burada da beklenmeli.
- **Seyrek küçük olaylar:** EQ-Live'daki canlı testlerde EMSC Türkiye kaydı yaklaşık M ≥ 2 düzeyinde ve seyrek görüldü; PMSR'nin 50 km içinde 275 olay koşulu Türkiye olaylarında sık sık sağlanamadı ("Analiz için yeterli veri yok"). Mc **ölçülecek**, varsayılmayacak (ilke 1).
- **Büyüklük türü karışımı:** ML, MD, Mw, mb; kurumlar arası ML farkları.
- **Olası ağ/işleme kırılmaları:** ağ genişlemeleri ve büyük dizilerden sonraki işleme yükü (ör. 2023 Kahramanmaraş dizisi NAF dışında olsa da ulusal işleme kapasitesini etkilemiş olabilir). Kırılma tarihleri SCEDC kadar belgeli değil; İP-N1'de veriyle aranır ve **keşifsel** olarak etiketlenir.

## 4. Çalışma alanı: NAF ve segmentler

**Fay izi kaynağı (karar gerekli):** (a) MTA Türkiye Diri Fay Veritabanı (Emre vd., 2018) — öneri; (b) GEM Global Active Faults (Styron & Pagani, 2020; EQ-Live'da katman olarak var). Kaynak dosyası sürümüyle arşive alınır.

**Ön segment listesi** (batıdan doğuya; 20. yüzyıl kırıklarına dayalı; sınırlar fay modelinden):

| Segment | Not |
|---|---|
| Ganos (1912) | Kara ve Saros uzantısı |
| Marmara Denizi (Orta Marmara, Adalar) | Deniz içi; konum belirsizliği yüksek; sismik boşluk tartışması |
| İzmit (1999) | |
| Düzce (1999) | 2022 Gölyaka-Düzce Mw 6,1 bu kesimde |
| Mudurnu–Abant (1957, 1967) | |
| Bolu–Gerede (1944) | |
| Tosya–Kurşunlu (1943, 1951) | |
| Niksar–Erbaa (1942) | |
| Erzincan (1939) | Karlıova'ya kadar |

Uzaklık şeritleri, mesafe tanımı ve yeterlilik kuralı (Mc üstünde N ≥ 100) SAF tasarımıyla **aynı**. Güney kol ve Marmara'daki çoklu kollar için atama kuralı ön kayıtta belirlenir.

**Büyük diziler (2008–2026, işaretlenir):** 2022 Gölyaka-Düzce Mw 6,1; Marmara'da Silivri açıkları 2019 M 5,7 ve 2025-04-23 Mw 6,2 (Kumburgaz segmenti; AFAD ve Temblor, doi:10.32858/temblor.368). Ders 6 kapsamındaki 2021 → 2022 Düzce dizisi, İP-N4 için doğal bir vaka çalışmasıdır.

## 5. İş paketleri (SAF protokolüyle aynı; farklar)

### İP-N1 — Katalog karakterizasyonu ve EMSC ↔ AFAD karşılaştırması (RQ-N1, RQ-N2) · makale NAF-P1
- Mc(t), Mc(x), büyüklük türü ve **kurum** dağılımı (SAF İP1 yöntemleriyle aynı; birincil Mc yöntemi SAF ile aynı seçilir).
- **EMSC ↔ AFAD:** örnek aylar ve segmentlerde olay eşleştirme (zaman ± birkaç s, konum ± birkaç km; tolerans ön kayıtta). Ölçütler: eşleşen, yalnız birinde olan, büyüklük farkı dağılımı (türe göre), Mc farkı. Bu, SCEDC ↔ ComCat testinin NAF karşılığıdır.
- **Çıktı:** dönem ve segment başına önerilen Mc; EMSC'nin hangi büyüklük aralığında AFAD'la tutarlı olduğu.

### İP-N2 — b-değeri (RQ-N3) · makale NAF-P2
SAF İP2 ile aynı: Aki–Utsu MLE, Shi–Bolt ve bootstrap, Utsu testi ve FDR, b-positive kontrolü, Marzocchi vd. (2020) uyarıları. Ek: Marmara deniz içi kesiminde konum belirsizliği yüzünden şerit ataması belirsizdir; ±5 km duyarlılık.

### İP-N3 — Ayıklama (RQ-N4)
SAF İP3 ile aynı üç yöntem ve aynı parametre protokolü. GK74 ve Reasenberg EQ-Live'daki doğrulanmış uygulamalarla, **değiştirilmeden**.

### İP-N4 — PMSR
- Kod değiştirilmeden (OUT 4). **Beklenen sorun:** EMSC ile çoğu ana şokta Mc için 275 olay koşulu sağlanmayabilir. Sonuç "sınanamadı" olarak raporlanır, "artış yok" olarak değil.
- **Karar gerekli:** İP-N1, AFAD'ın NAF'ta yeterli yoğunluk sağladığını gösterirse İP-N4'ün AFAD ile de çalıştırılması (duyarlılık olarak, ayrı etiketle).
- 2021 → 2022 Düzce vakası açıklayıcı örnek olarak; "öncü" dili kullanılmaz (OUT 7).

### İP-N5 — SAF–NAF karşılaştırması (RQ-N5) · makale P5 (ortak)
1. **Doğal Mc** ile karşılaştırma (her katalog kendi Mc'siyle).
2. **Ortak eşik:** M_ortak = max(Mc_SAF, Mc_NAF) (+0,2, +0,5 duyarlılık).
3. **Veri–yöntem ayrımı (ilke 3):**
   - SAF tarafında SCEDC ile EMSC'nin Kaliforniya kaydı karşılaştırılır. "EMSC kullanmak SAF sonuçlarını nasıl değiştirirdi?" sorusu, NAF'taki EMSC etkisinin ölçeğini verir.
   - NAF tarafında EMSC ile AFAD karşılaştırılır (İP-N1).
   - Böylece 2 fay × 2 katalog türü (bölgesel birincil ↔ toplayıcı) düzeni kurulur. Tektonik farkın yorumu yalnızca **katalog türünden bağımsız kalan** farklara dayandırılır.
4. **Yasak çıkarım (OUT 5):** b_SAF ve b_NAF değerleri doğrudan eşdeğer kabul edilmez; karşılaştırma yalnızca aynı protokol, aynı eşik ve belgelenmiş katalog farklarıyla yapılır.

## 6. Tekrarlanabilirlik
SAF tasarımı §6 ile aynı. Ek olarak her EMSC sorgusunun tam URL'si, sorgu zamanı, yanıt SHA-256'sı ve satır sayısı kaydedilir. Dondurulmamış (canlı) EMSC sonucu yayın analizlerinde kullanılmaz.

## 7. Riskler ve sınırlılıklar
- **EMSC'nin düşük yoğunluğu:** b ve PMSR için N yetersiz kalabilir. Önlem: segmentleri birleştirme kuralı ön kayıtta; AFAD duyarlılığı.
- **Kurum karışımı:** konum ve büyüklük farklı kurumlardan gelebilir; kurum bazında alt kümeler raporlanır.
- **Deniz içi Marmara:** konum belirsizliği; ağ geometrisi.
- **Belgelenmemiş işleme değişiklikleri:** SCEDC'deki gibi resmi değişiklik geçmişi yok; kırılmalar keşifsel olarak bulunur.
- **Fay modeli seçimi:** ikinci modelle duyarlılık.

## 8. Aşamalar
1. Danışman onayı ve §9 kararları → 2. EMSC anlık görüntü arşivinin ayrı onayı ve oluşturulması → 3. İP-N1 ön kaydı → 4. İP-N1 → 5. İP-N2, İP-N3 → 6. İP-N4 → 7. İP-N5 (SAF ile birlikte).

## 9. Danışman kararı gereken konular
1. Fay izi kaynağı: MTA Diri Fay Veritabanı (öneri) / GEM GAF.
2. EMSC dondurulmuş anlık görüntü arşivi (`data/emsc_naf/`) oluşturulsun mu?
3. AFAD duyarlılık kataloğu: kapsam (yalnız İP-N1 mi, İP-N4 de mi) ve veri alma yolu (kullanıcı indirmesi; tarayıcıdan erişim sorunu analiz için engel değil).
4. Güney kol ve Marmara'daki kolların segment ataması.
5. SAF tarafında EMSC'nin Kaliforniya kaydıyla karşılaştırma (İP-N5 madde 3) ana tasarıma girsin mi? (Öneri: evet; ilke 3'ün en doğrudan sınaması.)

## Kaynaklar
- Barka, A. (1996). Slip distribution along the North Anatolian Fault associated with the large earthquakes of the period 1939 to 1967. BSSA 86(5), 1238–1254.
- Emre, Ö., Duman, T. Y., Özalp, S., Şaroğlu, F., Olgun, Ş., Elmacı, H., Çan, T. (2018). Active fault database of Turkey. Bull. Earthquake Eng. 16, 3229–3275.
- Öncel, A. O., Wyss, M. (2000). The major asperities of the 1999 Mw = 7.4 Izmit earthquake defined by the microseismicity of the two decades before it. GJI 143(3), 501–506.
- Stein, R. S., Barka, A. A., Dieterich, J. H. (1997). Progressive failure on the North Anatolian fault since 1939 by earthquake stress triggering. GJI 128(3), 594–604.
- Styron, R., Pagani, M. (2020). The GEM Global Active Faults Database. Earthquake Spectra 36(1_suppl), 160–180.
- Şengör, A. M. C. vd. (2005). The North Anatolian Fault: A new look. Annu. Rev. Earth Planet. Sci. 33, 37–112.
- Yöntem kaynakları (Aki, Utsu, Shi & Bolt, Wiemer & Wyss, Woessner & Wiemer, Cao & Gao, van der Elst, Marzocchi vd., Gardner & Knopoff, Reasenberg, Zaliapin & Ben-Zion, Mizrahi vd., Khan vd.): `TASARIM_SCEDC_SAF.md`.

*Kaynak künyeleri kod aşamasından önce DOI ile tek tek doğrulanacaktır.*
