# Faz 5 — Üretime aktarım planı (SALT OKUNUR, 2026-10-21)

**Durum:** plan; uygulanmadı, onaylanmadı. `main` (incelenen sürüm `0e875b0`), `index.html`, `eq_historical.json`, `mw_authority.json`, GK74 ve mevcut merdiven değişmedi. Korunan dosyaların `main` ile aynı olduğu SHA-256 ile doğrulandı: `eq_historical.json` bd303aa3…, `mw_authority.json` 5f39c6d8…. Prototip referansı: `homog-faz0` @ `68132ec` (aday merdiven) ve `f09b26c` (sabitlenmiş Mw aktarımı).

Betikler: `katalog_hazirla.py` (seriler) ve `etki_weichert.js`. İkincisi, üretim Weichert zincirini `main`'deki `index.html`'den birebir okur; yöntem `scripts/test_weichert_chain.js` ile aynıdır ve kod kopyası tutulmaz. Sonuçlar: `out/etki_weichert.json`.

## 1. Dosya ve kod incelemesi

### 1.1 Tamlık merdiveni üretimde nerede?

| Yer | İçerik | Rolü | Not |
|---|---|---|---|
| `index.html` `csSteps` (≈ satır 4770–5300) | Kullanıcının girdiği basamaklar; URL parametresi; "Öneri" düğmesi veriden üretir | Weichert / b(t) hesabı | **Sabit bir merdiven tablosu yok.** Aday merdiven kodda "değiştirilecek" bir değer değildir |
| `scripts/fetch_combined_catalog.py` `MC` (satır 20–34) | 1900:5,5 · 1965:4,5 · 1980:4,0 · 1990:3,5 · 1998:3,0 | ISC/EMSC **sorgu alt sınırları** (katalog bu eşiklerle indirildi) | Faz 1c–4'teki "mevcut merdiven" budur. Değiştirilirse indirilen katalog değişir; **değiştirilmemeli** |
| `eq_historical.json` → `completeness` | 1900–1960: 5,5 · 1960–1998: 4,5 · 1998–2026: 3,0 | Yalnız bilgi satırı (`histHint`, ≈ satır 7168) | `MC` tablosuyla **tutarsız** (1960 ↔ 1965; 1980/1990 basamakları yok). Korunan dosyada olduğu için yalnız işaretlendi |

**Sonuç:** Merdiveni aktarmak, bir değeri değiştirmek değil, `index.html`'e **isteğe bağlı bir hazır basamak seçeneği** (preset) eklemek ve yöntemi belgelemek demektir.

### 1.2 Tekdüzelik sorunu (karar gerektirir)

Basamaklı tamlık tekdüze olmalıdır: bir eşiğin tam olduğu yıldan sonra daha yüksek eşikler de tamdır. Aday tablo (M 5,0–5,5 → 1979) ile korunan M < 5 eşiği (4,5 → 1965) bu kuralla çelişir: 4,5 sınıfı 1965'ten tam ise 5,0 sınıfı da tam olmalıdır.

Etki analizinde bu yüzden en az değişiklikli tekdüze sürüm kullanıldı:

**L1 = 1904: 6,0 · 1970: 5,5 · 1979: 4,5 · 1980: 4,0 · 1990: 3,5 · 1998: 3,0**

4,5 basamağı 1965 → 1979'a kaydı. Bu kayma kararın kendisinden değil, tekdüzelik kuralından kaynaklanıyor; onaya sunulur.

### 1.3 1.144 Mw aktarımı hangi dosyaları etkiler?

**Aktarımın bileşimi:**
- **Döneme göre:** 1904–1962: 133 · 1963–1997: 543 · 1998–2021: 468 aktarım.
- **Kaynak olaya göre:** ISC 676 · EMSC 468.
- **Mw türüne göre:** doğrudan 638 · vekil 506.
- 14 aktarım koruma istisnasıyla yapıldı.
- Ayrıca 273 adet 1904–1962 ISC-GEM olayı ekleniyor.

