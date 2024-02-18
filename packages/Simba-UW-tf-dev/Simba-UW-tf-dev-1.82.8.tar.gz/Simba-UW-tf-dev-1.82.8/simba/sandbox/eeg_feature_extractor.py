import time

import numpy as np
import pandas as pd
from numba import typed
import pickle
from simba.mixins.timeseries_features_mixin import TimeseriesFeatureMixin


WINDOW_SIZES = np.array([0.5, 1.0, 2.0])

class EEGFeatureExtractor(TimeseriesFeatureMixin):

    def __init__(self,
                 data: np.ndarray,
                 sample_rate):

        TimeseriesFeatureMixin.__init__(self)
        self.sample_rate, self.data = sample_rate, data

    def run(self):
        self.hjort_parameters = self.sliding_hjort_parameters(data=self.data, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_mean_crossings = self.sliding_crossings(data=self.data, val=np.mean(data), window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_zero_crossings = self.sliding_crossings(data=self.data, val=0, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_80_20_percentile_difference = self.sliding_percentile_difference(data=self.data, upper_pct=80, lower_pct=20, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_percent_beyond_2_std = self.sliding_percent_beyond_n_std(data=self.data, n=2, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_percent_beyond_1_std = self.sliding_percent_beyond_n_std(data=self.data, n=1, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_percent_beyond_05_std = self.sliding_percent_beyond_n_std(data=self.data, n=0.5, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_percent_in_80_60_window = self.sliding_percent_in_percentile_window(data=self.data, upper_pct=80, lower_pct=60, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_percent_in_100_90_window = self.sliding_percent_in_percentile_window(data=self.data, upper_pct=100, lower_pct=90, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_percent_in_0_10_window = self.sliding_percent_in_percentile_window(data=self.data, upper_pct=10, lower_pct=0, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.sliding_percent_in_20_40_window = self.sliding_percent_in_percentile_window(data=self.data, upper_pct=40, lower_pct=20, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.petrosian_fractal_dimension = self.sliding_petrosian_fractal_dimension(data=self.data, window_sizes=WINDOW_SIZES, sample_rate=sample_rate)
        self.sliding_line_lengths = self.sliding_line_length(data=self.data, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate)
        self.descriptives = self.sliding_descriptive_statistics(data=self.data, window_sizes=WINDOW_SIZES, sample_rate=self.sample_rate, statistics=typed.List(['var', 'max', 'min', 'std', 'median', 'mean', 'mad']))


    def save(self):
        self.out_df = pd.DataFrame()
        self.out_df['DATA'] = self.data
        for i in range(WINDOW_SIZES.shape[0]):
            self.out_df[f'HJORT_MOBILITY_{WINDOW_SIZES[i]}'] = self.hjort_parameters[0, :, i]
            self.out_df[f'HJORT_COMPLEXITY_{WINDOW_SIZES[i]}'] = self.hjort_parameters[1, :, i]
            self.out_df[f'HJORT_ACTIVITY_{WINDOW_SIZES[i]}'] = self.hjort_parameters[2, :, i]
            self.out_df[f'SLIDING_MEAN_CROSSINGS_{WINDOW_SIZES[i]}'] = self.sliding_mean_crossings[:, i]
            self.out_df[f'SLIDING_ZERO_CROSSINGS_{WINDOW_SIZES[i]}'] = self.sliding_zero_crossings[:, i]
            self.out_df[f'SLIDING_80_20_PERCENTILE_CROSSINGS_{WINDOW_SIZES[i]}'] = self.sliding_zero_crossings[:, i]
            self.out_df[f'SLIDING_80_20_PERCENTILE_DIFFERENCE_{WINDOW_SIZES[i]}'] = self.sliding_80_20_percentile_difference[:, i]
            self.out_df[f'sliding_percent_beyond_2_std_{WINDOW_SIZES[i]}'] = self.sliding_percent_beyond_2_std[:, i]
            self.out_df[f'sliding_percent_beyond_1_std_{WINDOW_SIZES[i]}'] = self.sliding_percent_beyond_1_std[:, i]
            self.out_df[f'sliding_percent_beyond_0.5_std_{WINDOW_SIZES[i]}'] = self.sliding_percent_beyond_05_std[:, i]
            self.out_df[f'sliding_percent_in_80_60_window_{WINDOW_SIZES[i]}'] = self.sliding_percent_in_80_60_window[:, i]
            self.out_df[f'sliding_percent_in_100_90_window_{WINDOW_SIZES[i]}'] = self.sliding_percent_in_100_90_window[:, i]
            self.out_df[f'sliding_percent_in_0_10_window_{WINDOW_SIZES[i]}'] = self.sliding_percent_in_0_10_window[:, i]
            self.out_df[f'sliding_percent_in_20_40_window_{WINDOW_SIZES[i]}'] = self.sliding_percent_in_20_40_window[:, i]
            self.out_df[f'petrosian_fractal_dimension_{WINDOW_SIZES[i]}'] = self.petrosian_fractal_dimension[:, i]
            self.out_df[f'sliding_line_lengths_{WINDOW_SIZES[i]}'] = self.sliding_line_lengths[:, i]
            self.out_df[f'DESCRIPTIVES_VAR_{WINDOW_SIZES[i]}'] = self.descriptives[0, :, i]
            self.out_df[f'DESCRIPTIVES_MAX_{WINDOW_SIZES[i]}'] = self.descriptives[1, :, i]
            self.out_df[f'DESCRIPTIVES_MIN_{WINDOW_SIZES[i]}'] = self.descriptives[2, :, i]
            self.out_df[f'DESCRIPTIVES_STD_{WINDOW_SIZES[i]}'] = self.descriptives[3, :, i]
            self.out_df[f'DESCRIPTIVES_MEDIAN_{WINDOW_SIZES[i]}'] = self.descriptives[4, :, i]
            self.out_df[f'DESCRIPTIVES_MIN_{WINDOW_SIZES[i]}'] = self.descriptives[5, :, i]
            self.out_df[f'DESCRIPTIVES_MAD_{WINDOW_SIZES[i]}'] = self.descriptives[6, :, i]




        #for window_size in WINDOW_SIZES:








#data = (data - np.min(data)) / (np.max(data) - np.min(data))
DOWNSAMPLE_RATE = 10
with open('/Users/simon/Desktop/envs/eeg/sample_data/converted/split/G-008.pickle', 'rb') as handle:
    input = pickle.load(handle)

data = input['data'][1::DOWNSAMPLE_RATE]
sample_rate = input['frequency_parameters']['amplifier_sample_rate']

start = time.time()
feature_extractor = EEGFeatureExtractor(data=data, sample_rate=2000)
feature_extractor.run()
feature_extractor.save()
print(time.time() - start)


#feature_extractor.out_df