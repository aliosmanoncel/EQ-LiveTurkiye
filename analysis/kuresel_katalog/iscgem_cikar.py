"""
ISC-GEM v12.1 ham CSV'lerinden tarayıcıda ve ölçüm betiklerinde kullanılacak sıkıştırılmış çıkarımı üretir ve doğrular.
Ölçüm 2 / aşama 1 (2026-10-26). Ham zip/CSV depoya KONMAZ; yalnız bu betik ve çıktısı.

Kullanım:
  python analysis/kuresel_katalog/iscgem_cikar.py <isc-gem-cat.csv> <isc-gem-suppl.csv> [--zip isc-gem.zip]

Çıktılar (analysis/kuresel_katalog/out/):
  iscgem_v12.1_ana.json.gz   ana katalog  (varsayılan olarak kullanılan küme)
  iscgem_v12.1_ek.json.gz    ek katalog (Supplement) — AYRI tutulur, varsayılan olarak hiçbir analize girmez
  iscgem_dogrulama.json      doğrulama raporu (sayılar, aralıklar, eksik alanlar, kimlik çakışmaları, özet değerleri)

Şema: {"meta": {...}, "alanlar": [...], "olaylar": [[...], ...]}; her olay alanlar sırasıyla bir dizi.
Eksik değer: null (CSV'de boş). Değerler tahminle DOLDURULMAZ.
Alanlar: t (ISO-8601 UTC), lat, lon, dep (km), dep_unc, mw, mw_unc, mw_q (A/B/C), mw_s (d = doğrudan M0, p = vekil),
         loc_q (A/B/C), dep_q, eventid (ISC-GEM olay kimliği, tam sayı).
"""
import csv, gzip, hashlib, json, math, sys, collections, os

BEKLENEN = {   # 2026-10-21 kaydı (analysis/homog_faz1/out/LISANS_ISC-GEM.txt, homog-faz0 dalı)
    'isc-gem.zip': '92a52fb933594f0c99f76c96c16fb6a04a360980283e7e22483b587f502949c5',
    'isc-gem-cat.csv': 'b4e63841e8a6527f1fa6a0ea823b83cfc5b053ab1c7d8746446e34645592cc8d',
    'isc-gem-suppl.csv': '1ea390ab6fc319746e7799bf08ea543d2e747dea64f5ba937ac61b481b0f21bf'}
SUTUN = ['date', 'lat', 'lon', 'smajax', 'sminax', 'strike', 'q_loc', 'depth', 'unc_dep', 'q_dep', 'mw', 'unc_mw', 'q_mw', 's_mw', 'mo', 'fac',
         'mo_auth', 'mpp', 'mpr', 'mrr', 'mrt', 'mtp', 'mtt', 'str1', 'dip1', 'rake1', 'str2', 'dip2', 'rake2', 'type', 'eventid']
ALANLAR = ['t', 'lat', 'lon', 'dep', 'dep_unc', 'mw', 'mw_unc', 'mw_q', 'mw_s', 'loc_q', 'dep_q', 'eventid']
ZORUNLU = ['t', 'lat', 'lon', 'mw', 'eventid']
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def num(s):
    s = s.strip()
    if s == '': return None
    v = float(s); return v if math.isfinite(v) else None

def oku(p):
    bas = [l for l in open(p, encoding='utf-8', errors='strict') if l.startswith('#')]
    surum = next((l[1:].strip() for l in bas if l.startswith('# Version') and 'released' in l.lower()), None)
    satirlar = [l for l in open(p, encoding='utf-8') if not l.startswith('#') and l.strip()]
    olaylar, hatalar = [], []
    for i, r in enumerate(csv.reader(satirlar)):
        r = [c.strip() for c in r]
        if len(r) != len(SUTUN): hatalar.append({'satir': i, 'neden': f'{len(r)} sütun (beklenen {len(SUTUN)})'}); continue
        d = dict(zip(SUTUN, r))
        t = d['date'].replace(' ', 'T') + 'Z' if d['date'] else None
        olaylar.append([t, num(d['lat']), num(d['lon']), num(d['depth']), num(d['unc_dep']), num(d['mw']), num(d['unc_mw']),
                        d['q_mw'] or None, d['s_mw'] or None, d['q_loc'] or None, d['q_dep'] or None, int(d['eventid']) if d['eventid'] else None])
    return surum, olaylar, hatalar

