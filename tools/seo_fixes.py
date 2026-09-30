"""Prestamigo technical SEO fixes (2026-09-30). Run from the repo root, then python tools/build_guides.py. Safe to rerun.

- Titles, meta descriptions, canonicals and og tags on pages that lacked them
- Homepage: keyword H1 + Organization/WebSite/FAQPage JSON-LD; calculadora.html gets an H1
- Remove the non-working ES/EN toggle
- faq.html (thin, old layout) redirects to the guide's FAQ; booked/book are noindex
- Internal links use /comprar-vs-rentar.html (one URL per page)
- Clean sitemap.xml and robots.txt
"""
import html, json, re

SITE = 'https://prestamigo.com'

def rd(f): return open(f, 'rb').read()
def wr(f, b): open(f, 'wb').write(b)
def nl_of(b): return b'\r\n' if b.count(b'\r\n') * 2 > b.count(b'\n') else b'\n'

PAGES = {  # file: (title, description or None to keep, canonical path)
    'index.html': (None, None, '/'),
    'calculadora.html': ('Calculadora de Hipoteca en Espa&ntilde;ol: Pago Mensual | Prestamigo',
                         'Calcula tu pago mensual de hipoteca, compara un refinanciamiento y ve cu&aacute;nto ahorras con pagos adelantados. Calculadora gratis en espa&ntilde;ol.',
                         '/calculadora.html'),
    'calculadora-poder-de-compra.html': ('&iquest;Cu&aacute;nta Casa Puedo Comprar? Calculadora de Poder de Compra | Prestamigo',
                                         'Calcula cu&aacute;nta casa puedes comprar seg&uacute;n tu ingreso, tus deudas y tu enganche. Calculadora gratis en espa&ntilde;ol para compradores en Arizona.',
                                         '/calculadora-poder-de-compra.html'),
    'comprar-vs-rentar.html': ('&iquest;Comprar o Rentar Casa? Calculadora en Espa&ntilde;ol | Prestamigo',
                               '&iquest;Te conviene comprar casa o seguir rentando? Compara el costo real de comprar contra rentar con esta calculadora gratis en espa&ntilde;ol.',
                               '/comprar-vs-rentar.html'),
    'deduccion-fiscal.html': ('Deducci&oacute;n de Intereses Hipotecarios: Calculadora | Prestamigo', None, '/deduccion-fiscal.html'),
    'guia-hipotecaria.html': ('Gu&iacute;a Hipotecaria en Espa&ntilde;ol: Tipos de Pr&eacute;stamo y Documentos | Prestamigo',
                              'Gu&iacute;a en espa&ntilde;ol de los tipos de pr&eacute;stamo hipotecario (convencional, FHA, VA), los documentos que necesitas y consejos para comprar tu primera casa.',
                              '/guia-hipotecaria.html'),
    'tasas-de-interes.html': ('Tasas de Inter&eacute;s Hipotecarias Hoy, en Espa&ntilde;ol | Prestamigo',
                              'Consulta las tasas de inter&eacute;s hipotecarias de hoy y entiende qu&eacute; cambia tu tasa: cr&eacute;dito, enganche y tipo de pr&eacute;stamo. Explicado en espa&ntilde;ol.',
                              '/tasas-de-interes.html'),
    'politica-de-privacidad.html': (None, None, '/politica-de-privacidad.html'),
    'terminos-de-servicio.html': (None, None, '/terminos-de-servicio.html'),
}

TOGGLE = re.compile(rb'[ \t]*<li>\s*<div class="language-toggle">.*?</div>\s*</li>\r?\n', re.S)

