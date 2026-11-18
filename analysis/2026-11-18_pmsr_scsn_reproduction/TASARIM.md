# EQ-LiveTürkiye · Öncü Deprem Örüntüsü Analizi
**Foreshock Pattern Analysis (FPA) — Teknik Tasarım ve Test Planı · Taslak v0.4**
Tarih: 2026-11-18 | Durum: Tasarım prensipte onaylandı; Faz 0 (depo dışı doğrulama) başladı — ilk sonuçlar §9'da. Depoya hiçbir şey gönderilmedi.

**v0.3 değişiklikleri:** T2 ikiye ayrıldı (T2a Poisson, T2b ETAS); T3'e ×1 negatif kontrol ve süre/başlangıç duyarlılığı; p-değeri kalibrasyonu T2'nin parçası; T10 (Mc duyarlılığı) ve T11 (katalog kararlılığı) eklendi; T8'e çoklu test ve alarm kümelenmesi kontrolü; GPL notu düzeltildi (§1.3); Mod C için ileriye sızıntı yasağı kabul ölçütü oldu (§6.1); Faz 0 sırası T1 → T4 → T2a → T2b → T3 → T10–T11.

**v0.2 değişiklikleri:** Type A / Type B filtreleri ayrıldı (§3); Mc yarıçapı ile analiz yarıçapı ayrı raporlanıyor (§3); örtüşen pencereler ve etkin bağımsız pencere sayısı notu (§3.1); T8 alarm eşleştirme kuralları önceden sabitlendi (§6.1); iki etiket (§4); açık kod kaynakları ve "yeniden yazmak yerine yararlan" kararı (§1.4); fazlar yeniden sıralandı: önce depo dışında Python doğrulaması (Faz 0).

---

## 0. Amaç ve geliştirme ilkeleri

**Amaç.** Seçilen bir depremden önceki sismik etkinliğin, o noktanın kendi geçmiş etkinliğine göre istatistiksel olarak anlamlı biçimde artıp artmadığını, literatürde doğrulanmış yöntemlerle ve tekrarlanabilir biçimde göstermek. İlk vaka: 17 Kasım 2021 Düzce Mw 5,0; ikinci vaka: 23 Kasım 2022 Gölyaka Mw 5,9.

**Bu modül ne değildir.** Deprem tahmini değildir; "öncü deprem bulundu" demez. Gulia ve Wiemer (2019) öncü trafik ışığı sistemi (FTLS) değildir.

