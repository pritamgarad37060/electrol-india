import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
// Extract, without rewriting, the supplied HTML's styles and inline scripts.
// This keeps its DOM/renderers intact while avoiding a multi-megabyte copy on
// every generated SEO page. index.html remains the authoritative frontend.
export async function prepareHTML(){
 const input=await fs.readFile(path.join(root,'index.html'),'utf8');
 const scripts=[],styles=[];let serial=0;
 let html=input.replace(/<style\b([^>]*)>([\s\S]*?)<\/style>/gi,(_tag,attributes,code)=>{
  const hash=createHash('sha256').update(code).digest('hex').slice(0,12),file=`html-design.${hash}.css`;styles.push({file,code});return `<link rel="stylesheet" href="/css/${file}">`;
 }).replace(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi,(tag,attributes,code)=>{
  if(/\bsrc\s*=|application\/ld\+json|application\/json/i.test(attributes))return tag.replace(/src="js\//g,'src="/js/');
  const hash=createHash('sha256').update(code).digest('hex').slice(0,12),file=`html-${serial++}.${hash}.js`;scripts.push({file,code});return `<script${attributes} src="/js/${file}"></script>`;
 });
 html=html.replace(/<title>[\s\S]*?<\/title>/i,'<title><!--TITLE--></title>').replace(/<meta\s+name="description"[^>]*>/i,'<!--SEO-->');
 html=html.replace('</body>','<!--SSR--></body>');
 await fs.mkdir(path.join(root,'src'),{recursive:true});
 for(const {file,code} of scripts)await fs.writeFile(path.join(root,'js',file),code);
 for(const {file,code} of styles)await fs.writeFile(path.join(root,'css',file),code);
 await fs.writeFile(path.join(root,'src/shell.html'),html);
 return {html,scripts:scripts.map(s=>s.file),styles:styles.map(s=>s.file)};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){const {scripts,styles}=await prepareHTML();console.log(JSON.stringify({scripts,styles}));}
