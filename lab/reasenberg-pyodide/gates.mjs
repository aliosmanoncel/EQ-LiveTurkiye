// gates.mjs — Dinamik Reasenberg için UYGUNLUK KAPILARI (DENEME).
//
// Kural: her çalıştırmadan önce veri yeterliliği ve parametre koşulları denetlenir.
//   KAPALI   (OFF)     : en az bir zorunlu koşul sağlanmıyor → hesap YAPILMAZ, neden(ler) gösterilir.
//   UYARILI  (WARNING) : zorunlu koşullar sağlanıyor; yorumu sınırlayan uyarı var → hesap + uyarı.
//   UYGUN    (ELIGIBLE): yazılım bütünlüğü (öz-sınama, sha256) ve veri koşulları sağlandı.
// "UYGUN", sonucun bilimsel olarak doğrulandığı anlamına GELMEZ; yalnız denetlenen koşulların sağlandığını söyler.
// Koşul sonradan sağlanırsa (ör. sorgu sınırı artırılır) aynı denetim yeniden ON verir.
//
// Mc ayrımı: "Mc (tahmin)" veriden hesaplanan değerdir; "xmeff (seçim)" kullanıcının
// girdiği eşiktir. Seçimin tahminin üstünde olması yalnız tutarlılık denetimidir;
// Mc'nin bilimsel olarak doğrulandığı anlamına gelmez.
//
// Algoritma kodu içermez; Reasenberg hesabı rb_core.mjs → Pyodide → reasenberg.py.

export const DEFAULTS = Object.freeze({ minN: 50, maxInvalidFrac: 0.05, rfact: 10 });   // D-P4: başlangıç değerleri

const num = v => (v === null || v === undefined || v === '' || !Number.isFinite(+v)) ? null : +v;
const KM_PER_DEG = 111.195;

// Mc TAHMİNCİSİ = SİTENİN KENDİSİ (D-P1). Aşağıdaki iki fonksiyon index.html'den BİREBİR kopyadır
// (MAXC, Wiemer & Wyss 2000; +0.2 düzeltmesi, Woessner & Wiemer 2005). CI (gates.test.mjs) kopyanın
// index.html ile aynı kaldığını denetler; site değişirse test kırmızı olur.
// --- index.html kopyası başı ---
function mcSrcMag(e) { return e.mcv ? e.mag : (e.mw ?? e.mag); }
function computeMcSrc(evList) {
  const mags = evList.map(mcSrcMag).filter(m => m > 0);
  if (mags.length < 10) return null;
  const bins = {};
  mags.forEach(m => {
    const b = (Math.round(m * 10) / 10).toFixed(1);
    bins[b] = (bins[b] || 0) + 1;
  });
  let maxCount = -1, maxBin = null;
  for (const b in bins) {
    if (bins[b] > maxCount) { maxCount = bins[b]; maxBin = parseFloat(b); }
  }
  return maxBin !== null ? +(maxBin + 0.2).toFixed(1) : null;
}
// --- index.html kopyası sonu ---

// Reasenberg'in kullandığı büyüklük alanı (mag) üzerinde sitenin tahmincisi.
export function estimateMc(events) {
  const mc = computeMcSrc(events.map(e => ({ mag: num(e.mag) })).filter(e => e.mag !== null));
  return mc === null ? { mc: null, method: 'MAXC+0.2 (sitenin computeMcSrc)', reason: 'en az 10 geçerli büyüklük gerekir' }
                     : { mc, method: 'MAXC+0.2 (sitenin computeMcSrc)' };
}
export { computeMcSrc, mcSrcMag };

function epiKm(lat1, lon1, lat2, lon2) {
  const r = Math.PI / 180, dlat = (lat2 - lat1) * r, dlon = (lon2 - lon1) * r;
  const a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin(dlon / 2) ** 2;
  return 2 * 6371.0 * Math.asin(Math.sqrt(Math.min(1, a)));
}

// Reasenberg etkileşim yarıçapı (km): r(M) = 0.011·10^(0.4M); bağlantı ölçeği rfact·r.
export const interactionKm = (m, rfact = DEFAULTS.rfact) => rfact * 0.011 * 10 ** (0.4 * m);

/**
 * @param {object} p
 * @param {Array}  p.events   olaylar (id, time, lat, lon, dep, mag, mtype, src)
 * @param {boolean} p.capped  sorgu üst sınıra takıldı mı (sitede: regionCapped)
 * @param {number} p.limit    sorgu üst sınırı (bilgi)
 * @param {number} p.xmeff    kullanıcının seçtiği eşik
 * @param {object|null} p.mcEst estimateMcMaxc çıktısı
 * @param {object|null} p.region { type: 'circle', lat, lon, rKm } — sınır denetimi için
 */
