import numpy as np
from simba.utils.data import bucket_data
from simba.mixins.statistics_mixin import Statistics
from numpy.lib.stride_tricks import as_strided
from numba import jit
import numba as nb

# @jit(nopython=True)
# def vasicek_differential_entropy(data: np.ndarray,
#                                  time_windows: np.ndarray,
#                                  sample_rate: float):
#
#     m = np.sqrt(data.shape[0]) + 0.5
#     n = data.shape[-1]
#     shape = np.array(data.shape)
#     shape[-1] = m
#     Xl = nb.np..(data[..., [0]], shape)
#
#
#

data = np.random.randint(0, 100, (100))
vasicek_differential_entropy(data=data, time_windows=np.array([1.0]), sample_rate=20)




