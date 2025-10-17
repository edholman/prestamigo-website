/**
 * Prestamigo Visitor Tracking Module
 * This module captures visitor information for ad retargeting purposes
 */

(function() {
    // Configuration
    const TRACKING_ENDPOINT = '/api/track-visitor';
    
    // Helper functions
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    function setCookie(name, value, days) {
        let expires = '';
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = `; expires=${date.toUTCString()}`;
        }
        document.cookie = `${name}=${value}${expires}; path=/`;
    }
    
    function getUrlParameters() {
        const params = {};
        const queryString = window.location.search.substring(1);
        const pairs = queryString.split('&');
        
        for (let i = 0; i < pairs.length; i++) {
            if (!pairs[i]) continue;
            
            const pair = pairs[i].split('=');
            params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
        }
        
        return params;
    }
    
    function getUtmParameters() {
        const utmParams = {};
        const allParams = getUrlParameters();
        
        const utmTags = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
        
        utmTags.forEach(tag => {
            if (allParams[tag]) {
                utmParams[tag] = allParams[tag];
            }
        });
        
        return utmParams;
    }
    
    function getReferrer() {
        return document.referrer || null;
    }
    
    function trackVisitor(additionalData = {}) {
        // Get UTM parameters
        const utmParams = getUtmParameters();
        
        // Get referrer
        const referrer = getReferrer();
        
        // Get client ID from Google Analytics if available
        let gaClientId = null;
        if (typeof ga !== 'undefined') {
            try {
                ga(function(tracker) {
                    gaClientId = tracker.get('clientId');
                });
            } catch (e) {
                console.log('Unable to get GA client ID');
            }
        }
        
        // Get Facebook FBID if available
        let fbid = null;
        if (typeof FB !== 'undefined' && FB.getAuthResponse) {
            try {
                const authResponse = FB.getAuthResponse();
                if (authResponse) {
                    fbid = authResponse.userID;
                }
            } catch (e) {
                console.log('Unable to get Facebook ID');
            }
        }
        
        // Basic visitor data
        const visitorData = {
            page_url: window.location.href,
            page_path: window.location.pathname,
            referrer: referrer,
            utm_tags: JSON.stringify(utmParams),
            ga_client_id: gaClientId,
            fbid: fbid,
            timestamp: new Date().toISOString(),
            ...additionalData
        };
        
        // Determine source
        if (utmParams.utm_source) {
            visitorData.source = utmParams.utm_source;
        } else if (referrer) {
            // Extract domain from referrer
            const referrerDomain = referrer.split('/')[2];
            if (referrerDomain) {
                if (referrerDomain.includes('google')) {
                    visitorData.source = 'Google';
                } else if (referrerDomain.includes('facebook')) {
                    visitorData.source = 'Facebook';
                } else if (referrerDomain.includes('instagram')) {
                    visitorData.source = 'Instagram';
                } else if (referrerDomain.includes('bing')) {
                    visitorData.source = 'Bing';
                } else {
                    visitorData.source = referrerDomain;
                }
            }
        }
        
        // Send data to server
        fetch(TRACKING_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(visitorData)
        })
        .then(response => response.json())
        .then(data => {
            // Store visitor ID in cookie for 30 days
            if (data.visitor_id) {
                setCookie('prestamigo_visitor_id', data.visitor_id, 30);
            }
        })
        .catch(error => {
            console.error('Error tracking visitor:', error);
        });
    }
    
    // Track pageview on load
    window.addEventListener('load', function() {
        // Check if visitor has been tracked before
        const visitorId = getCookie('prestamigo_visitor_id');
        
        // Track pageview
        trackVisitor({
            visitor_id: visitorId
        });
    });
    
    // Expose tracking function globally
    window.prestamigoTrackUser = function(userData) {
        trackVisitor(userData);
    };
})();