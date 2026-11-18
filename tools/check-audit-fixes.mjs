import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
const browser=await launchBrowser(),page=await browser.newPage({viewport:{width:393,height:852}}),errors=[];
page.on('pageerror',error=>errors.push(error.message));
await page.route('**/*',async route=>{
 const url=new URL(route.request().url());if(url.hostname!=='127.0.0.1')return route.abort();
 try{
  if(url.pathname.startsWith('/api/'))return route.fulfill({json:{configured:false,user:null}});
  if(/^\/(js|css|data|assets)\//.test(url.pathname))return route.fulfill({body:await fs.readFile(path.join(root,url.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[path.extname(url.pathname)]||'application/octet-stream'});
  const response=await render(url.pathname);return route.fulfill({status:response.status,contentType:'text/html',body:response.html});
 }catch(error){return route.fulfill({status:500,body:error.message});}
});
const ready=async()=>{await page.waitForFunction(()=>window.ElectrolBackend&&window.ElectrolProfiles);await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(()=>ElectrolProfiles.ready);};
const results=()=>page.waitForFunction(()=>document.getElementById('panel').getAttribute('aria-busy')==='false');
try{
 await page.goto('http://127.0.0.1/');await ready();
 await page.evaluate(()=>openAuth('login'));
 assert(!/demo|no emails sent/i.test(await page.locator('.auth-panel-foot').innerText()));
 await page.evaluate(()=>document.getElementById('auth-panel').close());

 await page.evaluate(()=>openMunicipalProfile('pune'));
 await page.evaluate(()=>municipalCompareForm());
 const pair=await page.locator('#mc-compare-form').evaluate(form=>[form.elements.a.value,form.elements.b.value]);
 assert(pair.every(Boolean));assert.notEqual(pair[0],pair[1]);
 await page.locator('#mc-compare-form select[name=b]').selectOption(pair[0]);
 assert(await page.locator('#mc-compare-form button[type=submit]').isDisabled());
 await page.evaluate(()=>document.getElementById('dialog').close());

 await page.evaluate(()=>{electionStream='live';coverageState='all';coverageLevel='all';openElectionCentre();});
 await page.locator('#coverage-query').fill('Gujarat');
 assert((await page.locator('#coverage-search-results').innerText()).includes('Gujarat Assembly 2022'));
 await page.locator('#coverage-query').fill('Baramati');
 assert((await page.locator('#coverage-search-results').innerText()).includes('Baramati'));

 await page.evaluate(()=>{measure='seats';loadConfig({type:'lok',mode:'location',a:'All India',b:'Maharashtra',ya:'2024',yb:'2024',wa:'all',wb:'all'});});await results();
 const records=await page.evaluate(()=>records().map(r=>({n:r.n,complete:r._voteAvailable,unopposed:r._unopposedCount})));
 assert.equal(records[0].n,543);assert.equal(records[0].complete,true);assert.equal(records[0].unopposed,1);
 await page.evaluate(()=>{measure='votes';setTab('parties')});await results();
 assert((await page.locator('#panel').innerText()).includes('All-party comparison'));
 await page.locator('#comparison-party-search').fill('AIMIM');await results();
 assert((await page.locator('#panel table').innerText()).includes('All India Majlis-E-Ittehadul Muslimeen'));
 assert(!(await page.locator('#panel table').innerText()).includes('Not available'));

 await page.evaluate(()=>openMunicipalProfile('ahilyanagar',false,2026));
 assert((await page.locator('#mc-detail-content .source-status').first().innerText()).includes('63 of 63'));
 assert((await page.locator('#mc-detail-content .source-status').first().innerText()).includes('partial'));

 await page.evaluate(()=>{openNavigation('profile');showProfilePage('language');});
 await page.locator('[name=content-language][value=mr]').check();
 await page.locator('#language-form button[type=submit]').click();
 await page.waitForFunction(()=>document.documentElement.lang==='mr');
 await page.waitForFunction(()=>document.querySelector('#language-form')?.innerText.includes('पसंतीची वाचन भाषा'));
 await page.reload();await ready();assert.equal(await page.locator('html').getAttribute('lang'),'mr');
 await page.evaluate(()=>{appDetails.contentLanguage='bn';persistDetails();return ElectrolProfiles.setLanguage('bn');});
 await page.reload();await ready();assert.equal(await page.locator('html').getAttribute('lang'),'bn');
 await page.evaluate(()=>{appDetails.contentLanguage='hi';persistDetails();return ElectrolProfiles.setLanguage('hi');});
 await page.evaluate(()=>{measure='seats';loadConfig({type:'assembly',mode:'year',a:'Maharashtra',b:'Maharashtra',ya:'2024',yb:'2019',wa:'all',wb:'all'});});await results();
 await page.waitForFunction(()=>document.getElementById('swap').getAttribute('aria-label')==='चुनाव चयन बदलें');
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true);
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({authWording:'passed',municipalComparison:'distinct selections enforced',catalogSearch:'national and local catalogs',uncontested:'national votes available',allParties:'searchable expanded names',localCoverage:'partial rosters identified',languages:'Hindi/Marathi labels; Marathi/Bengali reload; translated ARIA',errors}));
}catch(error){console.log(JSON.stringify({errors,languageForm:await page.locator('#language-form').innerText().catch(()=>''),panel:await page.locator('#panel').innerText().catch(()=>''),url:page.url()}));throw error;}finally{await browser.close();}
