"""Replace the consent text in the homepage form with the current CONSENT from lead_form.py
(guide pages pick it up from build_guides.py). Safe to rerun."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lead_form import CONSENT

f = 'index.html'
b = open(f, 'rb').read()
b2, n = re.subn(rb'(<span class="lead-consent-text">).*?(</span></label>)', lambda m: m.group(1) + CONSENT.encode('utf-8') + m.group(2), b, flags=re.S)
assert n == 1, n
if b2 != b:
    open(f, 'wb').write(b2)
    print('consent updated in', f)
else:
    print('already current')
