"""Add a contact CTA block above the footer on pages that have no menu (their only contact option was the
removed GHL booking button). Byte-level; new text is ASCII with HTML entities. Safe to rerun."""
PAGES = ['calculadora-poder-de-compra.html', 'deduccion-fiscal.html']
BLOCK = ('    <!-- Contact CTA -->\n'
         '    <section style="background: linear-gradient(135deg, #3498db, #2980b9); color: #fff; text-align: center; padding: 50px 20px;">\n'
         '        <h2 style="margin: 0 0 10px; color: #fff;">&iquest;Listo para comprar tu casa?</h2>\n'
         '        <p style="margin: 0 auto 22px; max-width: 640px; font-size: 1.05rem;">D&eacute;janos tus datos y un asesor que habla espa&ntilde;ol te escribe por mensaje de texto. Gratis y sin compromiso.</p>\n'
         '        <a href="/contacto.html" style="display: inline-block; background: #fff; color: #2980b9; padding: 14px 30px; border-radius: 50px; font-weight: 700; text-decoration: none; box-shadow: 0 6px 20px rgba(0,0,0,0.15);">Revisa tus opciones gratis</a>\n'
         '    </section>\n\n')
for f in PAGES:
    b = open(f, 'rb').read()
    if b'<!-- Contact CTA -->' in b:
        print('already done', f); continue
    marker = b'    <!-- Footer -->'
    assert b.count(marker) == 1, f
    i = b.index(marker)
    nl = '\r\n' if b[i:].startswith(marker + b'\r\n') else '\n'
    b = b.replace(marker, BLOCK.replace('\n', nl).encode('ascii') + marker)
    open(f, 'wb').write(b)
    print('updated', f)
