"""Footer cleanup: copyright year 2024 -> 2026, remove the duplicate 'Igualdad de Vivienda Prestamista' line
(the 'Igualdad de Oportunidades en la Vivienda (Equal Housing Opportunity)' line stays). Byte-level edits."""
import glob, re
done = []
for f in sorted(glob.glob('*.html')):
    b = open(f, 'rb').read(); orig = b
    b, n1 = re.subn(rb'[ \t]*<p>Igualdad de Vivienda Prestamista</p>[ \t]*\r?\n(?:[ \t]*\r?\n)?', b'', b)
    b = b.replace(b'&copy; 2024', b'&copy; 2026').replace('© 2024'.encode(), '© 2026'.encode())
    if b != orig:
        assert n1 <= 1 and b'Equal Housing Opportunity' in b, f
        open(f, 'wb').write(b); done.append(f)
print('updated:', done)