`eq_historical.json`'u okuyan üretim bileşenleri:
- `index.html`: Tarihsel katman, bölge analizi, GK74, Weichert.
- `scripts/build_bvalue_*`, `build_delta_b`, `build_forecast_test`, `build_fractal_grid`: Çevrimdışı çalışırlar. Çoğu yalnız 1998 sonrası EMSC verisini kullanır.
- `scripts/validate_gk74_parity.py` ve `fixtures/gk74_*`: Fikstürler katalog alt kümesinin SHA-256 değerini doğrular. Katalog değişirse "katalog değişmiş" hatası verirler.
- `seismoreport/*`: kopya betikler.

| Seçenek | Ne değişir | Değerlendirme |
|---|---|---|
| **A. `eq_historical.json` yerinde güncellenir** | `mw` alanları ve 273 yeni olay | Korunan dosya değişir. GK74 eşdeğerlik fikstürleri geçersizleşir. "Original" = yalnız yerel Mw ilkesi (2026-10-11) bozulur. Çevrimdışı ürünler yeniden üretilirse 468 EMSC olayı da etkilenir. **Önerilmez** |
| **B. Ayrı katman (önerilen)** | Yeni dosyalar: `data/mw_iscgem.json` (1.144 kayıt, `aktarim_kaydi.json` alanları + 1910 alternatifi), `data/iscgem_ek_1904_1962.json` (273 olay), `data/LISANS_ISC-GEM.txt`. `index.html`: `mw_authority` yükleyicisinin benzeri, varsayılan **kapalı** bir "ISC-GEM v12.1 Mw" seçeneği ve "Aday merdiven" hazır basamak düğmesi | Korunan dosyalar, GK74 ve çevrimdışı betikler değişmez. Seçenek kapalıyken çıktı birebir aynı kalır |

**B için açık kararlar:**
1. **`mw_authority` ile öncelik:** İki seçenek birlikte açıkken aynı olaya iki Mw gelebilir. Öneri: `mw_authority` (USGS, doğrulanmış) önce gelsin.
2. **Magnitude Conversion seçicisiyle ilişki:** ISC-GEM Mw'si aktarılan olaylar yerel Mw gibi işlem görsün; bağıntı uygulanmasın, `mcv` alanı atanmasın.
3. **Lisans:** ISC-GEM verisi CC BY-SA 3.0 lisanslı. Türetilmiş veri dosyası atıf ve aynı lisansla yayımlanmalı. Depoda genel bir LICENSE dosyası yok; lisans dosyası veri dosyasının yanında tutulur.

## 2. Etki ve tutarlılık analizi

Hesap ayarları:
- Üretim kodu: `csBuild` → sınıflama → `weichertFit`.
- ΔM = 0,1; Mx yok; dönem 1900–2021 (ISC-GEM kapsamı).
- Tüm Türkiye kutusu.
- Mevcut merdiven L0, `MC` tablosudur.

**Kataloglar:**
- **C0:** üretim kataloğu, "Original" büyüklüklerle.
- **C1:** prototip; ISC-GEM Mw aktarılmış ve 273 olay eklenmiş.

Aşağıdaki tablo GK74 uygulanmış serilere aittir. Ham seriler `out/etki_weichert.json` dosyasında.

| Katalog · merdiven | b (M ≥ 4,5) | b (M ≥ 5,0) | λ(≥5,0) gözlenen /yıl | λ(≥5,5) gözlenen | λ(≥6,0) gözlenen |
|---|---|---|---|---|---|
| C0 · L0 (bugünkü durum) | 1,105 ± 0,019 | 0,927 ± 0,033 | 9,35 | 2,62 | 1,29 |
| C0 · L1 | 1,048 ± 0,020 | 0,888 ± 0,032 | 9,98 | 3,00 | 1,33 |
| C1 · L0 | 0,948 ± 0,016 | 0,944 ± 0,028 | 13,07 | 4,21 | 1,43 |
| **C1 · L1 (aday paket)** | 0,974 ± 0,019 | 0,917 ± 0,030 | 12,22 | 3,69 | 1,48 |

