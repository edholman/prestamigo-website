"""Add the "En qué parte de Arizona" select to the homepage lead form (guide pages get it from build_guides.py).
Safe to rerun."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lead_form import AREA_SELECT

f = 'index.html'
b = open(f, 'rb').read()
if b'name="area"' in b:
    print('already done')
else:
    marker = b'<select id="lf-goal" name="goal" data-to-message="Busca">'
    i = b.index(marker)
    j = b.index(b'</select>', i) + len(b'</select>')
    nl = b'\r\n' if b[j:j + 2] == b'\r\n' else b'\n'
    b = b[:j] + nl + AREA_SELECT.replace('\n', nl.decode()).encode('utf-8') + b[j:]
    open(f, 'wb').write(b)
    print('added area field to', f)
