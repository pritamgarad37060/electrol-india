import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {fetchFeed} from './collect-youtube.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
let data=JSON.parse(await fs.readFile(path.join(here,'youtube-data.json'),'utf8'));
let refreshing;let lastAttempt=0;const apiCache=new Map();
const key=process.env.YOUTUBE_API_KEY;
function person(id){const p=data.people.find(p=>p.id===id);if(!p){const e=Error('Unknown politician');e.status=404;throw e;}if(!p.youtube.channelId){const e=Error('Add a reviewed YouTube channel ID for this politician first.');e.status=409;throw e;}return p;}
async function api(endpoint,params){if(!key){const e=Error('Public feeds work without a key. Set YOUTUBE_API_KEY on the companion server for channel statistics, playlists and comments.');e.status=503;throw e;}const cacheKey=endpoint+JSON.stringify(params);const old=apiCache.get(cacheKey);if(old&&Date.now()-old.at<900000)return old.value;const u=new URL('https://www.googleapis.com/youtube/v3/'+endpoint);for(const [k,v]of Object.entries({...params,key}))u.searchParams.set(k,v);const r=await fetch(u,{signal:AbortSignal.timeout(20000)});const j=await r.json();if(!r.ok){const e=Error(j.error?.message||'YouTube API request failed');e.status=r.status;throw e;}apiCache.set(cacheKey,{at:Date.now(),value:j});return j;}
const duration=s=>{const m=s?.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);return m?[m[1],m[2]||'0',m[3]||'0'].filter((x,i)=>i>0||x).map((x,i)=>i?x.padStart(2,'0'):x).join(':'):s;};
function video(v){return {id:v.id,title:v.snippet.title,description:v.snippet.description,publishedAt:v.snippet.publishedAt,channelId:v.snippet.channelId,channelTitle:v.snippet.channelTitle,thumbnail:v.snippet.thumbnails?.high?.url||'https://i.ytimg.com/vi/'+v.id+'/hqdefault.jpg',views:v.statistics?.viewCount??null,likes:v.statistics?.likeCount??null,commentCount:v.statistics?.commentCount,duration:duration(v.contentDetails?.duration),definition:v.contentDetails?.definition,caption:v.contentDetails?.caption,liveBroadcastContent:v.snippet.liveBroadcastContent,embeddable:v.status?.embeddable,liveStreamingDetails:v.liveStreamingDetails};}
async function refresh(){if(refreshing)return refreshing;if(Date.now()-lastAttempt<900000)return;lastAttempt=Date.now();refreshing=(async()=>{let cursor=0;const failures=[];await Promise.all(Array.from({length:3},async()=>{while(cursor<data.people.length){const p=data.people[cursor++];if(!p.youtube.channelId)continue;try{const f=await fetchFeed(p.youtube.channelId,p.id);data.videos=data.videos.filter(v=>v.personId!==p.id).concat(f.videos);p.youtube.fetchedAt=new Date().toISOString();p.youtube.title=f.title;}catch(e){failures.push({personId:p.id,error:e.message});}}}));data.fetchedAt=new Date().toISOString();data.failures=failures;await fs.writeFile(path.join(here,'youtube-data.json'),JSON.stringify(data));})().finally(()=>refreshing=null);return refreshing;}
const server=http.createServer(async(req,res)=>{
 const u=new URL(req.url,'http://localhost');const origin=req.headers.origin;
 // Local standalone HTML can read public data. No credentials/cookies are accepted.
 if(origin==='null'||/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin||''))res.setHeader('Access-Control-Allow-Origin',origin);
 res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Cache-Control','no-store');
 const send=(status,j)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify(j));};
 if(req.method!=='GET'){send(405,{error:'GET only'});return;}
 try{
  if(u.pathname==='/'||u.pathname==='/electrol-social-posts.html'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(await fs.readFile(path.join(here,'electrol-social-posts.html')));return;}
  if(u.pathname==='/api/youtube/data'){if(u.searchParams.has('refresh'))refresh().catch(()=>{});send(200,{...data,refreshing:!!refreshing});return;}
  if(u.pathname==='/api/youtube/details'){const p=person(u.searchParams.get('person'));const c=(await api('channels',{part:'snippet,statistics,contentDetails,brandingSettings',id:p.youtube.channelId})).items?.[0];if(!c)throw Error('Channel unavailable');const ids=data.videos.filter(v=>v.personId===p.id).slice(0,50).map(v=>v.id);const rows=ids.length?(await api('videos',{part:'snippet,statistics,contentDetails,status,liveStreamingDetails',id:ids.join(',')})).items:[];send(200,{channel:{title:c.snippet.title,description:c.snippet.description,publishedAt:c.snippet.publishedAt,country:c.snippet.country,subscriberCount:c.statistics.hiddenSubscriberCount?null:c.statistics.subscriberCount,viewCount:c.statistics.viewCount,videoCount:c.statistics.videoCount,banner:c.brandingSettings?.image?.bannerExternalUrl},videos:rows.map(video)});return;}
  if(u.pathname==='/api/youtube/playlists'){const p=person(u.searchParams.get('person'));const page=u.searchParams.get('page');const j=await api('playlists',{part:'snippet,contentDetails',channelId:p.youtube.channelId,maxResults:20,...(page?{pageToken:page}:{})});send(200,{items:j.items.map(x=>({id:x.id,title:x.snippet.title,description:x.snippet.description,itemCount:x.contentDetails.itemCount})),nextPageToken:j.nextPageToken});return;}
  if(u.pathname==='/api/youtube/video'){const id=u.searchParams.get('id');if(!data.videos.some(v=>v.id===id)){send(404,{error:'Video not in this directory'});return;}const v=(await api('videos',{part:'snippet,statistics,contentDetails,status,liveStreamingDetails',id})).items?.[0];if(!v)throw Error('Video unavailable');let comments=[],commentError='';try{const j=await api('commentThreads',{part:'snippet',videoId:id,maxResults:10,textFormat:'plainText',order:'relevance'});comments=j.items.map(x=>({author:x.snippet.topLevelComment.snippet.authorDisplayName,text:x.snippet.topLevelComment.snippet.textDisplay}));}catch(e){commentError=e.message;}send(200,{video:video(v),comments,commentError});return;}
  send(404,{error:'Not found'});
 }catch(e){send(e.status||502,{error:e.message});}
});
const port=Number(process.env.SOCIAL_PREVIEW_PORT||8125);server.listen(port,'127.0.0.1',()=>console.log('Electrol YouTube: http://127.0.0.1:'+port));
const timer=setInterval(()=>refresh().catch(()=>{}),15*60*1000);timer.unref();
