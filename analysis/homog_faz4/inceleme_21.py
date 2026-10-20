"""1963–2021'de mevcut katalogda karşılığı olmayan ISC-GEM olaylarının olay bazında incelemesi (yalnız yerel veri; ekleme yapmaz).
Her olay için: ISC-GEM kaydı (zaman, konum, derinlik, Mw, kaynak, kalite); mevcut katalogda ±1 gün ve ≤ 300 km içindeki en yakın
aday (Δt, Δr, büyüklük, tür) ve kutu sınırına uzaklık. Sınıflama (önceden tanımlı):
  E1 'esik_disi_ayni_olay_olasi' : aday Δt ≤ 60 s ve Δr ≤ 150 km (Tablo 2 dışında kalan muhtemel aynı olay → ekleme değil aktarım konusu)
  E2 'katalogda_yok'             : ±1 gün/300 km içinde aday yok ya da aday Δt > 10 dk
  E3 'belirsiz'                  : diğerleri
  ayrıca 'kutu_siniri' bayrağı: sınıra ≤ 25 km."""
import json, math, importlib.util
s = importlib.util.spec_from_file_location('f3', 'analysis/homog_faz3/faz3_mw_aktarim.py'); F = importlib.util.module_from_spec(s); s.loader.exec_module(F)
L = {l['gem_id'] for l in json.load(open('analysis/homog_faz3/out/aktarim_kaydi.json'))}
alt = {a['alt_gem_id'] for a in json.load(open('analysis/homog_faz3/out/alternatif_buyuklukler.json'))}
G = [g for g in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if g['set'] == 'main' and g['mw'] is not None and 1963 <= int(g['date'][:4]) <= 2021 and g['eventid'] not in L and g['eventid'] not in alt]
A = json.load(open('data/eq_historical.json'))['events']
for e in A: e['_t'] = F.ts(e['time'])
def edge(g): return min((g['lat'] - 33) * 111.2, (45 - g['lat']) * 111.2, (g['lon'] - 23) * 111.2 * math.cos(math.radians(g['lat'])), (48 - g['lon']) * 111.2 * math.cos(math.radians(g['lat'])))
rows = []
for g in sorted(G, key=lambda g: g['date']):
    t = F.ts(g['date']); c = [(abs(e['_t'] - t), F.hav({'lat': g['lat'], 'lon': g['lon']}, e), e) for e in A if abs(e['_t'] - t) <= 86400]
    c = [x for x in c if x[1] <= 300]; c.sort(key=lambda x: x[0] / 60 + x[1] / 100)
    n = c[0] if c else None
    cls = 'E2_katalogda_yok' if (n is None or n[0] > 600) else 'E1_esik_disi_ayni_olay_olasi' if (n[0] <= 60 and n[1] <= 150) else 'E3_belirsiz'
    rows.append({'gem_id': g['eventid'], 'tarih': g['date'], 'enlem': g['lat'], 'boylam': g['lon'], 'derinlik': g['depth'], 'Mw': g['mw'], 'kaynak': g['s_mw'], 'kalite': g['q_mw'],
                 'sinira_km': round(edge(g)), 'kutu_siniri': edge(g) <= 25,
                 'en_yakin_aday': ({'id': n[2]['id'], 'zaman': n[2]['time'], 'mag': n[2]['mag'], 'tur': n[2]['mtype'], 'kaynak': n[2]['src'], 'dt_s': round(n[0], 1), 'dr_km': round(n[1])} if n else None), 'sinif': cls})
json.dump(rows, open('analysis/homog_faz4/out/inceleme_21.json', 'w'), ensure_ascii=False, indent=1)
import collections; print(len(rows), collections.Counter(r['sinif'] for r in rows), 'kutu sınırı:', sum(r['kutu_siniri'] for r in rows))
for r in rows:
    a = r['en_yakin_aday']; print(r['tarih'][:19], r['enlem'], r['boylam'], r['derinlik'], r['Mw'], r['kaynak'] + r['kalite'], 'sınır', r['sinira_km'], '|', (f"{a['tur']} {a['mag']} {a['kaynak']} Δt={a['dt_s']}s Δr={a['dr_km']}km" if a else '—'), '|', r['sinif'])
