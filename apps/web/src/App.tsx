import { useEffect, useRef, useState } from 'react';
import { names, evaluationUrl, reasonText } from './replay.mjs';
import { SpecimenStage } from './SpecimenStage';
import { ContactSheet } from './ContactSheet';
import { ResearchPanel } from './ResearchPanel';
import { Evaluation } from './Evaluation';
import { Icon } from './Icon';
import type { Manifest, Run, ViewMode, Evaluation as EvaluationData } from './types';

async function fetchJSON<T>(url:string,signal?:AbortSignal):Promise<T>{
  const response=await fetch(url,{signal});
  if(!response.ok)throw new Error(`Could not load ${url} (${response.status})`);
  let value:T;
  try{value=await response.json();}catch{throw new Error(`Missing or invalid demo JSON: ${url}`);}
  if(signal?.aborted)throw new DOMException('Request cancelled','AbortError');
  return value;
}

function Brand(){return <header className="site-header"><a className="brand" href="/" aria-label="Glimpse home">glimpse</a><span className="tagline">Know when to look.</span><nav aria-label="Main"><a href="#experiment" className="active">Experiment</a><a href="#research" onClick={()=>{const section=document.getElementById('research');if(section instanceof HTMLDetailsElement)section.open=true;}}>Research</a></nav></header>;}

