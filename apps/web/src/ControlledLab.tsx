import { useEffect, useRef, useState } from 'react';
import { Icon } from './Icon';
import { Microscope } from './Microscope';
import { CaptureFeedback } from './CaptureFeedback';
import { Arrow, Button, CaptureStatus, SourceDisclosure, SourceLink } from './PeekabooUI';

type Decision = { t: number; decision: string; reason?: string; aspect?: number; target_gap?: number };
type Method = { acquired_indices: number[]; decisions: Decision[] };
type Experiment = { key: string; seed: number; condition: string; frame_count: number; budget: number; observed: string; model: string | null; methods: Record<string, Method> };
type Manifest = { version: number; demo_seed: number; experiments: Experiment[]; model_backend: string | null; summary_sha256: string };
type Metric = { covered_events: number; events: number; event_coverage: number | null; event_distances: number[]; hold_mse_all_frames: number };
type Evidence = { key: string; events: number[]; reference: string; metrics: Record<string, Metric> };
const base = '/demo/controlled/';
const conditions = [['precursor', 'Visible precursors'], ['abrupt', 'Sudden divisions'], ['quiet', 'Quiet specimen']];
const fixedMethods = ['fixed_0', 'fixed_0.333333', 'fixed_0.666667'];

async function read<T>(file: string, signal: AbortSignal, root: string): Promise<T> {
  const response = await fetch(root + file, { signal });
  if (!response.ok) throw new Error('The controlled experiment assets are unavailable.');
  return response.json();
}

function ComparisonTimeline({ run, fixedKey, t, events, onSeek }: { run: Experiment; fixedKey: string; t: number; events?: number[]; onSeek: (value: number) => void }) {
  const progress = t / (run.frame_count - 1) * 100;
  return <div className="comparison-timeline">
    <div className="timeline-labels" aria-hidden="true"><span>Fixed schedule</span><span>Peekaboo</span></div>
    <div className="timeline-plot">
      <svg viewBox="0 0 1000 80" preserveAspectRatio="none" role="img" aria-label={`Exposure history through frame ${t}. Fixed schedule: ${run.methods[fixedKey].acquired_indices.filter(i => i <= t).length} images. Peekaboo: ${run.methods.event_focus.acquired_indices.filter(i => i <= t).length} images.`}>
        {([[fixedKey, 22], ['event_focus', 58]] as const).map(([key, y]) => <g key={key} className={key === 'event_focus' ? 'adaptive-lane' : 'fixed-lane'}>
          <line x1="0" x2="1000" y1={y} y2={y} className="lane-baseline"/>
          {run.methods[key].acquired_indices.filter(i => i <= t).map(i => <line key={i} x1={i / (run.frame_count - 1) * 1000} x2={i / (run.frame_count - 1) * 1000} y1={Number(y) - 7} y2={Number(y) + 7} className={`exposure-tick ${i === t ? 'just-captured' : ''}`}/>)}
          {events?.filter(event => event <= t).map((event, index) => {
            const caught = run.methods[key].acquired_indices.some(i => i <= t && Math.abs(i - event) <= 1);
            const status = caught ? 'caught' : t <= event + 1 ? 'pending' : 'missed';
            return <circle key={index} cx={event / (run.frame_count - 1) * 1000} cy={y - 14} r="3" className={`event-mark ${status}`}><title>Division at frame {event} · {caught ? 'covered within ±1 frame' : status === 'pending' ? 'coverage window still open' : 'missed'}</title></circle>;
          })}
        </g>)}
      </svg>
      <span className="timeline-playhead" style={{ left: `${progress}%` }} aria-hidden="true"/>
      <input aria-label="Controlled replay frame" aria-valuetext={`Frame ${t} of ${run.frame_count - 1}`} type="range" min={0} max={run.frame_count - 1} value={t} onChange={e => onSeek(Number(e.target.value))}/>
    </div>
  </div>;
}

