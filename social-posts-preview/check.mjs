import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {last30Days,importAccount,requestX,XError} from './import-x.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const people=JSON.parse(await fs.readFile(path.join(here,'representatives.json'),'utf8'));
const html=await fs.readFile(path.join(here,'electrol-social-posts.html'),'utf8');
assert.equal(people.length,100);assert.equal(new Set(people.map(p=>p.id)).size,100);assert.equal(new Set(people.map(p=>p.handle.toLowerCase())).size,100);
assert(people.every(p=>/^[a-zA-Z0-9_]{1,15}$/.test(p.handle)));assert(people.some(p=>p.handle.toLowerCase()==='rahulgandhi'));
const embeds=JSON.parse(await fs.readFile(path.join(here,'embeds-five-days.json'),'utf8'));assert.equal(embeds.people.length,10);assert.equal(embeds.posts.length,10);assert.equal(new Set(embeds.posts.map(p=>p.personId)).size,10);
for(const p of embeds.posts){assert(p.createdAt>=embeds.range.start&&p.createdAt<embeds.range.end);assert.equal(p.createdAt,new Date(Number((BigInt(p.id)>>22n)+1288834974657n)).toISOString());const owner=people.find(r=>r.id===p.personId);assert(owner);assert.equal(new URL(p.url).pathname.toLowerCase(),('/'+owner.handle+'/status/'+p.id).toLowerCase());assert(p.source.startsWith('https://'));}
assert(!html.includes('/*__ROSTER__*/'));assert(!html.includes('Bearer '));assert(!html.includes('appt.pmo@'));assert(!html.includes('8975462014'));
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];new vm.Script(script);
const period=last30Days(new Date('2026-10-31T12:00:30Z'));assert.equal(period.start,'2026-10-01T12:00:00.000Z');assert.equal(period.end,'2026-10-31T12:00:00.000Z');
const person=people[0];let calls=[];
const row=(id,text='Fixture: importer test')=>({id,author_id:'123',text,created_at:'2026-10-30T13:00:00Z'});
const fake=async url=>{const u=new URL(url);calls.push(u);if(u.pathname.startsWith('/2/users/'))return {ok:true,json:async()=>({data:{id:'123',username:person.handle,protected:false}})};assert.equal(u.searchParams.get('query'),'from:'+person.handle);assert.equal(u.searchParams.get('start_time'),period.start);return {ok:true,json:async()=>u.searchParams.has('next_token')?{data:[row('101'),row('102')],meta:{result_count:2}}:{data:[row('101')],meta:{next_token:'page-two',result_count:1}}};};
const complete=await importAccount(person,{token:'fixture-only',period,fetcher:fake});assert.equal(complete.posts.length,2);assert.equal(complete.coverage.status,'complete');assert.equal(calls.length,3);assert(complete.posts.every(p=>p.personId===person.id&&p.url.endsWith('/'+p.id)));
const partial=await importAccount(person,{token:'fixture-only',period,fetcher:fake,maxPages:1});assert.equal(partial.coverage.status,'partial');
await assert.rejects(()=>requestX('https://example.org/',{token:'fixture-only',fetcher:fake}));
await assert.rejects(()=>importAccount(person,{token:'fixture-only',period,fetcher:async()=>({ok:false,status:401})}),e=>e instanceof XError&&e.status===401);
const badAuthor=async url=>new URL(url).pathname.startsWith('/2/users/')?{ok:true,json:async()=>({data:{id:'123',username:person.handle}})}:{ok:true,json:async()=>({data:[{...row('103'),author_id:'999'}],meta:{}})};
await assert.rejects(()=>importAccount(person,{token:'fixture-only',period,fetcher:badAuthor}),/does not match/);
console.log(JSON.stringify({representatives:100,distinctXAccounts:100,scriptSyntax:'passed',embeddedPortraits:people.filter(p=>p.photo).length,importerPaginationAndDeduplication:'passed',dateBoundaries:'passed',identityMismatchRejected:true,missingOrRejectedCredentials:'handled',noCredentialsInHTML:true}));
if(!process.argv.includes('--browser'))process.exit(0);
// Standalone Chromium with all DNS blocked, background networking disabled,
// no profile/extensions, and all browser requests fulfilled from local memory.
// This test never loads X, Sansad, Microsoft diagnostics or production services.
const {launchBrowser}=await import('../tools/browser.mjs');
const browser=await launchBrowser({args:['--disable-background-networking','--disable-breakpad','--disable-crash-reporter','--disable-component-update','--disable-domain-reliability','--disable-sync','--no-first-run','--no-default-browser-check','--host-resolver-rules=MAP * ~NOTFOUND']});
const context=await browser.newContext({serviceWorkers:'block'}),page=await context.newPage(),errors=[],blocked=[];
await context.route('**/*',async route=>{const u=new URL(route.request().url());if(u.origin==='http://127.0.0.1:8125')return route.fulfill({contentType:'text/html',body:html});blocked.push(u.origin);return route.abort();});
page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto('http://127.0.0.1:8125/');
 await page.waitForSelector('.x-post-embed .note-box');assert(blocked.includes('https://platform.twitter.com'),'Default feed should request post embeds automatically');
 assert.equal(await page.locator('.x-post-embed').count(),10);assert((await page.locator('#main').textContent()).includes('Selected posts'));
 for(const width of [320,393,768,1440])for(const theme of ['light','dark']){
  await page.setViewportSize({width,height:950});await page.evaluate(t=>ElectrolSocial.applyTheme(t),theme);
  for(const view of ['news','people','following','saved']){await page.evaluate(v=>ElectrolSocial.go(v),view);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,'Overflow: '+width+' '+theme+' '+view);}
  await page.evaluate(id=>ElectrolSocial.openPerson(id),person.id);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,'Profile overflow '+width);
 }
 await page.setViewportSize({width:393,height:852});await page.evaluate(()=>ElectrolSocial.go('people'));
 await page.locator('#search').fill('Narendra Modi');await page.waitForTimeout(250);assert.equal(await page.locator('.person-card').count(),1);
 await page.locator('.person-card').click();assert((await page.locator('.hero').textContent()).includes('Narendra Modi'));
 await page.locator('.hero [data-follow]').click();assert.equal(await page.locator('.hero [data-follow]').getAttribute('aria-pressed'),'true');
 await page.locator('[data-mode=timeline]').click();await page.waitForSelector('#timeline a');assert((await page.locator('#timeline a').first().getAttribute('href')).includes(person.handle));
 await page.locator('[data-tab=details]').click();assert((await page.locator('#main').textContent()).includes('Parliamentary biography'));
 await page.evaluate(()=>ElectrolSocial.go('news'));await page.locator('[data-action=filters]').click();assert(await page.locator('#filter-panel').isVisible());
 await page.locator('#region-filter').selectOption('Maharashtra');assert((await page.locator('#main').textContent()).includes('Maharashtra'));await page.locator('[data-action=clear]').click();
 const fixture={schema:1,fetchedAt:'2026-10-31T12:00:00.000Z',range:period,coverage:complete.coverage?[complete.coverage]:[],posts:[{...complete.posts[0],text:'<img src=x onerror="alert(1)"> Import fixture only'}]};
 await page.locator('.topbar [data-action=settings]').click();await page.locator('[data-action=import]').click();await page.locator('#load-file').setInputFiles({name:'posts.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(fixture))});
 await page.waitForSelector('article.post');assert.equal(await page.locator('article.post .post-body img').count(),0);assert((await page.locator('.post-body').textContent()).includes('<img'));
 await page.locator('[data-save]').click();await page.evaluate(()=>ElectrolSocial.go('saved'));assert.equal(await page.locator('article.post').count(),1);
 await page.evaluate(()=>ElectrolSocial.go('people'));await page.locator('#search').fill('not-a-real-name');await page.waitForTimeout(250);assert.equal(await page.locator('.person-card').count(),0);
 await page.evaluate(()=>{ElectrolSocial.go('news');ElectrolSocial.applyTheme('dark');});await page.reload();assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),'dark');
 await page.locator('[data-mode=timeline]').click();assert.equal(await page.locator('#timeline-person').count(),1);
 // Simulate only the official widget API response to verify automatic mounts and
 // account changes. This is a test fixture, never included as representative posts.
 await page.evaluate(()=>{window.twttr={widgets:{createTimeline:async(source,box)=>{const frame=document.createElement('iframe');frame.title='Test widget '+source.screenName;box.append(frame);return frame;},createTweet:async(id,box,options)=>{const frame=document.createElement('iframe');frame.title='Test post '+id+' '+options.theme;frame.style.width='550px';box.append(frame);return frame;}}};});
 await page.locator('#timeline-person').selectOption(people[1].id);await page.waitForSelector('#timeline iframe');assert((await page.locator('#timeline iframe').getAttribute('title')).includes(people[1].handle));
 await page.locator('[data-mode=embeds]').click();await page.waitForSelector('.x-post-embed iframe');assert((await page.locator('.x-post-embed iframe').first().getAttribute('title')).includes('dark'));assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,'Embedded post overflow');
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({browser:'passed',externalTraffic:'blocked',viewports:[320,393,768,1440],themes:['light','dark'],searchAndFilters:'passed',profilesAndFollows:'passed',archiveImportAndBookmarks:'passed',escapedPostText:'passed',XUnavailableFallback:'passed',errors}));
}finally{await browser.close();}
