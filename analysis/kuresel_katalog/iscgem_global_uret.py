"""
Aşama 2 (2026-10-26): ISC-GEM v12.1 ANA katalogundan küresel katalog dosyasını üretir ve doğrular.
Girdi: doğrulanmış çıkarım out/iscgem_v12.1_ana.json.gz (iscgem_cikar.py; ham CSV SHA-256'ları meta'da).
Çıktı: uretim/iscgem_global.json  (yalnız ana katalog; ek katalog ve USGS kayıtları YOK).

Kurallar (OLCUM_2_RAPOR.md §9 ve kullanıcı kararı 2026-10-26):
  - Değerler kaynaktaki gibi aktarılır; dönüştürme, yuvarlama, tahminle doldurma yapılmaz.
  - Her olayda büyüklük türü açıkça yazılır (M_tur). ISC-GEM ana katalogunda tür her zaman Mw'dir;
    Mw'nin doğrudan sismik momentten mi (s_mw = d) yoksa ISC-GEM'in Ms/mb'den vekil bağıntısıyla mı (s_mw = p)
    hesaplandığı Mw_yontem alanında ayrı tutulur (Di Giacomo vd. 2015a).
  - Şema, ileride ayrı ve isteğe bağlı USGS katmanının da aynı alanlarla kendi büyüklük türünü taşıyabileceği biçimdedir
    (USGS_KATMANI_TASARIM.md). Bu dosya o katmanı içermez.

Kullanım:
  python analysis/kuresel_katalog/iscgem_global_uret.py uret      # dosyayı üretir
  python analysis/kuresel_katalog/iscgem_global_uret.py dogrula   # dosyayı çıkarıma karşı denetler (çıkış kodu 0/1)
"""
import gzip, hashlib, json, os, sys, collections

KOK = os.path.dirname(os.path.abspath(__file__))
GIRDI = os.path.join(KOK, 'out', 'iscgem_v12.1_ana.json.gz')
CIKTI = os.path.join(KOK, 'uretim', 'iscgem_global.json')
SEMA = 'eq-live/kuresel-katalog/1'
ALANLAR = ['id', 't', 'lat', 'lon', 'dep', 'M', 'M_tur', 'M_unc', 'M_q', 'Mw_yontem', 'loc_q', 'dep_unc', 'dep_q']
YONTEM = {'d': 'dogrudan', 'p': 'vekil'}
TANIM = {
    'id': "Katman önekli olay kimliği: 'iscgem:<ISC-GEM eventid>'",
    't': 'Başlangıç zamanı, ISO-8601 UTC (kaynaktaki hassasiyetle)',
    'lat': 'Enlem, derece (WGS84)', 'lon': 'Boylam, derece (WGS84)',
    'dep': 'Derinlik, km', 'dep_unc': 'Derinlik belirsizliği, km (kaynakta verildiği gibi)',
    'M': 'Büyüklük değeri (M_tur türünde; dönüştürülmemiş)',
    'M_tur': "Büyüklük türü. Bu katmanda her zaman 'Mw'. Farklı türler birbirinin yerine kullanılamaz.",
    'M_unc': 'Büyüklük belirsizliği (kaynaktaki unc_mw)',
    'M_q': 'Büyüklük kalite sınıfı A/B/C (kaynaktaki q_mw)',
    'Mw_yontem': "Mw'nin elde edilişi: 'dogrudan' = sismik momentten (s_mw = d); 'vekil' = ISC-GEM'in Ms/mb'den ampirik bağıntıyla hesapladığı Mw (s_mw = p). Mw olmayan türlerde null.",
    'loc_q': 'Konum kalite sınıfı A/B/C (kaynaktaki q_loc)', 'dep_q': 'Derinlik kalite sınıfı A/B/C (kaynaktaki q_dep)'}

def sha(b): return hashlib.sha256(b).hexdigest()
def oku_girdi():
    ham = open(GIRDI, 'rb').read(); d = json.loads(gzip.decompress(ham)); return d, sha(ham)

