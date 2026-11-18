import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
import {accountFixture} from './account-test-fixture.mjs';
import {accountHandler} from '../netlify/functions/account.mjs';
const fixture=accountFixture();let writeGate=null,failWrite=false;
const handler=accountHandler({env:fixture.env,fetcher:async(url,options={})=>{
 if(new URL(url).pathname==='/rest/v1/user_follows'&&['POST','DELETE'].includes(options.method)){
  if(writeGate)await writeGate;
  if(failWrite){failWrite=false;return Response.json({},{status:503});}
 }
 return fixture.fetcher(url,options);
}});
const browser=await launchBrowser();
try{
 const context=await browser.newContext({viewport:{width:393,height:852}}),page=await context.newPage();
 await context.addCookies([{name:'ei_access',value:fixture.token,url:fixture.env.SITE_URL}]);
 const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',async route=>{
  const req=route.request(),u=new URL(req.url());
  if(u.pathname.startsWith('/api/account/')){requests.push(u.pathname);const response=await handler(new Request(req.url(),{method:req.method(),headers:req.headers(),body:req.postData()||undefined}));return route.fulfill({status:response.status,headers:{...Object.fromEntries(response.headers),'set-cookie':response.headers.getSetCookie().join('\n')},body:Buffer.from(await response.arrayBuffer())});}
  if(['/js/','/css/','/data/','/assets/'].some(p=>u.pathname.startsWith(p)))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json'})[path.extname(u.pathname)]||'application/octet-stream'});
  const r=await render(u.pathname);return route.fulfill({contentType:'text/html',body:r.html});
 });
 await page.goto(fixture.env.SITE_URL+'/');await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(()=>ElectrolHTMLData.ready);
 const result=await page.evaluate(()=>{
  let catalogCalls=0;const original=followCatalog;followCatalog=function(...args){catalogCalls++;return original(...args)};
  const start=performance.now();openExploreFollows();const ms=performance.now()-start;
  return {ms,catalogCalls,cards:document.querySelectorAll('.follow-item').length,total:availableFollowRows().length};
 });
 assert(result.ms<1000,'Explore Follows is still slow');assert(result.catalogCalls<10,'Follow catalog rebuilt per card');assert.equal(result.cards,36);
 await page.locator('[data-follow-more]').click();assert.equal(await page.locator('.follow-item').count(),72);
 const ids=await page.locator('.follow-item [data-toggle-follow]').evaluateAll(rows=>rows.map(x=>x.dataset.toggleFollow));assert.equal(new Set(ids).size,ids.length,'Duplicate cards after Show more');
 const hidden=await page.evaluate(()=>availableFollowRows().at(-1));
 await page.locator('#follow-search').fill(hidden.name);assert(await page.locator('[data-toggle-follow]').evaluateAll((rows,id)=>rows.some(x=>x.dataset.toggleFollow===id),hidden.id),'Search missed an item beyond the first batch');
 await page.locator('#follow-search').fill('no-such-follow-xyz');assert.equal(await page.locator('.follow-item').count(),0);
 await page.locator('#follow-search').fill('');assert.equal(await page.locator('.follow-item').count(),36);
 const sessions=requests.filter(x=>x.endsWith('/session')).length;
 const following=await page.evaluate(()=>{followView='following';const start=performance.now();renderNavigation();return {ms:performance.now()-start,count:document.querySelectorAll('.follow-item').length}});
 assert.equal(following.count,fixture.follows.size,'Following must contain each account follow exactly once');assert(following.ms<500,'Following is still slow');
 const first=page.locator('.follow-item [data-toggle-follow][aria-pressed=true]').first(),id=await first.getAttribute('data-toggle-follow');
 let releaseWrite;writeGate=new Promise(resolve=>{releaseWrite=resolve});
 const writesBefore=requests.filter(x=>x.endsWith('/unfollow')).length;
 await first.click();await page.waitForSelector('.follow-toggle[aria-busy=true] .follow-progress');
 assert(await first.isDisabled());await first.evaluate(button=>{button.click();button.click()});
 releaseWrite();writeGate=null;
 await page.waitForFunction(id=>!Array.from(document.querySelectorAll('.follow-item [data-toggle-follow]')).some(b=>b.dataset.toggleFollow===id),id);
 assert.equal(requests.filter(x=>x.endsWith('/unfollow')).length-writesBefore,1,'Duplicate unfollow request');
 const savedName=await page.evaluate(id=>findFollow(id).name,id);
 await page.locator('[data-follow-view=explore]').click();await page.locator('#follow-search').fill(savedName);
 await page.evaluate(id=>Array.from(document.querySelectorAll('[data-toggle-follow]')).find(b=>b.dataset.toggleFollow===id).click(),id);
 await page.waitForFunction(id=>Array.from(document.querySelectorAll('[data-toggle-follow]')).find(b=>b.dataset.toggleFollow===id)?.getAttribute('aria-pressed')==='true',id);
 failWrite=true;
 await page.evaluate(id=>Array.from(document.querySelectorAll('[data-toggle-follow]')).find(b=>b.dataset.toggleFollow===id).click(),id);
 await page.waitForFunction(id=>{const b=Array.from(document.querySelectorAll('[data-toggle-follow]')).find(b=>b.dataset.toggleFollow===id);return b&&!b.disabled&&b.getAttribute('aria-pressed')==='true'},id);
 assert.equal(requests.filter(x=>x.endsWith('/session')).length,sessions,'Switching follow views refreshed the account');
 await page.emulateMedia({reducedMotion:'reduce'});
 const reduced=await page.evaluate(()=>{followView='following';renderNavigation();return document.getElementById('navigation-body').getAnimations().length});assert.equal(reduced,0);
 await page.reload();await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(()=>ElectrolHTMLData.ready);
 await page.evaluate(()=>{openExploreFollows();followView='following';renderNavigation()});
 assert(await page.locator('[data-toggle-follow]').evaluateAll((rows,id)=>rows.some(b=>b.dataset.toggleFollow===id&&b.getAttribute('aria-pressed')==='true'),id),'Follow did not persist across reload');
 await fs.mkdir('reports/following',{recursive:true});
 for(const width of [393,1440]){
  await page.setViewportSize({width,height:852});await page.emulateMedia({reducedMotion:'no-preference'});
  await page.evaluate(()=>openExploreFollows());
  await page.screenshot({path:'reports/following/explore-'+width+'.png',animations:'disabled'});
  assert(await page.evaluate(()=>document.getElementById('navigation-body').scrollWidth<=document.getElementById('navigation-body').clientWidth+1),'Follow panel overflows');
 }
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({result,following,search:'all records',pagination:'no duplicates',followUnfollow:'passed',reload:'persisted',errorRecovery:'passed',reducedMotion:'passed',widths:[393,1440],errors}));
}finally{await browser.close()}
