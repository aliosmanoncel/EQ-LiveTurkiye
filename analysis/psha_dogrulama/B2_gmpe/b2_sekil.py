"""B2 şekli: (a) Vs30 = 360 m/s'de tehlike eğrileri; (b) %10/50 yıl PGA — model × Vs30 (dolu: kesilmemiş σ, boş: 3σ). Okabe–Ito."""
import json, math, textwrap, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.linewidth': 0.6, 'svg.fonttype': 'none'})
R = json.load(open('b2_sonuc.json', encoding='utf-8')); E = np.load('b2_egriler.npz'); x = E['x']; T = 50.0
mods = list(dict.fromkeys(r['model'] for r in R['sonuc'])); col = ['#000000', '#E69F00', '#0072B2', '#009E73', '#CC79A7']
fig, ax = plt.subplots(1, 2, figsize=(174 / 25.4, 80 / 25.4), gridspec_kw={'width_ratios': [1.05, 1]})
for m, c in zip(mods, col):
    k = f'{m}|360'.replace(' ', '_'); ax[0].loglog(x, -np.expm1(-E[k] * T), color=c, lw=1.1, label=m)
for p in (0.10, 0.02): ax[0].axhline(p, color='#888', lw=0.5, ls=':'); ax[0].text(0.0055, p * 1.12, f'%{int(100*p)}/50 yıl', fontsize=6, color='#555')
ax[0].set(xlim=(5e-3, 3), ylim=(1e-4, 1.2), xlabel='PGA (g)', ylabel='50 yılda aşılma olasılığı', title='(a) Vs30 = 360 m/s, aynı nokta kaynak modeli')
ax[0].legend(fontsize=5.8, frameon=False, loc='lower left'); ax[0].grid(True, lw=0.3, color='#ddd')
y = np.arange(len(mods))[::-1]
for i, (m, c) in enumerate(zip(mods, col)):
    for vs, off, mk in ((360.0, 0.12, 'o'), (760.0, -0.12, 's')):
        r = [q for q in R['sonuc'] if q['model'] == m and q['Vs30'] == vs][0]
        ax[1].plot(r['pga10'], y[i] + off, mk, color=c, ms=5); ax[1].plot(r['pga10_3sigma'], y[i] + off, mk, mfc='none', color=c, ms=5)
        ax[1].plot([r['pga10_3sigma'], r['pga10']], [y[i] + off] * 2, color=c, lw=0.6)
ax[1].set_yticks(y); ax[1].set_yticklabels(['\n'.join(textwrap.wrap(m, 22)) for m in mods], fontsize=6.5)
ax[1].set(xlabel='%10/50 yıl PGA (g)', title='(b) Model × zemin × σ kesmesi', xlim=(0.3, 1.05)); ax[1].grid(True, axis='x', lw=0.3, color='#ddd')
from matplotlib.lines import Line2D
ax[1].legend(handles=[Line2D([], [], marker='o', ls='', color='#444', label='Vs30 = 360 m/s'), Line2D([], [], marker='s', ls='', color='#444', label='Vs30 = 760 m/s'),
                      Line2D([], [], marker='o', ls='', mfc='none', color='#444', label='σ 3\'te kesik (boş)')], fontsize=6, frameon=False, loc='center right')
fig.text(0.01, 0.01, textwrap.fill('Model duyarlılığı — doğrulanmış tehlike değeri değildir. Kaynak modeli Aşama A ile aynı (Cotabato + Davao nokta kaynakları, medyan dal); '
         'yalnız GMPE, Vs30 ve σ kesmesi değişir. Parker ve Kuehn küresel sürümler (Filipinler bölgesel ayarı yok); Kuehn OpenQuake\'te deneysel.', 150), fontsize=5.5)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig('b2_sekil.png', dpi=600); fig.savefig('b2_sekil.svg'); print('ok')
