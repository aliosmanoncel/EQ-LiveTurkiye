"""Aşama A (tam motor akışı): ortak_girdi.json ve karsilastirma_sonuc.json'daki geometriden OpenQuake NRML girdileri üretir.
Aynı girdi: MFD oranları oq_karsilastirma.py'deki kod_mfd ile aynı aritmetik (aşağıda birebir; üretilen oranlar oranlar.json'a yazılır ve
oq_karsilastirma.py'nin kaynak nesneleriyle karşılaştırılır — kontrol.py). Geometri: aynı site boylamı ve kaynak 2 enlemi (rrup eşitlemesi).
GMPE: MindanaoKodGMPE (kod_gmpe.py; OpenQuake gsim paketine kayıtlı kopya). Her senaryo ayrı job:
  c1_med, c1_1sig, c2_med, c_comb, c_ftls, lt (27 dal: 9 kaynak modeli dalı [b × Mmax] × 3 GMPE dalı)."""
import os, json, math, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
S = json.load(open(os.path.join(P, 'karsilastirma_sonuc.json'), encoding='utf-8')); REF = np.load(os.path.join(P, 'referans_kod.npz'))
lon_s, lat2 = S['uzaklik']['site_lon'], S['uzaklik']['kaynak2_lat']; x_im = REF['psha_x_im']; M_ps = REF['psha_M_bins']
def kod_mfd(b, lam5, Mmin, Mmax, dM=0.2, M_bins=None):
    if M_bins is None: M_bins = np.arange(Mmin + dM / 2, Mmax, dM)
    M_edges = M_bins - dM / 2
    A = 10 ** (-b * (M_edges - Mmin)); B = 10 ** (-b * (Mmax - Mmin))
    lam_e = lam5 * (A - B) / (1.0 - B); lam_e = np.where(M_bins <= Mmax, lam_e, 0.0)
    return M_bins, np.maximum(-np.diff(np.append(lam_e, 0.0)), 0.0)
def ps(sid, lon, lat, h, Mb, r):
    return f'''    <pointSource id="{sid}" name="{sid}" tectonicRegion="Subduction Interface">
      <pointGeometry><gml:Point><gml:pos>{lon!r} {lat!r}</gml:pos></gml:Point>
        <upperSeismoDepth>0.0</upperSeismoDepth><lowerSeismoDepth>200.0</lowerSeismoDepth></pointGeometry>
      <magScaleRel>PointMSR</magScaleRel><ruptAspectRatio>1.0</ruptAspectRatio>
      <incrementalMFD minMag="{float(Mb[0])!r}" binWidth="0.2"><occurRates>{' '.join(repr(float(v)) for v in r)}</occurRates></incrementalMFD>
      <nodalPlaneDist><nodalPlane probability="1.0" strike="0.0" dip="90.0" rake="90.0"/></nodalPlaneDist>
      <hypoDepthDist><hypoDepth probability="1.0" depth="{h!r}"/></hypoDepthDist>
    </pointSource>'''
def model(name, srcs):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<nrml xmlns:gml="http://www.opengis.net/gml" xmlns="http://openquake.org/xmlns/nrml/0.5">
  <sourceModel name="{name}">
   <sourceGroup tectonicRegion="Subduction Interface">
{chr(10).join(srcs)}
   </sourceGroup>
  </sourceModel>
</nrml>
'''
def gsim_lt(branches):
    b = '\n'.join(f'''        <logicTreeBranch branchID="g{i}"><uncertaintyModel>[MindanaoKodGMPE]
Zt = {zt}
eps = {eps}</uncertaintyModel><uncertaintyWeight>{w}</uncertaintyWeight></logicTreeBranch>''' for i, (zt, eps, w) in enumerate(branches))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<nrml xmlns:gml="http://www.opengis.net/gml" xmlns="http://openquake.org/xmlns/nrml/0.5">
  <logicTree logicTreeID="gmpe">
      <logicTreeBranchSet uncertaintyType="gmpeModel" branchSetID="bs1" applyToTectonicRegionType="Subduction Interface">
{b}
      </logicTreeBranchSet>
  </logicTree>
</nrml>
'''
def ssm_lt(files):
    b = '\n'.join(f'        <logicTreeBranch branchID="s{i}"><uncertaintyModel>{f}</uncertaintyModel><uncertaintyWeight>{w!r}</uncertaintyWeight></logicTreeBranch>' for i, (f, w) in enumerate(files))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<nrml xmlns:gml="http://www.opengis.net/gml" xmlns="http://openquake.org/xmlns/nrml/0.5">
  <logicTree logicTreeID="kaynak">
      <logicTreeBranchSet uncertaintyType="sourceModel" branchSetID="bs0">
{b}
      </logicTreeBranchSet>
  </logicTree>
