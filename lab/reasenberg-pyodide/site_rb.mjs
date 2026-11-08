// site_rb.mjs — Araştırma Bölgesi paneline DİNAMİK Reasenberg (deneysel) anahtarı.
//
// Yeni algoritma yok: rb_core (dondurulmuş reasenberg.py, Pyodide) + gates (K0–K9).
// Varsayılan KAPALI. Açılınca: Pyodide (depodan) → K0 öz-sınama (oturumda bir kez) →
// her bölge/dönem değişikliğinde güncel regionEvents yeniden değerlendirilir; koşullar
// bozulursa KAPALI, yeniden sağlanırsa tekrar çalışır. Sonuç YALNIZ RAPORLANIR:
// harita, GK74 ve diğer analizler değişmez. Statik GK74/Reasenberg katmanı ayrı kalır.

import { initReasenberg, runReasenberg, runSelfTest, PY_FILES } from './rb_core.mjs';
import { evaluateGates, STATE_LABEL } from './gates.mjs';

const BASE = new URL('../../', import.meta.url).href;            // depo kökü (site kökü)
const PYODIDE = new URL('vendor/pyodide/0.27.7/', BASE).href;
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const f = n => (+n).toLocaleString('tr-TR');

const S = { on: false, py: null, meta: null, selfTest: null, busy: false, lastSrc: null, lastKey: null, result: null };
window.__rbDyn = S;   // test ve hata ayıklama için

async function getJson(p) { const r = await fetch(new URL(p, BASE)); if (!r.ok) throw new Error(`${p}: ${r.status}`); return r.json(); }
async function getBytes(p) { const r = await fetch(new URL(p, BASE)); if (!r.ok) throw new Error(`${p}: ${r.status}`); return new Uint8Array(await r.arrayBuffer()); }

async function ensureRuntime() {
  if (S.py && S.selfTest) return;
  report(`<b style="color:#fbbf24">⏳ Reasenberg hazırlanıyor</b> — Pyodide (depodan, ~17 MB, oturumda bir kez) ve öz-sınama…`);
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
  // Pencere başı: canlı EMSC/USGS sorgusu ile aynı kural (tarih alanı ya da üst zaman düğmesi)
  let windowStart = null;
  if (srcName === 'emsc' || srcName === 'usgs') {
    const df = $('regionDateFrom')?.value;
    windowStart = df ? Date.parse(df + 'T00:00:00') : (typeof hours !== 'undefined' ? Date.now() - hours * 3600e3 : null);
  }
  const mcEst = (() => {      // sitenin KENDİ Mc tahmincisi (computeMcSrc), Reasenberg'in kullandığı 'mag' üzerinde
    const mc = typeof computeMcSrc === 'function' ? computeMcSrc(events.map(e => ({ mag: e.mag }))) : null;
    return mc === null ? { mc: null, method: 'MAXC+0.2 (sitenin computeMcSrc)', reason: 'en az 10 geçerli büyüklük gerekir' }
                       : { mc, method: 'MAXC+0.2 (sitenin computeMcSrc)' };
  })();
  const xRaw = ($('rbXmeff')?.value || '').trim();
  const xmeff = xRaw === '' ? mcEst.mc : +xRaw;
  return { evs, events, capped: typeof regionCapped !== 'undefined' && !!regionCapped, limit: limEl ? +limEl.value || null : null,
           region: circle, windowStart, mcEst, xmeff, xFromUser: xRaw !== '' };
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
    const g = evaluateGates({ events: inp.events, capped: inp.capped, limit: inp.limit, xmeff: inp.xmeff, mcEst: inp.mcEst,
      region: inp.region, selfTestPassed: S.selfTest.passed, windowStart: inp.windowStart, bufferDays: 0 });
    let res = null, ms = 0;
    if (g.state !== 'OFF') {
      const t0 = performance.now();
      res = runReasenberg(S.py, inp.events, inp.xmeff);
      ms = performance.now() - t0;
    }
    S.lastSrc = inp.evs; S.lastKey = key; S.result = { gates: g, res, ms, inp: { n: inp.events.length, xmeff: inp.xmeff, mc: inp.mcEst.mc } };
    S.result.cmp = res && gkReady ? compareGk(res, inp.evs) : null;
    render(g, res, ms, inp, S.result.cmp, gkReady);
  } catch (e) {
    S.result = { error: e.message };
    setBtn('⛔ Reasenberg: KAPALI (hata)', 'gkWarn');
    report(`<b style="color:#f87171">KAPALI</b> — ${esc(e.message)}`);
  } finally { S.busy = false; }
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

function render(g, res, ms, inp, cmp, gkReady) {
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
      `<span style="color:#888">Süre ${Math.round(ms)} ms · kural zmap · modül ${esc(S.meta.module_version)} (sha256 ${esc(S.meta.sha256.slice(0, 10))}…) · Pyodide ${esc(S.meta.python ? '0.27.7' : '')}</span><br>` +
      `<span style="color:#9ab0c5">Sonuç yalnız raporlanır: harita, GK74 ve diğer analizler değişmez. Çalıştırılabilmesi, sonucun bilimsel olarak yorumlanabilir olduğu anlamına gelmez; sonuç bölgeye, döneme, kaynağa ve xmeff'e koşulludur.</span>` +
      cmpHtml(cmp, gkReady);
  } else {
    setBtn('⛔ Reasenberg: KAPALI (koşul sağlanmadı)', 'gkWarn');
    body = `<span style="color:#f87171">Hesap yapılmadı.</span> Koşul sağlanınca (ör. sorgu sınırını artırınca) kendiliğinden yeniden çalışır.`;
  }
  report(`<b style="color:${col}">${icon} Reasenberg (deneysel): ${STATE_LABEL[g.state]}</b><br>${mcLine}<br>` +
    `<label style="display:inline-flex;gap:4px;align-items:center;margin:3px 0">xmeff (seçim) <input id="rbXmeff" type="number" step="0.1" value="${inp.xFromUser ? inp.xmeff : ''}" placeholder="= Mc" style="width:58px;background:#111;color:#ddd;border:1px solid #444;border-radius:4px;padding:1px 4px"></label><br>` +
    body + `<details style="margin-top:3px"><summary style="cursor:pointer;color:#9ab0c5">Uygunluk kapıları (${g.checks.filter(c => c.status !== 'pass').length} uyarı/engel)</summary><table style="font-size:.68rem;border-collapse:collapse">${rows}</table>` +
    `<div style="color:#888;margin-top:3px">Öz-sınama: ${S.selfTest.rows.map(r => `${r.name} ${r.same ? '✓' : '✗'}`).join(' · ')}</div></details>`);
  const x = $('rbXmeff'); if (x) x.onchange = () => evaluate(true);
}

async function toggle() {
  S.on = !S.on;
  if (!S.on) { setBtn('🧪 Reasenberg (deneysel): KAPALI'); const r = $('rbReport'); if (r) r.style.display = 'none'; return; }
  await evaluate(true);
}

function init() {
  const btn = $('btnRegionRb'), gk = $('btnRegionDecluster');
  if (!btn || !gk) return;
  btn.onclick = toggle;
  setBtn('🧪 Reasenberg (deneysel): KAPALI');
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
