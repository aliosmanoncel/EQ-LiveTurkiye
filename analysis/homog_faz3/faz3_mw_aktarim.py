"""
Faz 3 — ISC-GEM Mw'nin 1904–2021 boyunca eşleşen olaylara aktarılması (PROTOTİP; üretim koduna, eq_historical.json'a,
GK74 koduna, mw_authority.json'a ve tamlık merdivenine dokunmaz).

Kurallar (önceden tanımlı):
 1. 1904–1962: ISC-GEM ana katalog birincil (karar: seçenek b). A'nın ISC-GEM ile eşleşen olayları ISC-GEM kaydıyla
    temsil edilir; A'nın eşleşmeyen olayları OLDUĞU GİBİ kalır (büyüklüğü değişmez).
 2. 1963–2021: A'nın olayları korunur; ISC-GEM ile eşleşen olaya ISC-GEM Mw atanır (ham mag/mtype saklanır).
    A'da karşılığı olmayan ISC-GEM olayları EKLENMEZ (yalnız sayılır).
 3. 2022–: değişmez.
 4. Eşleştirme: yalnız zaman–konum, Candia & Macedo (2026) Tablo 2 (ΔT dk / ΔR km: 1900–1940 200/250*, 1940–1963 10/200,
    1963–1990 2/150, 1990– 0,5/100; *1940 öncesi ΔR uyarlaması). Bire-bir: bir ISC-GEM olayı en çok bir A olayına
    atanır (en küçük Δt/ΔT + Δr/ΔR). Koruma: |M_A − Mw_ISC-GEM| > 1,0 ise aktarım yapılmaz, olay 'supheli_eslesme' olarak
    işaretlenir ve büyüklüğü değişmez — İSTİSNA (2026-10-21, kullanıcı onayı): Δt ≤ 10 s ve Δr ≤ 30 km ise ΔM
    aktarımı engellemez (mb doygunluğu / küçük Ms).
 5. Hiçbir olaya tahminî/dönüştürülmüş Mw atanmaz.
 mw_src: iscgem_direct | iscgem_proxy | catalog_native_mw | catalog_raw_<tür>
Doğrulama testleri ve süreklilik kontrolü sonunda; sonuç: out/faz3_rapor.json, değişen/eklenen kayıtlar: out/aktarim_kaydi.json.
"""
import bisect, collections, hashlib, json, math, sys
from datetime import datetime, timezone
sys.path.insert(0, 'scripts'); import decluster_gk74 as GK
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def ts(s): return datetime.fromisoformat(s.replace('Z', '').replace(' ', 'T').split('.')[0]).replace(tzinfo=timezone.utc).timestamp()
def hav(a, b):
    r = math.pi / 180; dl = (b['lat'] - a['lat']) * r; do = (b['lon'] - a['lon']) * r
    x = math.sin(dl / 2) ** 2 + math.cos(a['lat'] * r) * math.cos(b['lat'] * r) * math.sin(do / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
CM = [(1900, 1940, 200, 250), (1940, 1963, 10, 200), (1963, 1990, 2, 150), (1990, 3000, 0.5, 100)]
def thr(y): return next((dt, dr) for a, b, dt, dr in CM if a <= y < b)
def raw_src(e): return 'catalog_native_mw' if e.get('mw') is not None else 'catalog_raw_' + ((e.get('mtype') or '?').lower())
def main():
    A0 = json.load(open('data/eq_historical.json'))['events']
    G = [g for g in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if g['set'] == 'main' and g['mw'] is not None]
    A = [dict(e, _i=i, _t=ts(e['time']), _M=e['mw'] if e['mw'] is not None else e['mag']) for i, e in enumerate(A0)]
    for g in G: g['_t'] = ts(g['date'])
    Gs = sorted(G, key=lambda g: g['_t']); gt = [g['_t'] for g in Gs]
    # aday çiftler
    cand = []
    for e in A:
        y = int(e['time'][:4])
        if y > 2021: continue
        dtm, dr = thr(y); i0 = bisect.bisect_left(gt, e['_t'] - dtm * 60)
        for g in Gs[i0:]:
            if g['_t'] > e['_t'] + dtm * 60: break
            d = hav(e, g)
            if d <= dr: cand.append((abs(g['_t'] - e['_t']) / (dtm * 60) + d / dr, e['_i'], id(g), g, d))
    cand.sort(key=lambda c: c[0]); usedA, usedG, pairs = set(), set(), []
    for s, ia, ig, g, d in cand:                     # bire-bir açgözlü atama (en yakın önce)
        if ia in usedA or ig in usedG: continue
        usedA.add(ia); usedG.add(ig); pairs.append((ia, g, d, s))
    pa = {ia: (g, d) for ia, g, d, s in pairs}
    P, log, sus = [], [], []
    for e in A:
        y = int(e['time'][:4]); base = {k: e[k] for k in ('id', 'time', 'lat', 'lon', 'dep', 'mag', 'mtype', 'mw', 'mw_method', 'place', 'src')}
        if e['_i'] in pa:
            g, d = pa[e['_i']]; dM = e['_M'] - g['mw']; dts = abs(g['_t'] - e['_t'])
            if abs(dM) > 1.0 and not (dts <= 10 and d <= 30):   # 2026-10-21 onaylı koruma: Δt ≤ 10 s ve Δr ≤ 30 km ise ΔM engellemez
                sus.append({'id': e['id'], 'time': e['time'], 'M': e['_M'], 'mtype': e['mtype'], 'gem_id': g['eventid'], 'gem_mw': g['mw'], 'dM': round(dM, 2), 'dr_km': round(d, 1), 'dt_s': round(dts, 1)})
                # 2026-10-21 karar: özgün büyüklük korunur; ISC-GEM Mw alternatif yeniden değerlendirme olarak kaydedilir (ana kataloğa aktarılmaz)
                P.append({**base, 'M': e['_M'], 'mw_src': raw_src(e), 'not': 'eslesme_guclu_buyukluk_uyusmazligi_cozulmedi',
                          'alt_mw': g['mw'], 'alt_mw_src': 'iscgem_direct' if g['s_mw'] == 'd' else 'iscgem_proxy', 'alt_gem_id': g['eventid'], 'alt_unc_mw': g['unc_mw'], 'alt_q_mw': g['q_mw']}); continue
            src = 'iscgem_direct' if g['s_mw'] == 'd' else 'iscgem_proxy'
            if y < 1963:   # ISC-GEM kaydı birincil
                P.append({'id': 'iscgem:' + g['eventid'], 'time': g['date'].replace(' ', 'T'), 'lat': g['lat'], 'lon': g['lon'], 'dep': g['depth'], 'mag': e['mag'], 'mtype': e['mtype'],
                          'M': g['mw'], 'mw_src': src, 'gem_id': g['eventid'], 'eslesen_A_id': e['id'], 'src': 'ISC-GEM'})
            else:
                P.append({**base, 'M': g['mw'], 'mw_src': src, 'gem_id': g['eventid']})
            log.append({'A_id': e['id'], 'time': e['time'], 'M_eski': e['_M'], 'mtype': e['mtype'], 'M_yeni': g['mw'], 'mw_src': src, 'gem_id': g['eventid'], 'dr_km': round(d, 1), 'dt_s': round(dts, 1), 'koruma_istisnasi': abs(dM) > 1.0})
        else:
            P.append({**base, 'M': e['_M'], 'mw_src': raw_src(e)})
    added_pre = [g for g in G if int(g['date'][:4]) < 1963 and id(g) not in usedG]
    for g in added_pre:
        P.append({'id': 'iscgem:' + g['eventid'], 'time': g['date'].replace(' ', 'T'), 'lat': g['lat'], 'lon': g['lon'], 'dep': g['depth'], 'mag': None, 'mtype': None,
                  'M': g['mw'], 'mw_src': 'iscgem_direct' if g['s_mw'] == 'd' else 'iscgem_proxy', 'gem_id': g['eventid'], 'src': 'ISC-GEM', 'not': 'iscgem_eklenen_1963_oncesi'})
    notadded_post = [g for g in G if int(g['date'][:4]) >= 1963 and id(g) not in usedG]
    # ── doğrulama testleri ─────────────────────────────────────────────────────────────────────────────
    T = {}
    gcount = collections.Counter(p['gem_id'] for p in P if p.get('gem_id'))
    T['T1_bire_bir'] = {'gecti': max(gcount.values()) == 1, 'en_cok_tekrar': max(gcount.values())}
    unch = [p for p in P if p['mw_src'].startswith('catalog_')]
    bad = sum(1 for p in unch if abs(p['M'] - (p['mw'] if p['mw'] is not None else p['mag'])) > 1e-12)
    T['T2_eslesmeyenler_degismedi'] = {'gecti': bad == 0, 'olay': len(unch), 'degisen': bad}
    gem = {g['eventid']: g['mw'] for g in G}
    badm = sum(1 for p in P if p['mw_src'].startswith('iscgem') and abs(p['M'] - gem[p['gem_id']]) > 1e-12)
    T['T3_aktarilan_Mw_ISCGEM_ile_ayni'] = {'gecti': badm == 0, 'olay': sum(1 for p in P if p['mw_src'].startswith('iscgem')), 'farkli': badm}
    T['T4_ham_buyukluk_saklandi'] = {'gecti': all(('mag' in p and 'mtype' in p) for p in P)}
    alt = [p for p in P if 'alt_mw' in p]
    T['T10_alternatif_kayit'] = {'gecti': all(p['M'] == (p['mw'] if p['mw'] is not None else p['mag']) and p['mw_src'].startswith('catalog_') for p in alt), 'olay': len(alt),
                                 'liste': [{k: p[k] for k in ('id', 'time', 'mag', 'mtype', 'M', 'alt_mw', 'alt_mw_src', 'alt_gem_id', 'not')} for p in alt]}
    json.dump(alt, open('analysis/homog_faz3/out/alternatif_buyuklukler.json', 'w'), ensure_ascii=False, indent=1)
    T['T5_tahmini_Mw_yok'] = {'gecti': all(p['mw_src'] in ('iscgem_direct', 'iscgem_proxy', 'catalog_native_mw') or p['mw_src'].startswith('catalog_raw_') for p in P)}
    T['T6_2022_sonrasi_degismedi'] = {'gecti': all(p['mw_src'].startswith('catalog_') for p in P if int(p['time'][:4]) >= 2022)}
    dmt = collections.defaultdict(list)
    for l in log: dmt[(('1904-1962' if int(l['time'][:4]) < 1963 else '1963-1997' if int(l['time'][:4]) < 1998 else '1998-2021'), (l['mtype'] or '?').lower())].append(l['M_eski'] - l['M_yeni'])
    T['T7_dM_tani'] = {f'{a}|{b}': {'n': len(v), 'ort': round(sum(v) / len(v), 2), 'std': round((sum((x - sum(v) / len(v)) ** 2 for x in v) / max(1, len(v) - 1)) ** .5, 2)} for (a, b), v in sorted(dmt.items()) if len(v) >= 5}
    exc = [l for l in log if l['koruma_istisnasi']]
    T['T9_koruma_istisnalari'] = {'gecti': all(l['dt_s'] <= 10 and l['dr_km'] <= 30 for l in exc), 'olay': len(exc),
                                  'liste': [{k: l[k] for k in ('time', 'mtype', 'M_eski', 'M_yeni', 'dt_s', 'dr_km')} for l in exc]}
    # ── süreklilik: beşer yıllık λ (GK74 sonrası) P ile ISC-GEM'in tamamı ────────────────────────────────
    def dc(ev): rows, fl = GK.decluster([{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'mag': e['M']} for e in ev], mag_field='mag'); return [r for r, c in zip(rows, fl) if not c]
    Pd = dc([p for p in P if int(p['time'][:4]) <= 2021]); Gd = dc([{'time': g['date'], 'lat': g['lat'], 'lon': g['lon'], 'M': g['mw']} for g in G])
    Ad = dc([{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'M': e['_M']} for e in A if int(e['time'][:4]) <= 2021])
    rows = []
    for y in range(1904, 2022, 5):
        y2 = min(y + 5, 2022)
        def n(ev, th): return sum(1 for e in ev if y <= int(e['time'][:4]) < y2 and e['mag'] >= th)
        rows.append({'donem': f'{y}-{y2 - 1}', 'P_5.5': n(Pd, 5.5), 'ISCGEM_5.5': n(Gd, 5.5), 'A_5.5': n(Ad, 5.5), 'P_6.0': n(Pd, 6.0), 'ISCGEM_6.0': n(Gd, 6.0), 'A_6.0': n(Ad, 6.0)})
    def ratio(key, lo, hi, th):
        p = sum(r[f'P_{th}'] for r in rows if lo <= int(r['donem'][:4]) < hi); g = sum(r[f'ISCGEM_{th}'] for r in rows if lo <= int(r['donem'][:4]) < hi)
        a = sum(r[f'A_{th}'] for r in rows if lo <= int(r['donem'][:4]) < hi); return {'P': p, 'ISCGEM': g, 'A': a, 'P/ISCGEM': round(p / g, 2) if g else None, 'A/ISCGEM': round(a / g, 2) if g else None}
    cont = {f'{lo}-{hi - 1}|M>={th}': ratio(None, lo, hi, th) for lo, hi in ((1949, 1963), (1963, 1978), (1978, 1998), (1998, 2022)) for th in ('5.5', '6.0')}
    # kabul (önceden tanımlı): her dönem bloğunda P/ISCGEM 0,85–1,15 ve 1963 öncesi/sonrası blok oranları arasındaki fark ≤ 0,15
    acc = all(0.85 <= v['P/ISCGEM'] <= 1.15 for v in cont.values() if v['P/ISCGEM'] is not None)
    step = {th: round(cont[f'1963-1977|M>={th}']['P/ISCGEM'] - cont[f'1949-1962|M>={th}']['P/ISCGEM'], 2) for th in ('5.5', '6.0')}
    T['T8_sureklilik'] = {'gecti': acc and all(abs(v) <= 0.15 for v in step.values()), 'blok_oranlari': cont, '1963_sicrama(P/ISCGEM farki)': step,
                          'kabul': 'her blokta 0,85 ≤ P/ISC-GEM ≤ 1,15 ve 1963 sıçraması ≤ 0,15'}
    src = collections.Counter(p['mw_src'] if not p['mw_src'].startswith('catalog_raw_') else 'catalog_raw_*' for p in P)
    rep = {'meta': {'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'inputs': {'data/eq_historical.json': sha('data/eq_historical.json'), 'analysis/homog_faz1/out/iscgem_v12.1_kutu.json': sha('analysis/homog_faz1/out/iscgem_v12.1_kutu.json'), 'scripts/decluster_gk74.py': sha('scripts/decluster_gk74.py')}},
           'sayilar': {'A_olay': len(A), 'P_olay': len(P), 'eslesen_cift': len(pairs), 'Mw_aktarilan': len(log), 'supheli_eslesme': len(sus), 'iscgem_eklenen_1963_oncesi': len(added_pre),
                       'A_da_karsiligi_olmayan_ISCGEM_1963_2021(eklenmedi)': len(notadded_post), 'mw_src': dict(src)},
           'testler': T, 'bes_yillik': rows, 'supheli_eslesmeler': sus}
    json.dump(rep, open('analysis/homog_faz3/out/faz3_rapor.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(log, open('analysis/homog_faz3/out/aktarim_kaydi.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(json.dumps({'sayilar': rep['sayilar'], 'testler': {k: (v.get('gecti'), {kk: vv for kk, vv in v.items() if kk != 'gecti'} if k in ('T1_bire_bir', 'T2_eslesmeyenler_degismedi', 'T3_aktarilan_Mw_ISCGEM_ile_ayni', 'T8_sureklilik') else '') for k, v in T.items()}, 'T7': T['T7_dM_tani']}, ensure_ascii=False, indent=1))
if __name__ == '__main__': main()
