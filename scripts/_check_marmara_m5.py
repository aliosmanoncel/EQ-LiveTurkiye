import json
with open('data/eq_marmara_catalog.json', encoding='utf-8') as f:
    d = json.load(f)
ev = [e for e in d['events'] if e.get('mag',0)>=5.0]
ev.sort(key=lambda x: x['time'])
for e in ev:
    print(f"{e['time'][:10]}  M{e['mag']:.1f}  {e.get('place','')}  lat={e['lat']:.2f} lon={e['lon']:.2f}")
