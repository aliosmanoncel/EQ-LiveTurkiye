"""
Ölçüm 2 — ISC-GEM v12.1 ana katalog ile USGS ComCat karşılaştırması. Kurallar: OLCUM_2_ONKAYIT.md (sonuçlardan önce kaydedildi).

Kullanım:
  python olcum2_usgs.py indir   <usgs_onbellek.json.gz>                  # USGS'den 1904–2021, M ≥ 4,0, küresel (ağ gerekir)
  python olcum2_usgs.py esle    <usgs_onbellek.json.gz> [cikti.json]     # eşleştirme ve rapor (ağ gerekmez)
  python olcum2_usgs.py sina                                              # yapay veriyle iç denetim (ağ gerekmez)

USGS önbelleği depoya konmaz (büyük ve zamanla değişir); rapor, sorgu zamanını ve parça sayılarını içerir.
"""
import bisect, collections, gzip, json, math, os, re, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

DIZIN = os.path.dirname(os.path.abspath(__file__))
ISCGEM = os.path.join(DIZIN, 'out', 'iscgem_v12.1_ana.json.gz')
USGS = 'https://earthquake.usgs.gov/fdsnws/event/1/'
YIL0, YIL1, MINMAG = 1904, 2021, 4.0
# (yıl alt, yıl üst hariç, ΔT dakika, ΔR km) — OLCUM_2_ONKAYIT.md
PENCERE = [(1904, 1940, 200, 250), (1940, 1963, 10, 200), (1963, 1990, 2, 150), (1990, 2022, 0.5, 100)]
DONEM = [(1904, 1971, '1904–1970'), (1971, 1998, '1971–1997'), (1998, 2022, '1998–2021')]
MAGBIN = [(-99, 4.0, '<4,0'), (4.0, 5.0, '4,0–5,0'), (5.0, 5.5, '5,0–5,5'), (5.5, 6.0, '5,5–6,0'), (6.0, 99, '≥6,0')]

def ms(iso): return datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp() * 1000
def donem(y): return next(a for lo, hi, a in DONEM if lo <= y < hi)
def pencere(y): return next((dt * 60000, dr) for lo, hi, dt, dr in PENCERE if lo <= y < hi)
def uzaklik(a1, o1, a2, o2):
    r = math.pi / 180; d = math.sin((a2 - a1) * r / 2) ** 2 + math.cos(a1 * r) * math.cos(a2 * r) * math.sin((o2 - o1) * r / 2) ** 2
    return 2 * 6371.0 * math.asin(min(1, math.sqrt(d)))

# ── İndirme ─────────────────────────────────────────────────────────────────────────────────────────────────
def get(url, deneme=6):
    for k in range(deneme):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'EQ-Live olcum2 (github.com/aliosmanoncel/EQ-LiveTurkiye)'}), timeout=180) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 204: return 204, b''
            if e.code in (429, 500, 502, 503, 504) and k < deneme - 1: time.sleep(10 * (k + 1)); continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if k < deneme - 1: time.sleep(10 * (k + 1)); continue
            raise

