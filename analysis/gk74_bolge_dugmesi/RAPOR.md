# GK74 düğmesi: Bölge Analizi dikdörtgen, poligon ve linkle açılan bölgeler (2026-10-27)

**Dal:** `gk74-bolge-dugmesi` (`main`'den). `main`'e birleştirilmedi, canlıya gönderilmedi; birleştirme kullanıcı kararına bağlı.

## Sorun
GK74 artçı ayıklama düğmesi yalnız Araştırma Bölgesi ve daire yollarında görünür yapılıyordu. Bölge Analizi'nin kendi çizim yollarında hiç görünmüyordu:
- dikdörtgen ("🔲 Bölge Seç");
- poligon;
- linkle açılan bölge (`?rminlat…`, `rpoly`, `rcirc`).

GK74 hesabı bölgenin şekline bakmaz; seçili bölgedeki olaylar (`regionEvents`) üzerinde çalışır.

## Değişiklik (yalnız görünürlük)
`index.html`'de üç satır eklendi. Her biri, mevcut daire ve Araştırma Bölgesi yollarındaki satırın aynısı (`btnRegionDecluster.style.display = ''`):
- `regionMouseUp()`: dikdörtgen tamamlanınca;
- `polygonFinish()`: poligon tamamlanınca;
- linkle bölge kurulumu: daire, poligon ve dikdörtgen dallarından sonra.

**Değişmeyenler:**
- GK74 yöntemi.
- `regionCtxSupported()`: bağlamlı GK74 yalnız dairede.
- Araştırma Bölgesi yolları; ≤ 4 köşeli çokgeni kapsayan dikdörtgenle sorgulama dahil (mevcut davranış).
- Küresel ISC-GEM penceresi.
- Seçim başlatma işlevleri zaten `regionDeselect()` çağırıyor; her yeni seçimde düğme ve GK74 durumu sıfırlanır.

## Kabul testi
`kabul_gk74_dugme.js`, Playwright; sonuç `kabul_sonuc.json`. **16/16 geçti.**
- **Yöntem:** Aynı senaryolar `main` (önce) ve dal (sonra) sayfasında çalıştırıldı.
- **Veri:** Yerel tarihsel katalog (Türkiye modu, ISC 1971–1997); ağ gerekmez.
- **Poligon:** 6 köşeli, Batı Anadolu: (38,27) (39,5,28) (40,30) (39,31,5) (37,5,30,5) (37,28,5).

| Koşul | Sonuç |
|---|---|
| (1) Düğme görünür | Bölge Analizi dikdörtgen ✔, poligon ✔, link dikdörtgen ✔, link poligon ✔, link daire ✔. Önce hepsi gizliydi. |
| (2) Aynı poligon, iki yol | Bölge Analizi 489 olay → 295 ana şok; Araştırma Bölgesi 489 → 295; link poligonu 489 → 295 |
| (3) Daire ve bağlam kısıtı | Daire önce = sonra (274 → 194 bağlamsız, 190 bağlamlı). Bağlam kutucuğu dairede etkin; dikdörtgen ve poligonda devre dışı. `regionCtxSupported()` yalnız dairede true. Dikdörtgen ve poligonda bağlam kullanılmadı. |
| Etkilenmemesi gerekenler | Araştırma Bölgesi poligonu önce = sonra; bölge sorgusu olay sayıları önce = sonra (dikdörtgen 921, poligon 489); küresel ISC-GEM penceresi önce = sonra (74 159); sayfa hatası yok |

**Test notu:** Linkle açılan bölge canlı kaynağı sorgular; test ortamında ağ kapalı. Bu yüzden link senaryolarında iki kontrol yapıldı:
- düğmenin açılışta göründüğü;
- yerel tarihsel pencere açılıp bölge sorgusu yeniden çalıştıktan sonraki davranış.

İlk denemede bağlam kutucuğu durumu bu ağ kısıtı yüzünden güncellenmemişti; kod hatası değil.

**Birim testleri** (`scripts/test_*.js`): 13 dosya geçti. `test_fit_range.js` öncekiyle aynı nedenle çalışmıyor; bu değişiklikle ilgisi yok.
**GitHub iş akışları** (0b00312): GK74 eşdeğerliği (Python = JS), b güven aralığı ve ISC-GEM katmanı geçti.

**Kapsam dışı:** Canlı EMSC/USGS sorguları ve harita karoları sınanmadı (ağ kapalı); değişiklik bu yollara dokunmuyor.