**İlkeler**
1. `main` dalına, canlı veri akışına (`.github/workflows`, `data/`), `index.html`'deki çalışan analizlere dokunulmaz.
2. Çalışma `feature/foreshock-pattern-analysis` dalında yürür; birleştirme yalnızca bu belgedeki kabul ölçütleri sağlandıktan ve onayınızdan sonra.
3. Faz 1'de modül, mevcut `lab/reasenberg-pyodide/` gibi **ayrı bir laboratuvar sayfası** olarak yaşar (`lab/foreshock/`). Ana sayfaya bağlantı ancak Faz 3'te ve onayla eklenir.
4. AFAD verisi mevcut `apiv2/event/filter` çağrısıyla, salt okunur olarak alınır; mevcut çekme kodu değiştirilmez; modül kendi salt okunur sorgusunu ayrı bir dosyada yapar.
5. Her sonuç, girdi kataloğunun parmak izini (sorgu URL'si, çekim zamanı, olay sayısı, SHA-256) taşır.

---

## 1. Doğrulanmış yöntem tanımları

### 1.1 Khan vd. (2025) — ana yöntem
Azad Khan, R., Werner, M. J., Biggs, J., & Fagereng, Å. (2025). Effect of mainshock selection, earthquake catalog and definition on foreshock rate estimates in Southern California. *JGR: Solid Earth, 130*(7), e2024JB030733. doi:10.1029/2024JB030733

Parametreler makaleden okundu; **Empirical (ESR) algoritması ve ana şok seçimi, yazarların yayımladığı `statseis` 0.0.6 Python paketinin kaynak kodundan satır satır doğrulandı** (`foreshocks.py: ESR_model, select_mainshocks`).

| Öğe | Tanım |
|---|---|
| Ana şok adayı | M ≥ 4 (katalog başlangıcından ≥ 1 yıl sonra) |
| Seçim — Fixed | Son 1 yılda 10 km içinde daha büyük olay varsa aday dışlanır |
| Seçim — Mag-Dep | R(M) = 20 + 5·L(M) km, L = 10^((M−4,38)/1,49); T(M) = 50 + 25·(M−4) gün; bu pencerede daha büyük olayın artçısı sayılan aday dışlanır |
| Seçim — Combined (tercih) | Fixed **veya** Mag-Dep dışlıyorsa dışla |
| Yerel katalog | Ana şoktan önce, 10 km yarıçap |
| Öncü penceresi | Son **20 gün** → gözlenen sayı N_obs |
| Kalibrasyon dönemi | Ana şoktan önceki **365 → 20 gün** |
| Type A | 20 gün / 10 km içinde ≥ 1 adet M ≥ 3 olay |
| **Type B – Empirical (ana)** | 20 günlük pencere kalibrasyon dönemi boyunca **0,01 gün** adımla kaydırılır (~32 500 pencere). p = (sayısı ≥ N_obs olan pencere oranı). **p < 0,01 → anlamlı** |
| Type B – Gamma | Olaylar arası sürelere gamma dağılımı (MLE) uydurulur; simülasyonla 20 günlük sayım dağılımı üretilir |
| Type B – Poisson | Sabit oranlı karşılaştırma; makaleye göre oranı en çok şişiren seçim |
| Seyrek veri | N_obs = 0 → öncü yok. Kalibrasyonda olay yok ama N_obs > 0 → anlamlı |
| Mc | Yerel, b-değeri kararlılığı yöntemi (Cao ve Gao, 2002); 10 km'den başlayıp 5 km adımla en çok 50 km'ye, ≥ 275 olay olana dek genişler; sağlanamazsa ana şok analizden çıkar |
| Sonuç (G. Kaliforniya) | 74 ana şoktan 20'si (%27; özette "~%25") |

**Koddan çıkan iki ayrıntı.** (i) Yazarların kodunda yerel Mc kesmesi önce uygulanır, Type A eşiği (M ≥ 3) bu kesilmiş kataloğa uygulanır; G. Kaliforniya'da Mc ≈ 1–2 olduğu için sorun çıkmaz. AFAD'da yerel Mc 3'ü aşabileceğinden biz Type A'yı kesilmemiş katalogda sayıyoruz (§3) — bu, yazarların kodundan bilinçli bir sapma olarak raporlanır. (ii) `identify_foreshocks_short` içinde modelleme süresi 345 gün, `ESR_model` içinde 365 gündür; ikisi aynı kalibrasyon aralığını (365 → 20 gün) farklı yazımla ifade eder; T4'te ikisiyle de karşılaştırılır.

Not: Bu oran Güney Kaliforniya'ya ve QTM kataloğuna özgüdür; Türkiye için beklenti değildir. Wetzler vd. (2022, SRL 94, 428–442) Türkiye ve Yunanistan'da gözlenebilir öncülerin İtalya ve G. Kaliforniya'dan daha az olduğunu bildirir.

### 1.2 Karşılaştırma yöntemleri
- **Cui vd. (2025), GRL 52, e2025GL115394:** Sabit pencere (20 gün / 10 km) ve ampirik istatistik (ES) yöntemleri; ES, van den Ende ve Ampuero (2020, GRL 47, e2019GL086224) tanımıdır. Cui vd.'ne göre sabit pencere düşük Mc'de arka plan olaylarını öncü sayar; NNC ve ES Mc'ye karşı kararlıdır.
- **Helmstetter ve Sornette (2003):** Etiketin pencereye bağlılığı — sonuçların yorum çerçevesi.

### 1.3 Lisans notu
`statseis` **GPLv3** lisanslıdır. EQ-LiveTürkiye deposunda lisans dosyası bulunmuyor. Bu nedenle:
- JavaScript uygulaması kodun çevirisi değil, **makaledeki yöntem tanımından bağımsız olarak yazılır**.
- `statseis` yalnızca doğrulama (test kâhini) olarak, depo dışında Python ortamında kullanılır.
- Yalnızca dili değiştirmek GPL yükümlülüklerini kendiliğinden kaldırmaz. Doğrulama sırasında `statseis` kaynak kodu okunduğu için tam bir "temiz oda" ayrımı iddia edilmez; bunun yerine JS kodunun yöntem kaynağı (makale bölümleri) ve geliştirme geçmişi belgelenir, kaynak koddan satır aktarımı yapılmaz. Kesin hukuki değerlendirme gerekirse ayrıca alınır; bu belge hukuki görüş değildir.
- Depoya bir lisans eklenip eklenmeyeceği sizin kararınız (bkz. §8).

### 1.4 Açık kod kaynakları — yeniden yazmak yerine yararlanmak

| Yöntem | Kaynak kod | Lisans | Kullanım kararı |
|---|---|---|---|
| Khan vd. (2025): ana şok seçimi, BP, G-IET, ESR, Mc | `statseis` — github.com/RussellAzadKhan/seispy (PyPI: `statseis`); makalede Zenodo: doi:10.5281/zenodo.14051949 (paket), doi:10.5281/zenodo.14055540 (analiz kodu) | GPLv3 | **Faz 0'da doğrudan kullanılır** (referans ve vaka analizleri). Depoya kopyalanmaz. |
| van den Ende ve Ampuero (2020): G-IET | Yazarların açık kodu; `statseis` içine entegre | — | `statseis` üzerinden |
| Herrmann ve Marzocchi (2021): Lilliefors Mc | `statseis` içinde (`mc_lilliefors.py`) | — | Mc için ikinci kestirici |
| Cui vd. (2025) | Makalede kod bağlantısı yok; yalnızca katalog kaynakları verilmiş | — | Yöntemleri `statseis` ile aynı ailededir |
| Zaccagnino vd. (2024) | Makalede kod bağlantısı bulunamadı | — | Yalnızca yorum çerçevesi |
| NNC (Zaliapin ve Ben-Zion), ETAS | Açık uygulamalar mevcut; Faz 2'de seçilip burada listelenecek | — | Modül B, çevrim dışı |

**Neden doğrudan tarayıcıda çalıştırılamıyor?** `statseis.foreshocks` modülü cartopy, pyproj, seaborn, statsmodels ve IPython'u içe aktarıyor; cartopy Pyodide'de yok. Bu yüzden: Python tarafında paket olduğu gibi kullanılır; tarayıcı için yalnızca ESR çekirdeği (~30 satırlık mantık) makaledeki tanımdan bağımsız JS olarak yazılır ve T4'te `statseis` çıktısıyla birebir karşılaştırılır.

**Paketin kendi testleri.** Depoda yalnızca bir aktif test var (`test_utils.py`); öncü ve Mc fonksiyonlarının testleri yorum satırı. Bulut ortamında kuruldu ve çalıştırıldı (1 test geçti). Dolayısıyla T1–T4 yalnızca bizim kodumuz için değil, paketin bu iş için güvenilirliği için de gereklidir.

---

## 2. Mimari

| Bileşen | Soru | Yöntem | Çalışma yeri | Faz |
|---|---|---|---|---|
| **Faz 0 – Doğrulama (depo dışı)** | Yöntem ve paket bu veride güvenilir mi? | `statseis` doğrudan; T1–T6 | Bulut Python ortamı | 0 |
| **Modül A – Kısa dönem (olay merkezli)** | Seçilen depremden önceki 20 gün, kendi geçmişine göre anlamlı mı? | Khan vd. Type B (Empirical ana, Gamma ve Poisson yan); Type A karşılaştırma | Tarayıcı, JS + Web Worker (`lab/foreshock/`) | 1 |
| **Modül B – Uzun dönem kümelenme** | 2021 Mw 5,0 ile 2022 Mw 5,9 aynı kümede mi? | En yakın komşu kümelemesi (Zaliapin ve Ben-Zion); ETAS (p_ETAS; Cui vd.); Coulomb ΔCFS (Hoskan, 2024 ile karşılaştırma) | NNC: Pyodide lab; ETAS ve Coulomb: çevrim dışı Python (`analysis/`) | 2 |
| **Mod C – Canlı alarm modu** | "Şu an" bir noktada etkinlik anlamlı biçimde artmış mı? | Modül A'nın referans zamanı = şimdi olan nedensel sürümü | Tarayıcı | 3 — yalnızca §6 T7 değerlendirmesi tamamlanırsa |

Bir yıllık aralık (2021→2022) 20 günlük pencere yöntemine sığdırılmaz; bu soru Modül B'nindir.

**Modül A için önemli gözlem (Gölyaka).** 2022 ana şokunun kalibrasyon dönemi 23 Kasım 2021'de başlar; 2021 Mw 5,0 depremi (371 gün önce) dışarıda kalır, ancak 23 Kasım 2021 sonrasındaki artçıları kalibrasyonun içindedir. Bu, arka plan oranını yükseltip 2022 için anlamlılık eşiğini zorlaştırır. Sonuç raporunda ayrıca belirtilir; duyarlılık için artçılar ayıklanmış (GK74/Reasenberg) kalibrasyonla da çalıştırılır.

---

## 3. Modül A algoritması (sözde kod)

```
girdi: katalog K (AFAD, tek büyüklük türü), ana şok m (t_m UTC, konum, M)
parametreler: R=10 km, W=20 gün, C=365 gün, adım=0,01 gün, alfa=0,01

1  Mc_yerel ← b-değeri kararlılığı(K, merkez m, R0=10 → 50 km, ≥275 olay)
   yetersizse → "Analiz edilemedi: yerel Mc için olay sayısı yetersiz" ve dur
2  m ana şok mu? ← Combined seçim (Fixed ∪ Mag-Dep). Değilse rapora yaz, dur
   (canlı modda bu adım atlanır, bkz. Mod C)
3  L_tum ← {e ∈ K : t_e < t_m, mesafe ≤ R, 0 < t_m−t_e < C}     (Mc kesmesi yok)
   L_B   ← {e ∈ L_tum : M_e ≥ Mc_yerel}                         (Type B için)
4  N_obs ← |{e ∈ L_B : t_m−t_e < W}|
5  Kalibrasyon sayıları: her başlangıç noktası s ∈ [t_m−C+W … t_m−W] (0,01 gün adım)
   için n_s = |{e ∈ L_B : s−W < t_e ≤ s}|   — kümülatif sayaçla O(n + pencere)
6  p_emp ← |{s : n_s ≥ N_obs}| / |s|
7  Seyrek veri kuralları (§1.1) uygulanır
8  p_gamma, p_poisson ← yan modeller
9  Type A ← ∃ e ∈ L_tum : t_m−t_e < W ve M_e ≥ 3   (Mc'den bağımsız)
   Mc_yerel > 3 ise uyarı: "Type A eşiği yerel tamlığın altında; sonuç eksik olabilir"
çıktı: N_obs, p_emp, p_gamma, p_poisson, 99. persentil, medyan, kalibrasyondaki
       en büyük 20 günlük sayı, Mc_yerel, Mc yöntemi, Mc için kullanılan yarıçap,
       analiz yarıçapı, Type A, etiket, girdi parmak izi
```

Duyarlılık: R = 20 ve 50 km için aynı çıktılar yan yana.

**Mc ve yarıçap raporlaması.** Rapor üç değeri ayrı gösterir: (a) Mc'nin hesaplandığı gerçek yarıçap (10–50 km), (b) analiz yarıçapı (10 / 20 / 50 km), (c) her analiz yarıçapında uygulanan Mc. Varsayılan: tek Mc_yerel (a'dan) üç analize de uygulanır; duyarlılık için her analiz yarıçapında Mc ayrıca kestirilir ve fark tabloda verilir.

