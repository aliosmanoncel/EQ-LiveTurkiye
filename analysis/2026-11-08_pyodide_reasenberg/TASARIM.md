# Dinamik Reasenberg — Pyodide tasarım notu ve deneme sonuçları

**Tarih:** 2026-11-08 (2. tur: D-P1–D-P5 kararları işlendi) · **Dal:** `deneme/pyodide-reasenberg` · **Durum:** deneme; `main` ve site (`index.html`) değişmedi; statik GK74/Reasenberg katmanı aynen korunur.

> **Ayrım:** Pyodide ↔ CPython birebir eşleşmesi *yazılım uygulamasının* doğruluğunu destekler; Reasenberg algoritmasının *bilimsel geçerliliğini* tek başına kanıtlamaz. Arayüzdeki "UYGUN" durumu da yalnız denetlenen koşulların sağlandığını söyler.

## 1. Karar ve ilke

Reasenberg yalnız statik veriye bağlı değildir. Koşullar sağlanıyorsa dinamik (bölge/dönem seçimine göre alınan) katalogda da çalıştırılabilir. Koşullar sağlanmıyorsa hesap **yapılmaz** (OFF) ve hangi koşulun sağlanmadığı gösterilir. Koşullar sonradan sağlanırsa (ör. sorgu sınırı artırılırsa) hesap yeniden etkinleşir.

Çalıştırma ortamı **A seçeneği: Pyodide** (tarayıcıda CPython). Algoritma JavaScript'e çevrilmez:

- **Referans kodun bütünlüğü.** `scripts/reasenberg.py` v0.3.0, `decluster_gk74.py` ve `decluster_reasenberg.py` bayt bayt aynı biçimde Pyodide dosya sistemine yazılır. `reasenberg.py` sha256'sı iki kez denetlenir: JavaScript'te yüklemeden önce, adaptörde içeriden. Tutmazsa hesap başlamaz. Sunucudaki fonksiyonun aynısı (`decluster_reasenberg.decluster`) çağrılır.
- **Veri bütünlüğü.** Sorgu sınırına takılan katalogda hesap yapılmaz (K1).
- **Bağımsız doğrulama.** Tarayıcıdaki sonuç dondurulmuş referanslarla ve yerel CPython ile birebir karşılaştırılır (§4).
- **Mc ayrımı.** "Mc (tahmin)" ile "xmeff (seçim)" ayrı gösterilir. Seçimin tahminin üstünde olması yalnız bir tutarlılık denetimidir, doğrulama değildir.

## 2. Gelen yorumlar — kapsam içi (IN) / kapsam dışı (OUT)

| Öneri | Karar | Not |
|---|---|---|
| Pyodide öncelikli; `reasenberg.py` değişmeden, Pyodide yalnız çalıştırma ortamı | IN | `rb_core.mjs`: sha256 + aynı adaptör |
| Sorgu sınırı aşılınca hesap yok | IN (K1) | 500 algoritmanın değil veri erişiminin sınırıdır; sitede `regionLimit` 20 000'e kadar seçilebiliyor, `regionCapped` zaten tutuluyor |
| Tarayıcı sonucu ↔ referans çıktılar | IN (§4) | Dondurulmuş 4 referans + tam EMSC kataloğunda CPython ile birebir |
| Tahmin edilen Mc ile seçilen Mc ayrı | IN (K5) | Arayüzde iki ayrı değer; uyarı metni |
| Koşul tablosu: olay sayısı, katalog bütünlüğü, Mc, zaman sıralaması, sınır | IN (K1–K7) | Sınır: yalnız uyarı (açık karar D-P2) |
| "Koşul sağlanırsa yeniden ON" | IN | Kapılar her çalıştırmada yeniden değerlendirilir; durum saklanmaz |
| — (eklenen) Tek kaynak | IN (K2) | İki kaynaktan gelen aynı deprem sahte küme üretir → OFF |
| — (eklenen) Büyüklük ölçeği karışımı | IN (K8, uyarı) | r(M), τ büyüklüğe bağlı |
| JavaScript'e çeviri (B seçeneği) | OUT (şimdilik) | İkinci uygulama doğrulama yükü getirir; Pyodide yeterli hızda (§6) |

