"""
doublet_literatur.py — 6. tur (beşinci aşama): DOUBLET adaylarının yöntem sınıflarının literatürle karşılaştırılması.

Aday kuralı 1. turla aynı (yalnız aday; literatür tanımı değildir): iki olay M ≥ 6, |ΔM| ≤ 0,5, Δt ≤ 365 gün,
Δd ≤ 150 km (100 km işaretli). İki ölçekte üretilir:
  H0   ham EMSC büyüklüğü (1. tur listesi)
  H2+A sitenin combined_dispatch_md_eqml dönüşümü + otoriter Mw (5. tur varyantı; İzmit/Düzce gerçek Mw ile girer)
Her çift için: GK74 sınıfı ve GEREKÇE (2. olay 1. olayın penceresi içinde mi: Δt ≤ T(M1), Δd ≤ D(M1), M2 < M1),
Reasenberg sınıfı, aynı RB kümesi mi. Tüm bölge (80 929 olay), iki yöntem ilgili ölçekte yeniden çalıştırılır.
Literatür sınıfları RAPOR.md 6. turda kaynaklarıyla verilir (bu betik literatür okumaz).
Çıktı: doublet_literatur.json, doublet_literatur.csv.
Kullanım: python .../doublet_literatur.py   (proje kökünden)
"""
import csv, json, os, sys

sys.path.insert(0, 'scripts')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decluster_gk74 as GK  # noqa: E402
import decluster_reasenberg as D  # noqa: E402
from bok_analiz import parse, km, XMEFF  # noqa: E402
from turkiye_alt_kume import apply_mwauth  # noqa: E402
from olcek_homojenlestirme import convert  # noqa: E402

RULE = dict(mmin=6.0, dm=0.5, dt_days=365.0, dkm=150.0)


def run(ev, label):
    gevs, gcl = GK.decluster(ev, 'mag'); gk = {e['id']: (not c) for e, c in zip(gevs, gcl)}
    revs, o = D.decluster(ev, XMEFF, 'zmap', 'mag')
    rcls = {e['id']: k for e, k in zip(revs, o['event_class'])}; rcid = {e['id']: c for e, c in zip(revs, o['cluster_id'])}
    m6 = sorted((e for e in ev if e['mag'] >= RULE['mmin']), key=lambda e: e['time'])
    out = []
    for i, a in enumerate(m6):
        for b in m6[i + 1:]:
            dt = (parse(b['time']) - parse(a['time'])).total_seconds() / 86400
            if dt > RULE['dt_days']:
                break
            d = km(a['lat'], a['lon'], b['lat'], b['lon'])
            if d > RULE['dkm'] or abs(a['mag'] - b['mag']) > RULE['dm'] + 1e-9:
                continue
            T, Dk = GK.gk_window(a['mag'])
            out.append(dict(olcek=label, olay1=f"{a['time'][:16]} M{a['mag']:.1f} ({a['mtype']}) {a['place']}",
                            olay2=f"{b['time'][:16]} M{b['mag']:.1f} ({b['mtype']}) {b['place']}",
                            dt_gun=round(dt, 3), uzaklik_km=round(d, 1), dM=round(b['mag'] - a['mag'], 2), dkm_100_icinde=d <= 100,
                            gk_pencere_T_gun=round(T, 1), gk_pencere_D_km=round(Dk, 1),
                            gk_ikinci_pencerede=(dt <= T and d <= Dk and b['mag'] < a['mag']),
                            gk74_birinci='bağımsız' if gk[a['id']] else 'artçı', gk74_ikinci='bağımsız' if gk[b['id']] else 'artçı',
                            rb_birinci=rcls[a['id']], rb_ikinci=rcls[b['id']],
                            ayni_rb_kumesi=bool(rcid[a['id']] == rcid[b['id']] and rcid[a['id']] >= 0),
                            ikinci_iki_yontemde=('ayrışıyor' if gk[b['id']] != (rcls[b['id']] != 'dependent') else 'aynı')))
    return out


def main():
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    ev0 = [e for e in raw['events'] if e.get('src') == 'EMSC']
    evA = [dict(e) for e in ev0]
    for e in evA:
        v = convert(e, 'combined_dispatch_md_eqml')
        if v is not None:
            e['mag'] = v
    evA = apply_mwauth(evA)
    rows = run(ev0, 'H0 ham') + run(evA, 'H2+A otoriter Mw')
    json.dump(dict(kural=RULE, xmeff=XMEFF, adaylar=rows), open(os.path.join(HERE, 'doublet_literatur.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, 'doublet_literatur.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"{r['olcek']:16s} {r['olay1'][:44]:44s} → {r['olay2'][:44]:44s} Δt {r['dt_gun']:7.2f} g Δd {r['uzaklik_km']:5.1f} km "
              f"| GK pencere {r['gk_pencere_T_gun']:.0f} g/{r['gk_pencere_D_km']:.0f} km içinde={r['gk_ikinci_pencerede']} | GK {r['gk74_birinci']}/{r['gk74_ikinci']} "
              f"RB {r['rb_birinci']}/{r['rb_ikinci']} aynı küme={r['ayni_rb_kumesi']} | {r['ikinci_iki_yontemde']}")


if __name__ == '__main__':
    main()
