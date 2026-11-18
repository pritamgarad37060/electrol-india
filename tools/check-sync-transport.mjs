import assert from 'node:assert/strict';
import {sync} from './sync-public-data.mjs';
const originalFetch=globalThis.fetch,originalLog=console.log;
const previousURL=process.env.SUPABASE_URL,previousKey=process.env.SUPABASE_SECRET_KEY;
const remote=new Map();let posts=0;
process.env.SUPABASE_URL='https://fixture.invalid';
process.env.SUPABASE_SECRET_KEY='sb_secret_fixture';
try{
 globalThis.fetch=async (url,options)=>{
  const u=new URL(url);
  if(options.method==='POST'){
   assert.equal(options.headers.Prefer,'resolution=merge-duplicates,return=minimal');
   for(const row of JSON.parse(options.body))remote.set(row.path,row.checksum);
   posts++;
   // PostgREST can return 201 Created with no representation for an upsert.
   return new Response(null,{status:201});
  }
  const offset=Number(u.searchParams.get('offset')||0),limit=Number(u.searchParams.get('limit')||500);
  return Response.json([...remote].sort(([a],[b])=>a.localeCompare(b)).slice(offset,offset+limit).map(([path,checksum])=>({path,checksum})));
 };
 console.log=()=>{};
 const first=await sync('push');assert(first.changed>0);assert(first.verified);assert.equal(remote.size,first.localDatasets);
 const firstPosts=posts,second=await sync('push');assert.equal(second.changed,0);assert.equal(posts,firstPosts);
 assert.equal((await sync('verify')).verified,true);
 for(const status of [200,204]){
  globalThis.fetch=async()=>new Response(null,{status});
  if(status===204)await assert.rejects(()=>sync('verify'),/invalid dataset index/);
  else await assert.rejects(()=>sync('verify'),/empty JSON response/);
 }
 originalLog(JSON.stringify({empty201Upsert:'passed',allLocalDatasets:first.localDatasets,checksumVerification:'passed',rerunSkipsUploadedDatasets:'passed',emptyReadResponse:'passed'}));
}finally{
 globalThis.fetch=originalFetch;console.log=originalLog;
 if(previousURL===undefined)delete process.env.SUPABASE_URL;else process.env.SUPABASE_URL=previousURL;
 if(previousKey===undefined)delete process.env.SUPABASE_SECRET_KEY;else process.env.SUPABASE_SECRET_KEY=previousKey;
}
