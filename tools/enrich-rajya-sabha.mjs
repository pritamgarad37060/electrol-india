import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=async f=>JSON.parse(await fs.readFile(path.join(root,f),'utf8'));
const write=async(f,v)=>{await fs.mkdir(path.dirname(path.join(root,f)),{recursive:true});await fs.writeFile(path.join(root,f),JSON.stringify(v));};
const clean=v=>typeof v==='string'?v.replace(/\s+/g,' ').trim():v;
const iso=v=>{const m=String(v||'').match(/^(\d{2})\/(\d{2})\/(\d{4})$/);return m?`${m[3]}-${m[2]}-${m[1]}`:null;};
export async function enrichRajyaSabha(recordingsFile='tmp/rajya-sabha-recordings.json',activityFile='tmp/rajya-sabha-activity.json'){
 const recordings=await read(recordingsFile),activity=await read(activityFile),supplement=await read('tmp/rajya-sabha-supplement.json'),index=await read('data/rajya-sabha-index.json');
 const bioSnapshot=await read('reports/sources/rajya-sabha-'+index.reviewed_on+'.json');
 if(!recordings.done||!activity.done||!supplement.done||supplement.errors.length)throw Error('Source collection is not complete');
 if(index.profiles.length!==recordings.roster.records.length)throw Error('Roster changed; review before publishing');
 const staged=[],report={reviewed_at:activity.retrieved_at,members:0,recordings:0,oath_recordings:0,members_with_oath:0,counts:{},unavailable:[],backup:'tmp/rs-enrichment-backup-'+Date.now()};
 for(const entry of index.profiles){
  const id=entry.rsid,original=await read(entry.file.slice(1)),gallery=recordings.profiles[id],extra=activity.profiles[id],supp=supplement.profiles[id];
  if(supp?.bio?.length!==1||supp.bio[0].MP_CODE!==id)throw Error('Supplementary biography identity mismatch '+id);
  if(original.rsid!==id||!extra||!gallery)throw Error('Missing or mismatched source '+id);
  const rows=gallery.gallery.records;
  if(!Array.isArray(rows)||rows.length!==gallery.gallery._metadata.totalElements)throw Error('Incomplete recording pages '+id);
  if(rows.some(v=>Number(v.mpCode)!==id))throw Error('Cross-member recording '+id);
  const clips=[...new Map(rows.map(v=>[v.videoUrl,{member_id:id,title:clean(v.videoTitle),url:v.videoUrl,date:iso(v.dateEvent),source_date:v.dateEvent,session:v.session,category:clean(v.debName),category_code:v.debCode,size:clean(v.videoSize),source:gallery.source}])).values()];
  const oaths=clips.filter(v=>/\boath\b|affirmation/i.test(v.title+' '+v.category));
  const sections={};
  for(const [kind,section] of Object.entries(extra)){
   if(section.status==='unavailable'){sections[kind]=section;report.unavailable.push({id,kind,error:section.error});continue;}
   const data=section.data;
   if(data?.success===false||data?.error)throw Error('Source reported an error '+id+' '+kind);
   const records=Array.isArray(data)?data:data?.records||data?.data;
   if(!Array.isArray(records))throw Error('Unknown source shape '+id+' '+kind);
   if(data?._metadata&&records.length!==data._metadata.totalElements)throw Error('Incomplete '+kind+' pages for '+id);
   for(const row of records){const member=row.mp_code??row.mpCode??row.t_mp_code;if(member!=null&&Number(member)!==id){if(kind==='questions'&&/^\s*\(clubbed\)/i.test(row.qtitle||'')){row.member_association='clubbed-question';row.profile_member_id=id;report.clubbed_questions=(report.clubbed_questions||0)+1;}else throw Error('Cross-member '+kind+' '+id);}}
   const published=kind==='tours'?records.filter(row=>!(/\bthis is (?:a )?test\b|\btest event\b|\bdemo event\b|^event name$/i.test(clean(row.eventName)||''))):records;
   if(published.length!==records.length)(report.excluded_test_records||=[]).push({id,kind,count:records.length-published.length});
   sections[kind]={source:section.source,status:'available',total:published.length,source_total:records.length,records:published};
   report.counts[kind]=(report.counts[kind]||0)+published.length;
  }
  const b=bioSnapshot.profiles[id]?.bio,flag=String(b?.freeStruggle??'').trim();
  const sb=supp.bio[0];
  const fallback={father:'FATH_NAME',mother:'MOTH_NAME',birth_place:'PLACE_BIRTH',marital_status:'MARITIAL',marriage_date:'DATE_MARRIAGE',spouse:'SPOUSE_NAME',sons:'NO_SONS',daughters:'NO_DAUGHTER',education:'QUALIFICATION',profession:'OTHER_PROF_DETAIL',previous_membership:'PREVIOUS_MEMBERSHIP',books:'BOOKS',social_activities:'ACTIVITY',countries_visited:'COUNTRY_VISITED',hobbies:'HOBBIES',other_information:'ESSENTIAL_INFO'};
  for(const [key,sourceKey] of Object.entries(fallback))if(!original[key])original[key]=clean(sb[sourceKey])||null;
  original.other_present_address=clean(sb.OTH_C_LADDRESS)||null;
  original.other_present_phone=clean(sb.OTH_C_LTELE)||null;
  original.other_permanent_phone=clean(sb.OTH_C_PTELE)||null;
  original.present_postcode=clean(sb.C_LPIN)||null;
  original.permanent_postcode=clean(sb.C_PPIN)||null;
  original.other_present_postcode=clean(sb.OTH_C_LPIN)||null;
  original.other_permanent_postcode=clean(sb.OTH_C_PPIN)||null;
  original.source_supplementary_biography=supp.source;
  original.oath_date=/^(19|20)\d{2}-\d{2}-\d{2}T/.test(sb.oath||'')?sb.oath.slice(0,10):null;
  if(original.oath_date)report.oath_dates=(report.oath_dates||0)+1;
  sections.debates={source:supp.debates?.source,status:'unavailable',error:supp.debates?.error||'Official debate archive unavailable during collection'};
  report.unavailable.push({id,kind:'debates',error:sections.debates.error});
  original.freedom_fighter=flag==='1'?'Yes':flag==='0'?'No':null;
  original.brief_biography_hi=clean(b?.briefBioDataHin)||original.brief_biography_hi||null;
  original.activity_file='/data/rajya-sabha-activity/'+id+'.json';
  original.activity_summary=Object.fromEntries(Object.entries(sections).map(([k,s])=>[k,{status:s.status,total:s.total??null}]));
  original.recordings_count=clips.length;original.oath_recordings=oaths;
  original.oath_status=original.oath_date?'date-published':oaths.length?'recording-published':'not-found-in-published-gallery';
  original.activity_reviewed_at=activity.retrieved_at;
  staged.push({file:entry.file.slice(1),profile:original,activity:{rsid:id,house:'Rajya Sabha',name:original.name,reviewed_at:activity.retrieved_at,sections,recordings:{source:gallery.source,status:'available',total:clips.length,records:clips}}});
  report.members++;report.recordings+=clips.length;report.oath_recordings+=oaths.length;if(oaths.length)report.members_with_oath++;
 }
 // Validate the entire snapshot before changing any published profile.
 await fs.mkdir(path.join(root,report.backup),{recursive:true});
 await fs.cp(path.join(root,'data/public-profiles/rs'),path.join(root,report.backup,'profiles'),{recursive:true});
 await fs.copyFile(path.join(root,'js/html-profiles.js'),path.join(root,report.backup,'html-profiles.js'));
 for(const s of staged){await write(s.file,s.profile);await write(s.profile.activity_file.slice(1),s.activity);}
 await write('reports/rajya-sabha-enrichment.json',report);
 console.log(JSON.stringify({...report,unavailable:report.unavailable.length}));return report;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await enrichRajyaSabha(process.argv[2],process.argv[3]);
