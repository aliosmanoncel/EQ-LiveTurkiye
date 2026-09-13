# AFAD Katalog Entegrasyonu — Phase 1 Gereksinimleri

**Oluşturulma:** 2026-09-13
**Durum:** ❌ HENÜZ BAŞLAMADI — yalnızca bulgu/gereksinim kaydı, kod/commit yok
**Karar:** AFAD'ı üretim butonu (örn. "AFAD 2000–2026") olarak eklemeden önce bu doküman tamamlanmalı

---

## Neden bu doküman var

AFAD'ı üçüncü bir tek-kaynaklı tarihsel katalog butonu (bkz. `EMSC 1998–2026`, `ISC 1900–1970`, `ISC 1971–1997`, `EPICA 1003–1899`, `SHARE-CET 1003–1899`) olarak eklemek gerçek veriyle test edildi (2026-09-13). Sonuç: **AFAD gerçekten değerli, redundant değil** — ama "2000–2026" gibi bir kapsam etiketini veri kanıtı olmadan koda koymamak için bu doküman önce tamamlanmalı.

**Prensip (bu projenin tüm oturum boyunca sürdürdüğü disiplin):** kaynağı olduğu gibi etiketle, kanıtsız kapsam iddia etme.

---

## Test metodolojisi (tamamlandı)

26 yıllık (2000-2026) tam tarama yerine, iki fazlı örneklem kullanıldı:

| Faz | Pencere | Amaç |
|---|---|---|
| 1 — Sakin dönem | 2024-10 (tam ay) | Rutin sismisitede AFAD/EMSC ilişkisi |
| 2 — Yoğun dönem | 2023-02-06 – 2023-02-12 (Kahramanmaraş haftası) | Kriz/artçı sekansında ilişki değişiyor mu |

Her ikisinde de aynı Türkiye bbox (34–43°K, 25–46°D) için AFAD (`apiv2/event/filter`) ve EMSC (`fdsnws/event/1/query`) çekildi, zaman (±30sn) + konum (±50km) toleransıyla eşleştirildi.

---

## Üç kritik sonuç

### 1. AFAD API'si geniş pencerelerde güvenilmez

Geniş tarih aralığı (örn. tam ay) istendiğinde **sessizce eski kayıtları düşürüyor** — hata vermiyor, sayfalama parametresi/`X-Total-Count` header'ı yok. 4 farklı pencere boyutuyla (15/20/25/31 gün) doğrulandı: hepsi aynı sabit noktada kesiliyor (`2024-10-11T17:05:22` — istenen bitiş tarihinden bağımsız).

**Gereksinim:** ≤1 günlük parçalı çekim + `eventID` ile tekilleştirme + çakışan pencerelerle çapraz doğrulama. 26 yıl için bu ~9500 parçalı isteğe kadar çıkabilir.

### 2. AFAD redundant değil — ölçülmüş katkı

| | AFAD toplam | EMSC toplam | Ortak | Yalnız AFAD | Yalnız EMSC |
|---|---:|---:|---:|---:|---:|
| Ekim 2024 (sakin) | 2.583 | 2.260 | 2.127 | 456 (%18) | 133 |
| Kahramanmaraş haftası (yoğun) | 4.324 | 1.959 | 1.466 | **2.858 (%66)** | 493 |

Eşleşen çiftlerde ortalama fark — sakin: zaman 0,3sn / konum 1,9km / derinlik 0,84km / mag 0,06. Yoğun dönemde belirgin kötüleşiyor: zaman 1,7sn / konum 8,9km / derinlik 4,2km / mag 0,18.

**Sonuç:** AFAD'ın en değerli kullanım alanı **kriz/artçı-sekans dönemleri**, rutin izleme değil.

### 3. "AFAD 2000–2026" henüz kanıtlanmış bir katalog kapsamı değil

AFAD'ın kendi resmi istatistik grafiği (deprem.afad.gov.tr/event-statistics) 2000'den başlıyor gösteriyor — ama bu, EQ-LiveTurkiye'nin 2000-2026 arasını **eksiksiz** sunabileceği anlamına gelmiyor (madde 1'deki güvenilirlik sorunu nedeniyle). 2000-2003 ayrıca çok seyrek (ağ henüz yaygınlaşmamış).

---

## Ek bulgular

- EMSC'nin FDSN text formatındaki **"Contributor"** alanı doğrudan kaynağı gösteriyor: Ekim 2024 Türkiye verisinin **%72,6'sı "AFAD"**, %7,7'si "KOERI" etiketli. EMSC'nin Türkiye kapsamı büyük ölçüde zaten AFAD/KOERI'nin kendi pick'lerinin aktarımı.
- KOERI'nin EIDA FDSN node'unda (`eida.koeri.boun.edu.tr`) **event servisi yok**, sadece `dataselect`+`station` var — `scripts/eq_fetch_turkey.py`'deki `'koeri'` kaynak seçeneği (satır 24: `'koeri': 'http://eida.koeri.boun.edu.tr/fdsnws/event/1/query'`) bu yüzden **çalışmıyor**, muhtemelen hiç uçtan uca test edilmeden yazılmış.
- KOERI'nin kendi FDSN StationXML metadata'sı ağ kuruluş tarihini resmi olarak **1971-01-01** veriyor (`Network code="KO"`) — bu tarih zaten `ISC 1900–1970` / `ISC 1971–1997` buton sınırı olarak kullanılıyor, bağımsız doğrulama sağlıyor.

---

## Sonraki aşama — Phase 1 iş listesi

- [ ] Günlük/parçalı API collector (AFAD sunucusuna saygılı rate-limit ile)
- [ ] Overlap + deduplication (`eventID` bazlı)
- [ ] Ham AFAD verisini değiştirmeden saklama (provenance)
- [ ] `src:"AFAD"` kaynak etiketi (mevcut `data/eq_historical.json` şemasındaki `src` alan mimarisiyle tutarlı)
- [ ] API çekim tarihleri ve sorgu pencerelerinin provenance kaydı (hangi gün/pencere ne zaman çekildi)
- [ ] EMSC ile otomatik eşleştirme + zaman/konum/derinlik/Mw fark raporlaması
- [ ] Eksik pencere tespit mekanizması (hangi günler henüz çekilmedi/doğrulanmadı)
- [ ] **Ancak bunlardan SONRA:** AFAD'ın gerçekte hangi başlangıç tarihinden itibaren güvenilir sunulabileceği kararı — varsayım değil, veriyle doğrulanmış bir tarih

**Bu doküman güncel kalmalı** — AFAD entegrasyonuna dönüldüğünde başlangıç noktası burasıdır. Özellikle API'nin sessiz veri kesme davranışını zamanla değişebileceği için yeniden test etmeden varsaymayın.
