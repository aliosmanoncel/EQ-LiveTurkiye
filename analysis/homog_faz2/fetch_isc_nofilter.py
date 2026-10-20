"""
Faz 2 / seçenek (a) — 1904–1962 ISC Bulletin'i BÜYÜKLÜK SÜZGECİ OLMADAN çeker (yalnız analiz; üretim koduna dokunmaz).
Kaynak: ISC FDSN event servisi, format=xml (QuakeML), includeallmagnitudes=true; kutu 33–45° K, 23–48° D; yıllık dilimler.
Atıf: International Seismological Centre, On-line Bulletin, https://doi.org/10.31905/D808B830
Çıktı: analysis/homog_faz2/out/isc_1904_1962_nofilter.json — her olay için tercih edilen köken, tercih edilen büyüklük
ve TÜM büyüklükler (değer, tür, yazar). Her yıl için sorgu adresi, HTTP durumu ve olay sayısı ayrıca kaydedilir.
"""
import json, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
from datetime import datetime, timezone
B = dict(minlat=33.0, maxlat=45.0, minlon=23.0, maxlon=48.0)
URL = 'http://www.isc.ac.uk/fdsnws/event/1/query'
NS = {'q': 'http://quakeml.org/xmlns/bed/1.2'}
def t(el, path):
    x = el.find(path, NS); return x.text.strip() if x is not None and x.text else None
def main():
    events, log = [], []
    for y in range(1904, 1963):
        u = (f'{URL}?format=xml&includeallmagnitudes=true&starttime={y}-01-01T00:00:00&endtime={y + 1}-01-01T00:00:00'
             f'&minlat={B["minlat"]}&maxlat={B["maxlat"]}&minlon={B["minlon"]}&maxlon={B["maxlon"]}')
        st, raw = None, b''
        for k in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'EQ-LiveTurkiye homog-faz2'}), timeout=300) as r:
                    st, raw = r.status, r.read(); break
            except urllib.error.HTTPError as e:
                st = e.code
                if e.code == 204: break
                time.sleep(10 * (k + 1))
            except Exception as e:
                st = f'{type(e).__name__}: {e}'; time.sleep(10 * (k + 1))
        n = 0
        if raw:
            root = ET.fromstring(raw)
            for ev in root.iter('{http://quakeml.org/xmlns/bed/1.2}event'):
                pid = t(ev, 'q:preferredOriginID'); pmid = t(ev, 'q:preferredMagnitudeID')
                orgs = {o.get('publicID'): o for o in ev.findall('q:origin', NS)}
                o = orgs.get(pid) or (list(orgs.values())[0] if orgs else None)
                if o is None: continue
                mags = []
                for m in ev.findall('q:magnitude', NS):
                    v = t(m, 'q:mag/q:value')
                    mags.append({'id': m.get('publicID'), 'mag': float(v) if v else None, 'type': t(m, 'q:type'), 'author': t(m, 'q:creationInfo/q:author'),
                                 'origin': t(m, 'q:originID'), 'nsta': t(m, 'q:stationCount'), 'pref': m.get('publicID') == pmid})
                dep = t(o, 'q:depth/q:value')
                events.append({'id': ev.get('publicID').split('=')[-1], 'time': t(o, 'q:time/q:value'), 'lat': float(t(o, 'q:latitude/q:value')), 'lon': float(t(o, 'q:longitude/q:value')),
                               'dep_km': float(dep) / 1000 if dep else None, 'origin_author': t(o, 'q:creationInfo/q:author'), 'mags': mags})
                n += 1
        log.append({'year': y, 'url': u, 'status': st, 'n': n}); print(y, st, n, flush=True); time.sleep(2)
    json.dump({'meta': {'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'source': URL, 'box': B, 'params': 'format=xml&includeallmagnitudes=true; büyüklük süzgeci yok',
                        'citation': 'International Seismological Centre, On-line Bulletin, https://doi.org/10.31905/D808B830', 'log': log, 'n': len(events)}, 'events': events},
              open('analysis/homog_faz2/out/isc_1904_1962_nofilter.json', 'w'), ensure_ascii=False, separators=(',', ':'))
if __name__ == '__main__': main()
