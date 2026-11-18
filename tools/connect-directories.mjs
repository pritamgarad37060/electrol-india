import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=file=>fs.readFile(path.join(root,file),'utf8');
const write=(file,data)=>fs.writeFile(path.join(root,file),JSON.stringify(data));
const context={window:{}};
for(const name of ['data-mh-local-bodies','data-delhi-mcd'])vm.runInNewContext(await read('js/'+name+'.js'),context);
const sources=JSON.parse(await read('data/mc_data.json'));
const rural=JSON.parse(await read('data/civic-rural.json'));
const bodies=[];
const note='Existing project import. Available candidates may be partial; this election snapshot does not establish current office.';
function snapshot(body,year,rows,tally){return {year:Number(year),seats:body['seat_count_'+year]??body.seat_count??rows.length,wards:body['ward_count_'+year]??body.ward_count??new Set(rows.map(r=>r.ward)).size,party_tally:tally||{},rows:rows.map(r=>({...r,seat:String(r.seat||''),area:r.area||r.ward_name||'',name:r.candidate||r.name,cands:r.cands?.length?r.cands:[[r.candidate||r.name,r.party,r.votes??null]],complete:r.rosterComplete===true})),president:body.president||null,coverage:body.coverage_note||note};}
for(const [kind,list]of [['corporation',context.window.MH_CORPS],['council',context.window.MH_COUNCILS]])for(const b of list){
 if(/^test[-\s]/i.test(b.slug))continue;
 const id=kind+':'+b.slug, snapshots={};
 for(const key of Object.keys(b).filter(k=>/^winners_\d{4}$/.test(k)&&b[k]?.length)){const year=key.slice(-4);snapshots[year]=snapshot(b,year,b[key],b['party_tally_'+year]);}
 if(kind==='council'&&b.winners?.length)snapshots[2025]=snapshot(b,2025,b.winners,b.party_tally);
 const sourceId=b.slug==='pune-pmc'?'pune':b.slug==='bmc'?'mumbai':null;
 if(sourceId){const s=sources[sourceId];snapshots[s.year]={...s,party_tally:Object.fromEntries(s.parties),coverage:'Supplied HTML historical snapshot. Candidate votes are incomplete.',rows:s.rows.map(r=>({...r,name:r.name,cands:r.review?[]:[[r.name,r.party,r.votes??null]],complete:false}))};}
 bodies.push({id,slug:b.slug,uiId:sourceId||b.slug,name:sourceId==='mumbai'?'Mumbai':b.name.replace(/\([^)]*\)/g,'').trim(),state:b.state||'Maharashtra',district:b.district==='Maharashtra'?'':b.district||'',kind,source:b.source_url||'https://mahasec.maharashtra.gov.in/',snapshots});
}
const existingDelhi=bodies.findIndex(b=>b.id==='corporation:mcd');if(existingDelhi>=0)bodies.splice(existingDelhi,1);
const delhi=context.window.DELHI_MCD;
if(delhi)bodies.push({id:'corporation:mcd',slug:'mcd',uiId:'delhi',name:'Delhi',state:'Delhi (NCT)',district:'National Capital Territory of Delhi',kind:'corporation',source:'https://sec.delhi.gov.in/',snapshots:{2022:snapshot(delhi,2022,delhi.winners_2022||delhi.winners_2026||[],delhi.party_tally_2022||delhi.party_tally_2026)}});
for(const b of [...rural.panchayat,...rural.zilla]){const kind=b.body_type==='Nagar Panchayat'?'nagar':b.body_type==='Panchayat Samiti'?'samiti':'zp';bodies.push({id:kind+':'+b.slug,slug:kind+'-'+b.slug,uiId:kind+':'+b.slug,name:b.name,state:b.state,district:b.district,kind,source:b.source_url,snapshots:Object.fromEntries(Object.entries(b.snapshots||{}).map(([y,s])=>[y,{...s,year:Number(y),rows:s.rows||[],coverage:b.coverage_note}]))});}
await fs.mkdir(path.join(root,'data/local-results'),{recursive:true});
const index=[];
for(const b of bodies){const file='/data/local-results/'+b.kind+'-'+b.slug+'.json';await write(file.slice(1),b);index.push({id:b.id,slug:b.slug,uiId:b.uiId,name:b.name,state:b.state,district:b.district,kind:b.kind,file,source:b.source,years:Object.keys(b.snapshots).map(Number).sort((a,b)=>b-a),wards:Object.fromEntries(Object.entries(b.snapshots).map(([y,s])=>[y,[...new Set(s.rows.map(r=>String(r.ward)))]])),seats:Object.fromEntries(Object.entries(b.snapshots).map(([y,s])=>[y,s.seats]))});}
await write('data/local-catalog.json',index);
// Only party identities, background and per-edition totals are copied. The
// original UI reads candidates from the existing election files on demand.
const background=JSON.parse(await read('data/party-background.json'));
const aliases={AAAP:'AAP',AITC:'TMC',Independent:'IND','Shiv Sena':'SHS','Shiv Sena (UBT)':'SHSUBT','NCP (SP)':'NCPSP','SHS UBT':'SHSUBT'};
const canonical=code=>aliases[code]||String(code).toUpperCase();
const parties=new Map();
function party(code,name,color){code=canonical(code);if(code==='NOTA')return null;if(!parties.has(code))parties.set(code,{id:'party:'+code.toLowerCase(),code,short:code,name:name||code,color:color||'#7c8390',editions:[]});const p=parties.get(code);if(name&&name!==code&&p.name===code)p.name=name;return p;}
for(const b of background)Object.assign(party(b.code,b.name,b.colour),{formation:b.formation,origin:b.origin,source:b.source});
const catalog=JSON.parse(await read('data/catalog.json'));
const seats=new Map();
for(const e of catalog){const d=JSON.parse(await read(e.file.replace(/^\//,'')));for(const s of d.seats){const key=[d.level,s.state,s.n,s.t].join('|');if(!seats.has(key))seats.set(key,{id:'imported-seat:'+encodeURIComponent(key),title:s.t,region:s.state,district:s.district||'',type:d.level,level:d.level,number:s.n,reference:true,records:[]});seats.get(key).records.push({edition:e.id,year:d.year,url:s.url});}}
await write('data/seat-directory.json',[...seats.values()].map(s=>({...s,records:s.records.sort((a,b)=>b.year-a.year)})));
const people=JSON.parse(await read('data/representatives-index.json'));
await write('data/people-directory.json',{reviewed_on:people.reviewed_on,coverage:people.coverage,vacancies:people.vacancies,rows:people.rows.map(r=>({...r}))});
for(const e of catalog){const d=JSON.parse(await read(e.file.replace(/^\//,''))),totals=new Map();let denominator=0;for(const seat of d.seats){const candidates=seat.c.filter(c=>d.parties[c[1]].short!=='NOTA'),winner=candidates[0];for(const c of seat.c){denominator+=c[2]||0;const ref=d.parties[c[1]],p=party(ref.short||ref.name,ref.name,ref.color);if(!p)continue;if(!totals.has(p.code))totals.set(p.code,{seats:0,votes:0,candidates:0});const t=totals.get(p.code);t.votes+=c[2]||0;t.candidates++;if(c===winner)t.seats++;}}for(const [code,t]of totals)parties.get(code).editions.push({edition:e.id,level:e.level,state:e.state,year:e.year,total:d.seats.length,denominator,complete:d.seats.every(s=>s.status==='unopposed'||s.rosterComplete&&s.c.every(c=>c[2]!=null)),source:e.source,...t});}
for(const e of catalog.filter(e=>e.level==='lok'&&e.state==='All India')){const d=JSON.parse(await read(e.file.replace(/^\//,'')));for(const state of new Set(d.seats.map(s=>s.state))){const seats=d.seats.filter(s=>s.state===state),totals=new Map();let denominator=0;for(const s of seats)for(const c of s.c){denominator+=c[2]||0;const p=party(d.parties[c[1]].short);if(!p)continue;if(!totals.has(p.code))totals.set(p.code,{seats:0,votes:0});const t=totals.get(p.code);t.votes+=c[2]||0;if(c===s.c.find(c=>d.parties[c[1]].short!=='NOTA'))t.seats++;}for(const [code,t]of totals)parties.get(code).editions.push({edition:e.id,level:'lok',state,year:e.year,total:seats.length,denominator,complete:seats.every(s=>s.status==='unopposed'||s.rosterComplete&&s.c.every(c=>c[2]!=null)),source:e.source,...t});}}
for(const b of bodies)for(const [year,s]of Object.entries(b.snapshots)){const tally=s.party_tally||{};for(const [code,seats]of Object.entries(tally)){const p=party(code,code);if(p)p.editions.push({body:b.id,level:'local',kind:b.kind,state:b.state,district:b.district,place:b.name,year:Number(year),total:s.seats,seats,votes:s.party_votes?.[code]??null,denominator:s.recorded_votes_including_nota??null,complete:!!s.party_votes,source:b.source});}}
await write('data/party-directory.json',{aliases,parties:[...parties.values()].sort((a,b)=>a.name.localeCompare(b.name))});
console.log(JSON.stringify({localBodies:index.length,localEditions:index.reduce((n,b)=>n+b.years.length,0),parties:parties.size}));

await (await import('./build-identities.mjs')).buildIdentities();