for f, (title, desc, path) in PAGES.items():
    b = rd(f); b0 = b; nl = nl_of(b)
    ind = b'    '
    if title:
        b, n = re.subn(rb'<title>.*?</title>', b'<title>' + title.encode() + b'</title>', b, count=1, flags=re.S)
        assert n == 1, f
    add = []
    if desc:
        if b'name="description"' in b:
            b = re.sub(rb'<meta name="description" content="[^"]*">', b'<meta name="description" content="' + desc.encode() + b'">', b, count=1)
        else:
            add.append(b'<meta name="description" content="' + desc.encode() + b'">')
    if b'rel="canonical"' not in b:
        add.append(b'<link rel="canonical" href="' + (SITE + path).encode() + b'">')
    if b'property="og:title"' not in b:
        t = re.search(rb'<title>(.*?)</title>', b, re.S).group(1)
        d = re.search(rb'<meta name="description" content="([^"]*)"', b)
        add += [b'<meta property="og:type" content="website">', b'<meta property="og:title" content="' + t + b'">',
                b'<meta property="og:url" content="' + (SITE + path).encode() + b'">', b'<meta property="og:locale" content="es_US">',
                b'<meta property="og:image" content="https://i.imgur.com/t3pRlvV.png">']
        if d: add.append(b'<meta property="og:description" content="' + d.group(1) + b'">')
    if add:
        m = re.search(rb'</title>', b)
        b = b[:m.end()] + b''.join(nl + ind + a for a in add) + b[m.end():]
    b = TOGGLE.sub(b'', b)
    b = b.replace(b'href="/comprar-vs-rentar"', b'href="/comprar-vs-rentar.html"')
    if b != b0:
        wr(f, b); print('updated', f)

# Homepage: keyword H1, subtitle, schema
f = 'index.html'; b = rd(f); nl = nl_of(b)
b = b.replace('<h1 style="font-size: 2.2rem;">Consejo Hipotecaria</h1>'.encode(),
              '<h1 style="font-size: 2.2rem;">Préstamos para casa en Arizona, explicados en español</h1>'.encode())
b = b.replace('<p>Guía paso a paso para compradores en EE.UU.</p>'.encode(),
              '<p>Te guiamos paso a paso: primera casa, ITIN, DACA, trabajadores independientes, inversionistas y extranjeros.</p>'.encode())
