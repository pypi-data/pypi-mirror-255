from numba import cuda
import math
import numpy as np
import time

threadsperblock = 256


@cuda.jit
def sliding_ttest(data, stride, output):
    start = cuda.grid(1)
    stride_len = int(stride[0])
    if start < (data.shape[0] - stride_len):
        sample_1 = data[start:start + stride_len][0]
        sample_2 = data[start:start + stride_len][1]
        sample_1_sum = 0;
        sample_2_sum = 0;
        sample_1_deviation = 0;
        sample_2_deviation = 0
        for i in sample_1: sample_1_sum += i
        for i in sample_2: sample_2_sum += i
        sample_1_mean = sample_1_sum / sample_1.shape[0]
        sample_2_mean = sample_2_sum / sample_2.shape[0]
        for i in sample_1: sample_1_deviation += (sample_1_mean - i) ** 2
        for i in sample_2: sample_2_deviation += (sample_2_mean - i) ** 2
        sample_1_stdev = sample_1_deviation / sample_1.shape[0]
        sample_2_stdev = sample_2_deviation / sample_2.shape[0]
        pooled_std = math.sqrt(
            (len(sample_1) - 1) * sample_1_stdev ** 2 + (len(sample_2) - 1) * sample_2_stdev ** 2) / (
                                 len(sample_1) - 1) + (len(sample_2) - 1)

        result = (sample_1_mean - sample_2_mean) / (pooled_std * math.sqrt(1 / len(sample_1) + 1 / len(sample_1)))
        # output[start] = results
        output[start] += result


start = time.time()
sample_1 = np.random.randint(0, 10, (50000000,))
sample_2 = np.random.randint(0, 10, (50000000,))
sample_data = np.vstack((sample_1, sample_2)).T

results = np.full((sample_1.shape[0]), np.nan).astype(np.float64)

device_data = cuda.to_device(sample_data)
device_stride = cuda.to_device(np.array([10]).astype(np.float32))
device_results = cuda.device_array_like(results)

blocks_per_grid = math.ceil(sample_data.shape[0] / threadsperblock)
sliding_ttest[blocks_per_grid, threadsperblock](device_data, device_stride, device_results)
results = device_results.copy_to_host()
print(time.time() - start)