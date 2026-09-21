import urllib.request, ssl, json, sys
sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl._create_unverified_context()

base = 'https://maps.eu-risk.eucentre.it/api/project/European_Risk_Index_Gridded'
req = urllib.request.Request(base + '/layers/', headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    layers = json.loads(r.read())

print(f'Toplam {len(layers)} katman\n')
for L in layers:
    f = L['fields']
    print(json.dumps(f, indent=2, ensure_ascii=False)[:600])
    print('---')
