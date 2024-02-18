import time
from numba import jit, njit, float32, float64, types, prange, typed, boolean, bool_, int8
from typing import Optional
import numpy as np
from scipy.spatial.distance import yule
from simba.mixins.statistics_mixin import Statistics
from simba.utils.data import hist_1d, bucket_data
try:
    from typing import Literal
except:
    from typing_extensions import Literal
from simba.utils.enums import Options
from simba.utils.checks import check_instance, check_str
from simba.utils.errors import CountError


#@jit(nopython=True)

@njit((float32[:], float32[:]))
def _hellinger_helper(x: np.ndarray, y: np.ndarray):
    """ Jitted helper for computing Hellinger distances from ``hellinger_distance``"""
    result, norm_x, norm_y = 0.0, 0.0, 0.0
    for i in range(x.shape[0]):
        result += np.sqrt(x[i] * y[i])
        norm_x += x[i]
        norm_y += y[i]
    if norm_x == 0 and norm_y == 0:
        return 0.0
    elif norm_x == 0 or norm_y == 0:
        return 1.0
    else:
        return np.sqrt(1 - result / np.sqrt(norm_x * norm_y))

def hellinger_distance(x: np.ndarray,
                       y: np.ndarray,
                       bucket_method: Optional[Literal['fd', 'doane', 'auto', 'scott', 'stone', 'rice', 'sturges', 'sqrt']] = 'auto') -> float:
    """
    Compute the Hellinger distance between two vector distribitions.

    :param np.ndarray x: First 1D array representing a probability distribution.
    :param np.ndarray y: Second 1D array representing a probability distribution.
    :param Optional[Literal['fd', 'doane', 'auto', 'scott', 'stone', 'rice', 'sturges', 'sqrt']] bucket_method: Method for computing histogram bins. Default is 'auto'.
    :returns float: Hellinger distance between the two input probability distributions.

    :example:
    >>> x = np.random.randint(0, 9000, (500000,))
    >>> y = np.random.randint(0, 9000, (500000,))
    >>> hellinger_distance(x=y, y=y, bucket_method='auto')
    """

    check_instance(source=f'{hellinger_distance.__name__} x', instance=x, accepted_types=np.ndarray)
    check_instance(source=f'{hellinger_distance.__name__} y', instance=y, accepted_types=np.ndarray)
    if (x.ndim != 1) or (y.ndim != 1): raise CountError(msg=f'x and y are not 1D arrays, got {x.ndim} and {y.ndim}', source=hellinger_distance.__name__)
    check_str(name=f'{hellinger_distance} method', value=bucket_method, options=Options.BUCKET_METHODS.value)
    bin_width, bin_count = bucket_data(data=x, method=bucket_method)
    s1_h = hist_1d(data=x, bins=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    s2_h = hist_1d(data=y, bins=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    return _hellinger_helper(x=s1_h.astype(np.float32), y=s2_h.astype(np.float32))












# @njit([(int8[:], int8[:], types.misc.Omitted(value=False), float32[:]),
#        (int8[:], int8[:], types.misc.Omitted(value=False), types.misc.Omitted(None)),
#        (int8[:], int8[:], bool_, float32[:]),
#        (int8[:], int8[:], bool_, types.misc.Omitted(None))])
# def hamming_distance(x: np.ndarray,
#                      y: np.ndarray,
#                      sort: Optional[bool] = False,
#                      w: Optional[np.ndarray] = None) -> float:
#     """
#     Calculate the Hamming distance between two vectors.
#
#     :parameter np.ndarray x: First binary vector.
#     :parameter np.ndarray x: Second binary vector.
#     :parameter Optional[np.ndarray] w: Optional weights for each element. Can be classification probabilities. If not provided, equal weights are assumed.
#     :parameter Optional[bool] sort: If True, sorts x and y prior to hamming distance calculation. Default, False.
#
#     :example:
#     >>> x, y = np.random.randint(0, 10, (10,)).astype(np.float32), np.random.randint(0, 10, (10,)).astype(np.float32)
#     >>> Statistics().hamming_distance(x=x, y=y)
#     >>> 0.91
#     """
#     #pass
#     if w is None:
#         w = np.ones(x.shape[0]).astype(np.float32)
#
#     results = 0.0
#     if sort: x, y = np.sort(x), np.sort(y)
#     for i in prange(x.shape[0]):
#         if x[i] != y[i]:
#             results += (1.0 * w[i])
#             print(w[i])
#     return results / x.shape[0]


# @njit([(float32[:,:], float32[:,:]),
#        (float32[:,:], types.misc.Omitted(None))])
# def bray_curtis_dissimilarity(x: np.ndarray, w: Optional[np.ndarray] = None) -> np.ndarray:
#     """
#     Calculate Bray-Curtis dissimilarity matrix between samples based on feature values.
#
#     Useful for finding similar frames based on behavior.
#
#     :parameter np.ndarray x: 2d array with likely normalized feature values.
#     :parameter Optional[np.ndarray] w: Optional 2d array with weights of same size as x. Default None and all observations will have the same weight.
#     :returns np.ndarray: 2d array with same size as x representing dissimilarity values. 0 and the observations are identical and at 1 the observations are completly disimilar.
#
#     :example:
#     >>> x = np.array([[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1]]).astype(np.float32)
#     >>> bray_curtis_dissimilarity(x=x)
#     >>> [[0, 1., 1., 0.], [1., 0., 0., 1.], [1., 0., 0., 1.], [0., 1., 1., 0.]]
#     """
#     if w is None:
#         w = np.ones((x.shape[0], x.shape[0])).astype(np.float32)
#
#     results = np.full((x.shape[0], x.shape[0]), 0.0)
#     for i in prange(x.shape[0]):
#         for j in range(i+1, x.shape[0]):
#             s1, s2, num, den = x[i], x[j], 0.0, 0.0
#             for k in range(s1.shape[0]):
#                 num += (np.abs(s1[k] - s2[k]))
#                 den += (np.abs(s1[k] + s2[k]))
#             if den == 0.0: val = 0.0
#             else: val = (float(num) / den) * w[i, j]
#             results[i, j] = val
#             results[j, i] = val
#     return results.astype(float32)





# # Example usage
# x = np.array([[1, 1, 1, 1, 1],
#              [0, 0, 0, 0, 0],
#             [0, 0, 0, 0, 0],
#               [1, 1, 1, 1, 1]]).astype(np.float32)
#
# bray_curtis_dissimilarity(x=x)

#hamming_distance(x=y, y=x, sort=True, w=w)

# print("Sokal-Sneath Distance:", distance_ss)
#
# x = np.random.randint(0, 2, (50,)).astype(np.int8)
# y = np.random.randint(0, 2, (50,)).astype(np.int8)







