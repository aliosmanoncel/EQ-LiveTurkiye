# GK74 bağlam (tampon) prototipi — Saimbeyli doğrulaması

**Tarih:** 2026-10-06 · **Durum:** yalnızca Python prototipi; `index.html` DEĞİŞMEDİ, commit/push YOK.
**Betik:** `scripts/gk74_context_prototype.py` (yeni, `decluster_gk74.py` değişmedi)
**Çıktı:** `analysis/2026-10-06_gk74_baglam_saimbeyli.json`

## Girdi
- Katalog: `data/eq_historical.json` (ISC 1900–1997 + EMSC 1998–2026-09-14; M ≥ 3; `mag` alanı = tarayıcıdaki EMSC canlı sorgusuyla aynı alan).
- Daire: 37,74°K, 36,10°D, R = 50 km; 2012-01-20 → 2026-09-14 (14,65 yıl); ham N = 871 (M ≥ 3).
- Posterin canlı EMSC kataloğu (M ≥ ~1,5; 7.582 olay) ağ erişimi olmadığı için kullanılamadı. Sayılar posterle doğrudan karşılaştırılamaz; algoritmanın davranışı test edilmiştir.

## Varyantlar
| Kod | Tanım |
|---|---|
| A | Bağlamsız: yalnız daire olayları (bugünkü EQ-Live) |
| B | Bağlamlı: R < d ≤ R + 90 km, M ≥ 4,0, zaman [başlangıç − 1100 gün, bitiş] |
| B2 | B + erişim filtresi: yalnız D(M) ≥ d − R olan bağlam olayları |
| G | Altın standart: tüm katalog ayıklanır, sonra daire kesilir |

A ve G, referans `decluster_gk74.decluster()` çıktısıyla birebir aynı (betikte assert).

## Pencere kontrolü (`gk_window`, kodla hesaplandı)
| M | D (km) | T (gün) | T (yıl) |
|---|---|---|---|
| 4,5 | 34,7 | 77,1 | 0,21 |
| 5,0 | 40,0 | 143,7 | 0,39 |
| 5,2 | 42,3 | 184,4 | 0,50 |
| 6,0 | 53,2 | 499,3 | 1,37 |
| 7,5 | 81,6 | 952,6 | 2,61 |
| 7,6 | 83,9 | 959,6 | 2,63 |
| 7,8 | 88,8 | 973,9 | 2,67 |

D(M) = 10^(0,1238M + 0,983); T(M) = 10^(0,5409M − 0,547) (M < 6,5), 10^(0,032M + 2,7389) (M ≥ 6,5).
**Not:** EMSC kataloğunda Elbistan **M 7,5** (38,11°K, 37,24°D) olarak kayıtlı; pencere 84 km değil **81,6 km**. Göksun bu konuma 67 km uzaklıkta. Pazarcık M 7,8 (37,17°K, 37,08°D), daire merkezine 107 km.

## Sonuçlar (M ≥ 3,0, Mc = 3,0)
| | A bağlamsız | B bağlamlı | G altın standart |
|---|---|---|---|
| Ana şok N | 136 | 129 | 128 |
| Ayıklanan (daire içi / bağlam) | 735 / 0 | 359 / 383 | 359 / 384 |
| 6–7 Şubat 2023'te kalan | 3 (03:52 M3,8; 11:05 M4,8; 12:02 M6,0) | 1 (11:05 M4,8) | 1 (11:05 M4,8) |
| 2023'te kalan | 10 | 14 | 14 |
| G ile uyum (ortak / fazla / eksik) | 117 / 19 / 11 | 128 / 1 / 0 | — |
| b (Aki + Utsu) | 0,750 ± 0,064 | 0,735 ± 0,065 | 0,730 ± 0,065 |
| λ(M ≥ 3) /yıl | 9,28 | 8,80 | 8,74 |
| N5 (G–R) /yıl | 0,294 | 0,299 | 0,302 |
| M ≥ 5 gözlenen | 2 (0,137/yıl) | 1 (0,068/yıl) | 1 (0,068/yıl) |

En büyük bağlam katkısı (B): Elbistan M 7,5 → 272 olay; Pazarcık M 7,8 → 101 olay; 2022-10-11 M 5,0 (51 km) → 4; 2019-02-02 M 4,5 → 2.

### Duyarlılık
- Tampon 60 / 90 / 120 km: B sonucu değişmiyor (N = 129).
- Bağlam M ≥ 3,0: B = G birebir (128, fark 0). M ≥ 4,0: 1 fark. M ≥ 5,0: 4 fark.
- Erişim filtresi (B2): 306 → 95 bağlam olayı; sonuç B ile aynı.
- Mc 3,2: A b = 0,768 ± 0,077 → G 0,730 ± 0,076; Mc 3,5: A 0,814 ± 0,104.

