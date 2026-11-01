"""Karşılaştırma şekilleri (referans_kod.npz, oq_egriler.npz, karsilastirma_sonuc.json). Okabe–Ito renkleri; 600 dpi PNG + SVG."""
import json, math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.linewidth': 0.6, 'svg.fonttype': 'none'})
R = np.load('referans_kod.npz'); O = np.load('oq_egriler.npz'); S = json.load(open('karsilastirma_sonuc.json', encoding='utf-8'))
x = R['psha_x_im']; T = 50.0; poe = lambda lam: -np.expm1(-lam * T)
LMIN, LMAX = S['A_egriler']['c1_med']['lam_araligi']
C = {'c1_med': ('#0072B2', 'Cotabato megathrust (medyan)'), 'c2_med': ('#D55E00', 'Davao fay zonu'), 'c_comb': ('#000000', 'İki kaynak toplam'), 'c_ftls': ('#CC79A7', 'FTLS kaynağı (b = 0,635)')}
fig, ax = plt.subplots(2, 2, figsize=(174 / 25.4, 130 / 25.4), gridspec_kw={'height_ratios': [3, 1.3]})
for k, (c, lab) in C.items():
    ax[0, 0].loglog(x, poe(R['psha_' + k]), color=c, lw=1.6, alpha=0.45, label=f'{lab} — kod')
    ax[0, 0].loglog(x, poe(O['A_' + k]), color=c, lw=0.8, ls='--', label=f'{lab} — OpenQuake')
    m = (R['psha_' + k] >= LMIN) & (R['psha_' + k] <= LMAX)
    ax[1, 0].semilogx(x[m], 100 * (O['A_' + k][m] / R['psha_' + k][m] - 1), color=c, lw=0.9)
for p in (0.10, 0.02): ax[0, 0].axhline(p, color='#888', lw=0.5, ls=':'); ax[0, 0].text(0.006, p * 1.15, f'%{int(100*p)}/50 yıl', fontsize=6, va='bottom', color='#555')
ax[0, 0].set(ylim=(1e-5, 1.2), xlim=(5e-3, 3), ylabel='50 yılda aşılma olasılığı', title='(a) Eşit model: mevcut kod ve OpenQuake 3.26.2')
ax[0, 0].legend(fontsize=5.6, ncol=1, frameon=False, loc='lower left')
ax[1, 0].axhline(0, color='#888', lw=0.5); ax[1, 0].set(xlabel='PGA (g)', ylabel='λ fark (%)\nOQ / kod − 1', xlim=(5e-3, 3), ylim=(-0.3, 0.3))
# (b) mantık ağacı yüzdelikleri
FR = ['5.', '16.', '50.', '84.', '95.']; col = ['#56B4E9', '#009E73', '#000000', '#009E73', '#56B4E9']
for i, f in enumerate(FR):
    ax[0, 1].loglog(x, poe(R['lt_frac_curves'][i]), color=col[i], lw=1.6, alpha=0.45)
    ax[0, 1].loglog(x, poe(O['fr_oq'][i]), color=col[i], lw=0.8, ls='--')
ax[0, 1].loglog(x, poe(R['lt_lam_mean']), color='#E69F00', lw=1.6, alpha=0.45); ax[0, 1].loglog(x, poe(O['lam_mean_oq']), color='#E69F00', lw=0.8, ls='--')
ax[0, 1].loglog(x, poe(O['w97'] @ O['lt97']), color='#D55E00', lw=1.1, ls='-.', label='Youngs (1997), OpenQuake — EŞDEĞER DEĞİL\n(b ve Mmax dalları, kaya, ağırlıklı ortalama)')
for p in (0.10, 0.02): ax[0, 1].axhline(p, color='#888', lw=0.5, ls=':')
from matplotlib.lines import Line2D
ax[0, 1].legend(handles=[Line2D([], [], color='#000', lw=1.6, alpha=0.45, label='mevcut kod (kalın)'), Line2D([], [], color='#000', lw=0.8, ls='--', label='OpenQuake (kesikli)'),
    Line2D([], [], color='#000', label='50. yüzdelik'), Line2D([], [], color='#009E73', label='16./84.'), Line2D([], [], color='#56B4E9', label='5./95.'), Line2D([], [], color='#E69F00', label='ağırlıklı ortalama'),
    Line2D([], [], color='#D55E00', ls='-.', label='Youngs (1997), OQ — eşdeğer değil')], fontsize=5.6, frameon=False, loc='lower left')
ax[0, 1].set(ylim=(1e-5, 1.2), xlim=(5e-3, 3), title='(b) Mantık ağacı (27 dal): yüzdelikler')
mx = []
for i in range(27):
    m = (R['lt_branch_curves'][i] >= LMIN) & (R['lt_branch_curves'][i] <= LMAX); mx.append(np.abs(O['lt_oq'][i][m] / R['lt_branch_curves'][i][m] - 1).max())
ax[1, 1].bar(range(1, 28), 100 * np.array(mx), color='#0072B2', width=0.7); ax[1, 1].set(xlabel='Dal', ylabel='en büyük |λ fark| (%)', xlim=(0, 28))
for a in ax.flat: a.grid(True, which='major', lw=0.3, color='#ddd')
import textwrap
fig.text(0.01, 0.005, textwrap.fill('Eşit model: özel GMPE (mevcut koddaki bağıntının birebir kopyası), nokta kaynak (rrup = 58,11 / 122,58 km), aynı MFD sınıfları, '
         'Vs30 = 360 m/s, kesilmemiş σ. Fark yalnız 50 yıllık PoE 10⁻⁵–0,999 aralığında hesaplandı (OpenQuake olasılıkları 32 bit tutar). '
         'Uyuşma hesap motorlarının eşdeğerliğini gösterir; kaynak modelinin ya da GMPE\'nin doğruluğunu göstermez.', 150), fontsize=5.5)
fig.tight_layout(rect=(0, 0.055, 1, 1))
fig.savefig('karsilastirma_sekil.png', dpi=600); fig.savefig('karsilastirma_sekil.svg')
print('ok')
