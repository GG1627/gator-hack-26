"""Causal Gaussian tracking/forecasting from acquired pixels only.

No source files, annotations, full sequence, or oracle are accepted. The model
uses gated assignment in physical distance, damped velocity, and held shape/
intensity. Split candidates are observed morphology heuristics, not validated
mitosis predictions. Every child of a candidate split receives a fresh ID.
"""
from dataclasses import asdict, dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment

from photon.gaussian import (Gaussian, GaussianFitConfig, IntensityCalibration,
                             detect_and_fit, render_gaussians, valid_image)
from photon.schemas import ObservedFrame, PredictedFrame


@dataclass(frozen=True)
class TrackingConfig:
    assignment_gate_um: float = 5.0
    split_gate_um: float = 3.0
    velocity_smoothing: float = 0.7
    damping_per_frame: float = 0.03
    base_position_sigma_um: float = 0.15
    process_sigma_um_per_frame: float = 0.08
    detect_candidate_splits: bool = True

    def __post_init__(self):
        values=[self.assignment_gate_um,self.split_gate_um,self.velocity_smoothing,
                self.damping_per_frame,self.base_position_sigma_um,self.process_sigma_um_per_frame]
        if not np.isfinite(values).all() or min(values)<0 or min(self.assignment_gate_um,self.split_gate_um)<=0:
            raise ValueError("Invalid tracking parameters")
        if not 0<=self.velocity_smoothing<=1:
            raise ValueError("velocity_smoothing must be in [0,1]")


@dataclass(frozen=True)
class Track:
    identifier: int
    gaussian: Gaussian
    velocity: np.ndarray  # voxel-axis units per source frame
    observed_at: int
    observations: int
    parent_hint: int | None = None

    def __post_init__(self):
        velocity = np.array(self.velocity,dtype=float,copy=True)
        if velocity.shape!=self.gaussian.center.shape or not np.isfinite(velocity).all():
            raise ValueError("Invalid track velocity")
        velocity.flags.writeable = False
        object.__setattr__(self,"velocity",velocity)


def forecast_center(track, t, damping):
    dt = t-track.observed_at
    if dt<0:
        raise ValueError("Cannot forecast before a track observation")
    horizon = dt if damping==0 else -np.expm1(-damping*dt)/damping
    return track.gaussian.center+track.velocity*horizon