def donustur(d):
    I = {a: i for i, a in enumerate(d['alanlar'])}
    olaylar = []
    for e in d['olaylar']:
        olaylar.append(['iscgem:%d' % e[I['eventid']], e[I['t']], e[I['lat']], e[I['lon']], e[I['dep']], e[I['mw']], 'Mw',
                        e[I['mw_unc']], e[I['mw_q']], YONTEM.get(e[I['mw_s']]) if e[I['mw_s']] is not None else None,
                        e[I['loc_q']], e[I['dep_unc']], e[I['dep_q']]])
    return olaylar

def meta_yap(d, girdi_sha, olaylar):
    m = d['meta']
    return {'sema': SEMA, 'katman': 'iscgem_ana',
            'aciklama': 'ISC-GEM v12.1 ana katalogu, 1904–2021, küresel. Ek katalog (Supplement) ve USGS kayıtları bu dosyada YOK.',
            'kaynak': m['kaynak'], 'surum': m['surum'], 'telif': m['telif'], 'lisans': 'CC BY-SA 3.0 (unported), http://creativecommons.org/licenses/by-sa/3.0/',
            'atif': m['atif'], 'lisans_dosyasi': 'analysis/kuresel_katalog/uretim/LISANS_ISC-GEM_kuresel.txt',
            'degisiklikler': 'Ana katalogdan yalnız konum, derinlik, Mw ve kalite alanları alındı; alan adları değiştirildi; s_mw kodu (d/p) Mw_yontem olarak yazıldı. Değer değiştirilmedi.',
            'uretici': 'analysis/kuresel_katalog/iscgem_global_uret.py', 'girdi': {'dosya': 'analysis/kuresel_katalog/out/iscgem_v12.1_ana.json.gz', 'sha256': girdi_sha},
            'ham_girdi_sha256': m['girdi_sha256'], 'eksik_deger': 'null (tahminle doldurulmaz)',
            'olay_sayisi': len(olaylar), 'ilk': olaylar[0][1], 'son': olaylar[-1][1],
            'tamlik_notu': "Tamlık bu dosyada yeniden türetilmedi; ISC-GEM belgesine bakınız (Di Giacomo vd. 2018, ESSD 10:1877). Mw 5,0–5,5 kapsamı 2019 öncesinde bölgeye göre tekdüze değildir.",
            'alan_tanimlari': TANIM}

def uret():
    d, gs = oku_girdi(); olaylar = donustur(d)
    os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
    b = json.dumps({'meta': meta_yap(d, gs, olaylar), 'alanlar': ALANLAR, 'olaylar': olaylar}, ensure_ascii=False, separators=(',', ':')).encode()
    open(CIKTI, 'wb').write(b)
    print(json.dumps({'cikti': os.path.relpath(CIKTI, os.path.join(KOK, '..', '..')), 'olay': len(olaylar), 'bayt': len(b), 'bayt_gzip': len(gzip.compress(b, mtime=0)), 'sha256': sha(b)}, ensure_ascii=False))

