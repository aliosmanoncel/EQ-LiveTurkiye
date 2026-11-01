# Deprem aşılma olasılığı modülü — geliştirme planı (2026-11-01, aşama 0)

**Durum:** Bu belge yalnızca plandır; tabloya ve eğriye kod eklenmedi.

**Dal:** `bolge-karsilastirma-a-etiketi`, güncel `main` (5ea201d) ile eşitlendi: 0424a6e, çakışma yok. Dal `main`'in gerisinde değil; `main`'e göre 9 commit önde. Yalnızca G–R panelindeki Poisson satırını ve `analysis/poisson_olasilik/`'i ekliyor.

## 0. Mevcut Poisson satırının yeniden doğrulanması (güncel `main` üzerinde)

| Denetim | Sonuç |
|---|---|
| `scripts/test_poisson_prob.js` (analitik P ve Tr, panel eğrisiyle tutarlılık, sentetik kapsama, gözlenen–öngörülen) | 23/23 |
| `kabul_poisson.js`, önce = güncel `main`: G–R grafiği ve Poisson satırı dışındaki metin aynı; λ, Tr, P bağımsız hesapla aynı; uyarılar | 42/42 |
| Tüm birim testleri (18 dosya) | 18/18 |

## 1. Veri akışı (bugünkü kod)

**Karşılaştırma tablosu:**
- `cmpAdd` (satır 3570) bir kayıt saklıyor: `{ name, src, shape, area, cLat, t0, t1, Mc, dm, mags[], types, pts[], url }`.
  - `mags`: `lastGrEvList`'ten `(e.mw ?? e.mag)`, 0,01'e yuvarlanmış.
  - `Mc`: `lastGrMc` ya da `computeMcScale`.
  - `t0`, `t1`: `regionWindowStart` / `regionWindowEnd`.
- `cmpStats` (satır 3590) hesaplıyor:
  - T = (t1 − t0)/365,25 gün; u = A/10⁴ km².
  - b = `computeBvalue` (Aki–Utsu, ΔM düzeltmeli); a = log₁₀(n/(T·u)) + b·Mc.
  - **tr6 = 1/(10^(a − 6b)·u)**, yani λ(≥6) = (n/T)·10^(−b(6 − Mc)) ve tr6 = 1/λ(≥6).
- `cmpRender` (satır 3603) tabloyu ve `cmpSvg` grafiğini çiziyor. Grafik PNG ve poster çıktısına giriyor (satır 4342–4365).
- Karşılaştırma yalnızca **tek Mc**'yle çalışıyor; tamlık basamakları (Weichert) kullanılmıyor.

**G–R panelindeki Poisson satırı (dal):**
- λ, tek Mc: `grLambdaSimple(n, T, b, Mc, M)` (satır 5647).
- λ, Weichert: `grLambdaWeichert(rate0, β, m0, M, mx)` (satır 5649); Mx girilmişse kesik G–R.
- P = `grPoissonP(λ, t)` = −expm1(−λt) (satır 5645); Tr = 1/λ.
- Belirsizlik:
  - `grPoissonBootSimple` (satır 5657): n* ~ Poisson(n), büyüklükler b̂ ile üstel çekilip ΔM ızgarasına yuvarlanır, b* yeniden kestirilir. **a ve b'nin ortak belirsizliğini zaten taşıyor**: n* a'yı, b* b'yi değiştirir.
  - `grPoissonBootWeichert` (satır 5670): sınıf sayıları Poisson'dan çekilir, Weichert yeniden uydurulur.
- Gözlenen ile beklenen: `grObsVsExp` (kesin Poisson p, Garwood %95).

## 2. Yeni özelliklerin kullanacağı fonksiyonlar

| Özellik | Kullanılacak | Yeni kod |
|---|---|---|
| Tablo: P(M ≥ 5, 6, 7; t = 10, 50, 100) | λ = `grLambdaSimple(n, T, b, Mc, M)`, P = `grPoissonP(λ, t)`; n, T, b, Mc `cmpStats`'tan (aynı model, aynı λ) | `cmpStats`'a P alanları; `cmpRender`'a satırlar |
| Olasılık eğrisi: x = M, y = P(%); t = 10, 25, 50, 100; çok bölge | Aynı λ(M); M ızgarası Mc'den max(Mmax + 0,5; 8,0)'e, 0,1 adımla | Yeni SVG (`cmpProbSvg`); mevcut SVG yardımcıları |
| %95 bant (a ve b ortak) | `grPoissonBootSimple` ile aynı çekiliş şeması | Tek bootstrap geçişinde her çekilişin (n*, b*) çifti saklanır; λ*(M) = (n*/T)·10^(−b*(M − Mc)) bütün (M, t) noktaları için bu çiftlerden. Mevcut fonksiyon değişmez. |
| Uyarılar | `lastMcUyari`, `lastTurUyari`, GK74 durumu | `cmpAdd` kayda üç alan ekler: `gk74`, `mcUyari`, `turUyari`. Eski kayıtlarda (localStorage) "bilinmiyor" gösterilir. |

