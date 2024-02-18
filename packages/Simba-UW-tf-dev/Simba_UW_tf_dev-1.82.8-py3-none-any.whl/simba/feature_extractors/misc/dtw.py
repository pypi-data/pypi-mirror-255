import numpy as np
from collections import defaultdict
from numba import jit


#@jit(nopython=True)
def dtw(sample_1: np.ndarray, sample_2: np.ndarray):

    #dist = abs(sample_1 - sample_2)
    window = np.full((int(sample_1.shape[0] * sample_2.shape[0]), 2), -1)

    cnt = 0
    for i in range(sample_1.shape[0]):
        for j in range(sample_2.shape[0]):
            window[cnt] = [i+1, j+1]
            cnt += 1

    D = np.full((int((sample_1.shape[0]+1) * (sample_2.shape[0]+1)), 1), -1)

    D = defaultdict(lambda: (float('inf'),))
    D[0, 0] = (0, 0, 0)
    for cnt, (i, j) in enumerate(window):
        dt = abs(sample_1[i-1] - sample_2[j-1])
        #print(cnt)


        D[i, j] = min((D[i - 1, j][0] + dt, i - 1, j), (D[i, j - 1][0] + dt, i, j - 1),
                      (D[i - 1, j - 1][0] + dt, i - 1, j - 1), key=lambda a: a[0])
    #print(D.keys())
    #print(len(D.keys()))

    # window = [(i, j) for i in range(len(sample_1)) for j in range(len(sample_2))]
    # print(window)
    # #print(window)
    #print(sample_1.shape[0])


sample_1 = np.array([1, 2, 3, 4, 5, 6])
sample_2 = np.array([2, 1, 5, 10, 5, 6])

dtw(sample_1=sample_1, sample_2=sample_2)