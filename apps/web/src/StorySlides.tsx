import { Arrow, Button, SourceDisclosure, SourceLink } from './PeekabooUI';
import { Microscope } from './Microscope';
import { OpeningArtwork } from './OpeningArtwork';
import { GaussianSlide } from './GaussianSlide';
import { CudaSlide } from './CudaSlide';


function GaussianSketch() {
  return <svg className="gaussian-sketch" viewBox="0 0 300 240" role="img" aria-label="Conceptual Gaussian shapes: fitted centers, orientation, and spread">
    <defs><radialGradient id="gaussian-fill"><stop stopColor="#D99B50" stopOpacity=".55"/><stop offset="1" stopColor="#D99B50" stopOpacity="0"/></radialGradient></defs>
    {[[88, 75, 40, 27, -25], [208, 62, 31, 23, 22], [172, 164, 51, 29, 35], [67, 183, 22, 32, -16]].map(([x,y,rx,ry,angle],i)=><g key={i} transform={`translate(${x} ${y}) rotate(${angle})`}><ellipse rx={rx*1.7} ry={ry*1.7} fill="url(#gaussian-fill)"/><ellipse rx={rx} ry={ry} fill="none" stroke="currentColor" strokeWidth=".8"/><path d={`M${-rx} 0H${rx}M0 ${-ry}V${ry}`} stroke="currentColor" strokeWidth=".6" strokeDasharray="2 4"/><circle r="2" fill="currentColor"/></g>)}
  </svg>;
}

function AcquisitionLoop() {
  return <div className="acquisition-loop">
    <div className="workflow-stages">
      <article className="workflow-stage">
        <header><span>01</span><h2>Observe</h2></header>
        <figure><div className="workflow-visual"><Microscope file="304-precursor-observed.png" frame={0} label="Actual acquired synthetic image from the saved experiment, frame 0"/></div><figcaption>Acquired synthetic image · frame 0</figcaption></figure>
        <p className="workflow-action">Acquire a real observation.</p>
      </article>
      <Arrow/>
      <article className="workflow-stage">
        <header><span>02</span><h2>Estimate</h2></header>
        <figure><div className="workflow-visual workflow-model"><GaussianSketch/></div><figcaption>Gaussian shape estimates · conceptual</figcaption></figure>
        <p className="workflow-action">Fit shapes. Measure change.</p>
      </article>
      <Arrow/>
      <article className="workflow-stage">
        <header><span>03</span><h2>Decide</h2></header>
        <div className="workflow-visual workflow-decision">
          <svg className="decision-branches" viewBox="0 0 320 240" preserveAspectRatio="none" aria-hidden="true"><path className="wait-branch" d="M16 120C66 120 64 70 110 70M101 62L111 70L101 78"/><path className="capture-branch" d="M16 120C66 120 64 170 110 170M101 162L111 170L101 178"/></svg>
          <div className="decision-options"><div className="decision-wait"><span>Stable shapes</span><strong>Wait longer</strong></div><div className="decision-capture"><span>Changing shapes</span><strong>Capture sooner</strong></div></div>
        </div>
        <p className="decision-budget">Within the remaining image budget</p>
      </article>
    </div>
    <div className="workflow-return"><svg viewBox="0 0 1000 46" preserveAspectRatio="none" aria-hidden="true"><path d="M880 2V20Q880 35 865 35H135Q120 35 120 20V2M113 10L120 2L127 10"/></svg><p>Repeat after the next capture</p></div>
    <p className="workflow-caption">Conceptual workflow · model sketch and decision branches are illustrative.</p>
  </div>;
}

function ProblemTimeline() {
  return <figure className="problem-timeline">
    <svg viewBox="0 0 440 96" role="img" aria-label="Conceptual timing: frequent captures include a brief division, while sparse captures fall on either side and miss it">
      <rect className="division-window" x="225" y="12" width="28" height="74" rx="5"/>
      <text x="0" y="38">Frequent</text><text x="0" y="74">Sparse</text>
      {[34, 70].map(y => <line key={y} className="problem-track" x1="100" x2="432" y1={y} y2={y}/>)}
      {Array.from({ length: 19 }, (_, i) => 104 + i * 18).map(x => <line key={x} className="problem-capture" x1={x} x2={x} y1="26" y2="42"/>)}
      {[104, 184, 264, 344, 424].map(x => <line key={x} className="problem-capture sparse" x1={x} x2={x} y1="62" y2="78"/>)}
    </svg>
    <figcaption><span>Conceptual timing</span><span><i aria-hidden="true"/>Brief division</span></figcaption>
  </figure>;
}