export function ControlledLab({ active = true }: { active?: boolean }) {
  const [comparison, setComparison] = useState('efficiency');
  const lowerBudget = comparison === 'efficiency';
  const dataRoot = lowerBudget ? `${base}budget32/` : base;
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [error, setError] = useState('');
  const [seed, setSeed] = useState(304);
  const [condition, setCondition] = useState('precursor');
  const [phase, setPhase] = useState(0);
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [pace, setPace] = useState('quick');
  const [view, setView] = useState('observed');
  const [revealed, setRevealed] = useState(false);
  const [showDivisions, setShowDivisions] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [evidence, setEvidence] = useState<Evidence[] | null>(null);
  const [evidenceError, setEvidenceError] = useState('');
  const [retry, setRetry] = useState(0);
  const [evidenceRetry, setEvidenceRetry] = useState(0);
  const resultHeading = useRef<HTMLHeadingElement>(null);
  const comparisonHeading = useRef<HTMLHeadingElement>(null);
  const cohortDetails = useRef<HTMLDetailsElement>(null);
  const run = manifest?.experiments.find(e => e.seed === seed && e.condition === condition);
  const fixedKey = lowerBudget ? (phase === 0 ? 'fixed_0' : 'fixed_32') : fixedMethods[phase];

  useEffect(() => {
    const controller = new AbortController(); setError('');
    read<Manifest>('manifest.json', controller.signal, dataRoot).then(value => {
      if (controller.signal.aborted) return;
      if (value.version !== 1 || !value.experiments.length) throw new Error('Unsupported controlled experiment.');
      setManifest(value); setSeed(value.demo_seed);
    }).catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    return () => controller.abort();
  }, [retry, dataRoot]);
  useEffect(() => { setT(0); setPlaying(false); setRevealed(false); setShowDivisions(false); setShowResults(false); }, [seed, condition, phase]);
  useEffect(() => {
    if (!active) setPlaying(false);
  }, [active]);
  useEffect(() => {
    const hidden = () => { if (document.hidden) setPlaying(false); };
    document.addEventListener('visibilitychange', hidden);
    return () => document.removeEventListener('visibilitychange', hidden);
  }, []);
  useEffect(() => {
    if (!active || !playing || !run || t === 239) return;
    const capturing = [fixedKey, 'event_focus'].some(key => run.methods[key].acquired_indices.includes(t));
    const delay = pace === 'guided' ? (capturing ? 170 : 1000 / 24) : 1000 / 18;
    const timer = window.setTimeout(() => setT(value => Math.min(value + 1, 239)), delay);
    return () => window.clearTimeout(timer);
  }, [active, playing, run, t, pace, fixedKey]);
  useEffect(() => { if (t === 239) setPlaying(false); }, [t]);
  useEffect(() => {
    if ((!revealed && !showDivisions) || evidence) return;
    const controller = new AbortController(); setEvidenceError('');
    read<{ experiments: Evidence[] }>('evidence.json', controller.signal, dataRoot).then(value => {
      if (!controller.signal.aborted) setEvidence(value.experiments);
    }).catch(e => { if (e.name !== 'AbortError') setEvidenceError(e.message); });
    return () => controller.abort();
  }, [revealed, showDivisions, evidence, dataRoot, evidenceRetry]);
  useEffect(() => {
    if (showResults) { resultHeading.current?.focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: 'instant' }); }
  }, [showResults]);
  const result = revealed ? evidence?.find(e => e.key === run?.key) : undefined;
  const divisionEvents = showDivisions ? evidence?.find(e => e.key === run?.key)?.events : undefined;
  const focusMetric = result?.metrics.event_focus;
  const fixedMetric = result?.metrics[fixedKey];
  const focusImages = run?.methods.event_focus.acquired_indices.length ?? 0;
  const fixedImages = run?.methods[fixedKey]?.acquired_indices.length ?? 0;
  const savings = fixedImages ? 100 * (1 - focusImages / fixedImages) : 0;
  const advantage = focusMetric && fixedMetric ? focusMetric.covered_events - fixedMetric.covered_events : 0;
  const aggregate = (key: string) => {
    const rows = evidence?.filter(e => manifest?.experiments.find(x => x.key === e.key)?.condition === condition) ?? [];
    return [rows.reduce((sum, row) => sum + row.metrics[key].covered_events, 0), rows.reduce((sum, row) => sum + row.metrics[key].events, 0)];
  };
  const totals = aggregate('event_focus'), fixedTotals = aggregate(fixedKey);
  const switchComparison = (value: string) => {
    if (value === comparison) return;
    setManifest(null); setEvidence(null); setRevealed(false); setEvidenceError(''); setShowResults(false);
    setPlaying(false); setT(0); setPhase(0); setSeed(value === 'efficiency' ? 304 : 2026); setComparison(value);
  };
  const seek = (value: number) => { setT(value); setPlaying(false); };
  const backToComparison = () => { window.scrollTo({ top: 0, behavior: 'instant' }); setShowResults(false); window.requestAnimationFrame(() => comparisonHeading.current?.focus({ preventScroll: true })); };
  const replay = () => { window.scrollTo({ top: 0, behavior: 'instant' }); setRevealed(false); setShowDivisions(false); setShowResults(false); setT(0); setPlaying(true); window.requestAnimationFrame(() => comparisonHeading.current?.focus({ preventScroll: true })); };
  const openResults = () => { setPlaying(false); setRevealed(true); setShowDivisions(true); setShowResults(true); };
  const burst = run?.methods.event_focus.decisions.find(d => (d.target_gap ?? 12) < 12)?.t;

  return <section id="controlled-lab" className="controlled-lab" aria-label="Controlled synthetic microscopy comparison">
    {!showResults ? <>
      <div className="demo-heading"><div><h1 id="lab-title" ref={comparisonHeading} tabIndex={-1}>Same specimen. <br/>Different timing.</h1><p>Selected synthetic run · {conditions.find(([key]) => key === condition)?.[1]} · seed {seed}</p></div><details className="experiment-settings"><summary>Experiment settings<span aria-hidden="true">+</span></summary><div className="settings-body">
        <label>Comparison<select aria-label="Comparison mode" value={comparison} onChange={e => switchComparison(e.target.value)}><option value="efficiency">Fewer images · 32 vs 40</option><option value="equal">Equal budget · 40 vs 40</option></select></label>
        <label>Scenario<select aria-label="Controlled scenario" value={condition} onChange={e => setCondition(e.target.value)}>{conditions.map(([key, label]) => <option value={key} key={key}>{label}</option>)}</select></label>
        <label>Seed<select aria-label="Controlled seed" value={seed} onChange={e => setSeed(Number(e.target.value))}>{[...new Set(manifest?.experiments.map(e => e.seed) ?? [seed])].map(s => <option value={s} key={s}>{s}{lowerBudget && s === 304 ? ' · featured' : ''}</option>)}</select></label>
        <label>{lowerBudget ? 'Fixed budget' : 'Fixed timing'}<select aria-label={lowerBudget ? 'Fixed capture budget' : 'Fixed timing offset'} value={phase} onChange={e => setPhase(Number(e.target.value))}>{lowerBudget ? <><option value={0}>40 images · reference</option><option value={1}>32 images · equal budget</option></> : <><option value={0}>Standard</option><option value={1}>+⅓ interval</option><option value={2}>+⅔ interval</option></>}</select></label>
        <label>Image view<select aria-label="Controlled image view" value={view} onChange={e => setView(e.target.value)}><option value="observed">Acquired pixels</option><option value="model">Gaussian fit · native CUDA Rust</option></select></label>
        <label>Playback<select aria-label="Controlled playback pace" value={pace} onChange={e => setPace(e.target.value)}><option value="quick">Constant speed · shared clock</option><option value="guided">Capture pauses · viewing aid</option></select></label>
        <p>Settings select saved experiments. Playback speed is a presentation aid, not a microscope exposure duration.</p>
      </div></details></div>
      {error ? <div className="peek-error" role="alert">{error}<Button variant="quiet" onClick={() => setRetry(v => v + 1)}>Retry</Button></div> : !run ? <p role="status">Loading the experiment…</p> : <>
        <div className="demo-layout"><div className="lab-pair">{[[fixedKey, 'Fixed schedule'], ['event_focus', 'Peekaboo']].map(([key, title]) => {
            const method = run.methods[key], indices = method.acquired_indices.filter(i => i <= t), source = indices.at(-1) ?? 0;
            const capture = source === t, decision = method.decisions[t];
            const changing = (decision?.target_gap ?? 12) < 12;
            const guarded = decision?.reason === 'budget coverage guard';
            return <article key={key} className={`lab-panel ${key === 'event_focus' ? 'adaptive' : ''}`} data-capturing={capture} data-changing={key === 'event_focus' && changing && !guarded && t > 0}>
              <header><h2>{title}</h2><span>{method.acquired_indices.length} image budget</span></header>
              <div className="lab-optical">{active ? <Microscope root={dataRoot} file={view === 'model' && run.model ? run.model : run.observed} frame={source} label={`${title}: ${view === 'model' ? 'Gaussian fit of acquired image' : 'acquired synthetic image'} at frame ${source}; replay clock ${t}`}/> : null}<CaptureFeedback source={source} running={playing && active}/><span className="optical-label">{view === 'model' ? 'Gaussian fit' : 'Acquired pixels'}</span></div>
              <div key={source} className={playing && source > 0 ? 'capture-update' : undefined}><CaptureStatus capture={capture} source={source} count={indices.length}/></div>
              <p className="panel-reason">{key === 'event_focus' ? <><span>{guarded ? 'Budget guard' : t === 0 ? 'First observation' : changing ? 'Shape changing' : 'Shape stable'}</span><strong>{guarded ? 'Capture required' : t === 0 ? 'Establish the starting point' : changing ? 'Capture sooner' : 'Wait longer'}</strong></> : <><span>Even spacing</span><strong>Every ~{((run.frame_count - 1) / (fixedImages - 1)).toFixed(1)} frames</strong></>}</p>
            </article>;
          })}</div></div>
        <div className="demo-playback">
          <div className="lab-transport"><button className="round-play" aria-label={playing ? 'Pause controlled replay' : 'Play controlled replay'} onClick={() => { if (t === 239) replay(); else setPlaying(v => !v); }}><Icon name={playing ? 'pause' : 'play'} size={18}/><span>{playing ? 'Pause comparison' : t === 239 ? 'Replay comparison' : 'Play comparison'}</span></button><button className="text-button" disabled={burst === undefined} onClick={() => seek(Math.max(0, (burst ?? 0) - 2))}>Find a burst<Arrow/></button><div className="division-controls"><button className="division-toggle" aria-pressed={showDivisions} onClick={() => setShowDivisions(value => !value)}>{showDivisions ? 'Hide divisions' : 'Show divisions'}</button>{divisionEvents ? <span className="division-legend"><span><i className="covered"/>Division covered</span><span><i/>Missed</span><small>Within ±1 frame</small></span> : showDivisions && !evidenceError ? <span role="status">Loading division markers…</span> : null}{showDivisions && evidenceError ? <button className="division-toggle" onClick={() => setEvidenceRetry(value => value + 1)}>Retry division markers</button> : null}</div><output className="replay-time">Frame {String(t).padStart(3, '0')}<span> / 239</span></output><Button variant="quiet" className="results-button" onClick={openResults}>{t === 239 ? 'View results' : 'Reveal run results'}<Arrow/></Button></div>
          <ComparisonTimeline run={run} fixedKey={fixedKey} t={t} events={divisionEvents} onSeek={seek}/>
        </div>

      </>}
    </> : <div className="results-view">
      <p className="result-context">{t === 239 ? 'Completed' : 'Full saved run'} · controlled synthetic experiment · seed {seed}{lowerBudget && seed === 304 ? ' · selected example' : ''}</p>
      <h1 tabIndex={-1} ref={resultHeading}>{!focusMetric ? 'What did we capture?' : !focusMetric.events ? <>A quiet specimen.<br/>No divisions to score.</> : advantage > 0 ? savings > 0 ? <>More divisions.<br/>Fewer captures.</> : <>More divisions.<br/>Same light budget.</> : advantage < 0 ? <>Some moments arrive<br/>without warning.</> : savings > 0 ? <>Same event coverage.<br/>Fewer exposures.</> : <>Same budget.<br/>Same event coverage.</>}</h1>
      {evidenceError ? <div className="peek-error" role="alert">{evidenceError}<Button variant="quiet" onClick={() => setEvidenceRetry(v => v + 1)}>Retry results</Button></div> : focusMetric && fixedMetric ? <>
        <div className="result-stats" aria-label="Demo results">
          <div><h2>Divisions captured</h2><div className="metric-pair"><p className="adaptive-value"><span>Peekaboo</span><strong>{focusMetric.events ? `${focusMetric.covered_events}/${focusMetric.events}` : '—'}</strong></p><p className="fixed-value"><span>Fixed schedule</span><strong>{fixedMetric.events ? `${fixedMetric.covered_events}/${fixedMetric.events}` : '—'}</strong></p></div><small>{focusMetric.events ? 'Within ±1 source frame' : 'No events in this control'}</small></div>
          <div><h2>Captures</h2><div className="metric-pair"><p className="adaptive-value"><span>Peekaboo</span><strong>{focusImages}</strong></p><p className="fixed-value"><span>Fixed schedule</span><strong>{fixedImages}</strong></p></div><small>Same {run?.frame_count}-frame experiment</small></div>
          <div className="light-metric"><h2>Estimated imaging light</h2><strong>{savings.toFixed(0)}<em>% less</em></strong><small>Equal illumination per capture assumed.</small></div>
        </div>
        <p className="result-interpretation">{!focusMetric.events ? 'This control has no divisions; event coverage is undefined.' : advantage > 0 ? 'Visible shape changes let Peekaboo concentrate its observations around division.' : advantage < 0 ? 'Without warning cues, the sparse schedule misses sudden divisions.' : 'This run shows no event-coverage advantage.'} Reduced imaging light is an exposure estimate. Cell health has not been measured.</p>
      </> : <p role="status">Loading evaluation-only results…</p>}
      <div className="result-actions"><Button onClick={replay}><Icon name="reset" size={18}/>Replay</Button><Button variant="quiet" disabled={!result} onClick={() => { if (cohortDetails.current) { cohortDetails.current.open = true; cohortDetails.current.querySelector('summary')?.focus(); cohortDetails.current.scrollIntoView({ block: 'nearest' }); } }}>Inspect evidence<Arrow/></Button><Button variant="quiet" onClick={backToComparison}><Arrow back/>Back to comparison</Button></div>
      {result && focusMetric && fixedMetric ? <SourceDisclosure detailsRef={cohortDetails} label="All-seed results & evidence"><div className="cohort-evidence"><div><h2>Across all six evaluation seeds</h2><p className="cohort-count">{totals[1] ? `${totals[0]} / ${totals[1]}` : 'No events'}<span>Peekaboo · {totals[1] ? `${fixedTotals[0]} / ${fixedTotals[1]} fixed` : 'quiet control'}</span></p><p>{conditions.find(([key]) => key === condition)?.[1]} · {focusImages} adaptive / {fixedImages} fixed images per run.</p><p>{condition === 'precursor' ? 'This simulator includes visible shape changes before programmed division.' : condition === 'abrupt' ? 'Without a visible precursor, this controller misses more sudden divisions than fixed timing.' : 'No divisions occur in the quiet control. The controller still spends its declared budget.'}</p><p>{lowerBudget ? 'Seed 304 was selected after evaluation to show a successful example. All six seeds remain available, including a missed division in seed 301. ' : ''}These results do not establish performance on real cells.</p><SourceLink href={`${dataRoot}evidence.json`}>Inspect the measured ledger</SourceLink></div><figure>{active ? <Microscope root={dataRoot} file={result.reference} frame={t} label={`Evaluation-only synthetic reference at frame ${t}`}/> : null}<figcaption>Evaluation-only reference · frame {t}<br/>Never available to the controller before acquisition.</figcaption></figure></div><SourceLink href="https://www.nature.com/articles/srep15348">Why light dose is not a health score</SourceLink></SourceDisclosure> : null}
    </div>}
    <SourceDisclosure label="Experiment design & limitations"><p>Four synthetic nuclei drift slowly. In the precursor condition each elongates for 24 frames before a programmed split. Sudden divisions remove that cue; quiet specimens have no divisions. Event times are randomized independently of fixed timing.</p><p>Acquired Gaussian shapes guide target gaps of 12, 4, or 2 frames. Feasibility guards preserve the declared {focusImages || 32}-image budget and a maximum gap of 12. Shape is a heuristic, not a calibrated biological forecast. The Gaussian view holds a fit of the last acquired frame and does not predict a split.</p><p>{lowerBudget ? 'The 32-image budget was declared before evaluation on seeds 301–306, compared with fixed at 40 and 32 images. ' : 'The 40-image experiment uses six evaluation seeds and three fixed timing offsets. '}Settings were developed separately. This controller spends its budget; this is not automatic discovery of the minimum images needed.</p><p>Both methods share one 240-frame experiment clock. Constant-speed playback and optional capture pauses are viewing aids. Native CUDA Rust rendered the saved model assets; the browser replays them. Real microscopy was evaluated separately and is available in the research archive.</p></SourceDisclosure>
  </section>;
}
