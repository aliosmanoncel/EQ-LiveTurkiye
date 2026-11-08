// site_rb.mjs — Araştırma Bölgesi paneline DİNAMİK Reasenberg anahtarı.
//
// Yeni algoritma yok: rb_core (dondurulmuş reasenberg.py, Pyodide) + gates (K0–K9).
// Varsayılan KAPALI. Açılınca: Pyodide (depodan, Web Worker içinde) → K0 öz-sınama (oturumda bir kez) →
// her bölge/dönem değişikliğinde güncel regionEvents yeniden değerlendirilir; koşullar
// bozulursa KAPALI, yeniden sağlanırsa tekrar çalışır. Sonuç YALNIZ RAPORLANIR:
// harita, GK74 ve diğer analizler değişmez. Statik GK74/Reasenberg katmanı ayrı kalır.
// Geri tampon (2026-11-08): canlı EMSC/USGS sorgusunda pencere başından önceki 90 gün aynı bölge ve
// süzgeçlerle ayrıca çekilir, Reasenberg girdisine katılır; RAPORDA yalnız pencere olayları sayılır.
// Worker oluşturulamazsa hesap eski yolla ana iş parçacığında yapılır.

import { initReasenberg, runReasenberg, runSelfTest, PY_FILES } from './rb_core.mjs';
import { evaluateGates, STATE_LABEL } from './gates.mjs';

const BASE = new URL('../../', import.meta.url).href;            // depo kökü (site kökü)
const PYODIDE = new URL('vendor/pyodide/0.27.7/', BASE).href;
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const f = n => (+n).toLocaleString('tr-TR');

const BUFFER_DAYS = 90;   // zaman_tamponu.json: 90 günlük tamponla pencere başı farkı %0
const S = { on: false, py: null, meta: null, selfTest: null, busy: false, lastSrc: null, lastKey: null, result: null,
            worker: null, workerFailed: false, buf: { key: null, data: null } };
window.__rbDyn = S;   // test ve hata ayıklama için

async function getJson(p) { const r = await fetch(new URL(p, BASE)); if (!r.ok) throw new Error(`${p}: ${r.status}`); return r.json(); }
async function getBytes(p) { const r = await fetch(new URL(p, BASE)); if (!r.ok) throw new Error(`${p}: ${r.status}`); return new Uint8Array(await r.arrayBuffer()); }

// ── Worker (arayüz donmasın) ─────────────────────────────────────────────
let reqId = 0; const waiting = new Map();
function workerCall(msg) {
  return new Promise((resolve, reject) => {
    const id = ++reqId; waiting.set(id, { resolve, reject });
    S.worker.postMessage({ id, ...msg });
  });
}
function startWorker() {
  if (S.worker || S.workerFailed) return !!S.worker;
  try {
    S.worker = new Worker(new URL('./rb_worker.mjs', import.meta.url), { type: 'module' });
    S.worker.onmessage = ({ data }) => { const w = waiting.get(data.id); if (!w) return; waiting.delete(data.id); data.ok ? w.resolve(data) : w.reject(new Error(data.error)); };
    S.worker.onerror = e => { for (const w of waiting.values()) w.reject(new Error('Worker hatası: ' + (e.message || 'bilinmiyor'))); waiting.clear(); };
    return true;
  } catch (e) { S.workerFailed = true; S.worker = null; return false; }
}
async function runRb(events, xmeff) {
  if (S.worker) { const r = await workerCall({ type: 'run', events, xmeff }); return { res: r.res, ms: r.ms }; }
  const t0 = performance.now(); const res = runReasenberg(S.py, events, xmeff); return { res, ms: performance.now() - t0 };
}

