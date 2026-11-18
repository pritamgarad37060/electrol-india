import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import zlib from 'node:zlib';
import {promisify} from 'node:util';
import {prepareHTML} from './prepare-html.mjs';

const gzip = promisify(zlib.gzip);
const brotliCompress = promisify(zlib.brotliCompress);
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let catalog,shell;const data=new Map(),routes=new Map();
const directoryRoutes=new Map();
export const publicPages={'/':'Electrol India - Indian Election Results','/sources/':'Sources and Data Coverage','/elections/':'Indian Elections','/lok-sabha/':'Lok Sabha Elections','/explore/':'Explore Elections','/past-elections/':'Past Elections','/representatives/profile/':'Representative Profile','/assembly-elections/':'Assembly Elections','/municipal-corporations/':'Municipal Corporation Elections','/municipal-councils/':'Municipal Council Elections','/panchayat-samitis/':'Panchayat Samiti Elections','/local-elections/':'Local Elections','/panchayat-elections/':'Nagar Panchayat Elections','/zilla-parishad-elections/':'Zilla Parishad Elections','/representatives/':'Representatives','/parties/':'Political Parties','/constituencies/':'Constituencies','/analysis/':'Election Analysis','/compare/':'Compare Elections','/news/':'Election News','/legislative-council/':'Legislative Council'};
export const isPrivate=p=>/^\/(account|auth|admin|search|following|notifications|corrections)(\/|$)/.test(p);

