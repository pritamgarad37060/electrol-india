import fs from 'node:fs/promises';import path from 'node:path';
const root=path.resolve(process.argv[2]||'.');let checked=0;
async function visit(dir){for(const e of await fs.readdir(dir,{withFileTypes:true})){const file=path.join(dir,e.name);if(e.isDirectory())await visit(file);else if(e.name.endsWith('.json')){JSON.parse(await fs.readFile(file,'utf8'));checked++;}}}
await visit(path.join(root,'data'));console.log('Validated '+checked+' public JSON files.');
