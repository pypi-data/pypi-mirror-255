import numpy as np
from numpy.linalg import eig
from numba import njit, objmode, jit


def bah(data):
    x= np.real_if_close(data, tol=1)
    print(x.dtype)
    print(x.shape)
    return x
    #

@jit(nopython=True)
def rolling_pca(data: np.ndarray,
                window_sizes: np.ndarray,
                fps: int,
                n_components: int = 2) -> np.ndarray:

    results = np.full((data.shape[0], window_sizes.shape[0]), -1.0)
    for i in range(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * fps)
        for l, r in zip(range(0, data.shape[0] + 1), range(window_size, data.shape[0] + 1)):
            sample = data[l:r]
            print(sample)
            n = sample.shape[0]
            curr_arr = sample - (np.sum(sample, axis=0))
            curr_arr = curr_arr.astype(np.float32)
            cov = (curr_arr.T @ curr_arr)
            #print(cov)
            # with objmode(cov='float64[:,:]'):
            #     cov = x(cov)
            # print(cov)

            evals, evecs = np.linalg.eig(cov.astype(np.complex64))
            with objmode(evals='float32[:]', evecs='float32[:]'):
                evals, evecs = bah(evals), bah(evecs)
            print(evecs, evals)
            idx = np.argsort(evals)[:n_components]
            print(idx)
            evecs = evecs[:][idx].astype(np.float32)
            print(evecs.T.shape, curr_arr.T.shape)
            #reduced = (evecs.T @ curr_arr.T).T
            # print(reduced)
            # #reduced_out[start_idx: i, :] = reduced
            #


data = np.random.random((10, 10))


rolling_pca(data=data, window_sizes=np.array([1.0]), fps=10, n_components=2)