if b'"@type": "Organization"' not in b:
    s = b.decode('utf-8')
    faqs = []
    for q, a in re.findall(r'<div class="faq-question">\s*<h3>(.*?)</h3>.*?<div class="faq-answer">\s*<p>(.*?)</p>', s, re.S):
        faqs.append({'@type': 'Question', 'name': html.unescape(re.sub('<[^>]+>', '', q)).strip(),
                     'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(re.sub('<[^>]+>', '', a)).strip()}})
    assert len(faqs) >= 5, len(faqs)
    ld = [
        {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Prestamigo', 'legalName': 'INCITE LLC',
         'url': SITE + '/', 'logo': 'https://i.imgur.com/t3pRlvV.png', 'email': 'info@prestamigo.com', 'telephone': '+1-480-612-3718',
         'description': 'Educación hipotecaria en español para compradores de casa en Arizona: primera casa, ITIN, DACA, inversionistas y extranjeros.',
         'areaServed': {'@type': 'State', 'name': 'Arizona'}, 'knowsLanguage': ['es', 'en'],
         'sameAs': ['https://www.youtube.com/@Mi_Prestamigo']},
        {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Prestamigo', 'url': SITE + '/', 'inLanguage': 'es'},
        {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': faqs},
    ]
    tags = ''.join(nl.decode() + '    <script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)
    b = b.replace(b'</head>', tags.encode('utf-8') + nl + b'</head>', 1)
wr(f, b); print('homepage H1 + schema')

# calculadora.html: add an H1 above the tabs
f = 'calculadora.html'; b = rd(f)
if b'<h1' not in b:
    nl = nl_of(b)
    old = b'    <div class="container">' + nl + b'        <div class="tab-system">'
    assert b.count(old) == 1
    b = b.replace(old, b'    <div class="container">' + nl +
                  '        <h1 style="text-align: center; color: #2c3e50; margin: 30px 0 10px; font-size: 2rem;">Calculadora de hipoteca en español</h1>'.encode() + nl +
                  b'        <div class="tab-system">')
    wr(f, b); print('calculadora H1')

# deduccion-fiscal.html: H1 matches the topic
f = 'deduccion-fiscal.html'; b = rd(f)
b = b.replace('<h1><i class="fas fa-receipt"></i> Calculadora de Ahorros en Intereses</h1>'.encode(),
              '<h1><i class="fas fa-receipt"></i> Calculadora de Deducción de Intereses Hipotecarios</h1>'.encode())
wr(f, b)

# noindex utility pages
for f in ['booked.html', 'book.html']:
    b = rd(f)
    if b'name="robots"' not in b:
        nl = nl_of(b)
        m = re.search(rb'<meta charset="[^"]*">', b, re.I)
        b = b[:m.end()] + nl + b'    <meta name="robots" content="noindex">' + b[m.end():]
        b = b.replace(b'href="/comprar-vs-rentar"', b'href="/comprar-vs-rentar.html"')
        wr(f, b); print('noindex', f)

# faq.html -> the guide's FAQ section
GUIDE = SITE + '/como-calificar-prestamo-hipotecario-arizona.html'
wr('faq.html', ('<!DOCTYPE html>\r\n<html lang="es">\r\n<head>\r\n    <meta charset="UTF-8">\r\n'
                '    <title>Preguntas Frecuentes | Prestamigo</title>\r\n'
                '    <link rel="canonical" href="%s">\r\n'
                '    <meta http-equiv="refresh" content="0; url=/como-calificar-prestamo-hipotecario-arizona.html#preguntas">\r\n'
                '    <script>window.location.replace("/como-calificar-prestamo-hipotecario-arizona.html#preguntas");</script>\r\n'
                '</head>\r\n<body>\r\n    <p>Las preguntas frecuentes ahora est&aacute;n en nuestra '
                '<a href="/como-calificar-prestamo-hipotecario-arizona.html#preguntas">gu&iacute;a para calificar</a>.</p>\r\n'
                '</body>\r\n</html>\r\n' % GUIDE).encode())
print('faq.html -> guide FAQ')

# Layout + blog template links
for f in ['_layouts/default.html', 'blog/post.html', 'blog/index.html']:
    b = rd(f); b2 = b.replace(b'href="/comprar-vs-rentar"', b'href="/comprar-vs-rentar.html"')
    if b2 != b: wr(f, b2); print('links', f)

# sitemap.xml
URLS = [('/', '1.0', 'weekly'), ('/como-calificar-prestamo-hipotecario-arizona.html', '0.9', 'monthly'),
        ('/contacto.html', '0.8', 'monthly'), ('/guia-hipotecaria.html', '0.8', 'monthly'),
        ('/calculadora-poder-de-compra.html', '0.8', 'monthly'), ('/calculadora.html', '0.7', 'monthly'),
        ('/comprar-vs-rentar.html', '0.7', 'monthly'), ('/tasas-de-interes.html', '0.7', 'weekly'),
        ('/deduccion-fiscal.html', '0.6', 'yearly'), ('/blog/', '0.6', 'weekly'),
        ('/hipotecas/2025/05/05/concesiones-vendedor-primeros-compradores.html', '0.6', 'yearly'),
        ('/politica-de-privacidad.html', '0.2', 'yearly'), ('/terminos-de-servicio.html', '0.2', 'yearly')]
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p, pr, cf in URLS:
    xml += ['  <url>', '    <loc>%s%s</loc>' % (SITE, p), '    <lastmod>2026-09-30</lastmod>',
            '    <changefreq>%s</changefreq>' % cf, '    <priority>%s</priority>' % pr, '  </url>']
xml.append('</urlset>')
wr('sitemap.xml', ('\n'.join(xml) + '\n').encode())
print('sitemap.xml: %d URLs' % len(URLS))

wr('robots.txt', b'User-agent: *\nAllow: /\n\nSitemap: https://prestamigo.com/sitemap.xml\n')
print('robots.txt cleaned')
