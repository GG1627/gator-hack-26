import { useEffect, useRef, useState } from 'react';
import { Icon } from './Icon';
import './controlled-lab.css';

type Decision = {t:number; decision:string; reason?:string; aspect?:number; target_gap?:number};
type Method = {acquired_indices:number[]; decisions:Decision[]};
type Experiment = {key:string; seed:number; condition:string; frame_count:number; budget:number; observed:string; model:string|null; methods:Record<string,Method>};
type Manifest = {version:number; demo_seed:number; experiments:Experiment[]; model_backend:string|null; summary_sha256:string};
type Metric = {covered_events:number; events:number; event_coverage:number|null; event_distances:number[]; hold_mse_all_frames:number};
type Evidence = {key:string; events:number[]; reference:string; metrics:Record<string,Metric>};
const base='/demo/controlled/';
const conditions=[['precursor','Visible precursors'],['abrupt','Sudden divisions'],['quiet','Quiet specimen']];
const fixedMethods=['fixed_0','fixed_0.333333','fixed_0.666667'];

async function read<T>(file:string,signal:AbortSignal,root=base):Promise<T>{
  const response=await fetch(root+file,{signal});
  if(!response.ok)throw new Error('The controlled experiment assets are unavailable.');
  return response.json();
}

function Microscope({file,frame,label,root=base}:{file:string; frame:number; label:string; root?:string}){
  const canvas=useRef<HTMLCanvasElement>(null);
  const [image,setImage]=useState<HTMLImageElement|null>(null);
  const [failed,setFailed]=useState(false);
  useEffect(()=>{
    setImage(null);setFailed(false);
    const source=new Image();let active=true;
    source.onload=()=>{if(active)setImage(source);};
    source.onerror=()=>{if(active)setFailed(true);};
    source.src=root+file;
    return()=>{active=false;};
  },[file,root]);
  useEffect(()=>{
    const context=canvas.current?.getContext('2d');
    if(!context)return;
    context.fillStyle='#101b1a';context.fillRect(0,0,512,512);
    if(image){context.imageSmoothingEnabled=true;context.drawImage(image,(frame%16)*64,Math.floor(frame/16)*64,64,64,0,0,512,512);}
  },[image,frame]);
  return <div className="lab-microscope"><canvas ref={canvas} width={512} height={512} role="img" aria-label={label} data-source-frame={frame}/>{!image?<span className="lab-image-status" role="status">{failed?'Image could not load':'Loading image…'}</span>:null}<span className="lab-reticle" aria-hidden="true"/></div>;
}

function Timeline({method,t,events,seek,label}:{method:Method;t:number;events?:number[];seek:(t:number)=>void;label:string}){
  const last=method.acquired_indices.filter(i=>i<=t).at(-1)??0;
  return <div className="lab-timeline" aria-label={`${label} acquisition timeline`}>
    <svg viewBox="0 0 480 48" role="img" aria-label={`${method.acquired_indices.filter(i=>i<=t).length} observations acquired by frame ${t}`}>
      <line x1="1" y1="26" x2="479" y2="26" className="lab-time-line"/>
      {method.acquired_indices.map(i=><line key={i} x1={i*2} x2={i*2} y1="18" y2="34" className={i<=t?'lab-tick past':'lab-tick'}/>)}
      {events?.map((event,index)=><circle key={index} cx={event*2} cy="9" r="4" className={method.acquired_indices.some(i=>Math.abs(i-event)<=1)?'lab-event caught':'lab-event'}/>)}
      <circle cx={last*2} cy="26" r="4" className="lab-latest-tick"/>
      <line x1="0" x2="0" y1="0" y2="45" className="lab-clock" style={{transform:`translateX(${t*2}px)`}}/>
    </svg>
    <input aria-label={`Seek ${label} timeline`} type="range" min={0} max={239} value={t} onChange={e=>seek(Number(e.target.value))}/>
  </div>;
}

