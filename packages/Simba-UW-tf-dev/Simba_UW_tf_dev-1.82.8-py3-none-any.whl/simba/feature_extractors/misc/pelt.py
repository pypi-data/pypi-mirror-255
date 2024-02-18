import time

import numpy as np
from numba import jit, njit, prange
try:
    from typing import Literal
except:
    from typing_extensions import Literal


#@jit(nopython=True)
@njit("(float32[:], int64,)", fastmath=True, parallel=True)
def pelt(data: np.ndarray, penalty: int):

    def var_cost(data, i, j):
        return np.var(data[i:j])

    cost_array = np.zeros((len(data) + 1))
    change_points = np.full((len(data)+1), 0)

    for j in prange(1, len(data) + 1):
        cost_array[j] = var_cost(data, 0, j)

    for j in prange(1, len(data) + 1):
        for i in range(1, j):
            c = var_cost(data, i, j) + penalty + cost_array[i]
            if c < cost_array[j]:
                cost_array[j] = c
                change_points[j] = i

    return change_points[1:]


# Example usage
import pickle
with open('/Users/simon/Desktop/envs/eeg/sample_data/converted/split/A-011.pickle', 'rb') as handle:
    data = pickle.load(handle)['data'] / 1000
data = data[:10000]
data = np.array([1, 2, 3, 10, 15, 20, 21, 22, 30, 32]).astype(np.float32)

start = time.time()
penalty = 10
change_points = pelt(data, penalty)
#print("Change points:", change_points)
print(time.time() - start)




