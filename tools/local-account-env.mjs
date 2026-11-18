import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

// Local server configuration only. Existing process variables take precedence.
// This module must never be imported by frontend code or the production function.
export function loadLocalAccountEnv({env=process.env,directory=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..')}={}){
 const allowed=/^(WEB_PUSH_PUBLIC_KEY|WEB_PUSH_PRIVATE_KEY|WEB_PUSH_SUBJECT|SITE_URL|SUPABASE_URL|SUPABASE_PUBLISHABLE_KEY|SUPABASE_ANON_KEY|SUPABASE_SECRET_KEY|SUPABASE_SERVICE_ROLE_KEY|ACCOUNT_COOKIE_SECRET|ACCOUNT_ALLOW_LOCAL|RESEND_API_KEY|ACCOUNT_EMAIL_FROM|ACCOUNT_SOURCE_HOSTS)$/;
 for(const file of ['.env.local','.env']){
  const target=path.join(directory,file);if(!fs.existsSync(target))continue;
  for(const line of fs.readFileSync(target,'utf8').split(/\r?\n/)){
   const match=line.match(/^\s*(?:export\s+)?([A-Z_]+)\s*=\s*(.*?)\s*$/);if(!match||!allowed.test(match[1])||env[match[1]])continue;
   let value=match[2];if(/^(["']).*\1$/.test(value))value=value.slice(1,-1);else value=value.replace(/\s+#.*$/,'').trim();
   if(value)env[match[1]]=value;
  }
 }
 return env;
}
loadLocalAccountEnv();
