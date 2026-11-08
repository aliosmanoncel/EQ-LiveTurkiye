# Dinamik Reasenberg — Pyodide tasarım notu ve deneme sonuçları

**Tarih:** 2026-11-08 · **Dal:** `deneme/pyodide-reasenberg` · **Durum:** deneme; `main` ve site (`index.html`) değişmedi; statik GK74/Reasenberg katmanı aynen korunur.

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
| JavaScript'e çeviri (B seçeneği) | OUT (şimdilik) | İkinci uygulama doğrulama yükü getirir; Pyodide yeterli hızda (§5) |

## 3. Bileşenler (bu dal)

| Dosya | İş |
|---|---|
| `lab/reasenberg-pyodide/rb_core.mjs` | Pyodide'e üç Python dosyasını yazar, sha256 denetler, `decluster` çağırır. Algoritma kodu içermez. Tarayıcı ve Node ortak. |
| `lab/reasenberg-pyodide/gates.mjs` | Uygunluk kapıları K1–K8, MAXC+0.2 Mc tahmini (yalnız deneme için). |
| `lab/reasenberg-pyodide/index.html` | Deneme sayfası: ortam, öz-sınama, daire içi dinamik deneme. Sitenin parçası değil. |
| `scripts/reasenberg_tests/pyodide_parity.mjs` | Eşleşme testi (P1, P2) + süre ölçümü. |
| `scripts/reasenberg_tests/gates.test.mjs` | Kapıların birim testleri (9 test). |
| `.github/workflows/reasenberg-pyodide.yml` | CI: Pyodide 0.27.7 (GitHub sürümünden, önbellekli) + kapı testleri + eşleşme. |

## 4. Uygunluk kapıları

| Kod | Kapı | Sağlanmazsa |
|---|---|---|
| K1 | Katalog bütünlüğü: sorgu üst sınıra takılmadı | **OFF** |
| K2 | Tek kaynak (yineleme ayıklaması yok) | **OFF** |
| K3 | Geçersiz alan oranı ≤ %5 | **OFF** |
| K4 | Tekil kimlik (sıralama adaptörde UTC) | **OFF** |
| K5 | Mc tahmin edilebildi ve xmeff ≥ Mc (tahmin) | **OFF** |
| K6 | N(M ≥ xmeff) ≥ 50 | **OFF** |
| K7 | Sınır etkisi: kenara 10·r(Mmax) km'den yakın olay oranı | uyarı |
| K8 | Büyüklük ölçeği karışımı | uyarı |

Durum: herhangi bir **OFF** → hesap yok · yalnız uyarılar → "ON (uyarılı)" · hiçbiri → ON.

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
| Tarayıcı (Chromium) öz-sınaması, 4 referans | **birebir aynı** |

## 6. Performans

| | Node (Pyodide) | Chromium (Pyodide) | CPython |
|---|---|---|---|
| Başlatma (çekirdek + numpy + modül) | 3,1 s | 3,6 s (yerel dosya; ağdan ~13 MB ek indirme) | — |
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
| İzmit, R = 100 km, 1998–2026, EMSC, sınır 500 | **OFF** | K1: 500'e takıldı |
| Aynı, sınır 5000 / sınırsız (N = 1538) | ON (uyarılı) | K7 sınır (%57,8), K8 ölçek; tekil 1258 · temsilci 61 · bağımlı 219 |
| Aynı, 1990–2026, EMSC + ISC | **OFF** | K2: iki kaynak |
| Aynı, xmeff = 2,0 (seçim) | **OFF** | K5: Mc (tahmin) 3,2'nin altında |
| Tüm EMSC, xmeff = 3,0 | **OFF** | K5: Mc (MAXC+0,2) = 3,2 |
| Tüm EMSC, xmeff = 3,2 | ON (uyarılı) | K8; küme 2076, 5,8 s |

## 8. Bulgular ve açık kararlar

- **D-P1 Mc tahmincisi (önemli).** Deneme sayfasındaki MAXC+0,2, tüm EMSC kataloğu için Mc = 3,2 veriyor. Statik ürünün kullandığı xmeff = 3,0 bu tahminin altında, yani K5 statik ürünün yapılandırmasını engellerdi. Bu bir hata değil, Mc duyarlılığı sorusudur (metodoloji belgesinde "sıradaki araştırma" olarak açık). Bütünleştirmede sitenin mevcut Mc tahmincisi (kümülatif GFT) kullanılmalı; MAXC+0,2 yalnız denemedir. Karar gerekir: K5 hangi tahminciyle ve hangi payla (ör. tahmin ± belirsizlik) uygulanacak?
- **D-P2 Sınır etkisi eşiği.** Küçük dairelerde ve büyük olaylarda kenar payı çok büyüyor (R = 100 km, Mmax 6,3 → %58). Şu an yalnız uyarı. Bir oranın üstünde OFF olsun mu?
- **D-P3 Pyodide'in kaynağı.** Deneme sayfası jsDelivr'den sürüm sabitlenmiş (0.27.7) yükler. Tedarik zinciri için dağıtımın depoya alınması (~16 MB, GitHub Pages) ya da bütünlük karmalarının sayfada denetlenmesi seçenekleri var.
- **D-P4 En az olay sayısı (K6 = 50)** ve geçersiz oran eşiği (K3 = %5) deneme değerleridir.
- **D-P5 Sitede öz-sınama.** Her yüklemede 4 referansla kısa bir öz-sınama (~1 s) çalıştırılıp geçmezse dinamik hesap kapatılsın mı?

## 9. Sonraki aşama (ayrı onayla)

1. "Araştırma Bölgesi" panelinde GK74 satırının yanına **"Reasenberg (deneysel, Pyodide)"** anahtarı. Varsayılan KAPALI; açılınca Pyodide yüklenir.
2. Kapılar sitenin kendi durumundan beslenir: `regionCapped`, `regionLimit`, `regionSource`, sitenin Mc tahmincisi.
3. Çıktı: sayılar + isteğe bağlı harita vurgusu (bağımlı olaylar soluk). Tekrarlanabilirlik kaydına modül sha256, Pyodide sürümü, xmeff (seçim) ve Mc (tahmin) yazılır.
4. Statik GK74/Reasenberg katmanı referans olarak kalır.

## 10. Kapsam dışı

`reasenberg.py`'de değişiklik; JavaScript'e çeviri; `cluster2000x` kuralının dinamik kullanımı (deneysel, D1 açık); deprem tahmini.
