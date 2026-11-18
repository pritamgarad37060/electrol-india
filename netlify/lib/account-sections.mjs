import {AccountError,uuid} from './account-core.mjs';
export const contentTypes=['news','analysis','profiles','results','policies','interviews'];
export const interestTopics=['general','assembly','mlc','local','panchayat','municipal'];
const eq=encodeURIComponent;
const array=(v,allowed,max=50)=>{if(!Array.isArray(v)||v.length>max||v.some(x=>typeof x!=='string'||allowed&&!allowed.includes(x)))throw new AccountError('invalid_input');return [...new Set(v)];};
const queryText=v=>{if(typeof v!=='string'||v.length>100||/[,*()]/.test(v))throw new AccountError('invalid_input');return v.trim();};
export async function accountSection(service,s,req,headers,action,b){
 const u=new URL(req.url),page=Math.max(0,Math.min(10000,Math.floor(Number(u.searchParams.get('page'))||0))),offset=page*20;
 const get=q=>service.db(q,{token:s.token}),own=t=>t+'?user_id=eq.'+s.user.id;
 const mutate=(q,method,body)=>service.db(q,{token:s.token,method,body,headers:{Prefer:'resolution=merge-duplicates,return=representation'}});
 if(req.method==='GET'){
  if(action==='my-elections'){
   const status=u.searchParams.get('status')||null;if(status&&!['upcoming','ongoing','completed','unknown'].includes(status))throw new AccountError('invalid_input');
   const result=await service.rpc('account_elections',{p_status:status,p_query:queryText(u.searchParams.get('q')||''),p_offset:offset},s);
   return {...result,rows:result.rows.slice(0,20),has_more:result.rows.length>20};
  }
  if(action==='saved-content'){
   const type=u.searchParams.get('type')||'',search=queryText(u.searchParams.get('q')||'');if(type&&!contentTypes.includes(type))throw new AccountError('invalid_input');
   const rows=await service.rpc('account_saved_content',{p_type:type||null,p_query:search,p_oldest:u.searchParams.get('sort')==='oldest',p_offset:offset},s);
   return {rows:rows.slice(0,20),has_more:rows.length>20};
  }
  if(action==='connections')return {identities:(s.user.identities||[]).map(row=>({id:row.identity_id||row.id,provider:row.provider,email:row.identity_data?.email||s.user.email,created_at:row.created_at,last_sign_in_at:row.last_sign_in_at})),google:!!(await service.authSettings()).external?.google};
  if(action==='storage'){
   const rows=await service.provider('/storage/v1/object/list/account-profile-media',{method:'POST',token:s.token,body:{prefix:s.user.id+'/',limit:100,offset:0}});
   return {media:rows.map(row=>({name:row.name,bytes:Number(row.metadata?.size)||0,created_at:row.created_at})),media_bytes:rows.reduce((n,row)=>n+(Number(row.metadata?.size)||0),0)};
  }
 }
 if(req.method!=='POST')return;
 if(action==='interests'){
  const topics=array(b.topics,interestTopics,6),types=array(b.content_types,contentTypes,6),entities=array(b.entities,null,50);
  if(entities.some(id=>id.length>240||!/^[A-Za-z0-9:|%._-]+$/.test(id)))throw new AccountError('invalid_input');
  if(entities.length){const rows=await get('followable_entities?select=id&kind=in.(state,city,district,country)&active=eq.true&id=in.('+entities.map(eq).join(',')+')&limit=50');if(rows.length!==entities.length)throw new AccountError('invalid_input');}
  const rows=await mutate('profiles?id=eq.'+s.user.id,'PATCH',{interest_topics:topics,interest_content_types:types,interest_entities:entities});
  if(!rows.length)throw new AccountError('profile_unavailable',404);return {saved:true};
 }
 if(action==='preferences'){
  const values={user_id:s.user.id},types=['elections','representatives','government','news'];
  for(const key of ['in_app','email','security_email','quiet_enabled'])if(key in b){if(typeof b[key]!=='boolean')throw new AccountError('invalid_input');values[key]=b[key];}
  if('push' in b){if(typeof b.push!=='boolean')throw new AccountError('invalid_input');if(b.push&&!service.env.WEB_PUSH_PUBLIC_KEY)throw new AccountError('push_unavailable',503);values.push=b.push;}
  if(b.email&&(!service.env.RESEND_API_KEY||!service.env.ACCOUNT_EMAIL_FROM))throw new AccountError('email_delivery_unavailable',503);
  if('frequency'in b){if(!['important','instant','daily','weekly','off'].includes(b.frequency))throw new AccountError('invalid_input');values.frequency=b.frequency;}
  if('categories'in b)values.categories=array(b.categories,types,4);
  if('timezone'in b){if(!['Asia/Kolkata','UTC'].includes(b.timezone))throw new AccountError('invalid_input');values.timezone=b.timezone;}
  if('date_format'in b){if(!['DD MMM YYYY','DD/MM/YYYY','MM/DD/YYYY','YYYY-MM-DD'].includes(b.date_format))throw new AccountError('invalid_input');values.date_format=b.date_format;}
  if('time_format'in b){if(!['12','24'].includes(b.time_format))throw new AccountError('invalid_input');values.time_format=b.time_format;}
  for(const key of ['quiet_start','quiet_end'])if(key in b){if(typeof b[key]!=='string'||!/^([01]\d|2[0-3]):[0-5]\d$/.test(b[key]))throw new AccountError('invalid_input');values[key]=b[key];}
  if('quiet_days'in b){if(!Array.isArray(b.quiet_days)||b.quiet_days.some(d=>!Number.isInteger(d)||d<0||d>6))throw new AccountError('invalid_input');values.quiet_days=[...new Set(b.quiet_days)];}
  if(values.quiet_enabled&&(!values.quiet_days?.length||values.quiet_start===values.quiet_end))throw new AccountError('invalid_input');
  if(Object.keys(values).length===1)throw new AccountError('invalid_input');
  if('email'in b){values.consented_at=b.email?new Date().toISOString():null;}
  await mutate('notification_preferences','POST',values);return {saved:true};
 }
 if(action==='save-profile'){
  if(typeof b.entity_id!=='string'||b.entity_id.length>240)throw new AccountError('invalid_input');
  const rows=await get('followable_entities?id=eq.'+eq(b.entity_id)+'&kind=eq.person');if(!rows.length)throw new AccountError('entity_unavailable',404);
  if(b.remove)await mutate(own('saved_profiles')+'&entity_id=eq.'+eq(b.entity_id),'DELETE');
  else await mutate('saved_profiles','POST',{user_id:s.user.id,entity_id:b.entity_id});return {saved:true};
 }
 if(action==='reauth-send'){
  await service.rate(req,'auth',s.user.id);if(!s.user.email)throw new AccountError('reauthentication_required',403);
  await service.provider('/auth/v1/otp',{method:'POST',body:{email:s.user.email,create_user:false}});return {message:'check_email'};
 }
 if(action==='reauth-verify'){
  if(typeof b.code!=='string'||!/^\d{6}$/.test(b.code))throw new AccountError('invalid_otp');await service.rate(req,'auth',s.user.id);
  const result=await service.provider('/auth/v1/verify',{method:'POST',body:{email:s.user.email,token:b.code,type:'email'}});
  await service.complete(req,headers,result,{recent:true,expectedUser:s.user.id});return {reauthenticated:true};
 }
 if(action==='link-identity')return service.beginIdentityLink(req,headers,s);
 if(action==='unlink-identity'){
  service.recent(req,s);const identities=s.user.identities||[],target=identities.find(row=>(row.identity_id||row.id)===b.id);
  if(!uuid(b.id)||!target||target.provider==='email'||identities.length<2)throw new AccountError('last_identity',400);
  await service.provider('/auth/v1/user/identities/'+b.id,{method:'DELETE',token:s.token});await service.audit(s.user.id,'identity_unlinked',true);return {saved:true};
 }
 if(action==='clear-saved'){
  service.recent(req,s);if(b.confirmation!=='CLEAR SAVED CONTENT')throw new AccountError('confirmation_required');
  await mutate(own('bookmarks'),'DELETE');await mutate(own('saved_profiles'),'DELETE');await mutate(own('saved_searches'),'DELETE');return {saved:true};
 }
}