</nrml>
'''
JOB = '''[general]
description = Mindanao PSHA dogrulama — Asama A ({ad})
calculation_mode = classical
random_seed = 23
[geometry]
sites = {lon!r} 0.0
[logic_tree]
number_of_logic_tree_samples = 0
[erf]
rupture_mesh_spacing = 1.0
width_of_mfd_bin = 0.2
area_source_discretization = 5.0
[site_params]
reference_vs30_type = measured
reference_vs30_value = 360.0
reference_depth_to_1pt0km_per_sec = 100.0
reference_depth_to_2pt5km_per_sec = 1.0
[calculation]
source_model_logic_tree_file = ssm_lt.xml
gsim_logic_tree_file = gmpe_lt.xml
investigation_time = 50.0
intensity_measure_types_and_levels = {{"PGA": [{imls}]}}
truncation_level = 99.0
maximum_distance = 1000.0
pointsource_distance = 0
[output]
export_dir = ./cikti
mean = true
quantiles = 0.05 0.16 0.5 0.84 0.95
individual_rlzs = true
'''
S1 = (0.90, 3.0, 5.0, 8.5); S2 = (0.90, 1.0, 5.0, 7.5); SF = (0.635, 500 * 10 ** (-0.635 * 1.5) * (365 / 90), 5.0, 7.8)
L1, L2 = (0.0, 0.0, 35.5), (lon_s, lat2, 25.0)
imls = ', '.join(repr(float(v)) for v in x_im); oranlar = {}
def yaz(ad, ssm_files, gsims):
    d = os.path.join(H, ad); os.makedirs(d, exist_ok=True)
    for f, txt in ssm_files['dosya'].items(): open(os.path.join(d, f), 'w').write(txt)
    open(os.path.join(d, 'ssm_lt.xml'), 'w').write(ssm_lt(ssm_files['dal'])); open(os.path.join(d, 'gmpe_lt.xml'), 'w').write(gsim_lt(gsims))
    open(os.path.join(d, 'job.ini'), 'w').write(JOB.format(ad=ad, lon=lon_s, imls=imls))
def tek(ad, srcs, gs):
    txt = []
    for sid, (b, lam5, mn, mx), (lo, la, h) in srcs:
        Mb, r = kod_mfd(b, lam5, mn, mx, M_bins=M_ps); oranlar[f'{ad}/{sid}'] = {'M': Mb.round(6).tolist(), 'oran': r.tolist()}; txt.append(ps(sid, lo, la, h, Mb, r))
    yaz(ad, {'dosya': {'ssm.xml': model(ad, txt)}, 'dal': [('ssm.xml', 1.0)]}, gs)
tek('c1_med', [('s1', S1, L1)], [(0, 0.0, 1.0)]); tek('c1_1sig', [('s1', S1, L1)], [(0, 1.0, 1.0)]); tek('c2_med', [('s2', S2, L2)], [(0, 0.0, 1.0)])
tek('c_comb', [('s1', S1, L1), ('s2', S2, L2)], [(0, 0.0, 1.0)]); tek('c_ftls', [('ftls', SF, L1)], [(0, 0.0, 1.0)])
# mantık ağacı: kaynak dalı = b × Mmax (ağırlık w1·w3), GMPE dalı = (Zt, eps) (w2); toplam 27 gerçekleşme
B1 = [(0.635, 0.60), (0.900, 0.30), (1.120, 0.10)]; B3 = [(7.8, 0.50), (8.0, 0.30), (8.2, 0.20)]
files, dal = {}, []
for i, (b, w1) in enumerate(B1):
    for j, (mx, w3) in enumerate(B3):
        Mb, r = kod_mfd(b, 3.0, 5.0, mx); f = f'ssm_b{i}_m{j}.xml'; files[f] = model(f, [ps('lt', 0.0, 0.0, 35.5, Mb, r)]); dal.append((f, round(w1 * w3, 10)))
        oranlar[f'lt/{f}'] = {'M': Mb.round(6).tolist(), 'oran': r.tolist(), 'b': b, 'Mmax': mx}
yaz('lt', {'dosya': files, 'dal': dal}, [(0, 0.0, 0.70), (0, 0.5, 0.20), (1, 0.0, 0.10)])
json.dump(oranlar, open(os.path.join(H, 'oranlar.json'), 'w'), indent=0); print('üretildi:', sorted(os.listdir(H)))
