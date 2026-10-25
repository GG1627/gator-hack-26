"""Causal isolation and independent target/accounting checks for the new ablation."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import photon.adaptive as canonical
from photon.data import SequenceMetadata
from photon.development import aggregate_errors, image_error, record_development_run

spec=importlib.util.spec_from_file_location("perception_ablation",Path(__file__).parents[1]/"scripts/run_perception_ablation.py")
ablation=importlib.util.module_from_spec(spec);spec.loader.exec_module(ablation)


def sequence(frames):
    reads=[]
    metadata=SequenceMetadata("controlled","synthetic",len(frames),frames[0].shape,"uint16",
        source="synthetic",voxel_size_xyz_um=(1.,1.))
    def read(t): reads.append(t);return frames[t]
    return SimpleNamespace(metadata=metadata,fingerprint="controlled-test",read=read,reads=reads)


def frames():
    y,x=np.indices((32,32))
    return [np.round(sum(np.exp(-((y-16)**2+(x-center-t*.1)**2)/8) for center in [12,18])*4000).astype(np.uint16)
            for t in range(20)]


def test_candidate_policy_keeps_canonical_controller_isolated(tmp_path):
    original=canonical.GaussianSceneModel
    progress=[]
    candidate=ablation.make_candidate_policy(progress=lambda t,n:progress.append((t,n)))
    source=sequence(frames())
    run=record_development_run(source,candidate,4,42,"candidate",tmp_path/"candidate")
    assert canonical.GaussianSceneModel is original
    assert type(candidate.model) is not original
    assert source.reads==list(run.record.acquired_indices)
    assert progress==list(zip(run.record.acquired_indices,range(1,5)))
    assert len(run.record.acquired_indices)==4 and run.record.acquired_indices[0]==0
    assert np.all(np.diff(run.record.acquired_indices)>=2)
    assert np.all(np.diff(run.record.acquired_indices)<=12)
    assert 19-run.record.acquired_indices[-1]<=12


def test_unacquired_future_pixels_cannot_change_candidate_schedule_or_forecasts(tmp_path):
    original_frames=frames()
    first=record_development_run(sequence(original_frames),ablation.make_candidate_policy(),4,42,"first",tmp_path/"first")
    altered=[frame.copy() for frame in original_frames]
    rng=np.random.default_rng(97)
    for t in set(range(20))-set(first.record.acquired_indices):
        altered[t]=rng.integers(0,65535,size=(32,32),dtype=np.uint16)
    second=record_development_run(sequence(altered),ablation.make_candidate_policy(),4,42,"second",tmp_path/"second")
    assert first.record.acquired_indices==second.record.acquired_indices
    assert first.record.decisions==second.record.decisions
    for t in first.forecasts:
        assert len(first.forecasts[t])==len(second.forecasts[t])
        for left,right in zip(first.forecasts[t],second.forecasts[t]):
            np.testing.assert_array_equal(left.center,right.center)
            np.testing.assert_array_equal(left.covariance,right.covariance)
            assert left.amplitude==right.amplitude


def error(value):
    return image_error(np.array([value],dtype=float),np.zeros(1),np.zeros(1,dtype=bool))


def row(t,value):
    return {"t":t,"errors":{name:error(value) for name in ["raw_hold","gaussian_hold","gaussian_forecast"]}}


def test_pairwise_targets_are_not_replaced_by_three_way_intersection():
    scores=ablation.pairwise_scores({"a":[row(1,1),row(2,3)],"b":[row(2,2),row(3,4)],"c":[row(3,5)]})
    assert scores["a_vs_b"]["indices"]==[2]
    assert scores["a_vs_b"]["methods"]["a"]["raw_hold"]["mse"]==9
    assert scores["a_vs_b"]["methods"]["b"]["raw_hold"]["mse"]==4
    assert scores["b_vs_c"]["indices"]==[3]
    assert scores["a_vs_c"]["frames"]==0
    assert scores["a_vs_c"]["methods"]["a"]["raw_hold"]["mse"] is None


def test_scalar_accounting_rejects_wrong_targets_and_tampering():
    rows={"a":[row(1,2)]}
    metrics={name:aggregate_errors([error(2)]) for name in ["raw_hold","gaussian_hold","gaussian_forecast"]}
    summary={"variants":{"a":{"acquired_indices":[0],"own_withheld":metrics}}}
    ablation.verify_accounting(summary,rows,2,1)
    metrics["raw_hold"]["mse"]=0
    with pytest.raises(ValueError,match="accounting mismatch"):
        ablation.verify_accounting(summary,rows,2,1)
    with pytest.raises(ValueError,match="target ledger"):
        ablation.verify_accounting(summary,{"a":[row(0,2)]},2,1)
