import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { frameState } from './replay.mjs';
import { pointCloudUrl } from './geometry.mjs';
import { Icon } from './Icon';
import type { Run, SceneArchive, ViewMode } from './types';

const Viewer3D=lazy(()=>import('./Viewer3D'));
const pointCache=new Map<string,ArrayBuffer>();

export function SpecimenStage({run,t,mode,setMode}: {run: Run; t: number; mode: ViewMode; setMode: (mode: ViewMode)=>void}){
  const [archive,setArchive]=useState<SceneArchive|null>(null);
  const [points,setPoints]=useState<{url:string;data:ArrayBuffer}|null>(null);
  const [error,setError]=useState('');
  const [pointError,setPointError]=useState('');
  const [showImage,setShowImage]=useState(true);
  const [structure,setStructure]=useState(false);
  const [resetKey,setResetKey]=useState(0);
  const [cameraAction,setCameraAction]=useState({kind:'left',id:0});
  const [imageError,setImageError]=useState(false);
  const [copyError,setCopyError]=useState('');
  const current=frameState(run,'photon',t,false);
  const cloudUrl=pointCloudUrl(run,t);
  const frame=archive?.frames[t]??null;
  const onError=useCallback((value:string)=>setError(value),[]);
  const container=useRef<HTMLElement>(null);
  useEffect(()=>{
    const controller=new AbortController();setArchive(null);setError('');
    Promise.all([fetch('/demo/spatial/manifest.json',{signal:controller.signal}),fetch(`/demo/spatial/${run.key}/gaussians.json`,{signal:controller.signal})]).then(async responses=>{
      if(responses.some(r=>!r.ok))throw new Error('The 3D view is not ready. You can still inspect the acquired microscope images.');
      const [manifest,value]=await Promise.all(responses.map(r=>r.json()));
      if(manifest.version!==1||value.version!==1||value.frames.length!==run.frame_count)throw new Error('3D display assets are incomplete or unsupported.');
      if(!controller.signal.aborted)setArchive(value);
    }).catch(e=>{if(e.name!=='AbortError')setError(e.message);});
    return()=>controller.abort();
  },[run.key]);
  useEffect(()=>{
    if(mode!=='spatial')return;
    const controller=new AbortController();setPointError('');
    const cached=pointCache.get(cloudUrl);
    if(cached){setPoints({url:cloudUrl,data:cached});return;}
    fetch(cloudUrl,{signal:controller.signal}).then(async response=>{
      if(!response.ok||response.headers.get('content-type')?.includes('text/html'))throw new Error('Acquired voxel display is unavailable. Try Microscope view.');
      const data=await response.arrayBuffer();
      if(data.byteLength%8!==0)throw new Error('Invalid voxel display payload.');
      if(controller.signal.aborted)return;
      pointCache.set(cloudUrl,data);if(pointCache.size>5)pointCache.delete(pointCache.keys().next().value!);
      setPoints({url:cloudUrl,data});
    }).catch(e=>{if(e.name!=='AbortError')setPointError(e.message);});
    return()=>controller.abort();
  },[cloudUrl,mode]);
  useEffect(()=>{setImageError(false);},[current.image]);
  const loadedPoints=points?.url===cloudUrl?points.data:null;
  const loading=mode==='gaussians'?!archive:mode==='spatial'?!loadedPoints:false;
  const failed=mode==='spatial'?pointError||error:error;
  const label=mode==='gaussians'?(frame?.kind==='fit'?'MODEL FIT':'MODEL FORECAST'):current.measured?'MEASURED':'MEASURED · HELD';
  const keyboard=(event:React.KeyboardEvent<HTMLElement>)=>{
    if(event.target!==event.currentTarget||mode==='microscope')return;
    const kinds:Record<string,string>={ArrowLeft:'left',ArrowRight:'right','+':'in','=':'in','-':'out'};
    if(event.key==='Home'){event.preventDefault();setResetKey(v=>v+1);}
    else if(kinds[event.key]){event.preventDefault();setCameraAction(v=>({kind:kinds[event.key],id:v.id+1}));}
  };
  const fullscreen=()=>{
    setCopyError('');
    const action=document.fullscreenElement?document.exitFullscreen():container.current?.requestFullscreen();
    action?.catch(()=>setCopyError('Fullscreen is unavailable in this browser.'));
  };
  return <section className="specimen-stage" id="specimen" ref={container} data-acquired={current.measured} data-source-frame={current.last} aria-label="Peekaboo specimen viewer" tabIndex={mode==='microscope'?-1:0} onKeyDown={keyboard}>
    <div className="viewer-toolbar"><div className="view-tabs" role="tablist" aria-label="Specimen view">{(['spatial','gaussians','microscope'] as const).map(value=><button key={value} role="tab" aria-selected={mode===value} onClick={()=>setMode(value)}>{value[0].toUpperCase()+value.slice(1)}</button>)}</div><span className="state-label">{label}</span></div>
    <div className="scene-surface">
      {mode==='microscope'?<div className="microscope-view"><img key={current.image} src={current.image} alt={`MEASURED${current.measured?'':' · HELD'}: acquired volume ${current.last}, ${run.sequence_id}`} onError={()=>setImageError(true)}/>{imageError?<p className="stage-error" role="alert">The acquired image is unavailable.</p>:null}</div>:failed?<div className="stage-error" role="alert"><p>{failed}</p><button onClick={()=>setMode('microscope')}>Open microscope image</button></div>:<Suspense fallback={<p className="stage-loading">Opening the specimen…</p>}><Viewer3D run={run} frame={mode==='gaussians'?frame:null} points={loadedPoints} mode={mode} structure={structure} resetKey={resetKey} cameraAction={cameraAction} onError={onError}/>{loading?<p className="stage-loading" role="status">Loading {mode==='gaussians'?'saved model geometry':'acquired voxel samples'}…</p>:null}</Suspense>}
      {mode!=='microscope'?<aside className="source-reference"><label className="image-toggle"><input type="checkbox" checked={showImage} onChange={e=>setShowImage(e.target.checked)}/><span className="switch"/>Show acquired image</label>{showImage?<><img key={current.image} src={current.image} alt={`Source image acquired at ${current.last}; held measurement, not hidden truth`}/><span>MEASURED AT {current.last}<br/>{current.measured?'Acquired now':`Held · ${t-current.last} source steps`}</span></>:null}</aside>:null}
      <div className="viewer-bottom"><span>{mode==='gaussians'?`${frame?.gaussians.length??'—'} Gaussian components · ${frame?.kind==='fit'?'fit from acquired volume':'causal forecast'}`:mode==='spatial'?`${loadedPoints?loadedPoints.byteLength/8:'—'} acquired voxel samples · color = depth`:`Acquired at ${current.last} · whole-volume maximum projection`}</span><span>{mode==='microscope'?'MSKCC-CONFOCAL':'XYZ · μm'}</span></div>
    </div>
    <div className="viewer-tools"><span>{mode==='microscope'?'Real confocal microscopy. Source pixels preserved in the display projection.':'Drag to rotate · scroll to zoom · arrow keys rotate · + / − zoom'}</span><div>{mode==='gaussians'?<button className={structure?'active':''} aria-pressed={structure} onClick={()=>setStructure(v=>!v)} title="Inspect the 2-sigma component geometry"><Icon name="cube" size={16}/><span>Structure</span></button>:null}{mode!=='microscope'?<button onClick={()=>setResetKey(v=>v+1)} title="Reset camera"><Icon name="reset" size={16}/><span>Reset view</span></button>:null}<button aria-label="Toggle specimen fullscreen" title="Fullscreen" onClick={fullscreen}><Icon name="expand" size={17}/></button></div></div>
    {copyError?<p role="status" className="inline-note">{copyError}</p>:null}
  </section>;
}
