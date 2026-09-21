import urllib.request, ssl, re
sys_import = __import__('sys'); sys_import.stdout.reconfigure(encoding='utf-8')
ctx = ssl._create_unverified_context()

# EPICA download sayfasi
for url in [
    'https://www.emidius.eu/epica/',
    'https://www.emidius.eu/epica/catalogue/',
    'https://www.emidius.eu/epica/download/',
]:
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            html = r.read().decode('utf-8','replace')
            # download/csv/json linkleri
            links = re.findall(r'href=["\']([^"\']+)["\']', html)
            dl = [l for l in links if any(x in l.lower() for x in ['csv','json','xls','download','catalogue','catalog'])]
            print(f'\n{url}')
            for l in dl[:15]:
                print(f'  {l}')
    except Exception as e:
        print(f'ERR {url}: {e}')
