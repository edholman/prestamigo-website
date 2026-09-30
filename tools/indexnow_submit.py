"""Submit Prestamigo URLs to IndexNow (Bing, Yandex, etc.). Run from the repo root after the site deploys.

    python tools/indexnow_submit.py            # every URL in sitemap.xml
    python tools/indexnow_submit.py /page.html # specific paths
"""
import json, re, sys, urllib.request

HOST = 'prestamigo.com'
KEY = 'b9797bed30639b0dc7f8acc2c2b96b3a'  # key file served at https://prestamigo.com/<KEY>.txt

urls = ['https://%s%s' % (HOST, p) for p in sys.argv[1:]] or re.findall(r'<loc>([^<]+)</loc>', open('sitemap.xml', encoding='utf-8').read())
body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': 'https://%s/%s.txt' % (HOST, KEY), 'urlList': urls}).encode()
req = urllib.request.Request('https://www.bing.com/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow:', r.status, '(%d URLs)' % len(urls))
except urllib.error.HTTPError as e:
    print('IndexNow error:', e.code, e.read()[:300])
