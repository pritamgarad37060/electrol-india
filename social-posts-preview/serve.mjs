import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),port=Number(process.env.SOCIAL_PREVIEW_PORT||8125);
const routes=new Map([['/','electrol-social-posts.html'],['/electrol-social-posts.html','electrol-social-posts.html']]);
const server=http.createServer(async(req,res)=>{const u=new URL(req.url,'http://127.0.0.1');if(!['GET','HEAD'].includes(req.method)||!routes.has(u.pathname)){res.writeHead(404);res.end('Not found');return;}try{const data=await fs.readFile(path.join(here,routes.get(u.pathname)));res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(req.method==='HEAD'?undefined:data);}catch{res.writeHead(500);res.end('Build the preview first.');}});
server.listen(port,'127.0.0.1',()=>console.log('Electrol social preview: http://127.0.0.1:'+port+'/'));
