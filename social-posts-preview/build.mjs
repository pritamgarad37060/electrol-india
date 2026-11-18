import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
export const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(here);
function handleOf(value){
 const raw=String(value||'').trim();
 if(/^@?[a-zA-Z0-9_]{1,15}$/.test(raw))return raw.replace(/^@/,'');
 try{const u=new URL(raw);if(!/^(www\.)?(twitter|x)\.com$/i.test(u.hostname))return '';const h=u.pathname.split('/').filter(Boolean).map(s=>s.replace(/^@/,''));return h.length===1&&/^[a-zA-Z0-9_]{1,15}$/.test(h[0])?h[0]:'';}catch{return '';}
}
export async function roster(){
 try{await fs.access(path.join(root,'data/profile-index.json'));}catch{return JSON.parse(await fs.readFile(path.join(here,'representatives.json'),'utf8'));}
 const entries=JSON.parse(await fs.readFile(path.join(root,'data/profile-index.json'),'utf8'));
 const rs=JSON.parse(await fs.readFile(path.join(root,'data/rajya-sabha-index.json'),'utf8'));
 const candidates=[];const used=new Set();
 for(const e of [...entries,...rs.profiles]){
  const p=JSON.parse(await fs.readFile(path.join(root,e.file.replace(/^\//,'')),'utf8'));
  if(p.house==='Lok Sabha'&&p.status!=='Sitting')continue;
  const handle=handleOf(p.social?.twitter||p.social?.x);if(!handle||used.has(handle.toLowerCase()))continue;used.add(handle.toLowerCase());
  const name=p.name.replace(/^(Shri|Smt\.?|Shrimati|Dr\.?)\s+/i,'');
  let photo='';if(p.local_photo){try{photo='data:image/jpeg;base64,'+(await fs.readFile(path.join(root,p.local_photo.replace(/^\//,'')))).toString('base64');}catch{}}
  const id=p.member_key||((p.house==='Rajya Sabha'?'rs-':'ls-')+(p.rsid||p.id));
  candidates.push({id,name,handle,state:p.state||'',party:p.party||'',partyCode:p.party_code||'',house:p.house||'Lok Sabha',seat:p.constituency||p.matched_pc||p.state||'',source:p.source_profile||p.source_biography||'https://sansad.in/rs/members',photo,role:p.id===4589?'Prime Minister · Lok Sabha MP':p.house==='Rajya Sabha'?'Rajya Sabha MP':'Lok Sabha MP',details:{Education:p.education||p.qualification||'',Profession:p.profession||'',Interests:p.interests||'',Books:p.books||''},accountSource:p.source_profile||p.source_biography,reviewed:p.reviewed_on||'2026-10-30'});
 }
 const preferred=['narendramodi','rahulgandhi','amitshah','rajnathsingh','nitin_gadkari','drsjaishankar','nsitharaman','ombirlakota','supriya_sule','shashitharoor','yadavakhilesh','asadowaisi','mahuamoitra','iyc','priyankagandhi'];
 const selected=[];const ids=new Set();const add=p=>{if(p&&!ids.has(p.id)&&selected.length<100){selected.push(p);ids.add(p.id);}};
 for(const h of preferred)add(candidates.find(p=>p.handle.toLowerCase()===h));
 // Round-robin across recorded States and Houses, rather than taking 100 alphabetically.
 const groups=new Map();for(const p of candidates){const key=p.house+'|'+p.state;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p);}
 while(selected.length<100){let progress=false;for(const group of groups.values()){const p=group.shift();if(p){add(p);progress=true;}}if(!progress)break;}
 if(selected.length!==100)throw Error('100 distinct recorded X accounts are required.');
 return selected;
}
export async function build(){
 let people=process.argv.includes('--reuse-roster')?JSON.parse(await fs.readFile(path.join(here,'representatives.json'),'utf8')):await roster();
 let embeds={posts:[],people:[]};
 try{embeds=JSON.parse(await fs.readFile(path.join(here,'embeds-five-days.json'),'utf8'));}catch{}
 if(embeds.people?.length){const ids=new Set(embeds.people.map(p=>p.id));people=[...embeds.people,...people.filter(p=>!ids.has(p.id))].slice(0,100);}
 await fs.writeFile(path.join(here,'representatives.json'),JSON.stringify(people));
 let data={schema:1,fetchedAt:null,range:null,posts:[],coverage:[],note:'X archive not imported'};
 try{data=JSON.parse(await fs.readFile(path.join(here,'posts.json'),'utf8'));}catch{}
 let template=await fs.readFile(path.join(here,'template.html'),'utf8');
 let youtube={people:[],videos:[],fetchedAt:new Date().toISOString()};
 try{youtube=JSON.parse(await fs.readFile(path.join(here,'youtube-data.json'),'utf8'));}catch{}
 const youtubeUI=await fs.readFile(path.join(here,'youtube-ui.js'),'utf8');
 const youtubeCSS=await fs.readFile(path.join(here,'youtube.css'),'utf8');
 template=template.replace('function news(){','function baseNews(){').replace('function profile(){','function baseProfile(){').replace('function directory(){','function baseDirectory(){').replace('function settings(){','function baseSettings(){').replace('function coverage(){','function baseCoverage(){');
 template=template.replace('function go(view){','function baseGo(view){').replace('function openPerson(id){','function baseOpenPerson(id){').replace('function back(){','function baseBack(){');
 template=template.replace('</style>',youtubeCSS+'\n</style>');
 template=template.replace("applyTheme(['light','dark','system'].includes(theme)?theme:'system');readRoute();",youtubeUI+"\napplyTheme(['light','dark','system'].includes(theme)?theme:'system');readRoute();");
 const serial=x=>JSON.stringify(x).replace(/</g,'\\u003c');
 await fs.writeFile(path.join(here,'electrol-social-posts.html'),template.replace('/*__ROSTER__*/[]',()=>serial(people)).replace('/*__POSTS__*/{}',()=>serial(data)).replace('/*__EMBEDS__*/{}',()=>serial(embeds)).replace('/*__YOUTUBE__*/{}',()=>serial(youtube)));
 console.log(JSON.stringify({representatives:people.length,distinctAccounts:new Set(people.map(p=>p.handle.toLowerCase())).size,houses:[...new Set(people.map(p=>p.house))],posts:data.posts?.length||0,selectedEmbeds:embeds.posts?.length||0,file:'electrol-social-posts.html'}));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await build();
