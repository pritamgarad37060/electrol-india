/* Connect the supplied HTML's controls. Its DOM, styles and view renderers own
   presentation and navigation. No legacy frontend or CSS is loaded here. */
(()=>{
 'use strict';
 let session=null,csrf='',refreshing,revision=0,pageRevision=0,savedComparisons=[],sessionKnown=false;
 const savedProfiles=new Set();
 const pending=new Set(),resolved=new Map(),serverFollows=new Map(),pageData=new Map();
 const original={renderAuth,profilePageHTML,renderNavigation,showProfilePage,followCatalog,renderRepresentative,renderMunicipalContent};
 const authMotionQuery=matchMedia('(prefers-reduced-motion: reduce)');
 authMotionQuery.addEventListener('change',event=>{if(event.matches)for(const id of ['auth-panel-body','navigation-body'])document.getElementById(id)?.getAnimations().forEach(a=>a.cancel())});
 const errors={authentication_failed:'Check your email and password, or use password recovery.',accounts_not_configured:'The account backend is not configured.',email_delivery_unavailable:'Email delivery is unavailable. Please try again later.',google_not_configured:'Google sign-in is not configured.',reauthentication_required:'Confirm your password before continuing.',mfa_required:'Enter your authenticator code to continue.',invalid_otp:'This code is incorrect or has expired.',invalid_input:'Check the entered values.',push_unavailable:'Browser notifications are not configured.'};
 const localAccountHost=['localhost','127.0.0.1','[::1]'].includes(location.hostname);
 const updateAccountMessage=()=>localAccountHost?'The running server needs the latest account update. Close the old website server, reopen Start-Website.cmd, and use the address it prints.':'The live account service needs the latest update. Deploy the frontend and account function together.';
 async function api(action,body){
  const timeout=action==='auth-bootstrap'?3000:20000;
  let r;try{r=await fetch('/api/account/'+action,{method:body===undefined?'GET':'POST',credentials:'same-origin',cache:'no-store',headers:body===undefined?{}:{'Content-Type':'application/json','X-Account-CSRF':csrf},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(timeout)});}catch(error){
   if(navigator.onLine===false)throw Error('You are offline. Reconnect to the internet and retry.');
   if(error.name==='TimeoutError'||error.name==='AbortError')throw Error(action==='auth-bootstrap'?(localAccountHost?'Account startup timed out. Close the old website server, reopen Start-Website.cmd, and use its printed address.':'Account startup timed out. The live account service is not responding. Please retry.'): 'The account request timed out. Please retry.');
   throw Error(localAccountHost?'Cannot connect to the local account server. Open Start-Website.cmd and use the address it prints.':'Cannot connect to the account service. Check your connection and retry.');
  }
  if(action==='auth-bootstrap'&&[404,405].includes(r.status))throw Error(updateAccountMessage());
  let data;try{data=await r.json()}catch{throw Error(action==='auth-bootstrap'?updateAccountMessage():'The account service returned an invalid response. Please retry.');}
  if(data.csrf)csrf=data.csrf;if(!r.ok)throw Object.assign(Error(errors[data.error]||(data.error==='service_unavailable'?'The authentication provider is temporarily unavailable. Please retry.':'This action could not be completed. Please retry.')),{code:data.error,status:r.status});if(body!==undefined&&(data.saved||data.signed_out||data.authenticated))channel?.postMessage('changed');return data;
 }
 // Share a lightweight CSRF bootstrap; OAuth must not wait for profile,
 // follow-list or provider requests in the initial session refresh.
 let bootstrapPromise;
 function authBootstrap(){
  if(csrf)return Promise.resolve();
  if(!bootstrapPromise)bootstrapPromise=api('auth-bootstrap').then(data=>{
   for(const origin of [data.authOrigin,'https://accounts.google.com']){
    if(!origin||document.querySelector('link[data-auth-origin="'+origin+'"]'))continue;
    const u=new URL(origin);if(u.protocol!=='https:')continue;
    const link=document.createElement('link');link.rel='preconnect';link.href=u.origin;link.dataset.authOrigin=origin;document.head.append(link);
   }
  }).finally(()=>{bootstrapPromise=null});
  return bootstrapPromise;
 }
 let googleWarmUntil=0;
 function warmGoogle(){
  if(Date.now()<googleWarmUntil)return;
  googleWarmUntil=Date.now()+45000;
  // Read-only warmup: never create an OAuth flow or change its verifier here.
  void authBootstrap().then(()=>api('google-config')).catch(()=>{googleWarmUntil=0});
 }
 function status(message,error=false){const host=document.querySelector('#auth-panel[open] .auth-general-error,#navigation-panel[open] .form-error');if(host){host.textContent=message;host.setAttribute('role',error?'alert':'status')}else notify(message);}
 function signedIn(){if(session?.mfaRequired){openAuth('login');codeScreen('mfa');return false;}if(session?.user)return true;openAuth('login');return false;}
 const norm=s=>String(s||'').normalize('NFKC').toLocaleLowerCase().replace(/^(shri|smt|dr\.?|adv\.?)\s+/i,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim();
 const userItem=e=>({id:'account:'+e.id,name:e.name,short:e.name,type:({person:'leaders',body:'cities',constituency:'constituencies',election:'elections',party:'parties'})[e.kind]||'topics',location:e.subtitle||e.metadata?.state_name||'',region:e.metadata?.state_name||'',url:e.url,provenance:'sourced'});
 function entityMatches(item,e){if(!item||!e)return false;if(item.id==='account:'+e.id)return true;const target=window.ElectrolHTMLData?.identity(item.id)||{},url=target.url||item.url;const path=u=>{try{const v=new URL(u,location.origin);v.searchParams.sort();return v.pathname+v.search;}catch{return null;}};if(url&&e.url&&path(url)===path(e.url))return true;if(norm(item.name)!==norm(e.name))return false;const person=item.type==='leaders'||e.kind==='person';if(!person)return true;const m=e.metadata||{},state=m.state_name||m.state,seat=m.constituency||m.seat_name||m.body_name;return !!state&&!!seat&&norm(state)===norm(item.region)&&norm(seat)===norm(item.location)&&(!m.level||m.level===(item.level||item.d?.level));}
 function applyProfile(){
  const p=session?.profile;
  if(!session?.user){
   demoSession=null;
   try{
    const stored=JSON.parse(localStorage.getItem(NAV_PREF_KEY)||'{}');
    if(Array.isArray(stored.follows)&&stored.follows.length){
     navPrefs.follows=[...new Set([...navPrefs.follows,...stored.follows])];
    }
   }catch{}
   return;
  }
  demoSession={name:p?.display_name||session.user.email,email:session.user.email,demo:false};
  if(p){navPrefs.name=p.display_name||'';appDetails={...appDetails,username:p.username||'',bio:p.bio||'',location:p.location||'',website:p.website||'',social:{x:'',instagram:'',youtube:'',...p.social_links},photo:p.avatar_url||'',cover:p.cover_url||'',joinedAt:p.created_at||appDetails.joinedAt};}
  const prefs=session.preferences||{};appDetails.quiet={enabled:!!prefs.quiet_enabled,start:prefs.quiet_start||'22:00',end:prefs.quiet_end||'07:00'};appDetails.frequency=prefs.frequency==='instant'?'all':prefs.frequency||'important';navPrefs.notifications={...navPrefs.notifications,inapp:prefs.in_app!==false,elections:prefs.categories?.includes('elections')??true,leaders:prefs.categories?.includes('representatives')??true,news:prefs.categories?.includes('news')??true,policy:prefs.categories?.includes('government')??true};
 }
 function syncFollows(){
  if(!session?.user)return;
  navPrefs.follows=[];const catalog=original.followCatalog();
  for(const [entityId,row]of serverFollows){const e=row.entity;if(!e)continue;const matches=catalog.filter(item=>entityMatches(item,e));const item=matches.length===1?matches[0]:userItem(e);resolved.set(item.id,e);navPrefs.follows.push(item.id);followDetails[item.id]={saved:false,followedAt:row.followed_at,alerts:{enabled:!row.muted,news:row.alert_types?.includes('news'),elections:row.alert_types?.includes('elections'),events:false,policy:row.alert_types?.includes('government')},activity:[]};}
 }
 async function refresh(){
  if(refreshing)return refreshing;
  refreshing=(async()=>{await authBootstrap();const owner=session?.user?.id;session=await api('session');if(owner!==session.user?.id){resolved.clear();serverFollows.clear();pageData.clear();savedComparisons=[];savedProfiles.clear();navPrefs.name='';navPrefs.elections=[];appDetails={...defaultDetails(),contentLanguage:appDetails.contentLanguage,dateFormat:appDetails.dateFormat,hour12:appDetails.hour12,timeZone:appDetails.timeZone};for(const id of Object.keys(followDetails))delete followDetails[id];profileEditDraft=null;}
   if(session.user&&!session.mfaRequired){
    const [follows,saved,profiles]=await Promise.all([
     (async()=>{const rows=[];for(let page=0;page<500;page++){const data=await api('follows?page='+page);rows.push(...data.rows||[]);if(!data.has_more)break;}return rows;})(),
     api('saved-searches'),api('saved-content?type=profiles')
    ]);
    serverFollows.clear();for(const row of follows)serverFollows.set(row.entity_id,row);
    savedComparisons=(saved.rows||[]).filter(r=>r.filters?.htmlComparison).map(r=>({title:r.name,config:r.filters.htmlComparison,_backendId:r.id}));
    savedProfiles.clear();const catalog=original.followCatalog();for(const row of profiles.rows||[]){const e=row.item;if(!e?.id)continue;savedProfiles.add(e.id);const matches=catalog.filter(i=>entityMatches(i,e));resolved.set(matches.length===1?matches[0].id:'account:'+e.id,e);}
   }
   applyProfile();syncFollows();for(const [id,e]of resolved)if(savedProfiles.has(e.id))followDetails[id]={...followMeta(id),saved:true};sessionKnown=true;updateProfileBadges();enhanceFollowControls();return session;
  })().finally(()=>refreshing=null);return refreshing;
 }
 let followRenderSnapshot=null,followRenderIndex=null;
 const buildFollowCatalog=()=>{const rows=original.followCatalog().filter(r=>!r.legacy||!resolved.has(r.legacy)),ids=new Set(rows.map(r=>r.id));for(const [id,e]of resolved)if(!ids.has(id)){rows.push({...userItem(e),id});ids.add(id)}return rows;};
 followCatalog=()=>followRenderSnapshot||buildFollowCatalog();
 findFollow=function(id=activeFollowId){return followRenderIndex?followRenderIndex.get(id):followCatalog().find(x=>x.id===id)};
 function followRender(work){if(followRenderSnapshot)return work();followRenderSnapshot=buildFollowCatalog();followRenderIndex=new Map(followRenderSnapshot.map(x=>[x.id,x]));try{return work()}finally{followRenderSnapshot=null;followRenderIndex=null}}
 const nativeFollowResults=renderFollowResults;
 renderFollowResults=function(...args){return followRender(()=>nativeFollowResults(...args))};
 persistNavPrefs=function(){try{if(session?.user){const {follows,elections,...preferences}=navPrefs;localStorage.setItem(NAV_PREF_KEY,JSON.stringify(preferences));}else{localStorage.setItem(NAV_PREF_KEY,JSON.stringify(navPrefs));}return true;}catch{return false;}};
 persistDetails=function(){try{const prefs={};for(const key of ['contentLanguage','region','city','dateFormat','hour12','timeZone'])prefs[key]=appDetails[key];localStorage.setItem(DETAILS_KEY,JSON.stringify(prefs));return true}catch{return false}};
 persistFollowDetails=function(){try{if(!session?.user){localStorage.setItem(FOLLOW_KEY,JSON.stringify(followDetails));}return true;}catch{return false;}};
 async function entity(id){
  if(resolved.has(id))return resolved.get(id);
  if(id.startsWith('account:')){const row=serverFollows.get(id.slice(8));if(row?.entity){resolved.set(id,row.entity);return row.entity;}}
  let item=findFollow(id);if(!item)try{item=publicPerson(id)}catch{}
  if(!item?.name)throw Error('This item has not yet been matched to the account catalog.');
  if(item.type==='leaders')await window.ElectrolDirectories?.loadPeople();const target=window.ElectrolHTMLData?.identity(id)||{};
  if(target.url||item.url){const byURL=await api('entities?url='+encodeURIComponent(target.url||item.url));if(byURL.rows?.length===1){resolved.set(id,byURL.rows[0]);return byURL.rows[0];}}
  const name=item.type==='constituencies'?item.name.split(' · ')[0]:item.name,kind=({leaders:'person',parties:'party',constituencies:'constituency'})[item.type];
  const cleanQ=name.replace(/[\(\),\*]/g,' ').replace(/^(shri|smt|dr\.?|adv\.?)\s+/i,'').trim();
  const data=await api('entities?q='+encodeURIComponent(cleanQ)+(kind?'&kind='+kind:''));const matches=(data.rows||[]).filter(e=>entityMatches({...item,name},e));
  if(matches.length!==1)throw Error('This identity cannot yet be uniquely matched to the account catalog.');resolved.set(id,matches[0]);return matches[0];
 }
 isFollowing=function(id,item){
  if(!session?.user){return navPrefs.follows.includes(id);}
  if(!serverFollows.size)return navPrefs.follows.includes(id);
  let e=resolved.get(id);
  if(!e){try{item||=findFollow(id)||publicPerson(id)}catch{}if(item){const name=item.type==='constituencies'?item.name.split(' · ')[0]:item.name,matches=[...serverFollows.values()].filter(row=>row.entity&&entityMatches({...item,name},row.entity));if(matches.length===1){e=matches[0].entity;resolved.set(id,e);}}}
  return (!!e&&serverFollows.has(e.id))||navPrefs.follows.includes(id);
 };
 async function toggle(id){
  if(pending.has(id))return;
  if(!session?.user){
   let item=findFollow(id);if(!item)try{item=publicPerson(id)}catch{}
   let active=navPrefs.follows.includes(id);
   if(active){
    navPrefs.follows=navPrefs.follows.filter(x=>x!==id);
    if(followDetails[id])followDetails[id].alerts={enabled:false};
   }else{
    if(!navPrefs.follows.includes(id))navPrefs.follows.push(id);
    followDetails[id]={saved:false,followedAt:new Date().toISOString(),alerts:{enabled:true,news:true,elections:true,events:false,policy:true},activity:[]};
   }
   persistNavPrefs();
   persistFollowDetails();
   refreshFollowUI();
   enhanceFollowControls();
   notify(active?'Unfollowed.':'Added to My Follows on this device.');
   return;
  }
  pending.add(id);enhanceFollowControls();
  try{
   const e=await entity(id),was=serverFollows.has(e.id);
   await api(was?'unfollow':'follow',{entity_id:e.id});
   if(was){serverFollows.delete(e.id);navPrefs.follows=navPrefs.follows.filter(x=>x!==id);}
   else{serverFollows.set(e.id,{entity_id:e.id,entity:e,muted:false,alert_types:['elections','news'],followed_at:new Date().toISOString()});if(!navPrefs.follows.includes(id))navPrefs.follows.push(id);}
   syncFollows();refreshFollowUI();notify(was?'Unfollowed.':'Added to My Follows.');
  }
  catch(error){status(error.message,true)}finally{pending.delete(id);enhanceFollowControls();}
 }
 toggleFollowing=id=>{void toggle(id)};
 readSaved=function(){return savedComparisons.slice()};
 save=async function(){if(!signedIn())return;try{const config={...current},title=document.getElementById('comparison-title').textContent;if(savedComparisons.some(r=>JSON.stringify(r.config)===JSON.stringify(config))){notify('This comparison is already saved.');return;}await api('save-search',{name:title.slice(0,100),url:'/analysis/?htmlComparison='+encodeURIComponent(JSON.stringify(config)),filters:{htmlComparison:config}});await refresh();updateCounts();notify('Comparison saved to your account.');}catch(error){status(error.message,true)}};
 const followSelector='[data-toggle-follow],[data-rep-follow],[data-directory-follow],[data-institution-follow]';
 const followId=b=>b.dataset.toggleFollow||(b.hasAttribute('data-rep-follow')?representativeId:null)||b.dataset.directoryFollow||b.dataset.institutionFollow;
 function enhanceFollowControls(){followRender(()=>document.querySelectorAll(followSelector).forEach(b=>{
  const id=followId(b);if(!id)return;const saving=pending.has(id),busy=saving||!sessionKnown,following=sessionKnown?isFollowing(id,findFollow(id)):false;
  b.disabled=busy;b.setAttribute('aria-busy',String(busy));if(sessionKnown)b.setAttribute('aria-pressed',String(following));else b.removeAttribute('aria-pressed');
  if(busy){const mode=saving?'saving':'checking';if(b.dataset.followBusy!==mode){b.dataset.followBusy=mode;b.innerHTML='<span class="follow-progress" aria-hidden="true"></span><span>'+(saving?'Saving…':'Checking…')+'</span>';}return;}
  delete b.dataset.followBusy;const text=following?'Following':'Follow';if(b.textContent.trim()!==text)b.innerHTML=icons('follow')+' '+text;
 }))}
 const messages=new Map([
  ['Use at least 8 characters in this preview.','Use at least 12 characters.'],['Use demo code 123456.','Enter the code sent to your email.'],['No email has been sent.','Enter the verification code from your email.'],['Sign-in preview complete.','You’re signed in.'],['Your account preview is ready.','Your account is verified.'],['Password reset preview complete.','Your password has been reset.'],['Finish the password reset preview.','Choose a new password for your account.'],['Enter your email to preview the recovery flow.','Enter your account email to receive a recovery link.'],['This is a local profile. There is no signed-in account or online profile sync in this file.','Sign in to save your profile to your account.'],['End this demo session; keep local preferences','Sign out of this browser session'],['Your profile and preferences stay on this device. Account sync and live notifications need a connected service.','Sign in to synchronize your profile and follows.'],['Your space · On this device','Your space'],['Local profile since ','Account created '],['Comparisons saved in this browser.','Comparisons saved to your account.'],['Demo session','Signed-in account'],['Demo account','Signed-in account']
 ]);
 function wording(root){if(!root)return;const walk=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while(n=walk.nextNode()){if(n.parentElement.closest('script,style'))continue;let text=n.textContent;for(const [from,to]of messages)text=text.replaceAll(from,to);text=text.replace('Verification preview for','Verification for');if(text!==n.textContent)n.textContent=text;}}
 authDemoControls=()=>'';
 renderAuth=function(...args){const hostBefore=document.getElementById('auth-panel-body'),previousView=hostBefore?.dataset.authView;original.renderAuth(...args);
  const view=authState.step+':'+authState.method+':'+authState.flow,body=document.getElementById('auth-panel-body');body.dataset.authView=view;body.getAnimations().forEach(a=>a.cancel());
  if(previousView&&previousView!==view&&!authMotionQuery.matches){body.animate([{opacity:.4,transform:'translateY(5px)'},{opacity:1,transform:'translateY(0)'}],{duration:160,easing:'cubic-bezier(.2,.8,.2,1)'});}
  if(authState.busy){const submit=body.querySelector('.auth-submit:disabled');if(submit&&!submit.querySelector('.auth-spinner'))submit.insertAdjacentHTML('afterbegin','<span class="auth-spinner" aria-hidden="true"></span> ');}
 if(['login','signup','providers'].includes(authState.step))warmGoogle();const host=document.getElementById('auth-panel-body');wording(host);host?.querySelectorAll('.auth-demo-controls').forEach(e=>e.remove());host?.querySelectorAll('.badge').forEach(e=>{if(e.textContent.trim()==='Demo')e.textContent='Connected'});if(authState.step==='otp'){if(authState.flow==='mfa'){document.getElementById('auth-panel-title').textContent='Verify authenticator';const title=host.querySelector('h1');if(title)title.textContent='Enter your authenticator code.';const hint=host.querySelector('.auth-heading p');if(hint)hint.textContent='Use the current code from your authenticator app.';host.querySelector('[data-auth-resend]')?.classList.add('hidden');host.querySelector('[data-auth-change-email]')?.classList.add('hidden');}updateAuthClock();}};
 validateAuth=function(flow){const a=authState,error={};if(['signup','password-login','code-login','forgot'].includes(flow)&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(a.email.trim()))error.email='Enter a valid email address.';if(flow==='signup'&&a.name.trim().length<2)error.name='Enter your name.';if(['signup','reset'].includes(flow)){if(a.password.length<12)error.password='Use at least 12 characters.';if(a.password!==a.confirm)error.confirm='Passwords do not match.';}if(flow==='password-login'&&!a.password)error.password='Enter your password.';if(flow==='otp'&&!/^\d{6}$/.test(a.code))error.code='Enter the six-digit email code.';return error;};
 updateAuthClock=function(){const wait=Math.max(0,Math.ceil((authState.resendAt-Date.now())/1000)),clock=document.getElementById('auth-code-clock'),resend=document.getElementById('auth-resend');if(clock)clock.textContent=authState.flow==='mfa'?'Use the current code in your authenticator app.':'Use the latest verification code from your email.';if(resend){resend.disabled=wait>0||authState.busy;resend.textContent=wait?'Resend in '+wait+'s':'Resend code';}};
 function codeScreen(flow){authState.flow=flow;authState.step='otp';authState.password='';authState.confirm='';authState.code='';authState.busy=false;authState.error={};authState.expiresAt=Number.MAX_SAFE_INTEGER;authState.resendAt=Date.now()+30000;authState.lockedUntil=0;renderAuth();}
 async function authComplete(kind){await refresh();if(session?.mfaRequired){codeScreen('mfa');return;}authState.password='';authState.confirm='';authState.code='';authState.step='success';authState.success=kind;authState.error={};authState.busy=false;renderAuth();const p=document.querySelector('#auth-panel-body .auth-heading p');if(p)p.textContent=kind==='reset'?'You can now sign in with your new password.':'Your account is connected. Continue to Electrol India.';}
 submitAuth=async function(flow){
  if(authState.busy)return;authState.error=validateAuth(flow);if(Object.keys(authState.error).length){renderAuth(true);return;}const token=++revision;authState.busy=true;renderAuth();
  try{await authBootstrap();const a=authState;
   if(flow==='password-login'){await api('login',{email:a.email.trim(),password:a.password,next:'/'});await authComplete('login');}
   else if(flow==='signup'){await api('signup',{display_name:a.name.trim(),email:a.email.trim(),password:a.password});codeScreen('signup');}
   else if(flow==='code-login'){await api('send-otp',{email:a.email.trim(),mode:'login'});codeScreen('login');}
   else if(flow==='forgot'){await api('forgot-password',{email:a.email.trim()});a.busy=false;a.error={general:'Check your email for a password-reset link.'};renderAuth();document.querySelector('.auth-general-error')?.setAttribute('role','status');}
   else if(flow==='otp'){if(a.flow==='mfa'){const factor=session?.factors?.[0];if(!factor)throw Error('No verified authenticator is available.');const challenge=await api('mfa-challenge',{factor_id:factor.id});await api('mfa-verify',{factor_id:factor.id,challenge_id:challenge.id,code:a.code});}else await api('verify-otp',{email:a.email.trim(),code:a.code,next:'/'});await authComplete(a.flow==='signup'?'signup':'login');}
   else if(flow==='reset'){await api('password',{password:a.password});await authComplete('reset');}
  }catch(error){if(token!==revision)return;authState.busy=false;authState.error={general:error.message};renderAuth(true);}finally{if(token===revision)authState.busy=false;}
 };
 startProvider=async function(provider){if(provider!=='Google'){authState.provider=provider;authState.step='provider-error';authState.busy=false;renderAuth();const h=document.querySelector('#auth-panel-body .auth-heading p');if(h)h.textContent='This sign-in provider is not configured. Use email or an enabled provider.';return;}if(authState.busy)return;authState.busy=true;authState.error={};const buttons=[...document.querySelectorAll('[data-auth-provider]')];for(const button of buttons){button.disabled=true;button.setAttribute('aria-busy','true');if(button.dataset.authProvider===provider){const label=button.querySelector('.auth-provider-label');if(label)label.textContent='Opening Google…';button.querySelector(':scope > .icon')?.remove();button.insertAdjacentHTML('beforeend','<span class="auth-spinner" aria-hidden="true"></span>');}}performance.mark('electrol-google-click');try{await authBootstrap();sessionStorage.setItem('electrol-auth-return',JSON.stringify({path:location.pathname+location.search+location.hash,destination:siteDestination,person:siteDestination==='representative-profile'?representativeId:null,edition:electionEdition?.id,scope:fullScope,tab:electionDashboardTab,municipal:mcCurrent}));const r=await api('google',{next:'/'});performance.mark('electrol-google-redirect-ready');performance.measure('electrol-google-start','electrol-google-click','electrol-google-redirect-ready');location.assign(r.url);}catch(error){authState.busy=false;authState.error={general:error.message};renderAuth(true)}};
 async function resendCode(){if(authState.busy||Date.now()<authState.resendAt)return;try{authState.busy=true;renderAuth();await api('send-otp',{email:authState.email.trim(),mode:authState.flow==='signup'?'signup':'login',...(authState.flow==='signup'?{display_name:authState.name.trim(),accepted_privacy:true}:{})});codeScreen(authState.flow);}catch(error){authState.busy=false;authState.error={general:error.message};renderAuth(true)}}
 const loading=()=>panelEmpty('person','Loading your account','Please wait…');
 function rowsHTML(rows,render){return `<div class="settings-card">${rows.map(render).join('')}</div>`;}
 function securityForm(kind){return `<form id="connected-security-form" class="profile-form" data-kind="${esc(kind)}"><section class="settings-card"><h3>${kind==='password'?'Change password':kind==='delete'?'Delete account':'Two-factor authentication'}</h3><label class="setting-label" for="connected-current-password">Confirm current password</label><input id="connected-current-password" class="setting-input" type="password" autocomplete="current-password" required>${kind==='password'?'<label class="setting-label" for="connected-new-password">New password</label><input id="connected-new-password" class="setting-input" type="password" minlength="12" autocomplete="new-password" required>':''}${kind==='delete'?'<label class="setting-label">Type DELETE MY ACCOUNT<input id="connected-delete-confirm" class="setting-input" required></label>':''}<div id="connected-mfa"></div><p class="form-error" role="status"></p></section><div class="sticky-save"><button type="submit" class="primary">${kind==='password'?'Update password':kind==='delete'?'Delete account':'Set up authenticator'}</button></div></form>`;}
 let securityKind='password';
 profilePageHTML=function(){
  if(['sessions','login-activity','connections','notifications','correction-drafts'].includes(profilePage)){
   const data=pageData.get(profilePage);if(!data)return loading();if(data.error)return panelEmpty('info','Unable to load',esc(data.error),'<button class="secondary" data-backend-retry>Retry</button>');
   if(profilePage==='sessions')return rowsHTML(data.rows||[],r=>`<div class="provider-row"><span class="row-content"><strong>${esc(r.device_name||r.user_agent||'Browser session')}</strong><small>${r.current?'Current session · ':''}${esc(r.last_seen_at||'')}</small></span><button class="secondary" data-backend-revoke="${esc(r.id)}">Sign out</button></div>`);
   if(profilePage==='login-activity')return rowsHTML(data.rows||[],r=>`<div class="detail-row"><span>${esc(r.event_type)}</span><small>${esc(r.created_at)} · ${r.success?'Successful':'Failed'}</small></div>`);
   if(profilePage==='connections')return rowsHTML(data.identities||[],r=>`<div class="provider-row"><span class="row-content"><strong>${esc(r.provider)}</strong><small>${esc(r.email||'Connected')}</small></span></div>`)+(data.google?'<button class="secondary blue" data-backend-google-link>Connect Google</button>':'');
   if(profilePage==='notifications')return data.rows?.length?rowsHTML(data.rows,r=>`<div class="saved-row"><a class="open-save" href="${esc(r.url&&r.url.startsWith('/')&&!r.url.startsWith('//')?r.url:'/')}" data-backend-notification="${esc(r.id)}"><strong>${esc(r.title)}</strong><small>${esc(r.created_at)}</small></a></div>`):panelEmpty('bell','You’re all caught up','No account notifications are available.');
   return data.rows?.length?rowsHTML(data.rows,r=>`<div class="help-draft"><strong>${esc(r.category)} · ${esc(r.status)}</strong><p>${esc(r.description)}</p><small>${esc(r.created_at)}</small></div>`):panelEmpty('news','No submitted reports','Submitted corrections and their status will appear here.');
  }
  if(profilePage==='account-required')return session?.user?securityForm(securityKind):panelEmpty('shield','Sign in to continue','Account protection requires a signed-in account.','<button class="primary" data-open-auth="login">Sign in</button>');
  return original.profilePageHTML();
 };
 const endpoints={sessions:'sessions','login-activity':'security-events',connections:'connections',notifications:'notifications','correction-drafts':'corrections'};
 async function loadProfilePage(page,token){if(!endpoints[page]||!session?.user)return;try{pageData.set(page,await api(endpoints[page]));}catch(error){pageData.set(page,{error:error.message});}if(token===pageRevision&&profilePage===page)renderNavigation();}
 showProfilePage=function(page){pageRevision++;original.showProfilePage(page);if(endpoints[page]){pageData.delete(page);renderNavigation();void loadProfilePage(page,pageRevision)}};
 renderNavigation=function(...args){followRender(()=>original.renderNavigation(...args));const host=document.getElementById('navigation-body');wording(host);const footer=document.getElementById('nav-footer');if(footer&&navKind==='profile')footer.textContent=session?.user?'Your space · Account':'Your space';
  if(profilePage==='notification-settings'){const inputs=host.querySelectorAll('input[aria-label*="Email alerts"],input[aria-label*="Security email"]');for(const input of inputs){input.disabled=!session?.user;input.checked=input.getAttribute('aria-label').startsWith('Security')?session?.preferences?.security_email!==false:!!session?.preferences?.email;input.dataset.backendEmail=input.getAttribute('aria-label').startsWith('Security')?'security_email':'email';}host.querySelector('.subpage-intro')?.replaceChildren(document.createTextNode('Choose the notifications delivered to your account.'));}
  if(profilePage==='notification-settings'&&session?.user&&'PushManager'in window){const delivery=host.querySelector('#notification-frequency')?.closest('section');if(delivery&&!delivery.querySelector('[data-backend-push]')){const label=document.createElement('label');label.className='switch-row';label.innerHTML='<span><strong>Browser notifications</strong><small>Enable notifications on this device</small></span><input type="checkbox" class="ios-switch" role="switch" aria-label="Browser notifications" data-backend-push>';label.querySelector('input').checked=!!session.preferences?.push;delivery.insertBefore(label,delivery.firstChild.nextSibling);}}
  if(profilePage==='correction'){const button=host.querySelector('.sticky-save button[type=submit],button[type=submit]');if(button)button.textContent='Submit report';const hint=host.querySelector('.subpage-intro');if(hint)hint.textContent='Describe the issue and include a supporting source. Your report will be submitted for review.';const email=host.querySelector('#correction-email');if(email&&session?.user){email.value=session.user.email;email.readOnly=true;}}
  if(profilePage==='privacy'){const note=host.querySelector('.source-status');if(note)note.textContent=session?.user?'Manage the security of your connected account.':'Sign in to manage password, authenticator and active sessions.';}
  if(profilePage==='follows'){
     const scope=host.querySelector('.follow-scope');if(scope)scope.textContent=followView==='following'?(session?.user?'Your follows are synced with your account. Manage notification preferences for each item.':'Sign in to save follows across your devices.'):'Browse people, places and elections. Search and filters include the full directory.';
     const key=JSON.stringify([followView,followCategory,followSort,followLocation,followAlertFilter]),previous=host.dataset.followView;host.dataset.followView=key;
     host.getAnimations().forEach(a=>a.cancel());if(previous!==key&&!authMotionQuery.matches)host.animate([{opacity:.5,transform:'translateY(5px)'},{opacity:1,transform:'translateY(0)'}],{duration:160,easing:'cubic-bezier(.2,.8,.2,1)'});
    }
    enhanceFollowControls();
 };
 async function webp(file,kind){if(!file||!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>5*1024*1024)throw Error('Choose a JPEG, PNG or WebP image under 5 MB.');const image=await createImageBitmap(file);try{const max=kind==='photo'?320:1200,ratio=Math.min(1,max/Math.max(image.width,image.height)),canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(image.width*ratio));canvas.height=Math.max(1,Math.round(image.height*ratio));canvas.getContext('2d').drawImage(image,0,0,canvas.width,canvas.height);return canvas.toDataURL('image/webp',.8);}finally{image.close()}}
 readProfileImage=webp;
 async function saveProfile(){syncEditDraft();const d=profileEditDraft,images={};for(const [field,kind]of [['photo','avatar'],['cover','cover']]){if(d[field]?.startsWith('data:image/webp;base64,'))images[kind]={data:d[field].split(',')[1]};else if(!d[field]&&session.profile?.[kind+'_url'])images[kind]=null;}await api('profile',{display_name:d.name.trim(),username:d.username||'',bio:d.bio||'',location:d.location||'',website:d.website||'',social_links:d.social||{},images});await refresh();showProfilePage('profile');notify('Profile saved to your account.');}
 async function saveNotifications(){const categories=[];if(document.querySelector('[data-notify-choice=elections]')?.checked||document.querySelector('[data-notify-choice=results]')?.checked)categories.push('elections');if(document.querySelector('[data-notify-choice=leaders]')?.checked)categories.push('representatives');if(document.querySelector('[data-notify-choice=news]')?.checked)categories.push('news');if(document.querySelector('[data-notify-choice=policy]')?.checked)categories.push('government');const frequency=document.getElementById('notification-frequency').value;
  await api('preferences',{in_app:document.querySelector('[data-notify-choice=inapp]').checked,email:!!document.querySelector('[data-backend-email=email]')?.checked,security_email:document.querySelector('[data-backend-email=security_email]')?.checked!==false,categories,frequency:frequency==='all'?'instant':frequency,quiet_enabled:document.getElementById('quiet-enabled').checked,quiet_start:document.getElementById('quiet-start').value,quiet_end:document.getElementById('quiet-end').value,quiet_days:[0,1,2,3,4,5,6]});await refresh();notify('Notification preferences saved to your account.');
 }
 async function saveFollowAlerts(){const e=await entity(activeFollowId),types=[];for(const [ui,backend]of [['news','news'],['elections','elections'],['policy','government'],['events','representatives']])if(document.querySelector(`[data-item-alert-type=${ui}]`)?.checked)types.push(backend);await api('follow-preferences',{entity_id:e.id,muted:!document.getElementById('follow-alerts-enabled').checked,alert_types:types});await refresh();notify('Follow preferences saved.');}
 async function saveRepresentativeAlerts(){const form=document.getElementById('representative-alert-form'),e=await entity(representativeId),types=[];for(const [ui,backend]of [['news','news'],['elections','elections'],['policy','government'],['events','representatives']])if(form.elements[ui]?.checked)types.push(backend);await api('follow-preferences',{entity_id:e.id,muted:!form.elements.enabled.checked,alert_types:types});await refresh();document.getElementById('dialog').close();notify('Profile preferences saved.');}
 async function correction(){const category=document.getElementById('correction-category').value,description=[document.getElementById('correction-text').value.trim(),'Context: '+document.getElementById('correction-context').value,'Shown: '+document.getElementById('error-actual').value,'Expected: '+document.getElementById('error-expected').value].join('\n');await api('corrections',{page_url:location.pathname+location.search,category:/person|party/i.test(category)?'identity':/map|boundary/i.test(category)?'boundary':/result/i.test(category)?'result':'other',description,source_url:document.getElementById('error-source-url').value.trim()||null});showProfilePage('correction-drafts');notify('Your report was submitted.');}
 function download(name,data){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
 window.addEventListener('submit',event=>{
  const form=event.target,actions={'edit-profile-form':saveProfile,'notification-form':saveNotifications,'follow-alerts-form':saveFollowAlerts,'representative-alert-form':saveRepresentativeAlerts,'correction-form':correction};if(!actions[form.id]&&form.id!=='connected-security-form')return;event.preventDefault();event.stopImmediatePropagation();if(!form.reportValidity()||!signedIn())return;const button=form.querySelector('button[type=submit]');if(button?.disabled)return;if(button)button.disabled=true;
  (async()=>{if(form.id!=='connected-security-form')return actions[form.id]();await api('reauthenticate',{password:document.getElementById('connected-current-password').value});const kind=form.dataset.kind;if(kind==='password'){await api('password',{password:document.getElementById('connected-new-password').value});notify('Password updated.');showProfilePage('privacy');}else if(kind==='delete'){await api('delete-account',{confirmation:document.getElementById('connected-delete-confirm').value});await refresh();showProfilePage('root');notify('Account deleted.');}else{const r=await api('mfa-enroll',{});const host=document.getElementById('connected-mfa');host.replaceChildren();const text=document.createElement('p');text.textContent='Add this account to your authenticator using this secret: '+r.factor.totp.secret;host.append(text);const input=document.createElement('input');input.id='connected-mfa-code';input.className='setting-input';input.inputMode='numeric';input.autocomplete='one-time-code';input.placeholder='Authenticator code';host.append(input);const verify=document.createElement('button');verify.type='button';verify.className='primary';verify.textContent='Verify authenticator';verify.onclick=async()=>{try{const challenge=await api('mfa-challenge',{factor_id:r.factor.id});await api('mfa-verify',{factor_id:r.factor.id,challenge_id:challenge.id,code:input.value});host.replaceChildren();notify('Authenticator enabled.');}catch(error){status(error.message,true)}};host.append(verify);}})().catch(error=>status(error.message,true)).finally(()=>{if(button?.isConnected)button.disabled=false});
 },true);
 let afterConfirmation;
 async function protectedAction(action){try{return await action()}catch(error){if(error.code!=='reauthentication_required')throw error;afterConfirmation=action;showDialog('Confirm your identity',`<form id="backend-confirm-form" class="profile-form"><section class="settings-card"><label class="setting-label" for="backend-confirm-password">Current password</label><input type="password" id="backend-confirm-password" class="setting-input" autocomplete="current-password" required><p class="form-error" role="status"></p><button type="submit" class="primary">Continue</button></section></form>`);}}
 window.addEventListener('submit',event=>{if(event.target.id!=='backend-confirm-form')return;event.preventDefault();event.stopImmediatePropagation();const form=event.target;if(!form.reportValidity())return;const password=document.getElementById('backend-confirm-password').value;form.querySelector('button').disabled=true;(async()=>{await api('reauthenticate',{password});const action=afterConfirmation;afterConfirmation=null;document.getElementById('dialog').close();await action?.()})().catch(error=>{form.querySelector('.form-error').textContent=error.message}).finally(()=>{form.querySelector('button').disabled=false})},true);
 const settingsHTML=accountSettingsHTML;accountSettingsHTML=function(){return settingsHTML()+(session?.user?group('Account',[row('Delete account','trash','data-backend-delete','Permanently delete your account')]):'')};
 window.addEventListener('click',event=>{
  const b=event.target.closest('button,a');if(!b)return;const d=b.dataset;let action;
  if(b.matches(followSelector))action=()=>toggle(followId(b));
  else if(d.authSignout!==undefined)action=async()=>{await api('logout',{});await refresh();profileTab='activity';showProfilePage('root');notify('Signed out.');};
  else if(d.authResend!==undefined)action=resendCode;
  else if(d.authFinish!==undefined)action=()=>{closeAuth();openNavigation('profile')};
  else if(d.profilePage==='account-required'){securityKind=/two-factor/i.test(b.textContent)?'mfa':'password';}
  else if(d.backendRetry!==undefined)action=()=>showProfilePage(profilePage);
  else if(d.backendRevoke)action=()=>protectedAction(async()=>{if(!signedIn())return;await api('revoke-session',{id:d.backendRevoke});await refresh();showProfilePage('sessions');});
  else if(d.backendGoogleLink!==undefined)action=()=>protectedAction(async()=>{const r=await api('link-google',{});location.assign(r.url)});
  else if(d.exportLocal!==undefined)action=()=>protectedAction(async()=>{if(!signedIn())return;download('electrol-account.json',await api('export',{}));});
  else if(d.backendDelete!==undefined)action=()=>{securityKind='delete';showProfilePage('account-required')};
  else if(d.deleteSave!==undefined)action=async()=>{const item=savedComparisons[Number(d.deleteSave)];if(!item?._backendId||!signedIn())return;await api('save-search',{remove:true,id:item._backendId});await refresh();updateCounts();if(document.getElementById('navigation-panel').open)renderNavigation();else showSaved();};
  else if(d.saveFollow)action=async()=>{if(!signedIn())return;const e=await entity(d.saveFollow);await api('save-profile',{entity_id:e.id,remove:savedProfiles.has(e.id)});await refresh();refreshFollowUI();};
  if(!action)return;event.preventDefault();event.stopImmediatePropagation();Promise.resolve().then(action).catch(error=>status(error.message,true));
 },true);
 window.addEventListener('change',event=>{const input=event.target;if(!input.matches('[data-backend-push]'))return;input.disabled=true;(async()=>{if(!signedIn())return;const registration=await navigator.serviceWorker.register('/sw.js');await navigator.serviceWorker.ready;if(input.checked){const config=await api('push-config');if(!config.enabled)throw Error('Push delivery is not configured.');if(await Notification.requestPermission()!=='granted')throw Error('Notification permission was not granted.');const key=Uint8Array.from(atob(config.publicKey.replaceAll('-','+').replaceAll('_','/')),c=>c.charCodeAt(0)),subscription=await registration.pushManager.getSubscription()||await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:key});await api('push-subscribe',subscription.toJSON());}else{const subscription=await registration.pushManager.getSubscription();if(subscription){await api('push-unsubscribe',{endpoint:subscription.endpoint});await subscription.unsubscribe();}}await refresh();notify('Browser notification preference saved.');})().catch(error=>{input.checked=!input.checked;status(error.message,true)}).finally(()=>input.disabled=false);},true);
 // Preserve the HTML's News and appearance/language behavior. Remove only the
 // election calendar requested for a later release, without changing navigation.
 homeCalendarHTML=()=>'';
 const municipalContent=renderMunicipalContent;renderMunicipalContent=function(...args){municipalContent(...args);document.querySelectorAll('#mc-detail-content section').forEach(section=>{if(/schedule/i.test(section.querySelector('h2,h3')?.textContent||''))section.remove()})};
 const originalLegacy=legacyProfilePageHTML;legacyProfilePageHTML=function(){return originalLegacy().replace(/<div class="settings-card"><h3>Schedule watchlist<\/h3>[\s\S]*?<\/div>/g,'').replace(/<div class="detail-row"><span>Schedule watches<\/span>[\s\S]*?<\/div>/g,'');};
 async function restoreEntry(){
  const p=location.pathname.replace(/\/+$/,'')+'/',q=new URLSearchParams(location.search);
  if(/^\/auth\/(callback|verify)\//.test(p)){history.replaceState({},'',p);try{if(q.get('error'))throw Error('Sign-in was cancelled. Try again or use email.');const result=q.get('code')?await api('callback',{code:q.get('code')}):await api('verify-email',{token_hash:q.get('token_hash'),type:q.get('type')||'email'});await refresh();let back;try{back=JSON.parse(sessionStorage.getItem('electrol-auth-return')||'null')}catch{}sessionStorage.removeItem('electrol-auth-return');const safe=back?.path?.startsWith('/')&&!back.path.startsWith('//')&&!back.path.includes('\\')?back.path:'/';history.replaceState({},'',safe);if(result.next==='/auth/reset-password/'){openAuth('reset');return;}if(back?.edition){await window.ElectrolHTMLData?.edition(back.edition);await openElectionEdition(back.edition);if(back.scope)fullScope=back.scope;if(back.tab)electionDashboardTab=back.tab;renderElectionDashboard();}if(back?.person)openRepresentative(back.person);else if(back?.destination?.startsWith('municipal:')&&back.municipal)openMunicipalProfile(back.municipal);else if(!back?.edition)openNavigation('profile');}catch(error){openAuth('login');authState.error={general:error.message};renderAuth(true)}return;}
  if(/^\/auth\//.test(p)){openAuth(p.includes('signup')?'signup':p.includes('forgot')?'forgot':p.includes('reset')?'reset':'login');return;}
  if(/^\/account\//.test(p)){openNavigation('profile');const view=({'follows':'follows','security':'privacy','sessions':'sessions','preferences':'notification-settings','notifications':'notifications','settings':'account'})[p.split('/')[2]]||q.get('view')||'root';showProfilePage(view);}
 }
 let queued=false;new MutationObserver(()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;enhanceFollowControls()})}).observe(document.body,{childList:true,subtree:true});
 const channel=typeof BroadcastChannel==='function'?new BroadcastChannel('electrol-account'):null;channel?.addEventListener('message',()=>refresh().then(()=>{if(document.getElementById('navigation-panel').open)renderNavigation()}).catch(()=>{}));
 window.ElectrolBackend={api,refresh,entity,get user(){return session?.user||null},get configured(){return !!session?.configured}};
 if(siteDestination==='home')showPrimary('home');
 window.ElectrolBackend.ready=refresh().catch(error=>{session={configured:false,user:null};sessionKnown=true;applyProfile();enhanceFollowControls();return {configured:false,error:error.message};}).then(async()=>{await restoreEntry();await window.ElectrolHTMLData?.restoreEntry();});
})();
