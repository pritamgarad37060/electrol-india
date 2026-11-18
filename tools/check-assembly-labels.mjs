import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';

const catalog=JSON.parse(await fs.readFile(path.join(root,'data/catalog.json'),'utf8'));
const browser=await launchBrowser({args:['--disable-background-networking']});
try{
 for(const width of [393,1440]){
  const page=await browser.newPage({viewport:{width,height:852}});
  await page.route('**/*',async route=>{
   const url=new URL(route.request().url());
   if(url.hostname!=='127.0.0.1')return route.abort();
   if(url.pathname.startsWith('/api/'))return route.fulfill({json:{configured:false,user:null}});
   if(/^\/(js|css|data|assets)\//.test(url.pathname))return route.fulfill({body:await fs.readFile(path.join(root,url.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[path.extname(url.pathname)]||'application/octet-stream'});
   return route.fulfill({contentType:'text/html',body:(await render(url.pathname)).html});
  });
  await page.goto('http://127.0.0.1/assembly-elections/');
  await page.evaluate(async()=>{await ElectrolBackend.ready;await ElectrolHTMLData.ready;await ElectrolNavigation.ready;});
  for(const entry of catalog){
   await page.evaluate(async id=>{await openElectionEdition(id)},entry.id);
   assert.equal(await page.locator('.full-election-header h1').innerText(),(entry.level==='lok'?'Lok Sabha':entry.state+' Assembly')+' '+entry.year);
   assert.equal(await page.title(),(entry.level==='lok'?'Lok Sabha':entry.state+' Assembly')+' '+entry.year+' • Electrol India');
   if(entry.level==='assembly'){
    assert((await page.locator('.full-election-header p').innerText()).startsWith(entry.state+' Legislative Assembly'));
    await page.locator('[data-edition-tab="analytics"]').first().click();
    assert((await page.locator('#full-dashboard-content').innerText()).includes('Within '+entry.state));
    await page.locator('[data-edition-tab="more"]').first().click();
    const jurisdiction=page.locator('.detail-row').filter({has:page.locator('span',{hasText:/^Jurisdiction$/})});
    assert.equal(await jurisdiction.locator('strong').innerText(),entry.state);
   }
  }
  console.log(`${width}px: labels passed for all ${catalog.length} election editions.`);
  await page.close();
 }
}finally{await browser.close();}
