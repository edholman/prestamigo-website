/*
 * Prestamigo lead forms -> agent/CRM (https://sms.whyrebate.com/leads/prestamigo)
 *
 * Any <form class="lead-form"> on the page is handled here (data-form-name is sent as form_name).
 * On success the form is replaced by its .lead-success block and a Meta Pixel "Lead" event plus a
 * dataLayer "prestamigo_lead" event fire, only after the server confirms the lead.
 *
 * On every page this script also remembers first-touch attribution (UTM tags, gclid, fbclid, landing page)
 * for 30 days, so a lead who lands from an ad and fills out a form on another page is still credited.
 */
(function () {
  'use strict';

  var ENDPOINT = 'https://sms.whyrebate.com/leads/prestamigo';
  var STORE_KEY = 'prestamigo_attribution';
  var ATTR_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid'];
  var MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;

  var MSG = {
    sending: 'Enviando...',
    network: 'Hubo un problema al enviar tu información. Intenta de nuevo en un momento.',
    phone: 'Escribe un número de celular válido de Estados Unidos.',
    consent: 'Marca la casilla de consentimiento para que podamos enviarte mensajes.'
  };

  function safeStorage() {
    try { var s = window.localStorage; s.setItem('__t', '1'); s.removeItem('__t'); return s; } catch (e) { return null; }
  }

  function readAttribution() {
    var store = safeStorage(), saved = null;
    if (store) {
      try { saved = JSON.parse(store.getItem(STORE_KEY) || 'null'); } catch (e) { saved = null; }
      if (saved && (Date.now() - (saved.ts || 0)) > MAX_AGE_MS) saved = null;
    }
    var params = new URLSearchParams(window.location.search), fresh = {}, hasFresh = false;
    ATTR_KEYS.forEach(function (k) { var v = params.get(k); if (v) { fresh[k] = v.slice(0, 200); hasFresh = true; } });
    // A new ad click or tagged link replaces older attribution; otherwise keep the first touch.
    if (hasFresh || !saved) {
      saved = { ts: Date.now(), landing_page: window.location.href.slice(0, 500), data: fresh };
      if (store) { try { store.setItem(STORE_KEY, JSON.stringify(saved)); } catch (e) { /* ignore */ } }
    }
    var out = {};
    ATTR_KEYS.forEach(function (k) { if (saved.data && saved.data[k]) out[k] = saved.data[k]; });
    // Fall back to the Google Ads click ID stored by gtag (_gcl_aw = GCL.<time>.<gclid>).
    if (!out.gclid) {
      var m = document.cookie.match(/(?:^|;\s*)_gcl_aw=([^;]+)/);
      if (m) { var parts = decodeURIComponent(m[1]).split('.'); if (parts.length >= 3) out.gclid = parts.slice(2).join('.'); }
    }
    out.landing_page = saved.landing_page;
    return out;
  }

  var attribution = readAttribution();

  // Funnel step -> Google Analytics 4 event (+ dataLayer for GTM, + Clarity if installed).
  // GA4 is initialized by js/tracking.js on window load, so events wait until after that.
  function funnel(name, params) {
    params = params || {};
    try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: 'pm_' + name }, params)); } catch (e) { /* ignore */ }
    try { if (typeof window.clarity === 'function') window.clarity('event', name); } catch (e) { /* ignore */ }
    var send = function () { try { if (typeof window.gtag === 'function') window.gtag('event', name, params); } catch (e) { /* ignore */ } };
    if (document.readyState === 'complete') setTimeout(send, 400); else window.addEventListener('load', function () { setTimeout(send, 600); });
  }

  function trackLead(formName) {
    try { if (typeof window.fbq === 'function') window.fbq('track', 'Lead', { content_name: formName }); } catch (e) { /* ignore */ }
    try { (window.dataLayer = window.dataLayer || []).push({ event: 'prestamigo_lead', form_name: formName }); } catch (e) { /* ignore */ }
    funnel('generate_lead', { form_name: formName });
  }

  function showError(form, text) {
    var box = form.querySelector('.lead-error');
    if (!box) return;
    box.textContent = text;
    box.hidden = false;
  }

  function setup(form) {
    var button = form.querySelector('button[type="submit"]');
    var buttonText = button ? button.textContent : '';
    var sending = false;
    var formName = form.getAttribute('data-form-name') || 'website';
    var seen = {};
    function once(name, params) { if (!seen[name]) { seen[name] = true; funnel(name, Object.assign({ form_name: formName }, params || {})); } }

    // Funnel: form seen -> started typing -> clicked submit -> (error) -> generate_lead
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { once('form_view'); io.disconnect(); } });
      }, { threshold: 0.4 });
      io.observe(form);
    }
    form.addEventListener('focusin', function () { once('form_start'); });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (sending) return;
      funnel('form_submit_click', { form_name: formName });
      var errBox = form.querySelector('.lead-error');
      if (errBox) errBox.hidden = true;

      var phone = form.querySelector('[name="phone"]');
      var consent = form.querySelector('[name="consent"]');
      var digits = phone ? phone.value.replace(/\D/g, '') : '';
      if (digits.length === 11 && digits.charAt(0) === '1') digits = digits.slice(1);
      if (digits.length !== 10) { funnel('form_error', { form_name: formName, reason: 'phone' }); showError(form, MSG.phone); if (phone) phone.focus(); return; }
      if (!consent || !consent.checked) { funnel('form_error', { form_name: formName, reason: 'consent' }); showError(form, MSG.consent); if (consent) consent.focus(); return; }

      var payload = {}, notes = [];
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.disabled || el.type === 'submit') return;
        // Extra answers (goal, situation) travel inside "message" as "Label: value" lines.
        if (el.hasAttribute('data-to-message')) { if (el.value) notes.push(el.getAttribute('data-to-message') + ': ' + el.value); return; }
        if (el.type === 'checkbox') { if (el.name === 'consent') payload.consent = el.checked; else if (el.checked) payload[el.name] = el.value || 'yes'; return; }
        var v = (el.value || '').trim();
        if (v !== '' || el.name === 'website') payload[el.name] = v;
      });
      if (notes.length) payload.message = notes.join('\n') + (payload.message ? '\n' + payload.message : '');
      var consentTextEl = form.querySelector('.lead-consent-text');
      payload.consent_text = consentTextEl ? consentTextEl.textContent.replace(/\s+/g, ' ').trim() : '';
      payload.page_url = window.location.href;
      payload.form_name = form.getAttribute('data-form-name') || 'website';
      payload.language = 'es';
      Object.keys(attribution).forEach(function (k) { if (attribution[k] && !payload[k]) payload[k] = attribution[k]; });

      sending = true;
      if (button) { button.disabled = true; button.textContent = MSG.sending; }

      fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(function (res) {
          return res.json().catch(function () { return {}; }).then(function (body) { return { status: res.status, body: body }; });
        })
        .then(function (r) {
          if (r.status === 200 && r.body && r.body.ok) {
            trackLead(payload.form_name);
            var ok = form.parentNode.querySelector('.lead-success');
            form.hidden = true;
            if (ok) { ok.hidden = false; ok.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
            return;
          }
          funnel('form_error', { form_name: formName, reason: 'server_' + r.status });
          showError(form, (r.body && r.body.error) ? r.body.error : MSG.network);
        })
        .catch(function () { funnel('form_error', { form_name: formName, reason: 'network' }); showError(form, MSG.network); })
        .then(function () { sending = false; if (button) { button.disabled = false; button.textContent = buttonText; } });
    });
  }

  function init() { Array.prototype.forEach.call(document.querySelectorAll('form.lead-form'), setup); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