export function StorySlide({ index, onStart, onApproach, active = true }: { index: number; onStart: () => void; onApproach: () => void; active?: boolean }) {
  if (index === 0) return <>
    <div className="opening-copy"><h1 tabIndex={-1}>See more.<br/>Illuminate less.</h1><p>A better moment to look.</p><Button onClick={onStart}>Start the story<Arrow/></Button></div>
    <OpeningArtwork active={active}/>
  </>;
  if (index === 1) return <>
    <div className="slide-heading"><h1 tabIndex={-1}>How do you watch living cells<br/>{' '}without disrupting them?</h1></div>
    <div className="problem-composition"><figure className="real-specimen"><img src="/demo/images/mskcc_confocal_s2/0.png" alt="Real confocal image of fluorescent nuclei in a C. elegans embryo" width="512" height="512"/><figcaption>Real microscopy · C. elegans embryo</figcaption></figure>
      <div className="problem-copy"><p className="problem-explanation">Repeated imaging exposes cells to light that can stress or damage them.</p>
        <div className="problem-tradeoffs"><div><h2>Capture too often</h2><p>Unnecessary light exposure.</p></div><div><h2>Capture too rarely</h2><p>Important divisions can be missed.</p></div></div>
        <ProblemTimeline/>
      </div>
    </div>
    <p className="problem-question">When is another picture worth taking?</p>
    <SourceDisclosure><p>Fluorescence illumination can cause photobleaching and phototoxic effects. The response depends on wavelength, dose, labeling, and specimen. Our prototype measures acquisition counts and an exposure proxy, not cell health. The timing diagram is conceptual; the microscopy image provides dataset context.</p><SourceLink href="https://www.nature.com/articles/srep15348">Wäldchen et al. · light-induced cellular damage, 2015</SourceLink><SourceLink href="https://www.nature.com/articles/s41467-025-66209-6">PhotoFiTT · measuring phototoxicity, 2025</SourceLink><SourceLink href="https://celltrackingchallenge.net/3d-datasets/">Cell Tracking Challenge · MSKCC-CONFOCAL dataset</SourceLink><p>Image: MSKCC-CONFOCAL, sequence 02, frame 0. Maximum-intensity projection, original 512 px, rounded to 8-bit using the first-acquisition normalization. No generated imagery is used in this scientific display.</p></SourceDisclosure>
  </>;
  if (index === 2) return <>
    <div className="solution-copy"><h1 tabIndex={-1}>Meet<br/>{' '}Peekaboo.</h1><p className="solution-tagline">A better moment to look.</p><p className="solution-explanation">Software that chooses when a microscope takes its next image.</p><Button onClick={onApproach}>How it works<Arrow/></Button></div>
    <figure className="solution-art"><img src="/peekaboo/solution-capybara.png" alt="Illustrated capybara scientist presenting a blue microscope, stepping back to wait for the next observation" width={1374} height={1145}/></figure>
  </>;
  if (index === 3) return <>
    <div className="slide-heading"><h1 tabIndex={-1}>How does Peekaboo decide?</h1><p>Observe. Estimate. Decide.</p></div>
    <AcquisitionLoop/>
    <SourceDisclosure label="How the decision works"><p>The controlled-demo policy fits acquired pixels, measures aspect ratio, and shortens its target gap from 12 to 4 or 2 frames when shape changes. Budget guards preserve the declared capture count and maximum gap. This is a heuristic cue, not a calibrated probability of division.</p><p>Only acquired observations inform decisions. Hidden event times and future images remain unavailable to the controller. The demo will also let you inspect sudden divisions without a visible precursor.</p></SourceDisclosure>
  </>;
  if (index === 4) return <GaussianSlide/>;
  return <CudaSlide/>;
}
