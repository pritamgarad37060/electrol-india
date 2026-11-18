import {createHmac,randomBytes,createHash,timingSafeEqual} from 'node:crypto';
export class AccountError extends Error{constructor(code,status=400){super(code);this.code=code;this.status=status;}}
export const internalPath=value=>{if(typeof value!=='string'||value.length>2048||!value.startsWith('/')||value.startsWith('//')||/[\\\x00-\x1f]/.test(value))return '/account/';try{const u=new URL(value,'https://electrol.invalid');return u.origin==='https://electrol.invalid'?u.pathname+u.search:'/account/';}catch{return '/account/';}};
export const uuid=value=>typeof value==='string'&&/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/i.test(value);
export const safeURL=value=>{try{const u=new URL(value);if(u.protocol!=='https:'||u.username||u.password)throw Error();return u.href;}catch{throw new AccountError('invalid_url');}};
export const safeEqual=(a,b)=>{if(typeof a!=='string'||typeof b!=='string')return false;const x=Buffer.from(a),y=Buffer.from(b);return x.length===y.length&&timingSafeEqual(x,y);};
export function createAccountService(env=process.env,fetcher=fetch){
 const publicKey=env.SUPABASE_PUBLISHABLE_KEY||env.SUPABASE_ANON_KEY;
 const serverKey=env.SUPABASE_SECRET_KEY||env.SUPABASE_SERVICE_ROLE_KEY;
 const configured=!!(env.SUPABASE_URL&&publicKey&&serverKey&&env.ACCOUNT_COOKIE_SECRET?.length>=32);
 const origin=(env.SITE_URL||env.URL||'https://electrolindia.netlify.app').replace(/\/$/,''),base=(env.SUPABASE_URL||'').replace(/\/$/,'');
 const local=env.ACCOUNT_ALLOW_LOCAL==='true'&&/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
 const prefix=local?'ei_':'__Host-ei_',cookieOptions='; Path=/; HttpOnly; SameSite=Lax'+(local?'':'; Secure');
 const cookies=req=>Object.fromEntries((req.headers.get('cookie')||'').split(';').map(s=>s.trim().split(/=(.*)/s)).filter(a=>a.length>=2).map(([k,v])=>[k,v]));
 const sign=value=>{const payload=Buffer.from(JSON.stringify(value)).toString('base64url');return payload+'.'+createHmac('sha256',env.ACCOUNT_COOKIE_SECRET||'').update(payload).digest('base64url');};
 const unsign=value=>{try{const [payload,signature]=String(value).split('.');if(!safeEqual(signature,createHmac('sha256',env.ACCOUNT_COOKIE_SECRET||'').update(payload).digest('base64url')))return null;const d=JSON.parse(Buffer.from(payload,'base64url'));return d.exp>Date.now()?d:null;}catch{return null;}};
 const setCookie=(headers,name,value,seconds)=>headers.append('Set-Cookie',prefix+name+'='+value+'; Max-Age='+Math.max(0,Math.floor(seconds))+cookieOptions);
 const clear=headers=>{for(const k of ['access','refresh','reauth','flow'])setCookie(headers,k,'',0);};
 const ensure=()=>{if(!configured)throw new AccountError('accounts_not_configured',503);if(!/^https:\/\//.test(base)||(!/^https:\/\//.test(origin)&&!local))throw new AccountError('accounts_not_configured',503);};
 async function provider(path,{method='GET',body,rawBody,rawResponse=false,token,admin=false,headers={}}={}){
  ensure();const key=admin?serverKey:publicKey;
  // Modern API keys belong only in apikey. Authorization carries a user JWT,
  // or a legacy JWT key when an existing project still uses legacy keys.
  const authorization=token||(!key.startsWith('sb_')?key:null);
  let response;try{response=await fetcher(base+path,{method,headers:{apikey:key,...(authorization?{Authorization:'Bearer '+authorization}:{}),'Content-Type':'application/json',...headers},body:rawBody??(body===undefined?undefined:JSON.stringify(body)),signal:AbortSignal.timeout(12000)});}catch{throw new AccountError('service_unavailable',503);}
  if(rawResponse&&response.ok)return response;
  let value=null;try{const text=await response.text();value=text?JSON.parse(text):null;}catch{throw new AccountError('service_unavailable',503);}
  if(!response.ok){if(response.status===429)throw new AccountError('too_many_requests',429);if(response.status>=500)throw new AccountError('service_unavailable',503);if(['email_address_not_authorized','email_provider_disabled','smtp_max_frequency'].includes(value?.code))throw new AccountError('email_delivery_unavailable',503);const error=new AccountError(response.status===401?'authentication_failed':'operation_failed',response.status===401?401:400);error.providerCode=typeof value?.code==='string'?value.code:null;throw error;}
  return value;
 }
 let settingsPromise,settingsExpire=0;
 async function authSettings(){if(!settingsPromise||Date.now()>settingsExpire){settingsExpire=Date.now()+60000;settingsPromise=provider('/auth/v1/settings').catch(error=>{settingsPromise=null;throw error;});}return settingsPromise;}
 const db=(table,options={})=>provider('/rest/v1/'+table,options);
 const rpc=(name,body,{token,admin=false}={})=>db('rpc/'+name,{method:'POST',body,token,admin});
 async function rate(req,scope,user=''){const ip=req.headers.get('x-nf-client-connection-ip')||'unknown';const key=createHmac('sha256',env.ACCOUNT_COOKIE_SECRET).update(scope+'|'+ip+'|'+user).digest('hex');if(!await rpc('consume_account_rate',{p_key:key,p_limit:scope==='auth'?12:120,p_seconds:scope==='auth'?900:60},{admin:true}))throw new AccountError('too_many_requests',429);}
 function csrf(req,headers){const c=cookies(req);let token=c[prefix+'csrf'];if(!token||!/^[a-zA-Z0-9_-]{43}$/.test(token)){token=randomBytes(32).toString('base64url');setCookie(headers,'csrf',token,86400);}return token;}
 function checkMutation(req){if(req.headers.get('origin')!==origin||!req.headers.get('content-type')?.startsWith('application/json'))throw new AccountError('request_rejected',403);const value=cookies(req)[prefix+'csrf'];if(!safeEqual(value,req.headers.get('x-account-csrf')))throw new AccountError('request_rejected',403);}
 const claims=token=>{try{return JSON.parse(Buffer.from(token.split('.')[1],'base64url'));}catch{throw new AccountError('session_expired',401);}};
 async function verified(token){const user=await provider('/auth/v1/user',{token});const jwt=claims(token);if(!user?.id||user.id!==jwt.sub||!uuid(jwt.session_id)||jwt.exp*1000<=Date.now())throw new AccountError('session_expired',401);return {user,jwt,token};}
 function tokens(headers,result){if(!result?.access_token||!result?.refresh_token)throw new AccountError('authentication_failed',401);setCookie(headers,'access',result.access_token,result.expires_in||3600);setCookie(headers,'refresh',result.refresh_token,60*60*24*30);}
 async function session(req,headers){ensure();const c=cookies(req);let token=c[prefix+'access'],v;
  try{if(token)v=await verified(token);}catch(e){if(e.status!==401)throw e;}
  if(!v&&c[prefix+'refresh']){try{const result=await provider('/auth/v1/token?grant_type=refresh_token',{method:'POST',body:{refresh_token:c[prefix+'refresh']}});v=await verified(result.access_token);tokens(headers,result);}catch(e){if(e.status===503||e.status===429)throw e;clear(headers);throw new AccountError('session_expired',401);}}
  if(!v)throw new AccountError('sign_in_required',401);
  const rows=await db('account_sessions?select=id,created_at,last_seen_at&user_id=eq.'+v.user.id+'&id=eq.'+v.jwt.session_id+'&revoked_at=is.null',{admin:true});if(!rows?.length){clear(headers);throw new AccountError('session_expired',401);}
  v.mfaRequired=!!v.user.factors?.some(f=>f.status==='verified')&&v.jwt.aal!=='aal2';
  if(Date.now()-Date.parse(rows[0].last_seen_at)>300000)await db('account_sessions?id=eq.'+v.jwt.session_id+'&user_id=eq.'+v.user.id,{method:'PATCH',body:{last_seen_at:new Date().toISOString()},admin:true});
  return v;
 }
 const recent=(req,s)=>{const r=unsign(cookies(req)[prefix+'reauth']);if(!r||r.uid!==s.user.id||r.sid!==s.jwt.session_id)throw new AccountError('reauthentication_required',403);};
 const markRecent=(headers,s)=>setCookie(headers,'reauth',sign({uid:s.user.id,sid:s.jwt.session_id,exp:Date.now()+300000}),300);
 async function complete(req,headers,result,{recent=false,expectedUser}={}){const s=await verified(result.access_token);if(expectedUser&&s.user.id!==expectedUser)throw new AccountError('authentication_failed',401);if(!s.user.email_confirmed_at)throw new AccountError('authentication_failed',401);const ok=await rpc('register_account_session',{p_user:s.user.id,p_session:s.jwt.session_id,p_browser:(req.headers.get('user-agent')||'Browser').slice(0,160)},{admin:true});if(!ok)throw new AccountError('session_expired',401);await audit(s.user.id,'successful_sign_in',true);tokens(headers,result);if(recent)markRecent(headers,s);return s;}
 const audit=(user,event,success)=>rpc('record_account_security',{p_user:user,p_event:event,p_success:success},{admin:true});
 function beginOAuth(req,headers,next){const verifier=randomBytes(48).toString('base64url'),challenge=createHash('sha256').update(verifier).digest('base64url');setCookie(headers,'flow',sign({verifier,next:internalPath(next),exp:Date.now()+600000}),600);const u=new URL(base+'/auth/v1/authorize');for(const [k,v]of Object.entries({provider:'google',redirect_to:origin+'/auth/callback/',code_challenge:challenge,code_challenge_method:'s256'}))u.searchParams.set(k,v);return u.href;}
 async function finishOAuth(req,headers,code){const flow=unsign(cookies(req)[prefix+'flow']);if(!flow?.verifier||typeof code!=='string'||code.length>2048)throw new AccountError('invalid_auth_link');const result=await provider('/auth/v1/token?grant_type=pkce',{method:'POST',body:{auth_code:code,code_verifier:flow.verifier}});const s=await complete(req,headers,result,{expectedUser:flow.uid});setCookie(headers,'flow','',0);return {s,next:flow.next};}
 async function beginIdentityLink(req,headers,s){recent(req,s);const settings=await authSettings();if(!settings.external?.google)throw new AccountError('google_not_configured',503);const verifier=randomBytes(48).toString('base64url'),challenge=createHash('sha256').update(verifier).digest('base64url');const q=new URLSearchParams({provider:'google',redirect_to:origin+'/auth/callback/',code_challenge:challenge,code_challenge_method:'s256',skip_http_redirect:'true'});let result;try{result=await provider('/auth/v1/user/identities/authorize?'+q,{token:s.token});}catch(error){if(error.providerCode==='manual_linking_disabled')throw new AccountError('identity_linking_unavailable',503);throw error;}const url=safeURL(result?.url);setCookie(headers,'flow',sign({verifier,uid:s.user.id,next:'/account/?view=connections',exp:Date.now()+600000}),600);return {url};}
 async function staff(s){if(s.jwt.aal!=='aal2')throw new AccountError('admin_mfa_required',403);const rows=await db('staff_roles?select=role&user_id=eq.'+s.user.id,{token:s.token});if(!rows?.length)throw new AccountError('not_authorized',403);return rows[0].role;}
 return {configured,origin,base,ensure,provider,authSettings,db,rpc,rate,csrf,checkMutation,session,complete,tokens,clear,recent,markRecent,audit,beginOAuth,finishOAuth,beginIdentityLink,staff,cookies,prefix,env};
}
