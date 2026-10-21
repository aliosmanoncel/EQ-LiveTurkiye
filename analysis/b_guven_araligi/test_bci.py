"""Birim testleri: Tinti–Mulargia uygulamasının bağımsız denetimi ve normal yöntemin EQ-Live koduyla birebirliği."""
import math, json, subprocess, sys, os
import numpy as np
from scipy import stats, optimize
sys.path.insert(0, os.path.dirname(__file__)); import bci
ok = fail = 0
def chk(c, msg):
    global ok, fail
    ok += c; fail += (not c); print(('  ok  ' if c else '  !!  ') + msg)

print('1. Eş. 21 (beta-fonksiyonu) ile Eş. 18 (negatif binom, doğrudan kök bulma) aynı uçları veriyor')
# L_N(r,p) = Σ_{k≤r} C(N+k−1,N−1)(1−p)^N p^k = nbinom.cdf(r, N, 1−p)   (Eş. 16–17)
L = lambda r, N, p: stats.nbinom.cdf(r, N, 1 - p)
mx = 0
for N in (1, 2, 4, 10, 30, 49, 100):
    for r in (0, 1, 3, 7, 25, 80, 300):
        pl_b = 0.0 if r == 0 else __import__('scipy').special.betaincinv(r, N, 0.025)
        pu_b = 1 - __import__('scipy').special.betaincinv(N, r + 1, 0.025)
        pl_n = 0.0 if r == 0 else optimize.brentq(lambda p: L(r - 1, N, p) - 0.975, 1e-12, 1 - 1e-12)
        pu_n = optimize.brentq(lambda p: L(r, N, p) - 0.025, 1e-12, 1 - 1e-12)
        mx = max(mx, abs(pl_b - pl_n), abs(pu_b - pu_n))
chk(mx < 1e-8, f'en büyük fark {mx:.1e} (49 (N, r) çifti)')

print('2. N = 1 kapalı biçim (I_p(r,1) = p^r, I_q(1,r+1) = 1 − (1−q)^(r+1)): p_l = (α/2)^(1/r), p_u = (1 − α/2)^(1/(r+1))')
for r in (1, 2, 5):
    pl, pu = __import__('scipy').special.betaincinv(r, 1, .025), 1 - __import__('scipy').special.betaincinv(1, r + 1, .025)
    chk(abs(pl - .025 ** (1 / r)) < 1e-10 and abs(pu - .975 ** (1 / (r + 1))) < 1e-10, f'r = {r}: p_l = {pl:.6f} (beklenen {.025 ** (1 / r):.6f}), p_u = {pu:.6f} (beklenen {.975 ** (1 / (r + 1)):.6f})')

print('3. Büyük N: kesin uçlar Eş. 23 ML yaklaşımına yakınsıyor')
for N, z in ((2000, 4.0), (20000, 4.0)):
    r = int(N * z); a = bci.ci_tm(N, r, 0.1); b = bci.ci_tm_ml(N, r, 0.1)
    chk(max(abs(a[0] - b[0]), abs(a[1] - b[1])) < (0.01 if N == 2000 else 0.002), f'N = {N}: kesin {a[0]:.4f}–{a[1]:.4f}, ML {b[0]:.4f}–{b[1]:.4f}')

print('4. Şekil 2a ile karşılaştırma (N = 10, ΔM = 0,1, α = 0,05; değerler şekilden gözle okundu, okuma hassasiyeti ≈ ±0,15)')
FIG = {3: (1.3, 4.85), 10: (0.50, 1.68)}   # kesin (düz çizgi) β_l, β_u
for z, (fl, fu) in FIG.items():
    bl, bu = bci.ci_tm(10, 10 * z, 0.1); Bl, Bu = bl / bci.LOG10E, bu / bci.LOG10E
    chk(abs(Bl - fl) < 0.15 and abs(Bu - fu) < 0.2, f'z = {z}: hesap β = {Bl:.2f}–{Bu:.2f}, şekil ≈ {fl}–{fu}')
seq = [bci.ci_tm(10, r, 0.1) for r in (10, 30, 60, 100)]
chk(all(seq[i][0] > seq[i + 1][0] and seq[i][1] > seq[i + 1][1] for i in range(3)), 'uçlar z ile tekdüze azalıyor (şekildeki gibi)')
chk(all(bci.ci_tm(10, r, 0.1)[k] > bci.ci_tm_ml(10, r, 0.1)[k] for r in range(20, 101, 10) for k in (0, 1)), 'kesin uçlar ML uçlarının üstünde (şekildeki düz çizgi / nokta ilişkisi)')

print('5. χ² aralığı: sürekli üstel örneklemde kesin %95 (analitik denetim)')
N = 10; ql, qu = stats.chi2.ppf(.025, 20), stats.chi2.ppf(.975, 20)
# 2Nβ/β̂ = 2β Σ(m−m0) ~ χ²_{2N}  → P(β ∈ [ql/(2N)β̂, qu/(2N)β̂]) = 0,95
chk(abs((stats.chi2.cdf(qu, 20) - stats.chi2.cdf(ql, 20)) - 0.95) < 1e-12, 'P(q_l ≤ χ²_20 ≤ q_u) = 0,95')

print('6. normal yöntem ve kestirici EQ-Live index.html ile birebir (node ile)')
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
js = r'''
const fs=require('fs');const s=fs.readFileSync(process.argv[2],'utf8');
const cut=(a,b)=>{const i=s.indexOf(a),j=s.indexOf(b,i);return s.slice(i,j)};
eval(cut('function computeBvalue(','// Aki (1965) MLE için %95'));
const ciSrc=s.slice(s.indexOf('// Aki (1965) MLE için %95'));const fn=ciSrc.slice(ciSrc.indexOf('function'),ciSrc.indexOf('\n}')+2);eval(fn);
const name=fn.match(/function\s+(\w+)/)[1];
const inp=JSON.parse(process.argv[3]);
process.stdout.write(JSON.stringify(inp.map(([m,Mc,dm])=>{const b=computeBvalue(m,Mc,dm);return [b, globalThis[name]?null:null, eval(name)(b,m.filter(x=>x>=Mc-1e-9).length)]})));
'''
open('/tmp/_ci.js', 'w').write(js)
rng = np.random.default_rng(7); cases = []
for N, dm in ((10, 0.1), (40, 0.1), (100, 0.1), (20, 0.5)):
    m = np.round((rng.exponential(1 / math.log(10), N)) / dm) * dm + 3.0
    cases.append([m.tolist(), 3.0, dm])
out = subprocess.run(['node', '/tmp/_ci.js', os.path.join(root, 'index.html'), json.dumps(cases)], capture_output=True, text=True)
if out.returncode: print(out.stderr[:500])
res = json.loads(out.stdout)
for (m, Mc, dm), (bjs, _, hw) in zip(cases, res):
    b, N, _ = bci.b_eqlive(m, Mc, dm); lo, hi = bci.ci_normal(b, N)
    chk(abs(b - bjs) < 1e-12 and abs((hi - b) - hw) < 1e-12, f'N = {N}, ΔM = {dm}: b = {b:.6f} (JS {bjs:.6f}), yarı genişlik {hi - b:.6f} (JS {hw:.6f})')
print(f'\n{"PASS" if not fail else "FAIL"}: {ok} geçti, {fail} kaldı'); sys.exit(1 if fail else 0)
