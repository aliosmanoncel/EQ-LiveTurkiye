// gates.mjs — Dinamik Reasenberg için UYGUNLUK KAPILARI (DENEME).
//
// Kural: her çalıştırmadan önce veri yeterliliği ve parametre koşulları denetlenir.
//   OFF      : en az bir zorunlu koşul sağlanmıyor → hesap YAPILMAZ, neden(ler) gösterilir.
//   ON_WARN  : zorunlu koşullar sağlanıyor, yorum sınırlayıcı bir uyarı var → hesap + uyarı.
//   ON       : tüm koşullar sağlanıyor.
// Koşul sonradan sağlanırsa (ör. sorgu sınırı artırılır) aynı denetim yeniden ON verir.
//
// Mc ayrımı: "Mc (tahmin)" veriden hesaplanan değerdir; "xmeff (seçim)" kullanıcının
// girdiği eşiktir. Seçimin tahminin üstünde olması yalnız tutarlılık denetimidir;
// Mc'nin bilimsel olarak doğrulandığı anlamına gelmez.
//
// Algoritma kodu içermez; Reasenberg hesabı rb_core.mjs → Pyodide → reasenberg.py.

export const DEFAULTS = Object.freeze({ minN: 50, maxInvalidFrac: 0.05, mcBin: 0.1, mcCorr: 0.2, minForMc: 50, rfact: 10 });

const num = v => (v === null || v === undefined || v === '' || !Number.isFinite(+v)) ? null : +v;
const KM_PER_DEG = 111.195;

// MAXC + düzeltme (Wiemer & Wyss 2000; düzeltme +0.2: Woessner & Wiemer 2005).
// Deneme sayfası için; sitede bütünleştirmede sitenin mevcut Mc tahmincisi kullanılmalı.
export function estimateMcMaxc(mags, { bin = DEFAULTS.mcBin, corr = DEFAULTS.mcCorr, minN = DEFAULTS.minForMc } = {}) {
  const m = mags.map(num).filter(v => v !== null);
  if (m.length < minN) return { mc: null, method: 'MAXC+0.2', n: m.length, reason: `Mc için en az ${minN} geçerli büyüklük gerekir (${m.length})` };
  const counts = new Map();
  for (const v of m) { const k = Math.round(v / bin); counts.set(k, (counts.get(k) || 0) + 1); }
  let best = null, bestN = -1;
  for (const [k, c] of [...counts.entries()].sort((a, b) => a[0] - b[0])) if (c > bestN) { best = k; bestN = c; }
  return { mc: +(best * bin + corr).toFixed(2), method: `MAXC+${corr}`, n: m.length };
}

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
export function evaluateGates({ events, capped, limit, xmeff, mcEst, region = null, opts = {} }) {
  const o = { ...DEFAULTS, ...opts };
  const checks = [];
  const add = (id, label, status, detail) => checks.push({ id, label, status, detail });

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

  // K4 zaman sıralaması ve kimlik tekilliği (sıralamayı adaptör yapar; yinelenen kimlik = yinelenen kayıt)
  const ids = events.map(e => e.id);
  const dupIds = ids.length - new Set(ids).size;
  add('K4', 'Zaman sıralaması / tekil kayıt', dupIds ? 'fail' : 'pass',
    dupIds ? `${dupIds} yinelenen kimlik: aynı olay birden çok kez var.` : 'Kimlikler tekil; zaman sıralaması adaptörde UTC ile yapılır.');

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
  if (region && region.type === 'circle') {
    const mags = events.map(e => num(e.mag)).filter(v => v !== null);
    const mMax = mags.length ? Math.max(...mags) : null;
    const dB = mMax === null ? 0 : Math.min(region.rKm, interactionKm(mMax, o.rfact));
    const near = events.filter(e => num(e.lat) !== null && num(e.lon) !== null
      && region.rKm - epiKm(region.lat, region.lon, +e.lat, +e.lon) <= dB).length;
    const f = events.length ? near / events.length : 0;
    add('K7', 'Sınır etkisi', near ? 'warn' : 'pass',
      `Kenara ${dB.toFixed(1)} km'den yakın olay: ${near} (%${(100 * f).toFixed(1)}); ölçek = 10·r(Mmax=${mMax ?? '—'}). Bu olayların kümeleri daire dışına taşabilir.`);
  }

  // K8 büyüklük ölçeği (uyarı)
  const types = [...new Set(events.map(e => (e.mtype || '?').toLowerCase()))];
  add('K8', 'Büyüklük ölçeği', types.length > 1 ? 'warn' : 'pass',
    types.length > 1 ? `Karışık ölçek (${types.join(', ')}): r(M) ve τ büyüklüğe bağlı; sonuç bu karışıma koşulludur.` : `Ölçek: ${types[0]}`);

  const state = checks.some(c => c.status === 'fail') ? 'OFF' : checks.some(c => c.status === 'warn') ? 'ON_WARN' : 'ON';
  return { state, checks, n_use: nUse };
}
