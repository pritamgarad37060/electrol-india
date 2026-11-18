import fs from 'node:fs/promises';
import {uid} from './build-identities.mjs';

// Repair identifiers without changing established identities or public URLs.
export async function repairIdentities(){
 let changed=0;
 for(const file of ['data/people-directory.json','data/representatives-index.json']){
  const value=JSON.parse(await fs.readFile(file,'utf8'));
  const seen=new Set();let dirty=false;
  for(const row of value.rows){
   if(!row.key)throw Error('A representative has no source key: '+row.name);
   if(!row.person_uid){row.person_uid=uid('representative\u001f'+row.key);row.identity_status='source-scoped';changed++;dirty=true;}
   if(seen.has(row.person_uid))throw Error('Duplicate representative identifier: '+row.person_uid);
   seen.add(row.person_uid);
  }
  if(dirty)await fs.writeFile(file,JSON.stringify(value));
 }
 return changed;
}

export async function repairPartyNames(){
 const file='data/party-directory.json',directory=JSON.parse(await fs.readFile(file,'utf8'));
 const known=[...directory.parties.filter(p=>p.name&&p.name!==p.code),...JSON.parse(await fs.readFile('data/party-profile-index.json','utf8')),...JSON.parse(await fs.readFile('data/party-background.json','utf8')),...JSON.parse(await fs.readFile('data/party-name-overrides.json','utf8'))];
 const normalize=code=>String(code||'').toUpperCase().replace(/[^A-Z0-9]/g,'');
 const names=new Map();
 for(const p of known)for(const code of [p.code,p.short]){if(!code)continue;const key=normalize(code);if(!names.has(key))names.set(key,new Map());names.get(key).set(p.name,p);}
 let expanded=0;
 for(const p of directory.parties){
  if(p.name===p.code){const options=names.get(normalize(p.code));if(options?.size===1){const source=[...options.values()][0];p.name=source.name;p.name_source=source.source||source.file||null;expanded++;}}
  p.name_status=p.name===p.code?'code-only':'expanded';
 }
 await fs.writeFile(file,JSON.stringify(directory));return {expanded,codeOnly:directory.parties.filter(p=>p.name_status==='code-only').length};
}
if(process.argv[1]?.endsWith('repair-data-quality.mjs'))console.log(JSON.stringify({repairedRepresentativeIds:await repairIdentities(),partyNames:await repairPartyNames()}));
