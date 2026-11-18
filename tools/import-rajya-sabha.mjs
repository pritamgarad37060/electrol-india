import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {uid} from './build-identities.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const origin='https://sansad.in',source=origin+'/rs/members';
const clean=v=>typeof v==='string'?v.replace(/\s+/g,' ').trim():v??null;
const date=v=>{const m=clean(v)?.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);return m?`${m[3]}-${m[2]}-${m[1]}`:clean(v)||null;};
const read=async file=>JSON.parse(await fs.readFile(path.join(root,file),'utf8'));
const save=async(file,value)=>{const p=path.join(root,file);await fs.mkdir(path.dirname(p),{recursive:true});await fs.writeFile(p,JSON.stringify(value));};
const api=(type,id)=>`${origin}/api_rs/member/${type}?mpCode=${id}&locale=en`;
const names=s=>String(s||'').normalize('NFKC').toLowerCase().replace(/\b(shri|smt|shrimati|sushri|dr|adv|prof|mr|mrs|ms)\b\.?/g,'').match(/[\p{L}\p{N}]+/gu)||[];
const nameKey=s=>names(s).sort().join('|');
const region=s=>({Keralam:'Kerala'}[clean(s)]||clean(s));
const email=s=>clean(s)?.replace(/\[dot\]/gi,'.').replace(/\[at\]/gi,'@')||null;
const texts=(...values)=>[...new Set(values.map(clean).filter(v=>v&&v!==','&&!/^[,;\s]+$/.test(v)))].join('; ')||null;
async function download(){
 const json=async url=>{let error;for(let i=0;i<3;i++)try{const r=await fetch(url,{signal:AbortSignal.timeout(20000)});if(!r.ok)throw Error('HTTP '+r.status);return await r.json();}catch(e){error=e;}throw error;};
 const roster=await json(origin+'/api_rs/member/sitting-members?state=&party=&page=1&size=500&search=&locale=en&mpFlag=1');
 const result={source,retrieved_at:new Date().toISOString(),roster,profiles:{},errors:[]},queue=[...roster.records];
 await Promise.all(Array.from({length:4},async()=>{while(queue.length){const r=queue.shift(),[bio,terms]=await Promise.all([json(api('bio-data',r.mpsno)),json(api('term-years',r.mpsno))]);result.profiles[r.mpsno]={bio,terms};}}));return result;
}
export async function importRajyaSabha(snapshot){
 const raw=typeof snapshot==='string'?JSON.parse(await fs.readFile(snapshot,'utf8')):snapshot||await download();
 const records=raw.roster?.records||[],total=raw.roster?._metadata?.totalElements;
 if(!records.length||records.length!==total||new Set(records.map(r=>r.mpsno)).size!==total)throw Error('Incomplete or duplicate official sitting-member roster');
 const reviewed=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(raw.retrieved_at)),backup='tmp/rajya-sabha-backup-'+Date.now();
 for(const file of ['data/people-directory.json','data/representatives-index.json']){await fs.mkdir(path.dirname(path.join(root,backup,file)),{recursive:true});await fs.copyFile(path.join(root,file),path.join(root,backup,file));}
 const people=await read('data/people-directory.json'),existing=people.rows.filter(r=>r.kind!=='rs'),officeRows=existing.filter(r=>['office','officeholder'].includes(r.kind)),rows=[],index=[],links=[],unmatched=[];
 for(const roster of records){
  const id=Number(roster.mpsno),record=raw.profiles[id],b=record?.bio,t=record?.terms;
  if(!b||Number(b.mpCode)!==id||!t||!Array.isArray(t.records))throw Error('Missing or mismatched biography/terms for RS '+id);
  const officialName=clean(b.name)||clean(roster.name),state=region(roster.state),key='rs-'+id;
  const matched=officeRows.filter(o=>{
   const explicit=[o.membership_source,o.source].some(s=>s?.match(/\/rs\/members\/biographyM\/(\d+)/)?.[1]===String(id));
   if(explicit)return true;
   if(o.party!==clean(roster.partyCode)||!['India','',state].includes(region(o.membership_state||o.state)))return false;
   if([officialName,roster.name].some(n=>nameKey(n)===nameKey(o.name)))return true;
   if(!roster.currentMinister||!/minister/i.test(o.role||''))return false;
   const a=names(o.name),z=names(officialName);
   return a.length===z.length&&a.every(v=>z.some(w=>v===w||v.length===1&&w.startsWith(v)))&&a.some(v=>v.length>1&&z.includes(v));
  });
  const unique=matched.filter(o=>{const matches=records.filter(r=>{const bio=raw.profiles[r.mpsno]?.bio;return nameKey(o.name)===nameKey(bio?.name)||nameKey(o.name)===nameKey(r.name);});return matches.length<=1;});
  const offices=[...new Map(unique.flatMap(o=>o.office_records||o.offices||[]).map(o=>[JSON.stringify(o),o])).values()];
  links.push(...unique.map(o=>({from:o.key,to:key,method:o.membership_source?.includes('/biographyM/'+id)?'official-source-id':'office-name-party-and-state'})));
  const sourceProfile=`${origin}/rs/members/biographyM/${id}`,profileFile=`/data/public-profiles/rs/${id}.json`;
  const terms=t.records.map(o=>({term:o.termNumber,period:clean(o.termPeriod),state:region(o.state),party:clean(o.party),reason:clean(o.reasonAndVacation),vacation_date:date(o.vacationDate),source:api('term-years',id)}));
  const positions=(b.positionHelds||[]).map(o=>({period:clean(o.period),position:clean(o.position),source:api('position-held',id)}));
  const profile={id:key,rsid:id,house:'Rajya Sabha',name:officialName,source_name:clean(roster.name),name_hi:clean(roster.hname),state,source_state:clean(roster.state),nominated:state==='Nominated',party:clean(roster.party),party_code:clean(roster.partyCode),status:clean(roster.status),gender:clean(b.gender||roster.gender),dob:date(b.dateBirth||roster.dob),birth_place:clean(b.placeBirth),father:clean(b.fatherName),mother:clean(b.motherName),marital_status:clean(b.maritial),marriage_date:clean(b.dateMarriage),spouse:clean(b.spouseName),sons:clean(b.noSons),daughters:clean(b.noDaughter),education:clean(b.qualification),profession:texts(b.prof1,b.prof2,b.prof3,b.otherProfDetails),email:email(b.emailID||roster.emailID),phone:texts(b.mobileNo,b.mobileNo2,b.permanentTele),delhi_phone:clean(b.localTele||roster.localTele),present_address:clean(b.localAdd||roster.localAdd),permanent_address:texts(b.permanentAdd||roster.permanentAdd,b.otherPermanentAdd),books:clean(b.books),social_activities:clean(b.activity),hobbies:clean(b.hobbies),countries_visited:clean(b.countryVisited),other_information:clean(b.essentialInfo),previous_membership:clean(b.previousMembership),brief_biography:clean(b.briefBioData),brief_biography_hi:clean(b.briefBioDataHin),term:clean(roster.term),term_start:date(roster.notificationDate),term_end:date(roster.expirationDate),num_terms:roster.termCount,membership_terms:terms,positions,social:{},photo_url:clean(b.imageUrl||roster.imageUrl),source_profile:sourceProfile,source_biography:api('bio-data',id),source_positions:api('position-held',id),source_terms:api('term-years',id),reviewed_on:reviewed,source_updated_at:clean(roster.updatedAt),current_minister_in_source:!!roster.currentMinister};
  for(const extension of ['jpg','png','webp']){const photo=`/data/photos/rs/${id}.${extension}`;try{await fs.access(path.join(root,photo));profile.local_photo=photo;break;}catch{}}
  // A roster refresh must retain independently sourced profile enrichment.
  try{const previous=await read(profileFile.slice(1));if(previous.rsid===id){for(const key of ['activity_file','activity_summary','activity_reviewed_at','recordings_count','oath_recordings','oath_status','oath_date','source_supplementary_biography','freedom_fighter','other_present_address','other_present_phone','other_permanent_phone','present_postcode','permanent_postcode','other_present_postcode','other_permanent_postcode'])if(previous[key]!==undefined)profile[key]=previous[key];profile.social={...previous.social,...profile.social};for(const key of ['marriage_date','father','mother','spouse','sons','daughters','books','social_activities','countries_visited','hobbies','other_information','previous_membership','brief_biography_hi'])if(!profile[key]&&previous[key])profile[key]=previous[key];}}catch(error){if(error.code!=='ENOENT')throw error;}
  await save(profileFile.slice(1),profile);
  const row={key,kind:'rs',rsid:id,house:'Rajya Sabha',name:officialName,name_hi:profile.name_hi,state,constituency:'',party:profile.party_code,party_name:profile.party,gender:profile.gender,role:'Member of Parliament (Rajya Sabha)',status:'sitting',membership_status:'sitting',membership_source:sourceProfile,nominated:profile.nominated,term:profile.term,term_start:profile.term_start,term_end:profile.term_end,terms:profile.num_terms,categories:['rs',...new Set(offices.map(o=>o.category).filter(Boolean))],offices,office_records:offices,source:sourceProfile,source_roster:source,reviewed_on:reviewed,profile_file:profileFile,photo:profile.photo_url,person_uid:uid('representative\u001f'+key),identity_status:'official-house-member-id',source_aliases:unique.map(o=>({key:o.key,person_uid:o.person_uid})),current_minister_in_source:profile.current_minister_in_source};
  if(profile.local_photo)row.local_photo=profile.local_photo;
  rows.push(row);index.push({id:key,rsid:id,name:officialName,state,house:'Rajya Sabha',party:profile.party,party_code:profile.party_code,file:profileFile,photo_url:profile.photo_url});
 }
 for(const office of officeRows)if(/rajya sabha/i.test(office.membership||'')&&!links.some(l=>l.from===office.key))unmatched.push({key:office.key,name:office.name});
 const duplicates=links.filter((l,i)=>links.some((x,j)=>j!==i&&x.from===l.from&&x.to!==l.to));if(duplicates.length)throw Error('Ambiguous office-profile linkage; import stopped before publishing directory');
 for(const file of ['data/people-directory.json','data/representatives-index.json']){const directory=await read(file);directory.rows=[...directory.rows.filter(r=>r.kind!=='rs'),...rows];directory.rajya_sabha={source,reviewed_on:reviewed,sitting_members:rows.length,profile_index:'/data/rajya-sabha-index.json'};await save(file,directory);}
 await save('data/rajya-sabha-index.json',{source,reviewed_on:reviewed,total:rows.length,profiles:index});
 const searchFile='netlify/generated/global-search-index.json',searchIndex=await read(searchFile);
 await fs.mkdir(path.dirname(path.join(root,backup,searchFile)),{recursive:true});await fs.copyFile(path.join(root,searchFile),path.join(root,backup,searchFile));
 const replaced=new Set(links.map(l=>l.from));
 searchIndex.rows=searchIndex.rows.filter(r=>{if(r.category!=='people')return true;const key=new URL(r.url,'https://electrol.local').searchParams.get('id');return !key?.startsWith('rs-')&&!replaced.has(key);});
 for(const r of rows){const url='/representatives/profile/?id='+r.key;searchIndex.rows.push({id:'people|'+url+'|'+nameKey(r.name),category:'people',name:r.name,aliases:[r.name_hi,r.party_name,'Rajya Sabha',...r.source_aliases.map(a=>officeRows.find(o=>o.key===a.key)?.name)].filter(Boolean),url,state:r.state,constituency:'',party:r.party,role:r.role,roles:['mp','rs',...r.categories],period:'current',status:'sitting',photo:r.local_photo||r.photo,type:'rajya-sabha',house:'Rajya Sabha',entity_kind:'person',updated:raw.retrieved_at});}
 searchIndex.generated_at=new Date().toISOString();await save(searchFile,searchIndex);
 await save(`reports/sources/rajya-sabha-${reviewed}.json`,raw);
 const report={source,reviewed_on:reviewed,total:rows.length,biographies:Object.keys(raw.profiles).length,term_histories:rows.length,nominated:rows.filter(r=>r.nominated).length,office_aliases:links,unmatched_office_records:unmatched,fields_without_source:'Social-media URLs and election vote totals are not provided by these endpoints and are not inferred.',backup};
 await save('reports/rajya-sabha-import.json',report);console.log(JSON.stringify({...report,office_aliases:links.length}));return report;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await importRajyaSabha(process.argv[2]);