Tüm sınıflar birlikte (M ≥ 3,0) fitlendiğinde b dört durumda da 1,02–1,04 arasında. Bu fit M 3,0–3,5 sınıflarının ağırlığı altında kalıyor ve merdivene duyarsız.

**Bulgular** (yalnız bu hesaba dayanır; tehlike sonucu değildir):
1. **Baskın etki katalogdan geliyor (C0 → C1, L1 altında).** λ(≥5,0) %22, λ(≥5,5) %23 artıyor. b (M ≥ 4,5) 1,048 → 0,974'e iniyor; b (M ≥ 5,0) neredeyse değişmiyor (0,888 → 0,917). Bu yön, mb doyması düzeltmesiyle tutarlı. Aynı yön L0 altında daha da büyük.
2. **Merdiven etkisinin yönü kataloğa bağlı.** C0'da L1 oranları **artırıyor** (λ(≥5,5) +%15). C1'de **azaltıyor** (λ(≥5,5) −%12, λ(≥5,0) −%7); λ(≥6,0) yalnızca +%3. Önceki mesajımda mevcut merdivenin oranları "sistematik olarak düşük" gösterebileceğini yazmıştım. Bu, prototip katalog için **doğrulanmadı**; düzeltiyorum. Yönü belirleyen, dönemler arasındaki gözlenen oran farklarıdır.
3. **Merdiven, katalogla birlikte aktarılmalı.** L1 yalnızca C1 üzerinde sınandı. L1'i C0 ile kullanmak (C0 · L1) sınanmamış bir birleşimdir; tek başına aktarılmamalı.
4. **b'nin fit aralığına duyarlılığı merdiven etkisinden büyük.** C1 · L1'de M ≥ 4,5 için 0,974, M ≥ 5,0 için 0,917. Üretimde fit aralığı kullanıcının seçimidir; bu duyarlılık raporlanmalı.

## 3. Regresyon testleri

**Taban** (`main` @ `0e875b0`, ayrı bir çalışma ağacında, salt okunur çalıştırıldı):

| Test | Sonuç |
|---|---|
| test_amr | 27/0 |
| test_ben_decomp | 18/0 |
| test_bt_adaptive | 114/0 |
| test_class_levels | 29/0 |
| test_gr_consistency | 99/0 |
| test_mc_grid | 39/0 |
| test_md_chain | 21/0 |
| test_type_filter | 10/0 |
| test_weichert_chain | 27/0 |
| `validate_gk74_parity.py` (varsayılan, `--context`, `--mwauth`) | BİREBİR AYNI |
| `test_fit_range.js` | **`main`'de zaten bozuk** (`function csBvalueTimeSeries(cs)` bulunamıyor). Aktarımdan bağımsız; ayrıca düzeltilmeli |

**Aktarım için eklenmesi önerilen testler:**
- **T-kapalı:** Seçenek kapalıyken tüm testler ve GK74 eşdeğerliği tabanla birebir aynı. `eq_historical.json` ve `mw_authority.json` SHA-256 değerleri değişmemiş.
- **T-açık:** Tarayıcı yolu (yükleyici + katman + `csBuild`/`weichertFit`), `out/etki_weichert.json` içindeki C1 sayılarını (N, b, λ) yeniden üretiyor.
- **T-GK74:** Seçenek açıkken Python ve JS GK74 sonuçları aynı. Yeni fikstür, `mw_authority` ile aynı yapıda.
- **T-öncelik:** `mw_authority` ile ISC-GEM katmanı çakıştığında karar 1'deki kural uygulanıyor.
- **T-preset:** "Aday merdiven" düğmesi `csSteps`'i tam olarak L1 yapıyor; URL'de korunuyor.
- **T-1910:** 1910-02-18 olayı M 7,0'da kalıyor; 5,85 yalnızca alternatif olarak gösteriliyor.

