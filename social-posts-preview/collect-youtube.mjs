import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
export const decode=s=>String(s||'').replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g,'$1').replace(/&#(\d+);/g,(_,n)=>String.fromCodePoint(+n)).replace(/&quot;/g,'"').replace(/&apos;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
const tag=(s,t)=>decode(s.match(new RegExp('<'+t+'(?:\\s[^>]*)?>([\\s\\S]*?)</'+t+'>'))?.[1]||'');
export function parseFeed(xml,channelId,personId){
 if(!xml.includes('<feed'))throw Error('YouTube did not return a video feed');
 const feedId=tag(xml,'yt:channelId');if(feedId!==channelId&&'UC'+feedId!==channelId)throw Error('Channel identity mismatch');
 const title=tag(xml.split('<entry>')[0],'title');
 const videos=[...xml.matchAll(/<entry>([\s\S]*?)<\/entry>/g)].map(m=>{const s=m[1],id=tag(s,'yt:videoId');return {id,personId,channelId,title:tag(s,'title'),description:tag(s,'media:description'),publishedAt:tag(s,'published'),updatedAt:tag(s,'updated'),channelTitle:title,thumbnail:'https://i.ytimg.com/vi/'+id+'/hqdefault.jpg',url:'https://www.youtube.com/watch?v='+id,views:s.match(/<media:statistics[^>]*views="(\d+)"/)?.[1]??null,likes:s.match(/<media:starRating[^>]*count="(\d+)"/)?.[1]??null,source:'YouTube public feed'};}).filter(v=>/^[\w-]{11}$/.test(v.id));
 return {title,videos};
}
export async function fetchFeed(channelId,personId,fetcher=fetch){
 if(!/^UC[\w-]{22}$/.test(channelId))throw Error('Invalid channel ID');
 const r=await fetcher('https://www.youtube.com/feeds/videos.xml?channel_id='+channelId,{signal:AbortSignal.timeout(20000)});if(!r.ok)throw Error('YouTube feed HTTP '+r.status);return parseFeed(await r.text(),channelId,personId);
}
async function collect(){
 const query=`SELECT DISTINCT ?person ?personLabel ?personDescription ?channel WHERE { ?person wdt:P31 wd:Q5; wdt:P27 wd:Q668; wdt:P2397 ?channel; wdt:P106/wdt:P279* wd:Q82955. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 250`;
 let rows;
 try{const r=await fetch('https://query.wikidata.org/sparql?format=json&query='+encodeURIComponent(query),{headers:{'User-Agent':'ElectrolIndia-Prototype/1.0'},signal:AbortSignal.timeout(55000)});if(!r.ok)throw Error('Directory HTTP '+r.status);const j=await r.json();rows=j.results.bindings;await fs.writeFile(path.join(here,'youtube-directory-source.json'),JSON.stringify(j,null,2));}
 catch(e){console.log('Directory unavailable: '+e.message);throw e;}
 const existing=JSON.parse(await fs.readFile(path.join(here,'representatives.json'),'utf8'));
 const normalize=s=>s.toLowerCase().replace(/^(ms\.?|dr\.?|shri|smt\.?)\s+/,'').replace(/[^a-z]/g,'');
 const result=[],seen=new Set();
 for(const row of rows){const channelId=row.channel.value;if(!/^UC[\w-]{22}$/.test(channelId)||seen.has(channelId))continue;seen.add(channelId);const qid=row.person.value.split('/').pop(),name=row.personLabel.value;const old=existing.find(p=>normalize(p.name)===normalize(name));result.push({...old,id:old?.id||'wd-'+qid,name,handle:old?.handle||'',state:old?.state||'',party:old?.party||'',house:old?.house||'',seat:old?.seat||'',role:old?.role||row.personDescription?.value||'Indian political figure',details:old?.details||{},photo:old?.photo||'',source:old?.source||'https://www.wikidata.org/wiki/'+qid,youtube:{channelId,source:'https://www.wikidata.org/wiki/'+qid,identity:'Directory match; ownership not independently verified'}});}
 // Prioritize familiar representatives already in the Electrol directory.
 result.sort((a,b)=>(existing.findIndex(p=>p.id===a.id)<0?999:existing.findIndex(p=>p.id===a.id))-(existing.findIndex(p=>p.id===b.id)<0?999:existing.findIndex(p=>p.id===b.id)));
 const channels=[],videos=[],failures=[];let cursor=0;
 async function worker(){while(cursor<result.length&&channels.length<100){const p=result[cursor++];try{const f=await fetchFeed(p.youtube.channelId,p.id);if(channels.length>=100)break;channels.push({...p,youtube:{...p.youtube,title:f.title,fetchedAt:new Date().toISOString()}});videos.push(...f.videos);console.log(channels.length+' '+p.name+' / '+f.videos.length+' videos');}catch(e){failures.push({name:p.name,channelId:p.youtube.channelId,error:e.message});}}}
 await Promise.all(Array.from({length:4},worker));
 const data={schema:1,fetchedAt:new Date().toISOString(),source:'YouTube public Atom feeds; channel mappings from Wikidata P2397',scope:'Recent feed entries, not a complete archive. Directory associations require ownership review.',people:channels,videos,failures};
 await fs.writeFile(path.join(here,'youtube-data.json'),JSON.stringify(data));
 console.log(JSON.stringify({channels:channels.length,videos:videos.length,failed:failures.length}));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await collect();
