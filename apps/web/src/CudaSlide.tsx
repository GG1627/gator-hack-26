import { useRef, useState, type KeyboardEvent } from 'react';
import { Microscope } from './Microscope';
import { Arrow, SourceDisclosure, SourceLink } from './PeekabooUI';

const frameWidth = 64;
const frameHeight = 64;
const valuesPerTile = 128;
const tileCount = frameWidth * frameHeight / valuesPerTile;

function ParameterSketch() {
  return <svg viewBox="0 0 280 230" role="img" aria-label="Conceptual fitted Gaussian parameters: centers, elliptical spread and peak intensity">
    <defs><radialGradient id="cuda-parameter-glow"><stop stopColor="#f6d48b" stopOpacity=".7"/><stop offset="1" stopColor="#d99b50" stopOpacity="0"/></radialGradient></defs>
    {[[70, 65, 28, 21, -15], [204, 65, 34, 19, 10], [70, 168, 34, 19, -35], [204, 168, 21, 32, 10]].map(([x, y, rx, ry, angle], index) => <g key={index} transform={`translate(${x} ${y}) rotate(${angle})`}><ellipse rx={rx * 1.5} ry={ry * 1.5} fill="url(#cuda-parameter-glow)"/>{[1, 0.7, 0.4].map(scale => <ellipse key={scale} rx={rx * scale} ry={ry * scale} fill="none" stroke="currentColor" strokeWidth=".9"/>)}<path d={`M${-rx - 10} 0H${rx + 10}M0 ${-ry - 10}V${ry + 10}`} stroke="currentColor" strokeWidth=".6" strokeDasharray="3 5" opacity=".55"/><circle r="2" fill="currentColor"/></g>)}
  </svg>;
}

export function CudaSlide() {
  const [selected, setSelected] = useState(10);
  const buttons = useRef<(HTMLButtonElement | null)[]>([]);
  const first = selected * valuesPerTile;
  const last = first + valuesPerTile - 1;
  const keyTile = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    const columns = window.matchMedia('(max-width: 760px)').matches ? 4 : 8;
    const offsets: Record<string, number | undefined> = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -columns, ArrowDown: columns };
    const offset = offsets[event.key];
    if (offset === undefined && event.key !== 'Home' && event.key !== 'End') return;
    event.preventDefault(); event.stopPropagation();
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? tileCount - 1 : Math.max(0, Math.min(tileCount - 1, index + offset!));
    setSelected(next); buttons.current[next]?.focus();
  };
  return <>
    <div className="slide-heading cuda-heading"><h1 tabIndex={-1}>One model. Many pixels.</h1><p>Our CUDA Rust kernel renders Gaussian intensity in parallel.</p></div>
    <div className="cuda-render-flow">
      <article className="cuda-parameters"><h2>Fitted Gaussian parameters</h2><div className="cuda-parameter-visual"><ParameterSketch/></div><p className="cuda-parameter-label">Position · shape · brightness</p><p className="cuda-stage-caption">CPU: fit acquired pixels</p></article>
      <Arrow/>
      <article className="cuda-chip"><header><h2>NVIDIA CUDA Rust</h2><p>cuTile · {valuesPerTile} output values per tile</p></header>
        <div className="cuda-tile-grid" role="group" aria-label="Inspect logical output tiles">{Array.from({ length: tileCount }, (_, index) => <button key={index} ref={node => { buttons.current[index] = node; }} aria-label={`Inspect tile ${index + 1}`} title={`Output positions ${index * valuesPerTile}–${(index + 1) * valuesPerTile - 1}`} aria-pressed={selected === index} tabIndex={selected === index ? 0 : -1} onClick={() => setSelected(index)} onKeyDown={event => keyTile(event, index)}>{String(index + 1).padStart(2, '0')}</button>)}</div>
        <output className="cuda-tile-readout" aria-live="polite"><strong>Tile {selected + 1}</strong><span>Positions {first}–{last}</span></output>
      </article>
      <Arrow/>
      <article className="cuda-result"><h2>Rendered intensity</h2><div className="cuda-output-window"><Microscope file="304-precursor-model.png" frame={0} label="Actual saved native CUDA Rust Gaussian intensity output, synthetic seed 304, acquired frame 0"/><span className="cuda-output-band" style={{ top: `${first / (frameWidth * frameHeight) * 100}%`, height: `${valuesPerTile / (frameWidth * frameHeight) * 100}%` }} aria-hidden="true"/></div><p className="cuda-stage-caption">Saved native output · frame 0</p><p className="cuda-output-size">64 × 64 values</p></article>
    </div>
    <p className="cuda-illustration-note">Select a tile to inspect its output positions. Illustrative tiling · saved output.</p>
    <div className="cuda-role-strip"><p><span>CPU</span> chooses when to capture.</p><p><span>GPU</span> renders the model.</p><small>Checked against a CPU reference.</small></div>
    <SourceDisclosure label="Kernel, checks & sources"><p>The native cuTile Rust kernel partitions output into tiles of 128 positions. For each position it evaluates Gaussian contributions, sums them, applies the truncation rule and clips the accumulated intensity. The tile map shows the 32 logical tiles in a 64 × 64 saved frame; padded launch positions are omitted. Each selected tile corresponds to two complete output rows, not a rectangular 8 × 4 partition of the image.</p><p>The tile selector is a browser illustration. It changes the overlay only; the image is actual previously rendered native CUDA Rust output from the same acquired synthetic frame 0. No CUDA kernel executes in this browser.</p><p>Fitting and acquisition decisions stay on CPU. Native code receives Gaussian descriptors and public output dimensions, not microscopy files, hidden images or event labels. The Python bridge also checks and repairs flagged truncation-boundary values against the CPU reference.</p><p>Saved exports checked kernel execution and numerical agreement against the CPU renderer. Separate latency audits include startup, transfers and the full bridge: GPU rendering helps some dense synthetic workloads, while the CPU remains faster for the tested sparse real-volume prediction path. Device-only timing is not a whole-application speedup.</p><SourceLink href="https://github.com/GG1627/gator-hack-26/blob/main/crates/photon-gpu/src/main.rs">Our native Rust kernel</SourceLink><SourceLink href="/demo/controlled/budget32/export-verification.json">Saved render verification</SourceLink><SourceLink href="https://github.com/NVlabs/cutile-rs/blob/main/CHANGELOG.md">cuTile Rust · initial tagged release April 7, 2026</SourceLink><SourceLink href="https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels/">NVIDIA CUDA Rust announcement · September 8, 2026</SourceLink></SourceDisclosure>
  </>;
}
