
window.addEventListener('click',event=>{
 const control=event.target.closest('[data-desktop-account]');if(!control||!matchMedia('(min-width:801px)').matches)return;
 event.preventDefault();event.stopImmediatePropagation();profileTab='activity';openNavigation('profile');
 if(control.dataset.desktopAccount==='settings')showProfilePage('account');
});
matchMedia('(min-width:801px)').addEventListener('change',()=>{if(document.getElementById('navigation-panel').open&&navKind==='profile'&&profilePage==='root')renderNavigation()});