### 3.1 Empirical p-değerinin yorumu
0,01 gün adımla elde edilen ~32 500 pencere bağımsız gözlem değildir; komşu pencereler neredeyse aynı olayları içerir. 345 günlük kalibrasyonda birbiriyle örtüşmeyen 20 günlük pencere sayısı yalnızca ⌊345/20⌋ = **17**'dir. Bu yüzden p < 0,01 pratikte "son 20 günün sayısı, kalibrasyon yılındaki en yoğun 20 günü (yaklaşık) aşıyor" anlamına gelir; rapor bu nedenle kalibrasyondaki en büyük pencere sayısını da verir. p değeri bir olasılık kestirimi değil, ampirik bir sıralama ölçüsüdür. Yanlış pozitif davranışı T2'de sentetik kataloglarla ayrıca sınanır.

**Zaman.** Tüm hesap UTC. Ekranda yerel saat (TSİ, UTC+3) ikinci etiket olarak gösterilir. Saatlik histogram, ana şok anını (17 Kasım 2021 12:40 UTC = 15:40 TSİ) dikey çizgiyle böler; artçılar hiçbir zaman öncü sayımına girmez (koşul: t_e < t_m).

---

## 4. Etiketler ve arayüz dili

| Etiket (TR / EN) | Koşul | Renk |
|---|---|---|
| İstatistiksel olarak anlamlı artış gösterilmedi / No statistically significant increase | p_emp ≥ 0,01 | gri |
| İstatistiksel olarak anlamlı artış / Statistically significant seismicity increase | p_emp < 0,01 (Khan vd. 99. persentil) | turuncu |

