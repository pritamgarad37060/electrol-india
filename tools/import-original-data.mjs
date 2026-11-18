import fs from 'node:fs/promises';import path from 'node:path';import vm from 'node:vm';import {createHash} from 'node:crypto';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const original=path.resolve(process.argv[2]||path.join(root,'..'));
const read=async f=>JSON.parse(await fs.readFile(path.join(original,f),'utf8'));
const write=async(f,d)=>{const file=path.join(root,'data',f);await fs.mkdir(path.dirname(file),{recursive:true});await fs.writeFile(file,JSON.stringify(d));};
export const normalize=s=>String(s||'').toLowerCase().replace(/\b(shri|smt|shrimati|dr|adv|prof|mr|mrs)\b\.?/g,'').replace(/[^\p{L}\p{N}]/gu,'');
const context={window:{}};vm.runInNewContext(await fs.readFile(path.join(original,'js/data-ls-members.js'),'utf8'),context);
const members=context.window.LS_MEMBERS,profileIndex=[],people=await read('data/representatives-index.json');
const officeholders=await read('data/representative-officeholders.json');
for(const m of members){const file='public-profiles/'+m.id+'.json';await write(file,m);profileIndex.push({id:m.id,name:m.name,state:m.state,constituency:m.constituency,file:'/data/'+file});}
// Keep source record fields, including office sources and dated roles. Detailed biographies stay lazy-loaded.
const rows=people.rows.map(r=>({...r}));
for(const o of officeholders.rows){const matches=rows.filter(r=>normalize(r.name)===normalize(o.name)&&normalize(r.state)===normalize(o.state));for(const r of matches){r.office_records||=[];r.office_records.push(o);}if(!matches.length)rows.push({key:'office:'+createHash('sha256').update([o.name,o.state,o.role].join('|')).digest('hex').slice(0,20),name:o.name,state:o.state,party:o.party,kind:'officeholder',role:o.role,status:o.status,source:o.source,constituency:o.body||'',office_records:[o]});}
await write('people-directory.json',{reviewed_on:people.reviewed_on,coverage:people.coverage,vacancies:people.vacancies,rows});
await write('profile-index.json',profileIndex);
await fs.mkdir(path.join(root,'data/photos'),{recursive:true});
let photosCopied=0;for(const m of members){const source=path.join(original,'data/photos',String(m.id)+'.jpg');try{await fs.copyFile(source,path.join(root,'data/photos',String(m.id)+'.jpg'));photosCopied++;}catch(error){if(error.code!=='ENOENT')throw error;}}
await write('representative-officeholders.json',officeholders);
await write('representative-videos.json',await read('data/representative-videos.json'));
await write('assembly-buildings.json',await read('data/assembly-buildings.json'));
await write('election-notices.json',await read('data/elections/october_2026_byelection_summary.json'));
const partyIndex=[];for(const name of (await fs.readdir(path.join(original,'data/party-profiles'))).filter(n=>n.endsWith('.json'))){const p=await read('data/party-profiles/'+name);await write('party-profiles/'+name,p);partyIndex.push({code:p.code,short:p.short,name:p.name,id:p.id,file:'/data/party-profiles/'+name});}
await write('party-profile-index.json',partyIndex);
// Retain age and gender separately without changing the renderer's compact candidate tuple.
const catalog=JSON.parse(await fs.readFile(path.join(root,'data/catalog.json'),'utf8'));let enriched=0;
const originals=await fs.readdir(path.join(original,'data/elections'));
for(const e of catalog.filter(e=>e.level==='assembly')){const choices=originals.filter(f=>f.endsWith('_'+e.year+'.json'));let source;
 for(const name of choices){const d=await read('data/elections/'+name);const state=d.election?.state||d.state;if(state===e.state&&d.candidates_by_ac){source=d;break;}if(e.state==='Maharashtra'&&name==='maharashtra_assembly_'+e.year+'.json'&&d.candidates_by_ac)source=d;}
 if(!source)continue;const file=path.join(root,e.file),d=JSON.parse(await fs.readFile(file,'utf8'));
 for(const s of d.seats){const cs=source.candidates_by_ac[s.n]||[];s.candidateDetails=s.c.map(c=>{const same=cs.filter(x=>normalize(x.name)===normalize(c[0]));const x=same.length===1?same[0]:null;if(x){enriched++;return {age:x.age??null,gender:x.gender??null};}return null;});}
 await fs.writeFile(file,JSON.stringify(d));
}
console.log(JSON.stringify({biographies:members.length,photosCopied,people:rows.length,officeRecords:officeholders.rows.length,partyProfiles:partyIndex.length,candidatesEnriched:enriched}));

await import('./connect-profile-photos.mjs');

await (await import('./build-identities.mjs')).buildIdentities();
