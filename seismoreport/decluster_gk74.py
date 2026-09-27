"""
decluster_gk74.py
Gardner-Knopoff (1974) declustering.

Her buyuk olay (mainshock) etrafinda:
  - Zaman penceresi T(M) gun
  - Mesafe penceresi D(M) km
icindeki kucuk olaylar "aftershock" olarak isaretlenir (yalniz artci;
pencere yalnizca ILERI zamana acilir, oncu soklar ayiklanmaz).

Bu betik EQ-Live tarayicisindaki GK74 (index.html: gk74Window /
gk74Decluster) ile AYNI algoritmayi kullanir ve onun dogrulama referansidir:
  - Tum zamanlar UTC'dir. Saat dilimi belirtilmemis zamanlar UTC kabul edilir;
    bilgisayarin yerel saat dilimi / yaz saati sonucu ETKILEMEZ
    (2026-09-28 duzeltmesi: onceden naive datetime.timestamp() yerel saat
    kullaniyordu ve TR yaz saati donemlerinde pencere 1 saat kayiyordu).
  - Zaman cozunurlugu milisaniyedir (tarayicidaki JavaScript Date ile ayni;
    onceden saniyeye kirpiliyordu).
  - Olaylar cozumlenmis zamana gore (kararli) siralanir.
  - Islenmemis (isaretsiz) her olay kendi penceresini acar; isaretli olay
    pencere acmaz; M >= M_i olan olay artci sayilmaz.
  - Zamani/buyuklugu/koordinati gecersiz olay pencere acmaz ve cikarilmaz.

Referans:
  Gardner & Knopoff (1974) BSSA 64(5): 1363-1367

Kullanim:
  python scripts/decluster_gk74.py                       # varsayilan Marmara girdisi
  python scripts/decluster_gk74.py --input data/eq_historical.json \
         --output data/eq_historical_dc.json --mag-field mw
  --mag-field mw : tarayicidaki gibi e.mw ?? e.mag kullanilir.
"""

import argparse, json, math, sys
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INPUT  = 'data/eq_marmara_catalog.json'
OUTPUT = 'data/eq_marmara_declustered.json'

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def gk_window(m):
    """Gardner-Knopoff (1974) Tablo 1 penceresi."""
    if m >= 6.5:
        T_days = 10 ** (0.032 * m + 2.7389)
    else:
        T_days = 10 ** (0.5409 * m - 0.547)
    D_km = 10 ** (0.1238 * m + 0.983)
    return T_days, D_km


