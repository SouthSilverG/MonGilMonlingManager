/* Separate GitHub Pages projects; loopback preview uses the two local servers. */
(function(){const local=['localhost','127.0.0.1'].includes(location.hostname);if(local)for(const a of document.querySelectorAll('[data-party-link]'))a.href='http://127.0.0.1:8765/';})();