**2. tur (D-P1–D-P5 önerileri):**

| Öneri | Karar | Not |
|---|---|---|
| Eşleşme ≠ bilimsel geçerlilik ayrımı | IN | Not başına, öz-sınama ve "UYGUN" metinlerine yazıldı |
| D-P1 "sitenin kümülatif GFT tahmincisi" | IN, **düzeltilerek** | Sitede GFT yok; sitenin tahmincisi `computeMcSrc()` = MAXC+0,2. Kapı bu fonksiyonun **birebir kopyasını** kullanır; CI kopyanın `index.html` ile aynı kaldığını denetler. GFT'ye geçiş sitenin tümünü etkileyen ayrı bir bilimsel karardır |
| D-P2 önce uyarı; OFF için gerekçe ve eşik testi | IN | Sınır etkisi ölçüldü (§8): üyelik değişimi %0–1,5 → OFF için gerekçe yok; uyarı ölçülen değerleri gösterir |
| D-P3 sürümü sabit, depoda | IN | `vendor/pyodide/0.27.7/` (17 MB); CI resmi arşivle bayt bayt karşılaştırır; deneme sayfası dış kaynağa hiç istek atmaz |
| D-P4 50 olay / %5 başlangıç değeri | IN | `DEFAULTS` içinde "başlangıç değeri" olarak işaretli; duyarlılık testi sonraki tur |
| D-P5 her oturumda öz-sınama | IN | Yüklemeden sonra kendiliğinden çalışır; geçmezse K0 → KAPALI |
| Üç durum: VERIFIED / WARNING / OFF | IN, **adı değiştirilerek** | "VERIFIED (doğrulandı)" bilimsel doğrulama izlenimi verir; yukarıdaki ayrımla çelişir. Kullanılan adlar: **UYGUN** (ELIGIBLE) / **UYARILI** (WARNING) / **KAPALI** (OFF) |

## 3. Bileşenler (bu dal)

| Dosya | İş |
|---|---|
| `lab/reasenberg-pyodide/rb_core.mjs` | Pyodide'e üç Python dosyasını yazar, sha256 denetler, `decluster` çağırır. Algoritma kodu içermez. Tarayıcı ve Node ortak. |
| `lab/reasenberg-pyodide/gates.mjs` | Uygunluk kapıları K1–K8, MAXC+0.2 Mc tahmini (yalnız deneme için). |
| `lab/reasenberg-pyodide/index.html` | Deneme sayfası: ortam, öz-sınama, daire içi dinamik deneme. Sitenin parçası değil. |
| `scripts/reasenberg_tests/pyodide_parity.mjs` | Eşleşme testi (P1, P2) + süre ölçümü. |
| `scripts/reasenberg_tests/gates.test.mjs` | Kapıların birim testleri (9 test). |
| `.github/workflows/reasenberg-pyodide.yml` | CI: depodaki Pyodide = resmi sürüm (bayt bayt) + kapı testleri (Mc kopyası denetimi dahil) + eşleşme (depodaki Pyodide ile). |
| `vendor/pyodide/0.27.7/` | Pyodide çekirdeği + numpy 2.0.2, değiştirilmeden; `SHA256SUMS`, `LICENSE` (MPL-2.0), `README.md`. |
| `analysis/2026-11-08_pyodide_reasenberg/sinir_etkisi.py` | D-P2 ölçümü: daire sınırının üyeliğe etkisi (`sinir_etkisi.json`). |

## 4. Uygunluk kapıları

