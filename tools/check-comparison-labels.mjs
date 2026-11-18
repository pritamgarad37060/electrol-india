import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
await fs.mkdir('reports/comparison-labels',{recursive:true});
const browser=await launchBrowser(),page=await browser.newPage(),errors=[];
page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',async route=>{const u=new URL(route.request().url());if(u.hostname!=='127.0.0.1')return route.abort();try{
 if(u.pathname.startsWith('/api/'))return route.fulfill({json:{configured:false,user:null}});
 if(/^\/(js|css|data|assets)\//.test(u.pathname))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[path.extname(u.pathname)]||'application/octet-stream'});
 const r=await render(u.pathname);return route.fulfill({status:r.status,contentType:'text/html',body:r.html});
 }catch(e){return route.fulfill({status:500,body:e.message})}});
try{for(const width of [320,393,768,1024,1440]){
 await page.setViewportSize({width,height:900});await page.goto('http://127.0.0.1/');await page.waitForFunction(()=>window.ElectrolBackend&&window.ElectrolHTMLData);await page.evaluate(()=>ElectrolBackend.ready);
 for(const config of [
 {type:'assembly',mode:'year',a:'Maharashtra',b:'Maharashtra',ya:'2024',yb:'2019',wa:'all',wb:'all'},
 {type:'lok',mode:'year',a:'Maharashtra',b:'Maharashtra',ya:'2024',yb:'2019',wa:'all',wb:'all'},
 {type:'local',local:'corporation',mode:'location',a:'Pune',b:'Mumbai',sa:'Maharashtra',sb:'Maharashtra',da:'Pune',db:'Mumbai',ya:'2017',yb:'2017',wa:'all',wb:'all'}]){
 await page.evaluate(c=>loadConfig(c),config);await page.waitForFunction(()=>document.querySelector('#panel').getAttribute('aria-busy')==='false');
 if(width===393||width===1440)await page.screenshot({path:'reports/comparison-labels/'+config.type+'-'+width+'.png',fullPage:true});const metricValues=await page.locator('#panel .metric-values strong').allTextContents();assert(metricValues.every(v=>!/[0-9]\.[0-9]{3,}/.test(v)),'Turnout precision');const expected=await page.evaluate(()=>partyNames.slice());
 const axes=await page.locator('#panel svg.chart text').allTextContents();assert.deepEqual(axes.slice(-5),expected,'Chart axis must match party data');
 const actual=await page.evaluate(()=>({...current}));const labels=await page.locator('[id^=election-label-]').allTextContents();assert(labels[0].includes(actual.a)&&labels[0].includes(actual.ya));assert(labels[1].includes(actual.b)&&labels[1].includes(actual.yb));
 for(const selectedTab of ['overview','parties','map','seats','elections']){
 await page.evaluate(t=>setTab(t),selectedTab);await page.waitForFunction(()=>document.querySelector('#panel').getAttribute('aria-busy')==='false');
 const text=await page.locator('#panel').innerText();assert(!/Regional (?:party )?[AB]\b|Election [AB]\b|\bNaN\b|\bInfinity\b|sample results|illustrative/i.test(text),selectedTab+' has bad labels');
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2))console.log(await page.evaluate(()=>[...document.querySelectorAll('main *')].map(e=>({tag:e.tagName,cls:e.className,w:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).filter(e=>e.right>innerWidth+2).slice(0,12)));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'Overflow at '+width+' '+selectedTab);
 }
 await page.evaluate(()=>{openElectionMore('information')});const info=await page.locator('#election-more-body').innerText();assert(info.includes('Imported election records'));assert(!info.includes('2026'));await page.evaluate(()=>renderElectionMore(morePage='sources'));const sources=await page.locator('#election-more-body').innerText();assert(!/demonstration figures|state samples|sample years/i.test(sources));await page.evaluate(()=>document.querySelector('#election-more-panel').close());
 const csv=await page.evaluate(async()=>{const create=URL.createObjectURL;let result;const prevent=e=>{if(e.target.closest('a[download]'))e.preventDefault()};URL.createObjectURL=blob=>{result=blob;return create.call(URL,blob)};document.addEventListener('click',prevent,true);try{exportCSV();return await result.text()}finally{URL.createObjectURL=create;document.removeEventListener('click',prevent,true)}});assert(!/illustrative|\bNaN\b|Infinity|A seats|B seats/.test(csv));assert(csv.includes(actual.a)&&csv.includes(actual.ya));await page.evaluate(()=>setTab('history'));await page.waitForFunction(()=>document.querySelector('#panel').getAttribute('aria-busy')==='false');assert.equal(await page.locator('#panel svg [points*="NaN"]').count(),0);
 }
 console.log(JSON.stringify({width,partyAxes:'match imported parties',electionLabels:'selected name and year',tabs:5,overflow:false}));
}assert.deepEqual(errors,[]);}finally{await browser.close()}