async function ensureRuntime() {
  if (S.meta && S.selfTest) return;
  report(`<b style="color:#fbbf24">⏳ Reasenberg hazırlanıyor</b> — Pyodide (depodan, ~17 MB, oturumda bir kez) ve öz-sınama…`);
  if (startWorker()) {
    try { const r = await workerCall({ type: 'init' }); S.meta = r.meta; S.selfTest = r.selfTest; return; }
    catch (e) { S.worker.terminate(); S.worker = null; S.workerFailed = true; }   // ana iş parçacığına düş
  }
  const { loadPyodide } = await import(PYODIDE + 'pyodide.mjs');
  const py = await loadPyodide({ indexURL: PYODIDE });
  await py.loadPackage('numpy');
  const src = {}; for (const f of PY_FILES) src[f] = await getBytes('scripts/' + f);
  S.meta = await initReasenberg(py, src);                         // sha256 tutmazsa hata → KAPALI
  S.py = py;
  S.selfTest = await runSelfTest(py, getJson);                    // K0: oturumda bir kez, hesaptan önce
}

// Sitenin kendi durumundan girdiler (sorgu koduna dokunmadan)
function inputs() {
  const evs = (typeof regionEvents !== 'undefined' && regionEvents) ? regionEvents : [];
  const srcName = typeof regionSource !== 'undefined' ? regionSource : '?';
  const events = evs.map((e, i) => ({
    id: `r${i}`, time:   // kimlik = regionEvents dizinindeki sıra (GK74 ile olay bazında eşleme için)
    e.time instanceof Date ? e.time.toISOString() : e.time,
    lat: e.lat, lon: e.lon, dep: e.dep, mag: e.mag, mtype: e.mtype, src: e.src || srcName }));
  const limEl = $('regionLimit');
  const circle = typeof regionIsCircle !== 'undefined' && regionIsCircle && regionCircleCenter
    ? { type: 'circle', lat: regionCircleCenter.lat, lon: regionCircleCenter.lon, rKm: regionCircleRadiusKm } : { type: 'rect' };
  // Pencere başı: canlı EMSC/USGS sorgusunun kendi kaydettiği başlangıç (regionWindowStart); yoksa aynı kural
  let windowStart = null;
  if (srcName === 'emsc' || srcName === 'usgs') {
    const ws = typeof regionWindowStart !== 'undefined' && regionWindowStart ? +regionWindowStart : null;
    const df = $('regionDateFrom')?.value;
    windowStart = ws ?? (df ? Date.parse(df + 'T00:00:00') : (typeof hours !== 'undefined' ? Date.now() - hours * 3600e3 : null));
  }
  const mcEst = (() => {      // sitenin KENDİ Mc tahmincisi (computeMcSrc), Reasenberg'in kullandığı 'mag' üzerinde
    const mc = typeof computeMcSrc === 'function' ? computeMcSrc(events.map(e => ({ mag: e.mag }))) : null;
    return mc === null ? { mc: null, method: 'MAXC+0.2 (sitenin computeMcSrc)', reason: 'en az 10 geçerli büyüklük gerekir' }
                       : { mc, method: 'MAXC+0.2 (sitenin computeMcSrc)' };
  })();
  const xRaw = ($('rbXmeff')?.value || '').trim();
  const xmeff = xRaw === '' ? mcEst.mc : +xRaw;
  return { evs, events, srcName, capped: typeof regionCapped !== 'undefined' && !!regionCapped, limit: limEl ? +limEl.value || null : null,
           region: circle, windowStart, mcEst, xmeff, xFromUser: xRaw !== '' };
}

