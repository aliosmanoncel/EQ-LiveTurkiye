// gates.test.mjs — uygunluk kapılarının birim testleri (node --test).
import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluateGates, estimateMcMaxc, interactionKm } from '../../lab/reasenberg-pyodide/gates.mjs';

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

test('tüm koşullar sağlanınca ON (sınır denetimi yok)', () => {
  const ev = cat();
  const mc = estimateMcMaxc(ev.map(e => e.mag));
  const r = evaluateGates({ events: ev, capped: false, limit: 500, xmeff: mc.mc, mcEst: mc });
  assert.equal(r.state, 'ON');
});

test('K1: sorgu sınırına takılan katalog → OFF; sınır kalkınca yeniden ON', () => {
  const ev = cat(); const mc = estimateMcMaxc(ev.map(e => e.mag));
  assert.equal(evaluateGates({ events: ev, capped: true, limit: 400, xmeff: mc.mc, mcEst: mc }).state, 'OFF');
  assert.equal(evaluateGates({ events: ev, capped: false, limit: 2000, xmeff: mc.mc, mcEst: mc }).state, 'ON');
});

test('K2: birden çok kaynak → OFF', () => {
  const ev = [...cat(200), ...cat(200, { src: 'ISC' }).map(e => ({ ...e, id: 'i' + e.id }))];
  const mc = estimateMcMaxc(ev.map(e => e.mag));
  const r = evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc });
  assert.equal(r.state, 'OFF'); assert.equal(status(r, 'K2'), 'fail');
});

test('K3: geçersiz alan oranı eşiği aşınca → OFF', () => {
  const ev = cat(); for (let i = 0; i < 40; i++) ev[i].dep = null;
  const mc = estimateMcMaxc(ev.map(e => e.mag));
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc }), 'K3'), 'fail');
});

test('K4: yinelenen kimlik → OFF', () => {
  const ev = cat(); ev[5].id = ev[4].id;
  const mc = estimateMcMaxc(ev.map(e => e.mag));
  assert.equal(status(evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc }), 'K4'), 'fail');
});

test('K5: Mc tahmin edilemezse ya da xmeff tahminin altındaysa → OFF; tahmin ile seçim ayrı yazılır', () => {
  const ev = cat();
  const mc = estimateMcMaxc(ev.map(e => e.mag));
  const low = evaluateGates({ events: ev, capped: false, xmeff: mc.mc - 0.3, mcEst: mc });
  assert.equal(status(low, 'K5'), 'fail');
  const d = low.checks.find(c => c.id === 'K5').detail;
  assert.match(d, /Mc \(tahmin/); assert.match(d, /xmeff \(seçim\)/);
  const none = evaluateGates({ events: ev.slice(0, 10), capped: false, xmeff: 3.0, mcEst: estimateMcMaxc(ev.slice(0, 10).map(e => e.mag)) });
  assert.equal(status(none, 'K5'), 'fail');
});

test('K6: M ≥ xmeff olay sayısı yetersiz → OFF', () => {
  const ev = cat(); const mc = estimateMcMaxc(ev.map(e => e.mag));
  const r = evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, opts: { minN: 10000 } });
  assert.equal(status(r, 'K6'), 'fail'); assert.equal(r.state, 'OFF');
});

test('K7/K8: sınır ve karışık ölçek yalnız uyarı (ON_WARN), hesabı durdurmaz', () => {
  const ev = cat(); ev[0].mtype = 'mw';
  const mc = estimateMcMaxc(ev.map(e => e.mag));
  const r = evaluateGates({ events: ev, capped: false, xmeff: mc.mc, mcEst: mc, region: { type: 'circle', lat: 39.5, lon: 32.5, rKm: 60 } });
  assert.equal(r.state, 'ON_WARN'); assert.equal(status(r, 'K7'), 'warn'); assert.equal(status(r, 'K8'), 'warn');
});

test('etkileşim ölçeği: 10·0.011·10^(0.4M)', () => {
  assert.ok(Math.abs(interactionKm(5) - 11) < 1e-9);
});