| Kod | Kapı | Sağlanmazsa |
|---|---|---|
| K0 | Bu oturumda öz-sınama (4 dondurulmuş referansla birebir) geçti | **OFF** |
| K1 | Katalog bütünlüğü: sorgu üst sınıra takılmadı | **OFF** |
| K2 | Tek kaynak (yineleme ayıklaması yok) | **OFF** |
| K3 | Geçersiz alan oranı ≤ %5 | **OFF** |
| K4 | Tekil kimlik (sıralama adaptörde UTC) | **OFF** |
| K5 | Mc (sitenin MAXC+0,2'si, `mag` alanında) tahmin edilebildi ve xmeff (seçim) ≥ Mc (tahmin) | **OFF** |
| K6 | N(M ≥ xmeff) ≥ 50 | **OFF** |
| K7 | Sınır etkisi: kenara 10·r(Mmax) km'den yakın olay oranı + ölçülen üyelik değişimi (§8) | uyarı |
| K8 | Büyüklük ölçeği karışımı | uyarı |

Durum: herhangi bir zorunlu koşul sağlanmazsa **KAPALI** (hesap yok, nedenler listelenir) · yalnız uyarılar → **UYARILI** (hesap + uyarı) · hiçbiri → **UYGUN**. Durum saklanmaz; her çalıştırmada yeniden değerlendirilir.

## 5. Doğrulama sonuçları (birebir, tolerans yok)

Pyodide 0.27.7 · Python 3.12.7 · numpy 2.0.2 (yerel CPython 3.11 · numpy 2.5.3). Ayrıntı: `parity_node.json`.

| Ölçüt | Sonuç |
|---|---|
| P1 adiyaman (4231 olay) | üyelik ve bağımsız kümesi referansla **aynı** |
| P1 izmit_dogu (2267) | **aynı** |
| P1 saimbeyli (4510) | **aynı** |
| P1 van_bati (4468) | **aynı** |
| P2 tam EMSC (80 929), Pyodide ↔ CPython | üyelik **birebir aynı** |
| P2 toplamlar ↔ `data/reasenberg_gk74_emsc.json` | tekil 63 862 · temsilci 2 080 · bağımlı 14 987 · küme 2 080 — **aynı** |
| Tarayıcı (Chromium) öz-sınaması, 4 referans | **birebir aynı** (depodaki Pyodide ile; dış istek 0) |

## 6. Performans

| | Node (Pyodide) | Chromium (Pyodide) | CPython |
|---|---|---|---|
| Başlatma (çekirdek + numpy + modül) | 3,1 s | 3,0 s (yerel sunucu; ağdan 17 MB ilk indirme ayrıca) + öz-sınama ~1 s | — |
| N = 500 | 0,07 s | — | 0,04 s |
| N ≈ 1 500 (İzmit, R = 100 km) | — | 0,07–0,11 s | — |
| N = 2 000 | 0,12 s | — | 0,06 s |
| N = 5 000 | 0,31 s | — | 0,15 s |
| N = 20 000 | 1,35 s | — | 0,62 s |
| N = 80 929 (tümü) | 6,0 s | 5,8 s | 2,0 s |

Bölge sorgusu boyutlarında (≤ 20 000) hesap ≤ 1,4 s; asıl maliyet ilk yüklemedir (bir kez, yalnız düğmeye basılınca).

## 7. Tarayıcı senaryoları (deneme sayfası)

| Senaryo | Durum | Neden |
|---|---|---|
| İzmit, R = 100 km, 1998–2026, EMSC, sınır 500 | **KAPALI** | K1: 500'e takıldı |
| Aynı, sınır 5000 / sınırsız (N = 1538) | UYARILI | K7 sınır, K8 ölçek; tekil 1258 · temsilci 61 · bağımlı 219 |
| Aynı, 1990–2026, EMSC + ISC | **KAPALI** | K2: iki kaynak |
| Aynı, xmeff = 2,0 (seçim) | **KAPALI** | K5: Mc (tahmin) 3,2'nin altında |
| Tüm EMSC, xmeff = 3,0 | **KAPALI** | K5: Mc (sitenin MAXC+0,2'si) = 3,2 |
| Tüm EMSC, xmeff = 3,2 | UYARILI | K8; küme 2076, 5,8 s |

## 8. D-P2 ölçümü: sınır üyeliği ne kadar değiştiriyor?

**Yöntem** (`sinir_etkisi.py`, dondurulmuş modül, xmeff = 3,0, zmap): Referans olarak tüm EMSC kataloğunda (sınırsız) tek bir hesap yapıldı. Dinamik hesap yalnız daire içindeki olaylarla yapıldı. Daire içindeki her olayın "bağımsız / bağımlı" sınıfı iki hesap arasında karşılaştırıldı. 6 merkez × 3 yarıçap = 18 daire. Yalnız uzaysal sınır ölçüldü; zaman penceresinin etkisi ayrıca ölçülmeli.

| Merkez | R (km) | N | Mmax | L = 10·r(Mmax) (km) | K7 "kenara yakın" | Sınıfı değişen | Oran | Bağımlı (ref → dinamik) |
|---|---|---|---|---|---|---|---|---|
| izmit | 50 | 338 | 6.3 | 36.4 | %66.9 | 1 | %0.30 | 64 → 63 |
| izmit | 100 | 1538 | 6.3 | 36.4 | %57.8 | 13 | %0.85 | 230 → 217 |
| izmit | 200 | 4697 | 6.3 | 36.4 | %37.4 | 13 | %0.28 | 1229 → 1216 |
| van | 50 | 2826 | 7.3 | 50 | %100.0 | 3 | %0.11 | 1352 → 1349 |
| van | 100 | 3710 | 7.3 | 91.5 | %98.9 | 5 | %0.13 | 1431 → 1430 |
| van | 200 | 5839 | 7.3 | 91.5 | %32.3 | 0 | %0.00 | 1587 → 1587 |
| kahramanmaras | 50 | 984 | 7.8 | 50 | %100.0 | 15 | %1.52 | 283 → 268 |
| kahramanmaras | 100 | 3748 | 7.8 | 100 | %100.0 | 2 | %0.05 | 1158 → 1156 |
| kahramanmaras | 200 | 7725 | 7.8 | 145.0 | %84.7 | 27 | %0.35 | 1737 → 1710 |
| denizli | 50 | 1138 | 5.8 | 23.0 | %31.6 | 1 | %0.09 | 173 → 172 |
| denizli | 100 | 2084 | 5.8 | 23.0 | %33.1 | 4 | %0.19 | 307 → 303 |
| denizli | 200 | 13433 | 7.0 | 69.4 | %72.5 | 20 | %0.15 | 3533 → 3513 |
| elazig | 50 | 1243 | 6.8 | 50 | %100.0 | 4 | %0.32 | 256 → 252 |
| elazig | 100 | 2849 | 6.8 | 57.7 | %62.1 | 6 | %0.21 | 611 → 607 |
| elazig | 200 | 7865 | 7.5 | 110.0 | %68.5 | 95 | %1.21 | 1757 → 1724 |
| ege_samos | 50 | 2326 | 7.0 | 50 | %100.0 | 2 | %0.09 | 861 → 859 |
| ege_samos | 100 | 3735 | 7.0 | 69.4 | %74.5 | 1 | %0.03 | 950 → 949 |
| ege_samos | 200 | 15897 | 7.0 | 69.4 | %59.8 | 30 | %0.19 | 4955 → 4925 |

Kenara uzaklık / L kutularında değişen oranı (18 dairenin toplamı): **< 0,5 L: %0.61 (191/31215)** · 0,5–1 L: %0.18 (44/25125) · 1–2 L: %0.04 (7/17614) · > 2 L: %0.00 (0/8021).

**Sonuç:**
- K7'nin "kenara yakın olay oranı" (%32–100) üyelik değişiminin ölçüsü değildir. Ölçülen değişim %0–1,52, ortanca ≈ %0.19.
- Değişimin yönü tutarlı: sınır bazı bağımlı olayları bağımsız gösteriyor (bağımlı sayısı hep azalıyor ya da aynı kalıyor). Bunun nedeni, daire dışındaki ana şokların ve bağlantı halkalarının hesapta görünmemesi.
- **Karar:** K7 uyarı olarak kalır, otomatik OFF yok. Uyarı metni ölçülen değerleri gösterir. OFF için bir eşik, ancak zaman penceresi etkisi de ölçüldükten sonra yeniden değerlendirilir.

## 8b. Kararların durumu

| Karar | Durum |
|---|---|
| D-P1 Mc tahmincisi | **Uygulandı:** sitenin `computeMcSrc` (MAXC+0,2) birebir kopyası; CI denetimli. **Bulgu:** tüm EMSC için Mc = 3,2; statik ürünün xmeff = 3,0'ı bu tahminin altında. Statik ürün değiştirilmedi; konu metodolojideki "Mc duyarlılığı" açık işine eklenmeli. |
| D-P2 Sınır | **Uygulandı:** uyarı + ölçüm (§8). Zaman penceresi etkisi açık. |
| D-P3 Pyodide kaynağı | **Uygulandı:** depoda, 0.27.7, resmi arşivle CI karşılaştırması. |
| D-P4 Eşikler | **Başlangıç değeri** olarak uygulandı (50 olay, %5); duyarlılık testi açık. |
| D-P5 Öz-sınama | **Uygulandı:** her oturumda hesaptan önce; geçmezse K0 → KAPALI. |

## 9. Sonraki aşama (ayrı onayla)

1. "Araştırma Bölgesi" panelinde GK74 satırının yanına **"Reasenberg (deneysel, Pyodide)"** anahtarı. Varsayılan KAPALI; açılınca Pyodide yüklenir.
2. Kapılar sitenin kendi durumundan beslenir: `regionCapped`, `regionLimit`, `regionSource`; Mc için sitenin kendi `computeMcSrc`'i (kopya değil, doğrudan).
3. Çıktı: sayılar + isteğe bağlı harita vurgusu (bağımlı olaylar soluk). Tekrarlanabilirlik kaydına modül sha256, Pyodide sürümü, xmeff (seçim) ve Mc (tahmin) yazılır.
4. Statik GK74/Reasenberg katmanı referans olarak kalır.

## 10. Kapsam dışı

`reasenberg.py`'de değişiklik; JavaScript'e çeviri; `cluster2000x` kuralının dinamik kullanımı (deneysel, D1 açık); deprem tahmini.


## 11. Mc duyarlılığı: xmeff 3,0 ↔ 3,2 (`mc_ve_zaman.py`, `mc_ve_zaman.json`)

Aynı katalog, aynı bölge ve dönem (tüm EMSC + 18 daire). A: M ≥ 3,0, xmeff 3,0 (statik ürün) · B: aynı katalog, xmeff 3,2 (yalnız parametre) · C: M ≥ 3,2, xmeff 3,2 (modülün önerdiği tutarlı kurulum).

| | Tüm EMSC | 18 daire (aralık) |
|---|---|---|
| B: ortak olaylarda sınıfı değişen | %0.10 | %0.00–0.96 |
| B: A kümelerinin aynen yeniden üretilmesi | %99.4 | %91.7–100.0 |
| B: küme sayısı değişimi | %-0.19 | — |
| C: ortak olaylarda (M ≥ 3,2) sınıfı değişen | %0.52 | %0.48–3.32 |
| C: A kümelerinin aynen yeniden üretilmesi | %92.9 | %82.6–95.5 |
| C: küme sayısı değişimi | %-33.1 | %-55.3 … %-28.1 |
| C: bağımlı olay sayısı değişimi | %-34.1 | %-54.6 … %-24.9 |

**Yorum:** Parametrenin kendisi (3,0 → 3,2) üyeliği az değiştiriyor (≤ %1). Büyük fark katalog kesiminden geliyor: M 3,0–3,1 olayları çıkınca küme sayısı yaklaşık üçte bir azalıyor; çünkü kümelerin önemli bir bölümü küçük olaylarla kuruluyor. Ortak olayların sınıfı ise %0,5–3,3 değişiyor. Statik ürün (A) değiştirilmedi; bu bulgu metodolojideki "Mc duyarlılığı" açık işine girdidir.

## 12. Zaman penceresi sınırı (`mc_ve_zaman.json`, `zaman_tamponu.json`)

| Pencere | N | Sınıfı değişen |
|---|---|---|
| son 90 gün | 380 | %1.05 |
| son 1 yıl | 2225 | %0.72 |
| son 5 yıl | 14525 | %0.01 |
| 1999-09-01 → 1999-12-31 (İzmit sonrası başlar) | 1349 | %1.63 |
| 2020 yılı | 2817 | %0.00 |
| 2023-02-10 → 2023-12-31 (Kahramanmaraş sonrası başlar) | 3875 | %5.83 |

Pencere başından geçen süreye göre: ilk 30 gün **%8.4** · 30–365 gün %0.22 · > 365 gün %0.00.
**Geri tampon:** 90 günlük geri tampon, ölçülen 4 pencerenin 4'ünde değişimi %0'a indirdi (30 gün: 3/4). Zaman sınırı uzaysal sınırdan belirgin biçimde daha etkili. K9 uyarısı bu ölçümle eklendi. Sitede 90 günlük geri tampon sorgusu bir sonraki adımdır (sorgu koduna dokunmayı gerektirir).

## 13. Siteye bağlama (dal `ozellik/reasenberg-dinamik`, PR ayrı)

- Araştırma Bölgesi'nde GK74 düğmesinin altında **🧪 Reasenberg (deneysel)**, varsayılan KAPALI. Kod: `lab/reasenberg-pyodide/site_rb.mjs`; `index.html`'e yalnız 1 düğme, 1 rapor kutusu ve 1 modül satırı eklendi. Sorgu kodu ve GK74 kodu değişmedi.
- Açılınca: depodaki Pyodide → K0 öz-sınama (oturumda bir kez) → K1–K9. Girdiler sitenin kendi durumundan alınır: `regionEvents`, `regionCapped`, `regionLimit`, `regionSource`, daire geometrisi, pencere başı ve sitenin `computeMcSrc`'i.
- Bölge, dönem, sınır ya da xmeff değişince kendiliğinden yeniden değerlendirilir; koşul bozulursa KAPALI, sağlanınca yeniden çalışır.
- **GK74 ↔ Reasenberg double-check:** GK74 açıksa aynı olaylarda dört grup gösterilir: ikisi de bağımsız, ikisi de bağımlı, yalnız GK74 bağımlı, yalnız Reasenberg bağımlı. Ayrıca farklı grupların büyüklük dağılımı ve yıl aralığı verilir. Hiçbir yöntem doğru kabul edilmez.
- Sonuç yalnız raporlanır; harita, GK74 ve diğer analizler değişmez.
- Tarayıcı testi (İzmit R = 100 km, EMSC):

| Durum | Sonuç |
|---|---|
| Sınır 500 | KAPALI (K1) |
| Sınır 5000 | UYARILI, 61 küme, 64 ms (kendiliğinden yeniden çalıştı) |
| xmeff 2,5 | KAPALI (K5) |
| GK74 açık | ikisi de bağımsız 496 · ikisi de bağımlı 210 · yalnız GK74 823 · yalnız Reasenberg 9 (toplamlar GK74 ve Reasenberg sayılarıyla tutarlı) |
