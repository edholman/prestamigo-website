"""Replace the GHL booking calendar with the native lead form across the site. Run from the repo root, then
run tools/build_guides.py (it reads its header/footer from guia-hipotecaria.html). Safe to rerun.

- Removes the floating "Agendar Consulta" button, the booking modal, its scripts and GHL form_embed.js.
- Contacto links and CTA buttons go to /contacto.html (homepage: #contacto, where the form now sits).
- book.html now redirects to /contacto.html so old links and ads keep working.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lead_form import form_html

GHL = re.compile(rb'https://api\.leadconnectorhq\.com/widget/booking/\w+')
EMBED = b'    <script src="https://link.msgsndr.com/js/form_embed.js" type="text/javascript"></script>'
NAV_OLD = b'href="#" onclick="openBookingModal(); return false;"'
GHL_BUTTON = re.compile(rb'[ \t]*<!-- Go High Level Contact Button -->\r?\n[ \t]*<button onclick="openBookingModal\(\)" '
                        rb'class="contact-button">.*?</button>\r?\n(?:[ \t]*\r?\n)?', re.S)

def read(f): return open(f, 'rb').read()
def write(f, b): open(f, 'wb').write(b)
def lone_lf(b): return b.count(b'\n') - b.count(b'\r\n')

def cut(b, start, end, keep_end=False):
    """Remove b[start marker : end marker] (end included unless keep_end). The region must be booking code only."""
    i = b.index(start); j = b.index(end, i)
    if not keep_end:
        j += len(end)
        if b[j:j + 2] == b'\r\n': j += 2
        elif b[j:j + 1] == b'\n': j += 1
    region = b[i:j]
    assert b'bookingModal' in region and b'amburger' not in region and b'tracking.js' not in region, region[:200]
    return b[:i] + b[j:]

def check(f, b, lf_before):
    for bad in (b'openBookingModal', b'bookingModal', b'leadconnectorhq', b'msgsndr', b'calendly'):
        assert bad not in b, (f, bad)
    assert lone_lf(b) <= lf_before, (f, 'line endings changed')

# 1. Pages with the floating button + modal + script block
for f in ['calculadora.html', 'calculadora-poder-de-compra.html', 'comprar-vs-rentar.html', 'deduccion-fiscal.html',
          'guia-hipotecaria.html', 'index.html']:
    b = read(f)
    if b'bookingModal' not in b:
        print('already done', f); continue
    lf0 = lone_lf(b)
    b = GHL_BUTTON.sub(b'', b)
    start = b'    <!-- Floating Contact Button -->' if b'<!-- Floating Contact Button -->' in b else b'    <!-- Booking Modal -->'
    b = cut(b, start, EMBED)
    b = b.replace(NAV_OLD, b'href="#contacto"' if f == 'index.html' else b'href="/contacto.html"')
    if f == 'index.html':
        nl = '\r\n' if b'    <!-- Footer -->\r\n' in b else '\n'
        b = b.replace(b'class="cta-button">Agende una consulta gratis</a>', 'class="cta-button">Solicite su consulta gratis</a>'.encode())
        section = ('    <!-- Contact form (native lead form, replaces the GHL calendar) -->\n'
                   '    <section class="contact-section" id="contacto">\n'
                   '        <div class="container">\n'
                   '            <h2>Revisa tus opciones gratis</h2>\n'
                   '            <p>Déjanos tus datos y un asesor que habla español te escribe por mensaje de texto. Sin compromiso.</p>\n'
                   + form_html('home_page') + '\n'
                   '        </div>\n'
                   '    </section>\n\n').replace('\n', nl).encode()
        assert b.count(b'    <!-- Footer -->') == 1
        b = b.replace(b'    <!-- Footer -->', section + b'    <!-- Footer -->')
        head = ('    <link rel="stylesheet" href="/assets/lead-form.css">' + nl +
                '    <style>.contact-section { padding: 60px 0; background: #f4f8fb; text-align: center; } '
                '.contact-section h2 { color: #2c3e50; margin-bottom: 10px; }</style>' + nl + '</head>').encode()
        assert b.count(b'</head>') == 1
        b = b.replace(b'</head>', head)
        b = b.replace(b'    <script src="js/tracking.js"></script>',
                      ('    <script src="/assets/lead-form.js"></script>' + nl + '    <script src="js/tracking.js"></script>').encode())
        assert b.count(b'lead-form.js') == 1
        lf0 = lone_lf(b) if nl == '\n' else lf0
    check(f, b, lf0); write(f, b); print('updated', f)

# 2. Rates page: the booking script also holds the mobile menu code, so remove only the booking parts
f = 'tasas-de-interes.html'
b = read(f)
if b'bookingModal' in b:
    lf0 = lone_lf(b)
    b = cut(b, b'    <!-- Floating Contact Button -->', b'    <script>', keep_end=True)
    i = b.index(b'        // Preload the booking widget'); j = b.index(b'        // Add spinning animation', i)
    b = b[:i] + b[j:]
    b = re.sub(re.escape(EMBED) + rb'\r?\n', b'', b)
    b = b.replace(NAV_OLD, b'href="/contacto.html"')
    b, n = re.subn(rb'<button onclick="openBookingModal\(\)" class="cta-button">(\s*.*?\s*)</button>',
                   rb'<a href="/contacto.html" class="cta-button">\1</a>', b, flags=re.S)
    assert n == 1 and b'Hamburger Menu' in b
    check(f, b, lf0); write(f, b); print('updated', f)

# 3. Simple link swaps
for f, old, new in [
    ('booked.html', b'href="#" onclick="openBookingModal()"', b'href="/contacto.html"'),
    ('faq.html', b'href="https://calendly.com/prestamigo"', b'href="/contacto.html"'),
    ('blog/post.html', b'href="https://api.leadconnectorhq.com/widget/booking/qBoIcTx0Mr1zIeWeWD9D"', b'href="/contacto.html"'),
]:
    b = read(f)
    if old in b:
        lf0 = lone_lf(b); b = b.replace(old, new); check(f, b, lf0); write(f, b); print('updated', f)

f = '_layouts/default.html'
b = read(f); lf0 = lone_lf(b)
b, n = re.subn(rb'<a href="https://api\.leadconnectorhq\.com/widget/booking/\w+"(\s*class="contact-btn")\s*target="_blank"\s*rel="noopener noreferrer">',
               rb'<a href="/contacto.html"\1>', b)
if n: check(f, b, lf0); write(f, b); print('updated', f)

# 4. book.html -> redirect to the contact form
f = 'book.html'
b = read(f)
if GHL.search(b):
    lf0 = lone_lf(b)
    b = GHL.sub(b'/contacto.html', b)
    for old, new in [('Reserva una Cita | Prestamigo', 'Contacto | Prestamigo'),
                     ('Agenda una consulta con Prestamigo', 'Contacta a Prestamigo'),
                     ('<h1>Agenda Tu Consulta</h1>', '<h1>Contacto</h1>'),
                     ('Estás siendo redirigido a nuestro calendario de reservas.', 'Te estamos llevando a nuestro formulario de contacto.'),
                     ('// Redirección inmediata a la página de reservas', '// Redirección inmediata al formulario de contacto')]:
        b = b.replace(old.encode(), new.encode())
    check(f, b, lf0); write(f, b); print('updated', f)

# 5. Sitemap: book.html -> contacto.html, add the new guide
f = 'sitemap.xml'
b = read(f)
nl = b'\r\n' if b'\r\n' in b else b'\n'
b = b.replace(b'<loc>https://prestamigo.com/book.html</loc>', b'<loc>https://prestamigo.com/contacto.html</loc>')
if b'como-calificar' not in b:
    entry = nl.join([b'  <url>', b'    <loc>https://prestamigo.com/como-calificar-prestamo-hipotecario-arizona.html</loc>',
                     b'    <lastmod>2026-09-30</lastmod>', b'    <changefreq>monthly</changefreq>', b'    <priority>0.9</priority>',
                     b'  </url>', b'', b'</urlset>'])
    b = b.replace(b'</urlset>', entry)
write(f, b); print('updated', f)