## 4. Geri alma

- B seçeneği yalnızca ekleme yapar. Geri alma, aktarım commit'lerinin `git revert` ile geri alınmasıdır; veri dosyası silmeye gerek kalmaz.
- Acil durumda ara çözüm: varsayılan zaten kapalı olduğu için yalnız düğme gizlenir.
- `sw.js` ağı önceleyen bir önbellek kullanıyor; geri almada `VERSION` değiştirilmesi, eski veri önbelleğinin temizlenmesi için önerilir.
- Aktarım ayrı bir dalda, PR üzerinden yapılmalı. Birleştirmeden önce bölüm 3'teki testler GitHub Actions'ta çalıştırılmalı; `gk74-parity.yml` zaten mevcut.

## 5. Onaya sunulacak kararlar

1. B seçeneği (ayrı katman, varsayılan kapalı) mı, A mı?
2. Tekdüze aday merdiven L1: 4,5 basamağının 1965 → 1979'a kayması.
3. `mw_authority` önceliği ve seçici ile ilişki (bölüm 1.3, karar 1–2).
4. ISC-GEM türetilmiş verisinin CC BY-SA 3.0 ile depoda yayımlanması.
5. `eq_historical.json` → `completeness` tutarsızlığının belgelenip belgelenmeyeceği. Dosya korunduğu için düzeltilmez.
6. Bu plana göre uygulamaya geçilip geçilmeyeceği (üretim onayı).

## 6. Etki ayrıştırması (2×2 tasarım, GK74; bölüm 2'deki sayılardan, yeni hesap yok)

Toplam fark = C1·L1 − C0·L0. Etkiler iki sırada da hesaplandı ve ortalandı (Shapley ayrıştırması). Etkileşim büyük olduğu için tek sıralı ayrıştırma yanıltıcı olur.

| Gösterge | Toplam | Katalog etkisi (L0 / L1 altında → ort.) | Merdiven etkisi (C0 / C1 altında → ort.) |
|---|---|---|---|
| λ(≥5,0) /yıl | +2,87 | +3,72 / +2,24 → **+2,98** | +0,63 / −0,85 → **−0,11** |
| λ(≥5,5) /yıl | +1,07 | +1,60 / +0,69 → **+1,14** | +0,39 / −0,53 → **−0,07** |
| b (M ≥ 4,5) | −0,131 | −0,157 / −0,074 → **−0,116** | −0,057 / +0,026 → **−0,016** |

Net farkın tamamına yakını büyüklük homojenizasyonundan geliyor. Merdivenin net etkisi sıfıra yakın, ancak yönü kataloğa göre değişiyor (etkileşim).

Tekdüzelik notu (bölüm 1.2): Faz 4'te 4,5–5,0 sınıfı için Stepp (K2) **1995** başlangıcını verdi. Faz 4'te bu sınıf için bağımsız doğrulama yoktu. 4,5 basamağının 1979'a kayması bu kanıttan daha tutucu değil, daha serbesttir.

## 7. Geliştirme dalı ve test sonuçları (2026-10-21) — üretime ONAYLANMADI

Dal `homog-uretim-aday` @ `5f73246`, `main` @ `0e875b0` üzerine. `main`'e birleştirilmedi, PR açılmadı.

**Değişiklik listesi:**

