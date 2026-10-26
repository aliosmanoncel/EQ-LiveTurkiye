# Arayüz hazırlığı: küresel ISC-GEM v12.1 penceresi (2026-10-26)

**Durum:** Yalnız `kuresel-katalog-olcum` dalında. `main` dalına birleştirilmedi, canlıya alınmadı. Bu adımlar ayrı bir karar gerektirir.
**Kapsam ilkesi:** ISC-GEM v12.1, 1904–2021 dönemindeki **küresel büyük depremlerin** kataloğudur. Tüm büyüklükleri içeren tam bir küresel katalog değildir. Bu ifade arayüzde, düğmenin açıklamasında ve seçildiğinde ipucu satırında yer alır.

## 1. Değişiklikler
- **Veri:**
  - `analysis/kuresel_katalog/uretim/iscgem_global.json` → `data/iscgem_global.json` (git mv).
  - Lisans dosyası → `data/LISANS_ISC-GEM_kuresel.txt`. Mevcut `data/LISANS_ISC-GEM.txt` değişmedi; o dosya Türkiye katmanının iki dosyası içindir.
  - Olay içeriği birebir aynı. Meta alanında yalnız `lisans_dosyasi` yolu değişti.
  - Yeni SHA-256: `f35e29fada433486d09fde9e3000c0d1a00bc24c99b87faa8d6fa77f49c8f87c`.
  - Boyut: 8 317 700 bayt; gzip ile 1 915 301 bayt (GitHub Pages sıkıştırarak sunar).
  - Bütünlük: `iscgem_global_uret.py dogrula` 26/26 geçti. Yeniden üretim bayt bayt aynı.
- **Üretici ve iş akışı:**
  - `iscgem_global_uret.py` çıktısını `data/`'ya yazıyor.
  - `kuresel-asama2.yml` `data/` yolunu denetliyor.
  - `duyarlilik_1980/b_vekil_1980.js` yeni yolu okuyor.
- **`index.html`** (yalnız ekleme; mevcut satırlarda değişiklik yok, `rebuildHistoricalView` içindeki yeniden düzenleme hariç):
  1. **Düğme:** "Tarihsel (küresel): ISC-GEM 1904–2021 (deneysel)", `global-only` sınıfıyla. Yalnız Global ve EMSC modlarında görünür ve varsayılan olarak kapalıdır. Açıklama metni kapsamı, seçim eşiklerini, vekil/doğrudan ayrımını, dahil olmayan kaynakları (ek katalog, USGS) ve lisansı belirtir.
  2. **Yükleyici:** `loadIscgemGlobal()` / `iscgemGlobalEvents()`. Dosya yalnız düğmeye basılınca bir kez indirilir; şema denetlenir (`eq-live/kuresel-katalog/1`).
     - Olaylar: `mtype: 'mw'`; Magnitude Conversion seçicisi bağıntı uygulamaz.
     - `msrc: iscgem_direct | iscgem_proxy`; `mw_m0: gcmt | bibliog | null`; `mw_q`, `mw_unc`.
     - Yer adı: ISC-GEM'de yer adı yoktur. Etiket koordinat ve kimlikten oluşur (ör. "38,14°G 73,41°B · ISC-GEM 879136"). Boş bırakılırsa arayüzün yedek etiketleri ("Türkiye", "EMSC Region") yanlış yer gösteriyordu; kabul testinde yakalandı.
  3. **`rebuildHistoricalView`:**
     - Pencereler Türkiye pencereleri ve küresel pencere olarak ayrılır.
     - Yalnız küresel pencere seçiliyse `eq_historical.json` (14 MB) indirilmez.
     - Türkiye yolu korunur. Testin denetlediği satır (`const cat = iscgemWanted() ? …`) aynen yerinde.
     - İpucu satırı: olay sayısı, doğrudan/vekil/belirsiz sayı ve oranları, kapsam uyarısı, vekil Mw açıklaması, lisans ve atıf.
  4. **`setScope('tr')`:** Küresel pencere seçiliyse kapatılır; Türkiye modunda gizli bir pencere açık kalmaz. Seçili değilse hiçbir şey yapmaz.

