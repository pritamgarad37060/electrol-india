import fs from 'node:fs/promises';
const root=new URL('./',import.meta.url);
const people=JSON.parse(await fs.readFile(new URL('representatives.json',root),'utf8'));
const get=async(host,params)=>{const r=await fetch(host+'?'+new URLSearchParams(params),{signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error('Public directory HTTP '+r.status);return r.json();};
let old=[];try{old=JSON.parse(await fs.readFile(new URL('youtube-lookups.json',root),'utf8'));}catch{}
const norm=s=>s.toLowerCase().replace(/^(ms\.?|dr\.?)\s+/,'').replace(/[^a-z]/g,'');
for(let start=0;start<people.length;start+=50){
 try{
 const batch=people.slice(start,start+50);
 const wiki=await get('https://en.wikipedia.org/w/api.php',{action:'query',titles:batch.map(p=>p.name.replace(/^(Ms\.?|Dr\.?)\s+/,'')).join('|'),prop:'pageprops',redirects:'1',format:'json'});
 const pages=Object.values(wiki.query.pages).filter(x=>x.pageprops?.wikibase_item);
 const ids=pages.map(x=>x.pageprops.wikibase_item);
 const entities=await get('https://www.wikidata.org/w/api.php',{action:'wbgetentities',ids:ids.join('|'),props:'claims',format:'json'});
 for(const page of pages){const p=batch.find(p=>norm(p.name)===norm(page.title));if(!p)continue;const qid=page.pageprops.wikibase_item;const channelId=entities.entities[qid]?.claims?.P2397?.find(x=>x.mainsnak.datavalue)?.mainsnak.datavalue.value;
 if(channelId){old=old.filter(x=>x.id!==p.id);old.push({id:p.id,name:p.name,channelId,source:'https://www.wikidata.org/wiki/'+qid,status:'Directory claim'});}}
 await fs.writeFile(new URL('youtube-lookups.json',root),JSON.stringify(old));console.log('batch',start,'channels',old.filter(x=>x.channelId).length);
 }catch(e){console.log(e.message);}
}
