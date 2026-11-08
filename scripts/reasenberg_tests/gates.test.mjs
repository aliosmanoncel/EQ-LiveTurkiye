// gates.test.mjs — uygunluk kapılarının birim testleri (node --test).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { evaluateGates, estimateMc, interactionKm, computeMcSrc, mcSrcMag } from '../../lab/reasenberg-pyodide/gates.mjs';

// 0.1 adımlı, M 2.0–4.9 arası, mod 3.0'da olan yapay katalog (deterministik)
function cat(n = 400, { src = 'EMSC', mtype = 'ml', lat0 = 39, lon0 = 32 } = {}) {
  const ev = [];
  for (let i = 0; i < n; i++) {
    const m = 3.0 + ((i * 7) % 20) / 10 * (i % 3 === 0 ? -0.5 : 1);
    ev.push({ id: `e${i}`, time: new Date(Date.UTC(2020, 0, 1) + i * 3600e3).toISOString(), lat: lat0 + ((i * 13) % 100) / 100,
      lon: lon0 + ((i * 17) % 100) / 100, dep: 10, mag: +m.toFixed(1), mtype, src });
  }
  return ev;
}
const status = (r, id) => r.checks.find(c => c.id === id)?.status;

test('tüm koşullar sağlanınca UYGUN (sınır denetimi yok)', () => {
  const ev = cat();
  const mc = estimateMc(ev);
  const r = evaluateGates({ events: ev, capped: false, limit: 500, xmeff: mc.mc, mcEst: mc });
  assert.equal(r.state, 'ELIGIBLE');
});

test('K1: sorgu sınırına takılan katalog → OFF; sınır kalkınca yeniden ON', () => {
  const ev = cat(); const mc = estimateMc(ev);
  assert.equal(evaluateGates({ events: ev, capped: true, limit: 400, xmeff: mc.mc, mcEst: mc }).state, 'OFF');
  assert.equal(evaluateGates({ events: ev, capped: false, limit: 2000, xmeff: mc.mc, mcEst: mc }).state, 'ELIGIBLE');
});

test('K2: birden çok kaynak → OFF', () => {
  const ev = [...cat(200), ...cat(200, { src: 'ISC' }).map(e => ({ ...e, id: 'i' + e.id }))];
  const mc = estimateMc(ev);
  const r = evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc });
  assert.equal(r.state, 'OFF'); assert.equal(status(r, 'K2'), 'fail');
});

test('K3: geçersiz alan oranı eşiği aşınca → OFF', () => {
  const ev = cat(); for (let i = 0; i < 40; i++) ev[i].dep = null;
  const mc = estimateMc(ev);
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc }), 'K3'), 'fail');
});

test('K4: içerikçe yinelenen kayıt → OFF (kimlik olmasa da)', () => {
  const ev = cat().map(({ id, ...e }) => e); ev[5] = { ...ev[4] };
  const mc = estimateMc(ev);
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc }), 'K4'), 'fail');
});

test('K5: Mc tahmin edilemezse ya da xmeff tahminin altındaysa → OFF; tahmin ile seçim ayrı yazılır', () => {
  const ev = cat();
  const mc = estimateMc(ev);
  const low = evaluateGates({ events: ev, capped: false, xmeff: mc.mc - 0.3, mcEst: mc });
  assert.equal(status(low, 'K5'), 'fail');
  const d = low.checks.find(c => c.id === 'K5').detail;
  assert.match(d, /Mc \(tahmin/); assert.match(d, /xmeff \(seçim\)/);
  const none = evaluateGates({ events: ev.slice(0, 10), capped: false, xmeff: 3.0, mcEst: estimateMc(ev.slice(0, 5)) });
  assert.equal(status(none, 'K5'), 'fail');
});

test('K6: M ≥ xmeff olay sayısı yetersiz → OFF', () => {
  const ev = cat(); const mc = estimateMc(ev);
  const r = evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, opts: { minN: 10000 } });
  assert.equal(status(r, 'K6'), 'fail'); assert.equal(r.state, 'OFF');
});

test('K7/K8: sınır ve karışık ölçek yalnız uyarı (UYARILI), hesabı durdurmaz', () => {
  const ev = cat(); ev[0].mtype = 'mw';
  const mc = estimateMc(ev);
  const r = evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, region: { type: 'circle', lat: 39.5, lon: 32.5, rKm: 60 } });
  assert.equal(r.state, 'WARNING'); assert.equal(status(r, 'K7'), 'warn'); assert.equal(status(r, 'K8'), 'warn');
});

test('etkileşim ölçeği: 10·0.011·10^(0.4M)', () => {
  assert.ok(Math.abs(interactionKm(5) - 11) < 1e-9);
});

test('K0: öz-sınama geçmediyse → KAPALI (D-P5)', () => {
  const ev = cat(); const mc = estimateMc(ev);
  const r = evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, selfTestPassed: false });
  assert.equal(r.state, 'OFF'); assert.equal(status(r, 'K0'), 'fail');
});

test('D-P1: Mc tahmincisi index.html computeMcSrc/mcSrcMag ile BİREBİR aynı kod', () => {
  const idx = readFileSync('index.html', 'utf8');
  const norm = f => f.toString().replace(/\s+/g, ' ').trim();
  const pick = name => { const i = idx.indexOf(`function ${name}(`); assert.ok(i >= 0, name);
    // fonksiyonun sonu: dengeli süslü parantez
    let d = 0, j = idx.indexOf('{', i); for (; j < idx.length; j++) { if (idx[j] === '{') d++; else if (idx[j] === '}' && --d === 0) break; }
    return idx.slice(i, j + 1); };
  assert.equal(norm(computeMcSrc), norm(pick('computeMcSrc')));
  assert.equal(norm(mcSrcMag), norm(pick('mcSrcMag')));
});

test('estimateMc: Reasenberg ile aynı büyüklük alanı (mag) kullanılır; mw yok sayılır', () => {
  const ev = cat().map(e => ({ ...e, mw: 9.9 }));
  assert.equal(estimateMc(ev).mc, estimateMc(cat()).mc);
});

test('K4: kimliksiz ama farklı olaylar yineleme sayılmaz', () => {
  const ev = cat().map(({ id, ...e }) => e); const mc = estimateMc(ev);
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc }), 'K4'), 'pass');
});

test('K9: geri tampon yoksa uyarı, ≥90 gün tamponla geçer, başlangıç bilinmiyorsa uyarı', () => {
  const ev = cat(); const mc = estimateMc(ev); const t0 = Date.parse(ev[0].time);
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, windowStart: t0 }), 'K9'), 'warn');
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, windowStart: t0, bufferDays: 90 }), 'K9'), 'pass');
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, windowStart: null }), 'K9'), 'warn');
  assert.equal(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc }).checks.some(c => c.id === 'K9'), false);
});

test('K7: köşeli bölgede genel sınır uyarısı', () => {
  const ev = cat(); const mc = estimateMc(ev);
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, region: { type: 'rect' } }), 'K7'), 'warn');
});