v0.2'de yalnızca bu iki etiket kullanılır (Khan vd.'ne sadakat). 0,01–0,05 aralığı arayüzde etiket olarak değil, raporda duyarlılık analizi olarak verilir.

Kırmızı kullanılmaz. "Öncü", "foreshock", "uyarı", "alarm" sözcükleri sonuç etiketlerinde geçmez.

Her sonuç kartında sabit not:
> Bu, seçilen noktadaki son 20 günlük etkinliğin, aynı noktanın önceki yılına göre olağan dışı olup olmadığını gösterir. Anlamlı artışların çoğu büyük bir depremle sonuçlanmaz; öncüler ancak ana şoktan sonra, geriye dönük olarak tanımlanabilir (Helmstetter ve Sornette, 2003; Zaccagnino vd., 2024). Deprem tahmini değildir.

---

## 5. Dosya yapısı (Faz 1)

```
lab/foreshock/
  index.html        bağımsız laboratuvar sayfası (ana sayfa değişmez)
  fpa_core.mjs      saf fonksiyonlar: mesafe, Mc, seçim, sayım, p-değerleri
  fpa_worker.mjs    ağır hesap Web Worker'da
  fpa_afad.mjs      AFAD sorgusu (salt okunur) + parmak izi
analysis/2026-11-xx_fpa_dogrulama/
  reference_statseis.py   statseis ile referans çıktılar (depo dışı ortamda çalışır)
  fixtures/*.csv          dondurulmuş test katalogları
  expected/*.json         beklenen çıktılar
  README.md               nasıl yeniden üretilir
METHODOLOGY_B14_FPA.md    bu belgenin onaylı son hali
```

