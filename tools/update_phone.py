"""Replace the old Prestamigo phone (480) 612-3718 with the CRM number (602) 610-8305 in every format.
Byte-level, safe to rerun. Run from the repo root, then python tools/build_guides.py."""
import glob

PAIRS = [(b'+1-480-612-3718', b'+1-602-610-8305'), (b'+14806123718', b'+16026108305'),
         (b'(480) 612-3718', b'(602) 610-8305'), (b'480-612-3718', b'602-610-8305')]
files = sorted(set(glob.glob('*.html') + glob.glob('blog/*.html') + glob.glob('_layouts/*.html') + glob.glob('_includes/*.html')
                   + glob.glob('_posts/*.md') + glob.glob('tools/*.py') + glob.glob('js/*.js') + ['_config.yml']))
for f in files:
    if f.endswith('update_phone.py'):
        continue
    b = open(f, 'rb').read(); b0 = b
    for old, new in PAIRS:
        b = b.replace(old, new)
    if b != b0:
        open(f, 'wb').write(b); print('updated', f)
