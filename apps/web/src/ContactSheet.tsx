import { contactSlots } from './geometry.mjs';
import { names } from './replay.mjs';
import type { Run } from './types';
import { useEffect, useState } from 'react';

export function ContactSheet({run,comparator,t,onSeek,events}: {run:Run;comparator:string;t:number;onSeek:(t:number)=>void;events?:number[]}){
  const responsiveCount=()=>window.innerWidth<=650?6:window.innerWidth<=1050?12:18;
  const [count,setCount]=useState(responsiveCount);
  useEffect(()=>{const resize=()=>setCount(responsiveCount());window.addEventListener('resize',resize);return()=>window.removeEventListener('resize',resize);},[]);
  const slots=contactSlots(run,'photon',t,count);
  const start=slots[0].start,end=slots.at(-1)!.end;
  const cursor=Math.max(0,Math.min(100,(t-start)/(end-start+1)*100));
  return <section className="contact-sheet" aria-label="Acquisition contact sheet">
    <div className="sheet-caption"><span>Observation history</span><span>Source frames {start}–{end} · shared {end-start+1}-frame window</span></div>
    {[comparator,'photon'].map(method=>{
      const counts=run.methods[method].config.acquired_indices.filter(i=>i<=t).length;
      return <div className="contact-row" key={method}><div className="policy-label"><strong>{method==='photon'?'Peekaboo':method==='fixed'?'Fixed timing':names[method]}</strong><span>{counts} / {run.budget} acquired</span></div><div className="contact-track">
        <div className="contact-slots" style={{gridTemplateColumns:`repeat(${count},minmax(0,1fr))`}}>{contactSlots(run,method,t,count).map(slot=><button key={slot.start} className={`contact-slot ${slot.kind}`} onClick={()=>onSeek(slot.imageIndex??slot.start)} aria-label={slot.imageIndex==null?`${method}: ${slot.kind} at frames ${slot.start} to ${slot.end}`:`${method}: inspect acquired frame ${slot.imageIndex}`} title={slot.imageIndex==null?`${slot.start}–${slot.end}: ${slot.kind}`:`Acquired ${slot.indices.join(', ')}; showing ${slot.imageIndex}`}>
          {slot.imageIndex!=null?<><img src={`/demo/images/${run.sequence_id}/${slot.imageIndex}.png`} alt={`Measured at ${slot.imageIndex}`} loading="eager"/><span>{slot.imageIndex}{slot.indices.length>1?` +${slot.indices.length-1}`:''}</span></>:<span className="slot-dash">—</span>}
        </button>)}</div>
        <svg viewBox="0 0 1000 15" preserveAspectRatio="none" aria-label={`${names[method]} acquisition markers in the current window`} role="img">
          <line x1="0" x2="1000" y1="7" y2="7" className="sheet-line"/>
          {run.methods[method].config.acquired_indices.filter(i=>i>=start&&i<=end).map(i=><circle key={i} cx={(i-start)/(end-start+1)*1000} cy="7" r="2" className={`${method==='photon'?'adaptive-dot':'fixed-dot'} ${i>t?'future-dot':''}`}><title>Acquire frame {i}</title></circle>)}
          {events?[...new Set(events)].filter(i=>i>=start&&i<=end).map(i=><path key={i} d={`M${(i-start)/(end-start+1)*1000} 2v10`} className="event-mark"><title>Annotated division at {i}, evaluation only</title></path>):null}
        </svg>
        <span className="contact-cursor" style={{left:`${cursor}%`}}/>
      </div></div>;
    })}
    <div className="sheet-legend"><span><i className="acquired-key"/>Acquired image</span><span><i className="skipped-key"/>Skipped observation</span><span><i className="future-key"/>Future in replay</span>{events?<span><i className="event-key"/>Annotated division · eval only</span>:null}<span>Both schedules have the same total image budget.</span></div>
  </section>;
}
