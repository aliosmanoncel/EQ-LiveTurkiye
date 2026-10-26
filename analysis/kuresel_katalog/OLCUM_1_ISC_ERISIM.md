# Küresel katalog — Ölçüm 1: ISC canlı sorgu servisine tarayıcıdan erişim (2026-10-26)

**Kapsam:** Yalnız ölçüm. Kod, tarihsel katalog ve arayüz değişmedi.
**Soru:** ISC FDSN event servisi, EQ-Live'ın tarayıcıda çalışan kodu tarafından canlı veri kaynağı olarak doğrudan sorgulanabilir mi?

## Yöntem

- **Ortam:** Kullanıcının Chrome'u (Türkiye'den); istekler canlı sitenin kendi adresinden (`https://aliosmanoncel.github.io`) gönderildi, böylece uygulamanın kullanacağı kimlik (Origin) sınandı.
- **Sorgu:** Türkiye kutusu dışında, Japonya kutusu (30–46°K, 129–146°D), M ≥ 4,5; 1975 yılı (EMSC öncesi) ve 2010 yılı.
- **Uç noktalar:**
  - ISC: `https://www.isc.ac.uk/fdsnws/event/1/query` (QuakeML ve `format=text`)
  - IRIS üzerindeki ISC yansısı (bellekten yazılan adres)
  - USGS ve EMSC (karşılaştırma)
