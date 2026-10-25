"""Small causal/measurement checks, independent of long real-volume runs."""
import sys
import time
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.controlled.benchmark import ControlledSequence, FixedPolicy, make_clip, run_closed, score
from experiments.controlled.event_focus import EventFocusPolicy


def test_exact_budget_gaps_and_future_pixel_independence():
    clip, _, _ = make_clip(7,"precursor")
    first = run_closed(ControlledSequence(clip),EventFocusPolicy(),40,7,time.monotonic()+15)
    altered = clip.copy()
    altered[121:] = 0  # Future changes cannot alter an earlier decision.
    second = run_closed(ControlledSequence(altered),EventFocusPolicy(),40,7,time.monotonic()+15)
    assert first["decisions"][:121] == second["decisions"][:121]
    indices = first["acquired_indices"]
    assert len(indices)==40 and indices[0]==0 and len(set(indices))==40
    assert min(np.diff(indices))>=2 and max(np.diff(indices))<=12
    assert 239-indices[-1]<=12


@pytest.mark.parametrize("phase",[0.,1/3,2/3])
def test_fixed_phases_equal_budget_and_no_event_metadata(phase):
    clip, events, _ = make_clip(42,"abrupt")
    seq = ControlledSequence(clip)
    assert "42" not in str(seq.metadata) and not hasattr(seq.metadata,"events")
    record=run_closed(seq,FixedPolicy(phase),40,42,time.monotonic()+15)
    assert len(record["acquired_indices"])==40
    assert record["acquired_indices"][0]==0 and record["acquired_indices"][-1]==239
    assert score(record,clip,events)["events"]==4


def test_quiet_and_exact_event_tolerance():
    clip, events, _ = make_clip(7,"quiet")
    record=run_closed(ControlledSequence(clip),FixedPolicy(0.),40,7,time.monotonic()+15)
    assert score(record,clip,events)["event_coverage"] is None
    scored=score({"acquired_indices":[0,10,239]},clip,[9,11,12])
    assert scored["covered_events"]==2 and scored["event_distances"]==[1,1,2]


def test_rejects_nonacquired_pixels_and_bad_history():
    clip, _, _ = make_clip(7,"quiet")
    policy=EventFocusPolicy()
    policy.reset(ControlledSequence(clip).metadata,40,7)
    with pytest.raises(TypeError):
        policy.observe(clip[0])
    policy.indices=[0]
    with pytest.raises(ValueError):
        policy.decide(1,())
