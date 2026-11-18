export async function publicDataHandler(request,{env=process.env,fetcher=fetch}={}){
 const headers={'Content-Type':'application/json; charset=utf-8','X-Content-Type-Options':'nosniff','Cache-Control':'public, max-age=300, stale-while-revalidate=86400'};
 const response=(body,status=200,extra={})=>new Response(request.method==='HEAD'?null:JSON.stringify(body),{status,headers:{...headers,...extra}});
 if(!['GET','HEAD'].includes(request.method))return response({error:'method_not_allowed'},405,{Allow:'GET, HEAD'});
 const id=new URL(request.url).searchParams.get('path')||'';
 if(!/^\/data\/[a-zA-Z0-9_./-]+\.json$/.test(id)||id.includes('..')||id.length>250)return response({error:'invalid_dataset'},400);
 const key=env.SUPABASE_PUBLISHABLE_KEY||env.SUPABASE_ANON_KEY;if(!env.SUPABASE_URL||!key)return response({error:'data_not_configured'},503,{'Cache-Control':'no-store'});
 try{const upstream=await fetcher(env.SUPABASE_URL+'/rest/v1/website_datasets?path=eq.'+encodeURIComponent(id)+'&select=content,checksum&limit=1',{headers:{apikey:key},signal:AbortSignal.timeout(8000)});if(!upstream.ok)throw Error();const [row]=await upstream.json();if(!row)return response({error:'dataset_not_found'},404);const etag='"'+row.checksum+'"';if(request.headers.get('if-none-match')===etag)return new Response(null,{status:304,headers:{...headers,ETag:etag}});return response(row.content,200,{ETag:etag});}catch{return response({error:'data_temporarily_unavailable'},503,{'Cache-Control':'no-store'});}
}
export default request=>publicDataHandler(request);