## Değerlendirme
1. **6 Şubat kümesi ayıklanıyor mu? — Kısmen.** Bağlam, sözde ana şokları ayıklıyor: 12:02 M 6,0 (Göksun; Elbistan'a 68 km) ve 03:52 M 3,8 (Pazarcık'a 74 km). Ancak 11:05 M 4,8 (Elbistan episantrına 86 km > 81,6 km) altın standartta da kalıyor. 6 Şubat 2023 – Eylül 2025 arasında G'de kalan 30 olayın yaklaşık 16'sı Göksun'a 16–26 km, Elbistan episantrına 82–93 km uzaklıkta; yani pencere sınırının hemen dışında, kırığın batı ucunda. Neden: GK74 uzaklığı **episantrdan** ölçer; Elbistan kırığı Göksun'a kadar uzandığı için kırığın ucundaki artçılar pencere dışında kalıyor. Bağlam **gerekli ama yeterli değil**; M ≥ 7 için kırık izine uzaklık gerekir.
2. **Bağlamsız–bağlamlı fark:** 30 olay (A'da 19 fazla, 11 eksik). 19 fazla: sınır dışındaki M 4–5 olayların ve iki 6 Şubat ana şokunun artçıları (2012–2025). 11 eksik: A'da M 6,0 sözde ana şokunun 499 günlük, 53 km penceresiyle yanlışlıkla ayıklanan olaylar; bağlamlı ayıklamada M 6,0 kendisi artçı sayıldığı için pencere açmıyor ve bu olaylar geri geliyor (2023'te kalan sayı 10 → 14).
3. **Değişimler beklenen yönde mi?**
   - λ azalıyor (9,28 → 8,74/yıl) ve gözlenen M ≥ 5 oranı yarıya iniyor (M 6,0 sözde ana şoku ayıklandı): beklenen yön.
   - b hafif düşüyor (0,750 → 0,730), ancak fark 1σ'nın (≈ 0,065) çok altında. Nedeni mekanik: bağlamlı ayıklamada geri gelen 11 olayın üçü M 4,8; çıkarılan 19 olayın çoğu M 3,0–3,8. Geri gelen M 4,8'ler büyük olasılıkla kırık ucundaki artçılar olduğundan G'deki b aşağı, N5 (G–R) yukarı yanlı olabilir. Kırık izine dayalı uzaklıkla bu yanlılığın azalması beklenir.
   - Pazarcık M 7,8 penceresi (973,9 gün) Eylül 2025'e kadar dairenin güneyinde 70–80 km'deki M 3,0–3,7 olayları ayıklıyor; GK74'ün büyük depremlerde uzun zamanlarda aşırı ayıklama eğilimi burada da görülüyor.

## JS'ye taşıma önerisi (bu aşamada yapılmadı)
- Bağlam: R + 90 km, **M ≥ bölge Mc'si** (B = G için), zaman başlangıçtan 1100 gün önce. Erişim filtresi yalnızca sorguyu küçültmek için güvenli.
- Ayrı adım (önerilen 2. değişiklik): M ≥ 7 olaylar için uzaklığı kırık izinden ölçmek (kaynak: yayımlanmış yüzey kırığı izleri, ör. Softa ve ark. 2024). Tek değişiklik → test → karşılaştırma ilkesiyle ayrı prototiplenmeli.
- Posterin kendi kataloğuyla karşılaştırma için: EQ-Live'dan iki CSV dışa aktarımı (R = 50 km ham; R = 140 km, M ≥ Mc bağlam).

## Ek test: M ≥ 7 için şişirilmiş yarıçap (D + Δ), altın standart G üzerine
| Δ | Ana şok N | Ek ayıklanan | Göksun ≤ 30 km | Uzak (> 30 km) | Geri gelen |
|---|---|---|---|---|---|
| 0 (G) | 128 | — | — | — | — |
| +15 km | 114 | 19 | 14 | 5 | 5 |
| +25 km | 119 | 20 | 9 | 11 | 11 |

Sonuç: etki Δ ile tek yönlü değil (zincir etkisi); +25 km, +15 km'den daha az kırık ucu artçısı, daha çok uzak olay ayıklıyor (ör. daire merkezine 7 km'deki 2024-05-31 M 3,8; 2024-10-27 M 4,9). İzotrop şişirme kırık doğrultusundan bağımsız olarak her yöne büyüdüğü için arka plan olaylarını da siliyor. Faz 2 için kırık izine (çizgi) uzaklık tercih edilmeli; Δ gibi serbest bir parametre kullanılmamalı.

## Ek test: iki kademeli bağlam sorgusu
M < 4 olayların penceresi en fazla 30 km (D(1,5) = 14,7; D(2,0) = 17,0; D(3,0) = 22,6; D(4,0) = 30,1 km). Bu nedenle küçük olaylar yalnız sınıra yakın dar bir halkada önemlidir.
| Bağlam | Olay | N | G ile fark |
|---|---|---|---|
| Tek kademe: M ≥ 4, R + 90 km | 306 | 129 | 1 fazla |
| İki kademe: M ≥ Mc, R + 30 km + M ≥ 4, R + 90 km | 868 | 128 | **0** |
Öneri (Faz 1 JS): iki kademeli sorgu. Dar halka, düşük Mc'li EMSC kataloğunda bile 20.000 sınırının altında kalmalı; posterin kataloğuyla CSV üzerinden doğrulanmalı.

## Faz 1 — donmuş referans ve JS taşıması (2026-10-06)
**Donmuş referans:** `scripts/gk74_context.py` (select_context, decluster_with_context; kurallar dosya başında).
**Fixture'lar:** `scripts/fixtures/gk74_ctx_saimbeyli_ref_mag.json`, `..._mw.json`, `gk74_ctx_adiyaman_ref_mag.json` (katalog sha256, parametreler, A/B kimlikleri + sha256, her olay için gerekçe kaydı).
| Fixture | Hedef | Bağlam | A | B | G | B = G |
|---|---|---|---|---|---|---|
| Saimbeyli, mag | 871 | 868 | 136 | 128 | 128 | ✔ |
| Saimbeyli, mw | 871 | 868 | 124 | 118 | 118 | ✔ |
| Adıyaman 37,33/38,86 R=70, 1998–, mag | 445 | 1006 | 293 | 287 | 287 | ✔ |

**JS (index.html; yedek: index.before-gk74ctx-2026-10-06.html.bak):** `gk74Decluster(evList, ctxList)` + gerekçe kaydı (rec), `gk74SelectContext()`, `GK74_CTX`; bağlam yükleme (`ensureRegionContext`: canlı EMSC/USGS iki sorgu, Tarihsel Katalog yerel), onay kutusu, bilgi satırı, poster yöntem cümlesi, CSV'de gk74_status/by_* sütunları (yalnız GK74 açıkken). Yeni parametre/model yok.

**Doğrulama:** `python scripts/validate_gk74_parity.py --context scripts/fixtures/gk74_ctx_*_ref_*.json` → 3 fixture × 8 kontrol: BİREBİR AYNI (bağlam seçimi, A, B, gerekçe kayıtları; JS = Python = donmuş). Eski testler değişmedi: 447 → 295, 88.333 → 39.424 (mag); 447 → 290, 88.333 → 37.010 (mw); TZ=Europe/Istanbul aynı. scripts/test_*.js: 5/5 OK. index.html CRLF korundu; sha256 42827847251cb244….

**Test edilmeyen (ağ yok):** canlı bağlam sorgusu ve arayüz akışı. Elle test listesi:
1. Daire modu, EMSC, R = 50 km, Saimbeyli, 2012-01-20 → bugün; GK74 aç; kutuyu işaretle → bilgi satırında "bağlamlı", dar/geniş halka sayıları, en büyük katkı Elbistan.
2. Kutuyu kaldır → sonuç bağlamsız sayıya döner.
3. Dikdörtgen/poligon ya da AFAD → kutu soluk/devre dışı, açıklama satırı.
4. CSV dışa aktar → gk74_* sütunları; 2023-02-06 12:02 M6,0 satırı: suppressed, by = Elbistan, by_role = context.
5. Yeni sorgu → bağlam kendiliğinden yeniden yüklenir.

## Dondurma beyanı ve çok bölgeli test (2026-10-06)
- `GK74_VERSION = 'gk74-ctx-frozen-2026-10-06'` (index.html + gk74_context.py; doğrulayıcı eşitliği denetler).
- Fixture'lar artık kendi alt kataloglarını taşıyor (d ≤ R + 90 km, tüm zamanlar); `eq_historical.json` yeniden üretilse de geçerli. A/B özet değerleri öncekiyle aynı.
- Mutasyon testi: `narrowKm` 30 → 29 ve `B.m < A.m` → `<=` değişiklikleri doğrulayıcıda FARK olarak yakalandı.
- CI: `.github/workflows/gk74-parity.yml` (index.html / GK74 betikleri / fixture değişince).

| Fixture | Hedef | Bağlam | A | B = G | Ayıklama A → B | Bağlamın payı | En büyük katkı |
|---|---|---|---|---|---|---|---|
| Saimbeyli (mag) | 871 | 868 | 136 | 128 | 0,844 → 0,853 | 0,52 | Elbistan M7,5 → 272 |
| Adıyaman R=70 | 445 | 1006 | 293 | 287 | 0,342 → 0,355 | 0,04 | M4,6 / M3,3 → 2 |
| İzmit-doğu (40,80/30,60) | 824 | 551 | 194 | 177 | 0,765 → 0,785 | 0,45 | 1999 İzmit **mb 6,3** → 231 |
| Van-batı (38,75/42,80) | 1266 | 1901 | 240 | 187 | 0,810 → 0,852 | 0,95 | 2011 Van Ms 7,3 → 986 |

**Faz 2 için kritik bulgu:** `eq_historical.json`'da 1999 İzmit (Mw 7,4) **mb 6,3**, Düzce (Mw 7,2) **mb 6,0** olarak kayıtlı (mb doyması; `mw` alanı boş ya da mb dönüşümü). Pencereler gerçek Mw'den küçük (M6,3: 57,9 km ve 726 gün yerine M7,4: 79,3 km ve 946 gün), ve "M ≥ 7" anahtarı bu depremlerde hiç tetiklenmez. Faz 2, büyük depremler için seçilmiş bir Mw tablosuna (ör. GCMT/USGS Mww) dayanmalı.

## Büyüklük doyması — katalog kontrolü (2026-10-06)
- 1998+ M ≥ 6,0 olay: 41 (30 mw, 1 Ms, 10 mb). mb olanların 4'ü dönüştürülmemiş (`unconverted_mb`: Scordilis 2006 mb dönüşümü yalnız 3,5 ≤ mb ≤ 6,2 aralığında, `fetch_combined_catalog.py` satır 57): 1999 İzmit mb 6,3; 2006 Güney Yunanistan mb 6,5; 2008 Onikiadalar mb 6,4; 2018 İran–Irak mb 6,3.
- Dönüştürülenler doymayı gidermiyor: 1999 Düzce mb 6,0 → Scordilis Mw 6,13 (gerçek Mw ≈ 7,2).
- Sonuç: "Mw varsa Mw, yoksa kalibre mb" kuralı zaten katalogda var (`mw` alanı, `e.mw ?? e.mag`) ve büyük depremlerde çalışmıyor; mb doyduğu için hiçbir mb→Mw kalibrasyonu bilgiyi geri getiremez. Faz 2a: büyük depremler için otoriter Mw (GCMT / USGS Mww) geçersiz kılma tablosu; kaynak ve tarih alanlarıyla.

## Faz 2a prototipi — otoriter Mw tablosu (2026-10-06; index.html'e TAŞINMADI)
- Tablo: `data/mw_authority.json` (schema mw_authority/1, sürüm mwauth-2026-10-06): 9 doğrulanmış kayıt (A: İzmit, Düzce, Van, Pazarcık, Elbistan; B: Samos, Halabja 2017, Kythira 2006, Sarpol-e Zahab 2018) + 1 doğrulanmamış (Onikiadalar 2008; USGS olay kimliği bulunamadı, kullanılmıyor). Değer kuralı: USGS ComCat tercihli büyüklüğü; alternatifler (Duputel W-fazı, Mwb, Mwc) ayrıca kayıtlı. Erişim 2026-10-06, USGS detay GeoJSON.
- Modül: `scripts/mw_authority.py` (eşleşme: kaynak kimliği, yoksa |dt| ≤ 60 s ve ≤ 50 km, en küçük |dt|; her kayıt en çok bir olaya). `gk74_context.py`'ye isteğe bağlı `mag_fn` parametresi eklendi; verilmezse Faz 1 davranışı (doğrulayıcı: 5 fixture BİREBİR AYNI).
- Karşılaştırma: `scripts/gk74_mwauth_prototype.py` → `analysis/2026-10-06_gk74_mwauth_prototip.json`.

Eşleşme (9/9; |dt| ≤ 1,9 s, uzaklık ≤ 18,4 km):
| Deprem | Katalog | Otoriter | Pencere (km / gün) |
|---|---|---|---|
| 1999 İzmit | mb 6,3 | Mwc 7,6 | 57,9/726 → 83,9/960 |
| 1999 Düzce | mb 6,0 | Mwc 7,2 | 53,2/499 → 74,9/932 |
| 2011 Van | Ms 7,3 | Mww 7,1 | 77,0/939 → 72,8/925 (küçülüyor) |
| 2006 Kythira | mb 6,5 | Mwb 6,7 | 61,3/885 → 64,9/898 |
| Pazarcık, Elbistan, Samos, Halabja, Sarpol-e Zahab | aynı | aynı | değişmez |

| Bölge | Faz 1 B (= G) | Faz 2a B (= G) | Ek ayıklanan / geri gelen | b (M ≥ 3) | λ /yıl |
|---|---|---|---|---|---|
| Saimbeyli | 128 | 128 | 0 / 0 | 0,730 → 0,730 | 8,74 → 8,74 |
| Adıyaman | 287 | 287 | 0 / 0 | değişmez | değişmez |
| İzmit-doğu | 177 | 152 | 28 / 3 | 1,206 → 1,168 (σ ≈ 0,09) | 6,17 → 5,30 |
| Van-batı | 187 | 190 | 0 / 3 | 1,101 → 1,109 | 8,62 → 8,76 |

Sonuç: B = G Faz 2a'da da her bölgede geçerli (bağlam tasarımı otoriter Mw ile de tam). Etki yalnız doymuş/farklı ölçekli büyük depremlerin yakınında; Saimbeyli değişmiyor (Pazarcık/Elbistan zaten Mw). Van örneği, düzeltmenin iki yönlü olduğunu gösteriyor (Ms 7,3 > Mw 7,1 → pencere küçülür).

## Faz 2a dondurma (2026-10-06)
- `scripts/gk74_mwauth.py` (GK74_MWAUTH_VERSION = gk74-ctx-mwauth-2026-10-06); fixture'lar `scripts/fixtures/gk74_mwauth_*_ref_mag.json` (4 bölge; B = G hepsinde): Saimbeyli 128, Adıyaman 287, İzmit-doğu 152, Van-batı 190.
- Eşleşme kapsamı tanımlandı: bağlam seçiminde aday havuzu, ayıklamada hedef + bağlam birleşimi.
- Doğrulayıcı `--mwauth`: sürüm, alt katalog ve tablo sha256'sı, geçersiz kılınan olaylar, B kimlikleri ve gerekçe kayıtları donmuş referansla aynı. JS == Python: Faz 2a JS'ye taşınmadığı için yok.
- Faz 1 fixture'ları ve eski testler değişmedi.

## Faz 2a JS portu (2026-10-06)
- Yedek: `index.before-gk74mwauth-2026-10-06.html.bak`. Eklenenler: `GK74_MWAUTH_VERSION`, `gk74BuildMwOverride()` (mw_authority.build_override ile birebir), `gk74SelectContext(…, mwEntries)` (eşleşme kapsamı: aday havuzu), `gk74Decluster(…, mwEntries)` (kapsam: hedef + bağlam), tablo yükleme (`loadMwAuth`), "Büyük depremlerde otoriter Mw (Faz 2a)" kutusu (varsayılan kapalı), bilgi satırında geçersiz kılınan depremler, poster yöntem cümlesi ve CSV başlığında sürüm. Bağlam havuzu saklanıyor; Faz 1 / Faz 2a bağlam listeleri ayrı önbellekte.
- Doğrulama: `--mwauth` 4 fixture × 13 kontrol BİREBİR AYNI (bağlam seçimi, geçersiz kılınan olaylar, B, gerekçe kayıtları, bağlamsız + otorite A). Faz 1: 5 fixture ve eski testler değişmedi; test_*.js 5/5 (test_fit_range 37, test_gr_consistency 99, test_weichert_chain 27 PASS).
- Mutasyon: `dtS = 60 → 1` ve pencerede otoriteyi yok sayma → FARK yakalandı.
- Elle test (ağ yok, denenmedi): Tarihsel Katalog, İzmit-doğu dairesi, GK74 + bağlam + otorite → bilgi satırında "1999 İzmit 6,3 mb → Mw 7,6"; Saimbeyli'de sonuç değişmemeli.

## Kapanış (2026-10-06)
Çalışma burada durduruldu. Faz 1 (bağlamlı GK74) ve Faz 2a (otoriter Mw) dondurulmuş, Python = JS doğrulanmış; Faz 2a arayüzde varsayılan kapalı. Faz 2b (kırık izine uzaklık + D(M) yeniden kalibrasyonu) ERTELENDİ; yeniden ele alınırsa başlangıç noktası: faylanma türüne göre tek geometri (2023: USGS veri sürümü 10.5066/P985I7U2; 1999: SURE 2.0, Zenodo 10.5281/zenodo.7020265; Van: USGS FFM), geometrisi olmayan deprem episantrla, kaynak seçimi duyarlılık testiyle.