const origin=()=>process.env.SITE_URL?.replace(/\/$/,'')||'https://electrolindia.netlify.app';
export async function loadCatalog(){
 if(catalog)return catalog;
 catalog=JSON.parse(await fs.readFile(path.join(root,'data/catalog.json'),'utf8'));shell=(await prepareHTML()).html;
 const context=JSON.parse(await fs.readFile(path.join(root,'data/result-context.json'),'utf8'));
 for(const d of catalog){const value=JSON.parse(await fs.readFile(path.join(root,d.file),'utf8'));for(const s of value.seats){const extra=context[(d.level==='assembly'?'Assembly':'Lok Sabha')+':'+d.year+':'+d.state+':'+s.n];if(extra){s.context=extra;for(const k of ['ballots','electors','turnout','rejected','tendered'])if(extra[k]!=null)s[k]=extra[k];}}data.set(d.id,value);routes.set(d.url,{edition:d});for(const s of value.seats){routes.set(s.url,{edition:d,seat:s});for(const alias of s.aliases||[])routes.set(alias,{edition:d,seat:s});if(d.level==='lok')routes.set(s.url.replace(/\/\d+-([^/]+)\/$/,'/$1/'),{edition:d,seat:s});}}
 const parties=JSON.parse(await fs.readFile(path.join(root,'data/party-directory.json'),'utf8'));
 for(const p of parties.parties)directoryRoutes.set('/parties/'+p.id.replace('party:','')+'/',{title:p.name+' - Election Performance',description:'Explore '+p.name+' results across imported elections. Coverage and available editions vary.',content:'<h1>'+esc(p.name)+'</h1><p>Imported election performance by year and region.</p><ul>'+p.editions.map(e=>'<li>'+esc(e.state)+' '+esc(e.year)+': '+fmt(e.seats)+' seats</li>').join('')+'</ul>'});
 const local=JSON.parse(await fs.readFile(path.join(root,'data/local-catalog.json'),'utf8'));
 for(const b of local){const section=({corporation:'municipal-corporations',council:'municipal-councils',nagar:'panchayat-elections',zp:'zilla-parishad-elections',samiti:'panchayat-samitis'})[b.kind];if(section)directoryRoutes.set('/'+section+'/'+b.slug+'/',{title:b.name+' - '+publicPages['/'+section+'/'],description:b.name+', '+b.state+'. Available election years: '+b.years.join(', ')+'. Candidate coverage may be partial.',content:'<h1>'+esc(b.name)+'</h1><p>'+esc(b.state)+'; available election years: '+esc(b.years.join(', '))+'. Detailed candidate coverage may be partial.</p>'});}
 for(const b of local){const section=({corporation:'municipal-corporations',council:'municipal-councils',nagar:'panchayat-elections',zp:'zilla-parishad-elections',samiti:'panchayat-samitis'})[b.kind];const canonical='/'+section+'/'+b.slug+'/';const entry=directoryRoutes.get(canonical);if(entry){entry.url=canonical;if(b.uiId&&/^[a-z0-9-]+$/i.test(b.uiId)&&b.uiId!==b.slug)directoryRoutes.set('/'+section+'/'+b.uiId+'/',entry);}}
 return catalog;
}
const fmt=n=>n==null?'Not available':Number(n).toLocaleString('en-IN');
function seatHTML(d,s){const people=s.c.filter(c=>d.parties[c[1]].short!=='NOTA'),total=s.rosterComplete?s.c.reduce((n,c)=>n+(c[2]||0),0):null;return `<article class="card"><h1>${esc(s.t)} ${d.level==='lok'?'Lok Sabha':'Assembly'} ${d.year}</h1><p>${esc(s.state)} · ${s.status==='unopposed'?'Elected unopposed; no poll held':s.rosterComplete?'Imported candidate results':'Partial candidate coverage'}</p><table><caption>Candidate standings</caption><thead><tr><th>Candidate</th><th>Party</th><th>Votes</th><th>Share</th></tr></thead><tbody>${s.c.map(c=>`<tr><td>${esc(c[0])}</td><td>${esc(d.parties[c[1]].short)}</td><td>${fmt(c[2])}</td><td>${total?((c[2]||0)/total*100).toFixed(2)+'%':'Not available'}</td></tr>`).join('')}</tbody></table><p>${people.length} imported candidates, excluding NOTA. ${s.rosterComplete?'Vote share denominator: candidate votes plus NOTA.':'Complete roster is not available.'}</p><p><a href="${esc(d.source||'https://www.eci.gov.in/statistical-reports')}">Election source</a></p></article>`;}
export async function render(pathname){
 pathname=pathname==='/'?'/':pathname.replace(/\/+$/,'')+'/';
 const localized=pathname.match(/^\/(en|hi|mr|bn|te|ta|gu|ur|kn|ml)(\/.*)$/),language=localized?.[1]||'en';if(localized)pathname=localized[2];
 await loadCatalog();const route=routes.get(pathname);let title='Electrol India — Election Results',content='',status=200;
 if(route){const d=data.get(route.edition.id);title=route.seat?`${route.seat.t} ${d.level==='lok'?'Lok Sabha':'Assembly'} Election Results ${d.year}`:`${d.state} ${d.level==='lok'?'Lok Sabha':'Assembly'} Election Results ${d.year}`;content=route.seat?seatHTML(d,route.seat):`<section class="card"><h1>${esc(title)}</h1><p>${esc(route.edition.coverage)}</p><ul>${d.seats.map(s=>`<li><a href="${s.url}">${esc(s.t)} — ${esc(s.c[0]?.[0])}</a></li>`).join('')}</ul></section>`;}
 else if(pathname==='/'){content=`<section class="card"><h1>Electrol India</h1><p>Explore Indian election records.</p><nav>${Object.entries(publicPages).filter(([p])=>p!=='/'&&p!=='/representatives/profile/').map(([p,t])=>'<a href="'+esc(p)+'">'+esc(t)+'</a> ').join('')}</nav><ul>${catalog.map(d=>`<li><a href="${d.url}">${esc(d.state)} ${d.level==='lok'?'Lok Sabha':'Assembly'} ${d.year}</a></li>`).join('')}</ul></section>`;}
 else if(directoryRoutes.has(pathname)){const d=directoryRoutes.get(pathname);title=d.title;content='<section class="card">'+d.content+'</section>';}
 else if(!publicPages[pathname]&&!isPrivate(pathname)){status=404;title='Page not found — Electrol India';content='<section class="card"><h1>Page not found</h1><a href="/">Return home</a></section>';}
 else {title=(publicPages[pathname]||pathname.split('/').filter(Boolean)[0].replaceAll('-',' '))+' - Electrol India';content='<section class="card"><h1>'+esc(title)+'</h1><p>Enable JavaScript to use the interactive tools.</p><a href="/">Election catalog</a></section>';}
 if(publicPages[pathname]&&pathname!=='/'&&!isPrivate(pathname)){const entries=[...new Map([...directoryRoutes.values()].filter(d=>d.url?.startsWith(pathname)).map(d=>[d.url,d])).values()];if(entries.length)content='<section class="card"><h1>'+esc(title)+'</h1><ul>'+entries.map(d=>'<li><a href="'+esc(d.url)+'">'+esc(d.title)+'</a></li>').join('')+'</ul></section>';}
 const privatePage=isPrivate(pathname)||pathname==='/representatives/profile/',url=origin()+(route?.seat?.url||route?.edition?.url||directoryRoutes.get(pathname)?.url||pathname);
 const description=directoryRoutes.get(pathname)?.description||(route?.seat?title+'. Candidate votes, party standings and source coverage. '+(route.seat.rosterComplete?'Imported candidate roster available.':'Candidate roster is partial.'):(title+'. Explore imported Indian election records, candidate results and source coverage.'));
 const graph=[{'@type':'WebSite','@id':origin()+'/#website',name:'Electrol India',url:origin()+'/'},{'@type':'WebPage',name:title,description,url,isPartOf:{'@id':origin()+'/#website'}}];
 if(route)graph.push({'@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:'Home',item:origin()+'/'},{'@type':'ListItem',position:2,name:route.edition.state+' '+route.edition.year,item:origin()+route.edition.url},...(route.seat?[{'@type':'ListItem',position:3,name:route.seat.t,item:url}]:[])]});
 const seo=`<meta name="description" content="${esc(description)}"><link rel="canonical" href="${esc(url)}"><meta name="robots" content="${privatePage||status===404?'noindex, nofollow':'index, follow, max-image-preview:large'}"><meta property="og:site_name" content="Electrol India"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:url" content="${esc(url)}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="${esc(title)}"><meta name="twitter:description" content="${esc(description)}"><script type="application/ld+json">${JSON.stringify({'@context':'https://schema.org','@graph':graph}).replaceAll('<','\\u003c')}</script>`;

 let html=shell.replace('<!--TITLE-->',esc(title)).replace('<!--SEO-->',seo).replace('<!--SSR-->','<noscript>'+content+'</noscript>');
 html=html.replace('<html lang="en">',`<html lang="${language}" dir="${language==='ur'?'rtl':'ltr'}">`);
 if(route?.seat)html=html.replace('</head>',`<script id="route-context" type="application/json">${JSON.stringify({edition:route.edition.id,seat:route.seat.n,state:route.seat.state}).replaceAll('<','\\u003c')}</script></head>`);
 else if(route)html=html.replace('</head>',`<script id="route-context" type="application/json">${JSON.stringify({edition:route.edition.id})}</script></head>`);
 if(status===404)html=html.replace('</body>',`<script>window.addEventListener('load',async()=>{await window.ElectrolBackend?.ready;pageShell('not-found');document.getElementById('destination-view').innerHTML='<section class="card"><h1>Page not found</h1><p>This address does not match an available page.</p><a class="primary" href="/">Return home</a></section>';document.title='Page not found - Electrol India';});</script></body>`);
 return {html,status,title};
}
export async function build(){
 await loadCatalog();const out=path.join(root,'dist');await fs.mkdir(out,{recursive:true});
 const publicRoutes=['/municipal-councils/','/panchayat-samitis/','/corrections/','/legislative-council/','/local-elections/','/panchayat-elections/','/zilla-parishad-elections/','/','/elections/','/assembly-elections/','/municipal-corporations/','/representatives/','/parties/','/news/','/analysis/','/constituencies/','/search/','/account/','/account/follows/','/account/security/','/account/settings/','/account/sessions/','/account/preferences/','/account/notifications/','/account/delete/','/auth/login/','/auth/signup/','/auth/callback/','/auth/verify/','/auth/reset-password/','/auth/forgot-password/'];
 const pages=[...new Set([...Object.keys(publicPages),...publicRoutes,...directoryRoutes.keys(),...routes.keys()])];
 for(let i=0;i<pages.length;i+=16){
  const batch=pages.slice(i,i+16).map(pathname=>({pathname,target:path.join(out,pathname,'index.html')}));
  for(const {target} of batch)await fs.mkdir(path.dirname(target),{recursive:true});
  await Promise.all(batch.map(async({pathname,target})=>{
   const html=(await render(pathname)).html;
   const previous=await fs.readFile(target,'utf8').catch(error=>{if(error.code==='ENOENT')return null;throw error;});
   if(previous!==html)await fs.writeFile(target,html);
  }));
 }
 await fs.writeFile(path.join(out,'404.html'),(await render('/not-a-real-page/')).html);
 for(const dir of ['js','css','data','assets'])await fs.cp(path.join(root,dir),path.join(out,dir),{recursive:true});
 for(const p of ['sw.js','manifest.json'])await fs.copyFile(path.join(root,p),path.join(out,p));
 await fs.writeFile(path.join(out,'robots.txt'),`User-agent: *\nDisallow: /api/\nSitemap: ${origin()}/sitemap.xml\n`);
 await fs.writeFile(path.join(out,'sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+[...new Set([...Object.keys(publicPages).filter(p=>p!=='/representatives/profile/'),...[...directoryRoutes].map(([pathname,entry])=>entry.url||pathname),...catalog.map(d=>d.url),...[...routes.values()].filter(r=>r.seat).map(r=>r.seat.url)])].map(p=>`<url><loc>${esc(origin()+p)}</loc></url>`).join('')+'</urlset>');
 if(process.env.ENABLE_PRECOMPRESS==='true'){
  await precompressStaticAssets(out);
  console.log(`Built ${pages.length} routes from ${catalog.length} election editions with Brotli and Gzip pre-compression.`);
 }else{
  console.log(`Built ${pages.length} routes from ${catalog.length} election editions (pre-compression skipped, dynamic edge compression enabled).`);
 }
}
async function compressFile(filePath){
 const ext=path.extname(filePath).toLowerCase();
 if(!['.html','.js','.css','.json','.svg','.xml','.txt'].includes(ext))return;
 try{
  const stat=await fs.stat(filePath);
  if(stat.size<1024)return;
  const brStat=await fs.stat(filePath+'.br').catch(()=>null);
  if(brStat&&brStat.mtimeMs>=stat.mtimeMs)return;
  const content=await fs.readFile(filePath);
  const [gz,br]=await Promise.all([
   gzip(content,{level:9}),
   brotliCompress(content,{params:{[zlib.constants.BROTLI_PARAM_QUALITY]:9}})
  ]);
  await Promise.all([
   fs.writeFile(filePath+'.gz',gz),
   fs.writeFile(filePath+'.br',br)
  ]);
 }catch{}
}
async function collectFiles(dir,files=[]){
 const entries=await fs.readdir(dir,{withFileTypes:true});
 for(const entry of entries){
  const fullPath=path.join(dir,entry.name);
  if(entry.isDirectory()){
   await collectFiles(fullPath,files);
  }else if(entry.isFile()&&!entry.name.endsWith('.gz')&&!entry.name.endsWith('.br')){
   files.push(fullPath);
  }
 }
 return files;
}
async function precompressStaticAssets(outDir){
 const files=await collectFiles(outDir);
 const eligible=files.filter(f=>['.html','.js','.css','.json','.svg','.xml','.txt'].includes(path.extname(f).toLowerCase()));
 for(let i=0;i<eligible.length;i+=32){
  await Promise.all(eligible.slice(i,i+32).map(compressFile));
 }
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await build();