def dogrula(ad, olaylar):
    I = {a: i for i, a in enumerate(ALANLAR)}
    eksik = {a: sum(1 for e in olaylar if e[I[a]] is None) for a in ALANLAR}
    aralik = lambda a: [min(e[I[a]] for e in olaylar if e[I[a]] is not None), max(e[I[a]] for e in olaylar if e[I[a]] is not None)]
    gecersiz = {'lat': sum(1 for e in olaylar if e[1] is not None and not -90 <= e[1] <= 90), 'lon': sum(1 for e in olaylar if e[2] is not None and not -180 <= e[2] <= 180),
                'dep<0': sum(1 for e in olaylar if e[3] is not None and e[3] < 0), 'mw<=0': sum(1 for e in olaylar if e[5] is not None and e[5] <= 0)}
    kimlik = collections.Counter(e[11] for e in olaylar)
    ayni_kon = collections.Counter((e[0], e[1], e[2]) for e in olaylar)
    sirali = all(olaylar[i][0] <= olaylar[i + 1][0] for i in range(len(olaylar) - 1))
    on_yil = collections.Counter(int(e[0][:3]) * 10 for e in olaylar)
    kaynak = collections.Counter((int(e[0][:4]) < 1964 and '1904–1963' or int(e[0][:4]) < 1980 and '1964–1979' or '1980–2021', e[8]) for e in olaylar)
    def yuzdelik(a, b):
        m = sorted(e[5] for e in olaylar if a <= int(e[0][:4]) < b and e[5] is not None)
        return {'N': len(m), 'en_kucuk': m[0], 'p05': m[len(m) // 20], 'p50': m[len(m) // 2]} if m else None
    return {'ad': ad, 'olay': len(olaylar), 'ilk': olaylar[0][0], 'son': olaylar[-1][0], 'zamana_gore_sirali': sirali,
            'eksik_deger': eksik, 'zorunlu_alan_eksik': {a: eksik[a] for a in ZORUNLU},
            'aralik': {a: aralik(a) for a in ['lat', 'lon', 'dep', 'mw', 'mw_unc']}, 'gecersiz_deger': gecersiz,
            'yinelenen_eventid': sum(1 for k, v in kimlik.items() if v > 1), 'ayni_zaman_ve_konum': sum(1 for v in ayni_kon.values() if v > 1),
            'on_yillara_gore': dict(sorted(on_yil.items())), 'mw_kaynagi_doneme_gore': {f'{k[0]} {k[1]}': v for k, v in sorted(kaynak.items(), key=str)},
            'mw_q': dict(collections.Counter(e[7] for e in olaylar)),
            'mw_yuzdelik': {f'{a}–{b - 1}': yuzdelik(a, b) for a, b in [(1904, 1940), (1940, 1964), (1964, 1976), (1976, 1980), (1980, 2019), (2019, 2022)]}}

def yaz(ad, meta, olaylar):
    p = os.path.join(OUT, ad); veri = json.dumps({'meta': meta, 'alanlar': ALANLAR, 'olaylar': olaylar}, ensure_ascii=False, separators=(',', ':')).encode()
    with gzip.GzipFile(p, 'wb', mtime=0) as g: g.write(veri)   # mtime=0: aynı girdi → bayt bayt aynı çıktı
    return {'dosya': ad, 'bayt_gz': os.path.getsize(p), 'bayt_json': len(veri), 'sha256_gz': sha(p)}

def main():
    a = sys.argv[1:]; zp = a[a.index('--zip') + 1] if '--zip' in a else None; a = [x for x in a if x not in ('--zip', zp)]
    cat, sup = a[0], a[1]; os.makedirs(OUT, exist_ok=True)
    girdi = {'isc-gem-cat.csv': sha(cat), 'isc-gem-suppl.csv': sha(sup)}
    if zp: girdi['isc-gem.zip'] = sha(zp)
    uyum = {k: v == BEKLENEN[k] for k, v in girdi.items()}
    if not all(uyum.values()): sys.exit(f'SHA-256 uyuşmuyor: {uyum}')
    s1, ana, h1 = oku(cat); s2, ek, h2 = oku(sup)
    ortak = set(e[11] for e in ana) & set(e[11] for e in ek)
    meta = {'kaynak': 'ISC-GEM Global Instrumental Earthquake Catalogue', 'surum': s1, 'lisans': 'CC BY-SA 3.0 (unported)',
            'telif': '© International Seismological Centre and GEM Foundation',
            'atif': 'International Seismological Centre (2025), ISC-GEM Earthquake Catalogue, https://doi.org/10.31905/D808B825',
            'girdi_sha256': {k: v for k, v in girdi.items() if k.endswith('.csv')}, 'uretici': 'analysis/kuresel_katalog/iscgem_cikar.py', 'eksik_deger': 'null (tahminle doldurulmaz)'}
    c1 = yaz('iscgem_v12.1_ana.json.gz', {**meta, 'kume': 'ana katalog'}, ana)
    c2 = yaz('iscgem_v12.1_ek.json.gz', {**meta, 'kume': 'ek katalog (Supplement) — varsayılan olarak kullanılmaz'}, ek)
    rapor = {'girdi_sha256': girdi, 'beklenenle_ayni': uyum, 'surum_ana': s1, 'surum_ek': s2, 'okunamayan_satir': {'ana': h1, 'ek': h2},
             'ana': dogrula('ana', ana), 'ek': dogrula('ek', ek), 'ana_ve_ekte_ortak_eventid': len(ortak), 'cikti': [c1, c2]}
    json.dump(rapor, open(os.path.join(OUT, 'iscgem_dogrulama.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: rapor[k] for k in ('beklenenle_ayni', 'surum_ana', 'okunamayan_satir', 'ana_ve_ekte_ortak_eventid', 'cikti')}, ensure_ascii=False, indent=1))
    for k in ('ana', 'ek'): r = rapor[k]; print(k, r['olay'], r['ilk'], r['son'], 'sıralı', r['zamana_gore_sirali'], 'zorunlu eksik', r['zorunlu_alan_eksik'], 'geçersiz', r['gecersiz_deger'], 'yinelenen kimlik', r['yinelenen_eventid'], 'aynı zaman+konum', r['ayni_zaman_ve_konum'])

if __name__ == '__main__': main()
