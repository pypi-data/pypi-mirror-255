import numpy as np
import cv2 as cv
import spams
import copy
from abc import ABC, abstractmethod



class TissueMaskException(Exception):
    pass
class ABCStainExtractor(ABC):

    @staticmethod
    @abstractmethod
    def get_stain_matrix(I):
        """
        Estimate the stain matrix given an image.
        :param I:
        :return:
        """

class ABCTissueLocator(ABC):
    @staticmethod
    @abstractmethod
    def get_tissue_mask(I):
        """
        Get a boolean tissue mask.
        :param I:
        :return:
        """

class LuminosityThresholdTissueLocator(ABCTissueLocator):

    @staticmethod
    def get_tissue_mask(I, luminosity_threshold=0.8):
        """
        Get a binary mask where true denotes pixels with a luminosity less than the specified threshold.
        Typically we use to identify tissue in the image and exclude the bright white background.
        :param I: RGB uint 8 image.
        :param luminosity_threshold: Luminosity threshold.
        :return: Binary mask.
        """
        assert is_uint8_image(I), "Image should be RGB uint8."
        I_LAB = cv.cvtColor(I, cv.COLOR_RGB2LAB)
        L = I_LAB[:, :, 0] / 255.0  # Convert to range [0,1].
        mask = L < luminosity_threshold

        # Check it's not empty
        if mask.sum() == 0:
            raise TissueMaskException("Empty tissue mask computed")
        return mask

class LuminosityStandardizer(object):

    @staticmethod
    def standardize(I, percentile=95):
        """
        Transform image I to standard brightness.
        Modifies the luminosity channel such that a fixed percentile is saturated.
        :param I: Image uint8 RGB.
        :param percentile: Percentile for luminosity saturation. At least (100 - percentile)% of pixels should be fully luminous (white).
        :return: Image uint8 RGB with standardized brightness.
        """
        assert is_uint8_image(I), "Image should be RGB uint8."
        I_LAB = cv.cvtColor(I, cv.COLOR_RGB2LAB)
        L_float = I_LAB[:, :, 0].astype(float)
        p = np.percentile(L_float, percentile)
        I_LAB[:, :, 0] = np.clip(255 * L_float / p, 0, 255).astype(np.uint8)
        I = cv.cvtColor(I_LAB, cv.COLOR_LAB2RGB)
        return I

def get_concentrations(I, stain_matrix, regularizer=0.01):
    """
    Estimate concentration matrix given an image and stain matrix.
    :param I:
    :param stain_matrix:
    :param regularizer:
    :return:
    """
    OD = convert_RGB_to_OD(I).reshape((-1, 3))
    return spams.lasso(X=OD.T, D=stain_matrix.T, mode=2, lambda1=regularizer, pos=True).toarray().T

def get_sign(x):
    """
    Returns the sign of x.
    :param x: A scalar x.
    :return: The sign of x.
    """
    if x > 0:
        return +1
    elif x < 0:
        return -1
    elif x == 0:
        return 0

def normalize_matrix_rows(A):
    """
    Normalize the rows of an array.
    :param A: An array.
    :return: Array with rows normalized.
    """
    return A / np.linalg.norm(A, axis=1)[:, None]

def convert_RGB_to_OD(I):
    """
    Convert from RGB to optical density (OD_RGB) space.
    RGB = 255 * exp(-1*OD_RGB).
    :param I: Image RGB uint8.
    :return: Optical denisty RGB image.
    """
    mask = (I == 0)
    I_masked = copy.deepcopy(I)
    I_masked[mask] = 1
    #I[mask] = 1
    return np.maximum(-1 * np.log(I_masked / 255), 1e-6)

def convert_OD_to_RGB(OD):

    """
    Convert from optical density (OD_RGB) to RGB.
    RGB = 255 * exp(-1*OD_RGB)
    :param OD: Optical denisty RGB image.
    :return: Image RGB uint8.
    """
    assert OD.min() >= 0, "Negative optical density."
    OD = np.maximum(OD, 1e-6)
    return (255 * np.exp(-1 * OD)).astype(np.uint8)

def is_image(I):
    """
    Is I an image.
    """
    if not isinstance(I, np.ndarray):
        return False
    if not I.ndim == 3:
        return False
    return True

def is_uint8_image(I):
    """
    Is I a uint8 image.
    """
    if not is_image(I):
        return False
    if I.dtype != np.uint8:
        return False
    return True

def lab_split(I):
    """
    Convert from RGB uint8 to LAB and split into channels
    :param I: uint8
    :return:
    """
    I = cv.cvtColor(I, cv.COLOR_RGB2LAB)
    I = I.astype(np.float32)
    I1, I2, I3 = cv.split(I)
    I1 /= 2.55
    I2 -= 128.0
    I3 -= 128.0
    return I1, I2, I3

