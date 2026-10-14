/*
 * Prestamigo WhatsApp buttons. Any <a data-wa> gets a wa.me link with a pre-filled message based on the page,
 * and each tap is recorded as a whatsapp_click event (GA4 + dataLayer + Clarity if installed).
 */
(function () {
  'use strict';
  var NUMBER = '16026108305';  // (602) 610-8305, Prestamigo
  // OFF while the number moves to Twilio's WhatsApp platform: buttons go to the contact form instead.
  var ENABLED = false;
  var TOPIC = {
    'comprar-casa-con-daca-arizona': 'Hola, vi la guía de DACA en Prestamigo y quiero información para comprar casa.',
    'prestamo-itin-arizona': 'Hola, vi la guía de préstamos ITIN en Prestamigo y quiero información para comprar casa.',
    'prestamo-fha-arizona-requisitos': 'Hola, vi la guía de FHA en Prestamigo y quiero saber si califico.',
    'prestamo-trabajadores-independientes-arizona': 'Hola, trabajo por mi cuenta y vi la guía en Prestamigo. Quiero saber si califico.',
    'prestamo-dscr-arizona': 'Hola, vi la guía de préstamos DSCR en Prestamigo y quiero información para invertir.',
    'como-calificar-prestamo-hipotecario-arizona': 'Hola, vi la guía en Prestamigo y quiero saber si califico para comprar casa.',
    'como-sacar-itin': 'Hola, vi la guía para sacar el ITIN en Prestamigo y tengo preguntas.',
    'como-abrir-llc-arizona': 'Hola, vi la guía de LLC en Prestamigo y quiero información para financiar una propiedad.',
    'como-sacar-ein': 'Hola, vi la guía del EIN en Prestamigo y quiero información para financiar una propiedad.'
  };
  var DEFAULT = 'Hola, vi su página de Prestamigo y quiero información para comprar casa.';

  var slug = window.location.pathname.replace(/^\/|\.html$|\/$/g, '');
  var text = TOPIC[slug] || DEFAULT;
  var href = 'https://wa.me/' + NUMBER + '?text=' + encodeURIComponent(text);

  function track(where) {
    var p = { page: slug || 'home', placement: where };
    try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: 'pm_whatsapp_click' }, p)); } catch (e) { /* ignore */ }
    try { if (typeof window.gtag === 'function') window.gtag('event', 'whatsapp_click', p); } catch (e) { /* ignore */ }
    try { if (typeof window.clarity === 'function') window.clarity('event', 'whatsapp_click'); } catch (e) { /* ignore */ }
  }

  function init() {
    if (!ENABLED) {
      var formHere = document.getElementById('contacto');
      Array.prototype.forEach.call(document.querySelectorAll('a[data-wa]'), function (a) {
        a.setAttribute('href', formHere ? '#contacto' : '/contacto.html');
        a.removeAttribute('target');
        a.innerHTML = /¿Tienes preguntas/.test(a.textContent) ? '¿Tienes preguntas? Escríbenos aquí' : 'Escríbenos aquí';
        a.addEventListener('click', function () { track('form_fallback_' + (a.getAttribute('data-wa') || 'link')); });
      });
      return;
    }
    Array.prototype.forEach.call(document.querySelectorAll('a[data-wa]'), function (a) {
      a.setAttribute('href', href);
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener');
      a.addEventListener('click', function () { track(a.getAttribute('data-wa') || 'link'); });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
