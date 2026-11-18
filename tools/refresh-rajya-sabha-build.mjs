// Refresh only the changed static assets; election pages and routes stay intact.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {brotliCompressSync,gzipSync,constants} from 'node:zlib';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const files=['js/html-directories.js','js/html-profiles.js','js/html-profile-seats.js','data/people-directory.json','data/representatives-index.json','data/rajya-sabha-index.json','data/profile-index.json'];
async function collect(dir){for(const entry of await fs.readdir(path.join(root,dir),{withFileTypes:true})){const file=dir+'/'+entry.name;if(entry.isDirectory())await collect(file);else files.push(file);}}
for(const dir of ['data/public-profiles','data/photos','data/parliament'])await collect(dir);
for(const file of files){const body=await fs.readFile(path.join(root,file)),destination=path.join(root,'dist',file);await fs.mkdir(path.dirname(destination),{recursive:true});await fs.writeFile(destination,body);if(/\.(js|json)$/.test(file)){await fs.writeFile(destination+'.br',brotliCompressSync(body,{params:{[constants.BROTLI_PARAM_QUALITY]:5}}));await fs.writeFile(destination+'.gz',gzipSync(body));}}
console.log(JSON.stringify({updatedBuildAssets:files.length,existingElectionRoutes:'preserved'}));