| Dosya | Tür | İçerik |
|---|---|---|
| `index.html` | +67 / −1 satır | `#histIscgem` işaret kutusu (varsayılan kapalı); `iscgemApply` / `loadIscgem` / `iscgemCatalog`; `rebuildHistoricalView` içinde tek koşullu satır; bilgi satırı; `CS_PRESETS` + `csApplyPreset` ve "Aday merdiven" düğmesi |
| `data/mw_iscgem.json` | yeni | 1.144 aktarım (133'ünde 1963 öncesi zaman/konum) + 1910 alternatifi; lisans/atıf meta |
| `data/iscgem_ek_1904_1962.json` | yeni | 273 olay, eq_historical şeması, `src: ISC-GEM` |
| `data/LISANS_ISC-GEM.txt` | yeni | CC BY-SA 3.0, telif (ISC ve GEM Vakfı), veri ve makale atıfları, değişiklik bildirimi |
| `scripts/test_iscgem_overlay.js`, `scripts/fixtures/iscgem_overlay_ref.json` | yeni | 35 denetim |
| `.github/workflows/iscgem-overlay.yml` | yeni | Katman testi ve Weichert zinciri testi |

Korunan dosyalar (`eq_historical.json`, `mw_authority.json`, `decluster_gk74.py`, `fetch_combined_catalog.py`) değişmedi.

**Kaynak önceliği kuralı:**
- ISC-GEM aktarılan bir olay `mw_authority` kaydıyla da eşleşirse `mw_authority` Mw kullanılır. Eşleştirme GK74 Faz 2a eşleştiricisiyle yapılır (kaynak kimliği ya da ±60 s ve ≤ 50 km).
- ISC-GEM karşılığı olmayan olaylara dokunulmaz.
- 7 çakışma bulundu: 1999 İzmit 7,58→7,6; 1999 Düzce 7,16→7,2; 2011 Van 7,14→7,1; 2020 Samos 6,99→7,0; 2017 Halabja 7,4→7,3; 2006 Kythira 6,73→6,7; 2018 Sarpol-e Zahab 6,3→6,3. Farklar en çok 0,1.

**Test sonuçları:**

| Test | Sonuç |
|---|---|
| Katman testi, yerel (35 denetim) | 35/0 |
| Katman testi, GitHub Actions run 39513857705 | başarılı |
| Kapalı seçenek: mevcut 10 JS testi ve 5 GK74 eşdeğerlik çalıştırması | Çıktılar `main` ile **bayt bayt aynı**. `test_fit_range.js` `main`'de de aynı hatayla bozuk; yalnız dosya yolu farklı |
| Açık seçenek: katalog özeti (88.606 olay, zaman, konum, M) | Sabitlenmiş prototiple birebir aynı (SHA-256). Weichert N ve b, etki analiziyle aynı |
| Açık seçenek: GK74 Python == tarayıcı JS (mag, mw) | BİREBİR AYNI |
| Tarayıcı (Chromium, yerel sunucu, 1900–1970 penceresi) | Kapalıyken n = 662, `main` ile aynı; açıkken 935 (+273); kapatınca yine 662. Sayfa hatası yok. Ağa bağlı WebSocket hatası ortam kaynaklı |
| GK74 eşdeğerlik iş akışı (dalda) | başarılı |

**Lisans:** ISC indirme sayfası (erişim 2026-10-21) şunları belirtiyor:
- Telif: "Copyright (C) 2025 International Seismological Centre and GEM Foundation".
- Lisans: "CC-BY-SA 3.0 (unported)". Ayrı bir yeniden dağıtım kuralı belirtilmemiş.

Atıf biçimi isc.ac.uk/iscgem/citing.php sayfasından alındı. Önceki dosyalarda telif sahibi yalnız ISC olarak yazılmıştı; düzeltildi. CC BY-SA 3.0'ın gerektirdikleri: atıf, lisans adresi, değişikliklerin belirtilmesi ve türetilmiş verinin aynı lisansla paylaşılması. Lisans yalnız iki veri dosyası için yazıldı. Bu bir hukuki görüş değildir.

**Bilinen sınırlar:**
1. `eq_historical.json`'daki ISC zamanları saat dilimi eki taşımaz ve tarayıcı bunları yerel saat olarak okur. Bu, `main`'de de var olan bir durumdur. Katman, aynı biçimi kullanarak tutarlılığı korur.
2. Merdiven ön ayarı katman kapalıyken de seçilebilir; bu durumda bir uyarı gösterilir.
3. M 4,5 basamağı bağımsız olarak doğrulanmadı (Stepp 1995).
