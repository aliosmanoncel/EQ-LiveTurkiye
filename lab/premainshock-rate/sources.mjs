// sources.mjs — katalog kaynakları ve ayrıştırıcılar (EQ-Live Research · PMSR)
// Ortak olay biçimi: { id, t (UTC epoch s), lat, lon, m, magType }

const iso = t => new Date(t * 1000).toISOString().slice(0, 19);

export const SOURCES = {
  usgs: {
    label: 'USGS — Global (canlı FDSN)',
    url: (b, t0, t1) => `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&orderby=time-asc&limit=20000` +
      `&minlatitude=${b.s}&maxlatitude=${b.n}&minlongitude=${b.w}&maxlongitude=${b.e}&starttime=${iso(t0)}&endtime=${iso(t1)}`,
    limit: 20000,
    parse: txt => (JSON.parse(txt).features || []).map(f => ({
      id: f.id, t: f.properties.time / 1000, lat: f.geometry.coordinates[1], lon: f.geometry.coordinates[0],
      m: f.properties.mag, magType: (f.properties.magType || '').toLowerCase(),
      evType: f.properties.type })).filter(e => e.evType === 'earthquake' || !e.evType),
  },
  emsc: {
    label: 'EMSC — Avrupa, Türkiye dahil (canlı FDSN)',
    url: (b, t0, t1) => `https://www.seismicportal.eu/fdsnws/event/1/query?format=text&orderby=time-asc&limit=20000` +
      `&minlat=${b.s}&maxlat=${b.n}&minlon=${b.w}&maxlon=${b.e}&start=${iso(t0)}&end=${iso(t1)}`,
    limit: 20000,
    parse: parseFdsnText,
  },
};

// FDSN metin biçimi: EventID|Time|Latitude|Longitude|Depth|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|...
export function parseFdsnText(txt) {
  const out = [];
  for (const line of txt.split('\n')) {
    if (!line.trim() || line.startsWith('#') || !line.includes('|')) continue;
    const c = line.split('|');
    const t = Date.parse(c[1].trim().replace(/Z?$/, 'Z')) / 1000;
    const m = parseFloat(c[10]);
    if (!isFinite(t) || !isFinite(m)) continue;
    // Author: konum çözümünü veren kurum; MagAuthor: büyüklüğü veren kurum (ör. AFAD, KOERI, INGV, NOA)
    out.push({ id: c[0].trim(), t, lat: +c[2], lon: +c[3], m, magType: (c[9] || '').trim().toLowerCase(),
      author: (c[5] || '').trim() || '(boş)', magAuthor: (c[11] || '').trim() || '(boş)' });
  }
  return out;
}

// Kullanıcı dosyası: CSV (başlıklı) ya da AFAD JSON/CSV dışa aktarımı.
// CSV başlıkları (büyük/küçük harf duyarsız): id|eventid, time|date|datetime, lat|latitude, lon|longitude, mag|magnitude|m, magtype|type
// Saat dilimi belirtilmemiş zamanlar `tzOffsetHours` ile UTC'ye çevrilir (AFAD dışa aktarımları için genelde +3).
export function parseUpload(text, tzOffsetHours = 0) {
  const toT = s => {
    s = String(s).trim().replace(' ', 'T');
    const hasTz = /([zZ]|[+-]\d\d:?\d\d)$/.test(s);
    const t = Date.parse(hasTz ? s : s + 'Z') / 1000;
    return hasTz ? t : t - tzOffsetHours * 3600;
  };
  const trimmed = text.trim();
  if (trimmed.startsWith('[') || trimmed.startsWith('{')) {
    let arr = JSON.parse(trimmed); if (!Array.isArray(arr)) arr = arr.features || arr.events || arr.data || [];
    return arr.map((r, i) => ({
      id: r.eventID ?? r.eventId ?? r.id ?? i, t: toT(r.date ?? r.time ?? r.datetime),
      lat: +(r.latitude ?? r.lat), lon: +(r.longitude ?? r.lon), m: +(r.magnitude ?? r.mag ?? r.m),
      magType: String(r.type ?? r.magType ?? r.magtype ?? '').toLowerCase() })).filter(ok);
  }
  const lines = trimmed.split(/\r?\n/).filter(l => l.trim() && !l.startsWith('#'));
  const sep = lines[0].includes(';') ? ';' : (lines[0].includes('\t') ? '\t' : ',');
  const h = lines[0].split(sep).map(x => x.trim().toLowerCase().replace(/"/g, ''));
  const col = (...names) => h.findIndex(x => names.includes(x));
  const ci = { id: col('id', 'eventid', 'evid', 'event_id'), t: col('time', 'date', 'datetime', 'origin_time', 'tarih'),
    lat: col('lat', 'latitude', 'enlem'), lon: col('lon', 'lng', 'longitude', 'boylam'),
    m: col('mag', 'magnitude', 'm', 'buyukluk', 'büyüklük'), mt: col('magtype', 'mag_type', 'type', 'tip') };
  if (ci.t < 0 || ci.lat < 0 || ci.lon < 0 || ci.m < 0) throw new Error('CSV başlıkları tanınmadı: time, lat, lon, mag gerekli.');
  return lines.slice(1).map((l, i) => {
    const c = l.split(sep).map(x => x.trim().replace(/^"|"$/g, ''));
    return { id: ci.id >= 0 ? c[ci.id] : i, t: toT(c[ci.t]), lat: +c[ci.lat], lon: +c[ci.lon], m: +c[ci.m],
      magType: ci.mt >= 0 ? (c[ci.mt] || '').toLowerCase() : '' };
  }).filter(ok);
}
const ok = e => isFinite(e.t) && isFinite(e.lat) && isFinite(e.lon) && isFinite(e.m);

export function magTypeSummary(cat) {
  const c = {}; for (const e of cat) c[e.magType || '?'] = (c[e.magType || '?'] || 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1]);
}

// Kurum dağılımı (EMSC). field: 'author' (konum/zaman çözümünü veren, Origin Agency)
// ya da 'magAuthor' (büyüklüğü veren, Magnitude Agency). İkisi aynı olmak zorunda değildir.
export function agencySummary(cat, field = 'magAuthor') {
  const c = {}; for (const e of cat) if (e[field]) c[e[field]] = (c[e[field]] || 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1]);
}

export async function sha256OfCatalog(cat) {
  const s = cat.map(e => `${e.id},${e.t},${e.lat},${e.lon},${e.m},${e.magType},${e.author || ''},${e.magAuthor || ''}`).join('\n');
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}

// Baskın büyüklük türü filtresi: yalnız M < mMin olaylara uygulanır; M ≥ mMin (ana şok adayları,
// çoğunlukla Mw) türünden bağımsız korunur. Döner: { cat, dominant }
export function filterDominantMagType(cat, mMin) {
  const types = magTypeSummary(cat);
  if (types.length <= 1) return { cat, dominant: types[0] ? types[0][0] : null };
  const dom = types[0][0];
  return { cat: cat.filter(e => (e.magType || '?') === dom || e.m >= mMin), dominant: dom };
}
