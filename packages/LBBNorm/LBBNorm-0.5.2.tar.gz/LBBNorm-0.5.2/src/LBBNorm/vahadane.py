 
import spams
import numpy as np
import cv2 as cv

def notwhite_mask(I, thresh=0.8):
    """
    Get a binary mask where true denotes 'not white'
    :param I:
    :param thresh:
    :return:
    """
    I_LAB = cv.cvtColor(I, cv.COLOR_RGB2LAB)
    L = I_LAB[:, :, 0] / 255.0
    return (L < thresh)

def remove_zeros(I):
    """
    Remove zeros, replace with 1's.
    :param I: uint8 array
    :return:
    """
    mask = (I == 0)
    I[mask] = 1
    return I

def RGB_to_OD(I):
    """
    Convert from RGB to optical density
    :param I:
    :return:
    """
    I = remove_zeros(I)
    return -1 * np.log(I / 255)


def OD_to_RGB(OD):
    """
    Convert from optical density to RGB
    :param OD:
    :return:
    """
    return (255 * np.exp(-1 * OD)).astype(np.uint8)

def normalize_rows(A):
    """
    Normalize rows of an array
    :param A:
    :return:
    """
    return A / np.linalg.norm(A, axis=1)[:, None]

def standardize_brightness(I):
    """

    :param I:
    :return:
    """
    p = np.percentile(I, 90)
    return np.clip(I * 255.0 / p, 0, 255).astype(np.uint8)

def get_concentrations(I, stain_matrix, lamda=0.01):
    """
    Get concentrations, a npix x 2 matrix
    :param I:
    :param stain_matrix: a 2x3 stain matrix
    :return:
    """
    OD = RGB_to_OD(I).reshape((-1, 3))
    return spams.lasso(OD.T, D=stain_matrix.T, mode=2, lambda1=lamda, pos=True).toarray().T

# ==========================================================================================


def get_stain_matrix(I, threshold=0.8, lamda=0.1):
    """
    Get 2x3 stain matrix. First row H and second row E
    :param I:
    :param threshold:
    :param lamda:
    :return:
    """
    mask = notwhite_mask(I, thresh=threshold).reshape((-1,))
    OD = RGB_to_OD(I).reshape((-1, 3))
    OD = OD[mask]
    if OD.size == 0:
        raise ValueError("all pixels have all been masked as being to bright")
    dictionary = spams.trainDL(OD.T, K=2, lambda1=lamda, mode=2, modeD=0, posAlpha=True, posD=True, verbose=False).T
    if dictionary[0, 0] < dictionary[1, 0]:
        dictionary = dictionary[[1, 0], :]
    dictionary = normalize_rows(dictionary)
    return dictionary


class Vahadane():
    """
    A stain normalization object TODO
    """

    def __init__(self):
        super().__init__()
        self.stain_matrix_target = None

    def fit(self, target_image):
        if type(target_image) != 'numpy.ndarray':
            ValueError('Invalid input, try to pass your image as a Numpy matrix')
        target = standardize_brightness(target_image)
        self.stain_matrix_target = get_stain_matrix(target_image)

    def transform(self, I):
        if self.stain_matrix_target is None:
            raise AssertionError('Run fit function first.')
        if type(I) != 'numpy.ndarray':
            ValueError('Invalid input, try to pass your image as a Numpy matrix')
        I = standardize_brightness(I)
        stain_matrix_source = get_stain_matrix(I)
        source_concentrations = get_concentrations(I, stain_matrix_source)
        return (255 * np.exp(-1 * np.dot(source_concentrations, self.stain_matrix_target).reshape(I.shape))).astype(
            np.uint8)

    # def target_stains(self):
    #     return OD_to_RGB(self.stain_matrix_target)

    # def hematoxylin(self, I):
    #     I = standardize_brightness(I)
    #     h, w, c = I.shape
    #     stain_matrix_source = get_stain_matrix(I)
    #     source_concentrations = get_concentrations(I, stain_matrix_source)
    #     H = source_concentrations[:, 0].reshape(h, w)
    #     H = np.exp(-1 * H)
    #     return H
