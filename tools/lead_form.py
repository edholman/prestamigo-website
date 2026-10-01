"""Prestamigo lead form markup (shared by build_guides.py and switch_to_form.py). Posts via /assets/lead-form.js."""

CONSENT = ('Al marcar esta casilla, acepto recibir llamadas y mensajes de texto de Prestamigo (INCITE LLC) '
           'al n&#250;mero proporcionado, incluidos mensajes enviados con tecnolog&#237;a '
           'automatizada, sobre mis opciones de pr&#233;stamo hipotecario. El consentimiento no es una condici&#243;n de compra. '
           'Pueden aplicarse tarifas de mensajes y datos. La frecuencia de los mensajes var&#237;a. Responde STOP para cancelar '
           'o HELP para obtener ayuda. Consulta nuestra <a href="/politica-de-privacidad.html">Pol&#237;tica de Privacidad</a> '
           'y <a href="/terminos-de-servicio.html">T&#233;rminos de Servicio</a>.')

def options(items):
    return '\n'.join('                            <option>%s</option>' % o for o in items)

# Where in Arizona (Arizona focus for now; "Fuera de Arizona" flags out-of-state leads for later routing)
AREAS = ['Phoenix y alrededores (condado de Maricopa)', 'Tucson (condado de Pima)',
         'Pinal (Casa Grande, San Tan Valley, Maricopa)', 'Otra parte de Arizona', 'Fuera de Arizona']
AREA_SELECT = ('                        <label for="lf-area">¿En qué parte de Arizona quieres comprar?</label>\n'
               '                        <select id="lf-area" name="area" data-to-message="Zona">\n'
               '                            <option value="">Selecciona una opción</option>\n'
               + '\n'.join('                            <option>%s</option>' % a for a in AREAS) + '\n'
               '                        </select>')

def form_html(form_name):
    return '''                <div class="lead-card">
                    <form class="lead-form" data-form-name="%(name)s" novalidate>
                        <div class="lead-row">
                            <div><label for="lf-first">Nombre</label><input id="lf-first" type="text" name="first_name" autocomplete="given-name"></div>
                            <div><label for="lf-last">Apellido</label><input id="lf-last" type="text" name="last_name" autocomplete="family-name"></div>
                        </div>
                        <div class="lead-row">
                            <div><label for="lf-phone">Celular</label><input id="lf-phone" type="tel" name="phone" autocomplete="tel" inputmode="tel" required></div>
                            <div><label for="lf-email">Correo electrónico <span class="opt">(opcional)</span></label><input id="lf-email" type="email" name="email" autocomplete="email"></div>
                        </div>
                        <label for="lf-goal">¿Qué quieres hacer?</label>
                        <select id="lf-goal" name="goal" data-to-message="Busca">
                            <option value="">Selecciona una opción</option>
%(goals)s
                        </select>
%(area)s
                        <label for="lf-sit">Tu situación <span class="opt">(opcional)</span></label>
                        <select id="lf-sit" name="situation" data-to-message="Situación">
                            <option value="">Selecciona una opción</option>
%(sits)s
                        </select>
                        <label for="lf-when">¿Cuándo quieres comprar? <span class="opt">(opcional)</span></label>
                        <select id="lf-when" name="timeline">
                            <option value="">Selecciona una opción</option>
%(times)s
                        </select>
                        <label for="lf-msg">¿Algo que debamos saber? <span class="opt">(opcional)</span></label>
                        <textarea id="lf-msg" name="message" maxlength="1000"></textarea>
                        <div class="lead-hp" aria-hidden="true"><label for="lf-website">Website</label><input id="lf-website" type="text" name="website" tabindex="-1" autocomplete="off"></div>
                        <label class="lead-consent"><input type="checkbox" name="consent" value="yes"><span class="lead-consent-text">%(consent)s</span></label>
                        <button type="submit">Quiero que me contacten</button>
                        <div class="lead-error" role="alert" hidden></div>
                    </form>
                    <div class="lead-success" hidden><strong>¡Gracias! Recibimos tu información.</strong><p>Un asesor te va a escribir por mensaje de texto en unos minutos. Si es después de las 9 PM, te escribimos en la mañana.</p></div>
                    <p class="lead-note">No mandes documentos por aquí. Si los necesitamos, te enviamos un enlace seguro.</p>
                    <p class="lead-alt">¿Prefieres hablar? Llámanos al <a href="tel:+16026108305">(602) 610-8305</a></p>
                </div>''' % dict(
        name=form_name, consent=CONSENT, area=AREA_SELECT,
        goals=options(['Comprar mi primera casa', 'Comprar otra casa para vivir', 'Comprar para rentar o invertir',
                       'Comprar viviendo fuera de EE.UU.', 'Refinanciar mi casa']),
        sits=options(['Trabajo con W-2', 'Trabajo por mi cuenta o con 1099', 'Tengo ITIN', 'Tengo DACA o permiso de trabajo',
                      'Vivo fuera de EE.UU.']),
        times=options(['Lo antes posible', 'En los próximos 3 meses', 'De 3 a 6 meses', 'En 6 meses o más', 'Solo estoy investigando']))
