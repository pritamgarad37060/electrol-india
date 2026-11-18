import {randomUUID} from 'node:crypto';
import {AccountError,safeURL} from './account-core.mjs';

export const PROFILE_BODY_LIMIT=3*1024*1024;
const bucket='account-profile-media';
const clean=(value,max)=>{if(typeof value!=='string'||value.length>max||/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(value))throw new AccountError('invalid_input');return value.trim();};
export const ownMedia=(path,user)=>typeof path==='string'&&new RegExp('^'+user+'/(avatar|cover)-[a-f0-9-]{36}\\.webp$').test(path);
export function webpImage(value){
 if(!value||typeof value.data!=='string'||value.data.length>1398104||!/^[A-Za-z0-9+/]+={0,2}$/.test(value.data))throw new AccountError('invalid_image');
 const bytes=Buffer.from(value.data,'base64');
 if(bytes.length<30||bytes.length>1048576||bytes.toString('ascii',0,4)!=='RIFF'||bytes.toString('ascii',8,12)!=='WEBP'||bytes.readUInt32LE(4)!==bytes.length-8)throw new AccountError('invalid_image');
 let width,height;const chunk=bytes.toString('ascii',12,16);
 if(chunk==='VP8X'){width=1+bytes.readUIntLE(24,3);height=1+bytes.readUIntLE(27,3);}
 else if(chunk==='VP8 '&&bytes.toString('hex',23,26)==='9d012a'){width=bytes.readUInt16LE(26)&0x3fff;height=bytes.readUInt16LE(28)&0x3fff;}
 else if(chunk==='VP8L'&&bytes[20]===0x2f){width=1+(bytes[21]|((bytes[22]&63)<<8));height=1+((bytes[22]>>6)|(bytes[23]<<2)|((bytes[24]&15)<<10));}
 if(!width||!height||width>2048||height>2048)throw new AccountError('invalid_image');
 return bytes;
}
export function profileFields(body){
 const update={};
 for(const [key,max] of [['display_name',100],['bio',500],['location',120],['website',2048]])if(key in body)update[key]=clean(body[key],max);
 if('display_name'in update&&!update.display_name)throw new AccountError('invalid_input');
 if(update.website)update.website=safeURL(update.website);
 for(const key of ['avatar_url','language','theme','preferred_state','preferred_constituency'])if(key in body)update[key]=body[key];
 if('avatar_url'in update){if(update.avatar_url!==null&&update.avatar_url!=='')update.avatar_url=safeURL(clean(update.avatar_url,2048));else update.avatar_url=null;}
 if('language'in update&&!['en','mr','hi'].includes(update.language)||'theme'in update&&!['light','dark','system'].includes(update.theme))throw new AccountError('invalid_input');
 for(const key of ['preferred_state','preferred_constituency'])if(key in update)update[key]=update[key]?clean(update[key],240):null;
 if('social_links'in body){if(!body.social_links||typeof body.social_links!=='object'||Array.isArray(body.social_links))throw new AccountError('invalid_input');const hosts={x:['x.com','twitter.com'],instagram:['instagram.com','www.instagram.com'],youtube:['youtube.com','www.youtube.com','youtu.be']};update.social_links={};for(const [key,value]of Object.entries(body.social_links)){if(!Object.hasOwn(hosts,key))throw new AccountError('invalid_input');if(value){const url=safeURL(clean(value,2048));if(!hosts[key].includes(new URL(url).hostname))throw new AccountError('invalid_input');update.social_links[key]=url;}}}
 return update;
}
export function presentProfile(profile){
 if(!profile)return null;
 const result={...profile};
 for(const kind of ['avatar','cover'])if(ownMedia(profile[kind+'_path'],profile.id))result[kind+'_url']='/api/account/profile-media?kind='+kind+'&v='+profile[kind+'_path'].split('/')[1];
 return result;
}
export async function removeProfileMedia(service,session,paths){
 const prefixes=paths.filter(path=>ownMedia(path,session.user.id));
 if(prefixes.length)await service.provider('/storage/v1/object/'+bucket,{method:'DELETE',body:{prefixes},token:session.token});
}
export async function saveProfile(service,session,body){
 const update=profileFields(body),images=body.images||{};
 if(typeof images!=='object'||Array.isArray(images)||Object.keys(images).some(k=>!['avatar','cover'].includes(k)))throw new AccountError('invalid_image');
 const prepared={};for(const [kind,value]of Object.entries(images))prepared[kind]=value===null?null:webpImage(value);
 for(const key of ['preferred_state','preferred_constituency'])if(update[key]){
  const rows=await service.db('followable_entities?id=eq.'+encodeURIComponent(update[key])+'&kind=eq.'+(key==='preferred_state'?'state':'constituency'),{token:session.token});
  if(!rows.length)throw new AccountError('invalid_input');
 }
 const profiles=await service.db('profiles?id=eq.'+session.user.id,{token:session.token});
 if(!profiles?.length)throw new AccountError('profile_unavailable',404);
 const old=profiles[0],uploaded=[];
 try{
  for(const [kind,bytes]of Object.entries(prepared)){
   const path=bytes?session.user.id+'/'+kind+'-'+randomUUID()+'.webp':null;
   if(bytes){await service.provider('/storage/v1/object/'+bucket+'/'+path,{method:'POST',rawBody:bytes,token:session.token,headers:{'Content-Type':'image/webp','Cache-Control':'private, no-store'}});uploaded.push(path);}
   update[kind+'_path']=path;if(kind==='avatar')update.avatar_url=null;
  }
  if(!Object.keys(update).length)throw new AccountError('invalid_input');
  const rows=await service.db('profiles?id=eq.'+session.user.id,{method:'PATCH',body:update,token:session.token,headers:{Prefer:'return=representation'}});
  if(!rows?.length)throw new AccountError('profile_unavailable',404);
  const obsolete=Object.keys(prepared).map(kind=>old[kind+'_path']).filter(Boolean);
  let cleanupPending=false;try{await removeProfileMedia(service,session,obsolete);}catch{cleanupPending=true;}
  return {saved:true,profile:presentProfile(rows[0]),media_cleanup_pending:cleanupPending};
 }catch(error){try{await removeProfileMedia(service,session,uploaded);}catch{/* Account deletion also removes abandoned files in the owner's folder. */}throw error;}
}
export async function profileMediaResponse(service,session,kind,headers){
 if(!['avatar','cover'].includes(kind))throw new AccountError('invalid_input');
 const rows=await service.db('profiles?id=eq.'+session.user.id+'&select='+kind+'_path',{token:session.token}),path=rows?.[0]?.[kind+'_path'];
 if(!ownMedia(path,session.user.id))throw new AccountError('not_found',404);
 const response=await service.provider('/storage/v1/object/authenticated/'+bucket+'/'+path,{token:session.token,rawResponse:true});
 headers.set('Content-Type','image/webp');headers.set('Cache-Control','private, no-store');headers.set('Vary','Cookie');headers.set('X-Content-Type-Options','nosniff');
 return new Response(await response.arrayBuffer(),{headers});
}
export async function deleteProfileMedia(service,session){
 // Delete through the Storage API, never directly from storage.objects.
 for(;;){
  const rows=await service.provider('/storage/v1/object/list/'+bucket,{method:'POST',token:session.token,body:{prefix:session.user.id+'/',limit:100,offset:0}});
  if(!rows?.length)return;
  const paths=rows.map(row=>session.user.id+'/'+row.name).filter(path=>ownMedia(path,session.user.id));
  if(!paths.length)return;
  await removeProfileMedia(service,session,paths);
 }
}
