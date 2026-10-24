import { names, metricValue, frameState } from './replay.mjs';
import { Difference } from './ReplayView';
import type { Run, Evaluation as EvaluationData } from './types';

export function Evaluation({run, data, comparator, t, gaussian, onClose}: {run: Run; data: EvaluationData; comparator: string; t: number; gaussian: boolean; onClose?:()=>void}) {
  const photon = data.methods.photon;
  const other = data.methods[comparator];
  const truth = `/demo/images/${run.sequence_id}/${t}.png`;
  const prediction = frameState(run, 'photon', t, gaussian);
  const matched = photon.metrics;
  return <section className="evaluation" aria-label="Revealed offline evaluation">
    <div className="section-heading"><div><h2>The observations we withheld.</h2><p>GROUND TRUTH (EVAL ONLY) · Source frame {t}. This reveal never changes a decision.</p></div><div className="evaluation-actions"><span className="eval-label">EVALUATION MODE</span>{onClose?<button onClick={onClose}>Close evidence</button>:null}</div></div>
    <div className="reveal-images">
      <figure><img src={truth} alt={`GROUND TRUTH (EVAL ONLY): actual withheld volume at frame ${t}`}/><figcaption>GROUND TRUTH (EVAL ONLY) · {run.methods.photon.config.acquired_indices.includes(t) ? 'Also acquired by Glimpse at this time' : 'Withheld from Glimpse at this time'}</figcaption></figure>
      <figure><Difference key={`${truth}:${prediction.image}`} truth={truth} prediction={prediction.image}/><figcaption>Absolute display difference · truth vs {prediction.predicted ? 'Gaussian forecast' : 'Glimpse measurement'}. 8-bit MIP; not the full-volume metric.</figcaption></figure>
    </div>
    <div className="table-scroll"><table>
      <caption>Recorded whole-run results · equal budgets · {data.status}</caption>
      <thead><tr><th scope="col">Method</th><th scope="col">Images</th><th scope="col">Exposure proxy</th><th scope="col">Events covered ±1</th><th scope="col">Own withheld raw-hold MSE ↓</th><th scope="col">Own Gaussian forecast MSE ↓</th></tr></thead>
      <tbody>{[comparator, 'photon'].map(name => {const value = data.methods[name]; return <tr key={name} className={name === 'photon' ? 'accent' : ''}>
        <th scope="row">{names[name]}</th><td>{run.budget} / {run.frame_count}</td><td>{(run.budget / run.frame_count).toFixed(3)}</td>
        <td>{value.event.covered_events} / {value.event.events} <small>({(value.event.event_coverage * 100).toFixed(1)}%)</small></td>
        <td>{metricValue(value.metrics?.own_withheld.raw_hold.mse)}</td><td>{metricValue(value.metrics?.own_withheld.gaussian_forecast.mse)}</td>
      </tr>;})}</tbody>
    </table></div>
    <div className="findings"><p>{other.event.covered_events > photon.event.covered_events ? `${names[comparator]} covered ${other.event.covered_events - photon.event.covered_events} more annotated divisions than Glimpse in this condition.` : other.event.covered_events === photon.event.covered_events ? 'Both schedules covered the same number of annotated divisions in this condition.' : `Glimpse covered ${photon.event.covered_events - other.event.covered_events} more annotated divisions in this condition.`} Coverage is retrospective capture timing, not event detection.</p>
      <p>{data.reason ?? `Image scores are first-pass; independent source rerender is pending. Scalar accounting: ${data.accounting.replaceAll('_', ' ')}.`} Own-withheld target sets differ between schedules and can reverse rankings.</p></div>
    <details><summary>Matched-target comparison & metric provenance</summary><div className="detail-body">
      <p>Fixed vs Glimpse only: {matched ? `${matched.matched_fixed.raw_hold.frames} common withheld volumes. Raw-hold MSE: fixed ${metricValue(matched.fixed_on_matched.raw_hold.mse)}, Glimpse ${metricValue(matched.matched_fixed.raw_hold.mse)}.` : 'Pending / not computed.'} These matched targets depend on both schedules; a gain here does not establish overall superiority.</p>
      <p>Scores use normalized full 3D volumes and the first-acquired-frame calibration. Display projections and 8-bit difference images are not used for these metrics. Exposure proxy = acquired volumes / total source volumes; biological phototoxicity was not measured.</p>
      {[comparator, 'photon'].map(name => <p key={name}>{names[name]}: {data.methods[name].metrics_source ? <a href={`/demo/${data.methods[name].metrics_source}`} target="_blank" rel="noreferrer">Original metrics.json</a> : 'image metrics pending'}</p>)}
      <a href="/demo/sources/runs/phase5/event-audit.json" target="_blank" rel="noreferrer">All 36 original event audits</a>
    </div></details>
  </section>;
}
