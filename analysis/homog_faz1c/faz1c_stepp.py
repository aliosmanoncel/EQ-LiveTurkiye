"""
Faz 1c — Stepp (1972) tamlık testi prototipi (yalnız analiz; üretim koduna, eq_historical.json'a, GK74 koduna,
mw_authority.json'a ve mevcut tamlık merdivenine DOKUNMAZ; GK74 yalnızca scripts/decluster_gk74.py'den içe aktarılıp kopya veride çalıştırılır).

Seriler (aynı kutu 33–45° K, 23–48° D; ortak bitiş 2021-12-31 = ISC-GEM v12.1'in son yılı):
  A_ham   : data/eq_historical.json, büyüklük = mw ?? mag (tarayıcıdaki varsayılanla aynı)
  A_GK74  : A_ham + Gardner & Knopoff (1974), aynı büyüklükle
  B_ham   : ISC-GEM v12.1 ana katalog, Mw (doğrudan + vekil); ayrıca B_ham_dogrudan ve B_ham_vekil
  B_GK74  : B_ham + GK74 (Mw ile)
  Ana seri ÖNCEDEN belirlendi: A_GK74 ve B_GK74 (Stepp testi durağan Poisson varsayar); ham seriler duyarlılıktır.
Yöntem (Stepp 1972, eş. 2–4): her büyüklük sınıfı için, bitişten geriye uzayan T = 1…Tmax yıllık pencerelerde
  λ(T) = N(T)/T ve σ(T) = √(λ(T)/T). Tam kayıt aralığında σ ∝ T^−1/2.
Tamlık başlangıcının nesnel kestirimi (iki ölçüt, ikisi de raporlanır; ikisi de Stepp'in görsel kararının yerine geçen
  bizim uyarlamamızdır):
  (i) kırılma noktası: log σ – log T'ye iki parçalı uyum; 1. parça (kısa T) eğimi −0,5'e sabit, 2. parça serbest;
      kalıntı kareler toplamını en küçük yapan T* (T* ≥ 10 yıl ve ≥ 5 olay şartıyla).
  (ii) Poisson düşüşü: λ_ref = λ(T*) ; T, λ(T) ≥ λ_ref − 2√(λ_ref/T) olduğu sürece tam sayılır; ilk ihlalden önceki en
      büyük T.
  Yeterlilik: tamlık süresi ≥ 5τ (τ = 1/λ_ref) ve N ≥ 5 olay ayrıca raporlanır (5τ tek başına yeterlilik kanıtı değildir).
Kullanım: python analysis/homog_faz1c/faz1c_stepp.py
"""
import collections, hashlib, json, math, sys
from datetime import datetime, timezone
sys.path.insert(0, 'scripts'); import decluster_gk74 as GK
END = datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp(); END_Y = 2022.0
CLS = [(4.5, 5.0), (5.0, 5.5), (5.5, 6.0), (6.0, 10.0)]
LADDER = [(1900, 5.5), (1965, 4.5), (1980, 4.0), (1990, 3.5), (1998, 3.0)]   # mevcut merdiven (referans; değiştirilmez)
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def ts(s): return datetime.fromisoformat(s.replace('Z', '').replace(' ', 'T').split('.')[0]).replace(tzinfo=timezone.utc).timestamp()
def yr(t): return 1970 + t / (365.2425 * 86400)
def series_A():
    ev = json.load(open('data/eq_historical.json'))['events']
    out = [{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'mag': e['mw'] if e['mw'] is not None else e['mag'], 'mtype': e['mtype']} for e in ev]
    return [e for e in out if ts(e['time']) < END]
def series_B():
    g = [x for x in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if x['set'] == 'main' and x['mw'] is not None]
    return [{'time': x['date'], 'lat': x['lat'], 'lon': x['lon'], 'mag': x['mw'], 's': x['s_mw']} for x in g]
def gk(ev):
    rows, fl = GK.decluster([dict(e) for e in ev], mag_field='mag'); return [e for e, c in zip(rows, fl) if not c]
