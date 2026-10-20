"""
Faz 5 — ISC-GEM katman dosyalarını üretir (yalnız YENİ dosyalar; eq_historical.json'a yazmaz).
Girdi: sabitlenmiş prototip (homog-faz0: faz3 aktarim_kaydi.json, alternatif_buyuklukler.json, faz1 iscgem_v12.1_kutu.json).
Kurallar faz4_merdiven.build_P ile birebir: 1963 öncesi eşleşen olaylarda zaman/konum ISC-GEM'den alınır; 1963+ yalnız Mw;
1963 öncesi eşleşmemiş ISC-GEM (main set, Mw var) olayları eklenir, 16958073 hariç (1910-02-18: M 7,0 korunur, 5,85 alternatif).
Kullanım: python3 analysis/homog_faz5/uret_katman.py <hedef depo kökü>
"""
import json, sys, hashlib, subprocess, os
dst = sys.argv[1]
A = {e['id']: e for e in json.load(open('data/eq_historical.json'))['events']}
L = json.load(open('analysis/homog_faz3/out/aktarim_kaydi.json'))
G = [g for g in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if g['set'] == 'main' and g['mw'] is not None]
Gi = {g['eventid']: g for g in G}
ALT = json.load(open('analysis/homog_faz3/out/alternatif_buyuklukler.json'))
commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
# 1963 öncesi olaylar ISC dönemindedir; eq_historical.json'daki ISC kayıtlarıyla aynı biçim (saat dilimi eki yok) kullanılır
def iso(s): return s.replace(' ', 'T').rstrip('Z')
LIS = {'lisans': 'CC BY-SA 3.0 (unported), http://creativecommons.org/licenses/by-sa/3.0/',
       'atif': 'International Seismological Centre (2026), ISC-GEM Earthquake Catalogue, https://doi.org/10.31905/d808b825 (kullanılan sürüm: v12.1, 2025-11-26; atıf biçimi isc.ac.uk/iscgem/citing.php, erişim 2026-10-21)',
       'atif_makaleler': ['Storchak vd. (2013) SRL doi:10.1785/0220130034', 'Storchak vd. (2015) PEPI doi:10.1016/j.pepi.2014.06.009', 'Di Giacomo vd. (2018) ESSD doi:10.5194/essd-10-1877-2018', 'Bondár vd. (2015) PEPI doi:10.1016/j.pepi.2014.06.002 (konum)', 'Di Giacomo vd. (2015a) PEPI doi:10.1016/j.pepi.2014.06.005 (büyüklük)'],
       'telif': 'Copyright (C) 2025 International Seismological Centre and GEM Foundation (isc.ac.uk/iscgem/download.php, erişim 2026-10-21)',
       'degisiklik': 'Türkiye kutusu alt kümesi; EQ-Live olaylarıyla eşleştirme (Candia & Macedo 2026 eşikleri, koruma kuralı); yalnız Mw, Mw türü, kalite ve konum alanları',
       'paylasim': 'Bu türetilmiş dosya da CC BY-SA 3.0 ile paylaşılır (bkz. data/LISANS_ISC-GEM.txt)'}
used = set(); rows = []
for l in L:
    e = A[l['A_id']]; y = int(e['time'][:4]); g = Gi[l['gem_id']]; used.add(l['gem_id'])
    rows.append({'A_id': l['A_id'], 'Mw': l['M_yeni'], 'mw_src': l['mw_src'], 'q_mw': g['q_mw'], 'unc_mw': g['unc_mw'], 'gem_id': l['gem_id'],
                 'M_eski': l['M_eski'], 'mtype_eski': l['mtype'], 'dt_s': l['dt_s'], 'dr_km': l['dr_km'], 'koruma_istisnasi': l['koruma_istisnasi'],
                 'konum': {'time': iso(g['date']), 'lat': g['lat'], 'lon': g['lon'], 'dep': g['depth']} if y < 1963 else None})
