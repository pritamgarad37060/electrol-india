import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
const read=async f=>JSON.parse(await fs.readFile(path.join(root,f),'utf8'));
const index=await read('data/rajya-sabha-index.json');
let oaths=0,recordings=0,dates=0;
for(const entry of index.profiles){
 const m=await read(entry.file),a=await read(m.activity_file);
 assert.equal(a.rsid,m.rsid);assert.equal(m.rsid,entry.rsid);
 assert.equal(a.recordings.total,a.recordings.records.length);
 assert.equal(new Set(a.recordings.records.map(v=>v.url)).size,a.recordings.total);
 assert(a.recordings.records.every(v=>v.member_id===m.rsid));
 for(const [kind,s] of Object.entries(a.sections)){if(s.status==='available'){assert.equal(s.total,s.records.length);for(const r of s.records){const id=r.mp_code??r.mpCode??r.t_mp_code;if(id!=null&&Number(id)!==m.rsid){assert.equal(kind,'questions');assert.equal(r.member_association,'clubbed-question');assert(/^\s*\(clubbed\)/i.test(r.qtitle));assert.equal(r.profile_member_id,m.rsid);}}}}
 assert((m.oath_recordings||[]).every(v=>/oath|affirmation/i.test(v.title+' '+v.category)));
 if(m.oath_date){assert(/^\d{4}-\d{2}-\d{2}$/.test(m.oath_date));dates++;}
 oaths+=m.oath_recordings.length;recordings+=a.recordings.total;
}
const browser=await launchBrowser(),page=await browser.newPage({viewport:{width:393,height:852}}),errors=[],activityRequests=[];
page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',async route=>{const u=new URL(route.request().url());if(u.hostname!=='127.0.0.1')return route.abort();try{if(u.pathname.startsWith('/api/'))return route.fulfill({contentType:'application/json',body:JSON.stringify({configured:false,user:null})});if(u.pathname.includes('/rajya-sabha-activity/'))activityRequests.push(u.pathname);if(/^\/(js|css|data|assets)\//.test(u.pathname))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.svg':'image/svg+xml'})[path.extname(u.pathname)]||'application/octet-stream'});const r=await render(u.pathname);return route.fulfill({status:r.status,contentType:'text/html',body:r.html});}catch{return route.fulfill({status:404,body:''});}});
try{
 await page.goto('http://127.0.0.1/representatives/profile/?id=rs-1929');await page.evaluate(()=>ElectrolBackend.ready);await page.waitForSelector('.rep-hero');await page.evaluate(async()=>{await ElectrolProfiles.biography(publicPerson(representativeId));renderRepresentative()});
 assert.equal(activityRequests.length,0,'Directory and biography must not load the activity archive');
 await page.locator('[data-rs-profile-tab=recordings]').click();await page.waitForFunction(()=>document.querySelector('#representative-content video'));
 const profile=await read('data/public-profiles/rs/1929.json');let text=await page.locator('#representative-content').textContent();assert(text.includes(profile.oath_date));
 assert.equal(await page.locator('video:not([preload="none"])').count(),0);
 const videoURLs=await page.locator('video').evaluateAll(nodes=>nodes.map(n=>n.src));assert.equal(new Set(videoURLs).size,videoURLs.length,'Oath clips must not appear twice');
 await page.locator('[data-rs-profile-tab=parliament]').click();await page.waitForSelector('[data-rs-kind=questions]');
 const a=await read(profile.activity_file);assert.equal(await page.locator('#representative-content article').count(),Math.min(20,a.sections.questions.total));
 if(a.sections.questions.total>20){await page.locator('[data-rs-next]').click();assert.equal(await page.locator('#representative-content article').count(),Math.min(40,a.sections.questions.total));}
 await page.locator('[data-rs-search] input').fill('Tourist infrastructure');await page.locator('[data-rs-search] button').click();assert((await page.locator('#representative-content').textContent()).includes('Tourist infrastructure'));
 await page.locator('[data-rs-kind=committees]').click();assert((await page.locator('#representative-content').textContent()).includes('Labour'));
 await page.locator('[data-rs-kind=attendance_sessions]').click();text=await page.locator('#representative-content').textContent();assert(text.includes('not attendance totals'));assert(!text.includes('0%'));
 await page.locator('[data-rs-kind=debates]').click();assert((await page.locator('#representative-content').textContent()).includes('does not mean zero activity'));
 for(const width of [393,1440]){await page.setViewportSize({width,height:900});for(const tab of ['parliament','recordings']){await page.locator('[data-rs-profile-tab='+tab+']').click();const sizes=await page.evaluate(()=>({w:innerWidth,s:document.documentElement.scrollWidth}));assert(sizes.s<=sizes.w+1,'Overflow '+width+' '+tab);}}
 await page.evaluate(()=>Promise.all([openRepresentative('imported-person:rs-1929'),openRepresentative('imported-person:rs-2288')]));assert.equal(await page.evaluate(()=>publicPerson(representativeId)._import.rsid),2288);
 await page.locator('[data-rs-profile-tab=recordings]').click();const other=await read('data/public-profiles/rs/2288.json');await page.waitForFunction(()=>!document.querySelector('#representative-content [role=status]'));if(other.oath_date)assert((await page.locator('#representative-content').textContent()).includes(other.oath_date));
 const noDate=await Promise.all(index.profiles.map(e=>read(e.file))).then(rows=>rows.find(m=>!m.oath_date));if(noDate){await page.evaluate(id=>openRepresentative('imported-person:rs-'+id),noDate.rsid);await page.locator('[data-rs-profile-tab=recordings]').click();assert((await page.locator('#representative-content').textContent()).includes('not published in this biography'));}
 assert.deepEqual(errors,[]);
 await fs.mkdir(path.join(root,'tmp/rs-enrichment-check'),{recursive:true});await page.screenshot({path:path.join(root,'tmp/rs-enrichment-check/profile.png'),fullPage:true});
 console.log(JSON.stringify({members:index.profiles.length,recordings,oathRecordings:oaths,publishedOathDates:dates,memberIdentity:'passed',lazyLoading:'passed',paginationAndSearch:'passed',missingData:'passed',profileSwitching:'passed',mobileAndDesktop:'passed',errors}));
}finally{await browser.close();}