// ── 90 günlük geri tampon: pencere başından önceki olaylar, AYNI bölge ve süzgeçlerle ──────────
// Sitenin sorgu kodu değişmez; aynı servis, aynı ayrıştırıcılar (parseEMSCText/parseGeoJSON) ve aynı
// poligon/daire süzgeci kullanılır. Tampon olayları yalnız Reasenberg girdisidir; raporda sayılmaz.
async function fetchBuffer(inp) {
  const none = reason => ({ evs: [], days: 0, capped: false, reason });
  if (!(inp.srcName === 'emsc' || inp.srcName === 'usgs')) return none('canlı EMSC/USGS sorgusu değil');
  if (!inp.windowStart || typeof regionRect === 'undefined' || !regionRect) return none('pencere başı ya da bölge yok');
  const b = regionRect.getBounds(), v = id => $(id)?.value || '';
  const t1 = inp.windowStart - 1000, t0 = inp.windowStart - BUFFER_DAYS * 86400e3, fmt = t => new Date(t).toISOString().slice(0, 19);
  const common = `&starttime=${fmt(t0)}&endtime=${fmt(t1)}&minmagnitude=${v('regionMagMin') || 0}${v('regionMagMax') ? `&maxmagnitude=${v('regionMagMax')}` : ''}` +
    `${v('regionDepMin') ? `&mindepth=${v('regionDepMin')}` : ''}${v('regionDepMax') ? `&maxdepth=${v('regionDepMax')}` : ''}&limit=20000&orderby=time`;
  const [s, n, w, e] = [b.getSouth(), b.getNorth(), b.getWest(), b.getEast()].map(x => x.toFixed(3));
  const url = inp.srcName === 'usgs'
    ? `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minlatitude=${s}&maxlatitude=${n}&minlongitude=${w}&maxlongitude=${e}` + common
    : `https://www.seismicportal.eu/fdsnws/event/1/query?format=text&minlat=${s}&maxlat=${n}&minlon=${w}&maxlon=${e}` + common;
  if (S.buf.key === url) return S.buf.data;
  const res = await fetchTimeout(url, {}, 20000);
  let evs = [], raw = 0;
  if (res.status !== 204) {
    if (!res.ok) throw new Error(`tampon sorgusu HTTP ${res.status}`);
    if (inp.srcName === 'usgs') { const js = await res.json(); raw = (js.features || []).length; evs = parseGeoJSON(js); }
    else { const tx = await res.text(); raw = tx.split('\n').filter(l => l.trim() && !l.startsWith('#') && l.includes('|')).length; evs = parseEMSCText(tx); }
  }
  if (typeof regionIsPolygon !== 'undefined' && regionIsPolygon) { const poly = regionRect.getLatLngs()[0]; evs = evs.filter(x => pointInPolygon(x.lat, x.lon, poly)); }
  if (typeof regionIsCircle !== 'undefined' && regionIsCircle && regionCircleCenter) evs = evs.filter(x => pointInCircle(x.lat, x.lon, regionCircleCenter.lat, regionCircleCenter.lon, regionCircleRadiusKm));
  evs = evs.filter(x => x.time.getTime() < inp.windowStart);
  const capped = raw >= 20000;
  // orderby=time en yeniden başlar: sınıra takılırsa pencereye en yakın kısım kalır; kapsanan gün sayısı ondan ölçülür
  const days = capped && evs.length ? Math.floor((inp.windowStart - Math.min(...evs.map(x => x.time.getTime()))) / 86400e3) : BUFFER_DAYS;
  const data = { evs, days, capped, reason: null };
  S.buf = { key: url, data };
  return data;
}

function report(html) { const r = $('rbReport'); if (r) { r.style.display = ''; r.innerHTML = html; } }
function setBtn(text, cls) {
  const b = $('btnRegionRb'); if (!b) return;
  b.textContent = text; b.classList.remove('gkOn', 'gkWarn', 'gkBusy'); if (cls) b.classList.add(cls);
  b.setAttribute('aria-pressed', S.on ? 'true' : 'false');
}

