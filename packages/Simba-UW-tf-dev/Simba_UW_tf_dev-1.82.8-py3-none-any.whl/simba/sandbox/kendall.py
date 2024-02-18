import numpy as np
from numba import njit, prange
import time



@njit('(float32[:], float32[:], float64[:], int64)')
def sliding_kendall_tau(sample_1: np.ndarray,
                        sample_2: np.ndarray,
                        time_windows: np.ndarray,
                        fps: float) -> np.ndarray:

    results = np.full((sample_1.shape[0], time_windows.shape[0]), 0.0)
    for time_window_cnt in range(time_windows.shape[0]):
        window_size = int(time_windows[time_window_cnt] * fps)
        for left, right in zip(range(0, sample_1.shape[0] + 1), range(window_size, sample_1.shape[0] + 1)):
            sliced_sample_1, sliced_sample_2 = sample_1[left:right], sample_2[left:right]
            rnks = np.argsort(sliced_sample_1)
            s1_rnk, s2_rnk = sliced_sample_1[rnks], sliced_sample_2[rnks]
            cncrdnt_cnts, dscrdnt_cnts = np.full((s1_rnk.shape[0] - 1), np.nan), np.full((s1_rnk.shape[0] - 1), np.nan)
            for i in range(s2_rnk.shape[0] - 1):
                cncrdnt_cnts[i] = np.argwhere(s2_rnk[i + 1:] > s2_rnk[i]).flatten().shape[0]
                dscrdnt_cnts[i] = np.argwhere(s2_rnk[i + 1:] < s2_rnk[i]).flatten().shape[0]
            results[right][time_window_cnt] = (np.sum(cncrdnt_cnts) - np.sum(dscrdnt_cnts)) / (np.sum(cncrdnt_cnts) + np.sum(dscrdnt_cnts))

    return results


data_sizes = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]
runs = 5

# data_sizes = [1]
# runs = 1
import pickle
for i in range(1, runs+1):
    print(i)
    for j in data_sizes:
        data_1 = np.random.randint(0, 50, (j)).astype(np.float32)
        data_2 = np.random.randint(0, 50, (j)).astype(np.float32)
        start = time.time()
        results = sliding_kendall_tau(sample_1=data_1, sample_2=data_2, time_windows=np.array([1.0]), fps=15)
        print(time.time() - start)