**Tutarlılık testleri** (ChatGPT koşulu 1):
- (a) P(M ≥ 6, t) = 1 − e^(−t/tr6), sayısal olarak tablodaki tr6 ile aynı.
- (b) Tablo hücreleri, eğrinin aynı (M, t) noktalarıyla aynı.
- (c) Yeni bootstrap sarmalayıcısı, aynı tohumla tek (M, t) için `grPoissonBootSimple` ile aynı yüzdelikleri veriyor.
- (d) P, M arttıkça azalıyor, t arttıkça artıyor (monoton).

## 3. Bilimsel uyarılar (panelde görünür)

- Sabit metin: **"Poisson modeli: sabit oranlı, zamandan bağımsız istatistiksel olasılık. Deprem tahmini değildir."** ve "Olasılık bölgenin tamamı içindir (A km²)".
- **Ekstrapolasyon:** M > gözlenen Mmax hücreleri işaretli; eğri bu bölümde kesikli.
- **Tamlık ve tür:** Kayıtta Mc uyarısı ya da tür geçişi uyarısı varsa bölge satırında ⚠ ve kısa açıklama: "olasılıklar ölçek ya da tamlık farkından etkilenebilir".
- **Bağımsızlık:**
  - GK74 kapalı: "artçılar dahil: olasılıklar büyük olasılıkla şişkin".
  - GK74 açık: "GK74 bağımsızlığı garanti etmez; büyük dizi dönemlerinde olasılıklar iyimser kalabilir" (Poisson dönem raporu §3).
- **mb doygunluğu:** Büyüklüklerin çoğu mb ise "M ≥ 6'da eksik sayım olası".
- **Kesik G–R (Mx):** Karşılaştırmada yok; tablo kesilmesiz G–R ile çalışır (tr6 ile aynı) ve bu yazılır. Kesik G–R ileride seçenek olarak eklenebilir (karar 2).

## 4. Testler (üretim güvenliği)

1. **Birim testleri:** analitik P, tutarlılık (a)–(d), sentetik katalogda bootstrap bandının kapsaması (birkaç (M, t) için ≈ %95), eski kayıtlarla uyum.
2. **Kabul testi, önce = sonra:** Karşılaştırma tablosunun mevcut satırları (a, b, N, tr6, Ṁ₀ …) ve `cmpSvg` aynı; G–R paneli, Poisson satırı, b(t), a(t), Mc ve tür uyarıları aynı. Yeni satırlar ve yeni grafik ayrıca denetlenir.
3. **PNG ve poster çıktısı:** `cmpSvg` ve yeni `cmpProbSvg` dışa aktarımda doğru boyut ve metinle çıkıyor.
4. **Canlı denetim** birleştirmeden sonra.

## 5. Ayrı bir düzeltme önerisi: T'nin bugünü aşması (karar 1)

- Canlı sorguda `endT = dateToVal + 'T23:59:59'`. Tarih kutusuna ileri bir gün yazılınca (örneğin 2026-12-31), T henüz yaşanmamış süreyi de içeriyor.
- Örnek: Hong Kong karşılaştırmasında dönem sonu 2027-01-01 göründü. Etki: T yaklaşık %0,3 uzun, λ aynı oranda küçük.
- Kısa pencerelerde etki büyür: 2026'nın tamamı Kasım'da sorgulanırsa T yaklaşık %17 uzun.
- Önerilen düzeltme: T = min(endT, şimdi).
- **Bu, mevcut a, λ ve tr6 değerlerini değiştirir.** Bu yüzden "önce = sonra" kapsamına girmez; ayrı commit, önce/sonra değerlerinin raporu ve ayrı onay gerektirir.
- Ayrıca başlangıç etiketi yerel saat ile UTC'den dolayı 1970-12-31 görünüyor; yalnızca etiket.

## 6. Literatür dayanağı (Zotero kütüphanesi)

- **Alkan vd. (2025),** Marmara: bölge bölge P(M) = 1 − e^(−N(M)·T) ve tekrarlanma süreleri. Tablo ve eğrinin doğrudan karşılığı.
- **Murru vd. (2016),** Marmara M ≥ 7: Poisson ile BPT ve BPT + ΔCFF karşılaştırması; olasılık benzetimden 16., 50. ve 84. yüzdeliklerle. Bant için %95'e ek olarak 16–84 seçeneği önerisi bu çalışmadan.
- **Parsons (2004):** Marmara 30 yıllık bölgesel Poisson olasılığı. Zamana bağlı modellerle farkın tartışması için.
- **Khodaverdian vd. (2016):** büyüklüğe göre yıllık aşılma olasılığı eğrisi.

Not: Bu modül yalnızca zamandan bağımsız Poisson modelini kapsar. BPT ya da zamana bağlı modeller kapsam dışı; panelde bu açıkça yazılır.

## 7. Karar bekleyen noktalar

1. T düzeltmesi (§5) bu işe mi dahil olsun, yoksa önce ayrı bir düzeltme mi yapılsın?
2. Karşılaştırmada kesik G–R (Mx) seçeneği istenir mi?
3. Bant: %95 (2,5–97,5) mı, 16–84 mü, ikisi birden mi?
4. Eğrinin süreleri: önerilen 10, 25, 50, 100 yıl; 30 yıl (Parsons, Murru) eklensin mi?
