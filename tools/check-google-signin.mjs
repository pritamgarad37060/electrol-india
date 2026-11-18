import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {accountHandler} from '../netlify/functions/account.mjs';
import {createAccountService} from '../netlify/lib/account-core.mjs';
import {accountFixture} from './account-test-fixture.mjs';
import {render,root} from './build.mjs';
import {launchBrowser} from './browser.mjs';
const fixture=accountFixture(),headers=new Headers();
const csrf=createAccountService(fixture.env).csrf(new Request(fixture.env.SITE_URL),headers);
const cookie=headers.getSetCookie()[0].split(';')[0];
const entered=[],releases=[];
const handler=accountHandler({env:fixture.env,fetcher:async url=>{
 const p=new URL(url).pathname;entered.push(p);
 await new Promise(resolve=>releases.push(resolve));
 if(p==='/auth/v1/settings')return Response.json({external:{google:true}});
 if(p.endsWith('/rpc/consume_account_rate'))return Response.json(true);
 throw Error('Unnecessary request: '+p);
}});
const request=()=>new Request(fixture.env.SITE_URL+'/api/account/google',{method:'POST',headers:{Origin:fixture.env.SITE_URL,Cookie:cookie,'X-Account-CSRF':csrf,'Content-Type':'application/json'},body:JSON.stringify({next:'/'})});
const pending=handler(request());
await new Promise(resolve=>setTimeout(resolve,30));
assert.equal(entered.length,2,'Provider and rate checks must start together');
releases.forEach(resolve=>resolve());
const response=await pending;assert.equal(response.status,200);
const target=new URL((await response.json()).url);
assert.equal(target.searchParams.get('provider'),'google');
assert.equal(target.searchParams.get('code_challenge_method'),'s256');
assert.match(response.headers.getSetCookie().join(';'),/ei_flow=.*HttpOnly/);
assert.equal((await handler(new Request(fixture.env.SITE_URL+'/api/account/google',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}))).status,403);
// The CSRF bootstrap must finish locally even when Supabase is stalled.
const localOnly=accountHandler({env:fixture.env,fetcher:()=>{throw Error('Bootstrap contacted Supabase')}});
const boot=await localOnly(new Request(fixture.env.SITE_URL+'/api/account/auth-bootstrap'));
assert.equal(boot.status,200);assert((await boot.json()).csrf);
assert.match(response.headers.get('Server-Timing'),/oauth_rate;dur=/);
const browser=await launchBrowser();
const results=[];
try{
 for(const [width,signedIn] of [[393,false],[1440,true]]){
  const context=await browser.newContext({viewport:{width,height:852}}),page=await context.newPage();
  const requests=[],errors=[];let fail=true,followsWaiting=false,savedInParallel=false;
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.pathname.startsWith('/api/account/')){
    const action=u.pathname.split('/').at(-1);requests.push(action);
    if(action==='auth-bootstrap')return route.fulfill({json:{csrf:'fixture-csrf',authOrigin:'https://example.supabase.co'}});
    if(action==='google-config')return route.fulfill({json:{google:true}});
    if(action==='session')return route.fulfill({json:{configured:true,user:signedIn?{id:fixture.user.id,email:fixture.user.email}:null,csrf:'fixture-csrf',preferences:{}}});
    if(action==='follows'){followsWaiting=true;await new Promise(resolve=>setTimeout(resolve,150));followsWaiting=false;}
    if(['saved-searches','saved-content'].includes(action)&&followsWaiting)savedInParallel=true;
    if(action==='google'){
     await new Promise(resolve=>setTimeout(resolve,60));
     return route.fulfill({status:fail?503:200,json:fail?{error:'google_not_configured'}:{url:fixture.env.SITE_URL+'/oauth-test/'}});
    }
    return route.fulfill({json:{rows:[],has_more:false}});
   }
   if(u.pathname==='/oauth-test/')return route.fulfill({contentType:'text/html',body:'<h1>Provider redirect reached</h1>'});
   if(['/js/','/css/','/data/','/assets/'].some(p=>u.pathname.startsWith(p)))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json'})[path.extname(u.pathname)]||'application/octet-stream'});
   const r=await render(u.pathname);return route.fulfill({contentType:'text/html',body:r.html});
  });
  await page.goto(fixture.env.SITE_URL+'/');
  await page.evaluate(()=>ElectrolBackend.ready);
  await page.evaluate(()=>ElectrolHTMLData.ready);
  if(signedIn)assert(savedInParallel,'Saved account content waited for follows');
  await page.evaluate(()=>openAuth('login'));
  const motion=await page.evaluate(()=>{authSetStep('signup');return document.getElementById('auth-panel-body').getAnimations().length});
  assert(motion>0,'Auth step transition was not animated');
  await page.emulateMedia({reducedMotion:'reduce'});
  const reduced=await page.evaluate(()=>{authSetStep('login');return {animations:document.getElementById('auth-panel-body').getAnimations().filter(a=>a.playState==='running').length,panel:getComputedStyle(document.getElementById('auth-panel')).animationName}});
  assert.equal(reduced.animations,0,'Reduced motion left a step animation running');
  assert.equal(reduced.panel,'none');
  await page.emulateMedia({reducedMotion:'no-preference'});
  await fs.mkdir('reports/sign-in',{recursive:true});
  await page.evaluate(()=>openAuth('login'));
  assert(await page.locator('#auth-panel').isVisible(),'Sign-in dialog must be visible');
  await page.screenshot({path:'reports/sign-in/auth-'+width+'.png',animations:'disabled'});
  const sessions=requests.filter(x=>x==='session').length;
  const busy=await page.evaluate(()=>{void startProvider('Google');void startProvider('Google');const b=document.querySelector('[data-auth-provider="Google"]');return {disabled:b.disabled,spinner:!!b.querySelector('.auth-spinner'),label:b.textContent}});
  assert(busy.disabled&&busy.spinner&&busy.label.includes('Opening Google'),'Google button must immediately show a loading spinner');
  await page.waitForFunction(()=>!authState.busy&&!!authState.error.general);
  assert.equal(requests.filter(x=>x==='google').length,1,'Duplicate click initiated overlapping OAuth flows');
  assert.equal(requests.filter(x=>x==='session').length,sessions,'Google click refreshed the full account');
  assert.equal(await page.locator('[data-auth-provider="Google"]').isEnabled(),true);
  fail=false;const started=performance.now();
  await page.locator('[data-auth-provider="Google"]').click();
  await page.waitForURL('**/oauth-test/');
  results.push({width,signedIn,simulatedRedirectMs:Math.round(performance.now()-started),extraSessionRequests:requests.filter(x=>x==='session').length-sessions});
  assert.deepEqual(errors,[]);await context.close();
 }
 // Reproduce clicking Google while the initial session request is stalled.
 const coldContext=await browser.newContext(),coldPage=await coldContext.newPage();
 let releaseSession,googleStarted=false,sessionReleased=false;
 const sessionGate=new Promise(resolve=>{releaseSession=resolve});
 await coldPage.route('**/*',async route=>{
  const u=new URL(route.request().url());
  if(u.pathname==='/api/account/auth-bootstrap')return route.fulfill({json:{csrf:'cold-csrf',authOrigin:'https://example.supabase.co'}});
  if(u.pathname==='/api/account/session'){await sessionGate;sessionReleased=true;return route.fulfill({json:{configured:true,user:null,csrf:'cold-csrf'}}).catch(()=>{});}
  if(u.pathname==='/api/account/google-config')return route.fulfill({json:{google:true}});
  if(u.pathname==='/api/account/google'){googleStarted=true;return route.fulfill({json:{url:fixture.env.SITE_URL+'/oauth-test/'}});}
  if(u.pathname==='/oauth-test/')return route.fulfill({contentType:'text/html',body:'<h1>Provider redirect reached</h1>'});
  if(['/js/','/css/','/data/','/assets/'].some(p=>u.pathname.startsWith(p)))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json'})[path.extname(u.pathname)]||'application/octet-stream'});
  const r=await render(u.pathname);return route.fulfill({contentType:'text/html',body:r.html});
 });
 try{
  await coldPage.goto(fixture.env.SITE_URL+'/',{waitUntil:'domcontentloaded'});
  await coldPage.waitForFunction(()=>window.ElectrolBackend);
  await coldPage.evaluate(()=>{openAuth('login');void startProvider('Google')});
  await coldPage.waitForURL('**/oauth-test/',{timeout:3000});
  assert(googleStarted&&!sessionReleased,'Google waited for the initial session');
 }finally{releaseSession();await coldContext.close();}
 console.log(JSON.stringify({coldSession:'Google redirects while initial session is stalled',backend:'parallel availability and rate checks; PKCE cookie and CSRF verified',browser:results,retry:'passed',duplicateClicks:'blocked'}));
}finally{await browser.close()}
