import { useMemo, useState } from 'react';
import { Microscope } from './Microscope';
import { Arrow, Button, SourceDisclosure, SourceLink } from './PeekabooUI';

type Parameters = { position: number; shape: number; brightness: number };
const initial: Parameters = { position: 0, shape: 1.6, brightness: 0.8 };
type Point = [number, number];

// Educational analytic Gaussian. This does not fit pixels or run the controller.
function makeSurface({ position, shape, brightness }: Parameters) {
  const center = position * 0.85;
  const sx = 0.72 * Math.sqrt(shape), sy = 0.72 / Math.sqrt(shape);
  const intensity = (x: number, y: number) => brightness * Math.exp(-0.5 * (((x - center) / sx) ** 2 + (y / sy) ** 2));
  const project = (x: number, y: number, z = 0): Point => [260 + (x - y) * 40, 202 + (x + y) * 14 - z * 190];
  const coords = (point: Point) => point.map(value => value.toFixed(2)).join(',');
  const cells = [];
  const count = 26, extent = 2.7, step = extent * 2 / count;
  for (let j = 0; j < count; j++) for (let i = 0; i < count; i++) {
    const x = -extent + i * step, y = -extent + j * step;
    const vertices = [[x, y], [x + step, y], [x + step, y + step], [x, y + step]];
    const height = vertices.reduce((sum, [px, py]) => sum + intensity(px, py), 0) / 4;
    cells.push({ key: `${i}-${j}`, depth: x + y, points: vertices.map(([px, py]) => coords(project(px, py, intensity(px, py)))).join(' '), opacity: 0.02 + height * 0.8, strokeOpacity: 0.06 + height * 0.58 });
  }
  cells.sort((a, b) => a.depth - b.depth);
  const grid = [-2.7, -1.35, 0, 1.35, 2.7].flatMap(value => [
    `${coords(project(-extent, value))} ${coords(project(extent, value))}`,
    `${coords(project(value, -extent))} ${coords(project(value, extent))}`,
  ]);
  const contours = [1, 2, 3].map(radius => Array.from({ length: 73 }, (_, i) => {
    const angle = i / 72 * Math.PI * 2;
    return coords(project(center + Math.cos(angle) * sx * radius, Math.sin(angle) * sy * radius));
  }).join(' '));
  return { cells, grid, contours, center: project(center, 0), peak: project(center, 0, brightness) };
}

function ParameterControl({ name, description, value, valueText, min, max, step, onChange }: { name: string; description: string; value: number; valueText: string; min: number; max: number; step: number; onChange: (value: number) => void }) {
  const id = `gaussian-${name.toLowerCase()}`;
  return <div className="gaussian-control">
    <label htmlFor={id}><strong>{name}</strong><span>{description}</span></label>
    <div className="gaussian-range"><output htmlFor={id}>{valueText}</output><input id={id} aria-label={`Gaussian ${name.toLowerCase()}`} aria-valuetext={valueText} type="range" min={min} max={max} step={step} value={value} onChange={event => onChange(Number(event.target.value))}/></div>
  </div>;
}

export function GaussianSlide() {
  const [parameters, setParameters] = useState(initial);
  const surface = useMemo(() => makeSurface(parameters), [parameters]);
  const update = (key: keyof Parameters, value: number) => setParameters(previous => ({ ...previous, [key]: value }));
  const positionText = Math.abs(parameters.position) < 0.1 ? 'Centered' : parameters.position < 0 ? 'Left' : 'Right';
  return <>
    <div className="gaussian-explainer">
      <div className="gaussian-heading"><h1 tabIndex={-1}>What is a Gaussian?</h1><p>Bright at the center. Fainter toward the edges.</p></div>
      <figure className="gaussian-surface">
        <svg viewBox="0 0 520 300" role="img" aria-label={`Conceptual Gaussian intensity surface: ${positionText.toLowerCase()}, shape ratio ${parameters.shape.toFixed(1)}, relative peak ${Math.round(parameters.brightness * 100)} percent`}>
          <g className="gaussian-plane">{surface.grid.map((points, index) => <polyline key={index} points={points}/>)}<g className="gaussian-contours">{surface.contours.map((points, index) => <polyline key={index} points={points}/>)}</g></g>
          <g className="gaussian-mesh">{surface.cells.map(cell => <polygon key={cell.key} points={cell.points} fill={`rgba(246, 194, 100, ${cell.opacity.toFixed(3)})`} stroke={`rgba(246, 212, 139, ${cell.strokeOpacity.toFixed(3)})`}/>)}</g>
          <line className="gaussian-axis" x1={surface.center[0]} y1={surface.center[1]} x2={surface.peak[0]} y2={surface.peak[1]}/>
          <circle className="gaussian-peak" cx={surface.peak[0]} cy={surface.peak[1]} r="3"/>
        </svg>
        <figcaption>Conceptual Gaussian · interactive · relative units</figcaption>
      </figure>
      <div className="gaussian-controls">
        <ParameterControl name="Position" description="Where the signal sits." value={parameters.position} valueText={positionText} min={-1} max={1} step={0.05} onChange={value => update('position', value)}/>
        <ParameterControl name="Shape" description="Spread and elongation." value={parameters.shape} valueText={`${parameters.shape.toFixed(1)}×`} min={1} max={2.5} step={0.1} onChange={value => update('shape', value)}/>
        <ParameterControl name="Brightness" description="Relative peak intensity." value={parameters.brightness} valueText={`${Math.round(parameters.brightness * 100)}%`} min={0.35} max={1} step={0.05} onChange={value => update('brightness', value)}/>
        <Button className="gaussian-reset" variant="quiet" onClick={() => setParameters(initial)}>Reset model</Button>
      </div>
    </div>
    <div className="gaussian-application">
      <div className="gaussian-saved-example"><figure><figcaption>Acquired image</figcaption><Microscope file="304-precursor-observed.png" frame={0} label="Actual acquired synthetic pixels from seed 304, frame 0"/></figure><Arrow/><figure><figcaption>Saved Gaussian fit</figcaption><Microscope file="304-precursor-model.png" frame={0} label="Actual saved native CUDA Rust Gaussian fit of the same acquired frame 0"/></figure><p>Synthetic example · frame 0</p></div>
      <div className="gaussian-purpose"><h2>From pixels to timing</h2><p>Peekaboo measures shape change across acquired images to choose when to look again.</p></div>
    </div>
    <SourceDisclosure><p>A Gaussian is a smooth intensity function described by a center, covariance (spread and orientation), and peak amplitude. The interactive surface illustrates one analytic Gaussian in relative units; its sliders do not alter a scientific run. Intensity height is not cell height.</p><p>Our CPU fitter estimates intensity-weighted position and covariance from acquired signal, then fits peak amplitude. The controlled-demo policy uses fitted aspect ratios and changes between acquisitions to adjust the target capture gap. Brightness is part of the image model, not a cell-health score or a division probability.</p><p>The small image pair uses the same acquired frame of the saved synthetic experiment. The fit is actual native CUDA Rust output and stays unchanged when you adjust the conceptual surface. Fits are held between captures; this view does not predict a split. Shapes approximate fluorescent intensity rather than verified cell boundaries.</p><p>Inspired by CellSplat4D, first submitted October 3, 2026. This is a scoped Gaussian approximation, not a reproduction of the full paper's PSF-aware 4D model or training pipeline.</p><SourceLink href="https://arxiv.org/abs/2610.04199">CellSplat4D · Tao & Lu, October 2026</SourceLink></SourceDisclosure>
  </>;
}