async function evaluate(force = false) {
  if (!S.on || S.busy) return;
  if (typeof regionLoading !== 'undefined' && regionLoading) { setBtn('⏳ Reasenberg: bölge verisi yükleniyor', 'gkBusy'); return; }
  const inp = inputs();
  const gkReady = typeof regionDeclusterOn !== 'undefined' && regionDeclusterOn && gk74Cache && gk74Cache.src === inp.evs;
  const key = `${inp.xmeff}|${inp.capped}|${inp.limit}|${gkReady ? gk74Cache.keep.size + ':' + (gk74Cache.ctx ? 'ctx' : '') : 'nogk'}`;
  if (!force && inp.evs === S.lastSrc && key === S.lastKey) return;   // aynı katalog, aynı ayar
  S.busy = true; setBtn('⏳ Reasenberg ÇALIŞIYOR…', 'gkBusy');
  try {
    await ensureRuntime();
    let buf;
    try { buf = await fetchBuffer(inp); } catch (e) { buf = { evs: [], days: 0, capped: false, reason: 'tampon alınamadı: ' + e.message }; }
    const g = evaluateGates({ events: inp.events, capped: inp.capped, limit: inp.limit, xmeff: inp.xmeff, mcEst: inp.mcEst,
      region: inp.region, selfTestPassed: S.selfTest.passed, windowStart: inp.windowStart, bufferDays: buf.days });
    let res = null, ms = 0;
    if (g.state !== 'OFF') {
      const bufEvents = buf.evs.map((e, i) => ({ id: `b${i}`, time: e.time instanceof Date ? e.time.toISOString() : e.time,
        lat: e.lat, lon: e.lon, dep: e.dep, mag: e.mag, mtype: e.mtype, src: e.src || inp.srcName }));
      const out = await runRb(bufEvents.concat(inp.events), inp.xmeff);
      res = windowOnly(out.res); ms = out.ms;
    }
    S.lastSrc = inp.evs; S.lastKey = key;
    S.result = { gates: g, res, ms, buf: { n: buf.evs.length, days: buf.days, capped: buf.capped, reason: buf.reason },
                 inp: { n: inp.events.length, xmeff: inp.xmeff, mc: inp.mcEst.mc } };
    S.result.cmp = res && gkReady ? compareGk(res, inp.evs) : null;
    render(g, res, ms, inp, S.result.cmp, gkReady, S.result.buf);
  } catch (e) {
    S.result = { error: e.message };
    setBtn('⛔ Reasenberg: KAPALI (hata)', 'gkWarn');
    report(`<b style="color:#f87171">KAPALI</b> — ${esc(e.message)}`);
  } finally { S.busy = false; }
}

// Tampon olaylarını sonuçtan çıkar: raporda yalnız pencere olayları (id 'r…') sayılır. Küme sayısı, en az bir
// pencere olayı içeren kümelerdir (yalnız tampondaki kümeler sayılmaz).
function windowOnly(r) {
  const keep = r.ids.map((id, k) => id.startsWith('r') ? k : -1).filter(k => k >= 0);
  const cl = new Set(keep.map(k => r.cluster_id[k]).filter(c => c >= 0));
  return { ...r, ids: keep.map(k => r.ids[k]), cluster_id: keep.map(k => r.cluster_id[k]), event_class: keep.map(k => r.event_class[k]),
           n_clusters: cl.size, n_input: r.ids.length };
}

// GK74 ile olay bazında karşılaştırma (double-check). Hiçbiri "doğru" kabul edilmez; farklar karşılaştırmanın verisidir.
function compareGk(res, evs) {
  const bins = [['<3,5', 0, 3.5], ['3,5–4', 3.5, 4], ['4–5', 4, 5], ['≥5', 5, 99]];
  const cat = { both_indep: 0, both_dep: 0, only_gk_dep: 0, only_rb_dep: 0 };
  const byM = { only_gk_dep: bins.map(() => 0), only_rb_dep: bins.map(() => 0) };
  const yrs = { only_gk_dep: [], only_rb_dep: [] };
  res.ids.forEach((id, k) => {
    const e = evs[+id.slice(1)]; if (!e) return;
    const gkDep = !gk74Cache.keep.has(e), rbDep = res.event_class[k] === 'dependent';
    const c = gkDep && rbDep ? 'both_dep' : gkDep ? 'only_gk_dep' : rbDep ? 'only_rb_dep' : 'both_indep';
    cat[c]++;
    if (byM[c]) { byM[c][bins.findIndex(b => e.mag >= b[1] && e.mag < b[2])]++; yrs[c].push(e.time.getUTCFullYear()); }
  });
  const span = a => a.length ? `${Math.min(...a)}–${Math.max(...a)}` : '—';
  return { cat, bins: bins.map(b => b[0]), byM, span: { only_gk_dep: span(yrs.only_gk_dep), only_rb_dep: span(yrs.only_rb_dep) },
           n: res.ids.length, ctx: !!gk74Cache.ctx };
}

