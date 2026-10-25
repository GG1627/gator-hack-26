import { Arrow, Button, SourceDisclosure, SourceLink } from './PeekabooUI';
import { Microscope } from './Microscope';
import { OpeningArtwork } from './OpeningArtwork';

const paper = 'https://arxiv.org/abs/2610.04199';
const rust = 'https://github.com/NVlabs/cutile-rs/blob/main/CHANGELOG.md';

function GaussianSketch() {
  return <svg className="gaussian-sketch" viewBox="0 0 300 240" role="img" aria-label="Conceptual Gaussian shapes: fitted centers, orientation, and spread">
    <defs><radialGradient id="gaussian-fill"><stop stopColor="#D99B50" stopOpacity=".55"/><stop offset="1" stopColor="#D99B50" stopOpacity="0"/></radialGradient></defs>
    {[[88, 75, 40, 27, -25], [208, 62, 31, 23, 22], [172, 164, 51, 29, 35], [67, 183, 22, 32, -16]].map(([x,y,rx,ry,angle],i)=><g key={i} transform={`translate(${x} ${y}) rotate(${angle})`}><ellipse rx={rx*1.7} ry={ry*1.7} fill="url(#gaussian-fill)"/><ellipse rx={rx} ry={ry} fill="none" stroke="currentColor" strokeWidth=".8"/><path d={`M${-rx} 0H${rx}M0 ${-ry}V${ry}`} stroke="currentColor" strokeWidth=".6" strokeDasharray="2 4"/><circle r="2" fill="currentColor"/></g>)}
  </svg>;
}

function TimingSketch({ adaptive = false }: { adaptive?: boolean }) {
  const ticks = adaptive ? [8, 61, 114, 156, 164, 172, 180, 188, 224, 278] : [8, 38, 68, 98, 128, 158, 188, 218, 248, 278];
  return <svg className="timing-sketch" viewBox="0 0 290 54" role="img" aria-label={adaptive ? 'Concept: spaced observations, then a burst around change' : 'Concept: evenly spaced captures'}><line x1="0" x2="290" y1="27" y2="27"/>{ticks.map((x,i)=><line key={i} x1={x} x2={x} y1={adaptive && x>150 && x<200 ? '10' : '18'} y2={adaptive && x>150 && x<200 ? '44' : '36'} className={adaptive && x>150 && x<200 ? 'emphasis' : ''}/>)}</svg>;
}