def dogrula():
    d, gs = oku_girdi(); ham = open(CIKTI, 'rb').read(); g = json.loads(ham)
    I = {a: i for i, a in enumerate(d['alanlar'])}; J = {a: i for i, a in enumerate(g['alanlar'])}
    S, H = [], 0
    def chk(c, m):
        nonlocal H; S.append(('GEÇTİ' if c else 'KALDI') + ' ' + m); H += (not c)
    E, O = d['olaylar'], g['olaylar']
    chk(g['meta']['sema'] == SEMA and g['alanlar'] == ALANLAR, f'şema {SEMA}, {len(ALANLAR)} alan')
    chk(g['meta']['girdi']['sha256'] == gs, 'meta girdi SHA-256 = çıkarım dosyası')
    chk(g['meta']['ham_girdi_sha256']['isc-gem-cat.csv'] == 'b4e63841e8a6527f1fa6a0ea823b83cfc5b053ab1c7d8746446e34645592cc8d', 'ham CSV SHA-256 zinciri (2026-10-21 kaydı)')
    chk(len(O) == len(E) == 74159 and g['meta']['olay_sayisi'] == len(O), f'olay sayısı {len(O)} (çıkarım {len(E)})')
    chk(all(len(o) == len(ALANLAR) for o in O), 'her olayda tüm alanlar')
    es = {'id': lambda e: 'iscgem:%d' % e[I['eventid']], 't': lambda e: e[I['t']], 'lat': lambda e: e[I['lat']], 'lon': lambda e: e[I['lon']],
          'dep': lambda e: e[I['dep']], 'M': lambda e: e[I['mw']], 'M_unc': lambda e: e[I['mw_unc']], 'M_q': lambda e: e[I['mw_q']],
          'loc_q': lambda e: e[I['loc_q']], 'dep_unc': lambda e: e[I['dep_unc']], 'dep_q': lambda e: e[I['dep_q']]}
    for a, f in es.items():
        fark = sum(1 for e, o in zip(E, O) if f(e) != o[J[a]] or type(f(e)) is not type(o[J[a]]))
        chk(fark == 0, f'{a}: çıkarımla birebir aynı (fark {fark})')
    chk(all(o[J['M_tur']] == 'Mw' for o in O), "M_tur her olayda 'Mw'")
    yk = collections.Counter((e[I['mw_s']], o[J['Mw_yontem']]) for e, o in zip(E, O))
    chk(set(yk) <= {('d', 'dogrudan'), ('p', 'vekil')}, f'Mw_yontem eşlemesi d→dogrudan, p→vekil: {dict((f"{k[0]}→{k[1]}", v) for k, v in yk.items())}')
    nul = {a: sum(1 for o in O if o[J[a]] is None) for a in ALANLAR}
    nul0 = {a: sum(1 for e in E if e[I[a]] is None) for a in ['t', 'lat', 'lon', 'dep', 'dep_unc', 'mw', 'mw_unc', 'mw_q', 'mw_s', 'loc_q', 'dep_q']}
    chk(sum(nul.values()) == sum(nul0.values()), f'null sayısı çıkarımla aynı ({sum(nul.values())}); tahminle doldurulan yok')
    chk(len(set(o[0] for o in O)) == len(O), 'kimlikler tekil')
    chk(all(O[i][1] <= O[i + 1][1] for i in range(len(O) - 1)), 'zamana göre sıralı')
    chk(O[0][1].startswith('1904-04-04') and O[-1][1].startswith('2021-12-31'), f'kapsam {O[0][1]} – {O[-1][1]}')
    ek = json.loads(gzip.decompress(open(os.path.join(KOK, 'out', 'iscgem_v12.1_ek.json.gz'), 'rb').read()))
    eki = set('iscgem:%d' % e[ek['alanlar'].index('eventid')] for e in ek['olaylar'])
    chk(not (eki & set(o[0] for o in O)), f'ek katalog olayı yok (ek katalog {len(eki)} kimlik, kesişim 0)')
    chk(g['meta']['lisans'].startswith('CC BY-SA 3.0') and 'D808B825' in g['meta']['atif'] and os.path.exists(os.path.join(KOK, 'uretim', 'LISANS_ISC-GEM_kuresel.txt')), 'lisans, atıf ve lisans dosyası')
    ozet = {'olay': len(O), 'Mw_yontem': dict(collections.Counter(o[J['Mw_yontem']] for o in O)), 'M_q': dict(collections.Counter(o[J['M_q']] for o in O)),
            'vekil_orani_doneme_gore': {}, 'sha256': sha(ham), 'bayt': len(ham), 'bayt_gzip': len(gzip.compress(ham, mtime=0))}
    for a, b in [(1904, 1964), (1964, 1980), (1980, 2022)]:
        x = [o for o in O if a <= int(o[1][:4]) < b]; ozet['vekil_orani_doneme_gore'][f'{a}–{b - 1}'] = {'N': len(x), 'vekil': sum(o[J['Mw_yontem']] == 'vekil' for o in x)}
    for s in S: print(s)
    print(json.dumps(ozet, ensure_ascii=False))
    print(f"\n{'KALDI' if H else 'GEÇTİ'}: {len(S) - H} geçti, {H} kaldı"); return H, ozet

if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    if k == 'uret': uret()
    elif k == 'dogrula': sys.exit(1 if dogrula()[0] else 0)
    else: sys.exit(__doc__)
