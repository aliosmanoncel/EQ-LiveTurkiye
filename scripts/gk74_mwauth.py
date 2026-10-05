"""
gk74_mwauth.py — Faz 2a: baglamli GK74 + otoriter Mw. DONMUS REFERANS (Python), 2026-10-06.
JS'ye HENUZ TASINMADI; tasindiginda bu modulle AYNI sonucu uretmelidir.

Faz 1 (gk74_context.py) kurallarinin tumu aynen gecerlidir. Tek fark buyukluk:
  M_eff(e) = otoriter Mw   eger e, data/mw_authority.json'daki dogrulanmis bir kayitla eslesiyorsa
           = event_mag(e)  aksi halde (Faz 1 ile ayni: mag ya da mw ?? mag)
Eslesme (mw_authority.build_override): kaynak olay kimligi; yoksa |dt| <= 60 s ve <= 50 km,
en kucuk |dt| (esitlikte en kucuk uzaklik); her kayit en cok bir olayla eslesir.
Eslesme KAPSAMI: islenen liste. Baglam secimi icin aday havuzu (pool), ayiklama icin
hedef + secilen baglam birlesimi. M_eff hem pencerede (D, T) hem baglam esiklerinde kullanilir.
"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decluster_gk74 import haversine, parse_time_ms, event_mag  # noqa: E402
from gk74_context import select_context, decluster_with_context, _sha, CTX_WIDE_KM  # noqa: E402
from mw_authority import load_table, make_mag_fn  # noqa: E402

GK74_MWAUTH_VERSION = 'gk74-ctx-mwauth-2026-10-06'


def run(target, pool, lat, lon, radius, t0, t_end, mmin, entries, mag_field='mag'):
    fn_pool = make_mag_fn(pool, entries, mag_field)
    ctx = select_context(pool, lat, lon, radius, t0, t_end, mmin, mag_field, fn_pool)
    union = list(target) + [e for e, _ in ctx]
    fn_u = make_mag_fn(union, entries, mag_field)
    kept, recs = decluster_with_context(target, ctx, mag_field, fn_u)
    overridden = [dict(id=e['id'], role='target' if i < len(target) else 'context',
                       entry=fn_u.override[id(e)]['name'], catalog_mag=e.get('mag'), catalog_mtype=e.get('mtype'),
                       mw=fn_u.override[id(e)]['mw'])
                  for i, e in enumerate(union) if id(e) in fn_u.override]
    return ctx, kept, recs, overridden


def freeze(name, lat, lon, radius, start, subset_path, table_path, out, full_catalog='data/eq_historical.json', mag_field='mag'):
    sraw = open(subset_path, 'rb').read(); traw = open(table_path, 'rb').read()
    pool = json.loads(sraw.decode('utf-8'))['events']
    T, ents = load_table(table_path)
    t0 = parse_time_ms(start)
    full = json.load(open(full_catalog, encoding='utf-8'))['events']
    t_end = max(t for t in (parse_time_ms(e.get('time')) for e in full) if t is not None)
    target = [e for e in pool if haversine(lat, lon, e['lat'], e['lon']) <= radius
              and parse_time_ms(e.get('time')) is not None and parse_time_ms(e['time']) >= t0]
    mmin = min(event_mag(e, mag_field) for e in target)
    ctx, kept, recs, ovr = run(target, pool, lat, lon, radius, t0, t_end, mmin, ents, mag_field)
    ids = [e['id'] for e in kept]
    # Altin standart (tum katalog, otoriter Mw tum katalog uzerinde) — yalniz donma aninda
    fn_full = make_mag_fn(full, ents, mag_field)
    _, recG = decluster_with_context(full, [], mag_field, fn_full)
    tid = set(e['id'] for e in target)
    G = [r['id'] for r in recG if r['status'] == 'kept' and r['id'] in tid]
    fx = dict(frozen='2026-10-06', version=GK74_MWAUTH_VERSION, module='scripts/gk74_mwauth.py', name=name,
              mw_authority=table_path, mw_authority_version=T.get('version'), mw_authority_sha256=hashlib.sha256(traw).hexdigest(),
              catalog_subset=subset_path, catalog_subset_sha256=hashlib.sha256(sraw).hexdigest(),
              params=dict(lat=lat, lon=lon, radius_km=radius, start=start, mag_field=mag_field, mmin=mmin, t_end_ms=t_end),
              n_target=len(target), n_context=len(ctx), overridden=ovr,
              B=dict(n=len(ids), sha256=_sha(ids), ids=sorted(ids)), G=dict(n=len(G), sha256=_sha(G)),
              B_equals_G=set(ids) == set(G), B_records=recs)
    json.dump(fx, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return fx


if __name__ == '__main__':
    SITES = [('saimbeyli', 37.74, 36.10, 50, '2012-01-20'), ('adiyaman', 37.33, 38.86, 70, '1998-01-01'),
             ('izmit_dogu', 40.80, 30.60, 50, '1998-01-01'), ('van_bati', 38.75, 42.80, 50, '2005-01-01')]
    for name, lat, lon, R, start in SITES:
        fx = freeze(name, lat, lon, R, start, f'scripts/fixtures/gk74_ctx_{name}_catalog.json', 'data/mw_authority.json',
                    f'scripts/fixtures/gk74_mwauth_{name}_ref_mag.json')
        print(f"{name:11s} hedef {fx['n_target']} | baglam {fx['n_context']} | B {fx['B']['n']} | G {fx['G']['n']} | B==G {fx['B_equals_G']} | "
              f"gecersiz kilinan: {', '.join(o['entry'] + ' ' + str(o['catalog_mag']) + o['catalog_mtype'] + '->' + str(o['mw']) for o in fx['overridden']) or 'yok'}")
