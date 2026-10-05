"""
gk74_context.py — GK74 BAGLAMLI ayiklama: DONMUS REFERANS DAVRANIS (Faz 1, 2026-10-06)

Bu modul, EQ-Live tarayicisindaki baglamli GK74'un (index.html:
gk74SelectContext / gk74Decluster(evList, ctxList)) dogrulama referansidir.
JS uygulamasi bu modulle AYNI sonucu uretmelidir (benzer degil, ayni).
Dogrulama: scripts/validate_gk74_parity.py --context

Kurallar (degistirilirse fixture yeniden dondurulmali ve not dusulmeli):
  * Pencere kurallari scripts/decluster_gk74.py ile BIREBIR aynidir
    (gk_window; yalniz artci; ileri pencere; isaretli olay pencere acmaz;
    M >= M_i olan olay artci sayilmaz; UTC, ms).
  * Hedef (target): daire ici olaylar, d <= R. Ciktiya yalnizca bunlar girer.
  * Baglam (context), iki kademe (daire merkezine uzaklik d):
      dar halka  : R < d <= R + 30 km,  M >= hedef sorgunun alt esigi (mmin)
      genis halka: R + 30 < d <= R + 90 km, M >= max(4.0, mmin)
      zaman      : [baslangic - 1100 gun, bitis]
    Gerekce: D(M) < 30,1 km (M < 4); D(7,8) = 88,8 km.
  * Tarama sirasi: hedef + baglam birlesik liste, zamana gore KARARLI
    siralama (hedefler once, sonra baglam; esit zamanda bu sira korunur).
  * Baglam olaylari pencere acar ve isaretlenebilir (isaretliyse pencere
    acmaz) ama ciktiya GIRMEZ.
  * Her olay icin gerekce kaydi: role (target|context), ring (null|dar|genis),
    status (kept|suppressed), by (isaretleyen olayin id'si), by_role.
"""
import hashlib, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decluster_gk74 import gk_window, haversine, parse_time_ms, event_mag, decluster  # noqa: E402

GK74_VERSION = 'gk74-ctx-frozen-2026-10-06'   # index.html GK74_VERSION ile ayni olmali
CTX_NARROW_KM = 30.0
CTX_WIDE_KM = 90.0
CTX_WIDE_MMIN = 4.0
CTX_PAD_DAYS = 1100.0
DAY_MS = 86400000


def _f(v):
    try:
        x = float(v); return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def select_context(events, lat, lon, radius_km, t_start_ms, t_end_ms, mmin=None, mag_field='mag', mag_fn=None):
    """Iki kademeli baglam secimi. Donus: [(olay, 'dar'|'genis'), ...] (girdi sirasi korunur)."""
    lo_t = t_start_ms - CTX_PAD_DAYS * DAY_MS
    m_dar = mmin if mmin is not None else -math.inf
    m_gen = max(CTX_WIDE_MMIN, m_dar)
    out = []
    for e in events:
        t = parse_time_ms(e.get('time')); m = mag_fn(e) if mag_fn else event_mag(e, mag_field)
        la, lo = _f(e.get('lat')), _f(e.get('lon'))
        if t is None or m is None or la is None or lo is None:
            continue
        if t < lo_t or t > t_end_ms:
            continue
        d = haversine(lat, lon, la, lo)
        if d <= radius_km:
            continue
        if d <= radius_km + CTX_NARROW_KM:
            if m >= m_dar:
                out.append((e, 'dar'))
        elif d <= radius_km + CTX_WIDE_KM:
            if m >= m_gen:
                out.append((e, 'genis'))
    return out


