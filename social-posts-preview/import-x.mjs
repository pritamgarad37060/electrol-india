import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
export function last30Days(now=new Date()){
 const end=new Date(now.getTime()-30000),start=new Date(end);start.setUTCDate(start.getUTCDate()-30);
 return {start:start.toISOString(),end:end.toISOString()};
}
export class XError extends Error{constructor(status){super(status===401?'X rejected the API token.':status===403?'This X app does not have access to the requested endpoint.':status===429?'X rate limit reached. Retry later.':status===402?'X credits are required.':status===404?'X account unavailable.':'X request failed (HTTP '+status+').');this.status=status;}}
export async function requestX(url,{token,fetcher=fetch}){
 const u=new URL(url);if(u.origin!=='https://api.x.com')throw Error('Unexpected API destination.');
 const r=await fetcher(u,{headers:{Authorization:'Bearer '+token},redirect:'error',signal:AbortSignal.timeout(25000)});
 if(!r.ok)throw new XError(r.status);
 return r.json();
}
export function normalizePost(row,person,userId,media=[],period){
 if(String(row.author_id)!==String(userId)||!/^\d+$/.test(row.id)||typeof row.text!=='string'||!Number.isFinite(Date.parse(row.created_at)))throw Error('X returned a post that does not match this account.');
 const createdAt=new Date(row.created_at).toISOString();if(createdAt<period.start||createdAt>=period.end)return null;
 const refs=row.referenced_tweets||[];
 return {id:row.id,personId:person.id,authorId:String(userId),createdAt,text:row.note_tweet?.text||row.text,url:'https://x.com/'+person.handle+'/status/'+row.id,kind:refs.find(r=>r.type==='retweeted')?.type||refs.find(r=>r.type==='replied_to')?.type||refs.find(r=>r.type==='quoted')?.type||'post',media:(row.attachments?.media_keys||[]).map(k=>media.find(m=>m.media_key===k)).filter(Boolean).map(m=>({type:m.type,url:m.url||'',preview:m.preview_image_url||'',alt:m.alt_text||''}))};
}
export async function importAccount(person,{token,period,maxPages=50,fetcher=fetch,pause=()=>Promise.resolve()}){
 const get=url=>requestX(url,{token,fetcher});
 const lookup=await get('https://api.x.com/2/users/by/username/'+encodeURIComponent(person.handle)+'?user.fields=protected');
 const user=lookup.data;if(!user?.id||user.username?.toLowerCase()!==person.handle.toLowerCase())throw Error('X account lookup did not match the recorded handle.');
 if(user.protected)return {posts:[],coverage:{personId:person.id,handle:person.handle,status:'unavailable',count:0,note:'Protected account; no public archive imported.'}};
 const posts=new Map();let cursor;const cursors=new Set();let pages=0,problem='';
 do{
  const url=new URL('https://api.x.com/2/tweets/search/all');
  const params={query:'from:'+person.handle,start_time:period.start,end_time:period.end,max_results:'100','tweet.fields':'id,text,author_id,created_at,attachments,referenced_tweets,note_tweet',expansions:'attachments.media_keys','media.fields':'media_key,type,url,preview_image_url,alt_text'};
  if(cursor)params.next_token=cursor;url.search=new URLSearchParams(params).toString();
  let data;
  try{data=await get(url.href);}catch(e){if(posts.size)return {posts:[...posts.values()],coverage:{personId:person.id,handle:person.handle,accountId:user.id,status:'partial',count:posts.size,pages,note:e.message}};throw e;}
  pages++;
  for(const row of data.data||[]){const normalized=normalizePost(row,person,user.id,data.includes?.media||[],period);if(normalized)posts.set(normalized.id,normalized);}
  if(data.errors?.length)problem='X reported partial errors in its response.';
  cursor=data.meta?.next_token;
  if(cursor){if(cursors.has(cursor)){problem='X returned a repeated pagination token.';break;}cursors.add(cursor);}
  if(cursor&&pages<maxPages)await pause();
 }while(cursor&&pages<maxPages);
 return {posts:[...posts.values()],coverage:{personId:person.id,handle:person.handle,accountId:user.id,status:cursor||problem?'partial':'complete',count:posts.size,pages,note:problem||(cursor?'Page limit reached; increase --max-pages to continue a fresh full import.':'Finished pagination of the public posts returned by X. Deleted, protected, withheld, or unindexed content is not included.')}};
}
export async function run({token=process.env.X_BEARER_TOKEN,fetcher=fetch,maxPages=50,now=new Date(),limit=100,write=true,pause=()=>new Promise(resolve=>setTimeout(resolve,1100))}={}){
 if(!token){console.error('X_BEARER_TOKEN is not configured. No X requests were made. Set the token in this terminal, then run this importer. Do not put it in the HTML.');return {configured:false};}
 const people=JSON.parse(await fs.readFile(path.join(here,'representatives.json'),'utf8')).slice(0,limit);
 const period=last30Days(now),output={schema:1,fetchedAt:null,range:period,method:'X API v2 full-archive search',posts:[],coverage:[],note:'Public posts returned by the official X search index. No guarantee for deleted, protected, withheld, unindexed content, or repost completeness.'};
 for(const person of people){
  try{const result=await importAccount(person,{token,period,maxPages,fetcher,pause});output.posts.push(...result.posts);output.coverage.push(result.coverage);console.log(person.name+': '+result.coverage.status+' ('+result.posts.length+' posts)');}
  catch(e){output.coverage.push({personId:person.id,handle:person.handle,status:'unavailable',count:0,note:e instanceof XError?e.message:'The account could not be imported or its response failed validation.'});console.log(person.name+': unavailable');
   if(e instanceof XError&&[401,402,403,429].includes(e.status)){for(const p of people.slice(output.coverage.length))output.coverage.push({personId:p.id,handle:p.handle,status:'not_attempted',count:0,note:'Import stopped: '+e.message});break;}
  }
  // Checkpoint after every account: interrupted imports are always marked incomplete.
  if(write){output.fetchedAt=new Date().toISOString();await fs.writeFile(path.join(here,'posts.json'),JSON.stringify(output));}
  await pause();
 }
 output.fetchedAt=new Date().toISOString();output.posts.sort((a,b)=>b.createdAt.localeCompare(a.createdAt));
 if(write)await fs.writeFile(path.join(here,'posts.json'),JSON.stringify(output));
 return output;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const maxIndex=process.argv.indexOf('--max-pages'),limitIndex=process.argv.indexOf('--limit');
 const maxPages=maxIndex>=0?Number(process.argv[maxIndex+1]):50,limit=limitIndex>=0?Number(process.argv[limitIndex+1]):100;
 if(!Number.isInteger(maxPages)||maxPages<1||maxPages>1000||!Number.isInteger(limit)||limit<1||limit>100)throw Error('Use --max-pages 1..1000 and --limit 1..100.');
 const result=await run({maxPages,limit});
 if(result.configured===false)process.exitCode=2;
 else {const {build}=await import('./build.mjs');await build();console.log(JSON.stringify({posts:result.posts.length,complete:result.coverage.filter(c=>c.status==='complete').length,accounts:result.coverage.length,window:result.range}));}
}
