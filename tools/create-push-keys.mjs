import {createECDH} from 'node:crypto';
import fs from 'node:fs/promises';
const key=createECDH('prime256v1');key.generateKeys();
const file=new URL('../.env.local',import.meta.url),existing=await fs.readFile(file,'utf8').catch(()=> '');
if(/WEB_PUSH_PRIVATE_KEY=/.test(existing))throw Error('Push keys already exist; do not rotate keys for active subscriptions.');
await fs.appendFile(file,'\nWEB_PUSH_PUBLIC_KEY='+key.getPublicKey().toString('base64url')+'\nWEB_PUSH_PRIVATE_KEY='+key.getPrivateKey().toString('base64url')+'\nWEB_PUSH_SUBJECT=https://electrolindia.netlify.app\n');
console.log('Push keys written to private local configuration.');