class GaussianSceneModel:
    def __init__(self,spacing,*,fit_config=GaussianFitConfig(),tracking_config=TrackingConfig()):
        self.spacing = np.asarray(spacing,dtype=float).copy()
        if self.spacing.ndim!=1 or self.spacing.size not in (2,3) or not np.isfinite(self.spacing).all() or self.spacing.min()<=0:
            raise ValueError("Expected positive YX/ZYX physical spacing")
        self.spacing.flags.writeable = False
        self.fit_config,self.config = fit_config,tracking_config
        self.shape = self.calibration = self.last_observed = None
        self.acquired_indices = []
        self.tracks = {}
        self.next_identifier = 1
        self.observation_log = []
        self.base_uncertainty = self.config.base_position_sigma_um

    def _new_track(self,gaussian,t,*,parent=None,velocity=None):
        identifier = self.next_identifier
        self.next_identifier += 1
        return Track(identifier,gaussian,np.zeros(len(self.spacing)) if velocity is None else velocity,t,1,parent)

    def observe(self, frame: ObservedFrame):
        if not isinstance(frame,ObservedFrame) or frame.kind!="MEASURED" or not isinstance(frame.index,int) or frame.index<0:
            raise ValueError("Model accepts acquired ObservedFrame inputs only")
        if self.last_observed is not None and frame.index<=self.last_observed:
            raise ValueError("Observations must advance strictly in time")
        image = valid_image(frame.pixels)
        if image.ndim!=len(self.spacing) or (self.shape is not None and image.shape!=self.shape):
            raise ValueError("Observation shape/spacing changed")
        calibration = self.calibration or IntensityCalibration.from_image(image)
        signal = calibration.normalize(image,clip=False)
        detections,diagnostics = detect_and_fit(signal,self.spacing,calibration.noise_sigma,self.fit_config)
        previous = sorted(self.tracks.values(),key=lambda track:track.identifier)
        predicted = np.array([forecast_center(track,frame.index,self.config.damping_per_frame) for track in previous])
        distances = (np.linalg.norm((predicted[:,None,:]-np.array([g.center for g in detections])[None,:,:])*self.spacing,axis=2)
                     if previous and detections else np.empty((len(previous),len(detections))))
        next_tracks, events, consumed_detections, split_mothers = {}, [], set(), set()
        if self.config.detect_candidate_splits and previous and len(detections)>=2:
            closest_parent = np.argmin(distances,axis=0)
            for row,track in enumerate(previous):
                eligible = [i for i in np.argsort(distances[row]) if closest_parent[i]==row and i not in consumed_detections
                            and distances[row,i]<=self.config.split_gate_um]
                if len(eligible)<2 or track.gaussian.mass<=0:
                    continue
                a,b = eligible[:2]
                fractions = np.array([detections[a].mass,detections[b].mass])/track.gaussian.mass
                separation = np.linalg.norm((detections[a].center-detections[b].center)*self.spacing)
                if not (np.all((fractions>=0.2)&(fractions<=0.85)) and 0.6<=fractions.sum()<=1.6 and separation>0.2):
                    continue
                children = []
                for index in (a,b):
                    child = self._new_track(detections[index],frame.index,parent=track.identifier,velocity=track.velocity)
                    next_tracks[child.identifier] = child
                    children.append(child.identifier)
                split_mothers.add(row)
                consumed_detections.update((a,b))
                events.append({"kind":"candidate_split","mother_id":track.identifier,"child_ids":children,
                               "note":"observed mass/proximity heuristic; not verified mitosis"})
        old_rows = [r for r in range(len(previous)) if r not in split_mothers]
        new_columns = [c for c in range(len(detections)) if c not in consumed_detections]
        matched_rows = set()
        if old_rows and new_columns:
            costs = distances[np.ix_(old_rows,new_columns)]/self.config.assignment_gate_um
            costs = np.where(costs<=1,costs,1e6)
            # Explicit unmatched columns avoid invalid forced matches changing valid assignments.
            augmented = np.concatenate([costs,np.ones((len(old_rows),len(old_rows)))],axis=1)
            rows,columns = linear_sum_assignment(augmented)
            for row,column in zip(rows,columns):
                if column>=len(new_columns) or augmented[row,column]>1:
                    continue
                prior = previous[old_rows[row]]
                index = new_columns[column]
                gaussian = detections[index]
                measured_velocity = (gaussian.center-prior.gaussian.center)/(frame.index-prior.observed_at)
                velocity = self.config.velocity_smoothing*measured_velocity+(1-self.config.velocity_smoothing)*prior.velocity
                updated = Track(prior.identifier,gaussian,velocity,frame.index,prior.observations+1,prior.parent_hint)
                next_tracks[updated.identifier] = updated
                consumed_detections.add(index)
                matched_rows.add(old_rows[row])
        for index,gaussian in enumerate(detections):
            if index not in consumed_detections:
                child = self._new_track(gaussian,frame.index)
                next_tracks[child.identifier] = child
                events.append({"kind":"birth_or_unmatched_detection","track_id":child.identifier})
        for row,track in enumerate(previous):
            if row not in matched_rows and row not in split_mothers:
                events.append({"kind":"retired_unmatched_track","track_id":track.identifier})
        self.shape,self.calibration = image.shape,calibration
        self.tracks,self.last_observed = next_tracks,frame.index
        self.acquired_indices.append(frame.index)
        ambiguity = len(events)/max(1,len(previous)+len(detections))
        self.base_uncertainty = self.config.base_position_sigma_um+0.25*ambiguity+(0.5 if not detections else 0)
        self.observation_log.append({"t":frame.index,"detection":diagnostics,"active_tracks":len(self.tracks),"events":events})

    def scene_at(self,t):
        if self.last_observed is None:
            raise ValueError("Acquire an observation before prediction")
        if isinstance(t,bool) or not isinstance(t,int) or t<self.last_observed:
            raise ValueError("Prediction time must be at/after the latest acquired observation")
        return [Gaussian(forecast_center(track,t,self.config.damping_per_frame),track.gaussian.covariance,
                         track.gaussian.amplitude,track.gaussian.mass,track.gaussian.voxel_count)
                for track in sorted(self.tracks.values(),key=lambda track:track.identifier)]

    def position_uncertainty(self,t):
        if self.last_observed is None or isinstance(t,bool) or not isinstance(t,int) or t<self.last_observed:
            raise ValueError("Invalid uncertainty time")
        return float(np.hypot(self.base_uncertainty,(t-self.last_observed)*self.config.process_sigma_um_per_frame))

    def predict(self,t,*,include_uncertainty_map=False,backend="cpu",runner=None):
        scene = self.scene_at(t)
        sigma = self.position_uncertainty(t)
        metadata = None
        samples = None
        if backend != "cpu":
            from photon.gpu import render_gaussian_batch
            scenes = [scene]
            if include_uncertainty_map:
                for axis in range(len(self.spacing)):
                    for direction in (-1,1):
                        offset = np.zeros(len(self.spacing))
                        offset[axis] = direction*sigma/self.spacing[axis]
                        scenes.append([Gaussian(g.center+offset,g.covariance,g.amplitude,g.mass,g.voxel_count) for g in scene])
            batch = render_gaussian_batch(self.shape,scenes,backend=backend,runner=runner)
            pixels, samples, metadata = batch.pixels[0], batch.pixels[1:], batch.metadata
        else:
            pixels = render_gaussians(self.shape,scene)
        disagreement = None
        if include_uncertainty_map:
            # Deterministic +/- physical-axis translations: a common-motion
            # ensemble, not independent object uncertainty or a calibrated probability.
            mean = np.zeros(self.shape,dtype=np.float32)
            m2 = np.zeros(self.shape,dtype=np.float32)
            count = 0
            sample_index = 0
            for axis in range(len(self.spacing)):
                for direction in (-1,1):
                    offset = np.zeros(len(self.spacing))
                    offset[axis] = direction*sigma/self.spacing[axis]
                    shifted = [Gaussian(g.center+offset,g.covariance,g.amplitude,g.mass,g.voxel_count) for g in scene]
                    sample = render_gaussians(self.shape,shifted) if samples is None else samples[sample_index]
                    sample_index += 1
                    count += 1
                    delta = sample-mean
                    mean += delta/count
                    m2 += delta*(sample-mean)
            disagreement = np.sqrt(np.maximum(m2/count,0)).astype(np.float32)
            disagreement.flags.writeable = False
        pixels.flags.writeable = False
        return PredictedFrame(t,pixels,tuple(self.acquired_indices),sigma,
                              uncertainty_map=disagreement,normalization=self.calibration.to_dict(),
                              backend="cpu" if metadata is None else metadata["backend"],backend_metadata=metadata)

    def state_dict(self):
        return {"model_version":"causal-moment-gaussian-v1","array_axes":"ZYX" if len(self.spacing)==3 else "YX",
                "spacing_um":self.spacing.tolist(),"acquired_indices":list(self.acquired_indices),
                "normalization":None if self.calibration is None else self.calibration.to_dict(),
                "fit_config":asdict(self.fit_config),"tracking_config":asdict(self.config),
                "tracks":[{"id":track.identifier,"center_voxels":track.gaussian.center.tolist(),
                    "covariance_voxels2":track.gaussian.covariance.tolist(),"amplitude":track.gaussian.amplitude,
                    "velocity_voxels_per_frame":track.velocity.tolist(),"observed_at":track.observed_at,
                    "parent_hint":track.parent_hint} for track in sorted(self.tracks.values(),key=lambda tr:tr.identifier)],
                "observations":self.observation_log}
