/**
 * Prestamigo Analytics & Tracking Integration
 * This file implements Google Analytics, Google Tag Manager, and Facebook Pixel
 */

(function() {
    // Configuration
    const GA_MEASUREMENT_ID = 'G-DCWV68YXJ9';
    const GTM_ID = 'GTM-NVH5B947';
    const FB_PIXEL_ID = '111216968559815';

    // Initialize Google Tag Manager
    function initGTM() {
        (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer',GTM_ID);
        
        // Add GTM noscript frame for non-JS environments
        const noscript = document.createElement('noscript');
        const iframe = document.createElement('iframe');
        iframe.src = `https://www.googletagmanager.com/ns.html?id=${GTM_ID}`;
        iframe.height = '0';
        iframe.width = '0';
        iframe.style.display = 'none';
        iframe.style.visibility = 'hidden';
        noscript.appendChild(iframe);
        document.body.insertBefore(noscript, document.body.firstChild);
    }

    // Initialize Google Analytics
    function initGA() {
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', GA_MEASUREMENT_ID);
        
        // Load GA script
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
        document.head.appendChild(script);
    }

    // Initialize Facebook Pixel
    function initFBPixel() {
        !function(f,b,e,v,n,t,s)
        {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};
        if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
        n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t,s)}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
        fbq('init', FB_PIXEL_ID);
        fbq('track', 'PageView');
        
        // Add FB Pixel noscript image for non-JS environments
        const noscript = document.createElement('noscript');
        const img = document.createElement('img');
        img.height = '1';
        img.width = '1';
        img.style.display = 'none';
        img.src = `https://www.facebook.com/tr?id=${FB_PIXEL_ID}&ev=PageView&noscript=1`;
        noscript.appendChild(img);
        document.body.appendChild(noscript);
    }

    // Track page view on load
    window.addEventListener('load', function() {
        // Initialize tracking services
        initGTM();
        initGA();
        initFBPixel();
    });

    // Public tracking functions
    window.prestamigoTrackEvent = function(eventName, eventParams) {
        // Track event in Google Analytics
        if (window.gtag) {
            window.gtag('event', eventName, eventParams);
        }
        
        // Track event in Facebook Pixel
        if (window.fbq) {
            window.fbq('track', eventName, eventParams);
        }
    };
    
    // Track form submissions
    document.addEventListener('DOMContentLoaded', function() {
        // Find all forms on the page
        const forms = document.querySelectorAll('form');
        
        forms.forEach(function(form) {
            form.addEventListener('submit', function(event) {
                // Determine the form type based on the form ID or action
                let formType = 'generic_form';
                let formData = {};
                
                if (form.id === 'contactForm' || form.action.includes('submit-form')) {
                    formType = 'contact_form';
                    
                    // Get name and email for better tracking
                    const nameField = form.querySelector('#name');
                    const emailField = form.querySelector('#email');
                    
                    if (nameField && emailField) {
                        formData = {
                            form_name: 'contact',
                            page_url: window.location.href,
                            page_path: window.location.pathname
                        };
                    }
                }
                
                // Track the form submission event
                window.prestamigoTrackEvent(formType + '_submission', formData);
                
                // Specifically track the lead event in Facebook Pixel
                if (window.fbq) {
                    window.fbq('track', 'Lead', {
                        content_name: formType,
                        content_category: 'form_submission'
                    });
                }
            });
        });
    });
})();