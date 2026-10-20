"""S3 grubundaki 13 olay (1963–1964) için Faz 1b'deki iki ISC sorgusunun AYNISI (isc_query, ±5 dk, ±3°;
B1 süzgeçsiz, B2 minmagnitude=5.5). Ekleme yapmaz; yalnız sonuç kaydı."""
import json, sys, time, importlib.util
s = importlib.util.spec_from_file_location('t1b', 'analysis/homog_faz1b/tamlik_1963oncesi.py'); T = importlib.util.module_from_spec(s); s.loader.exec_module(T)
R = [r for r in json.load(open('analysis/homog_faz4/out/inceleme_21.json')) if r['sinif_son'] == 'S3_1963_1964_katalogda_yok']
out = []
for r in R:
    t = T.ts(r['tarih'])
    b1, u1 = T.isc_query(t, r['enlem'], r['boylam']); time.sleep(1.5)
    b2, u2 = T.isc_query(t, r['enlem'], r['boylam'], 5.5); time.sleep(1.5)
    res = 'sorgu hatası' if b1 is None or b2 is None else 'ISC FDSN döndürmüyor' if not b1 else 'ISC var, M≥5,5 süzgecinde yok' if not b2 else 'ISC M≥5,5 ile döndürüyor'
    out.append({**{k: r[k] for k in ('gem_id', 'tarih', 'enlem', 'boylam', 'derinlik', 'Mw', 'kaynak', 'kalite')}, 'B1_url': u1, 'B2_url': u2, 'B1': b1, 'B2': b2, 'sonuc': res})
    print(r['tarih'], r['Mw'], res, [(q['id'], q['mag'], q['mtype'], q['magauthor']) for q in (b1 or [])], flush=True)
json.dump(out, open('analysis/homog_faz4/out/dogrulama_13.json', 'w'), ensure_ascii=False, indent=1)
