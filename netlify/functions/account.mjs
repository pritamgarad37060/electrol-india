import {projectAction} from '../lib/project-actions.mjs';
import {accountSection} from '../lib/account-sections.mjs';
import {homeData} from '../lib/home-data.mjs';
import {globalSearch} from '../lib/global-search.mjs';
import {PROFILE_BODY_LIMIT,presentProfile,saveProfile,profileMediaResponse,deleteProfileMedia} from '../lib/account-profile.mjs';
import {createAccountService,AccountError,uuid,internalPath,safeURL} from '../lib/account-core.mjs';
const json=(value,status=200,headers=new Headers())=>{headers.set('Content-Type','application/json; charset=utf-8');headers.set('Cache-Control','private, no-store, max-age=0');headers.set('Vary','Cookie');headers.set('X-Content-Type-Options','nosniff');return new Response(JSON.stringify(value),{status,headers});};
const text=(v,max=200)=>{if(typeof v!=='string'||v.length>max||/[\u0000-\u0008]/.test(v))throw new AccountError('invalid_input');return v.trim();};
const email=v=>{v=text(v,254);if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))throw new AccountError('invalid_email');return v;};
const password=v=>{if(typeof v!=='string'||v.length<12||v.length>128)throw new AccountError('password_requirements');return v;};
const eq=v=>encodeURIComponent(String(v));
const types=['elections','representatives','government','news'];
export function accountHandler({env=process.env,fetcher=fetch}={}){
 const service=createAccountService(env,fetcher);
 return async function handler(req){const headers=new Headers();let action=new URL(req.url).pathname.split('/').filter(Boolean).at(-1),s;
  try{
   if(req.method==='OPTIONS')return json({error:'request_rejected'},403,headers);
   const searchResult=await globalSearch(service,req);if(searchResult!==undefined)return json(searchResult,200,headers);
   if(!service.configured)return json({configured:false,error:'accounts_not_configured'},503,headers);
   service.ensure();const csrf=service.csrf(req,headers);
   const homeResult=await homeData(service,req,fetcher);if(homeResult!==undefined)return json(homeResult,200,headers);
   if(req.method==='GET'&&action==='auth-bootstrap')return json({csrf,authOrigin:new URL(service.base).origin},200,headers);
   if(req.method==='GET'&&action==='google-config'){
    const settings=await service.authSettings();return json({google:!!settings.external?.google},200,headers);
   }
   if(req.method==='GET'&&action==='session'){
    try{s=await service.session(req,headers);}catch(e){if(e.status===401){const settings=await service.authSettings();return json({configured:true,user:null,csrf,expired:e.code==='session_expired',capabilities:{push:!!(env.WEB_PUSH_PUBLIC_KEY&&env.WEB_PUSH_PRIVATE_KEY&&env.WEB_PUSH_SUBJECT),passkeys:false,google:!!settings.external?.google}},200,headers);}throw e;}
    if(s.mfaRequired)return json({configured:true,user:{id:s.user.id,email:s.user.email},mfaRequired:true,factors:(s.user.factors||[]).filter(f=>f.status==='verified').map(({id,friendly_name,factor_type})=>({id,friendly_name,factor_type})),csrf,capabilities:{push:!!(env.WEB_PUSH_PUBLIC_KEY&&env.WEB_PUSH_PRIVATE_KEY&&env.WEB_PUSH_SUBJECT),passkeys:false}},200,headers);
    const [profiles,summary,roles,preferences]=await Promise.all([service.db('profiles?id=eq.'+s.user.id,{token:s.token}),service.rpc('account_summary',{},s),service.db('staff_roles?select=role&user_id=eq.'+s.user.id,{token:s.token}),service.db('notification_preferences?user_id=eq.'+s.user.id,{token:s.token})]);
    return json({configured:true,user:{id:s.user.id,email:s.user.email,email_change_pending:!!s.user.new_email},profile:presentProfile(profiles?.[0]||null),preferences:preferences?.[0]||{},summary,staff:!!roles?.length,aal:s.jwt.aal,csrf,capabilities:{push:!!(env.WEB_PUSH_PUBLIC_KEY&&env.WEB_PUSH_PRIVATE_KEY&&env.WEB_PUSH_SUBJECT),passkeys:false,email:!!(env.RESEND_API_KEY&&env.ACCOUNT_EMAIL_FROM)}},200,headers);
   }
   if(req.method==='GET'&&action==='entities'){
    await service.rate(req,'catalog');const u=new URL(req.url),q=(u.searchParams.get('q')||'').trim(),kind=u.searchParams.get('kind'),parent=u.searchParams.get('parent');
    const page=Math.max(0,Math.min(10000,Number(u.searchParams.get('page'))||0)),limit=Math.max(1,Math.min(60,Number(u.searchParams.get('limit'))||20));
    let query='followable_entities?active=eq.true&order=name.asc,id.asc&limit='+(limit+1)+'&offset='+(page*limit);
    if(q){if(q.length>100||/[,*()]/.test(q))throw new AccountError('invalid_input');query+='&name=ilike.'+eq('*'+q+'*');}
    if(kind){if(!/^[a-z]+$/.test(kind))throw new AccountError('invalid_input');query+='&kind=eq.'+kind;}
    if(parent)query+='&parent_id=eq.'+eq(text(parent,240));
    if(u.searchParams.get('url'))query+='&url=eq.'+eq(internalPath(u.searchParams.get('url')));
    const rows=await service.db(query);return json({rows:rows.slice(0,limit),has_more:rows.length>limit},200,headers);
   }
   let b={};if(req.method!=='GET'){if(req.method!=='POST')throw new AccountError('request_rejected',405);service.checkMutation(req);const raw=await req.text();if(Buffer.byteLength(raw)>(action==='profile'?PROFILE_BODY_LIMIT:32768))throw new AccountError('invalid_input',413);try{b=JSON.parse(raw);}catch{throw new AccountError('invalid_input');}if(!b||typeof b!=='object'||Array.isArray(b)||['user_id','userId','role','service_role','access_token','refresh_token'].some(k=>k in b))throw new AccountError('invalid_input');}
   if(action==='entity-lookup'&&req.method==='POST'){await service.rate(req,'catalog');if(!Array.isArray(b.urls)||b.urls.length>30)throw new AccountError('invalid_input');const paths=b.urls.map(v=>internalPath(text(v,2048)));const q=new URLSearchParams({select:'id,kind,name,url,subtitle',url:'in.('+paths.map(v=>JSON.stringify(v)).join(',')+')',active:'eq.true',limit:'60'});return json({rows:paths.length?await service.db('followable_entities?'+q):[]},200,headers);}
   if(['signup','login','forgot-password','google','callback','verify-email','send-otp','verify-otp'].includes(action)){
    if(req.method!=='POST')throw new AccountError('request_rejected',405);
    // OAuth initiation needs no session/profile refresh. Run its independent
    // provider availability and rate-limit checks together on cold requests.
    let googleSettings;
    if(action==='google'){
     const timed=async(name,work)=>{const started=performance.now();try{return await work()}finally{headers.append('Server-Timing',name+';dur='+(performance.now()-started).toFixed(1))}};
     [googleSettings]=await Promise.all([timed('oauth_settings',()=>service.authSettings()),timed('oauth_rate',()=>service.rate(req,'auth'))]);
    }else await service.rate(req,'auth',typeof b.email==='string'?b.email.toLowerCase():'');
    if(action==='send-otp'){
     const address=email(b.email);if(!['login','signup'].includes(b.mode))throw new AccountError('invalid_input');
     if(b.mode==='signup'&&b.accepted_privacy!==true)throw new AccountError('invalid_input');
     const payload={email:address,create_user:b.mode==='signup',...(b.mode==='signup'?{data:{display_name:text(b.display_name,100)}}:{})};
     try{await service.provider('/auth/v1/otp?redirect_to='+eq(service.origin+'/auth/verify/'),{method:'POST',body:payload});}catch(e){if(e.status===503||e.status===429)throw e;if(!['otp_disabled','user_not_found','user_already_exists'].includes(e.providerCode))throw new AccountError('email_delivery_unavailable',503);/* Do not reveal whether an address has an account. */}
     return json({message:'check_email',retry_after:60},200,headers);
    }
    if(action==='verify-otp'){
     const address=email(b.email),code=text(b.code,6);if(!/^[0-9]{6}$/.test(code))throw new AccountError('invalid_otp');
     let result;try{result=await service.provider('/auth/v1/verify',{method:'POST',body:{email:address,token:code,type:'email'}});}catch(e){if(e.status===503||e.status===429)throw e;throw new AccountError('invalid_otp');}
     await service.complete(req,headers,result);return json({authenticated:true,next:internalPath(b.next)},200,headers);
    }
    if(action==='signup'){
     const settings=await service.provider('/auth/v1/settings');if(settings.mailer_autoconfirm)throw new AccountError('email_verification_not_configured',503);
     const payload={email:email(b.email),password:password(b.password),data:{display_name:text(b.display_name,100)}};try{await service.provider('/auth/v1/signup?redirect_to='+eq(service.origin+'/auth/verify/'),{method:'POST',body:payload});}catch(e){if(e.status===503||e.status===429)throw e;}
     // Never treat an unverified signup response as an authenticated session.
     return json({message:'check_email'},200,headers);
    }
    if(action==='forgot-password'){const address=email(b.email);try{await service.provider('/auth/v1/recover?redirect_to='+eq(service.origin+'/auth/verify/'),{method:'POST',body:{email:address}});}catch(e){if(e.status===503||e.status===429)throw e;}return json({message:'check_email'},200,headers);}
    if(action==='google'){if(!googleSettings.external?.google)throw new AccountError('google_not_configured',503);return json({url:service.beginOAuth(req,headers,b.next)},200,headers);}
    if(action==='callback'){const result=await service.finishOAuth(req,headers,text(b.code,2048));return json({authenticated:true,next:result.next},200,headers);}
    if(action==='verify-email'){
     if(!['email','signup','recovery','email_change'].includes(b.type))throw new AccountError('invalid_auth_link');
     const result=await service.provider('/auth/v1/verify',{method:'POST',body:{token_hash:text(b.token_hash,512),type:b.type}});
     if(result?.access_token){await service.complete(req,headers,result,{recent:b.type==='recovery'});return json({authenticated:true,next:b.type==='recovery'?'/auth/reset-password/':'/account/'},200,headers);}
     return json({message:'verification_complete'},200,headers);
    }
    try{const result=await service.provider('/auth/v1/token?grant_type=password',{method:'POST',body:{email:email(b.email),password:text(b.password,128)}});await service.complete(req,headers,result);return json({authenticated:true,next:internalPath(b.next)},200,headers);}catch(e){if(e.status===401||e.code==='operation_failed'){await service.audit(null,'failed_sign_in',false);throw new AccountError('authentication_failed',401);}throw e;}
   }
    s=await service.session(req,headers);await service.rate(req,'private',s.user.id);
   if(s.mfaRequired&&!['mfa-factors','mfa-challenge','mfa-verify','logout'].includes(action))throw new AccountError('mfa_required',403);
    const projectResult=await projectAction(service,s,req,action,b); if(projectResult!==undefined)return json(projectResult,200,headers);
    const sectionResult=await accountSection(service,s,req,headers,action,b);
    if(sectionResult!==undefined)return json(sectionResult,200,headers);
   const u=new URL(req.url),page=Math.max(0,Math.min(10000,Number(u.searchParams.get('page'))||0)),offset=page*20;
   const get=table=>service.db(table,{token:s.token});
   const mutate=(table,method,body,extra={})=>service.db(table,{method,body,token:s.token,headers:{Prefer:'return=representation',...extra}});
   const own=table=>table+'?user_id=eq.'+s.user.id;
   if(req.method==='GET'){
    if(action==='home-context'){
     const follows=await get(own('user_follows')+'&select=entity:followable_entities!inner(id,kind,name,url,parent_id,metadata)&order=followed_at.desc&limit=500');
     const profiles=await get('profiles?id=eq.'+s.user.id+'&select=preferred_state,preferred_constituency,interest_topics,interest_entities');
     const profile=profiles[0]||{},ids=[profile.preferred_state,profile.preferred_constituency,...(profile.interest_entities||[])].filter(Boolean);
     const entities=ids.length?await get('followable_entities?active=eq.true&id=in.('+ids.map(eq).join(',')+')'):[];
     return json({profile,entities,follows:follows.map(r=>r.entity)},200,headers);
    }
    if(action==='follow-counts')return json({counts:await service.rpc('account_follow_counts',{},s)},200,headers);
    if(action==='profile-media')return await profileMediaResponse(service,s,u.searchParams.get('kind'),headers);
    if(action==='follow-detail'){
     const id=text(u.searchParams.get('id'),240),entities=await get('followable_entities?id=eq.'+eq(id));if(!entities.length)throw new AccountError('entity_unavailable',404);
     const [follows,updates,schedule,saved]=await Promise.all([get(own('user_follows')+'&entity_id=eq.'+eq(id)),get('update_entities?entity_id=eq.'+eq(id)+'&approved=eq.true&select=update:updates!inner(id,title,summary,canonical_url,published_at,category,status)&update.status=eq.published&order=update(published_at).desc&limit=5'),get('scheduled_elections?entity_id=eq.'+eq(id)+'&approved=eq.true'+(u.searchParams.get('history')==='1'&&entities[0].kind==='election'?'':'&event_at=gte.'+eq(new Date().toISOString()))+'&order=event_at.asc&limit=20'),entities[0].kind==='person'?get(own('saved_profiles')+'&entity_id=eq.'+eq(id)):Promise.resolve([])]);
     return json({entity:entities[0],follow:follows[0]||null,saved_profile:!!saved?.length,updates:updates.map(row=>row.update),schedule},200,headers);
    }
    if(action==='follows'){
     const search=u.searchParams.get('q'),kind=u.searchParams.get('kind');
     let q=own('user_follows')+'&select=*,entity:followable_entities!inner(*)&order='+(u.searchParams.get('sort')==='name'?'entity(name).asc,entity_id.asc':u.searchParams.get('sort')==='oldest'?'followed_at.asc,entity_id.asc':'followed_at.desc,entity_id.asc')+'&limit=21&offset='+offset;
     if(kind){if(!/^[a-z]+$/.test(kind))throw new AccountError('invalid_input');q+='&entity.kind=eq.'+kind;}
     if(search){if(search.length>100||/[,*()]/.test(search))throw new AccountError('invalid_input');q+='&entity.name=ilike.'+eq('*'+search+'*');}
     if(u.searchParams.get('ids')){
      let ids;try{ids=JSON.parse(u.searchParams.get('ids'));}catch{throw new AccountError('invalid_input');}
      if(!Array.isArray(ids)||ids.length>60||ids.some(id=>typeof id!=='string'||id.length>240||!/^[A-Za-z0-9:|%._-]+$/.test(id)))throw new AccountError('invalid_input');
      return json({rows:ids.length?await get(own('user_follows')+'&select=entity_id,muted,alert_types&entity_id=in.('+ids.map(eq).join(',')+')&limit=60'):[]},200,headers);
     }
     const [rows,counts]=await Promise.all([get(q),service.rpc('account_follow_counts',{},s)]);return json({rows:rows.slice(0,20),has_more:rows.length>20,counts},200,headers);
    }
    if(action==='feed'){const category=u.searchParams.get('category');if(category&&!types.includes(category))throw new AccountError('invalid_input');return json({rows:await service.rpc('account_feed',{p_category:category||null,p_offset:offset,p_limit:20},s)},200,headers);}
    if(action==='notifications'){let query=own('notifications')+'&archived_at=is.null&order=created_at.desc&limit=20&offset='+offset;const category=u.searchParams.get('category');if(category){if(![...types,'security'].includes(category))throw new AccountError('invalid_input');query+='&category=eq.'+category;}if(u.searchParams.get('unread')==='true')query+='&read_at=is.null';return json({rows:await get(query)},200,headers);}
    if(action==='preferences'){const rows=await get(own('notification_preferences'));return json({preferences:rows?.[0]||{in_app:true,email:false,push:!!(env.WEB_PUSH_PUBLIC_KEY&&env.WEB_PUSH_PRIVATE_KEY&&env.WEB_PUSH_SUBJECT),frequency:'important',security_email:true,categories:types,timezone:'Asia/Kolkata'}},200,headers);}
    if(action==='saved-searches')return json({rows:await get(own('saved_searches')+'&order=created_at.desc&limit=20&offset='+offset)},200,headers);
    if(action==='bookmarks')return json({rows:await get(own('bookmarks')+'&select=*,update:updates(*)&order=created_at.desc&limit=20&offset='+offset)},200,headers);
    if(action==='sessions')return json({rows:(await get(own('account_sessions')+'&revoked_at=is.null&order=last_seen_at.desc')).map(r=>({...r,current:r.id===s.jwt.session_id})),scope:'application_sessions'},200,headers);
    if(action==='security-events')return json({rows:await get(own('security_audit_events')+'&select=event_type,success,created_at&order=created_at.desc&limit=20&offset='+offset)},200,headers);
    if(action==='upcoming'){const follows=await get(own('user_follows')+'&select=entity_id');const ids=follows.map(f=>f.entity_id);const rows=ids.length?await get('scheduled_elections?approved=eq.true&event_at=gte.'+eq(new Date().toISOString())+'&order=event_at.asc&limit=100'):[];return json({rows:rows.filter(r=>ids.includes(r.entity_id))},200,headers);}

    if(action==='mfa-factors')return json({factors:s.user.factors||[]},200,headers);
    if(action==='admin'){await service.staff(s);const [health,pending,sources]=await Promise.all([service.rpc('account_admin_health',{},s),get('updates?status=eq.pending&order=ingested_at.desc&limit=20'),get('update_sources?order=name.asc')]);return json({health,pending,sources},200,headers);}
    throw new AccountError('not_found',404);
   }
   if(action==='follow'||action==='unfollow'||action==='follow-preferences'){
    const id=text(b.entity_id,240);const entities=await get('followable_entities?id=eq.'+eq(id)+(action==='follow'?'&active=eq.true':''));if(!entities.length)throw new AccountError('entity_unavailable',404);
    if(action==='follow')await mutate('user_follows','POST',{user_id:s.user.id,entity_id:id},{Prefer:'resolution=ignore-duplicates,return=representation'});
    if(action==='unfollow')await mutate(own('user_follows')+'&entity_id=eq.'+eq(id),'DELETE');
    if(action==='follow-preferences'){if(typeof b.muted!=='boolean'||!Array.isArray(b.alert_types)||b.alert_types.some(t=>!types.includes(t)))throw new AccountError('invalid_input');const rows=await mutate(own('user_follows')+'&entity_id=eq.'+eq(id),'PATCH',{muted:b.muted,alert_types:b.alert_types});if(!rows.length)throw new AccountError('follow_unavailable',404);}
    return json({saved:true},200,headers);
   }
   if(action==='profile')return json(await saveProfile(service,s,b),200,headers);

   if(action==='notification-read'||action==='notification-archive'){const patch=action==='notification-read'?{read_at:new Date().toISOString()}:{archived_at:new Date().toISOString()};if(b.all&&action==='notification-read')await mutate(own('notifications')+'&read_at=is.null','PATCH',patch);else{if(!uuid(b.id))throw new AccountError('invalid_input');await mutate(own('notifications')+'&id=eq.'+b.id,'PATCH',patch);}return json({saved:true},200,headers);}
   if(action==='bookmark'||action==='hide-update'){if(!uuid(b.id))throw new AccountError('invalid_input');const table=action==='bookmark'?'bookmarks':'hidden_updates';if(b.remove)await mutate(own(table)+'&update_id=eq.'+b.id,'DELETE');else await mutate(table,'POST',{user_id:s.user.id,update_id:b.id},{Prefer:'resolution=ignore-duplicates,return=representation'});return json({saved:true},200,headers);}
   if(action==='save-search'){if(b.remove){if(!uuid(b.id))throw new AccountError('invalid_input');await mutate(own('saved_searches')+'&id=eq.'+b.id,'DELETE');}else await mutate('saved_searches','POST',{user_id:s.user.id,name:text(b.name,100),url:internalPath(b.url),filters:b.filters&&typeof b.filters==='object'?b.filters:{}});return json({saved:true},200,headers);}
   if(action==='reauthenticate'){const result=await service.provider('/auth/v1/token?grant_type=password',{method:'POST',body:{email:s.user.email,password:text(b.password,128)}});await service.complete(req,headers,result,{recent:true,expectedUser:s.user.id});return json({reauthenticated:true},200,headers);}
   if(action==='password'||action==='email'){service.recent(req,s);const payload=action==='password'?{password:password(b.password)}:{email:email(b.email)};await service.provider('/auth/v1/user',{method:'PUT',body:payload,token:s.token});await service.audit(s.user.id,action==='password'?'password_changed':'email_change_requested',true);return json({saved:true,message:action==='email'?'check_email':'password_changed'},200,headers);}
   if(action==='mfa-enroll'){service.recent(req,s);const factor=await service.provider('/auth/v1/factors',{method:'POST',token:s.token,body:{factor_type:'totp',friendly_name:'Electrol India'}});return json({factor},200,headers);}
   if(action==='mfa-challenge'){if(!uuid(b.factor_id))throw new AccountError('invalid_input');return json(await service.provider('/auth/v1/factors/'+b.factor_id+'/challenge',{method:'POST',token:s.token,body:{}}),200,headers);}
   if(action==='mfa-verify'){if(!uuid(b.factor_id)||!uuid(b.challenge_id)||!/^\d{6}$/.test(b.code))throw new AccountError('invalid_input');const result=await service.provider('/auth/v1/factors/'+b.factor_id+'/verify',{method:'POST',token:s.token,body:{challenge_id:b.challenge_id,code:b.code}});await service.complete(req,headers,result,{recent:true,expectedUser:s.user.id});await service.audit(s.user.id,'mfa_verified',true);return json({verified:true},200,headers);}
   if(action==='mfa-unenroll'){service.recent(req,s);if(s.jwt.aal!=='aal2'||!uuid(b.factor_id))throw new AccountError('reauthentication_required',403);await service.provider('/auth/v1/factors/'+b.factor_id,{method:'DELETE',token:s.token});await service.audit(s.user.id,'mfa_disabled',true);return json({saved:true},200,headers);}
   if(action==='revoke-session'){service.recent(req,s);if(!b.all&&!uuid(b.id))throw new AccountError('invalid_input');await service.rpc('revoke_account_sessions',{p_all:!!b.all,p_session:b.id||null},s);if(b.all||b.id===s.jwt.session_id){try{await service.provider('/auth/v1/logout?scope='+(b.all?'global':'local'),{method:'POST',token:s.token});}finally{service.clear(headers);}}await service.audit(s.user.id,'sessions_revoked',true);return json({saved:true},200,headers);}
   if(action==='logout'){await service.db('account_sessions?id=eq.'+s.jwt.session_id+'&user_id=eq.'+s.user.id,{method:'PATCH',admin:true,body:{revoked_at:new Date().toISOString()}});try{await service.provider('/auth/v1/logout?scope=local',{method:'POST',token:s.token});}finally{service.clear(headers);}return json({signed_out:true},200,headers);}
   if(action==='export'){
    service.recent(req,s);
    const tables=['profiles','user_follows','notification_preferences','saved_profiles','saved_searches','bookmarks','notifications','security_audit_events','push_subscriptions','account_sessions','hidden_updates','data_corrections'];
    const order={profiles:'id',saved_profiles:'entity_id',user_follows:'entity_id',bookmarks:'update_id',hidden_updates:'update_id',notification_preferences:'user_id'};
    const values=await Promise.all(tables.map(async t=>{
     const result=[];
     for(let start=0;;start+=500){const rows=await get(t+(t==='profiles'?'?id=eq.':'?user_id=eq.')+s.user.id+'&limit=500&offset='+start+'&order='+(order[t]||'id'));result.push(...rows);if(rows.length<500)return result;}
    }));
    headers.set('Content-Disposition','attachment; filename="electrol-account-data.json"');
    return json({exported_at:new Date().toISOString(),data:Object.fromEntries(tables.map((t,i)=>[t,values[i]]))},200,headers);
   }
   if(action==='delete-account'){service.recent(req,s);if(b.confirmation!=='DELETE MY ACCOUNT')throw new AccountError('confirmation_required');await deleteProfileMedia(service,s);await service.audit(s.user.id,'account_deletion_requested',true);await service.db('account_sessions?user_id=eq.'+s.user.id,{method:'PATCH',admin:true,body:{revoked_at:new Date().toISOString()}});service.clear(headers);await service.provider('/auth/v1/logout?scope=global',{method:'POST',token:s.token});await service.provider('/auth/v1/admin/users/'+s.user.id,{method:'DELETE',admin:true,body:{should_soft_delete:false}});return json({deleted:true},200,headers);}
   if(action==='admin-review'){await service.staff(s);if(!uuid(b.id)||!Array.isArray(b.entity_ids)||b.entity_ids.some(id=>typeof id!=='string'||id.length>240)||typeof b.important!=='boolean')throw new AccountError('invalid_input');await service.rpc('review_account_update',{p_update:b.id,p_entities:b.entity_ids,p_important:b.important,p_reject:!!b.reject},s);return json({saved:true},200,headers);}
   if(action==='admin-role'){const role=await service.staff(s);service.recent(req,s);if(role!=='owner'||!uuid(b.user)||!['reviewer','operator','admin','owner','remove'].includes(b.staff_role)||b.confirmation!=='CHANGE STAFF ROLE')throw new AccountError('not_authorized',403);await service.rpc('manage_account_staff',{p_actor:s.user.id,p_target:b.user,p_role:b.staff_role},{admin:true});return json({saved:true},200,headers);}
   throw new AccountError('not_found',404);
  }catch(e){const code=e instanceof AccountError?e.code:'operation_failed',status=e instanceof AccountError?e.status:500;return json({error:code},status,headers);}
 };
}
export default accountHandler();
export const config={path:'/api/account/*'};
