"""Point every contact link/button on the site at WhatsApp (602) 610-8305 instead of the contact form.
Pages that load /assets/whatsapp.js get a page-specific message; others keep the generic one below.
Byte-level, safe to rerun. Run from the repo root, then python tools/build_guides.py."""
import glob, re

WA = 'https://wa.me/16026108305?text=Hola%2C%20vi%20su%20p%C3%A1gina%20de%20Prestamigo%20y%20quiero%20informaci%C3%B3n%20para%20comprar%20casa.'
def attr(where):
    return 'href="' + WA + '" target="_blank" rel="noopener" data-wa="' + where + '"'

files = sorted(set(glob.glob('*.html') + glob.glob('blog/*.html') + glob.glob('_layouts/*.html')))
for f in files:
    if f == 'book.html':
        continue
    b = open(f, 'rb').read(); b0 = b
    # menu "Contacto" / "Consulta Gratis" links
    b = re.sub(rb'href="(?:/contacto\.html|#contacto)"( data-translate="nav-contacto")?>(Contacto|Consulta Gratis)',
               lambda m: attr('nav').encode() + (m.group(1) or b'') + b'>' + m.group(2), b)
    # blue CTA boxes on the calculator pages
    b = re.sub(rb'<a href="/contacto\.html"( style="[^"]*")>Revisa tus opciones gratis</a>',
               lambda m: b'<a ' + attr('cta_box').encode() + m.group(1) + '>¿Tienes preguntas? Escríbenos por WhatsApp</a>'.encode(), b)
    # rates page "Obtener Precalificacion" button
    b = b.replace(b'<a href="/contacto.html" class="cta-button">', b'<a ' + attr('rates_cta').encode() + b' class="cta-button">')
    # cache-bust the WhatsApp script
    b = b.replace(b'src="/assets/whatsapp.js"', b'src="/assets/whatsapp.js?v=2"')
    if b != b0:
        open(f, 'wb').write(b); print('updated', f)
