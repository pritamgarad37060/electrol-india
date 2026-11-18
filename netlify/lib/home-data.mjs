import {AccountError} from './account-core.mjs';
const catalogs=new WeakMap();

async function readAll(service,query){
 const rows=[];
 // PostgREST caps each response; don't let the first page silently hide an area.
 for(let offset=0;offset<20000;offset+=1000){const page=await service.db(query+'&limit=1000&offset='+offset);rows.push(...page);if(page.length<1000)return rows;}
 throw new AccountError('service_unavailable',503);
}

// Public reads use the existing anonymous role and RLS. Never expose private activity.
export async function homeData(service,req,fetcher=fetch){
 const u=new URL(req.url),action=u.pathname.split('/').at(-1);
 if(req.method!=='GET'||!['home-data','home-location','home-discover'].includes(action))return;
 await service.rate(req,'catalog');
 if(action==='home-location'){
  const lat=Number(u.searchParams.get('lat')),lon=Number(u.searchParams.get('lon'));
  if(!u.searchParams.has('lat')||!u.searchParams.has('lon')||!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)throw new AccountError('invalid_input');
  // Coordinates are used for this request only; never stored in the account or a URL log in our database.
  const url=new URL('https://nominatim.openstreetmap.org/reverse');
  url.search=new URLSearchParams({format:'jsonv2',lat:String(lat),lon:String(lon),zoom:'10','accept-language':'en'});
  const response=await fetcher(url,{headers:{'User-Agent':'ElectrolIndia/2.0 (location lookup)','Accept':'application/json'},signal:AbortSignal.timeout(8000)});
  if(!response.ok)throw new AccountError('service_unavailable',503);
  const data=await response.json(),a=data.address||{};
  if(a.country_code!=='in')return {location:null};
  // Residential city/district names are deliberately not converted to electoral constituencies.
  return {location:{state:a.state||'',district:a.state_district||'',city:a.city||a.town||a.village||''}};
 }
 if(action==='home-discover'){
  const kind=u.searchParams.get('kind'),parent=u.searchParams.get('parent');
  if(!['person','constituency'].includes(kind)||parent&&!/^[A-Za-z0-9:|%._-]{1,240}$/.test(parent))throw new AccountError('invalid_input');
  return {rows:await service.db('followable_entities?active=eq.true&kind=eq.'+kind+(parent?'&parent_id=eq.'+encodeURIComponent(parent):'')+'&order=name.asc&limit=60')};
 }
 const cached=catalogs.get(service);if(cached&&cached.until>Date.now())return cached.promise;
 const promise=Promise.all([
  readAll(service,'followable_entities?active=eq.true&kind=eq.election&order=id.asc'),
  readAll(service,'scheduled_elections?approved=eq.true&order=event_at.asc,id.asc'),
  readAll(service,'followable_entities?active=eq.true&kind=in.(country,state,district,city,body)&order=id.asc')
 ]).then(([entities,schedule,locations])=>({entities,schedule,locations,trending:[]})).catch(error=>{catalogs.delete(service);throw error;});
 catalogs.set(service,{until:Date.now()+60000,promise});return promise;
}
