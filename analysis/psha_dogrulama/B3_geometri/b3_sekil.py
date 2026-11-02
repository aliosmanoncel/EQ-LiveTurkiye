"""B3 şekli: %10/50 yıl PGA — geometri × GMPE × Vs30 (Cotabato ve Davao ayrı panel; Davao alternatifleri birleştirilmez). Okabe–Ito."""
import json, textwrap, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.linewidth': 0.6, 'svg.fonttype': 'none'})
R = json.load(open('b3_sonuc.json', encoding='utf-8'))
mods = list(dict.fromkeys(r['model'] for r in R['sonuc']))
GE = {'Cotabato': [('P0', 'nokta (B2, rrup 58 km)', '#000000', 'o'), ('P1', 'nokta, gerçek konum', '#999999', 'o'), ('F', 'sonlu fay, eğim 47°', '#0072B2', 's'), ('F2_dip30', 'sonlu fay, eğim 30°', '#56B4E9', 's')],
      'Davao': [('P0', 'nokta (B2)', '#000000', 'o'), ('FDdik', 'fay, görüş hattına dik', '#D55E00', 's'), ('FDpar', 'fay, görüş hattına paralel', '#E69F00', 's'), ('A', 'alan (r = 40 km)', '#009E73', 'D')]}
fig, ax = plt.subplots(2, 2, figsize=(174 / 25.4, 120 / 25.4), sharey=True)
for j, vs in enumerate((360.0, 760.0)):
    for i, (kay, gl) in enumerate(GE.items()):
        a = ax[i, j]; y = np.arange(len(mods))[::-1]
        for k, (g, lab, c, mk) in enumerate(gl):
            v = [[r for r in R['sonuc'] if r['kaynak'] == kay and r['geometri'] == g and r['model'] == m and r['Vs30'] == vs][0]['pga10'] for m in mods]
            a.plot(v, y + 0.27 - 0.18 * k, mk, color=c, ms=4.5, label=lab)
        a.set_yticks(y); a.set_yticklabels(mods, fontsize=6.8); a.grid(True, axis='x', lw=0.3, color='#ddd')
        a.set_title(f'({"abcd"[2 * i + j]}) {kay}\nVs30 = {int(vs)} m/s', fontsize=8); a.set_xlabel('%10/50 yıl PGA (g)' if i else '')
        if j == 1: a.legend(fontsize=6, frameon=False, loc='upper left', bbox_to_anchor=(1.02, 1.0))
fig.text(0.01, 0.01, textwrap.fill('Model duyarlılığı — doğrulanmış tehlike değeri değildir. MFD, oranlar, Mmax, GMPE ve Vs30 B2 ile aynı; yalnız geometri değişir. '
         'Davao alternatifleri ayrı gösterilir, birleştirilmez. σ kesilmemiş.', 150), fontsize=5.6)
fig.tight_layout(rect=(0, 0.04, 0.82, 1)); fig.savefig('b3_sekil.png', dpi=600); fig.savefig('b3_sekil.svg'); print('ok')