export function ControlledLab(){
  const [comparison,setComparison]=useState('efficiency');
  const lowerBudget=comparison==='efficiency';
  const dataRoot=lowerBudget?`${base}budget32/`:base;
  const [manifest,setManifest]=useState<Manifest|null>(null);
  const [error,setError]=useState('');
  const [seed,setSeed]=useState(304);
  const [condition,setCondition]=useState('precursor');
  const [phase,setPhase]=useState(0);
  const [t,setT]=useState(0);
  const [playing,setPlaying]=useState(false);
  const [pace,setPace]=useState('quick');
  const [view,setView]=useState('observed');
  const [revealed,setRevealed]=useState(false);
  const [evidence,setEvidence]=useState<Evidence[]|null>(null);
  const [evidenceError,setEvidenceError]=useState('');
  const [retry,setRetry]=useState(0);
  const section=useRef<HTMLElement>(null);
  const finish=useRef<HTMLDivElement>(null);
  const finishShown=useRef(false);
  const run=manifest?.experiments.find(e=>e.seed===seed&&e.condition===condition);
  const fixedKey=lowerBudget?(phase===0?'fixed_0':'fixed_32'):fixedMethods[phase];
  useEffect(()=>{
    const controller=new AbortController();setError('');
    read<Manifest>('manifest.json',controller.signal,dataRoot).then(value=>{
      if(value.version!==1||!value.experiments.length)throw new Error('Unsupported controlled experiment.');
      setManifest(value);setSeed(value.demo_seed);
    }).catch(e=>{if(e.name!=='AbortError')setError(e.message);});
    return()=>controller.abort();
  },[retry,dataRoot]);
  useEffect(()=>{setT(0);setPlaying(false);setRevealed(false);},[seed,condition,phase]);
  useEffect(()=>{
    if(!playing||!run||t===239)return;
    const capturing=[fixedKey,'event_focus'].some(key=>run.methods[key].acquired_indices.includes(t));
    const delay=pace==='guided'?(capturing?170:1000/24):1000/18;
    const timer=window.setTimeout(()=>setT(value=>Math.min(value+1,239)),delay);
    return()=>window.clearTimeout(timer);
  },[playing,run,t,pace,fixedKey]);
  useEffect(()=>{
    if(t===239){setPlaying(false);setRevealed(true);}
    else finishShown.current=false;
  },[t]);
  useEffect(()=>{
    if(t!==239||!revealed||!evidence||finishShown.current)return;
    finishShown.current=true;
    finish.current?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  },[t,revealed,evidence]);
  useEffect(()=>{
    const node=section.current;if(!node)return;
    const observer=new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)setPlaying(false);});observer.observe(node);
    const hidden=()=>{if(document.hidden)setPlaying(false);};document.addEventListener('visibilitychange',hidden);
    return()=>{observer.disconnect();document.removeEventListener('visibilitychange',hidden);};
  },[]);
  useEffect(()=>{
    if(!revealed||evidence)return;
    const controller=new AbortController();setEvidenceError('');
    read<{experiments:Evidence[]}>('evidence.json',controller.signal,dataRoot).then(value=>setEvidence(value.experiments)).catch(e=>{if(e.name!=='AbortError')setEvidenceError(e.message);});
    return()=>controller.abort();
  },[revealed,evidence,dataRoot]);
  const result=evidence?.find(e=>e.key===run?.key);
  const seek=(value:number)=>{setT(value);setPlaying(false);};
  const aggregate=(key:string)=>{
    const rows=evidence?.filter(e=>manifest?.experiments.find(x=>x.key===e.key)?.condition===condition)||[];
    return [rows.reduce((sum,row)=>sum+row.metrics[key].covered_events,0),rows.reduce((sum,row)=>sum+row.metrics[key].events,0)];
  };
  const totalFocus=aggregate('event_focus'),totalFixed=aggregate(fixedKey);
  const burst=run?.methods.event_focus.decisions.find(d=>(d.target_gap??12)<12)?.t;
  const focusMetric=result?.metrics.event_focus;
  const fixedMetric=result?.metrics[fixedKey];
  const advantage=focusMetric&&fixedMetric?focusMetric.covered_events-fixedMetric.covered_events:0;
  const focusImages=run?.methods.event_focus.acquired_indices.length??0;
  const fixedImages=run?.methods[fixedKey]?.acquired_indices.length??0;
  const fewerCaptures=focusImages<fixedImages;
  const savings=fixedImages?100*(1-focusImages/fixedImages):0;
  const switchComparison=(value:string)=>{
    if(value===comparison)return;
    setManifest(null);setEvidence(null);setRevealed(false);setEvidenceError('');
    setPlaying(false);setT(0);setPhase(0);setSeed(value==='efficiency'?304:2026);
    finishShown.current=false;setComparison(value);
  };
  const showCaptures=()=>section.current?.querySelector('.lab-pair')?.scrollIntoView({block:'start',behavior:'auto'});
  const replay=()=>{setRevealed(false);setT(0);setPlaying(true);showCaptures();};
  return <section className="controlled-lab" id="controlled-lab" ref={section} aria-labelledby="lab-title">
    <div className="lab-heading"><div><p className="eyebrow">The demo <span className="lab-synthetic">Controlled · synthetic microscopy</span></p><h2 id="lab-title">Spend light on<br/>the moment that matters.</h2></div><div className="lab-intro"><p>Each sweep is a new capture. Between captures, the microscope stays dark and the last image holds. Watch Glimpse save its observations for a changing cell.</p><a href="#real-study" onClick={()=>{const archive=document.getElementById('real-study');if(archive instanceof HTMLDetailsElement)archive.open=true;}}>Explore the real microscopy study <span aria-hidden="true">↗</span></a></div></div>
    <div className="lab-comparison-switch" role="group" aria-label="Comparison mode"><button aria-pressed={lowerBudget} onClick={()=>switchComparison('efficiency')}>Fewer images</button><button aria-pressed={!lowerBudget} onClick={()=>switchComparison('equal')}>Equal budget</button><span>{lowerBudget?`32 adaptive captures · ${fixedImages||40} fixed captures`:'40 captures for each method'}</span></div>
    {error?<div className="error" role="alert">{error} <button onClick={()=>setRetry(value=>value+1)}>Retry</button></div>:!run?<p role="status">Loading the controlled experiment…</p>:<>
      <div className="lab-controls"><div className="lab-condition" role="group" aria-label="Controlled scenario">{conditions.map(([key,label])=><button key={key} aria-pressed={condition===key} onClick={()=>setCondition(key)}>{label}</button>)}</div><div className="lab-selects"><label>Seed<select aria-label="Controlled seed" value={seed} onChange={e=>setSeed(Number(e.target.value))}>{[...new Set(manifest!.experiments.map(e=>e.seed))].map(s=><option value={s} key={s}>{s}{lowerBudget&&s===304?' · featured':''}</option>)}</select></label><label>{lowerBudget?'Fixed budget':'Fixed timing'}<select aria-label={lowerBudget?'Fixed capture budget':'Fixed timing offset'} value={phase} onChange={e=>setPhase(Number(e.target.value))}>{lowerBudget?<><option value={0}>40 images · reference</option><option value={1}>32 images · equal budget</option></>:<><option value={0}>Standard</option><option value={1}>+⅓ interval</option><option value={2}>+⅔ interval</option></>}</select></label></div></div>
      <p className="lab-comparison-note">Same {run.frame_count}-frame experiment. {fewerCaptures?`Glimpse uses ${focusImages} images; fixed uses ${fixedImages}.`:`Same ${focusImages}-image budget.`} Fixed spaces captures evenly; Glimpse concentrates them around change.</p>
      <div className="lab-pair">{[[fixedKey,'Fixed interval','Same rhythm, every time.'],['event_focus','Glimpse · event focus','Quiet sentinels. Focused bursts.']].map(([key,title,subtitle])=>{
        const method=run.methods[key];const indices=method.acquired_indices.filter(i=>i<=t);const source=indices.at(-1)??0;
        const capture=source===t;const decision=method.decisions[t];const metric=result?.metrics[key];
        return <article className={`lab-panel ${key==='event_focus'?'adaptive':''} ${capture?'exposing':''}`} key={key}>
          <header><div><h3>{title}</h3><p>{subtitle}</p></div><span className="lab-counter"><strong>{indices.length.toString().padStart(2,'0')}</strong> / {method.acquired_indices.length} images</span></header>
          <div className="lab-optical"><Microscope root={dataRoot} file={view==='model'&&run.model?run.model:run.observed} frame={source} label={`${title}: ${view==='model'?'Gaussian model from':'synthetic observation at'} frame ${source}; replay clock ${t}`}/><span key={`${comparison}-${run.key}-${source}-${view}`} className={`lab-capture-sweep ${playing?'animate':''}`} aria-hidden="true"/><div className="lab-optical-hud"><span className={capture?'lab-shutter on':'lab-shutter'}><i/>{capture?'CAPTURED NOW':'NO EXPOSURE'}</span><span>IMAGE {String(source).padStart(3,'0')}<br/><small>{t-source} frames old</small></span></div><span className="lab-image-caption">{view==='model'?'Gaussian fit of acquired image · held':'Last acquired image · held until the next capture'}</span><span className="lab-capture-stamp">CAPTURE #{String(indices.length).padStart(2,'0')}</span></div>
          <div className="lab-capture-state"><i className={capture?'on':''}/><strong>{capture?`New image · frame ${String(source).padStart(3,'0')}`:`Holding frame ${String(source).padStart(3,'0')}`}</strong><span>{capture?'One exposure used':'No new exposure'}</span></div>
          <div className="lab-panel-status"><span>{key==='event_focus'?decision?.reason==='budget coverage guard'?'Budget guard → capture required':t===0?'First image → assess shape':(decision?.target_gap??12)<12?'Shape changing → capture more often':'Shape stable → wait longer':'Same interval → next capture'}</span><span>{key==='event_focus'?`Target gap ${decision?.target_gap??12} frames`:`Every ~${((run.frame_count-1)/(fixedImages-1)).toFixed(1)} frames`}</span></div>
          <Timeline method={method} t={t} events={revealed?result?.events:undefined} seek={seek} label={title}/>
          {revealed&&metric?<div className="lab-score"><strong>{metric.events?`${metric.covered_events} / ${metric.events}`:'—'}</strong><span>{metric.events?'Full run · divisions captured within ±1 frame':'No divisions in this control'}</span></div>:null}
        </article>;
      })}</div>
      <div className="lab-transport"><button className="play-button" aria-label={playing?'Pause controlled replay':'Play controlled replay'} onClick={()=>{if(t===239){replay();return;}if(!playing)showCaptures();setPlaying(value=>!value);}}><Icon name={playing?'pause':'play'} size={21}/></button><label className="lab-scrubber"><span className="sr-only">Controlled replay frame</span><input type="range" min={0} max={239} value={t} onChange={e=>seek(Number(e.target.value))}/></label><output>{String(t).padStart(3,'0')} <span>/ 239</span></output><button onClick={()=>seek(Math.max(0,(burst??0)-2))} disabled={burst===undefined}>Find a burst</button><button className="evidence-button" aria-pressed={revealed} onClick={()=>{setPlaying(false);setRevealed(value=>!value);}}><Icon name="eye" size={17}/>{revealed?'Hide results':'Reveal results'}</button></div>
      <div className="lab-playback-note"><span><i/>Ticks are captures. Both panels follow the same experiment clock.</span><label>Playback<select aria-label="Controlled playback pace" value={pace} onChange={e=>setPace(e.target.value)}><option value="quick">Constant speed · shared clock</option><option value="guided">Capture pauses · viewing aid</option></select></label></div>
      <div className="lab-footnote"><span>Recorded causal runs · Glimpse {focusImages} images · Fixed {fixedImages} images · {fewerCaptures?`${savings.toFixed(0)}% fewer exposures than fixed, assuming equal light per image.`:`${(100*(1-focusImages/run.frame_count)).toFixed(1)}% fewer captures than all-frame imaging, for both schedules.`}</span>{run.model?<label>Image view<select aria-label="Controlled image view" value={view} onChange={e=>setView(e.target.value)}><option value="observed">Acquired pixels</option><option value="model">Gaussian model · CUDA Rust</option></select></label>:null}</div>
      {revealed?(evidenceError?<p className="error" role="alert">{evidenceError}</p>:result&&focusMetric&&fixedMetric?<>
        <div className="lab-finish" ref={finish} role="region" aria-label="Demo results" aria-live="polite">
          <div className="lab-finish-heading"><div><p className="eyebrow"><i/>{t===239?'Run complete':'Recorded run results'} · seed {seed}</p><h3>{!focusMetric.events?<>A quiet specimen.<br/>No divisions to score.</>:advantage>0?fewerCaptures?<>More divisions.<br/>Less light.</>:<>More of the moment.<br/>Same amount of light.</>:advantage<0?<>Some moments arrive<br/>without warning.</>:fewerCaptures?<>Same event coverage.<br/>Fewer exposures.</>:<>Same budget.<br/>Every moment accounted for.</>}</h3></div><button onClick={replay}><Icon name="play" size={16}/>Play again</button></div>
          <div className="lab-finish-stats">
            <div className="lab-finish-stat primary"><span>Divisions captured</span><strong>{focusMetric.events?`${Math.round(100*focusMetric.covered_events/focusMetric.events)}%`:'—'}</strong><p>Glimpse {focusMetric.covered_events}/{focusMetric.events} <span>·</span> Fixed {fixedMetric.covered_events}/{fixedMetric.events}</p><small>{focusMetric.events?`${advantage>0?'+':''}${Math.round(100*advantage/focusMetric.events)} percentage points vs fixed`:'No divisions in this control'}</small></div>
            <div className="lab-finish-stat"><span>Images taken</span><strong>{focusImages}</strong><p>of {run.frame_count} possible frames</p><small>Fixed {fewerCaptures?'takes':'also takes'} {fixedImages} images{fewerCaptures?` · ${fixedImages-focusImages} fewer with Glimpse`:''}</small></div>
            <div className="lab-finish-stat"><span>Fewer exposures</span><strong>{fewerCaptures?savings.toFixed(0):(100*(1-focusImages/run.frame_count)).toFixed(1)}<em>%</em></strong><p>{fewerCaptures?'vs fixed-interval imaging':'vs imaging every frame'}</p><small>{fewerCaptures?`${fixedImages-focusImages} fewer captures over the same experiment.`:'Same capture count for both schedules.'}</small></div>
            <div className="lab-finish-stat"><span>Less imaging light</span><strong>{savings.toFixed(0)}<em>%</em></strong><p>vs fixed-interval imaging</p><small>Equal illumination per capture assumed. Light exposure can cause phototoxic stress.</small></div>
          </div>
          <div className="lab-dose-comparison" aria-label="Exposure comparison"><p>Where the light goes <span>Equal light per capture assumed</span></p>{[['Every frame',run.frame_count],['Fixed interval',fixedImages],['Glimpse',focusImages]].map(([label,count])=><div key={label}><span>{label}</span><div className="lab-dose-track"><i style={{width:`${100*Number(count)/run.frame_count}%`}}/></div><strong>{count} exposures</strong></div>)}<small>{fewerCaptures?`Glimpse uses ${savings.toFixed(0)}% fewer exposures than fixed. With unchanged illumination per image, this corresponds to ${savings.toFixed(0)}% less imaging light.`:'Both sparse schedules use the same light budget. The comparison tests division coverage.'} Cell health has not been measured. <a href="https://www.nature.com/articles/srep15348" target="_blank" rel="noreferrer">Why dose is not a health score ↗</a></small></div>
          <p className="lab-finish-note">Controlled synthetic run · event capture within ±1 frame. {advantage>0?'Observed shape changes let Glimpse concentrate its images around division.':advantage<0?'Without warning cues, the sparse quiet-period schedule misses sudden divisions.':'This run does not show an event-capture advantage.'}</p>
        </div>
        <details className="lab-cohort"><summary>Across all six evaluation seeds <span>Results & source reference</span></summary><div className="lab-results"><div className="lab-aggregate"><span className="eyebrow">All six evaluation seeds · {conditions.find(([key])=>key===condition)?.[1]}</span><h3>{totalFocus[1]?<><strong>{totalFocus[0]} / {totalFocus[1]}</strong> events caught by Glimpse.<br/><span>{totalFixed[0]} / {totalFixed[1]} with this fixed timing.</span></>:<>A quiet control.<br/><span>No events to score.</span></>}</h3><p>{condition==='precursor'?'The simulator gives nuclei visible shape changes before division. Glimpse measures the acquired shapes and concentrates its remaining observations.':condition==='abrupt'?'Without an observable precursor, this controller cannot anticipate division. Its quiet-period spacing misses more sudden events than the fixed baseline.':`Glimpse uses ${focusImages} images; fixed uses ${fixedImages}. This controller spends its declared budget; this is not a claim of minimum captures needed.`}</p>{lowerBudget?<p>Glimpse takes 32 images per run; this fixed comparison takes {fixedImages}. Seed 304 was selected after evaluation to feature a successful precursor example. All six seeds remain available, including the missed division in seed 301. These results do not establish performance on real cells.</p>:null}<p className="lab-reference-legend"><i/> Caught event <i className="missed"/> Missed event · dots appear above the timelines.</p></div><figure className="lab-reference"><Microscope root={dataRoot} file={result.reference} frame={t} label={`Evaluation-only synthetic reference at frame ${t}`}/><figcaption>Evaluation-only reference · frame {t}<br/>Never available to the controller before acquisition.</figcaption></figure></div></details>
      </>:<p role="status">Loading evaluation-only results…</p>):null}
      <details className="lab-method"><summary>How this experiment works <span>Conditions, fairness & limits</span></summary><div><p>Four synthetic nuclei drift slowly. In the precursor condition, each elongates for 24 frames before a programmed split. Event times are randomized independently of fixed schedules. The sudden condition removes the precursor; the quiet condition removes divisions. This simplified forward model does not establish biological performance.</p><p>The controller fits Gaussian shapes to acquired pixels. A high aspect ratio shortens the observation gap from 12 to 4 or 2 frames. Integer feasibility guards preserve its exact {focusImages}-image budget and a maximum gap of 12. Shape is a heuristic cue, not a calibrated division probability. Predictions and hidden event times are never inputs.</p><p>{lowerBudget?'The 32-image budget was declared before testing seeds 301–306. The same unchanged controller is compared with fixed at 40 images, and fixed at 32 is also available for an equal-budget check. This demonstrates a chosen lower budget, not automatic discovery of the minimum number of captures.':'Settings were developed on seeds 7 and 42, then evaluated unchanged on these six seeds. Three fixed timing offsets and the original controller were also evaluated.'} Images are acquired synthetic observations, or explicitly labeled Gaussian fits rendered with the native CUDA Rust kernel. The model view holds the most recent fit; it does not predict a split. Real microscopy results are a separate experiment below.</p><a href={`${dataRoot}evidence.json`} target="_blank" rel="noreferrer">Inspect the measured ledger ↗</a></div></details>
    </>}
  </section>;
}
