// Offline evidence container: built-in Node modules only. Never runs generated programs.
import {readFileSync,writeFileSync,mkdirSync,readdirSync,lstatSync} from 'node:fs';
import {resolve,join,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash,scryptSync,randomBytes,createCipheriv,createDecipheriv} from 'node:crypto';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createInterface} from 'node:readline';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const sha=b=>createHash('sha256').update(b).digest('hex');
const password='agent-recovery-case-study-public-artifact-v1';
const salt='appworld-derived-evidence-2026-10-23';
const key=scryptSync(password,salt,32);
export function encode(data){
 const nonce=randomBytes(12),c=createCipheriv('aes-256-gcm',key,nonce);
 const body=Buffer.concat([c.update(gzipSync(data)),c.final()]);
 return Buffer.concat([Buffer.from('ARC1'),nonce,c.getAuthTag(),body]);
}
export function decode(data){
 if(data.length<32||data.subarray(0,4).toString()!=='ARC1')throw Error('Invalid container');
 const c=createDecipheriv('aes-256-gcm',key,data.subarray(4,16));c.setAuthTag(data.subarray(16,32));
 return gunzipSync(Buffer.concat([c.update(data.subarray(32)),c.final()]),{maxOutputLength:128*1024*1024});
}
function safe(p){if(typeof p!=='string'||!p||p.startsWith('/')||p.includes('\\')||p.split('/').some(s=>s===''||s==='.'||s==='..'))throw Error('Unsafe evidence path');return p;}
if(process.argv[2]==='pack'){
 const lab=resolve(process.argv[3]),files={},seen=new Set();let logicalBytes=0,storedBytes=0;
 const skip=new Set(['node_modules','.venv','.git','__pycache__','dist','.DS_Store','.env']);
 const env=readFileSync(join(lab,'.env'),'utf8');
 const secrets=env.split('\n').filter(s=>/^[A-Z_]*(?:KEY|TOKEN)=/.test(s)).map(s=>s.slice(s.indexOf('=')+1).trim().replace(/^['"]|['"]$/g,'')).filter(s=>s.length>12);
 function visit(dir){for(const d of readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
  if(skip.has(d.name)||d.name.startsWith('.env.'))continue;
  const f=join(dir,d.name),st=lstatSync(f);if(st.isSymbolicLink())continue;if(st.isDirectory()){visit(f);continue;}if(!st.isFile())throw Error('Unsupported file');
  const path=safe(relative(lab,f)),b=readFileSync(f);
  if(secrets.some(s=>b.includes(Buffer.from(s))))throw Error('Credential detected in selected file: '+path);
  const h=sha(b);files[path]={sha256:h,bytes:b.length};logicalBytes+=b.length;
  if(!seen.has(h)){const e=encode(b);writeFileSync(join(root,'evidence/blobs',h+'.bin'),e);seen.add(h);storedBytes+=e.length;}
 }}
 visit(lab);
 const manifest={format:1,originalRoot:lab,files};
 const b=encode(Buffer.from(JSON.stringify(manifest)));writeFileSync(join(root,'evidence/manifest.bin'),b);
 const catalog={format:1,createdAt:new Date().toISOString(),encryption:'AES-256-GCM over gzip; scrypt key derivation',publicPassphrase:password,salt,manifestSha256:sha(b),logicalFiles:Object.keys(files).length,uniqueBlobs:seen.size,logicalBytes,storedBytes};
 writeFileSync(join(root,'evidence/catalog.json'),JSON.stringify(catalog,null,2)+'\n');console.log(JSON.stringify(catalog));
}else if(process.argv[2]==='serve'){
 const catalog=JSON.parse(readFileSync(join(root,'evidence/catalog.json'))),cipher=readFileSync(join(root,'evidence/manifest.bin'));
 if(sha(cipher)!==catalog.manifestSha256)throw Error('Manifest integrity failure');
 const manifest=JSON.parse(decode(cipher));
 const get=p=>{const item=manifest.files[safe(p)];if(!item||!(/^[a-f0-9]{64}$/.test(item.sha256)))throw Error('Unlisted evidence');const b=decode(readFileSync(join(root,'evidence/blobs',item.sha256+'.bin')));if(b.length!==item.bytes||sha(b)!==item.sha256)throw Error('Plaintext integrity failure');return b;};
 for await(const line of createInterface({input:process.stdin,crlfDelay:Infinity})){
  try{const q=JSON.parse(line);let result;
   if(q.op==='manifest')result=manifest;
   else if(q.op==='verify'){const unique=new Set();for(const [p,x] of Object.entries(manifest.files))if(!unique.has(x.sha256)){get(p);unique.add(x.sha256);}result={files:Object.keys(manifest.files).length,uniqueBlobs:unique.size};}
   else if(q.op==='get')result=get(q.path).toString('base64');
   else if(q.op==='extract'){
    const prefix=safe(q.prefix),out=resolve(q.out);let count=0;
    for(const p of Object.keys(manifest.files))if(p===prefix||p.startsWith(prefix+'/')){
     const sub=p===prefix?p.split('/').at(-1):p.slice(prefix.length+1);safe(sub);const dest=join(out,sub);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,get(p));count++;
    }if(!count)throw Error('Empty extraction');result={files:count};
   }else throw Error('Unknown operation');
   process.stdout.write(JSON.stringify({ok:true,result})+'\n');
  }catch(e){process.stdout.write(JSON.stringify({ok:false,error:String(e.message)})+'\n');}
 }
}
