import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
const browser=await launchBrowser(),page=await browser.newPage({viewport:{width:393,height:852}}),errors=[];
page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',async route=>{const u=new URL(route.request().url());if(u.hostname!=='127.0.0.1')return route.abort();try{if(u.pathname.startsWith('/api/'))return route.fulfill({contentType:'application/json',body:JSON.stringify({configured:false,user:null})});if(/^\/(js|css|data|assets)\//.test(u.pathname))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.svg':'image/svg+xml'})[path.extname(u.pathname)]||'application/octet-stream'});const r=await render(u.pathname);return route.fulfill({status:r.status,contentType:'text/html',body:r.html});}catch{return route.fulfill({status:404,body:''});}});
try{
 await page.goto('http://127.0.0.1/');await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(()=>ElectrolDirectories.loadPeople());
 for(const id of ['imported-person:mp-4589','leader:modi']){
  await page.evaluate(id=>openRepresentative(id),id);
  assert.equal(await page.evaluate(()=>publicPerson(representativeId).modi),true);
  assert.equal(await page.locator('.rep-socials a').count(),5);
  const urls=await page.locator('.rep-socials a').evaluateAll(a=>a.map(x=>x.href));
  for(const account of ['x.com/narendramodi','facebook.com/narendramodi','instagram.com/narendramodi','youtube.com/narendramodi','narendramodi.in'])assert(urls.some(url=>url.includes(account)),account);
  await page.evaluate(()=>{representativeTab='elections';renderRepresentative()});
  const elections=await page.locator('#representative-content').textContent();
  for(const year of ['2024','2019','2014','2012','2007','2002'])assert(elections.includes(year),'Missing Modi election '+year);
  await page.evaluate(()=>{representativeTab='personal';renderRepresentative()});
  let content=await page.locator('#representative-content').textContent();
  for(const label of ['Political information','Official & social links','Books','Parliamentary biography','Social activities'])assert(content.includes(label),label);
  await page.evaluate(()=>{representativeTab='positions';renderRepresentative()});
  assert(await page.locator('[data-rep-position-view="portfolio"]').count());
  content=await page.locator('#representative-content').textContent();assert(content.includes('Atomic Energy'));assert(content.includes('Parliamentary position history'));
  await page.evaluate(()=>{representativeTab='more';renderRepresentative()});
  assert(await page.locator('[data-rep-more="constituency"]').count());assert((await page.locator('#representative-content').textContent()).includes('Public contact details'));
  const extra=page.locator('[data-profile-extra]').filter({hasText:'Books & publications'});assert.equal(await extra.count(),1);
  assert.equal(await extra.locator('.rep-facts').isVisible(),false);await extra.locator('summary').click();assert.equal(await extra.locator('.rep-facts').isVisible(),true);
  const modiBio=JSON.parse(await fs.readFile(path.join(root,'data/public-profiles/4589.json'),'utf8'));assert.equal(await extra.locator('.rep-facts strong').textContent(),modiBio.books);
  for(const width of [393,1440]){await page.setViewportSize({width,height:852});const size=await page.evaluate(()=>({w:innerWidth,s:document.documentElement.scrollWidth}));assert(size.s<=size.w+1,'More details overflow '+width);}
  await extra.locator('summary').press('Enter');assert.equal(await extra.locator('.rep-facts').isVisible(),false);await page.setViewportSize({width:393,height:852});

 }
 await page.evaluate(()=>openRepresentative('imported-person:mp-5126'));
 const expected=JSON.parse(await fs.readFile(path.join(root,'data/public-profiles/5126.json'),'utf8')).social;
 for(const [field,label] of [['facebook','Facebook'],['twitter','X'],['instagram','Instagram']])if(expected[field])assert.equal(await page.locator('.rep-socials a[aria-label="'+label+'"]').getAttribute('href'),new URL(expected[field]).href);
 assert(!await page.locator('.rep-socials a').evaluateAll(a=>a.some(x=>x.href.includes('narendramodi'))));
 await page.evaluate(()=>{representativeTab='elections';renderRepresentative()});assert((await page.locator('#representative-content').textContent()).includes('Recorded election and membership history'));
 await page.evaluate(()=>Promise.all([openRepresentative('imported-person:mp-4589'),openRepresentative('imported-person:mp-5126')]));
 assert.equal(await page.evaluate(()=>publicPerson(representativeId)._import.mpid),5126);
 assert(!await page.locator('.rep-socials a').evaluateAll(a=>a.some(x=>x.href.includes('narendramodi'))));
 for(const width of [393,1440]){await page.setViewportSize({width,height:852});const size=await page.locator('.representative-page').evaluate(n=>({width:n.clientWidth,scroll:n.scrollWidth}));assert(size.scroll<=size.width+1);}
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({modiCanonicalAndLegacyProfiles:'passed',modiSocialLinks:5,modiElectionYears:[2024,2019,2014,2012,2007,2002],personalAndPoliticalSections:'passed',positionsAndPortfolios:'passed',moreMenuAndContacts:'passed',otherMPSocialLinks:'matched source',otherMPElectionHistory:'passed',rapidProfileSwitch:'passed',mobileAndDesktop:'passed',errors}));
}finally{await browser.close();}
