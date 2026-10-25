# Tarayıcı denetimleri (CI dışı, elle çalıştırılır)

Başsız Chromium (Playwright) ile uygulamanın tamamı çalıştırılır; dış ağ kapalı, Leaflet yerelden verilir, saat ve `Math.random` sabitlenir.

- `birebirlik.js <port> <sorgu> <çıktı.json>`: canlı ve tarihsel katalogda Time–Mag paneli, G–R, Mc tablosu, bölge satırı, artçı dizileri ve TR poster (PNG + tuval metni). `?bci=normal` ile dal ve `main` çıktıları karşılaştırılır; 2026-10-25'te 45 öğe ve poster PNG'si bayt bayt aynıydı (fark yalnız durum nesnelerindeki `lo/hi/ciM` alanları ve Mc tablosu başlığındaki statik etiket).
- `sentetik.js <port> <sorgu> <etiket>`: YAPAY katalog (b = 1 arka plan, iki ana şok ve Omori artçıları, son bölümde b ≈ 2,6); b(t), dizi paneli, Mc tablosu ve bölge karşılaştırması; NaN/∞ ve sayfa hatası denetimi, ekran görüntüleri.

Ortam: `LB` = leaflet@1.9.4 ve leaflet.heat@0.2.0 paketlerinin açıldığı klasör (`npm pack`), `SP` = çıktı klasörü, `NODE_PATH` = Playwright'ın bulunduğu yer. Depo kökü `python3 -m http.server <port>` ile sunulur.