---

## 6. Test planı

| No | Test | Veri | Kabul ölçütü |
|---|---|---|---|
| T1 | Birim testleri | Sentetik | Mesafe ±0,01 km; sayaç ve pencere sınırları el hesabıyla birebir; seyrek veri kurallarının dört dalı |
| T2a | Yanlış pozitif ve p kalibrasyonu (Poisson) | 1 000 sentetik homojen Poisson katalog × 4 oran | p < 0,01 / 0,05 / 0,10 oranları nominal değerle karşılaştırılır; sapma raporlanır |
| T2b | Kümelenmiş etkinlikte davranış (ETAS) | Sentetik ETAS katalogları (dallanma oranı 0,3 / 0,6 / 0,8) | (a) rastgele zamanlarda anlamlılık oranı; (b) yalnız kaskad içeren evrende ana şok öncesi anlamlılık oranı = **ETAS sıfır öncü oranı** |
| T3 | Güç testi | Enjekte küme ×1 (negatif kontrol), ×2, ×5, ×10; küme süresi ve başlangıcı değişken | ×1 ≈ T2a düzeyi; tespit oranı ×'le tekdüze artar |
| T4 | Referans uyumu | Aynı dondurulmuş katalog, `statseis.ESR_model` ile JS karşılaştırması | N_obs ve pencere sayıları birebir; p_emp farkı < 10⁻⁹ |
| T5 | **Düzce 2021 vakası** | AFAD, merkez 40,8448 K / 31,0316 D; 2020-11-01 → 2021-11-17 12:40 UTC; 10/20/50 km | Çıktılar raporlanır; saatlik histogram 14–17 Kasım'ı ve derste gözlenen "16 Kasım yok" durumunu açıklar |
| T6 | **Gölyaka 2022 vakası** | AFAD, 2021-11-01 → 2022-11-23 UTC | Çıktılar; kalibrasyondaki 2021 artçıları ile ve onlar ayıklanmış hâliyle iki sonuç |
| T7 | Türkiye geneli, olay merkezli | AFAD, M ≥ 4 ana şoklar (Combined seçim) | Öncü oranı ve %95 güven aralığı; Wetzler vd. (2022) ile karşılaştırma |
| T8 | **Alarm temelli değerlendirme (Mod C önkoşulu)** | Aynı katalog, referans zamanı her gün kaydırılarak (nedensel) | Tüm "anlamlı artış" pencereleri sayılır; sonrasında T gün / R km içinde M ≥ 4 olup olmadığına göre isabet, **yanlış alarm** ve kaçırılan olay oranları; Molchan diyagramı. Ana şokla sonuçlanmayan pencereler ayrıca değerlendirilir |
| T9 | Performans | 20 000 olay | Worker'da < 2 s; arayüz donmaz |
| T10 | Mc duyarlılığı | Gerçek vaka; Mc_yerel ± 0,2 ve ± 0,4 | Her Mc için N_obs, p_emp, etiket ve Type A tablosu |
| T11 | Katalog kararlılığı | Gerçek vaka; olayların %5–10'u rastgele çıkarılır, büyüklükler ± 0,1 bozulur (500 tekrar) | Etiketin değişme olasılığı raporlanır |