export const STATE_LABEL = Object.freeze({ ELIGIBLE: 'UYGUN', WARNING: 'UYARILI', OFF: 'KAPALI' });

export function evaluateGates({ events, capped, limit, xmeff, mcEst, region = null, selfTestPassed = true, windowStart = undefined, bufferDays = 0, opts = {} }) {
  const o = { ...DEFAULTS, ...opts };
  const checks = [];
  const add = (id, label, status, detail) => checks.push({ id, label, status, detail });

  // K0 yazılım bütünlüğü: bu oturumda öz-sınama (dondurulmuş referanslarla birebir) geçti mi (D-P5)
  add('K0', 'Öz-sınama (yazılım bütünlüğü)', selfTestPassed ? 'pass' : 'fail',
    selfTestPassed ? 'Bu oturumda 4 dondurulmuş referansla birebir eşleşme sağlandı (yazılım doğruluğu; bilimsel geçerlilik değil).'
                   : 'Bu oturumda öz-sınama geçmedi ya da çalışmadı; hesap yapılmaz.');

  // K1 katalog bütünlüğü (sorgu sınırı) — 500 algoritmanın değil veri erişiminin sınırıdır
  add('K1', 'Katalog bütünlüğü (sorgu sınırı)', capped ? 'fail' : 'pass',
    capped ? `Sorgu üst sınıra takıldı (N = ${limit}); katalog kesik, kümeler bölünür. Sınırı artırın veya bölgeyi/dönemi daraltın.`
           : `Sorgu sınırın altında (N = ${events.length}${limit ? ` / ${limit}` : ''}).`);

  // K2 tek kaynak — aynı deprem iki kaynaktan gelirse sahte küme oluşur
  const srcs = [...new Set(events.map(e => e.src || '?'))];
  add('K2', 'Tek kaynak', srcs.length > 1 ? 'fail' : 'pass',
    srcs.length > 1 ? `Birden çok kaynak (${srcs.join(', ')}): yinelenen olaylar sahte küme üretir; kaynakları birleştirme/yineleme ayıklaması yok.`
                    : `Kaynak: ${srcs[0] ?? '—'}`);

  // K3 geçerli alanlar (zaman, koordinat, derinlik, büyüklük) — geçersizler kümelenmez, çıkarılmaz
  const invalid = events.filter(e => !e.time || isNaN(Date.parse(e.time)) || [e.lat, e.lon, e.dep, e.mag].some(v => num(v) === null)).length;
  const fInv = events.length ? invalid / events.length : 0;
  add('K3', 'Geçerli alanlar', fInv > o.maxInvalidFrac ? 'fail' : 'pass',
    `${invalid} geçersiz olay (%${(100 * fInv).toFixed(1)}; eşik %${100 * o.maxInvalidFrac}). Geçersizler kümelenmez ve çıkarılmaz.`);

  // K4 zaman sıralaması ve tekil kayıt. Kimlik her kaynakta yok (EMSC metin biçimi), bu yüzden yineleme
  // İÇERİKLE denetlenir: aynı zaman (ms), konum (0,001°) ve büyüklük. Sıralamayı adaptör UTC ile yapar.
  const keyOf = e => `${Date.parse(e.time)}|${(+e.lat).toFixed(3)}|${(+e.lon).toFixed(3)}|${e.mag}`;
  const dupIds = events.length - new Set(events.map(keyOf)).size;
  add('K4', 'Zaman sıralaması / tekil kayıt', dupIds ? 'fail' : 'pass',
    dupIds ? `${dupIds} yinelenen kayıt (aynı zaman, konum, büyüklük).` : 'Yinelenen kayıt yok; zaman sıralaması adaptörde UTC ile yapılır.');

  // K5 Mc: tahmin ile seçim AYRI gösterilir
  const mcTxt = mcEst && mcEst.mc !== null ? `Mc (tahmin, ${mcEst.method}) = ${mcEst.mc.toFixed(2)}` : `Mc tahmin edilemedi${mcEst?.reason ? ` — ${mcEst.reason}` : ''}`;
  let k5 = 'pass', k5d = `${mcTxt}; xmeff (seçim) = ${(+xmeff).toFixed(2)}. Seçimin tahminin üstünde olması doğrulama değildir.`;
  if (!mcEst || mcEst.mc === null) { k5 = 'fail'; k5d = `${mcTxt}. xmeff yalnız kullanıcı seçimine dayanamaz.`; }
  else if (+xmeff < mcEst.mc - 1e-9) { k5 = 'fail'; k5d = `${mcTxt}; xmeff (seçim) = ${(+xmeff).toFixed(2)} tahminin ALTINDA: eksik katalog bölümü kümelemeye girer.`; }
  add('K5', 'Mc ve xmeff', k5, k5d);

  // K6 yeterli olay sayısı (M ≥ xmeff)
  const nUse = events.filter(e => num(e.mag) !== null && +e.mag >= +xmeff - 1e-9).length;
  add('K6', 'Olay sayısı (M ≥ xmeff)', nUse < o.minN ? 'fail' : 'pass', `N = ${nUse} (en az ${o.minN}).`);

  // K7 sınır etkisi (uyarı): en büyük olayın bağlantı ölçeği kadar kenara yakın olaylar
  if (region && region.type !== 'circle') {
    add('K7', 'Sınır etkisi', 'warn', 'Dikdörtgen/poligon bölgede sınır payı hesaplanmadı. Daireler için ölçülen üyelik değişimi %0–1,5 (sinir_etkisi.json); köşeli bölgelerde ölçülmedi.');
  } else if (region && region.type === 'circle') {
    const mags = events.map(e => num(e.mag)).filter(v => v !== null);
    const mMax = mags.length ? Math.max(...mags) : null;
    const dB = mMax === null ? 0 : Math.min(region.rKm, interactionKm(mMax, o.rfact));
    const near = events.filter(e => num(e.lat) !== null && num(e.lon) !== null
      && region.rKm - epiKm(region.lat, region.lon, +e.lat, +e.lon) <= dB).length;
    const f = events.length ? near / events.length : 0;
    add('K7', 'Sınır etkisi', near ? 'warn' : 'pass',
      `Kenara ${dB.toFixed(1)} km'den yakın olay: ${near} (%${(100 * f).toFixed(1)}); ölçek = 10·r(Mmax=${mMax ?? '—'}). `
      + `Bu oran üyelik değişimi DEĞİLDİR: 18 test dairesinde (tüm katalog referansına göre) sınıfı değişen olay %0–1,5, `
      + `kenara 0,5·L'den yakın olaylarda %0,6 ölçüldü (analysis/2026-11-08_pyodide_reasenberg/sinir_etkisi.json).`);
  }

  // K9 zaman penceresi başı (uyarı). Ölçüm (mc_ve_zaman.json, zaman_tamponu.json): pencere başından sonraki ilk
  // 30 günde sınıf değişimi %8,4; büyük bir depremin hemen ardından başlayan pencerede tüm pencerede %5,8.
  // 90 günlük geri tampon bu etkiyi ölçülen 4 pencerenin 4'ünde sıfırladı.
  if (windowStart !== undefined) {
    if (windowStart === null) {
      add('K9', 'Zaman penceresi başı', 'warn', 'Pencere başlangıcı bilinmiyor; pencere başındaki kümeler kesik olabilir.');
    } else if (bufferDays >= 90) {
      add('K9', 'Zaman penceresi başı', 'pass', `${bufferDays} günlük geri tampon kullanıldı (ölçümde 90 gün yeterliydi).`);
    } else {
      const t0 = +windowStart, first = events.filter(e => { const d = (Date.parse(e.time) - t0) / 86400e3; return d >= 0 && d < 30; }).length;
      add('K9', 'Zaman penceresi başı', 'warn',
        `Geri tampon yok (${bufferDays} gün). Pencerenin ilk 30 gündeki olay: ${first} (%${events.length ? (100 * first / events.length).toFixed(1) : 0}). `
        + `Ölçümde bu bölümde sınıf değişimi %8,4; büyük bir depremin hemen ardından başlayan pencerede tüm pencerede %5,8. 90 günlük geri tampon etkiyi sıfırladı (zaman_tamponu.json).`);
    }
  }

  // K8 büyüklük ölçeği (uyarı)
  const types = [...new Set(events.map(e => (e.mtype || '?').toLowerCase()))];
  add('K8', 'Büyüklük ölçeği', types.length > 1 ? 'warn' : 'pass',
    types.length > 1 ? `Karışık ölçek (${types.join(', ')}): r(M) ve τ büyüklüğe bağlı; sonuç bu karışıma koşulludur.` : `Ölçek: ${types[0]}`);

  const state = checks.some(c => c.status === 'fail') ? 'OFF' : checks.some(c => c.status === 'warn') ? 'WARNING' : 'ELIGIBLE';
  return { state, checks, n_use: nUse };
}
