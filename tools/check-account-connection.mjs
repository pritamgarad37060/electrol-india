import './local-account-env.mjs';
import {createAccountService} from '../netlify/lib/account-core.mjs';
const required=['SITE_URL','SUPABASE_URL','ACCOUNT_COOKIE_SECRET'];
const missing=required.filter(k=>!process.env[k]);
if(!process.env.SUPABASE_PUBLISHABLE_KEY&&!process.env.SUPABASE_ANON_KEY)missing.push('SUPABASE_PUBLISHABLE_KEY');
if(!process.env.SUPABASE_SECRET_KEY&&!process.env.SUPABASE_SERVICE_ROLE_KEY)missing.push('SUPABASE_SECRET_KEY');
if(missing.length){console.error('Missing server configuration: '+missing.join(', '));process.exitCode=1;}
else{try{const s=createAccountService();s.ensure();const settings=await s.provider('/auth/v1/settings');const entities=await s.db('followable_entities?select=id&limit=1');await s.db('notification_deliveries?select=lease_id&limit=0',{admin:true});console.log(JSON.stringify({databaseReachable:true,emailVerificationRequired:!settings.mailer_autoconfirm,googleEnabled:!!settings.external?.google,entityCatalogPresent:!!entities.length,jobsSchemaPresent:true}));}catch(e){console.error('Connection check failed: '+(e.code||'service_unavailable'));process.exitCode=1;}}
