import {writeFileSync,readFileSync,existsSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {inside,readJson,ffmpeg} from './lib.mjs';
const sourcePage='https://mixkit.co/free-stock-music/tag/technology/';
const html=await(await fetch(sourcePage)).text();
const data=[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(m=>JSON.parse(m[1]));
const graph=data.flatMap(x=>x['@graph']||[]);const list=graph.find(x=>x['@type']==='MusicPlaylist')?.track?.itemListElement;
// Metadata structure varies; recursively find the actual selected music recording.
function find(o){if(o&&typeof o==='object'){if(o['@type']==='MusicRecording'&&o.name==='Your Breath')return o;for(const x of Object.values(o)){const r=find(x);if(r)return r;}}return null;}
void list;
const item=find(data);if(!item||item.byArtist!=='Eugenio Mininni'||!item.isAccessibleForFree||item.copyrightNotice!=='Mixkit Stock Music Free License'||!item.url.startsWith('https://assets.mixkit.co/music/'))throw Error('Track or license metadata differs; review before download.');
const dir='public/audio/licensed';mkdirSync(inside(dir),{recursive:true});const src=dir+'/mixkit-your-breath.mp3';
if(!existsSync(inside(src))){const r=await fetch(item.url,{signal:AbortSignal.timeout(60000)});if(!r.ok)throw Error('Mixkit download failed '+r.status);writeFileSync(inside(src),Buffer.from(await r.arrayBuffer()));}
const normalized=dir+'/mixkit-your-breath.normalized.wav';
if(!existsSync(inside(normalized))){const r=spawnSync(process.execPath,[inside('scripts/audio-process.mjs'),'normalize',src,normalized],{encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error('Music normalization failed: '+r.stderr.slice(-400));}
writeFileSync(inside(dir+'/mixkit-your-breath.provenance.json'),JSON.stringify({...item,sourcePage,permission:'https://mixkit.co/license/#musicFree',sha256:createHash('sha256').update(readFileSync(inside(src))).digest('hex'),modifications:'Excerpt used in video with fades, volume envelope and ducking. Original audio retained locally.'},null,2));
const compressed=dir+'/mixkit-your-breath.normalized.m4a';
if(!existsSync(inside(compressed)))ffmpeg(['-n','-i',inside(normalized),'-c:a','aac','-b:a','192k','-f','mp4','-movflags','+faststart',inside(compressed)]);
const config=readJson('src/film/audio-config.json');config.music={src:compressed.replace(/^public\//,''),gain:0.24};writeFileSync(inside('src/film/audio-config.json'),JSON.stringify(config,null,2));
console.log(JSON.stringify({title:item.name,artist:item.byArtist,license:item.copyrightNotice,sourcePage,musicGain:config.music.gain}));