function cmpHtml(cmp, gkReady) {
  if (!gkReady) return `<div style="color:#9ab0c5;margin-top:3px">GK74 ile olay bazında karşılaştırma için yukarıdaki <b>GK74 artçı ayıklama</b>'yı açın.</div>`;
  const c = cmp.cat, n = cmp.n, p = x => n ? (100 * x / n).toFixed(1) : '0';
  const mrow = k => cmp.byM[k].map((v, i) => `${cmp.bins[i]}: ${f(v)}`).join(' · ');
  return `<div style="margin-top:4px;border-top:1px solid #334;padding-top:4px"><b>GK74 ↔ Reasenberg (aynı olaylar, double-check)</b>` +
    `<table style="font-size:.7rem;border-collapse:collapse;margin-top:2px">` +
    `<tr><td>İkisi de bağımsız</td><td style="text-align:right;padding-left:8px">${f(c.both_indep)}</td><td style="padding-left:6px;color:#888">%${p(c.both_indep)}</td></tr>` +
    `<tr><td>İkisi de bağımlı</td><td style="text-align:right;padding-left:8px">${f(c.both_dep)}</td><td style="padding-left:6px;color:#888">%${p(c.both_dep)}</td></tr>` +
    `<tr><td style="color:#c4b5fd">Yalnız GK74 bağımlı</td><td style="text-align:right;padding-left:8px">${f(c.only_gk_dep)}</td><td style="padding-left:6px;color:#888">%${p(c.only_gk_dep)}</td></tr>` +
    `<tr><td style="color:#fdba74">Yalnız Reasenberg bağımlı</td><td style="text-align:right;padding-left:8px">${f(c.only_rb_dep)}</td><td style="padding-left:6px;color:#888">%${p(c.only_rb_dep)}</td></tr></table>` +
    `<div style="color:#9ab0c5">Uyum %${p(c.both_indep + c.both_dep)} (doğruluk ölçüsü değil).</div>` +
    `<div style="color:#c4b5fd">Yalnız GK74 — M: ${mrow('only_gk_dep')} · yıllar ${cmp.span.only_gk_dep}</div>` +
    `<div style="color:#fdba74">Yalnız Reasenberg — M: ${mrow('only_rb_dep')} · yıllar ${cmp.span.only_rb_dep}</div>` +
    `<div style="color:#888">Yöntem farkı: GK74 burada yalnız artçı ayıklar (öncüler kalır), episantral mesafe${cmp.ctx ? ', bağlamlı' : ''}; Reasenberg öncüleri de kümeye katar, hiposantral mesafe. Hiçbir yöntem doğru kabul edilmez; farklar karşılaştırmanın verisidir.</div></div>`;
}

