__author__ = "Simon Nilsson"

import pandas as pd
import os, glob
from collections import defaultdict
from simba.utils.checks import check_int, check_if_filepath_list_is_empty
from simba.utils.data import detect_bouts
from simba.utils.printing import stdout_success
from simba.utils.read_write import get_fn_ext, read_df
from simba.mixins.config_reader import ConfigReader
from simba.utils.errors import NoChoosenMeasurementError

class TimeBinsClf(ConfigReader):

    """
    Class for aggregating classification results into user-defined time-bins. Results are stored in
    the ``project_folder/logs`` directory of the SimBA project`

    Parameters
    ----------
    config_path: str
        path to SimBA project config file in Configparser format
    bin_length: int
        Integer representing the time bin size in seconds
    measurements: list
        Aggregate statistic measures to calculate for each time bin. OPTIONS: ['First occurance (s)', 'Event count',
        Total event duration (s)', 'Mean event duration (s)', 'Median event duration (s)', 'Mean event interval (s)',
        'Median event interval (s)']
    classifiers: list
        Names of classifiers to calculate aggregate statistics in time-bins for. EXAMPLE: ['Attack', 'Sniffing']

    Example
    ----------

    >>> timebin_clf_analyzer = TimeBinsClf(config_path='MyConfigPath', bin_length=15, measurements=['Event count', 'Total event duration (s)'])
    >>> timebin_clf_analyzer.analyze_timebins_clf()

    """

    def __init__(self,
                 config_path: str,
                 bin_length: int,
                 measurements: list,
                 classifiers: list):

        super().__init__(config_path=config_path)
        if len(measurements) == 0:
            raise NoChoosenMeasurementError()
        check_int(name='Bin length', value=bin_length, min_value=1)
        self.bin_length, self.measurements, self.classifiers = int(bin_length), measurements, classifiers
        self.files_found = glob.glob(self.machine_results_dir + '/*.' + self.file_type)
        check_if_filepath_list_is_empty(filepaths=self.files_found,
                                        error_msg=f'SIMBA ERROR: Cannot perform time-bin classification analysis, no data in {self.machine_results_dir} directory')
        print('Processing {} video(s)...'.format(str(len(self.files_found))))
        self.out_df_lst = []

    def analyze_timebins_clf(self):
        """
        Method for running the classifier time-bin analysis. Results are stored in the
        ``project_folder/logs`` directory of the SimBA project.

        Returns
        ----------
        None
        """

        video_dict = {}
        for file_cnt, file_path in enumerate(self.files_found):
            dir_name, file_name, extension = get_fn_ext(file_path)
            data_df = read_df(file_path, self.file_type)
            video_settings, px_per_mm, fps = self.read_video_info(video_name=file_name)
            fps = int(fps)
            bin_frame_length = self.bin_length * fps
            data_df_lst = [data_df[i:i + bin_frame_length] for i in range(0, data_df.shape[0], bin_frame_length)]
            video_dict[file_name] = {}
            for bin_cnt, df in enumerate(data_df_lst):
                video_dict[file_name][bin_cnt] = {}
                bouts_df = detect_bouts(data_df=df, target_lst=list(self.clf_names), fps=fps)
                bouts_df['Shifted start'] = bouts_df['Start_time'].shift(-1)
                bouts_df['Interval duration'] = bouts_df['Shifted start'] - bouts_df['End Time']
                for clf in self.clf_names:
                    video_dict[file_name][bin_cnt][clf] = defaultdict(list)
                    bout_df = bouts_df.loc[bouts_df['Event'] == clf]
                    if len(bouts_df) > 0:
                        video_dict[file_name][bin_cnt][clf]['First occurance (s)'] = round(bout_df['Start_time'].min(), 3)
                        video_dict[file_name][bin_cnt][clf]['Event count'] = len(bout_df)
                        video_dict[file_name][bin_cnt][clf]['Total event duration (s)'] = round(bout_df['Bout_time'].sum(), 3)
                        video_dict[file_name][bin_cnt][clf]['Mean event duration (s)'] = round(bout_df["Bout_time"].mean(), 3)
                        video_dict[file_name][bin_cnt][clf]['Median event duration (s)'] = round(bout_df['Bout_time'].median(), 3)
                    else:
                        video_dict[file_name][bin_cnt][clf]['First occurance (s)'] = None
                        video_dict[file_name][bin_cnt][clf]['Event count'] = 0
                        video_dict[file_name][bin_cnt][clf]['Total event duration (s)'] = 0
                        video_dict[file_name][bin_cnt][clf]['Mean event duration (s)'] = 0
                        video_dict[file_name][bin_cnt][clf]['Median event duration (s)'] = 0
                    if len(bouts_df) > 1:
                        video_dict[file_name][bin_cnt][clf]['Mean event interval (s)'] = round(bout_df[:-1]['Interval duration'].mean(), 3)
                        video_dict[file_name][bin_cnt][clf]['Median event interval (s)'] = round(bout_df[:-1]['Interval duration'].median(), 3)
                    else:
                        video_dict[file_name][bin_cnt][clf]['Mean event interval (s)'] = None
                        video_dict[file_name][bin_cnt][clf]['Median event interval (s)'] = None

        for video_name, video_info in video_dict.items():
            for bin_number, bin_data in video_info.items():
                data_df = pd.DataFrame.from_dict(bin_data).reset_index().rename(columns={'index':'Measurement'})
                data_df = pd.melt(data_df, id_vars=['Measurement']).rename(columns={'value':'Value', 'variable': 'Classifier'})
                data_df.insert(loc=0, column='Time bin #', value=bin_number)
                data_df.insert(loc=0, column='Video', value=video_name)
                self.out_df_lst.append(data_df)
        out_df = pd.concat(self.out_df_lst, axis=0).sort_values(by=['Video', 'Time bin #']).set_index('Video')
        out_df = out_df[out_df['Measurement'].isin(self.measurements)]
        out_df = out_df[out_df['Classifier'].isin(self.classifiers)]
        save_path = os.path.join(self.project_path, 'logs', 'Time_bins_ML_results_' + self.datetime + '.csv')
        out_df.to_csv(save_path)
        self.timer.stop_timer()
        stdout_success(msg=f'Classification time-bins results saved at project_folder/logs/output/{str("Time_bins_ML_results_" + self.datetime + ".csv")}', elapsed_time=self.timer.elapsed_time_str)

# test = TimeBinsClf(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini',
#                    bin_length=2,
#                    measurements=['First occurance (s)', 'Event count', 'Total event duration (s)', 'Mean event duration (s)'],
#                    classifiers=['Attack', 'Sniffing'])
# test.analyze_timebins_clf()


# test = TimeBinsClf(config_path='/Users/simon/Desktop/troubleshooting/light_analyzer/project_folder/project_config.ini',
#                    bin_length=2,
#                    measurements=['First occurance (s)', 'Event count', 'Total event duration (s)', 'Mean event duration (s)'])
# test.analyze_timebins_clf()
