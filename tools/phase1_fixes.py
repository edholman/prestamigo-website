"""Prestamigo phase 1 fixes. Run from the repo root. Byte-level edits; new text uses HTML entities (ASCII).
- index.html: new title/description/og tags, remove duplicate <head>
- footers with 'NMLS 320841</p>': add Equal Housing Opportunity line
"""
import glob

def edit(path, pairs, count_check=True):
    b = open(path, 'rb').read(); n0 = sum(1 for x in b if x > 127)
    for old, new in pairs:
        if count_check:
            assert b.count(old) == 1, (path, old[:60], b.count(old))
        b = b.replace(old, new, 1)
    assert sum(1 for x in b if x > 127) == n0, path  # only ASCII added/removed
    open(path, 'wb').write(b)

TITLE = 'Pr&eacute;stamos para Casa en Espa&ntilde;ol en Arizona | Prestamigo'
DESC = ('Asesor&iacute;a hipotecaria en espa&ntilde;ol para comprar casa en Arizona: primera casa, '
        'pr&eacute;stamos ITIN, inversionistas y extranjeros. Equipo que habla espa&ntilde;ol.')
edit('index.html', [
    (b'<title>Prestamigo - Consejo Hipotecaria</title>',
     ('<title>%s</title>\n    <meta name="description" content="%s">\n    <link rel="canonical" href="https://prestamigo.com/">' % (TITLE, DESC)).encode()),
    (b'<meta property="og:title" content="Prestamigo - Consejo Hipotecaria">',
     ('<meta property="og:title" content="%s">' % TITLE).encode()),
    (b'<!-- End Meta Pixel Code -->\r\n <head>    \r\n', b'<!-- End Meta Pixel Code -->\r\n'),
])

EHO = b'NMLS 320841</p>\r\n                <p>Igualdad de Oportunidades en la Vivienda (Equal Housing Opportunity)</p>'
done = []
for f in sorted(glob.glob('*.html')):
    b = open(f, 'rb').read()
    if b.count(b'NMLS 320841</p>') == 1 and b'Equal Housing' not in b:
        edit(f, [(b'NMLS 320841</p>', EHO)])
        done.append(f)
print('title/description fixed on index.html; Equal Housing added to:', done)
