import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=async p=>JSON.parse(await fs.readFile(path.join(root,p),'utf8'));
const index=await read('data/profile-index.json'),catalog=await read('data/catalog.json'),entry=catalog.find(d=>d.level==='lok'&&d.state==='All India'&&d.year===2024),election=await read(entry.file);
const profiles=await Promise.all(index.map(p=>read(p.file)));
const norm=s=>String(s||'').toLowerCase().replace(/\((?:sc|st)\)/g,'').replace(/\b(shri|smt|shrimati|dr|adv|prof|mr|mrs|ms|km|and|nct of)\b\.?/g,'').replace(/[^\p{L}\p{N}]/gu,'');
const place=s=>norm(s).replace(/^dadar/,'dadra');
const links={},used=new Set(),unavailable=[];
for(const seat of election.seats){const winner=seat.c.find(c=>election.parties[c[1]].short!=='NOTA');let matches=profiles.filter(m=>norm(m.state)===norm(seat.state)&&norm(m.name)===norm(winner[0]));
 if(matches.length!==1)matches=profiles.filter(m=>norm(m.name)===norm(winner[0]));
 if(matches.length!==1)matches=profiles.filter(m=>norm(m.state)===norm(seat.state)&&[m.constituency,m.matched_pc].some(n=>place(n)===place(seat.t))&&m.positions?.some(p=>/2024/.test(p.period||'')&&/Elected.*18th/i.test(p.position||'')));
 if(matches.length===1){used.add(matches[0].id);links[seat.state+'|'+seat.n]=matches[0].id;}else unavailable.push({state:seat.state,seat:seat.t});
}
if(unavailable.length)throw Error('Unmatched historical winners: '+JSON.stringify(unavailable));
await fs.writeFile(path.join(root,'js/html-profile-seats.js'),'/* MP IDs joined from source names, matched constituencies and dated 2024 election histories. */\nwindow.ELECTROL_PROFILE_SEATS='+JSON.stringify(links)+';\n');
console.log(JSON.stringify({sourceBiographies:profiles.length,matchedWinnerPhotos:used.size,unavailable}));
