from statsmodels.tsa.stattools import adfuller, kpss, zivot_andrews, range_unit_root_test
import numpy as np
from numpy.lib.stride_tricks import as_strided
from simba.utils.read_write import find_core_cnt
import multiprocessing
try:
    from typing import Literal
except:
    from typing_extensions import Literal

from simba.utils.errors import InvalidInputError


def _adf_executor(data: np.ndarray) -> tuple:
    """
    Helper function to execute Augmented Dickey-Fuller (ADF) test on a data segment.
    Called by :meth:`timeseries_features_mixin.TimeseriesFeatureMixin.sliding_stationary_test_test`.
    """

    adfuller_results = adfuller(data)
    return adfuller_results[0], adfuller_results[1]

def _kpss_executor(data: np.ndarray):
    """
    Helper function to execute Kwiatkowski–Phillips–Schmidt–Shin (KPSS) test on a data segment.
    Called by :meth:`timeseries_features_mixin.TimeseriesFeatureMixin.sliding_stationary_test_test`.
    """

    kpss_results = kpss(data)
    return kpss_results[0], kpss_results[1]

def _zivotandrews_executor(data: np.ndarray):
    """
    Helper function to execute Zivot-Andrews structural-break unit-root test on a data segment.
    Called by :meth:`timeseries_features_mixin.TimeseriesFeatureMixin.sliding_stationary_test_test`.
    """
    try:
        za_results = zivot_andrews(data)
        return za_results[0], za_results[1]
    except (np.linalg.LinAlgError, ValueError):
        return 0, 0


def sliding_stationary_test_test(data: np.ndarray,
                                 time_windows: np.ndarray,
                                 sample_rate: int,
                                 test: Literal['ADF', 'KPSS', 'ZA'] = 'adf') -> (np.ndarray, np.ndarray):

    """
    Perform the Augmented Dickey-Fuller (ADF), Kwiatkowski-Phillips-Schmidt-Shin (KPSS), and Zivot-Andrews test on sliding windows of time series data.
    Parallel processing using all available cores is used to accelerate the computation.

    .. note::
       - ADF: A high p-value suggests non-stationarity, while a low p-value indicates stationarity.
       - KPSS: A high p-value suggests stationarity, while a low p-value indicates non-stationarity.
       - ZA: A high p-value suggests non-stationarity, while a low p-value indicates stationarity.

    :param np.ndarray data: 1-D NumPy array containing the time series data to be tested.
    :param np.ndarray time_windows: A 1-D NumPy array containing the time window sizes in seconds.
    :param np.ndarray sample_rate: The sample rate of the time series data (samples per second).
    :param Literal test: Test to perfrom: Options: 'ADF' (Augmented Dickey-Fuller), 'KPSS' (Kwiatkowski-Phillips-Schmidt-Shin), 'ZA' (Zivot-Andrews).
    :return (np.ndarray, np.ndarray): A tuple of two 2-D NumPy arrays containing test statistics and p-values. - The first array (stat) contains the ADF test statistics. - The second array (p_vals) contains the corresponding p-values

    :example:
    >>> data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    >>> sliding_stationary_test_test(data=data, time_windows=np.array([2.0]), test='KPSS', sample_rate=2)
    """

    stat = np.full((data.shape[0], time_windows.shape[0]), -1.0)
    p_vals = np.full((data.shape[0], time_windows.shape[0]), -1.0)
    if test == 'ADF':
        test_func = _adf_executor
    elif test == 'KPSS':
        test_func = _kpss_executor
    elif test == 'ZA':
        test_func = _zivotandrews_executor
    else:
        raise InvalidInputError(msg=f'Test {test} not recognized.')
    for i in range(time_windows.shape[0]):
        window_size = int(time_windows[i] * sample_rate)
        strided_data = as_strided(data,
                                  shape=(data.shape[0] - window_size + 1, window_size),
                                  strides=(data.strides[0] * 1, data.strides[0]))
        with multiprocessing.Pool(find_core_cnt()[0], maxtasksperchild=10) as pool:
            for cnt, result in enumerate(pool.imap(test_func, strided_data, chunksize=1)):
                stat[cnt+window_size-1, i] = result[0]
                p_vals[cnt + window_size - 1, i] = result[1]

    return stat, p_vals


#data = np.array([1, 0, 1, 4, 5, 6, 7, 1, 9, 1])
data = np.random.randint(0, 10, (100,))
sliding_stationary_test_test(data=data, test='ZA', time_windows=np.array([2.0]), sample_rate=10)
# from numpy.lib.stride_tricks import as_strided
# shape = (data.shape[0] - 2 + 1, 2)
# strides = (data.strides[0] * 1, data.strides[0])
# windows = as_strided(data, shape=shape, strides=strides)











# Parameters
# n = 100  # Number of data points
# t = np.arange(1, n + 1)  # Time index
# trend = 0.1  # Trend coefficient
# # Generate a dataset with a clear linear trend
# data = np.cumsum(np.random.normal(0, 1, n) + trend * t)
# result = adfuller(data)
# print("ADF Statistic:", result[0])
# print("P-value:", result[1])




# # Generate or load your time series data
# data = np.random.randint(0, 100, (100))
# adf(data=data)
#
# #
# # Perform the ADF test for structural break
# result = adfuller(data)
# print("ADF Statistic:", result[0])
# #print("P-value:", result[1])