ek = []
for g in G:
    if int(g['date'][:4]) < 1963 and g['eventid'] not in used and g['eventid'] != '16958073':
        ek.append({'id': 'iscgem:' + g['eventid'], 'time': iso(g['date']), 'lat': g['lat'], 'lon': g['lon'], 'dep': g['depth'], 'mag': g['mw'], 'mtype': 'mw',
                   'mw': g['mw'], 'mw_method': 'iscgem_direct' if g['s_mw'] == 'd' else 'iscgem_proxy', 'q_mw': g['q_mw'], 'unc_mw': g['unc_mw'], 'place': '', 'src': 'ISC-GEM'})
ek.sort(key=lambda e: e['time'])
meta = {'surum': 'iscgem-v12.1-homog-2026-10-21', 'uretim': f'analysis/homog_faz5/uret_katman.py @ homog-faz0 {commit[:12]}',
        'prototip': 'homog-faz0 @ f09b26c91525c5ced2c76db11ac06b3bfbad84ea (Mw aktarımı), 68132ec (aday merdiven)',
        'girdi_sha256': {'eq_historical.json': sha('data/eq_historical.json'), 'iscgem_v12.1_kutu.json': sha('analysis/homog_faz1/out/iscgem_v12.1_kutu.json'),
                         'aktarim_kaydi.json': sha('analysis/homog_faz3/out/aktarim_kaydi.json')}, **LIS}
os.makedirs(f'{dst}/data', exist_ok=True)
json.dump({'meta': {**meta, 'aciklama': 'eq_historical.json olaylarına (A_id = id) ISC-GEM v12.1 Mw aktarımı. konum != null ise (1963 öncesi) zaman/konum da ISC-GEM\'den alınır. Varsayılan KAPALI katman; eq_historical.json değişmez.',
           'oncelik': 'mw_authority.json (doğrulanmış) → ISC-GEM → katalog: ISC-GEM aktarılan olay mw_authority kaydıyla da eşleşirse (±60 s, ≤ 50 km; GK74 Faz 2a eşleştiricisi) mw_authority Mw kullanılır. ISC-GEM karşılığı olmayan olaylar değişmez.',
           'n': len(rows)}, 'aktarim': rows, 'alternatif': ALT},
          open(f'{dst}/data/mw_iscgem.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump({'meta': {**meta, 'aciklama': '1904–1962 ISC-GEM v12.1 olayları (main set, Mw var), EQ-Live kataloğunda karşılığı yok. Şema eq_historical.json ile aynı. Yalnız katman açıkken eklenir.', 'n': len(ek)}, 'events': ek},
          open(f'{dst}/data/iscgem_ek_1904_1962.json', 'w'), ensure_ascii=False, separators=(',', ':'))
open(f'{dst}/data/LISANS_ISC-GEM.txt', 'w').write(
    'data/mw_iscgem.json ve data/iscgem_ek_1904_1962.json, ISC-GEM Global Instrumental Earthquake Catalogue v12.1 (released 2025-11-26) verisinden türetilmiştir.\n'
    f"Lisans: {LIS['lisans']}\nAtıf (veri): {LIS['atif']}\nAtıf (makaleler): " + '; '.join(LIS['atif_makaleler']) + f"\n{LIS['telif']}\nYapılan değişiklikler: {LIS['degisiklik']}.\n{LIS['paylasim'].replace(' (bkz. data/LISANS_ISC-GEM.txt)', '')}.\n"
    'Bu lisans yalnız yukarıdaki iki veri dosyası için geçerlidir; deponun diğer içeriğini kapsamaz.\n'
    'Kaynak dosyalar (depoya konmadı): isc-gem.zip sha256 92a52fb933594f0c99f76c96c16fb6a04a360980283e7e22483b587f502949c5\n')
print(len(rows), 'aktarım,', len(ek), 'ek olay,', sum(r['konum'] is not None for r in rows), 'konum aktarımı')
