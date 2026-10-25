import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {parseEnv} from 'node:util';
import path from 'node:path';
import {inside,root} from './lib.mjs';
const local=Object.assign({},...[path.join(root,'..','.env'),inside('.env')].filter(existsSync).map(f=>parseEnv(readFileSync(f,'utf8'))));
const key=process.env.ELEVENLABS_API_KEY||local.ELEVENLABS_API_KEY;
if(!key)throw Error('Missing local credential.');
const id='d3MFdIuCfbAIwiu7jC4a';
const headers={'xi-api-key':key,'Content-Type':'application/json'};
const r=await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${id}/with-timestamps?output_format=mp3_44100_128`,{method:'POST',headers,body:JSON.stringify({text:'What if a microscope knew when to look?',model_id:'eleven_multilingual_v2',voice_settings:{stability:0.45,similarity_boost:0.75,style:0.15,speed:1.0}}),signal:AbortSignal.timeout(120000)});
mkdirSync(inside('public/audio/generated/anya-audition'),{recursive:true});
if(!r.ok){const body=await r.json().catch(()=>({}));const details=body.detail;console.log(JSON.stringify({status:r.status,providerStatus:details?.status,message:details?.message||'Voice request unavailable'}));writeFileSync(inside('.cache/selected-voice-result.json'),JSON.stringify({status:r.status,providerStatus:details?.status,message:details?.message||'Voice request unavailable'},null,2));process.exitCode=1;}
else{const response=await r.json();writeFileSync(inside('public/audio/generated/anya-audition/hook.mp3'),Buffer.from(response.audio_base64,'base64'));const {audio_base64,...metadata}=response;void audio_base64;writeFileSync(inside('public/audio/generated/anya-audition/hook.response.json'),JSON.stringify(metadata,null,2));console.log('Selected voice audition generated; no automatic full pass or subscription change.');}
