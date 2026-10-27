# USGS ek katmanı: tasarım (uygulanmadı)

**Durum:** Yalnız tasarım. Veri üretilmedi, arayüze bağlanmadı. Kullanıcı kararı (2026-10-26): katman **varsayılan olarak kapalı**, büyüklükler **orijinal türleriyle** kalır, dönüştürme yok.
**Dayanak:** `OLCUM_2_RAPOR.md` (Ölçüm 2 sonuçları ve çift kayıt bulguları).

## 1. Amaç ve sınır
- **Amaç:** ISC-GEM ana katalogunda olmayan USGS ComCat kayıtlarını ayrı, isteğe bağlı bir kaynak olarak sunmak. 2022 ve sonrası bu kayıtlara dahildir.
- **Sınır:** Katman ana katalogun parçası değildir. Duyarlılık analizi dışında, ana katalogla birleştirilip tek bir homojen katalog gibi kullanılmaz.

## 2. Dosya ve şema
- **Dosya:** `data/usgs_ek_katman.json` (üretilirse), `data/iscgem_global.json` ile aynı şema (`eq-live/kuresel-katalog/1`, `katman: "usgs_ek"`).
- **Ortak alanlar:**
  - `id = "usgs:<ComCat id>"`
  - `M`: USGS `mag` değeri, değiştirilmeden.
  - `M_tur`: USGS `magType`, değiştirilmeden (ör. `mb`, `Ms_20`, `ml`, `mww`, `md`).
  - `Mw_yontem`: her zaman `null`. USGS Mw türleri ISC-GEM'in doğrudan/vekil ayrımına eşlenmez.
  - Kalite alanları (`M_q`, `loc_q`, `dep_q`): `null`; USGS'de karşılıkları yok.
- **Ek alanlar:**
  - `kaynak_ag` (`net`), `usgs_ids` (`ids`), `olay_turu` (`type`).
  - `zaman_katmani`: `"1904–2021 tamamlayıcı"` veya `"2022– sonrası"`.
  - `iscgem_olasi_cift`: aşağıdaki 4. kurala göre.
- **Anlık görüntü:** ComCat zamanla değişir. Üretimde sorgu zamanı, sorgu parametreleri, parça sayıları ve çıktının SHA-256'sı meta alanına yazılır.

## 3. Ayıklama kuralları (sırayla)
1. `type ≠ earthquake` olan kayıtlar çıkarılır. Ölçüm 2'de 958 kayıt; 811'i nükleer patlama.
2. `ids` alanında herhangi bir ISC-GEM **ana** katalog kimliği (`iscgem<eventid>`) bulunan kayıtlar çıkarılır. Bu kural, iki ISC-GEM olayını birleştiren 2 USGS kaydını ve kimlikli kaydı pencere dışında kalan 33 olayı da kapsar.
3. `net = iscgemsup` olan kayıtlar ve `ids` alanında yalnız ISC-GEM **ek** katalog kimliği bulunan kayıtlar çıkarılır. Ek katalog dışarıda tutulur.

## 4. Kimlik bağı olmayan ISC-GEM olayları
Ölçüm 2'de bu tür 26 olay var (2 / 8 / 16). Kalan USGS kayıtları bu olaylarla, ön kayıttaki pencerelerle (`OLCUM_2_ONKAYIT.md`) eşleştirilir:
- **`tekil` eşleşme:** USGS kaydı çıkarılır ve eşleşme listesine yazılır.
- **`karsilikli_cok_adayli` veya `belirsiz`:** Kayıt katmanda kalır, ama `iscgem_olasi_cift = true` olarak işaretlenir ve tek tek listelenir. Otomatik karar verilmez.

## 5. Kullanım kuralları (arayüze bağlanırsa)
- Varsayılan kapalı. Açıldığında analizler büyüklük türüne göre ayrılır.
- b-değeri ve Mc yalnız tek bir `M_tur` grubunda hesaplanır. Farklı türler aynı frekans–büyüklük dağılımına konmaz.
- mb/Ms → Mw dönüşümü bu katmanın parçası değildir. İleride önerilirse bağıntı, geçerlilik aralığı, belirsizlik ve kaynak ayrı bir belgede tanımlanır. Dönüştürülmüş değerler ayrı bir alanda tutulur ve doğrudan Mw ile karıştırılmaz. Bu dikkat özellikle mb doygunluğu nedeniyle gereklidir.

## 6. Açık konular
- **Lisans:** USGS ComCat verisinin dağıtım koşulları ve katkı veren ağların koşulları **doğrulanmadı**. Doğrulanmadan katman üretilip yayımlanmaz.
- **Üretim yeri:** GitHub Actions (ComCat erişimi yalnız orada var); `olcum2_usgs.py indir` modu yeniden kullanılabilir.
