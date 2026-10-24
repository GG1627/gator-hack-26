import { useEffect, useRef, useState } from 'react';
import { frameState, names, reasonText } from './replay.mjs';
import type { Run } from './types';

export function ImagePanel({run, method, t, gaussian}: {run: Run; method: string; t: number; gaussian: boolean}) {
  const state = frameState(run, method, t, gaussian);
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [state.image]);
  return <section className={`image-panel ${method === 'photon' ? 'adaptive' : ''}`} aria-label={`${names[method]} viewer`}>
    <div className="panel-title"><h2>{method === 'photon' ? 'PHOTON' : names[method]}</h2><span>{state.label}</span></div>
    <div className="microscopy">
      <img key={state.image} src={state.image} alt={`${state.label}: ${run.sequence_id}, ${state.predicted ? 'saved causal Gaussian forecast at' : 'acquired volume'} frame ${state.predicted ? t : state.last}`} onError={() => setFailed(true)} />
      {failed ? <div className="image-error" role="alert">Image unavailable. Rebuild the demo assets.</div> : null}
      <div className="image-stamp"><span>{state.predicted ? `Forecast at ${t}` : `Acquired at ${state.last}`}<br/>{state.predicted ? 'Simplified Gaussian model' : state.measured ? 'Observation acquired now' : `Held for ${t - state.last} source steps`}</span><span>{state.count} / {run.budget}<br/>volumes used</span></div>
    </div>
    <div className="panel-foot"><span>{state.predicted ? 'Causal prediction · not a real image' : 'Real confocal image · 3D maximum projection'}</span><span>{state.predicted ? 'CPU render' : 'MSKCC'}</span></div>
  </section>;
}

export function Timeline({run, method, t, events, onSeek}: {run: Run; method: string; t: number; events?: number[]; onSeek: (t: number) => void}) {
  const indices = run.methods[method].config.acquired_indices;
  return <div className={`timeline ${method === 'photon' ? 'adaptive' : ''}`}>
    <div className="timeline-heading"><span>{names[method]}</span><span>{indices.filter(i => i <= t).length} exposures so far</span></div>
    <svg viewBox="0 0 1000 44" preserveAspectRatio="none" role="img" aria-label={`${names[method]} exposure timeline. Click a marker to inspect its decision.`}>
      <line x1="0" x2="1000" y1="32" y2="32" className="baseline"/>
      {events ? [...new Set(events)].map(e => <line key={`e${e}`} x1={e / (run.frame_count - 1) * 1000} x2={e / (run.frame_count - 1) * 1000} y1="2" y2="8" className="event-tick"/>) : null}
      {indices.map(i => <g key={i} className={i <= t ? 'exposed' : 'future-tick'} onClick={() => onSeek(i)}><title>Acquire at frame {i}: {run.methods[method].decisions[i].reason}</title><rect x={i / (run.frame_count - 1) * 1000 - 4} y="10" width="8" height="28" fill="transparent" stroke="none"/><line x1={i / (run.frame_count - 1) * 1000} x2={i / (run.frame_count - 1) * 1000} y1="15" y2="32"/></g>)}
      <line x1={t / (run.frame_count - 1) * 1000} x2={t / (run.frame_count - 1) * 1000} y1="0" y2="42" className="cursor"/>
    </svg>
  </div>;
}

export function DecisionInspector({run, t}: {run: Run; t: number}) {
  const row = run.methods.photon.decisions[t];
  return <section className="decision" aria-label="Decision rationale">
    <div><span className="tiny">PHOTON DECISION · FRAME {t}</span><strong className={row.decision === 'ACQUIRE' ? 'accent' : ''}>{row.decision === 'ACQUIRE' ? 'Acquire an observation' : 'Keep the light off'}</strong></div>
    <div className="decision-text"><p>{reasonText[row.reason] || row.reason.replaceAll('_', ' ')}</p><span className="tiny">RECORDED REASON: {row.reason}</span></div>
    <div className="decision-values"><span>Priority <b>{row.score?.toFixed(2) ?? '—'}</b></span><span>Budget left <b>{row.remaining_budget_after}</b></span></div>
  </section>;
}

export function Difference({truth, prediction}: {truth: string; prediction: string}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    let cancelled = false;
    setError(false);
    async function draw() {
      const images = await Promise.all([truth, prediction].map(src => new Promise<HTMLImageElement>((resolve, reject) => {
        const img = new Image(); img.onload = () => resolve(img); img.onerror = reject; img.src = src;
      })));
      if (cancelled || !canvas.current) return;
      const ctx = canvas.current.getContext('2d', {willReadFrequently: true});
      if (!ctx) throw new Error('Canvas unavailable');
      ctx.drawImage(images[0], 0, 0, 512, 512);
      const a = ctx.getImageData(0, 0, 512, 512);
      ctx.drawImage(images[1], 0, 0, 512, 512);
      const b = ctx.getImageData(0, 0, 512, 512);
      for (let i = 0; i < a.data.length; i += 4) {
        const difference = Math.abs(a.data[i] - b.data[i]);
        a.data[i] = a.data[i + 1] = a.data[i + 2] = difference;
      }
      ctx.putImageData(a, 0, 0);
    }
    draw().catch(() => { if (!cancelled) setError(true); });
    return () => { cancelled = true; };
  }, [truth, prediction]);
  return <div>{error ? <p role="alert">Difference image unavailable.</p> : <canvas ref={canvas} width="512" height="512" aria-label="Absolute difference of 8-bit display projections; not the 3D evaluation error"/>}</div>;
}
