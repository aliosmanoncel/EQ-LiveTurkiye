// site_donusum_parite.mjs — index.html'deki MAG_CONVERSIONS bloğunu (değiştirmeden) çalıştırıp
// EMSC olaylarının dispatch sonuçlarını yazar; olcek_homojenlestirme.py Python kopyasını bununla karşılaştırır.
// Kullanım: node analysis/2026-11-08_bagimsiz_olay_kimligi/site_donusum_parite.mjs <cikti.json>
import fs from 'node:fs';
const html = fs.readFileSync('index.html', 'utf8');
const a = html.indexOf('const TURKEY_REGIONAL_BBOX');
const b = html.indexOf('\n};', html.indexOf('const MAG_CONVERSIONS')) + 3;
const code = html.slice(a, b);
const MAG = new Function('panelBaseMag', code + '\nreturn MAG_CONVERSIONS;')(e => e.mag);
const ev = JSON.parse(fs.readFileSync('data/eq_historical.json', 'utf8')).events.filter(e => e.src === 'EMSC');
const KEYS = ['combined_dispatch', 'combined_dispatch_md_eqml', 'combined_dispatch_md'];
const out = {};
for (const k of KEYS) {
  const C = MAG[k];
  out[k] = ev.map(e => (C.applicable(e) ? C.convert(e) : null));
}
out.ids = ev.map(e => e.id);
fs.writeFileSync(process.argv[2], JSON.stringify(out));
console.log('blok', code.length, 'karakter; olay', ev.length);