## 2. Testler
**Birim testleri** (`scripts/test_*.js`, değişiklik sonrası):
- 13 dosya geçti. `test_iscgem_overlay.js` 37/37 geçti; Türkiye ISC-GEM katmanının kapalıyken aynı nesneyi kullandığı denetimi bu dosyada.
- `test_fit_range.js` değişiklikten **önce de** çalışmıyordu. Bu dalda bulunmayan `csBvalueTimeSeries` fonksiyonunu arıyor; bu değişiklikle ilgisi yok.

**Tarayıcı kabul testi** (`kabul/kabul_iscgem_global.js`, Playwright/Chromium; sonuç `kabul/kabul_sonuc.json`): **21/21 geçti.**
- **Yöntem:** Aynı tıklama dizisi değişiklik öncesi `index.html` kopyasında ve güncel sayfada çalıştırıldı.
- **Dış istekler:** Karo, canlı API ve WebSocket istekleri engellendi. Leaflet 1.9.4 ve leaflet.heat 0.2.0 aynı sürümlerin yerel kopyasından verildi.

| Denetim | Sonuç |
|---|---|
| EMSC 1998–2026 | Önce = sonra: N 80 929, olay özeti, durum ve ipucu metni, Mc 3,2, b 1,0212 |
| ISC 1900–1970 | Önce = sonra: N 662, Mc 4,7, b 0,5260 |
| ISC 1971–1997 | Önce = sonra: N 6 742, Mc 3,7, b 0,7176 |
| EPICA 1003–1899 | Önce = sonra: N 3 553, Mc 5,3, b 0,5534 |
| SHARE-CET 1003–1899 | Önce = sonra: N 165, Mc 6,4, b 0,7886 |
| TR ISC-GEM katmanı açık + ISC 1900–1970 | Önce = sonra: N 935, b 0,9084 |
| Çoklu seçim (ISC 1900–1970 + 1971–1997) | Önce = sonra: N 7 404 |
| Yeni satır | Türkiye modunda gizli, Global modda görünür, varsayılan kapalı; açılışta `iscgem_global.json` indirilmiyor |
| Küresel pencere | 74 159 olay; doğrudan 51 227 (%69), vekil 22 931 (%31), belirsiz 1; tür yalnız `mw`; 1904-04-04 – 2021-12-31 |
| İpucu ve durum | Kapsam uyarısı, oran, lisans ve atıf mevcut; "74159 deprem · Tarihsel katalog (ISC-GEM) · 1904–2021" |
| Yer etiketi | Boş 0, "Türkiye" 0; en büyük deprem kartı "38,14°G 73,41°B · ISC-GEM 879136" (1960 Şili, Mw 9,55) |
| Türkiye moduna dönüş | Küresel pencere kapandı, olaylar temizlendi |
| Sayfa hataları | Önce 0, sonra 0 |

**Testin kapsamadığı:** Canlı veri akışı (EMSC/USGS) ve harita karoları; ağ engelli olduğu için sınanmadı. Değişiklik bu yollara dokunmuyor.

## 3. Bilinen sınırlar ve mevcut sorunlar (bu değişiklikle gelmedi; düzeltilmedi)
- **Global moddaki analizler:** Global modda tehlike/risk/b-değeri **haritaları** yoktur (mevcut not). Zaman–büyüklük grafiği, Mc ve b özetleri yüklü olaylar üzerinden çalışır. Varsayılan b-değeri kümesi tüm ISC-GEM Mw'dir (yöntem kararı, `duyarlilik_1980/RAPOR.md`). "Yalnız doğrudan Mw" seçeneği bu hazırlıkta **eklenmedi**.
- **Mevcut hata:** Canlı zaman düğmesine (ör. "1 Ay") basılınca tarihsel düğmelerin vurgusu kalkıyor, ama `activeHistWindows` listesi temizlenmiyor. Sonra bir tarihsel pencere seçilirse, vurgusu kalkmış eski pencereler de birleşime giriyor. Türkiye pencerelerinde de aynı. Ayrı bir düzeltme olarak önerilir.
- **USGS ek katmanı:** Bu hazırlıkta yok (`USGS_KATMANI_TASARIM.md`).

## 4. Birleştirme ve yayın öncesi karar gerekenler
- Bu hâliyle `main`'e birleştirilsin mi? Birleştirme GitHub Pages ile canlıya çıkar ve `data/iscgem_global.json` (8,3 MB) depoya ve sitenin dosyalarına girer.
- Yukarıdaki mevcut hata, birleştirmeden önce mi sonra mı düzeltilsin?
