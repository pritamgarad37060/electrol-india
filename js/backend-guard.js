/* Fail closed if a backend attachment cannot load. The original HTML's demo
   handlers must never appear to authenticate or save private account data. */
(()=>{
 const message=()=>{const text='The account connection could not load. Refresh this page with the website server running.',host=document.querySelector('#auth-panel[open] .auth-general-error,#navigation-panel[open] .form-error');if(host){host.textContent=text;host.setAttribute('role','alert')}else if(typeof notify==='function')notify(text);};
 const block=e=>{e.preventDefault();e.stopImmediatePropagation();message();};
 window.addEventListener('submit',e=>{if(window.ElectrolBackend?.api)return;if(['auth-form','edit-profile-form','notification-form','follow-alerts-form','correction-form','interests-form','representative-alert-form'].includes(e.target.id))block(e);},true);
 window.addEventListener('click',e=>{if(window.ElectrolBackend?.api)return;const b=e.target.closest('[data-auth-provider],[data-auth-demo],[data-auth-signout],[data-toggle-follow],[data-rep-follow],[data-directory-follow],[data-institution-follow],[data-save-follow]');if(b)block(e);},true);
})();
