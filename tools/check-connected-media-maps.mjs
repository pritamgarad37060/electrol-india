import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
const read=async f=>JSON.parse(await fs.readFile(path.join(root,f),'utf8'));
const profiles=await read('data/profile-index.json'),people=await read('data/people-directory.json');
let photoBytes=0,sourceHashes=0;for(const p of profiles){const name='data/photos/'+p.id+'.jpg',image=await fs.readFile(path.join(root,name)),source=await fs.readFile(path.join(root,'..',name)).catch(e=>{if(e.code==='ENOENT')return null;throw e;});if(source){assert.equal(createHash('sha256').update(image).digest('hex'),createHash('sha256').update(source).digest('hex'));sourceHashes++;}assert.equal(image[0],255);assert.equal(image[1],216);photoBytes+=image.length;}
console.log(JSON.stringify({localPhotos:profiles.length,bytes:photoBytes,originalHashes:sourceHashes===profiles.length?'matched':'original project unavailable; verified local JPEG files',sourceHashes,profileRecordsWithMPID:people.rows.filter(p=>p.mpid).length}));
await fs.mkdir(path.join(root,'reports/media-maps'),{recursive:true});
const browser=await launchBrowser(),page=await browser.newPage({viewport:{width:393,height:852}}),errors=[];
page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',async route=>{const u=new URL(route.request().url());if(u.hostname!=='127.0.0.1')return route.abort();try{if(u.pathname.startsWith('/api/'))return route.fulfill({contentType:'application/json',body:JSON.stringify({configured:false,user:null})});if(/^\/(js|css|data|assets)\//.test(u.pathname))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.svg':'image/svg+xml'})[path.extname(u.pathname)]||'application/octet-stream'});const r=await render(u.pathname);return route.fulfill({status:r.status,contentType:'text/html',body:r.html});}catch{return route.fulfill({status:404,body:''});}});
try{
 await page.goto('http://127.0.0.1/');await page.evaluate(()=>ElectrolBackend.ready);
 await page.evaluate(()=>ElectrolDirectories.loadPeople());
 const matched=await page.evaluate(()=>allPublicWinners().map(p=>ElectrolProfiles.profileFor(p)?.id).filter(Boolean));assert.equal(new Set(matched).size,543);
 const member=people.rows.find(r=>Number(r.mpid)===5126);await page.evaluate(key=>openRepresentative('imported-person:'+key),member.key);
 await page.waitForFunction(()=>document.querySelector('.rep-hero img[data-profile-photo]')?.naturalWidth>0);assert((await page.locator('.rep-hero img').getAttribute('src')).endsWith('/5126.jpg'));
 await page.screenshot({path:path.join(root,'reports/media-maps/local-profile-photo.png')});await page.evaluate(()=>{peopleLevel='lok';return openPeopleDirectory();});const imgs=page.locator('.entity-avatar img[data-profile-photo]');assert(await imgs.count()>0);await page.waitForFunction(()=>[...document.querySelectorAll('.entity-avatar img[data-profile-photo]')].some(n=>n.naturalWidth>0));
 const states=[['Assam',2026,126],['Bihar',2025,243],['Kerala',2026,140],['Puducherry',2026,30],['Tamil Nadu',2026,234],['Uttar Pradesh',2022,403],['West Bengal',2026,294],['Maharashtra',2024,288]];
 for(const [state,year,count] of states){
  console.log('Checking map '+state);
  await page.evaluate(async([state,year])=>{await openElectionEdition('assembly|'+state+'|'+year);electionDashboardTab='map';renderElectionDashboard();},[state,year]);
  await page.waitForFunction(n=>document.querySelectorAll('[data-state-map-seat]').length===n,count,{timeout:30000});
  const ids=await page.locator('[data-state-map-seat]').evaluateAll(ns=>ns.map(n=>n.dataset.stateMapSeat));assert.equal(new Set(ids).size,count);
  const first=page.locator('[data-state-map-seat]').first();await first.focus();await page.keyboard.press('Enter');assert(await page.locator('[data-state-map-result]').count());
  const before=await page.locator('[data-state-map-svg]').getAttribute('viewBox');await page.locator('[data-state-map-zoom="1.5"]').click();assert.notEqual(await page.locator('[data-state-map-svg]').getAttribute('viewBox'),before);await page.locator('[data-state-map-zoom="reset"]').click();assert.equal(await page.locator('[data-state-map-svg]').getAttribute('viewBox'),before);
  await page.locator('[data-state-map-search]').fill('zzzz-no-seat');assert.equal(await page.locator('[data-state-map-seat].geo-dimmed').count(),count);await page.locator('[data-state-map-search]').fill('');assert.equal(await page.locator('[data-state-map-seat].geo-dimmed').count(),0);
 }
 for(const width of [320,393,768,1440])for(const theme of ['light','dark']){await page.setViewportSize({width,height:852});await page.evaluate(t=>applyAppearance(t),theme);const size=await page.locator('[data-state-map-svg]').boundingBox();assert(size.width<=width);assert(size.height>0);}
 await page.screenshot({path:path.join(root,'reports/media-maps/maharashtra-map.png')});await page.locator('[data-state-map-result]').click();await page.waitForSelector('#dialog[open] .full-seat-sheet');await page.evaluate(()=>document.querySelector('#dialog').close());
 await page.evaluate(()=>loadConfig({type:'assembly',mode:'location',a:'Kerala',b:'Tamil Nadu',ya:'2026',yb:'2026',wa:'all',wb:'all'}));await page.waitForFunction(()=>document.getElementById('panel').getAttribute('aria-busy')==='false');await page.evaluate(()=>{tab='map';mapLayout='geographic';mapRecordSide='a';return renderResults();});
 // Both the comparison tab and its panel renderer use the same boundary adapter.
 const comparison=await page.evaluate(()=>mapPanel(...records()));assert(comparison.includes('data-connected-state-map'));
 await page.waitForFunction(()=>document.querySelectorAll('#panel [data-state-map-seat]').length===140);await page.locator('#panel [data-map-election="b"]').click();await page.waitForFunction(()=>document.querySelectorAll('#panel [data-state-map-seat]').length===234);
 await page.evaluate(async()=>{await openElectionEdition('assembly|Maharashtra|1962');electionDashboardTab='map';renderElectionDashboard();});assert.equal(await page.locator('#destination-view [data-connected-state-map]').count(),0);
 await page.route('**/data/maps/tamil-nadu-assemblies.json',r=>r.fulfill({status:503,body:''}));await page.reload();await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(async()=>{await openElectionEdition('assembly|Tamil Nadu|2026');electionDashboardTab='map';renderElectionDashboard();});await page.waitForSelector('[data-state-map-retry]');assert.equal(await page.locator('[data-state-map-svg]').count(),0);await page.locator('[data-edition-tab="results"]').click();await page.waitForSelector('#full-result-list [data-full-seat]');
 assert.deepEqual(errors,[]);console.log(JSON.stringify({photos:'543 copied and matched to representatives',profilePhoto:'decoded locally',directoryPhotos:'decoded locally',stateMaps:states.length,boundaries:states.reduce((n,s)=>n+s[2],0),selection:'mouse and keyboard',zoomResetSearch:'passed',comparison:'connected',historicalBoundaries:'not misapplied',failedFetch:'results remain usable',widths:[320,393,768,1440],themes:['light','dark'],errors}));
}finally{await browser.close();}