def parca(t0, t1, kayit):
    q = f'starttime={t0}&endtime={t1}&minmagnitude={MINMAG}'
    n = int(get(USGS + 'count?' + q)[1]); time.sleep(1)
    if n >= 20000:   # böl
        a, b = ms(t0 + 'Z'), ms(t1 + 'Z'); m = datetime.fromtimestamp((a + b) / 2000, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        return parca(t0, m, kayit) + parca(m, t1, kayit)
    st, body = get(USGS + 'query?format=geojson&orderby=time-asc&limit=20000&' + q); time.sleep(1)
    f = json.loads(body)['features'] if st == 200 and body else []
    kayit.append({'baslangic': t0, 'bitis': t1, 'count': n, 'indirilen': len(f)})
    out = []
    for x in f:
        p, g = x['properties'], x['geometry']['coordinates']
        out.append([x['id'], p.get('ids'), p.get('sources'), p.get('net'), p['time'], g[1], g[0], g[2] if len(g) > 2 else None, p.get('mag'), p.get('magType'), p.get('type')])
    return out

def indir(yol):
    t_bas = datetime.now(timezone.utc).isoformat(); kayit, olay = [], []
    for y in range(YIL0, YIL1 + 1):
        olay += parca(f'{y}-01-01T00:00:00', f'{y + 1}-01-01T00:00:00', kayit)
        print(y, len(olay), flush=True)
    ham = len(olay); goruldu = set(); tekil = []
    for e in olay:   # parça sınırında aynı olay iki kez gelebilir
        if e[0] in goruldu: continue
        goruldu.add(e[0]); tekil.append(e)
    meta = {'kaynak': USGS, 'minmagnitude': MINMAG, 'donem': [YIL0, YIL1], 'sorgu_baslangic_utc': t_bas, 'sorgu_bitis_utc': datetime.now(timezone.utc).isoformat(),
            'parca_sayisi': len(kayit), 'count_eksik_indirilen': [k for k in kayit if k['count'] != k['indirilen']], 'ham_olay': ham, 'tekil_olay': len(tekil),
            'alanlar': ['id', 'ids', 'sources', 'net', 'time_ms', 'lat', 'lon', 'depth', 'mag', 'magType', 'type']}
    with gzip.open(yol, 'wt', encoding='utf-8') as g: json.dump({'meta': meta, 'parcalar': kayit, 'olaylar': tekil}, g, separators=(',', ':'))
    print(json.dumps({k: meta[k] for k in ('parca_sayisi', 'ham_olay', 'tekil_olay')}), 'eksik parça', len(meta['count_eksik_indirilen']))

# ── Köken ───────────────────────────────────────────────────────────────────────────────────────────────────
def koken(net, ids, sources):
    alan = ((ids or '') + ',' + (sources or '')).lower()
    if net and 'iscgem' in net.lower(): return 'iscgem_tercihli'
    if 'iscgem' in alan: return 'iscgem_katkili'
    if (ids or '').strip(',') or (sources or '').strip(','): return 'iscgem_katkisi_yok'
    return 'koken_belirsiz'

def mag_turu(t):
    t = (t or '').lower()
    return 'mw*' if t.startswith('mw') else 'mb' if t.startswith('mb') else 'ms' if t.startswith('ms') else 'diger'

def ozet(v):
    if not v: return {'N': 0}
    v = sorted(v); q = lambda p: v[min(len(v) - 1, int(p * (len(v) - 1) + 0.5))]
    return {'N': len(v), 'ortanca': round(q(0.5), 3), 'q25': round(q(0.25), 3), 'q75': round(q(0.75), 3)}

# ── Eşleştirme ──────────────────────────────────────────────────────────────────────────────────────────────
def esle(G, U):
    """G: ISC-GEM [(t_ms, lat, lon, mw, eventid, yil)], U: USGS [(t_ms, lat, lon, mag, magType, koken, id, ids, net, type)], zamana göre sıralı."""
    ut = [u[0] for u in U]
    aday_g = []                      # her ISC-GEM olayı için [(puan, u_index)]
    aday_u = collections.defaultdict(list)
    for gi, g in enumerate(G):
        dT, dR = pencere(g[5]); lo, hi = bisect.bisect_left(ut, g[0] - dT), bisect.bisect_right(ut, g[0] + dT); a = []
        for ui in range(lo, hi):
            u = U[ui]; r = uzaklik(g[1], g[2], u[1], u[2])
            if r <= dR: s = abs(u[0] - g[0]) / dT + r / dR; a.append((s, ui)); aday_u[ui].append((s, gi))
        a.sort(); aday_g.append(a)
    sinif, es = [], {}
    for gi, a in enumerate(aday_g):
        if not a: sinif.append('yalniz_iscgem'); continue
        ui = a[0][1]; enu = min(aday_u[ui])[1]
        if enu != gi: sinif.append('belirsiz'); continue
        sinif.append('tekil' if len(a) == 1 and len(aday_u[ui]) == 1 else 'karsilikli_cok_adayli'); es[gi] = ui
    return aday_g, aday_u, sinif, es

def rapor(G, U, aday_g, aday_u, sinif, es):
    R = {}
    for lo, hi, ad in DONEM:
        gi_d = [i for i, g in enumerate(G) if lo <= g[5] < hi]; ui_d = [i for i, u in enumerate(U) if lo <= datetime.fromtimestamp(u[0] / 1000, timezone.utc).year < hi]
        s = collections.Counter(sinif[i] for i in gi_d)
        sk = collections.defaultdict(collections.Counter)   # sınıf × eşleşen USGS kaydının kökeni
        for i in gi_d:
            if i in es: sk[sinif[i]][U[es[i]][5]] += 1
        ku = collections.Counter(U[i][5] for i in ui_d)
        yu = [i for i in ui_d if i not in aday_u]
        yu_tab = collections.Counter((next(b for a0, a1, b in MAGBIN if a0 <= U[i][3] < a1), mag_turu(U[i][4])) for i in yu)
        cift = [i for i in gi_d if len(aday_g[i]) >= 2]
        tani = collections.defaultdict(list)
        for i in gi_d:
            if sinif[i] == 'tekil': u = U[es[i]]; tani[mag_turu(u[4])].append(u[3] - G[i][3])
        kim = collections.Counter()
        for i in gi_d:
            idsx = None
            for j, (sc, ui) in enumerate(aday_g[i]):
                if re.search(r'(^|,)iscgem(sup)?%d(,|$)' % G[i][4], (U[ui][7] or '').lower()): idsx = ui; break
            if idsx is None: kim['kimlik_bagi_yok'] += 1
            elif es.get(i) == idsx: kim['kimlik_bagi_pencere_eslesmesiyle_ayni'] += 1
            else: kim['kimlik_bagi_farkli_aday_' + sinif[i]] += 1
        R[ad] = {'iscgem_olay': len(gi_d), 'usgs_olay': len(ui_d), 'iscgem_sinif': dict(s), 'iscgem_sinif_oran': {k: round(v / max(1, len(gi_d)), 4) for k, v in s.items()},
                 'eslesen_usgs_koken': {k: dict(v) for k, v in sk.items()}, 'usgs_koken_tum': dict(ku),
                 'yalniz_usgs': len(yu), 'yalniz_usgs_mag_x_tur': {f'{a} {b}': v for (a, b), v in sorted(yu_tab.items())},
                 'olasi_cift_kayit_iscgem_olayi': len(cift), 'olasi_cift_kayit_ornek': [{'iscgem_eventid': G[i][4], 'usgs': [U[ui][6] for _, ui in aday_g[i][:4]]} for i in cift[:5]],
                 'buyukluk_tanisi_tekil_usgs_eksi_mw': {k: ozet(v) for k, v in sorted(tani.items())}, 'kimlik_denetimi': dict(kim)}
    return R

def yukle_g():
    d = json.load(gzip.open(ISCGEM)); I = {a: i for i, a in enumerate(d['alanlar'])}
    return [(ms(e[I['t']]), e[I['lat']], e[I['lon']], e[I['mw']], e[I['eventid']], int(e[I['t']][:4])) for e in d['olaylar']], d['meta']

def yukle_u(yol):
    d = json.load(gzip.open(yol, 'rt', encoding='utf-8')); U = []
    for e in d['olaylar']:
        if e[4] is None or e[5] is None or e[6] is None or e[8] is None: continue
        U.append((e[4], e[5], e[6], e[8], e[9], koken(e[3], e[1], e[2]), e[0], e[1], e[3], e[10]))
    U.sort(key=lambda u: u[0]); return U, d['meta']

def calistir(yol, cikti):
    G, gm = yukle_g(); U, um = yukle_u(yol); t0 = time.time()
    a_g, a_u, s, es = esle(G, U); R = rapor(G, U, a_g, a_u, s, es)
    netler = collections.Counter(u[8] for u in U); onek = collections.Counter()
    for u in U:
        for k in set(re.findall(r'[a-z]+', (u[7] or '').lower())): onek[k] += 1
    tur = collections.Counter(u[9] for u in U)
    out = {'onkayit': 'analysis/kuresel_katalog/OLCUM_2_ONKAYIT.md', 'iscgem_meta': {k: gm[k] for k in ('surum', 'girdi_sha256')}, 'usgs_meta': um,
           'usgs_net_dagilimi': dict(netler.most_common()), 'usgs_ids_katalog_onekleri': dict(onek.most_common(40)), 'usgs_olay_turleri': dict(tur.most_common()),
           'donemler': R, 'sure_s': round(time.time() - t0, 1)}
    json.dump(out, open(cikti, 'w'), ensure_ascii=False, indent=1)
    for k, v in R.items(): print(k, 'ISC-GEM', v['iscgem_olay'], v['iscgem_sinif'], '| USGS', v['usgs_olay'], 'yalnız USGS', v['yalniz_usgs'], '| kimlik', v['kimlik_denetimi'])

# ── İç denetim (yapay veri) ─────────────────────────────────────────────────────────────────────────────────
def sina():
    import random; rnd = random.Random(7); ok = fail = 0
    def chk(c, m):
        nonlocal ok, fail; ok += c; fail += (not c); print(('  ok  ' if c else '  !!  ') + m)
    G, _ = yukle_g(); G = [g for g in G if g[5] in (1930, 1950, 1975, 2005)]
    U = []
    for g in G:   # her ISC-GEM olayına bir USGS kaydı, pencerenin yarısı içinde kaydırılmış
        dT, dR = pencere(g[5]); dt = rnd.uniform(-0.4, 0.4) * dT; dlat = rnd.uniform(-0.3, 0.3) * dR / 111.19
        U.append((g[0] + dt, g[1] + dlat, g[2], g[3] - 0.3, 'mb', 'iscgem_katkisi_yok', f'us{g[4]}', f',us{g[4]},iscgem{g[4]},', 'us', 'earthquake'))
    n_g = len(G); k = G[5]; dT, dR = pencere(k[5])
    U.append((k[0] + 0.1 * dT, k[1], k[2], 5.0, 'mb', 'koken_belirsiz', 'dup1', '', 'xx', 'earthquake'))       # olası çift kayıt
    U.append((k[0] + 3 * dT, k[1], k[2], 6.1, 'ms', 'koken_belirsiz', 'uzak1', '', 'xx', 'earthquake'))       # pencere dışı → yalnız USGS
    U.sort(key=lambda u: u[0]); a_g, a_u, s, es = esle(G, U); c = collections.Counter(s)
    chk(c['yalniz_iscgem'] == 0, f'her ISC-GEM olayı bir aday buldu ({n_g} olay; sınıflar {dict(c)})')
    chk(len(a_g[5]) == 2 and s[5] in ('karsilikli_cok_adayli', 'belirsiz'), f'çift kayıt: iki aday, sınıf {s[5]} (tekil değil)')
    R = rapor(G, U, a_g, a_u, s, es)
    chk(sum(v['yalniz_usgs'] for v in R.values()) >= 1, 'pencere dışı USGS olayı yalnız USGS sayıldı')
    kim = collections.Counter(); [kim.update(v['kimlik_denetimi']) for v in R.values()]
    chk(kim['kimlik_bagi_pencere_eslesmesiyle_ayni'] >= n_g - 2, f'kimlik bağı pencere eşleşmesiyle tutarlı: {dict(kim)}')
    t = [v['buyukluk_tanisi_tekil_usgs_eksi_mw'].get('mb', {}).get('ortanca') for v in R.values()]
    chk(all(x is None or abs(x + 0.3) < 1e-6 for x in t), f'büyüklük tanısı −0,3 (yapay kaydırma): {t}')
    G2 = [(0.0, 0.0, 0.0, 6.0, 1, 1950)]; dT2, dR2 = pencere(1950)
    U2 = [(0.5 * dT2, 0.0, 0.0, 6.0, 'mw', 'x', 'a', '', 'x', 'e'), (dT2 * 1.01, 0.0, 0.0, 6.0, 'mw', 'x', 'b', '', 'x', 'e')]
    chk(esle(G2, U2)[2] == ['tekil'], 'ΔT sınırının dışındaki olay aday sayılmaz')
    U3 = [(0.0, (dR2 * 1.01) / 111.19, 0.0, 6.0, 'mw', 'x', 'a', '', 'x', 'e')]
    chk(esle(G2, U3)[2] == ['yalniz_iscgem'], 'ΔR sınırının dışındaki olay aday sayılmaz')
    chk(koken('iscgem', ',iscgem1,', '') == 'iscgem_tercihli' and koken('us', ',us1,iscgem2,', ',us,iscgem,') == 'iscgem_katkili'
        and koken('us', ',us1,', ',us,') == 'iscgem_katkisi_yok' and koken('us', '', None) == 'koken_belirsiz', 'köken sınıflaması')
    print(f'\n{"PASS" if not fail else "FAIL"}: {ok} geçti, {fail} kaldı'); sys.exit(1 if fail else 0)

if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    if k == 'indir': indir(sys.argv[2])
    elif k == 'esle':
        try: calistir(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.path.join(DIZIN, 'out', 'olcum2_sonuc.json'))
        except Exception:   # Actions günlükleri okunamayabilir: hata izi dala yazılsın
            import traceback; open(os.path.join(DIZIN, 'out', 'olcum2_hata.txt'), 'w').write(traceback.format_exc()); raise
    elif k == 'sina': sina()
    else: sys.exit(__doc__)