### 6.1 T8 alarm eşleştirme kuralları (sonuçlar görülmeden önce sabitlenir)

| Öğe | Ana tanım | Duyarlılık |
|---|---|---|
| Değerlendirme noktaları | 0,1° ızgara hücre merkezleri (Türkiye karası ve kıyı); her gün 00:00 UTC | 0,05° ızgara |
| Alarm açılışı | Bir noktada p_emp < 0,01 olan ilk gün | — |
| Ardışık günler | Aynı noktada kesintisiz anlamlı günler **tek alarm** sayılır; araya ≥ 1 anlamlı olmayan gün girerse yeni alarm | araya ≤ 3 gün boşluk birleştirilir |
| Geçerlilik süresi T | Son anlamlı günden sonra **20 gün** | 7 ve 30 gün |
| Mekânsal kapsam R | Değerlendirme noktasından **10 km** | 20 km |
| Hedef olay | AFAD **M ≥ 4**, Combined seçimle ana şok | M ≥ 5 |
| Birden çok hedef | Bir alarm içinde birden fazla hedef olursa alarm bir kez "isabet" sayılır; her hedef ayrı ayrı "yakalandı" sayılır | — |
| Komşu alarmlar | Aynı hedefi kapsayan birden çok alarm: hedef bir kez yakalanır; alarmların her biri isabet sayılır ve bu durum ayrıca raporlanır | — |

**Çoklu test ve alarm kümelenmesi.** Binlerce hücrede her gün test yapıldığından hücre başına %1'lik yanlış pozitif, ülke ölçeğinde çok sayıda alarm üretir. Bu yüzden: (1) gerçek katalogla aynı olay sayısında sentetik kataloglar (ETAS ve zaman-karıştırılmış) üretilir; (2) aynı günlük algoritma tüm ızgarada çalıştırılır; (3) toplam alarm sayısı ve toplam alarm süresi sentetik dağılımla karşılaştırılır; (4) komşu hücrelerdeki eşzamanlı alarmların tek mekânsal alarm olarak birleştirildiği sürüm ayrıca raporlanır.

**İleriye sızıntı yasağı (Mod C kabul ölçütü).** Değerlendirme günü t için yalnızca t'den önce kataloğa girmiş olaylar kullanılır. Combined ana şok seçiminin gelecekteki olaylara dayanan bileşenleri alarm algoritmasının girdisi olamaz; yalnızca hedef olayları geriye dönük sınıflandırmak için kullanılır. Revize katalogla yapılan her T8 çalıştırması "revize katalog" etiketi taşır.

**Ölçütler birbirinden ayrı raporlanır:**
1. **Öncü oranı (hedef temelli):** Hedeflerin kaçının öncesinde, kendi 20 gün / 10 km penceresinde anlamlı artış var (T7).
2. **Yanlış alarm oranı (alarm temelli):** Alarmların kaçı süresi içinde hedefle sonuçlanmadı.
3. **Kaçırılan olay oranı:** Hiçbir alarmın kapsamadığı hedeflerin oranı.
4. **Molchan diyagramı:** alarm altındaki uzay-zaman payı (τ) ile kaçırma oranı (ν); rastlantısal köşegene göre kazanç.
5. **Toplam alarm sayısı ve toplam alarm süresi** (Molchan diyagramı tek başına yeterli değildir).

**Kabul kapısı:** T1–T4 geçmeden T5–T6 sonuçları yayımlanmaz. T8 tamamlanıp yanlış alarm oranı arayüzde gösterilmeden Mod C ana sayfaya eklenmez.

---

## 7. Riskler ve sınırlamalar

