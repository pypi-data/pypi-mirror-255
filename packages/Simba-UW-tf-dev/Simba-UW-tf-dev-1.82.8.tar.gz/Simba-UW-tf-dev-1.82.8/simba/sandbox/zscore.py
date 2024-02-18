import time

import numpy as np
from numba import njit, prange


@njit('(float32[:], float64[:], int64,)')
def sliding_z_scores(data: np.ndarray,
                     time_windows: np.ndarray,
                     fps: int) -> np.ndarray:

    """
    Calculate sliding Z-scores for a given data array over specified time windows.

    This function computes sliding Z-scores for a 1D data array over different time windows. The sliding Z-score
    is a measure of how many standard deviations a data point is from the mean of the surrounding data within
    the specified time window. This can be useful for detecting anomalies or variations in time-series data.

    :parameter ndarray data: 1D NumPy array containing the time-series data.
    :parameter ndarray time_windows: 1D NumPy array specifying the time windows in seconds over which to calculate the Z-scores.
    :parameter int time_windows: Frames per second, used to convert time windows from seconds to the corresponding number of data points.
    :returns np.ndarray: A 2D NumPy array containing the calculated Z-scores. Each row corresponds to the Z-scores calculated for a specific time window. The time windows are represented by the columns.

    :example:
    >>> data = np.random.randint(0, 100, (1000,)).astype(np.float32)
    >>> z_scores = sliding_z_scores(data=data, time_windows=np.array([1.0, 2.5]), fps=10)
    """

    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in range(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        for right in range(window_size-1, data.shape[0]):
            left = right - window_size+1
            sample_data = data[left:right+1]
            m, s = np.mean(sample_data), np.std(sample_data)
            vals = (sample_data - m) / s
            results[left:right+1, i] = vals

    return results