def merge_back(I1, I2, I3):
    """
    Take seperate LAB channels and merge back to give RGB uint8
    :param I1:
    :param I2:
    :param I3:
    :return:
    """
    I1 *= 2.55
    I2 += 128.0
    I3 += 128.0
    I = np.clip(cv.merge((I1, I2, I3)), 0, 255).astype(np.uint8)
    return cv.cvtColor(I, cv.COLOR_LAB2RGB)

def get_mean_std(I):
    """
    Get mean and standard deviation of each channel
    :param I: uint8
    :return:
    """
    I1, I2, I3 = lab_split(I)
    m1, sd1 = cv.meanStdDev(I1)
    m2, sd2 = cv.meanStdDev(I2)
    m3, sd3 = cv.meanStdDev(I3)
    means = m1, m2, m3
    stds = sd1, sd2, sd3
    return means, stds

def standardize_brightness(I):
    """
    :param I:
    :return: Image pixel values divided by the 90th percentile
    """
    p = np.percentile(I, 90)
    return np.clip(I * 255.0 / p, 0, 255).astype(np.uint8)



class MacenkoStainExtractor(ABCStainExtractor):
    @staticmethod
    def get_stain_matrix(I, luminosity_threshold=0.8, angular_percentile=99):
        """
        Stain matrix estimation via method of:
        M. Macenko et al. 'A method for normalizing histology slides for quantitative analysis'
        :param I: Image RGB uint8.
        :param luminosity_threshold:
        :param angular_percentile:
        :return:
        """
        assert is_uint8_image(I), "Image should be RGB uint8."
        # Convert to OD and ignore background
        tissue_mask = LuminosityThresholdTissueLocator.get_tissue_mask(I, luminosity_threshold=luminosity_threshold).reshape((-1,))
        OD = convert_RGB_to_OD(I).reshape((-1, 3))
        OD = OD[tissue_mask]
        # Eigenvectors of cov in OD space (orthogonal as cov symmetric)
        _, V = np.linalg.eigh(np.cov(OD, rowvar=False))
        # The two principle eigenvectors
        V = V[:, [2, 1]]
        # Make sure vectors are pointing the right way
        if V[0, 0] < 0: V[:, 0] *= -1
        if V[0, 1] < 0: V[:, 1] *= -1
        # Project on this basis.
        That = np.dot(OD, V)
        # Angular coordinates with repect to the principle, orthogonal eigenvectors
        phi = np.arctan2(That[:, 1], That[:, 0])
        # Min and max angles
        minPhi = np.percentile(phi, 100 - angular_percentile)
        maxPhi = np.percentile(phi, angular_percentile)
        # the two principle colors
        v1 = np.dot(V, np.array([np.cos(minPhi), np.sin(minPhi)]))
        v2 = np.dot(V, np.array([np.cos(maxPhi), np.sin(maxPhi)]))
        # Order of H and E.
        # H first row.
        if v1[0] > v2[0]:
            HE = np.array([v1, v2])
        else:
            HE = np.array([v2, v1])
        return normalize_matrix_rows(HE)


class Macenko(object):
    def __init__(self):
        self.extractor = MacenkoStainExtractor
        self.is_trained = False

    def fit(self, target_image):
        if type(target_image) != 'numpy.ndarray':
            ValueError('Invalid input, try to pass your image as a Numpy matrix')
        """
        Fit to a target image.
        :param target: Image matrix RGB uint8.
        :return:
        """
        self.is_trained = True

        self.stain_matrix_target = self.extractor.get_stain_matrix(target_image)
        self.target_concentrations = get_concentrations(target_image, self.stain_matrix_target)
        self.maxC_target = np.percentile(self.target_concentrations, 99, axis=0).reshape((1, 2))

    def transform(self, input_image):
        if not self.is_trained:
            raise AssertionError('Run fit function first.')
        if type(input_image) != 'numpy.ndarray':
            ValueError('Invalid input, try to pass your image as a 3-dimension Numpy matrix')
        """
        Transform an image.
        :param I: Image matrix RGB uint8.
        :return:
        """
        stain_matrix_source = self.extractor.get_stain_matrix(input_image)
        source_concentrations = get_concentrations(input_image, stain_matrix_source)
        maxC_source = np.percentile(source_concentrations, 99, axis=0).reshape((1, 2))
        source_concentrations *= (self.maxC_target / maxC_source)
        tmp = 255 * np.exp(-1 * np.dot(source_concentrations, self.stain_matrix_target))
        return tmp.reshape(input_image.shape).astype(np.uint8)