1. **Revize katalog ≠ 2021'de bilinen katalog.** AFAD API bugünkü (yeniden konumlandırılmış, büyüklüğü güncellenmiş) kataloğu verir. Gerçek sözde-ileriye dönük test, 18 Kasım 2021'de erişilebilen kataloğu gerektirir. Bu sürüm yoksa test "revize katalogla sözde-ileriye dönük" diye açıkça etiketlenir.
2. **Büyüklük türü.** EQ-Live b-değeri için ML→Mw dönüşümü kullanıyor. Sayım temelli testte tek ve dönüştürülmemiş büyüklük türü (AFAD ML) kullanılmalı; Mc de aynı türde kestirilmeli.
3. **Mc'nin zamanla değişmesi.** Kalibrasyon yılı içinde ağ yoğunluğu değişirse arka plan sayımı yanlı olur; Mc kayan pencereyle de kontrol edilir.
4. **Tek vaka yanılgısı.** Düzce ve Gölyaka sonuçları tek tek kanıt değildir; yorum T7–T8 ile birlikte yapılır.
5. **Lisans.** §1.3.

---

## 8. Kararlar (2026-11-18)

| Konu | Karar |
|---|---|
| Ara etiket (0,01–0,05) | İlk sürümde yok; yalnızca duyarlılık analizi olarak raporlanır |
| Depo lisansı | Şimdilik eklenmez; tarayıcı kodu bağımsız yazılır, `statseis` depo dışında kalır |
| Faz 1 (depoya yazma) | Tasarım prensipte onaylı; kodlama ve depoya yazma, T1–T4 sonuçları görüldükten sonra ayrı onaya bağlı |
| 2021 kataloğu | Bulunursa arşivlenir; bulunamazsa bugünkü revize katalogla yapılan çalışma gerçek zamanlı bir öngörü testi olarak sunulmaz |

**Sıradaki adım:** Faz 0 sürüyor (bkz. §9). Depoya yazma gerekmez.

---

## 9. Faz 0 ara sonuçları (2026-11-18, sentetik veri)

Ortam: bulut Python 3.13; `statseis` 0.0.6 (PyPI sürümünün `ESR_model` kodu GitHub sürümüyle aynı). Bağımsız Python ESR uygulaması yalnızca §1.1'deki tanımdan yazıldı (`fpa_ref.py`).

**T1 — Birim testleri: 7/7 geçti.** Boş katalog, yalnız öncü (kalibrasyon boş → anlamlı), 20,000 ve 19,999 gün sınırları, tek kalibrasyon olayı, el hesabıyla doğrulanan pencere oranı (2000/32 501 = 0,061537) ve 385 gün dışı olay. Her vakada bağımsız uygulama ile `statseis` birebir aynı.

**T4 — Referans uyumu: 24/24 katalog birebir.** p farkı en çok 0,0; 99. persentil ve en büyük pencere sayısı tümünde eşit (oranlar 0,02–2 olay/gün, enjekte öncülü ve pencere sınırına yuvarlanmış kataloglar dahil). Hız: `statseis` ≈ 30 s/ana şok; bağımsız uygulama milisaniye düzeyinde. Sonraki testler doğrulanmış bağımsız uygulamayla yapıldı.
*Henüz yapılmadı:* T4'ün ana şok seçimi (Combined) ve Mc (b-değeri kararlılığı) bileşenleri.

**T2a — Poisson altında yanlış pozitif (1 000 katalog/oran):**

| Oran (olay/gün) | Ort. N_obs | p < 0,01 | p < 0,05 | p < 0,10 |
|---:|---:|---:|---:|---:|
| 0,05 | 1 | 0,017 | 0,032 | 0,059 |
| 0,2 | 4 | 0,021 | 0,054 | 0,092 |
| 1 | 20 | 0,020 | 0,059 | 0,108 |
| 5 | 100 | 0,030 | 0,073 | 0,114 |

**Bulgu:** 1 yıllık kalibrasyonla nominal %1 eşiğin gerçek yanlış pozitif oranı **%1,7–3,0** (2–3 kat). Neden: etkin bağımsız pencere sayısı ~17; kataloğun %1'inden fazlasında son 20 gün yılın tüm pencerelerini aşıyor (p = 0), bu yüzden eşiği düşürmek düzeltmez. Ek deneme: kalibrasyon 3 yıla (1 095 gün) çıkarılınca oran **%1,1 (0,2/gün) ve %0,4 (1/gün)** — nominale iner. → Öneri: Türkiye uygulamasında 365 günlük kalibrasyon Khan vd.'ne sadakat için ana sonuç olarak kalır, **3 yıllık kalibrasyon duyarlılık sonucu olarak** eklenir; raporlarda "p < 0,01" yanında T2a'dan gelen gerçek yanlış pozitif oranı verilir.

**T2b — ETAS (toplam oran ~0,2/gün; α = 1,7, β = 2,3, c = 0,01 gün, p = 1,1):**