def stepp(ev, lo, hi):
    yrs = sorted(yr(ts(e['time'])) for e in ev if lo <= e['mag'] < hi)
    if not yrs: return None
    tmax = int(END_Y - math.floor(min(yrs))); curve = []
    for T in range(1, tmax + 1):
        n = sum(1 for y in yrs if y >= END_Y - T); lam = n / T
        curve.append({'T': T, 'N': n, 'lam': round(lam, 5), 'sigma': round(math.sqrt(lam / T), 6) if lam > 0 else None})
    pts = [(c['T'], c['sigma'], c['N']) for c in curve if c['sigma']]
    best = None
    for k in range(len(pts)):
        Ts, s, n = pts[k]
        if Ts < 10 or n < 5: continue
        a = sum(math.log10(p[1]) + 0.5 * math.log10(p[0]) for p in pts[:k + 1]) / (k + 1)     # 1. parça: eğim −0,5
        r1 = sum((math.log10(p[1]) - (a - 0.5 * math.log10(p[0]))) ** 2 for p in pts[:k + 1])
        rest = pts[k:]
        if len(rest) >= 3:
            X = [math.log10(p[0]) for p in rest]; Y = [math.log10(p[1]) for p in rest]; mx, my = sum(X) / len(X), sum(Y) / len(Y)
            sxx = sum((x - mx) ** 2 for x in X); bb = sum((x - mx) * (y - my) for x, y in zip(X, Y)) / sxx if sxx else 0
            r2 = sum((y - (my + bb * (x - mx))) ** 2 for x, y in zip(X, Y))
        else: r2, bb = 0.0, None
        if best is None or r1 + r2 < best[0]: best = (r1 + r2, Ts, bb)
    res = {'n_total': len(yrs), 'first_year': round(min(yrs), 2), 'curve': curve}
    if best:
        Tst = best[1]; lam_ref = next(c['lam'] for c in curve if c['T'] == Tst)
        Tp = Tst
        for c in curve:
            if c['T'] <= Tst: continue
            if c['lam'] < lam_ref - 2 * math.sqrt(lam_ref / c['T']): break
            Tp = c['T']
        Np = next(c['N'] for c in curve if c['T'] == Tp)
        res.update({'breakpoint_T': Tst, 'breakpoint_start': int(END_Y - Tst), 'slope_after': best[2] and round(best[2], 3), 'lam_ref': lam_ref,
                    'poisson_T': Tp, 'poisson_start': int(END_Y - Tp), 'N_in_complete': Np, 'tau_yr': round(1 / lam_ref, 2) if lam_ref else None,
                    'ge_5tau': bool(lam_ref and Tp >= 5 / lam_ref), 'N_ge_5': Np >= 5})
    return res
def ladder_start(m):
    s = None
    for y, mc in LADDER:
        if m >= mc: s = y if s is None else s; break
    return next((y for y, mc in LADDER if m >= mc), None)
def main():
    A = series_A(); A_gk = gk(A); B = series_B(); B_gk = gk(B)
    S = {'A_ham': A, 'A_GK74': A_gk, 'B_ham': B, 'B_GK74': B_gk, 'B_ham_dogrudan': [e for e in B if e['s'] == 'd'], 'B_ham_vekil': [e for e in B if e['s'] == 'p']}
    out = {'meta': {'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'end': '2021-12-31', 'classes': CLS, 'ladder_reference': LADDER, 'main_series': ['A_GK74', 'B_GK74'],
                    'inputs': {'data/eq_historical.json': sha('data/eq_historical.json'), 'analysis/homog_faz1/out/iscgem_v12.1_kutu.json': sha('analysis/homog_faz1/out/iscgem_v12.1_kutu.json'),
                               'scripts/decluster_gk74.py': sha('scripts/decluster_gk74.py')},
                    'n': {k: len(v) for k, v in S.items()}}, 'results': {}}
    for k, ev in S.items():
        out['results'][k] = {f'{lo}-{hi if hi < 10 else "+"}': stepp(ev, lo, hi) for lo, hi in CLS}
    json.dump(out, open('analysis/homog_faz1c/out/stepp_sonuc.json', 'w'), ensure_ascii=False, indent=1)
    # özet tablo
    print('seri | sınıf | N | kırılma başl. | Poisson başl. | λ_ref/yıl | τ | ≥5τ | merdiven başl.')
    for k, r in out['results'].items():
        for c, v in r.items():
            if not v or 'breakpoint_start' not in v: print(k, c, v and v['n_total'], '— yetersiz'); continue
            print(k, c, v['n_total'], v['breakpoint_start'], v['poisson_start'], v['lam_ref'], v['tau_yr'], v['ge_5tau'], ladder_start(float(c.split('-')[0])))
    # şekil
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(11, 8.5), sharex=True, sharey=True)
    for ax, k in zip(axs.flat, ['A_ham', 'A_GK74', 'B_ham', 'B_GK74']):
        for (lo, hi), col in zip(CLS, ['#0891b2', '#16a34a', '#ea580c', '#7c3aed']):
            v = out['results'][k][f'{lo}-{hi if hi < 10 else "+"}']
            if not v: continue
            T = [c['T'] for c in v['curve'] if c['sigma']]; s = [c['sigma'] for c in v['curve'] if c['sigma']]
            ax.loglog(T, s, '.', ms=3, color=col, label=f'M {lo}–{hi if hi < 10 else "+"}')
            if 'lam_ref' in v and v['lam_ref']:
                ax.loglog(T, [math.sqrt(v['lam_ref'] / t) for t in T], '-', lw=0.8, color=col, alpha=.6)
                ax.axvline(v['poisson_T'], color=col, ls=':', lw=0.8)
        ax.set_title(k); ax.grid(alpha=.3, which='both'); ax.legend(fontsize=7)
    for ax in axs[1]: ax.set_xlabel('Pencere uzunluğu T (yıl, bitiş 2021-12-31)')
    for ax in axs[:, 0]: ax.set_ylabel('σ_λ = √(λ/T)')
    fig.suptitle('Stepp (1972) testi — noktalar gözlenen σ, çizgiler √(λ_ref/T), kesikli: Poisson ölçütüne göre tamlık süresi')
    fig.tight_layout(); fig.savefig('analysis/homog_faz1c/out/stepp_egrileri.png', dpi=140)
if __name__ == '__main__': main()
