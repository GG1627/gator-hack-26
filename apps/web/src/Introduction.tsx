import { lazy, Suspense, useEffect, useState } from 'react';
import { Icon } from './Icon';
import './introduction.css';

const HeroField = lazy(()=>import('./HeroField'));
const stages = [
  {name:'Observe',detail:'Acquire a real image.',description:'Start with a real observation of the specimen.'},
  {name:'Estimate',detail:'Model the interval.',description:'Estimate how the specimen changes between observations.'},
  {name:'Decide',detail:'Choose when to look.',description:'Use uncertainty and the remaining budget to decide when to acquire again.'},
];

function FieldFallback(){return <div className="hero-field-fallback" aria-hidden="true"><div/><div/><div/><div/><div/><div/><div/></div>;}

export function Introduction(){
  const [phase,setPhase] = useState(0);
  const [playing,setPlaying] = useState(true);
  const [reduced,setReduced] = useState(()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  useEffect(()=>{
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = ()=>setReduced(media.matches);
    media.addEventListener('change',update);
    return ()=>media.removeEventListener('change',update);
  },[]);
  useEffect(()=>{
    if(!playing||reduced)return;
    const timer = window.setInterval(()=>{
      if(document.visibilityState==='visible')setPhase(value=>(value+1)%stages.length);
    },4000);
    return ()=>window.clearInterval(timer);
  },[playing,reduced]);
  return <section className="product-intro" aria-labelledby="product-title">
    <div className="intro-copy">
      <p className="eyebrow"><span/> Intelligent microscopy / Glimpse</p>
      <h1 id="product-title">See life.<br/>Spend light<br/><em>wisely.</em></h1>
      <p className="product-purpose">Repeated imaging can harm living cells. Glimpse decides when to capture—and when to wait.</p>
      <a className="explore-button" href="#controlled-lab">Explore the experiment <Icon name="arrow" size={20}/></a>
      <p className="hero-provenance">Controlled lab. Real microscopy. Evidence you can inspect.</p>
    </div>
    <figure className="hero-illustration" aria-label="Illustrated acquisition cycle">
      <div className="hero-field-title"><span><i/> A moment in the life of a specimen</span><span>FIG. 01</span></div>
      <div className="hero-field-wrap">
        <Suspense fallback={<FieldFallback/>}><HeroField phase={phase} playing={playing} reduced={reduced}/></Suspense>
        <span className="field-axis">Drag to rotate <i/> 3D</span>
        <span className="field-note">Conceptual specimen<br/>Not experimental data</span>
        <div className="field-phase" aria-hidden="true"><span>0{phase+1}</span><p>{stages[phase].name}<small>{stages[phase].detail}</small></p></div>
      </div>
      <figcaption className="hero-cycle">
        <div className="hero-cycle-steps" role="group" aria-label="Illustration stages">{stages.map((stage,index)=><button key={stage.name} aria-pressed={phase===index} onClick={()=>{setPhase(index);setPlaying(false);}}><span>0{index+1}</span>{stage.name}<i/></button>)}</div>
        <button className="hero-motion" aria-label={playing&&!reduced?'Pause illustration':'Play illustration'} onClick={()=>setPlaying(value=>!value)} disabled={reduced} title={reduced?'Animation disabled by reduced-motion preference':playing?'Pause illustration':'Play illustration'}><Icon name={playing&&!reduced?'pause':'play'} size={15}/></button>
      </figcaption>
      <p className="cycle-explanation">{stages[phase].description}</p>
    </figure>
    <div className="hero-explanation">
      <div><span className="explanation-index">01 / THE PROBLEM</span><h2>Seeing cells can disturb them.</h2><p>Repeated illumination can bleach fluorescent signals and harm living cells. Fixed schedules keep taking images—even when little changes.</p></div>
      <div><span className="explanation-index">02 / OUR APPROACH</span><h2>Let the specimen set the pace.</h2><p>Glimpse uses observed changes, uncertainty, and the remaining light budget to choose when to acquire again. We test those decisions against fixed schedules at the same image budget.</p></div>
    </div>
    <div className="intro-foundations"><span>See more. Illuminate less.</span><p>Dynamic Gaussian models <i aria-hidden="true">/</i> Adaptive scheduling <i aria-hidden="true">/</i> Native CUDA Rust</p></div>
  </section>;
}