function Replay({manifest}:{manifest:Manifest}){
  const [sequence,setSequence]=useState('mskcc_confocal_s2');
  const [budget,setBudget]=useState(54);
  const [comparator,setComparator]=useState('fixed');
  const [mode,setMode]=useState<ViewMode>('gaussians');
  const [run,setRun]=useState<Run|null>(null);
  const [error,setError]=useState('');
  const [t,setT]=useState(0);
  const [playing,setPlaying]=useState(false);
  const [speed,setSpeed]=useState(12);
  const [revealed,setRevealed]=useState(false);
  const [evaluation,setEvaluation]=useState<EvaluationData|null>(null);
  const [evalError,setEvalError]=useState('');
  const [preview,setPreview]=useState(false);
  const firstLoad=useRef(true);
  const condition=manifest.conditions.find(c=>c.sequence_id===sequence&&c.budget===budget);
  useEffect(()=>{
    const controller=new AbortController();
    setRun(null);setError('');setPlaying(false);setT(0);setRevealed(false);setEvaluation(null);setEvalError('');setPreview(false);
    if(!condition){setError('This experiment was not exported.');return;}
    fetchJSON<Run>(`/demo/${condition.replay}`,controller.signal).then(value=>{
      if(value.key!==condition.key||value.frame_count<1)throw new Error('Experiment metadata mismatch');
      setRun(value);
      // Explicit midpoint preview of a closed run. First Play starts at frame 0.
      if(firstLoad.current){firstLoad.current=false;setT(Math.floor((value.frame_count-1)/2));setPreview(true);}
    }).catch(e=>{if(e.name!=='AbortError')setError(e.message);});
    return()=>controller.abort();
  },[condition]);
  useEffect(()=>{
    if(!playing||!run)return;
    const timer=window.setInterval(()=>setT(value=>Math.min(value+1,run.frame_count-1)),1000/speed);
    return()=>window.clearInterval(timer);
  },[playing,run,speed]);
  useEffect(()=>{if(run&&t===run.frame_count-1)setPlaying(false);},[t,run]);
  useEffect(()=>{
    const controller=new AbortController();const url=condition&&evaluationUrl(condition,revealed);
    if(!url)return;setEvalError('');
    fetchJSON<EvaluationData>(url,controller.signal).then(setEvaluation).catch(e=>{if(e.name!=='AbortError')setEvalError(e.message);});
    return()=>controller.abort();
  },[condition,revealed]);
  useEffect(()=>{
    if(revealed&&evaluation)document.querySelector('.evaluation')?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  },[revealed,evaluation]);
  const seek=(value:number)=>{setPlaying(false);setPreview(false);setT(value);};
  const play=()=>{if(!run)return;if(preview||t===run.frame_count-1)setT(0);setPreview(false);setPlaying(value=>!value);};
  const activeRun=run?.key===condition?.key?run:null;
  const current=activeRun?.methods.photon.decisions[t];
  return <>
    <section className="intro" id="experiment"><h1>A glimpse.<br/>Then a decision.</h1><p>Glimpse chooses when to acquire a real<br className="desktop-break"/> microscopy image and estimates what happens<br className="desktop-break"/> between observations.</p></section>
    {error?<div className="error" role="alert">{error}<p>Rebuild the local demo assets, then reload this page.</p></div>:!activeRun?<div className="loading" role="status">Loading the recorded experiment…</div>:<>
      <SpecimenStage run={activeRun} t={t} mode={mode} setMode={setMode}/>
      <div className="transport"><button className="play-button" onClick={play} aria-label={playing?'Pause replay':'Play replay'} title={preview?'Play the complete experiment from frame 0':playing?'Pause replay':'Play replay'}><Icon name={playing?'pause':'play'} size={23}/></button><label className="scrubber"><span className="sr-only">Source frame</span><input type="range" min="0" max={activeRun.frame_count-1} value={t} onChange={e=>seek(Number(e.target.value))}/></label><output className="timecode"><span>{String(t).padStart(3,'0')} / {activeRun.frame_count-1}</span><small>{preview?'Recorded preview · play starts at 0':`${(t*activeRun.frame_interval_minutes).toFixed(2)} source min`}</small></output><label className="speed"><span className="sr-only">Playback speed</span><select value={speed} onChange={e=>setSpeed(Number(e.target.value))}><option value="6">6 frames/s</option><option value="12">12 frames/s</option><option value="24">24 frames/s</option></select></label></div>
      <ContactSheet run={activeRun} comparator={comparator} t={t} onSeek={seek} events={revealed?evaluation?.division_times:undefined}/>
      <div className="decision-rail" aria-label="Current acquisition decision"><span className="rail-label">Current decision</span><p><span className={`decision-marker ${current?.decision==='ACQUIRE'?'capture':''}`}/>{current?reasonText[current.reason]||current.reason.replaceAll('_',' '):'—'}</p><button className={revealed?'evidence-button selected':'evidence-button'} aria-pressed={revealed} onClick={()=>{setPlaying(false);setRevealed(value=>!value);}}><Icon name="eye" size={19}/>{revealed?'Hide evidence':'Reveal evidence'}</button></div>
      <div className="experiment-meta"><span>C. elegans · embryo {sequence.endsWith('2')?'02':'03'}<span className="meta-divider">/</span>{budget} of {activeRun.frame_count} volumes per schedule</span><span>Exposure proxy {(budget/activeRun.frame_count).toFixed(3)} · {((1-budget/activeRun.frame_count)*100).toFixed(1)}% fewer captures than all-frame imaging, for both schedules.</span></div>
      {revealed?(evalError?<p className="error" role="alert">{evalError}</p>:evaluation?<Evaluation run={activeRun} data={evaluation} comparator={comparator} t={t} gaussian={true} onClose={()=>{setRevealed(false);document.getElementById('experiment')?.scrollIntoView({block:'start'});}}/>:<p className="loading-inline" role="status">Opening evaluation-only images and results…</p>):null}
    </>}
    <div className="disclosures"><details id="settings"><summary>Experiment settings <span>Embryo, budget & comparison</span></summary><div className="detail-body experiment-controls"><label htmlFor="sequence">Sequence<select id="sequence" value={sequence} onChange={e=>setSequence(e.target.value)}>{[...new Set(manifest.conditions.map(c=>c.sequence_id))].map(s=><option key={s} value={s}>C. elegans · embryo {s.endsWith('2')?'02':'03'}</option>)}</select></label><label htmlFor="budget">Image budget<select id="budget" value={budget} onChange={e=>setBudget(Number(e.target.value))}>{[...new Set(manifest.conditions.map(c=>c.budget))].map(b=><option key={b} value={b}>{b} / 270 volumes</option>)}</select></label><label htmlFor="comparison">Compare with Glimpse<select id="comparison" value={comparator} onChange={e=>setComparator(e.target.value)}>{Object.entries(names).filter(([key])=>key!=='photon').map(([key,name])=><option key={key} value={key}>{name}</option>)}</select></label><p>All views replay authentic closed runs. Settings change which saved experiment you inspect; they do not execute or tune a controller.</p></div></details>{activeRun?<ResearchPanel manifest={manifest} run={activeRun} t={t} comparator={comparator}/>:null}</div>
    <footer><span>GLIMPSE <span className="footer-divider">/</span> GatorHack V 2026</span><span className="partial-status">Partial benchmark. Image scores first-pass; source verification pending.</span></footer>
  </>;
}

export default function App(){
  const [manifest,setManifest]=useState<Manifest|null>(null);const [error,setError]=useState('');
  useEffect(()=>{const controller=new AbortController();fetchJSON<Manifest>('/demo/manifest.json',controller.signal).then(value=>{if(value.version!==1||!value.conditions?.length)throw new Error('Unsupported or incomplete demo export');setManifest(value);}).catch(e=>{if(e.name!=='AbortError')setError(e.message);});return()=>controller.abort();},[]);
  return <main><Brand/>{manifest?<Replay manifest={manifest}/>:error?<section className="setup error" role="alert"><h1>Prepare the real experiment.</h1><p>{error}</p><p>Generate the local display assets:</p><code>.venv/Scripts/python.exe scripts/build_phase6_assets.py</code><p>Then export the 3D views with scripts/build_glimpse_spatial.py.</p><button onClick={()=>window.location.reload()}>Retry loading</button></section>:<p className="loading" role="status">Opening Glimpse…</p>}</main>;
}
