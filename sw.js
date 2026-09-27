/* EQ-Live Türkiye — service worker (ana ekrana eklenebilir uygulama + çevrimdışı son veri).
   İlke: çevrimiçiyken HER ZAMAN ağdan gelen güncel sürüm kullanılır (network-first); önbellek yalnızca
   bağlantı yokken devreye girer. Böylece site güncellemeleri kullanıcıya gecikmeden ulaşır.
   Önbelleğe alınanlar: sayfa + simgeler (kabuk), Leaflet kütüphaneleri (değişmeyen sürüm → önce önbellek),
   GitHub'daki katalog JSON'ları (son başarılı sürüm). Canlı EMSC/USGS sorguları (zamana bağlı adresler) ve
   harita karoları önbelleğe ALINMAZ: sınırsız büyür ve tarayıcı kotasını doldurur. Sürüm değişince eski
   önbellekler silinir. */
const VERSION = 'eqlive-2026-09-28b';
const SHELL = `${VERSION}-shell`, LIBS = `${VERSION}-libs`, DATA = `${VERSION}-data`;
const SHELL_ASSETS = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png'];
const DATA_MAX = 40;

// Harita kütüphaneleri ilk kurulumda indirilir; böylece site ilk kez açıldıktan sonra çevrimdışı da açılabilir
const LIB_ASSETS = ['https://unpkg.com/leaflet@1.9.4/dist/leaflet.css', 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js'];
self.addEventListener('install', e => {
  e.waitUntil(Promise.all([
    caches.open(SHELL).then(c => c.addAll(SHELL_ASSETS)),
    caches.open(LIBS).then(c => Promise.all(LIB_ASSETS.map(u => fetch(new Request(u, { mode: 'no-cors' }))
      .then(r => (r.ok || r.type === 'opaque') ? c.put(u, r) : null).catch(() => null))))
  ]).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => !k.startsWith(VERSION)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function trim(cacheName, max) {
  const c = await caches.open(cacheName), keys = await c.keys();
  for (let i = 0; i < keys.length - max; i++) await c.delete(keys[i]);
}
async function networkFirst(req, cacheName, opts) {
  const c = await caches.open(cacheName);
  try {
    // Sayfa ve aynı kökenli dosyalar: tarayıcının HTTP önbelleğini atlayıp sunucuya sor (cache: 'no-cache' =
    // her seferinde yeniden doğrula). GitHub Pages ~10 dk önbellek süresi verdiği için, aksi hâlde yeni sürüm
    // yayınlandıktan sonra kurulu uygulama bir süre eski sayfayı gösterebiliyordu.
    const res = (opts && opts.revalidate) ? await fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' }) : await fetch(req);
    if (res && res.ok) { c.put(req, res.clone()); if (cacheName === DATA) trim(DATA, DATA_MAX); }
    return res;
  } catch (err) {
    const hit = await c.match(req, opts) || (opts && opts.fallback ? await c.match(opts.fallback) : null);
    if (hit) return hit;
    throw err;
  }
}
async function cacheFirst(req, cacheName) {
  const c = await caches.open(cacheName), hit = await c.match(req);
  if (hit) return hit;
  const res = await fetch(req); if (res && (res.ok || res.type === 'opaque')) c.put(req, res.clone());
  return res;
}

self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Sayfa (adres parametreleri ne olursa olsun): ağdan; çevrimdışıysa kayıtlı sayfa
  if (req.mode === 'navigate' && url.origin === location.origin) {
    e.respondWith(networkFirst(req, SHELL, { ignoreSearch: true, fallback: './index.html', revalidate: true })); return;
  }
  if (url.origin === location.origin) { e.respondWith(networkFirst(req, SHELL, { ignoreSearch: true, revalidate: true })); return; }
  // Sürümlü kütüphaneler (Leaflet, leaflet.heat, qrcode-generator)
  if (/^(unpkg\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net)$/.test(url.hostname)) { e.respondWith(cacheFirst(req, LIBS)); return; }
  // GitHub'daki katalog/veri dosyaları: son başarılı sürüm çevrimdışı gösterilebilsin
  if (url.hostname === 'raw.githubusercontent.com' && /\/EQ-LiveTurkiye\//.test(url.pathname) && /\.json$/.test(url.pathname)) {
    e.respondWith(networkFirst(req, DATA)); return;
  }
  // Diğer her şey (canlı API'ler, harita karoları): tarayıcının olağan davranışı
});
