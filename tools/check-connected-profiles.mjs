import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {render,root} from './build.mjs';
import {launchBrowser} from './browser.mjs';
const read=async file=>JSON.parse(await fs.readFile(path.join(root,file),'utf8'));
const index=await read('data/local-catalog.json'),directory=await read('data/party-directory.json');
assert.equal(new Set(index.map(b=>b.id)).size,index.length);
assert.equal(new Set(directory.parties.map(p=>p.id)).size,directory.parties.length);
for(const b of index){const raw=await read(b.file);assert.equal(raw.id,b.id);for(const y of b.years){const s=raw.snapshots[y];assert(s);assert.equal(s.year,y);assert(Array.isArray(s.rows));assert(s.seats>=s.rows.length||s.rows.length===0,'Roster exceeds seats '+b.id+' '+y);}}
assert(index.filter(b=>b.kind==='council'&&b.years.includes(2025)).length>200);
assert.equal(index.filter(b=>b.kind==='corporation').length,30);
const browser=await launchBrowser();
const page=await browser.newPage({viewport:{width:393,height:852}}),errors=[];
page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',async route=>{const url=new URL(route.request().url());if(url.hostname!=='127.0.0.1')return route.abort();try{if(url.pathname.startsWith('/api/'))return route.fulfill({contentType:'application/json',body:JSON.stringify({configured:false,user:null})});if(/^\/(js|css|data|assets)\//.test(url.pathname))return route.fulfill({body:await fs.readFile(path.join(root,url.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[path.extname(url.pathname)]||'application/octet-stream'});const response=await render(url.pathname);return route.fulfill({status:response.status,contentType:'text/html',body:response.html});}catch(e){return route.fulfill({status:500,body:e.message});}});
try{
 const index=await read('data/profile-index.json'),people=await read('data/people-directory.json');
 assert.equal(index.length,JSON.parse(await fs.readFile(path.join(root,'reports/parliament-profile-import.json'),'utf8')).lok_sabha);assert.equal(new Set(people.rows.map(r=>r.key)).size,people.rows.length);
 assert(people.rows.some(r=>r.office_records?.length));
 await page.goto('http://127.0.0.1/');await page.evaluate(()=>ElectrolBackend.ready);
 const member=people.rows.find(r=>Number(r.mpid)===5126);assert(member);
 await page.evaluate(id=>openRepresentative('imported-person:'+id),member.key);await page.waitForSelector('.rep-hero h1');assert.equal(await page.evaluate(()=>publicPerson(representativeId).description),'Idukki · Kerala');
 await page.evaluate(()=>{representativeTab='personal';renderRepresentative()});assert((await page.locator('.rep-panel').allTextContents()).join(' ').includes('B.Sc.'));
 await page.evaluate(()=>{representativeTab='positions';renderRepresentative()});assert((await page.locator('.rep-panel').allTextContents()).join(' ').includes('18th Lok Sabha'));
 for(const width of [320,393,768,1440]){await page.setViewportSize({width,height:852});const size=await page.locator('.representative-page').evaluate(n=>({width:n.clientWidth,scroll:n.scrollWidth}));assert(size.scroll<=size.width+1,'Profile content overflow at '+width);}
 await page.goto('http://127.0.0.1/representatives/profile/?id='+encodeURIComponent(member.key));await page.evaluate(()=>ElectrolBackend.ready);await page.waitForSelector('.rep-hero h1');assert.equal(await page.evaluate(()=>publicPerson(representativeId).description),'Idukki · Kerala');assert((await page.locator('.rep-hero h1').textContent()).includes('Dean'));
 const supriya=people.rows.find(r=>Number(r.mpid)===4392);assert(supriya);await page.evaluate(id=>openRepresentative('imported-person:'+id),supriya.key);await page.evaluate(()=>{representativeTab='more';renderRepresentative()});assert(await page.locator('[data-profile-video]').count()>0);
 await page.evaluate(()=>ElectrolProfiles.setLanguage('mr'));assert.equal(await page.locator('html').getAttribute('lang'),'mr');await page.evaluate(()=>ElectrolProfiles.setLanguage('en'));assert.equal(await page.locator('html').getAttribute('lang'),'en');
 assert.deepEqual(errors,[]);console.log(JSON.stringify({biographies:index.length,people:people.rows.length,uniqueIds:true,personalDetails:'passed',positions:'passed',videos:'passed',directProfileURL:'passed',languageSwitch:'passed',profileWidths:[320,393,768,1440],errors}));
}finally{await browser.close();}
