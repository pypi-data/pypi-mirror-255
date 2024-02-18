import numpy as np
from numba import jit, float32, int64, prange, types, njit, float64, typed, boolean
from typing import Optional, Tuple, Union


@jit(nopython=True)
#@njit([(float32[:], float64, int64, boolean),])
def kmeans_1d(data: np.ndarray,
                    k: int,
                    max_iters: int,
                    calc_medians: bool) -> Tuple[np.ndarray, np.ndarray, Union[None, types.DictType]]:

    """
    Perform k-means clustering on a 1-dimensional dataset.

    :parameter np.ndarray data: 1d array containing feature values.
    :parameter int k: Number of clusters.
    :parameter int max_iters: Maximum number of iterations for the k-means algorithm.
    :parameter bool calc_medians: Flag indicating whether to calculate cluster medians.
    :returns Tuple: Tuple of three elements. Final centroids of the clusters. Labels assigned to each data point based on clusters. Cluster medians (if calc_medians is True), otherwise None.

    :example:
    >>> data_1d = np.array([1, 2, 3, 55, 65, 40, 43, 40]).astype(np.float64)
    >>> centroids, labels, medians = kmeans_1d(data_1d, 2, 1000, True)
    """

    data = np.ascontiguousarray(data)
    X = data.reshape((data.shape[0], 1))
    labels, medians = None, None
    centroids = X[np.random.choice(data.shape[0], k, replace=False)].copy()
    for _ in range(max_iters):
        labels = np.zeros(X.shape[0], dtype=np.int64)
        for i in range(X.shape[0]):
            min_dist = np.inf
            for j in range(k):
                dist = np.abs(X[i] - centroids[j])
                dist_sum = np.sum(dist)
                if dist_sum < min_dist:
                    min_dist = dist_sum
                    labels[i] = j

        new_centroids = np.zeros_like(centroids)
        counts = np.zeros(k, dtype=np.int64)
        for i in range(X.shape[0]):
            cluster = labels[i]
            new_centroids[cluster] += X[i]
            counts[cluster] += 1

        for j in range(k):
            if counts[j] > 0:
                new_centroids[j] /= counts[j]

        if np.array_equal(centroids, new_centroids):
            break
        else:
            centroids = new_centroids

    if calc_medians:
        labels, medians = labels.astype(np.int64), {}
        for i in prange(0, k, 1):
            medians[i] = np.median(data[np.argwhere(labels == i).flatten()])

    return centroids, labels, medians


# Example usage
#data_1d = np.random.rand(10000)

data_1d = np.array([1, 2, 3, 55, 65, 40, 43, 40]).astype(np.float64)
k = 2
centroids, labels, medians = kmeans_1d(data_1d, k, 1000, True)


mean_cluster1 = 3
std_dev_cluster1 = 1

# Mean and standard deviation for the second cluster
mean_cluster2 = 8
std_dev_cluster2 = 1

cluster1 = np.random.normal(loc=10, scale=1, size=10000)
cluster2 = np.random.normal(loc=20, scale=1, size=10000)

#data_1d = np.concatenate([cluster1, cluster2]).astype(np.float64)


import time
start = time.time()
centroids, labels, medians = kmeans_1d(data_1d, k, 1000, True)
print("Centroids:", centroids)
print("Labels:", labels)
print(time.time() - start)
