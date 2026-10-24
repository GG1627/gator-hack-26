"""Observed-component Gaussian approximation, not a PSF-calibrated renderer.

Coordinates/covariances use array-axis voxel units (YX or ZYX). Intensity scaling
is fitted once from the first acquired image. Detection uses smoothed signal;
moments and amplitude are fitted using the original positive signal. Thresholded
moments underestimate tails; touching nuclei may form one component. No labels
or withheld images are accepted by these functions.
"""
from dataclasses import asdict, dataclass

import numpy as np
from scipy import ndimage


def valid_image(image):
    image = np.asarray(image)
    if image.ndim not in (2,3) or min(image.shape)<1 or not np.issubdtype(image.dtype,np.number) or np.iscomplexobj(image):
        raise ValueError("Expected a nonempty numeric 2D image or 3D volume")
    if not np.isfinite(image).all():
        raise ValueError("Image contains NaN or infinity")
    return image


@dataclass(frozen=True)
class IntensityCalibration:
    background: float
    scale: float
    noise_sigma: float

    def __post_init__(self):
        if not np.isfinite([self.background,self.scale,self.noise_sigma]).all() or self.scale<=0 or self.noise_sigma<0:
            raise ValueError("Invalid intensity calibration")

    @classmethod
    def from_image(cls, image):
        image = valid_image(image).astype(np.float32)
        background = float(np.median(image))
        scale = float(np.percentile(image,99.99))-background
        if scale<=np.finfo(np.float32).eps*max(1,abs(background)):
            scale = 1.0  # a constant first image does not justify enormous signal amplification
        noise = float(1.4826*np.median(np.abs(image-background)))/scale
        return cls(background,scale,noise)

    def normalize(self,image,*,clip=True):
        signal = (valid_image(image).astype(np.float32)-self.background)/self.scale
        return np.clip(signal,0,1 if clip else np.inf).astype(np.float32)

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Gaussian:
    center: np.ndarray
    covariance: np.ndarray
    amplitude: float
    mass: float = 0.0
    voxel_count: int = 0

    def __post_init__(self):
        center = np.array(self.center,dtype=np.float64,copy=True)
        covariance = np.array(self.covariance,dtype=np.float64,copy=True)
        if center.ndim!=1 or center.size not in (2,3) or covariance.shape!=(center.size,center.size):
            raise ValueError("Gaussian center/covariance dimensions disagree")
        if not np.isfinite(center).all() or not np.isfinite(covariance).all() or not np.allclose(covariance,covariance.T,atol=1e-10):
            raise ValueError("Gaussian geometry must be finite and symmetric")
        if np.linalg.eigvalsh(covariance).min()<=0:
            raise ValueError("Gaussian covariance must be positive definite")
        if not np.isfinite([self.amplitude,self.mass]).all() or self.amplitude<0 or self.mass<0:
            raise ValueError("Gaussian intensity/mass must be finite and nonnegative")
        center.flags.writeable = covariance.flags.writeable = False
        object.__setattr__(self,"center",center)
        object.__setattr__(self,"covariance",covariance)


@dataclass(frozen=True)
class GaussianFitConfig:
    min_signal: float = 0.08
    noise_multiplier: float = 4.0
    smoothing_um: float = 0.15
    min_voxels: int = 24
    max_voxels: int = 1_000_000
    covariance_floor_voxels: float = 0.25
    max_components: int = 2048

    def __post_init__(self):
        values=[self.min_signal,self.noise_multiplier,self.smoothing_um,self.covariance_floor_voxels]
        if not np.isfinite(values).all() or min(values)<0 or self.covariance_floor_voxels<=0:
            raise ValueError("Invalid Gaussian fitting parameters")
        if not 1<=self.min_voxels<=self.max_voxels or self.max_components<1:
            raise ValueError("Invalid component size/count limits")