function render(g, res, ms, inp, cmp, gkReady, buf) {
  const col = { ELIGIBLE: '#4ade80', WARNING: '#fbbf24', OFF: '#f87171' }[g.state];
  const icon = { ELIGIBLE: '✅', WARNING: '⚠', OFF: '⛔' }[g.state];
  const rows = g.checks.map(c => `<tr><td style="white-space:nowrap;vertical-align:top">${c.id}</td><td style="color:${{ pass: '#4ade80', warn: '#fbbf24', fail: '#f87171' }[c.status]};vertical-align:top">${{ pass: '✓', warn: '!', fail: '✗' }[c.status]}</td><td>${esc(c.label)}: ${esc(c.detail)}</td></tr>`).join('');
  const mcLine = `Mc (tahmin, ${esc(inp.mcEst.method)}) <b>${inp.mcEst.mc ?? '—'}</b> · xmeff (${inp.xFromUser ? 'kullanıcı seçimi' : 'tahminden'}) <b>${Number.isFinite(inp.xmeff) ? inp.xmeff.toFixed(2) : '—'}</b>`;
  let body = '';
  if (res) {
    const c = k => res.event_class.filter(x => x === k).length;
    const n = res.ids.length, dep = c('dependent');
    setBtn(`${icon} Reasenberg ${STATE_LABEL[g.state]} · ${f(n)} → ${f(n - dep)} bağımsız`, g.state === 'ELIGIBLE' ? 'gkOn' : 'gkWarn');
    body = `Toplam <b>${f(n)}</b> olay → bağımsız <b>${f(n - dep)}</b> (tekil ${f(c('single'))} + temsilci ${f(c('representative'))}) · bağımlı <b>${f(dep)}</b> (%${n ? (100 * dep / n).toFixed(0) : 0}) · küme <b>${f(res.n_clusters)}</b><br>` +
      `<span style="color:#888">Geri tampon: ${buf && buf.days ? `${f(buf.n)} olay, ${buf.days} gün${buf.capped ? ' (sorgu sınırına takıldı)' : ''} — yalnız girdi, raporda sayılmaz` : esc(buf?.reason || 'yok')}</span><br>` +
      `<span style="color:#888">Süre ${Math.round(ms)} ms${S.worker ? ' (arka planda)' : ''} · kural zmap · modül ${esc(S.meta.module_version)} (sha256 ${esc(S.meta.sha256.slice(0, 10))}…) · Pyodide ${esc(S.meta.python ? '0.27.7' : '')}</span><br>` +
      `<span style="color:#9ab0c5">Sonuç yalnız raporlanır: harita, GK74 ve diğer analizler değişmez. Çalıştırılabilmesi, sonucun bilimsel olarak yorumlanabilir olduğu anlamına gelmez; sonuç bölgeye, döneme, kaynağa ve xmeff'e koşulludur.</span>` +
      cmpHtml(cmp, gkReady);
  } else {
    setBtn('⛔ Reasenberg: KAPALI (koşul sağlanmadı)', 'gkWarn');
    body = `<span style="color:#f87171">Hesap yapılmadı.</span> Koşul sağlanınca (ör. sorgu sınırını artırınca) kendiliğinden yeniden çalışır.`;
  }
  report(`<b style="color:${col}">${icon} Reasenberg (dinamik): ${STATE_LABEL[g.state]}</b><br>${mcLine}<br>` +
    `<label style="display:inline-flex;gap:4px;align-items:center;margin:3px 0">xmeff (seçim) <input id="rbXmeff" type="number" step="0.1" value="${inp.xFromUser ? inp.xmeff : ''}" placeholder="= Mc" style="width:58px;background:#111;color:#ddd;border:1px solid #444;border-radius:4px;padding:1px 4px"></label><br>` +
    body + `<details style="margin-top:3px"><summary style="cursor:pointer;color:#9ab0c5">Uygunluk kapıları (${g.checks.filter(c => c.status !== 'pass').length} uyarı/engel)</summary><table style="font-size:.68rem;border-collapse:collapse">${rows}</table>` +
    `<div style="color:#888;margin-top:3px">Öz-sınama: ${S.selfTest.rows.map(r => `${r.name} ${r.same ? '✓' : '✗'}`).join(' · ')}</div></details>`);
  const x = $('rbXmeff'); if (x) x.onchange = () => evaluate(true);
}

async function toggle() {
  S.on = !S.on;
  if (!S.on) { setBtn('🧪 Reasenberg (dinamik): KAPALI'); const r = $('rbReport'); if (r) r.style.display = 'none'; return; }
  await evaluate(true);
}

function init() {
  const btn = $('btnRegionRb'), gk = $('btnRegionDecluster');
  if (!btn || !gk) return;
  btn.onclick = toggle;
  setBtn('🧪 Reasenberg (dinamik): KAPALI');
  // Görünürlük GK74 düğmesini izler (bölge seçildiğinde görünür)
  const sync = () => { const vis = gk.style.display !== 'none'; btn.style.display = vis ? '' : 'none';
    if (!vis) { const r = $('rbReport'); if (r) r.style.display = 'none'; } else if (S.on && S.result) $('rbReport').style.display = ''; };
  new MutationObserver(sync).observe(gk, { attributes: true, attributeFilter: ['style'] }); sync();
  // Bölge verisi değişince (yeni sorgu, yeni bölge, temizleme) yeniden değerlendir
  if (typeof window.renderRegionInfo === 'function') {
    const orig = window.renderRegionInfo;
    window.renderRegionInfo = function (...a) { const r = orig.apply(this, a); setTimeout(() => evaluate(false), 0); return r; };
  }
}
init();
