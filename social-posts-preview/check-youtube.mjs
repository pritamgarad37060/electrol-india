import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {parseFeed} from './collect-youtube.mjs';
const html=await fs.readFile(new URL('electrol-social-posts.html',import.meta.url),'utf8');
const data=JSON.parse(await fs.readFile(new URL('youtube-data.json',import.meta.url),'utf8'));
assert.equal(data.people.length,100);assert.equal(new Set(data.people.map(p=>p.id)).size,100);
assert(data.videos.length>0);const byId=new Map(data.people.map(p=>[p.id,p]));
for(const v of data.videos){assert(/^[\w-]{11}$/.test(v.id));assert.equal(v.channelId,byId.get(v.personId).youtube.channelId);assert(Number.isFinite(Date.parse(v.publishedAt)));assert(v.title);}
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];new vm.Script(script);assert(!html.includes('/*__YOUTUBE__*/'));
const ch='UC1NF71EwP41VdjAU1iXdLkw',vid='a8zbxCMeG-M';
const fixture='<feed><yt:channelId>'+ch.slice(2)+'</yt:channelId><title>Fixture channel</title><entry><yt:videoId>'+vid+'</yt:videoId><yt:channelId>'+ch+'</yt:channelId><title>A &amp; B</title><published>2026-10-31T10:30:00Z</published><media:description>&lt;script&gt;fixture&lt;/script&gt;</media:description><media:statistics views="42"/></entry></feed>';
const parsed=parseFeed(fixture,ch,'fixture');assert.equal(parsed.videos[0].title,'A & B');assert.equal(parsed.videos[0].views,'42');assert.throws(()=>parseFeed(fixture,'UCxxxxxxxxxxxxxxxxxxxxxx','fixture'),/identity/);
const {launchBrowser}=await import('../tools/browser.mjs');
const browser=await launchBrowser({args:['--disable-background-networking','--disable-breakpad','--disable-crash-reporter','--disable-component-update','--disable-domain-reliability','--disable-sync','--no-first-run','--no-default-browser-check','--host-resolver-rules=MAP * ~NOTFOUND']});
const ctx=await browser.newContext({serviceWorkers:'block'});const page=await ctx.newPage();page.setDefaultTimeout(6000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
await ctx.route('**/*',async route=>{const u=new URL(route.request().url());if(u.origin==='http://127.0.0.1:8125'&&!u.pathname.startsWith('/api/'))return route.fulfill({contentType:'text/html',body:html});if(u.pathname==='/api/youtube/data')return route.fulfill({contentType:'application/json',body:JSON.stringify(data)});if(u.hostname==='www.youtube.com'&&u.pathname.startsWith('/embed/'))return route.fulfill({contentType:'text/html',body:'<!doctype html><p>Isolated player fixture</p>'});return route.abort();});
try{
 await page.goto('http://127.0.0.1:8125/');await page.waitForSelector('.yt-video');
 assert.equal(await page.locator('.yt-video').count(),12);
 for(const width of [320,393,768,1440])for(const theme of ['light','dark']){await page.setViewportSize({width,height:900});await page.evaluate(t=>window.ElectrolSocial.applyTheme(t),theme);const overflow=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,els:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,12).map(e=>({tag:e.tagName,cls:e.className,w:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right}))}));assert(overflow.scroll<=width,JSON.stringify(overflow));}
 await page.setViewportSize({width:393,height:850});
 const first=await page.locator('[data-yt-play]').first().getAttribute('data-yt-play');await page.locator('[data-yt-play]').first().click();assert((await page.locator('.yt-player iframe').first().getAttribute('src')).includes(first));
 await page.locator('[data-yt-save]').first().click();assert.equal(await page.locator('[data-yt-save]').first().getAttribute('aria-pressed'),'true');
 await page.locator('[data-action=saved]:visible').first().click();assert.equal(await page.locator('.yt-video').count(),1);
 await page.locator('[data-action=news]:visible').first().click();
 await page.locator('#yt-search').fill('NONEXISTENT-QUERY-924');await page.waitForTimeout(250);assert.equal(await page.locator('.yt-video').count(),0);await page.locator('#yt-search').fill('');await page.waitForTimeout(250);
 const matched=data.people.find(p=>p.youtube.channelId);await page.selectOption('#yt-person',matched.id);assert((await page.locator('.yt-video').count())>0);await page.locator('.yt-video [data-person]').first().click();assert(await page.locator('.hero h1').textContent());
 await page.locator('[data-yt-section=posts]').click();assert((await page.locator('#main').textContent()).includes('does not expose'));
 await page.locator('[data-yt-section=about]').first().click();assert((await page.locator('#main').textContent()).includes('About this YouTube channel'));
 await page.locator('[data-action=back]').click();await page.evaluate(()=>window.ElectrolSocial.go('people'));assert.equal(await page.locator('.person-card').count(),100);
 const unmatched=data.people.find(p=>!p.youtube.channelId);if(unmatched){await page.evaluate(id=>window.ElectrolSocial.openPerson(id),unmatched.id);assert((await page.locator('#main').textContent()).includes('Channel link needed'));}
 await page.evaluate(()=>{window.ElectrolSocial.go('news');window.ElectrolYouTube.selectPlatform('x');});assert((await page.locator('#main').textContent()).includes('X timelines'));
 await page.evaluate(()=>window.ElectrolYouTube.selectPlatform('youtube'));await page.locator('[data-yt-refresh]').click();await page.waitForTimeout(100);assert((await page.locator('.yt-video').count())>0);
 assert.deepEqual(errors,[]);console.log(JSON.stringify({profiles:100,matched:data.people.filter(p=>p.youtube.channelId).length,videos:data.videos.length,layouts:'320/393/768/1440 light and dark',playback:'iframe creation checked with fixture; live playback not verified',searchSaveFiltersProfiles:'passed',missingMappings:'explicit',xRetained:true,errors}));
}finally{await browser.close();}