def fit_component(signal, mask, *, offset=None, covariance_floor=0.25):
    """Intensity-weighted empirical moments and least-squares peak amplitude.

    On an untruncated analytic Gaussian these are its mean/covariance. Segmented
    components truncate tails, so fitted shape is an approximation, not exact
    deconvolution. Eigenvalue floor stabilizes thin/single-voxel components.
    """
    signal = valid_image(signal)
    mask = np.asarray(mask,dtype=bool)
    if mask.shape!=signal.shape or covariance_floor<=0 or not np.isfinite(covariance_floor):
        raise ValueError("Invalid component mask or covariance floor")
    coordinates = np.column_stack(np.nonzero(mask))
    if not len(coordinates):
        raise ValueError("Cannot fit an empty component")
    weights = np.maximum(signal[mask].astype(np.float64),0)
    mass = float(weights.sum())
    if mass<=0:
        raise ValueError("Component has no positive intensity")
    center = np.sum(coordinates*weights[:,None],axis=0)/mass
    centered = coordinates-center
    covariance = (centered*weights[:,None]).T@centered/mass
    eigenvalues,eigenvectors = np.linalg.eigh(covariance)
    covariance = (eigenvectors*np.maximum(eigenvalues,covariance_floor**2))@eigenvectors.T
    q = np.einsum("ni,ij,nj->n",centered,np.linalg.inv(covariance),centered)
    basis = np.exp(-0.5*q)
    amplitude = float(np.dot(weights,basis)/np.dot(basis,basis))
    if offset is not None:
        center += np.asarray(offset,dtype=float)
    return Gaussian(center,covariance,amplitude,mass,len(coordinates))


def detect_and_fit(signal, spacing, noise_sigma, config=GaussianFitConfig()):
    signal = valid_image(signal)
    spacing = np.asarray(spacing,dtype=float)
    if spacing.shape!=(signal.ndim,) or not np.isfinite(spacing).all() or spacing.min()<=0:
        raise ValueError("Spacing must be positive and match array axes")
    if not np.isfinite(noise_sigma) or noise_sigma<0:
        raise ValueError("Invalid noise estimate")
    threshold = max(config.min_signal,config.noise_multiplier*noise_sigma)
    smoothed = ndimage.gaussian_filter(signal.astype(np.float32),sigma=config.smoothing_um/spacing,mode="nearest")
    labels,count = ndimage.label(smoothed>threshold)  # face connectivity:4 in2D,6 in3D
    boxes = ndimage.find_objects(labels)
    components, rejected = [], 0
    for label,box in enumerate(boxes,1):
        if box is None:
            continue
        mask = labels[box]==label
        size = int(mask.sum())
        if not config.min_voxels<=size<=config.max_voxels:
            rejected += 1
            continue
        components.append(fit_component(signal[box],mask,offset=[axis.start for axis in box],
                                         covariance_floor=config.covariance_floor_voxels))
        if len(components)>config.max_components:
            raise ValueError("Component limit exceeded; inspect acquired-image threshold configuration")
    return components,{"threshold":threshold,"connected_regions":int(count),"accepted":len(components),
                       "rejected_size":rejected,"method":"thresholded observed-intensity moments"}


def render_gaussians(shape,components,*,truncate=4.0,clip_max=1.0):
    """Sum anisotropic Gaussian signals on voxel centers; zero background.

    Truncate at the stated Mahalanobis radius and clip the final accumulated
    signal only. Local bounding boxes avoid a Gaussian x full-volume allocation.
    Output float32; geometry/exponents evaluated in float64. This simplified
    additive signal is not alpha compositing or a calibrated optical forward model.
    """
    if len(shape) not in (2,3) or any(not isinstance(s,(int,np.integer)) or s<1 for s in shape):
        raise ValueError("Invalid render shape")
    if not np.isfinite(truncate) or truncate<=0 or (clip_max is not None and (not np.isfinite(clip_max) or clip_max<=0)):
        raise ValueError("Invalid render truncation/clipping")
    result = np.zeros(shape,dtype=np.float32)
    for component in components:
        if len(component.center)!=len(shape):
            raise ValueError("Gaussian/render dimension mismatch")
        radius = truncate*np.sqrt(np.diag(component.covariance))
        if np.any(component.center+radius<0) or np.any(component.center-radius>np.asarray(shape)-1):
            continue
        lower = np.maximum(np.floor(component.center-radius).astype(np.int64),0)
        upper = np.minimum(np.ceil(component.center+radius).astype(np.int64)+1,shape)
        if np.any(upper<=lower):
            continue
        box = tuple(slice(int(a),int(b)) for a,b in zip(lower,upper))
        coordinates = np.moveaxis(np.indices(tuple(upper-lower),dtype=float),0,-1)+lower
        delta = coordinates-component.center
        q = np.einsum("...i,ij,...j->...",delta,np.linalg.inv(component.covariance),delta)
        values = component.amplitude*np.exp(-0.5*q)
        values[q>truncate**2] = 0
        result[box] += values.astype(np.float32)
    if clip_max is not None:
        np.clip(result,0,clip_max,out=result)
    if not np.isfinite(result).all():
        raise ValueError("Rendered Gaussian accumulation overflowed")
    return result
