import hashlib
import json
import math
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1];folder=root/'runs/appearance-forecast-probe';base=root/'runs/perception-controller-ablation'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
summary=json.loads((folder/'summary.json').read_text());protocol=summary['protocol']
registration=json.loads((folder/'registration.json').read_text())
assert sha(folder/'protocol.json')==registration['protocol_sha256']==summary['protocol_sha256']
assert sha(folder/'source.zip')==registration['source_zip_sha256']
with zipfile.ZipFile(folder/'source.zip') as archive:
    assert archive.testzip() is None
    for path,expected in protocol['source_sha256'].items():
        assert sha(root/path)==expected
        assert hashlib.sha256(archive.read(Path(path).as_posix())).hexdigest()==expected
assert sha(base/'summary.json')==protocol['input_summary_sha256']
assert sha(base/'verification.json')==protocol['input_verification_sha256']
for path,expected in summary['image_sha256'].items(): assert sha(root/path)==expected
configs={name:json.loads((base/name/'config.json').read_text()) for name in protocol['methods']}
ledgers={name:{row['t']:row for row in map(json.loads,(base/name/'evaluation.jsonl').read_text().splitlines())} for name in protocol['methods']}
expected={(name,t) for name in protocol['methods'] for t in protocol['targets'] if t not in configs[name]['acquired_indices']}
assert {(r['method'],r['target']) for r in summary['rows']}==expected
assert len(summary['rows'])==len(expected)
baseline_checks=0
for row in summary['rows']:
    history=[t for t in configs[row['method']]['acquired_indices'] if t<row['target']]
    assert row['based_on_indices']==history and row['last_acquired']==history[-1]
    assert row['horizon']==row['target']-history[-1]
    assert row['common_target']==all(row['target'] not in c['acquired_indices'] for c in configs.values())
    for estimator in ['raw_hold','gaussian_forecast']:
        reference=ledgers[row['method']][row['target']]['errors'][estimator]
        for metric,total in [('mse','squared_error_sum'),('mae','absolute_error_sum')]:
            assert math.isclose(row['scores'][estimator][metric],reference[total]/reference['voxel_count'],rel_tol=1e-12,abs_tol=1e-14)
            baseline_checks+=1
excluded={(name,t) for name in protocol['methods'] for t in protocol['targets'] if t in configs[name]['acquired_indices']}
assert {(r['method'],r['target']) for r in summary['exclusions']}==excluded
wins={name:{metric:sum(row['scores']['appearance_corrected'][metric]<row['scores']['raw_hold'][metric] for row in summary['rows'] if row['method']==name)
            for metric in ['mse','mae']} for name in protocol['methods']}
runtime=(folder/'summary.json').stat().st_mtime-(folder/'protocol.json').stat().st_mtime
verification={'verified':True,'scope':'source/archive/input-image/causal-history checks and baseline-score agreement',
    'summary_sha256':sha(folder/'summary.json'),'rows':len(expected),'excluded':len(excluded),
    'baseline_scalar_checks':baseline_checks,'corrected_vs_raw_hold_wins':wins,
    'independent_corrected_volume_rerender':False,'post_registration_seconds':runtime,
    'runtime_note':'Filesystem interval from protocol registration to summary; excludes initial imports/input checks and is not a benchmark.',
    'verification_script_sha256':sha(Path(__file__))}
(folder/'verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
lines=['# Appearance-preserving forecast probe','',
    'Selected, previously inspected development s1 targets. This is not a full benchmark or a generalization result.','',
    '| Schedule | Target | Horizon | Raw-hold MSE | Direct Gaussian MSE | Corrected MSE |',
    '|---|---:|---:|---:|---:|---:|']
for row in summary['rows']:
    scores=row['scores']
    lines.append(f"| {row['method']} | {row['target']} | {row['horizon']} | {scores['raw_hold']['mse']:.8f} | {scores['gaussian_forecast']['mse']:.8f} | {scores['appearance_corrected']['mse']:.8f} |")
lines += ['','## Outcomes','']
for name in protocol['methods']:
    count=sum(row['method']==name for row in summary['rows'])
    lines.append(f"{name}: corrected forecast beats raw hold on {wins[name]['mse']}/{count} MSE comparisons and {wins[name]['mae']}/{count} MAE comparisons.")
all_worse=all(row['scores']['appearance_corrected'][metric]>row['scores']['raw_hold'][metric] for row in summary['rows'] for metric in ['mse','mae'])
lines += ['', 'All corrected errors are higher than raw hold on this panel; this negative result does not support an accuracy upgrade.' if all_worse else 'Inspect every outcome above; a selected panel cannot establish overall superiority.', '']
for exclusion in summary['exclusions']:
    lines.append(f"Excluded {exclusion['method']} target{exclusion['target']}: {exclusion['reason']}.")
common=sorted({row['target'] for row in summary['rows'] if row['common_target']})
lines += ['',f"Cross-policy table has {len(common)} shared withheld targets: {common}. Other eligible per-policy outcomes are retained above.",'',
    f"All{baseline_checks} baseline scalar comparisons match the earlier full-run evaluation ledger. Registered sources/archive, target image hashes, histories and exclusions match. Corrected volumes were not independently rerendered a second time.",'',
    'Interpretation requires both this selected probe and the full acquisition ablation. Keeping acquired appearance avoids discarding unmodeled detail, but the added motion change must earn an improvement over raw hold.','']
(folder/'report.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(verification,indent=2))
