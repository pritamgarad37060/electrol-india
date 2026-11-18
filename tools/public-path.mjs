import path from 'node:path';
export function publicFile(root,pathname){
 const group=pathname.split('/')[1];if(!['js','css','data','assets'].includes(group))return null;
 const allowed=path.join(root,group)+path.sep,file=path.resolve(root,'.'+pathname);return file.startsWith(allowed)?file:null;
}