def decluster_with_context(target, context, mag_field='mag', mag_fn=None):
    # mag_fn (Faz 2a prototipi): verilirse buyukluk event_mag yerine ondan okunur; None = Faz 1 (donmus)
    """Donus: (kept_targets [zaman sirali], records [her olay icin gerekce kaydi, tarama sirasinda])."""
    items = [(e, 'target', None) for e in target] + [(e, 'context', r) for e, r in context]
    rows = []
    for e, role, ring in items:
        rows.append((e, role, ring, parse_time_ms(e.get('time')), mag_fn(e) if mag_fn else event_mag(e, mag_field),
                     _f(e.get('lat')), _f(e.get('lon'))))
    rows.sort(key=lambda r: (r[3] is None, r[3] if r[3] is not None else 0))
    n = len(rows); by = [None] * n
    for i in range(n):
        if by[i] is not None:
            continue
        e0, _, _, t0, m, la, lo = rows[i]
        if t0 is None or m is None or la is None or lo is None:
            continue
        T_days, D_km = gk_window(m); T_ms = T_days * DAY_MS
        for j in range(i + 1, n):
            _, _, _, tj, mj, laj, loj = rows[j]
            if tj is None or tj - t0 > T_ms:
                break
            if by[j] is not None or mj is None or not (mj < m) or laj is None or loj is None:
                continue
            if haversine(la, lo, laj, loj) <= D_km:
                by[j] = i
    recs, kept = [], []
    for k, r in enumerate(rows):
        b = by[k]
        rec = dict(id=r[0].get('id'), role=r[1], ring=r[2],
                   status='kept' if b is None else 'suppressed',
                   by=None if b is None else rows[b][0].get('id'),
                   by_role=None if b is None else rows[b][1])
        recs.append(rec)
        if r[1] == 'target' and b is None:
            kept.append(r[0])
    return kept, recs


def _sha(ids):
    return hashlib.sha256('\n'.join(sorted(ids)).encode('utf-8')).hexdigest()


