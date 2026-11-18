import {AccountError,internalPath} from './account-core.mjs';
import {validateSubscription} from './push.mjs';
export async function projectAction(service,s,req,action,b){
 const db=(q,options={})=>service.db(q,{...options,token:s.token});
 if(action==='admin-corrections'&&req.method==='GET'){await service.staff(s);return {rows:await service.db('data_corrections?order=created_at.desc&limit=100',{admin:true})};}
 if(action==='review-correction'&&req.method==='POST'){await service.staff(s);if(typeof b.id!=='string'||!/^[a-f0-9-]{36}$/i.test(b.id)||!['reviewing','resolved','dismissed'].includes(b.status))throw new AccountError('invalid_input');await service.db('data_corrections?id=eq.'+b.id,{method:'PATCH',admin:true,body:{status:b.status}});return {saved:true};}
 if(action==='push-config'&&req.method==='GET')return {enabled:!!(service.env.WEB_PUSH_PUBLIC_KEY&&service.env.WEB_PUSH_PRIVATE_KEY&&service.env.WEB_PUSH_SUBJECT),publicKey:service.env.WEB_PUSH_PUBLIC_KEY||null};
 if(action==='push-subscribe'&&req.method==='POST'){
  if(!service.env.WEB_PUSH_PUBLIC_KEY||!service.env.WEB_PUSH_PRIVATE_KEY)throw new AccountError('push_unavailable',503);
  let subscription;try{subscription=validateSubscription(b)}catch{throw new AccountError('invalid_input')}
  const exists=await db('push_subscriptions?user_id=eq.'+s.user.id+'&endpoint=eq.'+encodeURIComponent(subscription.endpoint)+'&select=id');
  if(!exists.length)await db('push_subscriptions',{method:'POST',body:{user_id:s.user.id,...subscription}});
  else await db('push_subscriptions?id=eq.'+exists[0].id+'&user_id=eq.'+s.user.id,{method:'PATCH',body:{keys:subscription.keys}});
  await db('notification_preferences?user_id=eq.'+s.user.id,{method:'PATCH',body:{push:true,consented_at:new Date().toISOString()}});return {saved:true};
 }
 if(action==='push-unsubscribe'&&req.method==='POST'){
  if(typeof b.endpoint!=='string'||b.endpoint.length>4096)throw new AccountError('invalid_input');await db('push_subscriptions?user_id=eq.'+s.user.id+'&endpoint=eq.'+encodeURIComponent(b.endpoint),{method:'DELETE'});const remaining=await db('push_subscriptions?user_id=eq.'+s.user.id+'&select=id&limit=1');if(!remaining.length)await db('notification_preferences?user_id=eq.'+s.user.id,{method:'PATCH',body:{push:false}});return {saved:true};
 }
 if(action==='corrections'&&req.method==='GET')return {rows:await db('data_corrections?user_id=eq.'+s.user.id+'&order=created_at.desc&limit=50')};
 if(action==='corrections'&&req.method==='POST'){
  if(!['result','identity','boundary','other'].includes(b.category)||typeof b.description!=='string'||b.description.trim().length<20||b.description.length>4000||typeof b.page_url!=='string'||!b.page_url.startsWith('/')||b.page_url.startsWith('//')||b.page_url.includes('\\'))throw new AccountError('invalid_input');
  let source=null;if(b.source_url){try{const u=new URL(b.source_url);if(!['http:','https:'].includes(u.protocol)||u.username||u.password||u.href.length>2048)throw Error();source=u.href}catch{throw new AccountError('invalid_input')}}
  const rows=await db('data_corrections',{method:'POST',headers:{Prefer:'return=representation'},body:{user_id:s.user.id,page_url:internalPath(b.page_url),category:b.category,description:b.description.trim(),source_url:source}});return {submitted:true,id:rows?.[0]?.id};
 }
}
