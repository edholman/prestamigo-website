"""Build Prestamigo guide pages from tools/content/<slug>.html. Run from the repo root: python tools/build_guides.py

Reuses the site CSS, header and footer from guia-hipotecaria.html (so the look matches), swaps the GHL booking
modal for the native lead form (/assets/lead-form.js), and adds SEO tags, Article + FAQPage JSON-LD and
click-to-play YouTube embeds. Output is UTF-8 with CRLF like the rest of the site.
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SITE = 'https://prestamigo.com'
SRC = open('guia-hipotecaria.html', 'rb').read().decode('utf-8').replace('\r\n', '\n')

def between(s, start, end):
    i = s.index(start); j = s.index(end, i) + len(end)
    return s[i:j]

BASE_CSS = between(SRC, '<style>', '</style>')
HEADER = between(SRC, '<!-- Header -->', '</header>').replace(
    '<a href="#" onclick="openBookingModal(); return false;">Contacto</a>', '<a href="#contacto">Contacto</a>')
FOOTER = between(SRC, '<!-- Footer -->', '</footer>')
MENU_JS = between(SRC, '// Hamburger Menu for Mobile Navigation', '// Language Toggle').replace('// Language Toggle', '').rstrip()
assert 'openBookingModal' not in HEADER + FOOTER

from lead_form import CONSENT, form_html

PAGE_CSS = '''
        .container.narrow { max-width: 860px; }
        ul.guide-list { list-style: none; padding-left: 0; }
        .guide-hero .hero-cta, .cta-strip .hero-cta { display: inline-block; margin-top: 18px; background: #fff; color: #2980b9; padding: 14px 28px; border-radius: 50px; font-weight: 700; text-decoration: none; box-shadow: 0 6px 20px rgba(0,0,0,0.15); }
        .guide-hero .updated { font-size: 0.85rem; opacity: 0.85; margin-top: 14px; }
        .answer-box { background: #eef6fc; border-left: 5px solid #3498db; border-radius: 10px; padding: 22px 26px; margin: 10px 0 30px; }
        .answer-box h2 { margin-top: 0; color: #2c3e50; }
        .answer-box ol li { margin-bottom: 10px; }
        .toc { display: block; background: #f8f9fa; border-radius: 10px; padding: 18px 24px; margin-bottom: 40px; }
        .toc ul { columns: 2; margin: 10px 0 0; padding-left: 18px; }
        .toc a { color: #2980b9; text-decoration: none; }
        .table-wrap { overflow-x: auto; }
        .req-table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
        .req-table th { background: #2c3e50; color: #fff; text-align: left; padding: 10px; }
        .req-table td { border-bottom: 1px solid #e5e7eb; padding: 10px; vertical-align: top; }
        .req-table tbody tr:nth-child(even) { background: #f8f9fa; }
        .small { font-size: 0.85rem; color: #6c757d; }
        .center { text-align: center; }
        .guide-card.example { border-left: 4px solid #27ae60; }
        .alert-box { background: #fff8e6; border-left: 5px solid #f39c12; border-radius: 8px; padding: 16px 20px; margin: 20px 0; }
        .cta-strip { background: linear-gradient(135deg, #3498db, #2980b9); color: #fff; border-radius: 12px; padding: 26px; text-align: center; margin: 10px 0 50px; }
        .cta-strip p { margin: 0; font-size: 1.1rem; }
        .guide-section a:not(.hero-cta) { color: #2980b9; }
        .video-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin: 20px 0; }
        .video-grid.one { grid-template-columns: 1fr; max-width: 560px; }
        .yt { position: relative; aspect-ratio: 16 / 9; background: #000 center / cover no-repeat; border-radius: 10px; overflow: hidden; cursor: pointer; }
        .yt button { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; background: transparent; cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; color: #fff; font: 600 0.95rem 'Poppins', sans-serif; padding: 12px; }
        .yt button .play { width: 68px; height: 48px; border-radius: 12px; background: #e62117; display: flex; align-items: center; justify-content: center; }
        .yt button .play::after { content: ''; border-style: solid; border-width: 10px 0 10px 17px; border-color: transparent transparent transparent #fff; margin-left: 4px; }
        .yt iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
        ol.steps li { margin-bottom: 10px; }
        details.faq { background: #f8f9fa; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; }
        details.faq summary { font-weight: 600; cursor: pointer; color: #2c3e50; }
        details.faq p { margin: 10px 0 0; }
        .form-section { background: #f4f8fb; border-radius: 14px; padding: 30px 20px; }
        .form-section h2 { justify-content: center; text-align: center; }
        .sources { border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 40px; font-size: 0.9rem; }
        .sources a { color: #2980b9; }
        .float-cta { position: fixed; bottom: 24px; right: 24px; z-index: 999; background: linear-gradient(135deg, #3498db, #2980b9); color: #fff; padding: 14px 24px; border-radius: 50px; font-weight: 600; text-decoration: none; box-shadow: 0 6px 20px rgba(52,152,219,0.4); }
        @media (max-width: 768px) {
            .video-grid { grid-template-columns: 1fr; }
            .toc ul { columns: 1; }
            .float-cta { bottom: 16px; right: 16px; padding: 12px 18px; font-size: 0.95rem; }
        }
'''

YT_JS = '''
        // Click-to-play YouTube (loads the player only when clicked)
        document.querySelectorAll('.yt').forEach(function (box) {
            var id = box.getAttribute('data-id'), title = box.getAttribute('data-title') || 'Video';
            box.style.backgroundImage = 'url(https://i.ytimg.com/vi/' + id + '/hqdefault.jpg)';
            var b = document.createElement('button');
            b.type = 'button';
            b.setAttribute('aria-label', 'Ver video: ' + title);
            b.innerHTML = '<span class="play"></span>';
            b.addEventListener('click', function () {
                var f = document.createElement('iframe');
                f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
                f.title = title;
                f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture';
                f.allowFullscreen = true;
                box.innerHTML = '';
                box.appendChild(f);
            });
            box.appendChild(b);
        });
'''

def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()

def build(slug, content, title, h1_title, desc, form_name, published, article=True):
    body = open('tools/content/%s.html' % content, encoding='utf-8').read().replace('\r\n', '\n')
    body = body.replace('%(FORM)s', form_html(form_name))
    url = '%s/%s' % (SITE, slug)
    faqs = [{'@type': 'Question', 'name': strip_tags(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}}
            for q, a in re.findall(r'<summary>(.*?)</summary>\s*<p>(.*?)</p>', body, re.S)]
    videos = re.findall(r'data-id="([\w-]{11})"', body)
    ld = [
        {'@context': 'https://schema.org', '@type': 'Article', 'headline': h1_title, 'description': desc, 'inLanguage': 'es',
         'datePublished': published, 'dateModified': published, 'mainEntityOfPage': url,
         'image': ('https://i.ytimg.com/vi/%s/hqdefault.jpg' % videos[0]) if videos else 'https://i.imgur.com/t3pRlvV.png',
         'author': {'@type': 'Organization', 'name': 'Prestamigo', 'url': SITE + '/'},
         'publisher': {'@type': 'Organization', 'name': 'Prestamigo', 'logo': {'@type': 'ImageObject', 'url': 'https://i.imgur.com/t3pRlvV.png'}}},
        {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': faqs},
    ]
    if not article: ld = []
    if not faqs: ld = [x for x in ld if x['@type'] != 'FAQPage']
    ld_html = '\n'.join('    <script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)
    page = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%(title)s</title>
    <meta name="description" content="%(desc)s">
    <link rel="canonical" href="%(url)s">
    <meta property="og:type" content="%(ogtype)s">
    <meta property="og:title" content="%(title)s">
    <meta property="og:description" content="%(desc)s">
    <meta property="og:url" content="%(url)s">
    <meta property="og:image" content="%(ogimg)s">
    <meta property="og:locale" content="es_US">
    <link rel="icon" href="/favicon.png">
%(ld)s
    %(css)s
    <style>%(page_css)s    </style>
    <link rel="stylesheet" href="/assets/lead-form.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    %(header)s

%(body)s
    %(footer)s

    <script>
        %(menu_js)s
%(yt_js)s    </script>
    <script src="/assets/lead-form.js"></script>
    <script src="/js/tracking.js"></script>
</body>
</html>
''' % dict(title=title, desc=desc, url=url, ld=ld_html, css=BASE_CSS, page_css=PAGE_CSS, header=HEADER, body=body.rstrip() + '\n',
           footer=FOOTER, menu_js=MENU_JS, yt_js=YT_JS, ogtype='article' if article else 'website', ogimg=('https://i.ytimg.com/vi/%s/hqdefault.jpg' % videos[0]) if videos else 'https://i.imgur.com/t3pRlvV.png')
    for bad in ('—', '–'):
        assert bad not in body + PAGE_CSS + CONSENT, 'dash found'
    assert len(html.unescape(desc)) <= 160, len(html.unescape(desc))
    open(slug + '.html', 'wb').write(page.replace('\n', '\r\n').encode('utf-8'))
    print('%s.html: %d FAQs, %d videos, %d bytes' % (slug, len(faqs), len(videos), len(page)))


build(slug='como-calificar-prestamo-hipotecario-arizona', content='como-calificar',
      title='C&oacute;mo Calificar para un Pr&eacute;stamo Hipotecario en Arizona (2026) | Prestamigo',
      h1_title='Cómo calificar para un préstamo hipotecario en Arizona',
      desc=('Requisitos 2026 para comprar casa en Arizona: cr&eacute;dito, enganche, deudas e ingresos. FHA, convencional, '
            'ITIN, DSCR, extranjeros e independientes, en espa&ntilde;ol.'),
      form_name='guia_como_calificar', published='2026-09-30')

build(slug='contacto', content='contacto',
      title='Contacto: Asesor&iacute;a Hipotecaria Gratis en Espa&ntilde;ol | Prestamigo',
      h1_title='Contacto', form_name='contacto', published='2026-09-30', article=False,
      desc=('D&eacute;janos tus datos y un asesor que habla espa&ntilde;ol te escribe por mensaje de texto. Primera casa, ITIN, '
            'DACA, inversionistas y extranjeros en Arizona.'))

build(slug='comprar-casa-con-daca-arizona', content='daca',
      title='Comprar Casa con DACA en Arizona (2026): S&iacute; Se Puede | Prestamigo',
      h1_title='Comprar casa con DACA en Arizona',
      desc=('S&iacute; puedes comprar casa con DACA en Arizona. FHA ya no acepta DACA, pero el pr&eacute;stamo convencional s&iacute;, '
            'desde 3% de enganche. Requisitos y documentos.'),
      form_name='guia_daca', published='2026-09-30')

build(slug='prestamo-itin-arizona', content='itin',
      title='Pr&eacute;stamo ITIN en Arizona: Comprar Casa sin Seguro Social | Prestamigo',
      h1_title='Préstamo ITIN para comprar casa en Arizona',
      desc=('S&iacute; puedes comprar casa en Arizona con ITIN. Enganche de 10% a 20%, cr&eacute;dito desde 580 o cr&eacute;dito alternativo, '
            'requisitos y documentos, en espa&ntilde;ol.'),
      form_name='guia_itin', published='2026-09-30')

build(slug='prestamo-fha-arizona-requisitos', content='fha',
      title='Pr&eacute;stamo FHA en Arizona: Requisitos 2026 | Prestamigo',
      h1_title='Préstamo FHA en Arizona: requisitos 2026',
      desc=('Requisitos del pr&eacute;stamo FHA en Arizona para 2026: cr&eacute;dito desde 580, 3.5% de enganche, l&iacute;mites por condado '
            'y seguro hipotecario, en espa&ntilde;ol.'),
      form_name='guia_fha', published='2026-09-30')

build(slug='prestamo-trabajadores-independientes-arizona', content='independientes',
      title='Pr&eacute;stamo para Trabajadores Independientes en Arizona | Prestamigo',
      h1_title='Préstamo para trabajadores independientes en Arizona',
      desc=('&iquest;Trabajas por tu cuenta o con 1099? Califica para comprar casa en Arizona con tus impuestos o con estados de cuenta '
            'del banco. Requisitos y ejemplo.'),
      form_name='guia_independientes', published='2026-09-30')

build(slug='prestamo-dscr-arizona', content='dscr',
      title='Pr&eacute;stamo DSCR en Arizona: Compra con la Renta | Prestamigo',
      h1_title='Préstamo DSCR en Arizona: compra casas de renta con la renta',
      desc=('Pr&eacute;stamo DSCR para inversionistas en Arizona: califica con la renta de la propiedad, sin comprobar ingresos. '
            'Requisitos, ejemplo y LLC, en espa&ntilde;ol.'),
      form_name='guia_dscr', published='2026-09-30')

build(slug='como-sacar-itin', content='sacar-itin',
      title='C&oacute;mo Sacar un ITIN: Paso a Paso y Gratis (2026) | Prestamigo',
      h1_title='Cómo sacar un ITIN: paso a paso',
      desc=('C&oacute;mo sacar tu ITIN gratis: forma W-7, documentos, d&oacute;nde entregarla en Arizona y por qu&eacute; lo necesitas para '
            'comprar casa o abrir un negocio.'),
      form_name='guia_sacar_itin', published='2026-09-30')

build(slug='como-abrir-llc-arizona', content='abrir-llc',
      title='C&oacute;mo Abrir una LLC en Arizona: Paso a Paso (2026) | Prestamigo',
      h1_title='Cómo abrir una LLC en Arizona: paso a paso',
      desc=('C&oacute;mo registrar tu LLC en Arizona por $50, aunque tengas ITIN: nombre, agente estatutario, publicaci&oacute;n, '
            'EIN y por qu&eacute; ayuda a financiar.'),
      form_name='guia_abrir_llc', published='2026-09-30')

build(slug='como-sacar-ein', content='sacar-ein',
      title='C&oacute;mo Sacar un EIN Gratis para tu Negocio (2026) | Prestamigo',
      h1_title='Cómo sacar un EIN para tu negocio: paso a paso',
      desc=('C&oacute;mo sacar el EIN de tu negocio gratis en irs.gov, tambi&eacute;n con ITIN. Paso a paso y por qu&eacute; lo necesitas '
            'para el banco y para financiar.'),
      form_name='guia_sacar_ein', published='2026-09-30')
