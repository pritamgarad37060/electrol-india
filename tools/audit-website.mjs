import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
const routeMode=process.argv.includes('--routes');
const urls=routeMode?['/news/','/constituencies/','/local-elections/','/legislative-council/','/explore/','/lok-sabha/','/past-elections/','/sources/','/parties/dmk/','/municipal-corporations/pune/','/account','/auth/login','/parties/invalid-party/']:['/','/elections/','/municipal-corporations/','/municipal-councils/','/zilla-parishad-elections/','/panchayat-samitis/','/representatives/','/parties/','/constituencies/','/analysis/','/news/','/maharashtra/assembly/2024/213-hadapsar/'];
const browser=await launchBrowser();
const page=await browser.newPage(),errors=[],failures=[],results=[];
page.on('pageerror',e=>errors.push({url:page.url(),message:e.message}));
await page.route('**/*',async route=>{const u=new URL(route.request().url());if(u.hostname!=='127.0.0.1')return route.abort();try{
 if(u.pathname.startsWith('/api/'))return route.fulfill({json:{configured:false,user:null}});
 if(/^\/(js|css|data|assets)\//.test(u.pathname))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.jpg':'image/jpeg','.png':'image/png'})[path.extname(u.pathname)]||'application/octet-stream'});
 const r=await render(u.pathname);return route.fulfill({status:r.status,contentType:'text/html',body:r.html});
 }catch(e){failures.push({path:u.pathname,message:e.message});return route.fulfill({status:500,body:''});}});
await fs.mkdir('reports/website-audit',{recursive:true});
try{
for(const width of routeMode?[393,1440]:[320,393,768,1024,1440])for(const theme of routeMode?['light']:['light','dark']){
 await page.setViewportSize({width,height:900});
 for(const url of urls){
 await page.goto('http://127.0.0.1'+url);await page.waitForFunction(()=>window.ElectrolBackend?.ready);await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(t=>applyAppearance(t),theme);await page.waitForTimeout(120);
 const state=await page.evaluate(()=>({dialogs:[...document.querySelectorAll('dialog[open]')].map(e=>e.id),authForm:!!document.querySelector('#auth-form'),scroll:document.documentElement.scrollWidth,destination:typeof siteDestination==='undefined'?null:siteDestination,heading:[...document.querySelectorAll('h1,h2')].filter(e=>e.getClientRects().length).slice(0,4).map(e=>e.textContent.trim()),overflow:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.right>innerWidth+2&&getComputedStyle(e).position!=='fixed'&&!e.closest('svg,.table-wrap,[hidden]')}).slice(0,8).map(e=>({tag:e.tagName,cls:typeof e.className==='string'?e.className:'svg',right:Math.round(e.getBoundingClientRect().right)}))}));
 if(routeMode&&url.startsWith('/auth/'))assert(state.authForm,'Auth form not restored');if(routeMode&&url.startsWith('/account'))assert(state.dialogs.includes('navigation-panel'),'Profile panel not restored');results.push({url,width,theme,...state});
 if([393,1440].includes(width)&&['/','/elections/','/municipal-corporations/','/parties/','/maharashtra/assembly/2024/213-hadapsar/'].includes(url))await page.screenshot({path:`reports/website-audit/${url==='/'?'home':url.split('/').filter(Boolean).at(-1)}-${width}-${theme}.png`});
 }
 console.log('Reviewed',width,theme);
}
await fs.writeFile('reports/website-audit/'+(routeMode?'routes-recheck':'layout')+'.json',JSON.stringify({results,errors,failures},null,2));
assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);assert.equal(results.filter(r=>r.scroll>r.width+2).length,0,'Page-level overflow');
console.log(JSON.stringify({pages:results.length,errors,failures,overflow:results.filter(r=>r.scroll>r.width+2)}));
}finally{await browser.close();}