- **CORS ile ağ hatasını ayırmak için:**
  1. Normal `fetch` (CORS kipi).
  2. Başarısız olursa aynı isteği `no-cors` kipinde.
  3. Doğrudan sayfa olarak açma (üst düzey gezinti; CORS'a tabi değil).
  4. Chrome ağ kaydıyla HTTP durum kodu.
- **Belge:** Sunucu tarafı denetim bu oturumun ortamından yapılamadı (ağ izin listesi). Bunun yerine ISC belgesi okundu ([help.php](https://isc.ac.uk/fdsnws/event/1/help.php)).

## Sonuçlar

| # | Deneme | Sonuç |
|---|---|---|
| 1 | ISC, CORS `fetch`, QuakeML, JP 1975 | Başarısız ("Failed to fetch"); `no-cors`: opak yanıt geldi |
| 2 | ISC, CORS `fetch`, `format=text`, JP 1975 | Başarısız; `no-cors`: opak yanıt geldi |
| 3 | ISC sorgusu, doğrudan sayfa olarak | **HTTP 429** (Çok Fazla İstek) |
| 4 | Aynı sorgu, 3 dakika bekledikten sonra, doğrudan sayfa | **HTTP 200**, QuakeML, 176 olay, 1,30 MB, 2,99 s |
| 5 | ISC, CORS `fetch`, JP Ocak 1975 (canlı site adresinden) | Başarısız ("Failed to fetch") |
| 6 | Aynısı, 90 s sonra, ağ kaydı açık | Başarısız; ağ kaydında **HTTP 503** (Servis Kullanılamıyor) |
| 7 | IRIS ISC yansısı (`isc-mirror.iris.washington.edu`) | DNS'te yok (`NXDOMAIN`) |

**4 numaralı başarılı yanıtın içeriği** (ISC Bulletin, JP 1975, M ≥ 4,5):
- 176 olay; hepsinde koordinat ve derinlik var.
- İlk olay 1975-01-07T08:07:22, son olay 1975-12-31T14:12:37.
- Büyüklük türleri: mb 173, MS 18, M 3.
- Büyüklüğü veren ajans: ISC 191, JMA 3.
- Olay başına yaklaşık 7,4 kB (QuakeML).

**Notlar:**
- 1 ve 2'deki "opak yanıt" sunucunun bir şey döndürdüğünü gösterir, ama içeriği görülemez. 3'teki 429 ışığında bu yanıtlar büyük olasılıkla hata yanıtlarıydı; veri döndüğünün kanıtı değildir.
- CORS'un başarılı yanıtlarda izinli olup olmadığı **belirlenemedi**: tarayıcıdan gönderilen bütün ISC istekleri ya hata durumu (429/503) ya da okunamayan yanıt aldı, ve hata yanıtları CORS başlığı taşımaz.
- 7: Adres kendi bilgimden yazıldı; "yansı yok" değil, yalnız "bu adres çözülmüyor" sonucu çıkar.
- ISC belgesi (help.php):
  - "IP adresi başına aynı anda yalnızca bir sorgu çalışabilir"; bu kısıtın kullanıma göre gözden geçirileceği belirtiliyor.
  - Yanıt 40 000 olayla sınırlı.
  - Tek katalog seçeneği ISC Bulletin.
  - Varsayılan biçim QuakeML; ISF de var.
  - CORS ve 429/503 hakkında bilgi yok.

**Aynı sorgu, karşılaştırma** (JP, M ≥ 4,5; tarayıcıdan, canlı site adresinden; USGS ve EMSC CORS'a açık):

| Dönem | ISC | USGS | EMSC |
|---|---|---|---|
| 1975 | 176 (mb 173, MS 18, M 3) | 160 (mb 153, ms 6, mw 1) | 0 (HTTP 204) |
| 2010 | ölçülemedi (hız sınırı) | 118 (mwr 61, mwc 30, mb 17, mwb 10) | 164 (mb 156, mw 8) |

1975'te ISC ile USGS'nin ilk ve son olayları 2 saniye içinde aynı. Bu, iki kataloğun büyük ölçüde örtüştüğünü düşündürür, ama örtüşme oranı ölçülmedi.

Önceki ölçümden (2026-10-25, USGS/EMSC, M ≥ 3, yarım kaldı): EMSC hiçbir bölgede 1998 öncesi olay döndürmüyor.

## Karar: **B — Kısıtlı erişim**

ISC servisi çalışıyor ve geçerli, eksiksiz QuakeML döndürüyor (4). Ancak EQ-Live'ın tarayıcıdaki kodundan canlı kaynak olarak kullanmaya uygun değil:

1. Tarayıcıdan gönderilen dört ISC isteğinin hiçbiri okunabilir yanıt alamadı; ölçülebilen durum kodları 429 ve 503.
2. ISC kuralı gereği aynı IP'den aynı anda tek sorgu çalışabiliyor. EQ-Live parçalı sorgular, bağlam sorguları ve birden çok kullanıcıyla bu kurala sürekli takılır. Aynı kurumun ağındaki kullanıcılar da birbirini engeller.
3. CORS izni belgelenmemiş ve doğrulanamadı.
4. QuakeML büyük: olay başına yaklaşık 7,4 kB.

Bu ölçümün kendisi de sınıra takıldı: yaklaşık altı istekte 429 ve 503 alındı. Bu, canlı kullanımda karşılaşılacak durumun doğrudan bir örneği.

## Öneri (bir sonraki adım için; uygulanmadı)

ISC, Türkiye dosyasında olduğu gibi **sunucu tarafında, önceden çekilmiş statik dosyalar** yoluyla kullanılmalı.

- `scripts/fetch_combined_catalog.py` bunu zaten yapıyor: sıralı sorgular, aralarında 1,5 s bekleme, `format=text`, parça parça çekme.
- Küresel kullanım için iki seçenek var:
  - (a) Seçilen bölgeler için bu betiğin genelleştirilmesi.
  - (b) Bölge bölge önceden üretilmiş dosyalar.
- Bu tasarım kararı Ölçüm 2'den sonra verilmeli. Ölçüm 2'de dönemlere göre ISC–USGS örtüşmesi, ortak eşiklerde olay sayıları, büyüklük ölçekleri ve aynı depremin iki kez sayılması sunucu tarafında ölçülecek.
- Ölçüm 2'nin yapılabilmesi için ISC'ye erişebilen bir ortam gerekiyor: kullanıcının bilgisayarı ya da GitHub Actions. Bu oturumun bulut ortamı ve masaüstü kabuğu ISC, USGS ve EMSC'ye erişemiyor.
