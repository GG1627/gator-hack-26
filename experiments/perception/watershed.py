"""Experimental acquired-image instance separation; not used by frozen policies.

Marker-controlled intensity watershed is a classical baseline, not a frontier
technology or verified cell segmentation. Optional dependencies are isolated.
"""
from dataclasses import dataclass
import numpy as np
from scipy import ndimage
from photon.gaussian import GaussianFitConfig, fit_component, valid_image


@dataclass(frozen=True)
class WatershedConfig:
    seed_smoothing_um: float = 0.3
    peak_radius_um: float = 1.5

    def __post_init__(self):
        if not np.isfinite([self.seed_smoothing_um,self.peak_radius_um]).all() or min(self.seed_smoothing_um,self.peak_radius_um)<=0:
            raise ValueError("Seed smoothing and peak radius must be positive and finite")


def watershed_and_fit(signal, spacing, noise_sigma, config=GaussianFitConfig(), seeds=WatershedConfig()):
    """Split connected signal at acquired intensity peaks, then fit each basin.

    Physical spacing controls smoothing and the rectangular peak neighborhood.
    Foreground and size limits match the existing fitter. Oversized connected
    regions are split *before* the upper size filter. Only the input image is used.
    Returns components, diagnostics, and voxel labels (zero = excluded/background).
    """
    from skimage.segmentation import watershed
    signal = valid_image(signal).astype(np.float32)
    spacing = np.asarray(spacing,dtype=float)
    if spacing.shape!=(signal.ndim,) or not np.isfinite(spacing).all() or spacing.min()<=0:
        raise ValueError("Spacing must be positive and match array axes")
    if not np.isfinite(noise_sigma) or noise_sigma<0:
        raise ValueError("Noise estimate must be finite and nonnegative")
    threshold = max(config.min_signal,config.noise_multiplier*noise_sigma)
    smooth = ndimage.gaussian_filter(signal,sigma=config.smoothing_um/spacing,mode="nearest")
    connected,count = ndimage.label(smooth>threshold)
    sizes = np.bincount(connected.ravel())
    keep = sizes>=config.min_voxels
    keep[0] = False
    foreground = keep[connected]
    if not foreground.any():
        return [], {"method":"experimental intensity watershed", "connected_regions":int(count),
                    "markers":0,"accepted":0,"rejected_size":0,"retained_foreground_fraction":0.0}, np.zeros(signal.shape,dtype=np.int32)
    seed_image = ndimage.gaussian_filter(signal,sigma=seeds.seed_smoothing_um/spacing,mode="nearest")
    neighborhood = 2*np.ceil(seeds.peak_radius_um/spacing).astype(int)+1
    peaks = foreground & (seed_image==ndimage.maximum_filter(seed_image,size=tuple(neighborhood),mode="nearest"))
    plateau, n = ndimage.label(peaks)
    positions = list(ndimage.maximum_position(seed_image,plateau,list(range(1,n+1)))) if n else []
    # Every retained component needs a seed, even if a brighter neighboring
    # component suppressed its maximum. This avoids silently dropping it.
    seeded = {int(connected[position]) for position in positions}
    missing = [int(label) for label in np.flatnonzero(keep) if int(label) not in seeded]
    if missing:
        positions.extend(ndimage.maximum_position(seed_image,connected,missing))
    if len(positions)>config.max_components:
        raise ValueError("Marker limit exceeded; inspect acquired-image configuration")
    markers = np.zeros(signal.shape,dtype=np.int32)
    for index,position in enumerate(positions,1):
        markers[position] = index
    labels = watershed(-seed_image,markers=markers,mask=foreground,connectivity=1)
    components, rejected = [], 0
    accepted_labels = np.zeros(len(positions)+1,dtype=bool)
    for label,box in enumerate(ndimage.find_objects(labels),1):
        if box is None:
            continue
        mask = labels[box]==label
        size = int(mask.sum())
        if not config.min_voxels<=size<=config.max_voxels:
            rejected += 1
            continue
        components.append(fit_component(signal[box],mask,offset=[axis.start for axis in box],
                                         covariance_floor=config.covariance_floor_voxels))
        accepted_labels[label] = True
    labels = np.where(accepted_labels[labels],labels,0).astype(np.int32)
    return components, {"method":"experimental intensity watershed", "threshold":threshold,
        "connected_regions":int(count),"markers":len(positions),"accepted":len(components),
        "rejected_size":rejected,"retained_foreground_fraction":float(np.count_nonzero(labels)/foreground.sum()),
        "peak_neighborhood_voxels":neighborhood.tolist()}, labels
