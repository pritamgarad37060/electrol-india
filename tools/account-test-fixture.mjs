import {accountHandler} from '../netlify/functions/account.mjs';
export function accountFixture(){
 const id='00000000-0000-4000-8000-000000000001',sid='00000000-0000-4000-8000-000000000002';
 const env={SITE_URL:'http://127.0.0.1',ACCOUNT_ALLOW_LOCAL:'true',SUPABASE_URL:'https://example.supabase.co',SUPABASE_PUBLISHABLE_KEY:'sb_publishable_fixture',SUPABASE_SECRET_KEY:'sb_secret_fixture',ACCOUNT_COOKIE_SECRET:'fixture'.repeat(8)};
 const token='fixture.'+Buffer.from(JSON.stringify({sub:id,session_id:sid,exp:Math.floor(Date.now()/1000)+3600,aal:'aal1'})).toString('base64url')+'.signature';
 const profile={id,display_name:'Preview User',bio:'Election information and civic updates.',location:'Pune, Maharashtra',website:'https://example.com/',avatar_url:null,avatar_path:null,cover_path:null,language:'en',theme:'light',created_at:'2026-01-01T00:00:00Z',preferred_state:'state:mh',preferred_constituency:null};
 const entities=[{id:'state:mh',name:'Maharashtra',kind:'state',url:'/maharashtra/assembly/2024/',subtitle:'State / UT',active:true,metadata:{}},{id:'person:example',name:'Example Representative',kind:'person',url:'/representatives/',subtitle:'Representative record',active:true,metadata:{source:'https://sansad.in/'}},{id:'constituency:example',name:'Example constituency',kind:'constituency',url:'/constituencies/',subtitle:'Assembly constituency',active:true,metadata:{house:'Vidhan Sabha'}},{id:'body:example',name:'Example municipal corporation',kind:'body',url:'/municipal-corporations/',subtitle:'Local government',active:true,metadata:{}},{id:'ward:example',name:'Example ward',kind:'ward',url:'/municipal-corporations/',subtitle:'Ward snapshot',active:true,metadata:{year:2024}},{id:'state:historical',name:'Historical fixture',kind:'state',url:'/sources/',subtitle:'Inactive fixture',active:false,metadata:{}}];
 const follows=new Map(entities.slice(0,2).map(entity=>[entity.id,{entity_id:entity.id,user_id:id,muted:false,alert_types:['elections','news'],followed_at:'2026-01-02T00:00:00Z'}]));
 const preferences={user_id:id,in_app:true,email:false,security_email:true,frequency:'important',categories:['elections','representatives','government','news'],timezone:'Asia/Kolkata',date_format:'DD MMM YYYY',time_format:'12',quiet_enabled:false,quiet_days:[0,1,2,3,4,5,6],quiet_start:'22:00',quiet_end:'07:00'};const savedProfiles=new Map(),bookmarks=new Map(),updates=[];const storage=new Map(),calls=[];let failSave=false,failUpload=false;
 const counts=()=>Object.fromEntries([...new Set(entities.map(e=>e.kind))].map(kind=>[kind,entities.filter(e=>e.kind===kind&&follows.has(e.id)).length]));
 const user={id,email:'preview@example.test',email_confirmed_at:'2026-01-01',identities:[{identity_id:id,provider:'email',identity_data:{email:'preview@example.test'}}]};
 const fetcher=async(url,options={})=>{
  const u=new URL(url),p=u.pathname,q=u.searchParams,method=options.method||'GET',body=typeof options.body==='string'?JSON.parse(options.body):options.body;
  calls.push({path:p,query:u.search,method,body});
  if(p==='/auth/v1/user')return Response.json(user);
  if(p==='/auth/v1/settings')return Response.json({external:{google:false}});
  if(p==='/rest/v1/account_sessions')return Response.json([{id:sid,last_seen_at:new Date().toISOString()}]);
  if(p.endsWith('/rpc/consume_account_rate'))return Response.json(true);
  if(p.endsWith('/rpc/account_summary'))return Response.json({total_follows:follows.size,people:counts().person||0,unread:0,upcoming:0});
  if(p.endsWith('/rpc/account_follow_counts'))return Response.json(counts());
  if(p==='/rest/v1/notification_preferences'){if(method==='POST')Object.assign(preferences,body);return Response.json([preferences]);}
  if(p==='/rest/v1/saved_profiles'){const entity=q.get('entity_id')?.slice(3);if(method==='POST')savedProfiles.set(body.entity_id,body);if(method==='DELETE'){if(entity)savedProfiles.delete(entity);else savedProfiles.clear();}return Response.json([...savedProfiles.values()].map(row=>({...row,item:entities.find(e=>e.id===row.entity_id)})));}
  if(p.endsWith('/rpc/account_saved_content')){const rows=[...savedProfiles.values()].map(row=>({...row,item:entities.find(e=>e.id===row.entity_id)})).concat([...bookmarks.values()].map(row=>({...row,item:updates.find(e=>e.id===row.update_id)})));return Response.json(rows.filter(r=>!body.p_type||(r.entity_id?'profiles':r.item.content_type)===body.p_type).filter(r=>!body.p_query||(r.item.name||r.item.title).toLowerCase().includes(body.p_query.toLowerCase())).slice(body.p_offset,body.p_offset+21));}
  if(p.endsWith('/rpc/account_elections'))return Response.json({rows:[],counts:{}});
  if(p==='/rest/v1/bookmarks'){if(method==='POST')bookmarks.set(body.update_id,body);if(method==='DELETE')bookmarks.delete(q.get('update_id')?.slice(3));return Response.json([...bookmarks.values()]);}
  if(p==='/rest/v1/security_audit_events'||p==='/rest/v1/notifications')return Response.json([]);
  if(p==='/rest/v1/profiles'){
   if(method==='PATCH'){if(failSave)return Response.json({},{status:500});Object.assign(profile,body);}
   return Response.json([profile]);
  }
  if(p==='/rest/v1/followable_entities'){
   let rows=entities.filter(e=>!q.get('active')||e.active);
   if(q.get('id')){const value=q.get('id');rows=rows.filter(e=>value.startsWith('in.(')?value.slice(4,-1).split(',').includes(e.id):e.id===value.slice(3));}
   if(q.get('kind')){const value=q.get('kind');rows=rows.filter(e=>value.startsWith('in.(')?value.slice(4,-1).split(',').includes(e.kind):e.kind===value.slice(3));}
   if(q.get('name'))rows=rows.filter(e=>e.name.toLowerCase().includes(q.get('name').slice(7,-1).toLowerCase()));
   if(q.get('url'))rows=rows.filter(e=>e.url===q.get('url').slice(3));
   return Response.json(rows.slice(Number(q.get('offset')||0),Number(q.get('offset')||0)+Number(q.get('limit')||60)));
  }
  if(p==='/rest/v1/user_follows'){
   const entityId=q.get('entity_id')?.startsWith('eq.')?q.get('entity_id').slice(3):null;
   if(method==='POST'){if(!follows.has(body.entity_id))follows.set(body.entity_id,{...body,muted:false,alert_types:['elections','representatives','government','news'],followed_at:new Date().toISOString()});return Response.json([follows.get(body.entity_id)]);}
   if(method==='DELETE'){follows.delete(entityId);return Response.json([]);}
   if(method==='PATCH'){if(!follows.has(entityId))return Response.json([]);Object.assign(follows.get(entityId),body);return Response.json([follows.get(entityId)]);}
   let rows=[...follows.values()].map(row=>({...row,entity:entities.find(e=>e.id===row.entity_id)}));
   if(entityId)rows=rows.filter(row=>row.entity_id===entityId);
   if(q.get('entity_id')?.startsWith('in.')){const ids=q.get('entity_id').slice(4,-1).split(',');rows=rows.filter(row=>ids.includes(row.entity_id));}
   if(q.get('entity.kind'))rows=rows.filter(row=>row.entity.kind===q.get('entity.kind').slice(3));
   if(q.get('entity.name'))rows=rows.filter(row=>row.entity.name.toLowerCase().includes(q.get('entity.name').slice(7,-1).toLowerCase()));
   return Response.json(rows.slice(Number(q.get('offset')||0),Number(q.get('offset')||0)+Number(q.get('limit')||60)));
  }
  const bucket='/storage/v1/object/account-profile-media/';
  if(p.startsWith(bucket)&&method==='POST'){if(failUpload)return Response.json({},{status:500});storage.set(p.slice(bucket.length),Buffer.from(body));return Response.json({Key:p.slice(bucket.length)});}
  if(p==='/storage/v1/object/account-profile-media'&&method==='DELETE'){for(const key of body.prefixes)storage.delete(key);return Response.json([]);}
  if(p.startsWith('/storage/v1/object/authenticated/account-profile-media/')){const bytes=storage.get(p.split('/account-profile-media/')[1]);return bytes?new Response(bytes,{headers:{'Content-Type':'image/webp'}}):Response.json({},{status:404});}
  if(p==='/storage/v1/object/list/account-profile-media')return Response.json([...storage.keys()].filter(key=>key.startsWith(body.prefix)).map(key=>({name:key.split('/')[1],metadata:{size:storage.get(key).length}})).slice(0,100));
  if(p==='/rest/v1/staff_roles'||p==='/rest/v1/update_entities'||p==='/rest/v1/scheduled_elections'||p==='/rest/v1/bookmarks'||p==='/rest/v1/saved_searches'||p.endsWith('/rpc/account_feed'))return Response.json([]);
  throw Error('Unexpected fixture request: '+method+' '+p);
 };
 return {id,sid,env,token,user,profile,preferences,savedProfiles,bookmarks,updates,entities,follows,storage,calls,handler:accountHandler({env,fetcher}),fetcher,setFailSave:value=>failSave=value,setFailUpload:value=>failUpload=value};
}
