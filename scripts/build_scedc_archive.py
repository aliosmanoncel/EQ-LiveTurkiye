#!/usr/bin/env python3
"""SCEDC SCSN yıllık katalog dosyalarından EQ-Live statik arşivi oluşturur (yalnız standart kütüphane).

Kullanım:
  python3 scripts/build_scedc_archive.py --raw-dir <klasör> --snapshot 2026-11-18 \
      --downloaded '{"2009": "2026-11-18T19:22:30Z", ...}' [--partial 2026]

Kurallar (data/scedc/README.md):
- Ham dosya bayt bayt korunur (gzip, mtime=0 → deterministik); özgün dosyanın SHA-256'sı kaydedilir.
- İşlenmiş CSV, ham alanların METNİNİ aynen taşır (sayıya çevirip yeniden yazma yok → yuvarlama olamaz).
- Bir anlık görüntü (snapshot) yazıldıktan sonra dosyaları değiştirilmez/silinmez; yeni veri yeni anlık görüntüdür.
"""
import argparse, glob, gzip, hashlib, io, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'scedc')
COLS = ['id', 'time_utc', 'lat', 'lon', 'depth_km', 'mag', 'mag_type', 'event_type', 'geo_type', 'quality', 'nph', 'ngrm']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def gz(b):
    buf = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=buf, compresslevel=9, mtime=0) as g:
        g.write(b)
    return buf.getvalue()


def parse_raw(text):
    """Ham SCEDC satırları → (satırlar, altbilgi sayısı). Alanlar metin olarak döner."""
    rows = []
    for l in text.splitlines():
        if not l[:4].isdigit():
            continue
        p = l.split()
        if len(p) != 13:
            raise ValueError(f'13 alan bekleniyordu: {l!r}')
        D, T, ET, GT, MAG, M, LAT, LON, DEP, Q, EVID, NPH, NGRM = p
        rows.append([EVID, D.replace('/', '-') + 'T' + T, LAT, LON, DEP, MAG, M, ET, GT, Q, NPH, NGRM])
    m = re.search(r'Number of rows returned:\s*(\d+)', text)
    return rows, (int(m.group(1)) if m else None)


def to_csv(rows):
    out = io.StringIO()
    out.write(','.join(COLS) + '\n')
    for r in rows:
        out.write(','.join(r) + '\n')
    return out.getvalue().encode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-dir', required=True)
    ap.add_argument('--snapshot', required=True, help='anlık görüntü kimliği = indirme tarihi (YYYY-MM-DD)')
    ap.add_argument('--downloaded', default='{}', help='yıl → indirme zamanı (UTC, JSON)')
    ap.add_argument('--partial', nargs='*', type=int, default=[], help='tamamlanmamış yıllar')
    a = ap.parse_args()
    dl = json.loads(a.downloaded)

    man_path = os.path.join(ROOT, 'manifest.json')
    man = json.load(open(man_path, encoding='utf-8'))
    if any(s['id'] == a.snapshot for s in man['snapshots']):
        sys.exit(f'Anlık görüntü {a.snapshot} zaten var; var olan anlık görüntüler değiştirilmez.')

    raw_out = os.path.join(ROOT, 'raw', a.snapshot)
    csv_out = os.path.join(ROOT, 'scsn', a.snapshot)
    os.makedirs(raw_out, exist_ok=True)
    os.makedirs(csv_out, exist_ok=True)

    files = []
    for f in sorted(glob.glob(os.path.join(a.raw_dir, '20*.txt'))):
        y = int(os.path.basename(f)[:4])
        b = open(f, 'rb').read()
        rows, foot = parse_raw(b.decode('ascii'))
        if foot != len(rows):
            sys.exit(f'{f}: satır {len(rows)} ≠ altbilgi {foot}')
        years = {r[1][:4] for r in rows}
        if years != {str(y)}:
            sys.exit(f'{f}: beklenmeyen yıllar {years}')
        rgz = gz(b)
        csv = to_csv(rows)
        cgz = gz(csv)
        rp = f'raw/{a.snapshot}/{y}.catalog.gz'
        cp = f'scsn/{a.snapshot}/scsn_{y}.csv.gz'
        open(os.path.join(ROOT, rp), 'wb').write(rgz)
        open(os.path.join(ROOT, cp), 'wb').write(cgz)
        files.append(dict(
            year=y, status='partial' if y in a.partial else 'complete',
            first_event=min(r[1] for r in rows), last_event=max(r[1] for r in rows),
            downloaded_utc=dl.get(str(y)), source_file=os.path.basename(f),
            raw=dict(path=rp, sha256_original=sha(b), bytes_original=len(b), sha256_gz=sha(rgz)),
            processed=dict(path=cp, rows=len(rows), sha256_csv=sha(csv), sha256_gz=sha(cgz)),
            footer_rows=foot))
        print(y, len(rows), files[-1]['status'], file=sys.stderr)

    man['snapshots'].append(dict(id=a.snapshot, files=files))
    for f in files:                      # her yıl için geçerli (önerilen) anlık görüntü
        man['current'][str(f['year'])] = a.snapshot
    json.dump(man, open(man_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(man_path, 'a').write('\n')


if __name__ == '__main__':
    main()
