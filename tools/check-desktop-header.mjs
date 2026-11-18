import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {launchBrowser} from './browser.mjs';
import {render,root} from './build.mjs';
const browser=await launchBrowser();
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',async route=>{const u=new URL(route.request().url());
  if(u.pathname.startsWith('/api/account/'))return route.fulfill({json:{configured:true,user:null,csrf:'fixture-csrf',rows:[],preferences:{},google:false}});
  if(['/js/','/css/','/data/','/assets/'].some(p=>u.pathname.startsWith(p)))return route.fulfill({body:await fs.readFile(path.join(root,u.pathname)),contentType:({'.js':'text/javascript','.css':'text/css','.json':'application/json'})[path.extname(u.pathname)]||'application/octet-stream'});
  const r=await render(u.pathname);return route.fulfill({contentType:'text/html',body:r.html});
 });
 await page.goto('http://127.0.0.1/');await page.evaluate(()=>ElectrolBackend.ready);await page.evaluate(()=>ElectrolHTMLData.ready);
 await fs.mkdir('reports/desktop-header',{recursive:true});
 for(const width of [801,1024,1280,1440,1920]){
  await page.setViewportSize({width,height:1000});
  for(const appearance of ['light','dark']){
   await page.locator('.topbar [data-appearance='+appearance+']').click();
   assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),appearance);
   const geometry=await page.evaluate(()=>{
    const controls=[...document.querySelectorAll('.topbar .desktop-utility-group button,.topbar .desktop-theme-picker,.topbar .desktop-account-group button')].map(n=>{const r=n.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,top:r.top,bottom:r.bottom}});
    return {controls,overflow:document.documentElement.scrollWidth>innerWidth+1};
   });
   assert(!geometry.overflow,'Desktop overflow at '+width);
   geometry.controls.forEach((r,i)=>{assert(r.left>=0&&r.right<=width+1&&r.width>=32,'Clipped control at '+width);if(i)assert(r.left>=geometry.controls[i-1].right-1,'Overlapping controls at '+width)});
   if(width===1440)await page.screenshot({path:'reports/desktop-header/header-'+appearance+'.png',animations:'disabled'});
  }
 }
 await page.setViewportSize({width:1440,height:1000});
 await page.locator('[data-desktop-account=profile]').click();
 assert.equal(await page.locator('#navigation-title').textContent(),'Profile');
 assert.equal(await page.locator('#navigation-body .menu-tabs').count(),0);
 assert(await page.locator('#navigation-body').textContent().then(t=>t.includes('My activity')));
 await page.evaluate(()=>closeNavigation());
 await page.locator('[data-desktop-account=settings]').click();
 assert.equal(await page.locator('#navigation-title').textContent(),'Account settings');
 assert(await page.locator('#navigation-body').textContent().then(t=>t.includes('Display & region')));
 await page.screenshot({path:'reports/desktop-header/settings.png',animations:'disabled'});
 await page.evaluate(()=>closeNavigation());
 await page.locator('.topbar [data-appearance=system]').click();
 await page.emulateMedia({colorScheme:'dark'});await page.waitForFunction(()=>document.documentElement.dataset.theme==='dark');assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),'dark');
 await page.emulateMedia({colorScheme:'light'});await page.waitForFunction(()=>document.documentElement.dataset.theme==='light');assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),'light');
 await page.reload();await page.evaluate(()=>ElectrolBackend.ready);assert.equal(await page.evaluate(()=>document.documentElement.dataset.appearance),'system');
 for(const width of [393,768,800]){
  await page.setViewportSize({width,height:852});assert(!await page.locator('.topbar').isVisible());
  assert(await page.locator('.mobile-header').isVisible());assert(await page.locator('.bottom-nav [data-open-panel=profile]').isVisible());
 }
 await page.locator('.bottom-nav [data-open-panel=profile]').click();
 assert.equal(await page.locator('#navigation-body .menu-tabs button').count(),2,'Mobile profile tabs changed');
 assert(await page.locator('#navigation-body .menu-tabs').textContent().then(t=>t.includes('Activity')&&t.includes('Settings')));
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({desktopWidths:[801,1024,1280,1440,1920],appearance:['light','dark','system'],profileSettings:'separate working controls',mobile:'unchanged',errors}));
}finally{await browser.close()}
