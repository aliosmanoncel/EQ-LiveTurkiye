#!/usr/bin/env python3
"""EQ-Live SCEDC statik arşivi doğrulaması (yalnız standart kütüphane; ağ gerekmez).

Kullanım: python3 scripts/validate_scedc_archive.py [--base-manifest eski_manifest.json] [--json rapor.json]

Kontroller (her anlık görüntü, her yıl):
 1. Sıkıştırılmış ham ve işlenmiş dosyaların SHA-256'sı manifestle aynı.
 2. Açılmış ham dosya = özgün indirilen dosya (sha256_original, bayt sayısı).
 3. Ham veri satırı sayısı = SCEDC altbilgisi = işlenmiş satır sayısı.
 4. İşlenmiş CSV, ham dosyadan alan alan (metin olarak) birebir üretilebiliyor.
 5. Tüm olaylar dosyanın yılına ait; olay kimlikleri yıl içinde tekil; zaman biçimi 0,01 s.
 6. data/scedc altında manifestte olmayan veri dosyası yok; 'current' var olan anlık görüntüleri gösteriyor.
 7. (--base-manifest) Önceki anlık görüntüler değiştirilmemiş/silinmemiş (değişmezlik).
"""
import argparse, datetime, gzip, hashlib, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'scedc')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scedc_archive import parse_raw, to_csv  # aynı ayrıştırıcı: üretim ve doğrulama tek tanım

TIME = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{2}$')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-manifest')
    ap.add_argument('--json')
    a = ap.parse_args()
    man = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
    errors, report = [], {'snapshots': {}}

    listed = set()
    for snap in man['snapshots']:
        srep = {}
        for f in snap['files']:
            y, e = f['year'], []
            rp, cp = os.path.join(ROOT, f['raw']['path']), os.path.join(ROOT, f['processed']['path'])
            listed.update({os.path.normpath(rp), os.path.normpath(cp)})
            try:
                rgz, cgz = open(rp, 'rb').read(), open(cp, 'rb').read()
            except FileNotFoundError as x:
                errors.append(f'{snap["id"]}/{y}: dosya yok: {x.filename}'); continue
            if sha(rgz) != f['raw']['sha256_gz']: e.append('ham gz SHA-256 farklı')
            if sha(cgz) != f['processed']['sha256_gz']: e.append('işlenmiş gz SHA-256 farklı')
            try:
                raw, csv = gzip.decompress(rgz), gzip.decompress(cgz)
            except Exception as x:
                errors += [f'{snap["id"]}/{y}: {m}' for m in e + [f'gzip açılamadı: {x}']]
                srep[y] = dict(rows=0, footer=None, status=f['status'], ok=False, errors=e); continue
            if sha(raw) != f['raw']['sha256_original'] or len(raw) != f['raw']['bytes_original']:
                e.append('açılmış ham dosya özgün indirmeyle aynı değil')
            rows, foot = parse_raw(raw.decode('ascii'))
            if sha(csv) != f['processed']['sha256_csv']: e.append('işlenmiş CSV SHA-256 farklı')
            if not (len(rows) == foot == f['footer_rows'] == f['processed']['rows']):
                e.append(f'satır sayıları: ham {len(rows)}, altbilgi {foot}, manifest {f["footer_rows"]}/{f["processed"]["rows"]}')
            if to_csv(rows) != csv: e.append('işlenmiş CSV ham dosyadan alan alan üretilemiyor')
            lines = csv.decode('utf-8').splitlines()[1:]
            ids, badyear, badtime = set(), 0, 0
            for l in lines:
                c = l.split(',')
                ids.add(c[0])
                if c[1][:4] != str(y): badyear += 1
                if not TIME.match(c[1]): badtime += 1
                else:
                    try: datetime.datetime.strptime(c[1], '%Y-%m-%dT%H:%M:%S.%f')  # geçerli takvim zamanı
                    except ValueError: badtime += 1
                try:
                    la, lo = float(c[2]), float(c[3])
                    if not (-90 <= la <= 90 and -180 <= lo <= 180): badtime += 1
                except ValueError: badtime += 1
            if badyear: e.append(f'{badyear} olay başka yıla ait')
            if badtime: e.append(f'{badtime} olayın zaman/konum alanı geçersiz')
            if len(ids) != len(lines): e.append(f'{len(lines) - len(ids)} yinelenen olay kimliği')
            srep[y] = dict(rows=len(rows), footer=foot, status=f['status'], ok=not e, errors=e)
            errors += [f'{snap["id"]}/{y}: {x}' for x in e]
        report['snapshots'][snap['id']] = srep

    on_disk = set()
    for sub in ('raw', 'scsn'):
        for dp, _, fs in os.walk(os.path.join(ROOT, sub)):
            on_disk.update(os.path.normpath(os.path.join(dp, x)) for x in fs)
    orphans = sorted(os.path.relpath(p, ROOT) for p in on_disk - listed)
    if orphans: errors.append(f'manifestte olmayan dosyalar: {orphans}')
    ids = {s['id'] for s in man['snapshots']}
    for y, s in man['current'].items():
        if s not in ids: errors.append(f'current[{y}] = {s} var olan bir anlık görüntü değil')

    if a.base_manifest and os.path.exists(a.base_manifest):
        base = json.load(open(a.base_manifest, encoding='utf-8'))
        now = {s['id']: s for s in man['snapshots']}
        for s in base.get('snapshots', []):
            if s['id'] not in now: errors.append(f'anlık görüntü silinmiş: {s["id"]}')
            elif json.dumps(s, sort_keys=True) != json.dumps(now[s['id']], sort_keys=True):
                errors.append(f'anlık görüntü değiştirilmiş: {s["id"]}')
        report['immutability_checked_against'] = a.base_manifest

    report['total_rows'] = sum(v['rows'] for s in report['snapshots'].values() for v in s.values())
    report['errors'] = errors
    report['result'] = 'GEÇTİ' if not errors else 'BAŞARISIZ'
    if a.json: json.dump(report, open(a.json, 'w'), indent=1, ensure_ascii=False)
    for s, r in report['snapshots'].items():
        print(s, ' '.join(f'{y}:{v["rows"]}{"" if v["ok"] else "!"}' for y, v in r.items()))
    print('Toplam olay:', report['total_rows'])
    for x in errors: print('HATA:', x)
    print('SONUÇ:', report['result'])
    sys.exit(0 if not errors else 1)


if __name__ == '__main__':
    main()
