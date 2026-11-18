import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {fetchFeed} from './collect-youtube.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const people=JSON.parse(await fs.readFile(path.join(here,'representatives.json'),'utf8'));
const known={'ls-4589':{handle:'NarendraModi',channelId:'UC1NF71EwP41VdjAU1iXdLkw'},'ls-4074':{handle:'rahulgandhi',channelId:'UC1DtEMePmr4O6F2do6BVl7A'},'ls-5021':{handle:'AmitShah',channelId:'UCnC4JCEAMQetXkR_DVy2onA'}};
let old={people:[],videos:[]};try{old=JSON.parse(await fs.readFile(path.join(here,'youtube-data.json'),'utf8'));}catch{}
let lookups=[];try{lookups=JSON.parse(await fs.readFile(path.join(here,'youtube-lookups.json'),'utf8'));}catch{}
const normalize=s=>s.toLowerCase().replace(/[^a-z]/g,'');
const data={schema:1,fetchedAt:new Date().toISOString(),scope:'Recent public feeds only. Channel ownership requires review.',people:people.map(p=>({...p,youtube:old.people?.find(x=>x.id===p.id)?.youtube||{channelId:null,title:'Channel not connected',status:'Not checked'}})),videos:old.videos||[],failures:[]};
let cursor=0;let done=0;
const save=async()=>{data.fetchedAt=new Date().toISOString();await fs.writeFile(path.join(here,'youtube-data.json'),JSON.stringify(data));};
async function lookup(p){
 const k=known[p.id],record=lookups.find(x=>x.id===p.id&&x.channelId);
 if(k||record){const channelId=k?.channelId||record.channelId;const f=await fetchFeed(channelId,p.id);return {channelId,title:f.title,videos:f.videos,source:k?'https://www.youtube.com/@'+k.handle:record.source,identity:k?'Direct channel association; review ownership':'Wikidata channel association; review ownership'};}
 const handle=p.name.replace(/^(Ms\.?|Dr\.?)\s+/i,'').replace(/[^a-zA-Z0-9]/g,'');
 const source='https://www.youtube.com/@'+handle;
 const r=await fetch(source,{signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('No channel confirmed');const html=await r.text();
 const meta=html.slice(html.indexOf('"channelMetadataRenderer":'),html.indexOf('"channelMetadataRenderer":')+12000);
 let m;try{m={externalId:meta.match(/"externalId":"(UC[\w-]{22})"/)?.[1],title:JSON.parse(meta.match(/"title":("(?:[^"\\]|\\.)*")/)?.[1]||'null')};}catch{}
 if(!m?.externalId||!m?.title)throw Error('No channel metadata');
 const a=normalize(p.name.replace(/^(Ms\.?|Dr\.?)\s+/i,'')),b=normalize(m.title.replace(/official/ig,''));
 if(a!==b)throw Error('Channel title requires identity review');
 const f=await fetchFeed(m.externalId,p.id);return {channelId:m.externalId,title:f.title,videos:f.videos,source,identity:'Exact-name channel candidate; ownership not independently verified'};
}
async function worker(){while(cursor<data.people.length){const p=data.people[cursor++];if(p.youtube.channelId)continue;try{const ch=await lookup(p);p.youtube={...ch,videos:undefined,fetchedAt:new Date().toISOString(),status:'Available feed'};data.videos=data.videos.filter(v=>v.personId!==p.id).concat(ch.videos);}catch(e){p.youtube={channelId:null,title:'Channel not connected',status:'Needs channel link',note:e.message};data.failures.push({personId:p.id,error:e.message});}done++;await save();}}
await save();await Promise.all(Array.from({length:5},worker));await save();console.log(JSON.stringify({politicians:data.people.length,connected:data.people.filter(p=>p.youtube.channelId).length,videos:data.videos.length,checked:done}));