export function StorySlide({ index, onStart, active = true }: { index: number; onStart: () => void; active?: boolean }) {
  if (index === 0) return <>
    <div className="opening-copy"><h1 tabIndex={-1}>See more.<br/>Illuminate less.</h1><p>A better moment to look.</p><Button onClick={onStart}>Start the story<Arrow/></Button></div>
    <OpeningArtwork active={active}/>
  </>;
  if (index === 1) return <>
    <div className="slide-heading"><h1 tabIndex={-1}>Every observation<br/>has an exposure cost.</h1></div>
    <div className="problem-composition"><figure className="real-specimen"><img src="/demo/images/mskcc_confocal_s2/0.png" alt="Real confocal image of fluorescent nuclei in a C. elegans embryo" width="512" height="512"/><figcaption>Real microscopy · C. elegans embryo<br/>MSKCC-CONFOCAL · sequence 02, frame 0 · maximum-intensity projection</figcaption></figure>
      <div className="problem-copy"><p className="large-statement">Light reveals cells.<br/>Repeated exposure<br/>can disturb them.</p><div className="exposure-example"><span>Fixed-interval imaging</span><TimingSketch/><small>Same rhythm, whether anything changes or not.</small></div></div>
    </div>
    <SourceDisclosure><p>Fluorescence illumination can cause photobleaching and phototoxic effects. The response depends on wavelength, dose, labeling, and specimen. Our prototype measures acquisition counts and an exposure proxy, not cell health.</p><SourceLink href="https://www.nature.com/articles/srep15348">Wäldchen et al. · light-induced cellular damage, 2015</SourceLink><SourceLink href="https://www.nature.com/articles/s41467-025-66209-6">PhotoFiTT · measuring phototoxicity, 2025</SourceLink><SourceLink href="https://celltrackingchallenge.net/3d-datasets/">Cell Tracking Challenge · MSKCC-CONFOCAL dataset</SourceLink><p>Image: original 512 px projection, rounded to 8-bit using the first-acquisition normalization. No generated imagery is used in this scientific display.</p></SourceDisclosure>
  </>;
  if (index === 2) return <>
    <div className="slide-heading"><h1 tabIndex={-1}>Choose when to look.</h1><p>Wait through quiet periods. Look more often when acquired shapes change.</p></div>
    <div className="approach-flow"><figure><div className="concept-observation"><Microscope file="304-precursor-observed.png" frame={0} label="Acquired synthetic observation at frame 0"/></div><figcaption><span>01</span><h2>Observe</h2><p>Acquire an image.</p></figcaption></figure><Arrow/>
      <figure><GaussianSketch/><figcaption><span>02</span><h2>Estimate</h2><p>Measure shape and change.</p></figcaption></figure><Arrow/>
      <figure><div className="timing-illustration"><small>Stable</small><TimingSketch/><small>Changing</small><TimingSketch adaptive/></div><figcaption><span>03</span><h2>Decide</h2><p>Spend the next exposure.</p></figcaption></figure></div>
    <p className="visual-caption">Conceptual sequence · acquired synthetic image, illustrative model and timing</p>
    <SourceDisclosure label="How the decision works"><p>The controlled-demo policy fits acquired pixels, measures aspect ratio, and shortens its target gap from 12 to 4 or 2 frames when shape changes. Budget guards preserve the declared capture count and maximum gap. This is a heuristic cue, not a calibrated probability of division.</p><p>Only acquired observations inform decisions. Hidden event times and future images remain unavailable to the controller. The demo will also let you inspect sudden divisions without a visible precursor.</p></SourceDisclosure>
  </>;
  if (index === 3) return <>
    <div className="slide-heading"><h1 tabIndex={-1}>Turn observations into<br/>a compact model.</h1><p>Gaussian components describe intensity, position, and shape.</p></div>
    <div className="model-comparison"><figure><Microscope file="304-precursor-observed.png" frame={0} label="Acquired synthetic pixels, featured run, frame 0"/><figcaption><h2>Acquired image</h2><span>Synthetic observation · frame 0</span></figcaption></figure><span className="model-transfer"><Arrow/></span><figure><Microscope file="304-precursor-model.png" frame={0} label="Native CUDA Rust Gaussian fit of that same acquired synthetic frame"/><figcaption><h2>Gaussian fit</h2><span>Actual saved output · native CUDA Rust</span></figcaption></figure></div>
    <SourceDisclosure><p>Inspired by CellSplat4D, first submitted October 3, 2026. Peekaboo implements a simplified Gaussian model, not the full paper's PSF-aware 4D reconstruction or neural training pipeline. Shapes represent fitted intensity, not verified cell boundaries.</p><SourceLink href={paper}>CellSplat4D · Tao & Lu, October 2026</SourceLink><p>The two images above come from the same acquired frame of the controlled synthetic experiment. The model is held between acquisitions; this view does not predict a split.</p></SourceDisclosure>
  </>;
  return <>
    <div className="slide-heading"><h1 tabIndex={-1}>Render the model<br/>with CUDA Rust.</h1><p>A native CUDA Rust kernel turns Gaussian parameters into intensity images.</p></div>
    <div className="compute-flow"><article><span className="compute-number">01 / CPU</span><GaussianSketch/><h2>Fit & schedule</h2><p>Acquired pixels → shapes<br/>Shapes → capture decisions</p></article><Arrow/>
      <article className="kernel-stage"><span className="compute-number">02 / NATIVE GPU</span><div className="kernel-glyph" aria-hidden="true">{'{'}<span>G</span>{'}'}</div><h2>Render in Rust</h2><p>Gaussian intensity evaluation<br/>cuTile Rust · CPU parity verified</p></article><Arrow/>
      <article><span className="compute-number">03 / BROWSER</span><div className="replay-symbol" aria-hidden="true"><i/><i/><i/><span>▶</span></div><h2>Replay & compare</h2><p>Saved causal experiments<br/>Measured acquisition outcomes</p></article></div>
    <SourceDisclosure><SourceLink href={rust}>cuTile Rust · initial tagged release April 7, 2026</SourceLink><SourceLink href="https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels/">NVIDIA CUDA Rust announcement · September 8, 2026</SourceLink><p>The custom native kernel renders Gaussian intensity. Fitting and scheduling stay on CPU. The browser replays saved assets and does not run CUDA. Numerical parity was checked against a CPU reference; GPU device timing is not a complete-application speedup.</p><p>Practical difficulties included kernel boundaries, host/device transfer costs, and predicting events without advance cues. Fixed schedules still captured more annotated divisions in the real held-out Phase 5 benchmark. Explore the research archive for that separate experiment.</p></SourceDisclosure>
  </>;
}
