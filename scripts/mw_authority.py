"""
mw_authority.py — Faz 2a PROTOTIP (2026-10-06): buyuk depremler icin otoriter Mw.

Kural (data/mw_authority.json):
  * Yalniz status == 'verified' kayitlar kullanilir.
  * Eslesme BUYUKLUKLE yapilmaz, olay kimligiyle yapilir:
      1. kaynak olay kimligi (e['eid'] == source_event_id), yoksa
      2. |dt| <= 60 s ve uzaklik <= 50 km; en kucuk |dt|, esitlikte en kucuk uzaklik.
    Her tablo kaydi verilen listede EN COK BIR olayla eslesir (ayni dakikadaki
    bir artci yanlislikla Mw 7'ye cikarilmasin).
  * M_eff: eslesen olay icin otoriter Mw; digerleri icin event_mag(e, mag_field)
    (= tarayicidaki e.mw ?? e.mag ya da e.mag). Orta buyuklukteki olaylar DEGISMEZ.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decluster_gk74 import haversine, parse_time_ms, event_mag  # noqa: E402

DEFAULT_TABLE = 'data/mw_authority.json'


def load_table(path=DEFAULT_TABLE):
    T = json.load(open(path, encoding='utf-8'))
    ents = [e for e in T['entries'] if e.get('status') == 'verified']
    for e in ents:
        e['_t'] = parse_time_ms(e['time_utc'])
    return T, ents


def build_override(events, entries, dt_s=60, dist_km=50):
    """Donus: {id(olay): kayit}. Her kayit en cok bir olaya atanir."""
    out = {}
    for ent in entries:
        best = None
        for e in events:
            if ent.get('source_event_id') and e.get('eid') == ent['source_event_id']:
                best = (-1, 0.0, e); break
            t = parse_time_ms(e.get('time'))
            if t is None or e.get('lat') is None or e.get('lon') is None:
                continue
            d_t = abs(t - ent['_t']) / 1000.0
            if d_t > dt_s:
                continue
            d = haversine(ent['lat'], ent['lon'], e['lat'], e['lon'])
            if d > dist_km:
                continue
            key = (d_t, d)
            if best is None or key < best[:2]:
                best = (d_t, d, e)
        if best is not None:
            out[id(best[2])] = ent
    return out


def make_mag_fn(events, entries, mag_field='mag'):
    ov = build_override(events, entries)
    def mag_fn(e):
        ent = ov.get(id(e))
        return ent['mw'] if ent is not None else event_mag(e, mag_field)
    mag_fn.override = ov
    return mag_fn
