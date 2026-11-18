
/* Sandbox-safe history: preview frames (about:srcdoc) and some embeds throw SecurityError on replaceState/pushState. Deep links still work where allowed; elsewhere the call is ignored. */
(function(){try{var H=window.History&&History.prototype;if(!H)return;['replaceState','pushState'].forEach(function(k){var o=H[k];if(typeof o!=='function')return;H[k]=function(){try{return o.apply(this,arguments)}catch(e){if(e&&(e.name==='SecurityError'||e.code===18))return;throw e}}})}catch(e){}})();
