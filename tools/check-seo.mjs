import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {render,publicPages} from './build.mjs';
for(const p of [...Object.keys(publicPages),'/account','/auth/login','/parties/dmk/','/municipal-corporations/pune/','/maharashtra/assembly/2024/213-hadapsar/','/en/elections/']){
 const r=await render(p);assert.equal(r.status,200,p);assert.equal((r.html.match(/name="description"/g)||[]).length,1,p);assert.match(r.html,/property="og:description"/);assert.match(r.html,/name="twitter:card"/);JSON.parse(r.html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);if(/^\/(account|auth)/.test(p))assert.match(r.html,/noindex, nofollow/);
}
for(const p of ['/parties/not-a-party/','/elections/not-an-edition/','/municipal-corporations/not-a-city/','/does-not-exist/'])assert.equal((await render(p)).status,404,p);
const canonical=(await render('/municipal-corporations/pune/')).html.match(/rel="canonical" href="([^"]+)"/)[1];assert(!canonical.includes('/pune/'));
console.log('Passed page metadata, structured JSON, canonical aliases, localized entry, private roots and unknown-route statuses.');
if(process.argv.includes('--sitemap')){const xml=await fs.readFile('dist/sitemap.xml','utf8'),urls=[...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1]);assert.equal(new Set(urls).size,urls.length);assert(!urls.some(u=>/\/(account|auth|admin|search|representatives\/profile)(\/|$)/.test(new URL(u).pathname)));for(const url of urls)await fs.access(path.toNamespacedPath(path.resolve('dist','.'+decodeURIComponent(new URL(url).pathname)+'index.html')));console.log('Passed sitemap uniqueness, public-only coverage and '+urls.length+' existing page targets.');}

