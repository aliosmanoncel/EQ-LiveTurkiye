"""OpenQuake hazardlib için ÖZEL GMPE: seismo-report/scripts/mindanao_psha.py içindeki `youngs88_vec` bağıntısının birebir kopyası.

ÖNEMLİ: Bu, OpenQuake'in yerleşik bir modeli DEĞİLDİR. OpenQuake 3.26.2'de Youngs vd. (1988) yoktur; yalnız Youngs vd. (1997) sürümleri
vardır. Bu sınıf, iki HESAP MOTORUNU aynı model altında karşılaştırmak için mevcut koddaki denklemi aynen taşır. Denklemin Youngs vd. (1988)
yayınıyla tutarlılığı ayrıca doğrulanamadı (RAPOR §4): σ = 1,45 − 0,1M, OpenQuake'teki Youngs (1997) kaya PGA σ'sıyla aynıdır.

  ln μ[g] = 19,16 + 1,045 M − 4,738 ln(R + 205,5 e^(0,0968 M)) + 0,54 Zt + s,   s = 0,35 ln(760/Vs30) (Vs30 < 760), aksi 0
  σ = max(1,45 − 0,1 M; 0,35);   'epistemik kayma': ln μ ← ln μ + eps·σ (mevcut koddaki gibi)
  R = rrup (nokta kırık, PointMSR → hiposantral uzaklık)
"""
import numpy as np
from openquake.hazardlib.gsim.base import GMPE
from openquake.hazardlib import const
from openquake.hazardlib.imt import PGA


class MindanaoKodGMPE(GMPE):
    DEFINED_FOR_TECTONIC_REGION_TYPE = const.TRT.SUBDUCTION_INTERFACE
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = {PGA}
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = const.IMC.GEOMETRIC_MEAN
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = {const.StdDev.TOTAL}
    REQUIRES_SITES_PARAMETERS = {'vs30'}
    REQUIRES_RUPTURE_PARAMETERS = {'mag'}
    REQUIRES_DISTANCES = {'rrup'}

    def __init__(self, Zt=0, eps=0.0, **kw):
        self.Zt, self.eps = float(Zt), float(eps)

    def compute(self, ctx: np.recarray, imts, mean, sig, tau, phi):
        M, R, vs30 = ctx.mag, ctx.rrup, ctx.vs30
        site = np.where(vs30 < 760.0, 0.35 * np.log(760.0 / vs30), 0.0)
        s = np.maximum(1.45 - 0.1 * M, 0.35)
        ln_mu = 19.16 + 1.045 * M - 4.738 * np.log(R + 205.5 * np.exp(0.0968 * M)) + 0.54 * self.Zt + site
        for m, imt in enumerate(imts):
            mean[m] = ln_mu + self.eps * s
            sig[m] = s
