import numpy as np


"""
Source code adapted from:
https://github.com/DigitalSlideArchive/HistomicsTK/blob/master/histomicstk/preprocessing/color_normalization/reinhard.py
https://github.com/Peter554/StainTools/blob/master/staintools/reinhard_color_normalizer.py
"""

# constant conversion matrices between color spaces: https://gist.github.com/bikz05/6fd21c812ef6ebac66e1


_rgb2xyz = np.array([[0.412453, 0.357580, 0.180423],
                     [0.212671, 0.715160, 0.072169],
                     [0.019334, 0.119193, 0.950227]])

_xyz2rgb = np.linalg.inv(_rgb2xyz)


def rgb2lab(rgb):
    rgb = rgb.astype("float32")

    # convert rgb -> xyz color domain
    arr = rgb.copy()
    mask = arr > 0.04045
    arr[mask] = np.power((arr[mask] + 0.055) / 1.055, 2.4)
    arr[~mask] /= 12.92
    xyz = np.dot(arr, _rgb2xyz.T.astype(arr.dtype))

    # scale by CIE XYZ tristimulus values of the reference white point
    arr = xyz.copy()
    arr = arr / np.asarray((0.95047, 1., 1.08883), dtype=xyz.dtype)

    # Nonlinear distortion and linear transformation
    mask = arr > 0.008856
    arr[mask] = np.cbrt(arr[mask])
    arr[~mask] = 7.787 * arr[~mask] + 16. / 116.

    x, y, z = arr[..., 0], arr[..., 1], arr[..., 2]

    # Vector scaling
    L = (116. * y) - 16.
    a = 500.0 * (x - y)
    b = 200.0 * (y - z)

    # OpenCV format
    L *= 2.55
    a += 128
    b += 128

    # finally, get LAB color domain
    return np.concatenate([x[..., np.newaxis] for x in [L, a, b]], axis=-1)


def lab2rgb(lab):
    lab = lab.astype("float32")
    # first rescale back from OpenCV format
    lab[..., 0] /= 2.55
    lab[..., 1] -= 128
    lab[..., 2] -= 128

    # convert LAB -> XYZ color domain
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    y = (L + 16.) / 116.
    x = (a / 500.) + y
    z = y - (b / 200.)

    out = np.stack([x, y, z], axis=-1)

    mask = out > 0.2068966
    out[mask] = np.power(out[mask], 3.)
    out[~mask] = (out[~mask] - 16.0 / 116.) / 7.787

    # rescale to the reference white (illuminant)
    out *= np.array((0.95047, 1., 1.08883), dtype=out.dtype)
    
    # convert XYZ -> RGB color domain
    arr = out.copy()
    arr = np.dot(arr, _xyz2rgb.T)
    mask = arr > 0.0031308
    arr[mask] = 1.055 * np.power(arr[mask], 1 / 2.4) - 0.055
    arr[~mask] *= 12.92
    return np.clip(arr, 0, 1)

    
def csplit(I):
    return [I[..., i] for i in range(I.shape[-1])]

def cmerge(I1, I2, I3):
    return np.stack([I1, I2, I3], axis=-1)

def lab_split(I):
    I = I.astype("float32")
    I1, I2, I3 = csplit(I)
    return I1 / 2.55, I2 - 128, I3 - 128

def lab_merge(I1, I2, I3):
    return cmerge(I1 * 2.55, I2 + 128, I3 + 128)

def get_mean_std(I):
    return np.mean(I), np.std(I)

def standardize(x, mu, std):
    return (x - mu) / std





class Reinhard():
    def __init__(self):
        super().__init__()
        self.target_mus = None
        self.target_stds = None
    
    def fit(self, target):
        # normalize
        target = target.astype("float32") / 255

        # convert to LAB
        lab = rgb2lab(target)

        # get summary statistics
        stack_ = np.array([get_mean_std(x) for x in lab_split(lab)])
        self.target_means = stack_[:, 0]
        self.target_stds = stack_[:, 1]

    def transform(self, I):
        if self.target_mus is None and self.target_stds is None:
            raise AssertionError('Run fit function first.')
        # normalize
        I = I.astype("float32") / 255
        
        # convert to LAB
        lab = rgb2lab(I)
        labs = lab_split(lab)

        # get summary statistics from LAB
        stack_ = np.array([get_mean_std(x) for x in labs])
        mus = stack_[:, 0]
        stds = stack_[:, 1]

        # normalize
        # standardize intensities channel-wise and normalize using target mus and stds
        result = [standardize(x, mu_, std_) * std_T + mu_T for x, mu_, std_, mu_T, std_T \
            in zip(labs, mus, stds, self.target_means, self.target_stds)]

        # rebuild LAB
        lab = lab_merge(*result)

        # convert back to RGB from LAB
        lab = lab2rgb(lab)

        # rescale to [0, 255] uint8
        return (lab * 255).astype("uint8")
    
