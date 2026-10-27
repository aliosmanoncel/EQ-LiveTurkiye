# Tarihsel modda analiz penceresi (T) düzeltmesi — doğrulama raporu (2026-10-27)

Dal: `tarihsel-pencere-T`, `main` 543ac56'dan açıldı. Henüz `main`'e birleştirilmedi.

## 1. Hata

Tarihsel katalog modunda bölge analizi analiz penceresini yanlış yerden alıyordu. `fetchRegionEventsFromHistorical`:

```
regionWindowStart/End = historicalCache.starttime/endtime
```

Bu, kataloğun tamamıdır: 1900-01-01 → 2026-09-14. Seçili pencere ise örneğin ISC 1971–1997'dir. Olaylar doğru süzülüyordu, ama süre (T) yanlıştı.

Yanlış T şu yerlere giriyordu:
- Weichert tamlık dönemlerinin son dönem sonu (`csBuild`);
- G–R Oran/Yoğunluk modu;
- Bölge karşılaştırması (`cmpAdd` t0/t1);
- bölge bilgi satırı: Aktivite Yoğunluğu ve pencere etiketi;
- bağlamlı GK74 zaman aralığı.

**İkinci hata:** Yalnız küresel ISC-GEM penceresi seçiliyken `historicalCache` boş kalıyor. Bölge sorgusu da `dfmt(null)` hatasıyla duruyordu.

## 2. Düzeltme

Değişiklik `index.html`'de, yaklaşık 20 satır.

- `rebuildHistoricalView` seçili pencerelerin aralığını `histSelWindow` değişkeninde saklıyor: `{start, end, parts, contiguous}`.
  - Açık uçlu pencere (EMSC 1998–) şimdiki zamanda değil, katalog sonunda (`cat.endtime`) biter. Pencerede bu tarihten sonra olay varsa, son olayın zamanında biter.
  - Pencereler arasında bir günden büyük boşluk varsa `contiguous = false` olur ve durum satırında uyarı çıkar: "Seçili pencereler bitişik değil: T, aradaki boşluğu da içerir".
- `regionWindowStart/End = histSelWindow`. Seçili pencere yoksa eski davranış korunur.
- Pencere etiketinde yıl UTC ile yazılıyor. Önceden yerel saat (UTC+3) yüzünden 1997-12-31 23:59 UTC, "1998" görünüyordu.
- Hesap yöntemlerine (Aki–Utsu, Weichert, Mc, GK74) dokunulmadı. Yalnız T'nin kaynağı değişti.

## 3. Kabul testi: `kabul_pencere_T.js`, 19/19 geçti (önce = main 543ac56)

| Senaryo | Önce: pencere (T) | Sonra: pencere (T) | N |
|---|---|---|---|
| ISC 1971–1997 | 1900 → 2026-09-14 (126,7 yıl) | 1971-01-01 → 1997-12-31 (27,0 yıl) | 3328 |
| ISC 1971–1997 + EMSC 1998– | 1900 → 2026-09-14 (126,7) | 1971 → 2026-09-14 (55,7) | 51 912 |
| EMSC 1998– | 1900 → 2026-09-14 (126,7) | 1998 → 2026-09-14 (28,7) | 48 584 |
| ISC 1900–1970 + EMSC 1998– (boşluklu) | 1900 → 2026-09-14 (126,7) | aynı + "bitişik değil" uyarısı | 48 921 |
| Daire, ISC 1971–1997 | 1900 → 2026 (126,7) | 1971 → 1997 (27,0) | 506 |
| Küresel ISC-GEM 1904–2021 | **bölge sorgusu hata veriyordu** | 1904 → 2021 (118,0) | 2169 |

Kontrol listesi:

| Denetim | Sonuç |
|---|---|
| (1) Seçili aralık bütün bileşenlerde | pencere, Weichert son dönemi (1985 → 1997-12-31), karşılaştırma T = 27,0, bilgi satırı "Tarihsel Katalog (1971–1997)" |
| (2) Sınırlar | olaylar her senaryoda [başlangıç, bitiş] içinde; T(1971–1997) = 27,001 yıl; açık uçlu pencere katalog sonunda biter; bitişik pencereler tek aralık; boşlukta uyarı; ISC-GEM çalışıyor |
| (2) Olay sayıları | önce = sonra; yalnız T değişti |
| (3) Tek Mc | b, a, N(≥Mc), Mc önce = sonra (T'ye bağlı değil): b = 0,773, N = 2200 |
| (3) Weichert | aşağıdaki tablo |
| (4) Oran modu (daire) | T = 27,0 yıl (önce 126,7) |
| (4) Aktivite Yoğunluğu (daire) | 29,92 → 140,42 /10⁶ km²/yıl; oran 4,693 = T_önce/T_sonra (4,692) |
| (5) Canlı mod | `histSelWindow = null`, değişmedi |
| Sayfa hatası | 0 |

Weichert sonuçları; basamaklar 1971 M ≥ 4,5 ve 1985 M ≥ 4,0, bölge 36–42° K / 26–45° D:

| Pencere | b (önce → sonra) | λ(≥4)/yıl | λ(≥7)/yıl |
|---|---|---|---|
| ISC 1971–1997 | 0,805 → **0,947** | 25,20 → **67,25** | 0,0967 → 0,0969 |
| ISC 1971–1997 + EMSC 1998– | 1,0855 → 1,0855 | 105,11 → 105,11 | 0,0582 → 0,0582 |
| ISC 1971–1997, ilk basamak 1960 (pencere başından önce) | 0,862 → **0,947** (dönem 1960 → 1971'de kırpılıyor; 1971 basamağıyla aynı sonuç) | | |

Pencere verinin sonuna kadar uzanıyorsa (ikinci satır) tamlık dönemleri aynı kalıyor; yalnızca pencere sonu birkaç saat kayıyor. Ölçülen farklar:
- b: 1,0854657 → 1,0854634 (göreli 2e−6);
- λ(≥4): 105,1139 → 105,1116 (göreli 2e−5).

Bu kaymanın nedeni şu: pencere sonu artık katalog tarihinin 00:00'ı değil, seçili penceredeki son olayın zamanı (2026-09-14, aynı gün). Bu, o günün olaylarını da gözlem süresine katan daha doğru bir tanım.

Üçüncü satır, düzeltmenin ikinci bir etkisini gösteriyor: tamlık basamağı seçili pencereden önce başlıyorsa, eski kod pencere öncesindeki boş yılları da T'ye katıyordu. Hata yalnızca pencere katalog sonundan önce bittiğinde, ya da başlangıçtan önce boş yıllar sayıldığında sonuçları değiştiriyordu.

**Gerileme testleri:**
- Birim testleri 14/14 geçti.
- GK74 düğmesi kabul testi 16/16 geçti; daire, bağlamlı GK74 ve küresel ISC-GEM sonuçları önceki gibi.

## 4. Etki ve sınırlar

- Bu dalla birlikte tarihsel modda hesaplanan bütün yıllık oranlar ve yoğunluklar seçili pencereye göre değişir. Daha önce raporlanmış, katalog sonundan önce biten pencerelerle elde edilmiş oran/yoğunluk değerleri yeniden hesaplanmalıdır. Ham G–R, tek Mc b ve Mc etkilenmez.
- Bitişik olmayan pencerelerde T hâlâ toplam aralıktır; durum satırı bunu uyarır. Parça süreleri `histSelWindow.parts` içinde tutuluyor, ama hesaplara henüz bağlanmadı (ayrı karar).
- HK Yerel ve HK Tarihsel kataloglarında pencere seçimi yok. Bunlar katalog aralığını kullanmaya devam ediyor; değiştirilmedi.

## 5. Birleştirme öncesi son test kaydı (2026-10-27 14:20, dal ucu e98c1cf)

| Test | Sonuç |
|---|---|
| Birim testleri `scripts/test_*.js` (14 dosya; dal ucunda ayrı çalışma kopyasında) | 14/14 geçti |
| Kabul `kabul_pencere_T.js` (önce = main 543ac56) | 19/19 geçti |
| GK74 düğmesi kabul testi (gerileme) | 16/16 geçti |
| Güncel `main` ile birleştirme | çakışma yok (`git merge-tree`); `index.html` farkı 24 satır |
| Bu dalı içeren Poisson dalında (bdaa625) birim testleri | 15/15 geçti |

`main` ve canlı site değişmedi. Birleştirme ayrı onay bekliyor.