def haversine(la1, lo1, la2, lo2):
    R = 6371.0; r = math.pi / 180
    dl = (la2 - la1) * r; dlo = (lo2 - lo1) * r
    a = math.sin(dl/2)**2 + math.cos(la1*r) * math.cos(la2*r) * math.sin(dlo/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_time_ms(s):
    """ISO zamani -> UTC epoch milisaniye (int). Gecersizse None.

    Saat dilimi yoksa UTC kabul edilir; yerel saat dilimi hic kullanilmaz.
    Kesirli saniye milisaniyeye kirpilir (JavaScript Date ile ayni)."""
    if not s:
        return None
    s = str(s).strip().replace(' ', 'T')
    if s.endswith('Z') or s.endswith('z'):
        s = s[:-1] + '+00:00'
    # Kesirli saniyeyi 6 haneye tamamla/kirp (fromisoformat uyumu)
    try:
        date_part, _, rest = s.partition('T')
        if rest:
            tz = ''
            for sep in ('+', '-'):
                k = rest.rfind(sep)
                if k > 0:
                    tz = rest[k:]; rest = rest[:k]; break
            if '.' in rest:
                main, frac = rest.split('.', 1)
                rest = main + '.' + (frac + '000000')[:6]
            s = date_part + 'T' + rest + tz
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            dt = datetime.strptime(s[:10], '%Y-%m-%d')
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = dt - _EPOCH
    return (delta.days * 86400 + delta.seconds) * 1000 + delta.microseconds // 1000


def parse_time(s):
    """Geriye uyum: UTC epoch saniye (float) ya da None."""
    ms = parse_time_ms(s)
    return None if ms is None else ms / 1000.0


def _num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def event_mag(e, mag_field='mag'):
    """'mag' -> e['mag']; 'mw' -> e['mw'] varsa o, yoksa e['mag'] (tarayici: e.mw ?? e.mag)."""
    if mag_field == 'mw' and e.get('mw') is not None:
        return _num(e.get('mw'))
    return _num(e.get('mag'))


def decluster(events, mag_field='mag'):
    """GK74 (yalniz artci). Donus: (zaman sirali olaylar, artci bayraklari)."""
    rows = []
    for e in events:
        t = parse_time_ms(e.get('time'))
        rows.append((e, t, event_mag(e, mag_field), _num(e.get('lat')), _num(e.get('lon'))))
    # Kararli siralama; gecersiz zamanli olaylar sona
    rows.sort(key=lambda r: (r[1] is None, r[1] if r[1] is not None else 0))
    n = len(rows)
    cluster = [False] * n

    for i in range(n):
        if cluster[i]:
            continue  # zaten artci, mainshock degil
        _, t0, m, la, lo = rows[i]
        if t0 is None or m is None or la is None or lo is None:
            continue  # gecersiz olay pencere acmaz
        T_days, D_km = gk_window(m)
        T_ms = T_days * 86400000

        for j in range(i + 1, n):
            _, tj, mj, laj, loj = rows[j]
            if tj is None:
                break  # gecersiz zamanlilar sonda
            if tj - t0 > T_ms:
                break  # zaman sirali, kalan hepsi disinda
            if cluster[j]:
                continue
            if mj is None or not (mj < m):
                continue  # buyuk/esit olay artci sayilmaz
            if laj is None or loj is None:
                continue
            if haversine(la, lo, laj, loj) <= D_km:
                cluster[j] = True

    return [r[0] for r in rows], cluster


def main():
    ap = argparse.ArgumentParser(description='Gardner-Knopoff (1974) declustering (yalniz artci, UTC)')
    ap.add_argument('--input', default=INPUT)
    ap.add_argument('--output', default=OUTPUT)
    ap.add_argument('--mag-field', choices=['mag', 'mw'], default='mag',
                    help="'mag' (varsayilan) ya da 'mw' (e.mw ?? e.mag, tarayici ile ayni)")
    args = ap.parse_args()

    with open(args.input, encoding='utf-8') as f:
        data = json.load(f)

    events, cluster = decluster(data['events'], args.mag_field)
    n = len(events)
    print(f'[*] {n} olay yuklendi')

    main_events = [e for e, c in zip(events, cluster) if not c]
    removed     = sum(cluster)

    print(f'[*] Mainshock: {len(main_events)} | Artci: {removed} ({100*removed//max(n,1)}%)')

    # Yillara gore karsilastirma
    from collections import defaultdict
    by_year_all  = defaultdict(int)
    by_year_main = defaultdict(int)
    for e, c in zip(events, cluster):
        yr = int(str(e.get('time', '0000'))[:4] or 0)
        by_year_all[yr]  += 1
        if not c:
            by_year_main[yr] += 1
    for yr in sorted(by_year_all):
        print(f'  {yr}: {by_year_all[yr]:5d} → {by_year_main[yr]:5d}')

    out = {
        'generated'   : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'      : data.get('source', '') + ' | Declustered: Gardner-Knopoff (1974)',
        'method'      : 'Gardner-Knopoff (1974) | yalniz artci, ileri pencere | UTC, ms | mag_field=' + args.mag_field,
        'original_n'  : n,
        'main_n'      : len(main_events),
        'removed_n'   : removed,
        'count'       : len(main_events),
        'events'      : main_events,
    }
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'[OK] Kaydedildi: {args.output}')


if __name__ == '__main__':
    main()
