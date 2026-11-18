import fs from 'node:fs/promises';
import path from 'node:path';
import {render,root} from './build.mjs';
import assert from 'node:assert/strict';
import {launchBrowser} from './browser.mjs';
const browser=await launchBrowser();
try {
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 page.on('pageerror',e=>console.log('PAGE ERROR',e.message));
 await page.route('**/*',async route=>{const u=new URL(route.request().url());try{if(u.pathname.startsWith('/api/'))return route.fulfill({json:{configured:false,user:null,follows:[],saved:[],preferences:{}}});if(['/js/','/css/','/data/','/assets/'].some(p=>u.pathname.startsWith(p)))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json'})[path.extname(u.pathname)]||'application/octet-stream'});const r=await render(u.pathname);return route.fulfill({body:r.html,contentType:'text/html'});}catch{return route.abort()}});
 await page.goto('http://127.0.0.1/',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.ElectrolDirectories);
 await page.evaluate(()=>ElectrolHTMLData.ready);
 await page.waitForTimeout(1500);
 const result=await page.evaluate(()=>{
  const names=['homeHTML','homeOptionHTML','homePersonalHTML','homeFollowsHTML','homeFinderHTML','homeQuickLinksHTML','constituencyRecords','followCatalog','selectedHomeSeat'];
  const timings={};
  for(const name of names){const fn=window[name];if(typeof fn!=='function')continue;window[name]=function(...args){const t=performance.now();try{return fn.apply(this,args)}finally{const x=timings[name]||={ms:0,calls:0};x.ms+=performance.now()-t;x.calls++}}}
  const runs=[];for(let i=0;i<3;i++){showPrimary('explore');const t=performance.now();showPrimary('home');runs.push(performance.now()-t)}
  return {runs,timings,resources:performance.getEntriesByType('resource').filter(x=>x.duration>500).map(x=>({url:x.name,ms:x.duration}))};
 });
 assert(result.runs.every(ms=>ms<500),'Home rendering exceeded 500ms: '+result.runs);
 assert.equal(result.timings.followCatalog.calls,3,'Home rebuilt the follow catalog per item');
 for(const width of [393,1440]){
  await page.setViewportSize({width,height:852});
  await page.evaluate(()=>showPrimary('explore'));
  const button=page.locator('[data-primary="home"]').filter({visible:true}).first();
  await button.click();
  await page.waitForSelector('.home-hero');
  assert.equal(await page.locator('.home-hero').count(),1);
  const selected=await page.evaluate(()=>{homePrefs.seat=constituencyRecords()[0].id;showPrimary('home');return !!selectedHomeSeat()&&!!document.querySelector('[data-home-seat]')});
  assert(selected,'Saved constituency was not restored');
  await page.evaluate(()=>{homePrefs.seat='';showPrimary('home')});
 }
 console.log(JSON.stringify({status:'passed',widths:[393,1440],...result},null,2));
}finally{await browser.close()}