| Dallanma oranı n | Rastgele zamanda p < 0,01 | "Ana şok" (Mc + 2) öncesinde p < 0,01 |
|---:|---:|---:|
| 0,3 | 0,025 (1 500) | 0,046 (476) |
| 0,6 | 0,025 (1 500) | 0,047 (381) |
| 0,8 | 0,035 (1 500) | 0,130 (238) |

**Bulgu:** Yalnızca ardışık tetikleme içeren bir evrende bile ana şokların %5–13'ü "anlamlı artış"la öncelenir. Bu, Türkiye'de gözlenecek öncü oranının karşılaştırılması gereken **sıfır düzeyidir**: gözlenen oran bunu aşmıyorsa, öncüler kaskad tetiklemeden fazlasını göstermez (Helmstetter ve Sornette, 2003; Cui vd., 2025).

**T3 — Güç (500 katalog/hücre):**

| Fazla etkinlik | 0,2/gün | 1/gün |
|---|---:|---:|
| ×1 (negatif kontrol) | 0,014–0,026 | 0,026–0,032 |
| ×2 | 0,34–0,36 | 0,92–0,93 |
| ×5 | 0,99 | 1,00 |
| ×10 | 1,00 | 1,00 |

Aynı fazla olay sayısı 20 günün tamamına, son 5 güne ya da 15–20. günlere yerleştirildiğinde sonuç değişmiyor (yöntem yalnızca 20 günlük toplamı sayar; zamanlama bilgisi kullanılmaz). Düşük oranlı bölgelerde iki katlık bir artış çoğunlukla **yakalanamaz**.

**Sırada:** T4'ün ana şok seçimi ve Mc bileşenleri → T10–T11 (gerçek vaka verisi gerektirir: AFAD) → T5–T6.

---

## 10. Doğrulama programı (v0.4 eki, 2026-11-18)

**Başarı ölçütleri:** yeniden üretilebilirlik (Khan vd. verisi) → dayanıklılık (katalog, Mc, parametre) → aktarılabilirlik (AFAD).

| Aşama | Veri / vaka | Karşılaştırma hedefi |
|---|---|---|
| 1 | SCSN (179 446 olay, Mc 1,7) | Aday 257 → Fixed 106, Mag-Dep 108, Combined 88; ara listeler (aday, Fixed, Mag-Dep, Combined), yerel Mc ve Mc için kullanılan olay sayısı, ana şok bazında sınıflandırma; Empirical %22 (16/74) |
| 2 | QTM 12 | Combined 107; Empirical %27 (20/74) |
| 3 | QTM 9.5 (isteğe bağlı) | Combined 108; Empirical %26 (19/74) |
| 4 | AFAD — önceden tanımlı kurallarla **tüm** uygun M ≥ 4 adaylar | Öncü oranı; T2b ETAS sıfır düzeyi (%5–13) ile karşılaştırma |
| 5 | 2021 Düzce Mw 5,0 | Vaka |
| 6 | 2022 Gölyaka (AFAD Mw 5,9; Martínez-Garzón vd. 2023: Mw 6,0) | Standart FPA + ayrı duyarlılık analizi (yarıçap, kalibrasyon süresi). 6–11 Kasım kümesi (≈7,5 km K, Mw ≤ 2,2) 20 günlük pencerenin içinde. FPA sayım artışını ölçer; makale yerelleşme/yakınsamayı. "Anlamlı artış" çıkması makaleyle çelişki sayılmaz |
| Belgesel | 1999 Düzce | Uygulanamazlık örneği: Mag-Dep seçimi İzmit'in artçısı olarak dışlar; kalibrasyon İzmit artçılarıyla durağan değil. Öncü yokluğu: Wu vd. (2014, BSSA) |

**74'ün kökeni.** 88 / 107 / 108 katalog bazındaki Combined sayılardır. 74, üç kataloğun birleştirilmiş (Merged) Combined kümesinden (83) Mc için yeterli olayı olmayan 9 deniz içi olay çıkarılarak elde edilir. Yeniden üretim bu iki adımı ayrı ayrı doğrular.

**Gerekli dosyalar:** (1) SCSN kataloğu (SCEDC, doi:10.7909/C3WD3XH1, 2008–2017); (2) Khan vd. analiz arşivi (Zenodo, doi:10.5281/zenodo.14055540) — makale yalnızca sayıları verir; ana şok listeleri ve ara sonuçlar bu arşivdedir. Her ikisi de çalışma ortamından erişilemiyor; elle indirilmeli.