def freeze(catalog, out, lat, lon, radius, start, mag_field, subset_out=None):
    raw = open(catalog, 'rb').read()
    cat = json.loads(raw.decode('utf-8')); allev = cat['events']
    if subset_out:
        # Kendi kendine yeten alt katalog: d <= R + 90 km, tum zamanlar. A ve B'yi
        # yeniden uretmek icin yeterlidir (baglam secimi bu halkanin disina bakmaz);
        # boylece fixture, data/eq_historical.json yeniden uretilse de gecerli kalir.
        sub = [e for e in allev if haversine(lat, lon, e['lat'], e['lon']) <= radius + CTX_WIDE_KM]
        sraw = json.dumps(dict(source=catalog, source_sha256=hashlib.sha256(raw).hexdigest(),
                               note=f'd <= R + {CTX_WIDE_KM:g} km alt kumesi (GK74 baglam fixture)', events=sub),
                          ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        open(subset_out, 'wb').write(sraw)
    ids = [e['id'] for e in allev]
    assert len(ids) == len(set(ids)), 'katalogda tekrarlanan id var'
    t0 = parse_time_ms(start)
    t_end = max(t for t in (parse_time_ms(e.get('time')) for e in allev) if t is not None)
    target = [e for e in allev if haversine(lat, lon, e['lat'], e['lon']) <= radius
              and parse_time_ms(e.get('time')) is not None and parse_time_ms(e['time']) >= t0]
    tid = set(e['id'] for e in target)
    mmin = min(event_mag(e, mag_field) for e in target)
    ctx = select_context(allev, lat, lon, radius, t0, t_end, mmin, mag_field)
    A, recA = decluster_with_context(target, [], mag_field)
    ev_ref, cl_ref = decluster(target, mag_field)
    assert set(e['id'] for e in A) == set(e['id'] for e, c in zip(ev_ref, cl_ref) if not c), 'A != decluster()'
    B, recB = decluster_with_context(target, ctx, mag_field)
    ev_g, cl_g = decluster(allev, mag_field)
    G = [e for e, c in zip(ev_g, cl_g) if not c and e['id'] in tid]
    idsA, idsB, idsG = [e['id'] for e in A], [e['id'] for e in B], [e['id'] for e in G]
    from collections import Counter
    reasons = Counter((r['role'], r['ring'], r['status'], r['by_role']) for r in recB)
    byid = {e['id']: e for e in allev}
    contrib = Counter(r['by'] for r in recB if r['role'] == 'target' and r['by_role'] == 'context')
    top_ctx = [dict(id=k, time=byid[k]['time'], mag=byid[k].get('mag'), mw=byid[k].get('mw'),
                    dist_km=round(haversine(lat, lon, byid[k]['lat'], byid[k]['lon']), 1), n_suppressed=v)
               for k, v in contrib.most_common(5)]
    fx = dict(
        frozen='2026-10-06', version=GK74_VERSION, module='scripts/gk74_context.py',
        catalog_subset=subset_out, catalog_subset_sha256=(hashlib.sha256(open(subset_out, 'rb').read()).hexdigest() if subset_out else None),
        rules=dict(narrow_km=CTX_NARROW_KM, wide_km=CTX_WIDE_KM, wide_mmin=CTX_WIDE_MMIN, pad_days=CTX_PAD_DAYS),
        catalog=catalog, catalog_sha256=hashlib.sha256(raw).hexdigest(), catalog_n=len(allev),
        params=dict(lat=lat, lon=lon, radius_km=radius, start=start, mag_field=mag_field, mmin=mmin,
                    t_end_ms=t_end),
        n_target=len(target), n_context=len(ctx),
        n_context_dar=sum(1 for _, r in ctx if r == 'dar'), n_context_genis=sum(1 for _, r in ctx if r == 'genis'),
        A=dict(n=len(idsA), sha256=_sha(idsA), ids=sorted(idsA)),
        B=dict(n=len(idsB), sha256=_sha(idsB), ids=sorted(idsB)),
        G=dict(n=len(idsG), sha256=_sha(idsG)),
        B_equals_G=set(idsB) == set(idsG),
        summary=dict(suppression_ratio_A=round(1 - len(idsA) / len(target), 4),
                     suppression_ratio_B=round(1 - len(idsB) / len(target), 4),
                     context_share_of_suppressed_B=round(sum(contrib.values()) / max(1, len(target) - len(idsB)), 4),
                     top_context=top_ctx),
        B_reason_counts=[dict(role=k[0], ring=k[1], status=k[2], by_role=k[3], n=v) for k, v in sorted(reasons.items(), key=str)],
        B_records=recB,
    )
    json.dump(fx, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return fx


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Baglamli GK74 referansini dondur')
    ap.add_argument('--catalog', default='data/eq_historical.json')
    ap.add_argument('--lat', type=float, default=37.74)
    ap.add_argument('--lon', type=float, default=36.10)
    ap.add_argument('--radius', type=float, default=50.0)
    ap.add_argument('--start', default='2012-01-20')
    ap.add_argument('--mag-field', choices=['mag', 'mw'], default='mag')
    ap.add_argument('--freeze', required=True, help='cikti fixture yolu')
    ap.add_argument('--subset', default=None, help='kendi kendine yeten alt katalog yolu (onerilen)')
    a = ap.parse_args()
    fx = freeze(a.catalog, a.freeze, a.lat, a.lon, a.radius, a.start, a.mag_field, a.subset)
    print(f"[{a.mag_field}] hedef {fx['n_target']} | baglam {fx['n_context']} (dar {fx['n_context_dar']}, genis {fx['n_context_genis']}) | "
          f"A {fx['A']['n']} | B {fx['B']['n']} | G {fx['G']['n']} | B==G {fx['B_equals_G']}")
    print(f"   A sha256 {fx['A']['sha256'][:16]}…  B sha256 {fx['B']['sha256'][:16]}…  katalog sha256 {fx['catalog_sha256'][:16]}…")
    sm = fx['summary']
    print(f"   ayiklama orani A {sm['suppression_ratio_A']:.3f} | B {sm['suppression_ratio_B']:.3f} | B'de baglamin payi {sm['context_share_of_suppressed_B']:.3f}")
    for t in sm['top_context']: print(f"   baglam katkisi: {t['time'][:16]} M{t['mag']} ({t['dist_km']} km) -> {t['n_suppressed']}")
