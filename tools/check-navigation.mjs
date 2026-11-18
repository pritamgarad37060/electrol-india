import assert from 'node:assert/strict';
import fs from 'node:fs/promises';import path from 'node:path';
import {launchBrowser} from './browser.mjs';import {render,root} from './build.mjs';
const browser=await launchBrowser();let activePage;
try{
 for(const width of [393,1440]){
  const context=await browser.newContext({viewport:{width,height:852}}),page=await context.newPage(),errors=[];
  activePage=page;
  await page.addInitScript(()=>{window.navigationTrace=[];const native=History.prototype.pushState;History.prototype.pushState=function(state,...args){window.navigationTrace.push({kind:'push',id:state?.electrolNavigation?.id,page:state?.electrolNavigation?.route?.page});return native.call(this,state,...args)};window.addEventListener('popstate',event=>window.navigationTrace.push({kind:'pop',id:event.state?.electrolNavigation?.id,page:event.state?.electrolNavigation?.route?.page}));});
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{const u=new URL(route.request().url());
   if(u.hostname==='outside.example')return route.fulfill({contentType:'text/html',body:'<h1>Outside website</h1>'});
   if(u.pathname.startsWith('/api/account/'))return route.fulfill({json:{configured:true,user:null,csrf:'fixture-csrf',rows:[],preferences:{},google:false}});
   if(['/js/','/css/','/data/','/assets/'].some(p=>u.pathname.startsWith(p)))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json'})[path.extname(u.pathname)]||'application/octet-stream'});
   const r=await render(u.pathname);return route.fulfill({contentType:'text/html',body:r.html});
  });
  await page.goto('https://outside.example/');await page.goto('http://127.0.0.1/');
  await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(()=>ElectrolHTMLData.ready);
  const flush=()=>page.evaluate(()=>ElectrolNavigation.flush());
  const settle=()=>page.waitForFunction(()=>!ElectrolNavigation.restoring);
  await page.evaluate(()=>showPrimary('explore'));await flush();
  const previousScroll=await page.evaluate(()=>{window.scrollTo({top:280,behavior:'instant'});return scrollY});await flush();
  await page.evaluate(()=>showPrimary('news'));await flush();
  await page.goBack();await page.waitForFunction(()=>siteDestination==='explore');await settle();assert.equal(new URL(page.url()).hostname,'127.0.0.1');assert.equal(await page.evaluate(()=>Math.round(scrollY)),Math.round(previousScroll),'Back lost scroll position');
  for(let round=0;round<10;round++){
   await page.goForward();await page.waitForFunction(()=>siteDestination==='news');await settle();
   await page.goBack();await page.waitForFunction(()=>siteDestination==='explore');await settle();
  }
  // Branching after Back must retain a working previous-screen relationship.
  await page.evaluate(()=>openDiscovery('constituencies'));await flush();
  await page.locator('#destination-view .primary-back').click();await page.waitForFunction(()=>siteDestination==='explore');await settle();
  await page.evaluate(()=>openExploreFollows());await flush();
  await page.locator('#follow-search').fill('Pune');await flush();
  await page.evaluate(()=>showProfilePage('appearance'));await flush();
  await page.goBack();await page.waitForFunction(()=>profilePage==='follows');await settle();
  assert.equal(await page.locator('#follow-search').inputValue(),'Pune');
  await page.goBack();await page.waitForFunction(()=>!document.getElementById('navigation-panel').open);await settle();
  assert.equal(await page.evaluate(()=>siteDestination),'explore');
  await page.goBack();await page.waitForFunction(()=>siteDestination==='home');await settle();
  // Home is the actual entry page: Back remains free to leave the website.
  await page.goBack();await page.waitForURL('https://outside.example/');
  await page.goto('http://127.0.0.1/');await page.evaluate(()=>ElectrolNavigation.ready);
  await page.evaluate(()=>showPrimary('explore'));await flush();await page.evaluate(()=>showPrimary('news'));await flush();
  await page.reload();await page.evaluate(()=>ElectrolNavigation.ready);assert.equal(await page.evaluate(()=>siteDestination),'news','Reload lost the current screen');
  await page.goBack();await page.waitForFunction(()=>siteDestination==='explore');await settle();
  await page.evaluate(()=>openElectionEdition('assembly|Maharashtra|2024'));await flush();
  await page.evaluate(()=>openFullSeat(213,'Maharashtra'));await flush();
  await page.locator('#dialog .full-winner-card [data-result-person]').click();await page.waitForFunction(()=>siteDestination==='representative-profile');await flush();
  await page.goBack();await page.waitForFunction(()=>document.getElementById('dialog').open&&siteDestination==='election-dashboard');await settle();
  assert.equal(await page.evaluate(()=>electionEdition.id),'assembly|Maharashtra|2024');
  await page.goBack();await page.waitForFunction(()=>!document.getElementById('dialog').open);await settle();
  assert.equal(await page.evaluate(()=>siteDestination),'election-dashboard');
  const pageEntry=await page.evaluate(()=>ElectrolNavigation.current.id);
  await page.evaluate(()=>openFullSeat(213,'Maharashtra'));await flush();
  await page.locator('#close-dialog').click();await page.waitForFunction(id=>ElectrolNavigation.current.id===id,pageEntry);await settle();
  await page.goBack();await page.waitForFunction(()=>siteDestination==='explore');await settle();
  await page.evaluate(()=>loadConfig({type:'assembly',mode:'year',a:'Maharashtra',b:'Maharashtra',sa:'Maharashtra',sb:'Maharashtra',ya:'2024',yb:'2019',wa:'all',wb:'all'}));
  await page.waitForFunction(()=>document.getElementById('panel').getAttribute('aria-busy')==='false');await flush();
  const comparison=await page.evaluate(()=>JSON.stringify(current));
  await page.evaluate(()=>showPrimary('news'));await flush();
  await page.goBack();await page.waitForFunction(()=>siteDestination==='compare');await settle();
  assert.equal(await page.evaluate(()=>JSON.stringify(current)),comparison,'Back changed the comparison selection');
  assert.deepEqual(errors,[]);console.log(JSON.stringify({width,browserBackForward:'passed',inSiteBack:'passed',branching:'passed',followsFilters:'restored',exitFromEntry:'allowed',reload:'restored',representativeToResult:'restored',comparison:'restored',repeatedBackForward:10,errors}));
  await context.close();
 }
}catch(error){console.log(await activePage.evaluate(()=>({url:location.href,page:siteDestination,current:ElectrolNavigation.current,state:history.state,trace:window.navigationTrace})));throw error;}finally{await browser.close()}
