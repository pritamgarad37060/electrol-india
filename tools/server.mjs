import './local-account-env.mjs';
import {publicDataHandler} from '../netlify/functions/public-data.mjs';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gzip,brotliCompress,constants as zlibConstants} from 'node:zlib';
import {promisify} from 'node:util';
const gzipAsync=promisify(gzip),brotliAsync=promisify(brotliCompress);
import {createHash} from 'node:crypto';
import {accountHandler} from '../netlify/functions/account.mjs';
import {render,loadCatalog,root,isPrivate} from './build.mjs';
import {publicFile} from './public-path.mjs';
const port=Number(process.env.PORT||8100);
const env={...process.env,SITE_URL:process.env.LOCAL_SITE_URL||`http://127.0.0.1:${port}`,ACCOUNT_ALLOW_LOCAL:'true'};
let api=accountHandler({env});await loadCatalog();
// Backend patches must not be mistaken for an already-running current server.
const runtimeSources=['index.html','js/backend-bridge.js','netlify/functions/account.mjs','netlify/lib/account-core.mjs','tools/server.mjs','tools/build.mjs'];
const identityHash=createHash('sha256').update(process.platform==='win32'?root.toLowerCase():root);
for(const file of runtimeSources)identityHash.update(await fs.readFile(path.join(root,file)));
const projectId=identityHash.digest('hex');
async function sameProjectAt(port,identity){
 try{const r=await fetch(`http://127.0.0.1:${port}/__electrol/health`,{signal:AbortSignal.timeout(1000),redirect:'error'});if(!r.ok)return false;const data=await r.json();return data.app==='electrol-india-com'&&data.project===identity;}catch{return false;}
}
export function listenWithRecovery(server,{port=8100,identity,onPort=()=>{},probe=sameProjectAt,log=console.log,maxAttempts=10}={}){
 return new Promise((resolve,reject)=>{
  if(!Number.isInteger(port)||port<1||port>65535){reject(Error('PORT must be an integer between 1 and 65535.'));return;}
  let candidate=port,attempts=0;
  const cleanup=()=>{server.off('error',failed);server.off('listening',ready);};
  function ready(){cleanup();log(`Electrol India.Com: http://127.0.0.1:${candidate}/`);resolve({port:candidate,reused:false});}
  async function failed(error){
   if(error.code!=='EADDRINUSE'){cleanup();reject(error);return;}
   let same=false;try{same=await probe(candidate,identity);}catch{}
   if(same){cleanup();log(`Electrol India.Com is already running: http://127.0.0.1:${candidate}/`);resolve({port:candidate,reused:true});return;}
   if(attempts>=maxAttempts||candidate>=65535){cleanup();reject(Error('No available local port was found. Close an unused preview or choose another PORT.'));return;}
   log(`Port ${candidate} is occupied by another preview. Trying ${candidate+1}.`);candidate++;attempt();
  }
  function attempt(){attempts++;try{onPort(candidate);server.listen(candidate,'127.0.0.1');}catch(error){cleanup();reject(error);}}
  server.on('error',failed);server.once('listening',ready);attempt();
 });
}
const mime={'.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.html':'text/html; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp','.ico':'image/x-icon','.xml':'application/xml','.txt':'text/plain','.pdf':'application/pdf'};
const server=http.createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,env.SITE_URL),pathname=decodeURIComponent(url.pathname);
  if(pathname==='/__electrol/health'){
   res.writeHead(200,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify({app:'electrol-india-com',project:projectId}));return;
  }
  if(pathname==='/api/public-data'){const response=await publicDataHandler(new Request(env.SITE_URL+req.url,{method:req.method,headers:req.headers}),{env});response.headers.forEach((v,k)=>res.setHeader(k,v));res.writeHead(response.status);res.end(Buffer.from(await response.arrayBuffer()));return;}
  if(pathname.startsWith('/api/account/')){
   let size=0,chunks=[];for await(const c of req){size+=c.length;if(size>15*1024*1024){res.writeHead(413);res.end();return;}chunks.push(c)}
   const response=await api(new Request(env.SITE_URL+req.url,{method:req.method,headers:req.headers,body:['GET','HEAD'].includes(req.method)?undefined:Buffer.concat(chunks)}));
   response.headers.forEach((v,k)=>{if(k!=='set-cookie')res.setHeader(k,v)});res.setHeader('Set-Cookie',response.headers.getSetCookie());res.writeHead(response.status);res.end(Buffer.from(await response.arrayBuffer()));return;
  }
  let body,type,status=200;
  if(['/robots.txt','/sitemap.xml'].includes(pathname)){body=await fs.readFile(path.join(root,'dist',pathname.slice(1)));type=mime[path.extname(pathname)];}
  else if(/^\/(js|css|data|assets)\//.test(pathname)||['/sw.js','/manifest.json'].includes(pathname)){
   const file=['/sw.js','/manifest.json'].includes(pathname)?path.join(root,pathname):publicFile(root,pathname);if(!file){res.writeHead(403);res.end();return;}
   body=await fs.readFile(file);type=mime[path.extname(file)]||'application/octet-stream';
  }else{const result=await render(pathname);body=result.html;status=result.status;type='text/html; charset=utf-8';}
  const headers={'Content-Type':type,'Cache-Control':'no-cache','X-Content-Type-Options':'nosniff','Referrer-Policy':'strict-origin-when-cross-origin'};
  if(isPrivate(pathname)){headers['Cache-Control']='private, no-store';headers['X-Robots-Tag']='noindex, nofollow';}
  if(req.headers['accept-encoding']?.includes('br')&&/javascript|json|text|svg|xml/.test(type)){body=await brotliAsync(body,{params:{[zlibConstants.BROTLI_PARAM_QUALITY]:4}});headers['Content-Encoding']='br';headers.Vary='Accept-Encoding';}
  else if(req.headers['accept-encoding']?.includes('gzip')&&/javascript|json|text|svg|xml/.test(type)){body=await gzipAsync(body);headers['Content-Encoding']='gzip';headers.Vary='Accept-Encoding';}
  res.writeHead(status,headers);res.end(req.method==='HEAD'?undefined:body);
 }catch(error){res.writeHead(error.code==='ENOENT'?404:500,{'Content-Type':'text/plain'});res.end(error.code==='ENOENT'?'Not found':'Unable to serve this request');console.error(error.message);}
});
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{await listenWithRecovery(server,{port,identity:projectId,onPort(selected){const origin=new URL(process.env.LOCAL_SITE_URL||'http://127.0.0.1');origin.port=String(selected);env.SITE_URL=origin.origin;api=accountHandler({env});}});}catch(error){console.error('Unable to start Electrol India.Com: '+error.message);process.exitCode=1;}
}
