__author__ = "Simon Nilsson", "JJ Choong"
from simba.feature_extractors.unit_tests import (read_video_info_csv,
                                               read_video_info)
from simba.read_config_unit_tests import (read_config_entry,
                                          read_config_file,
                                          read_project_path_and_file_type)
from simba.train_model_functions import get_model_info
from simba.misc_tools import (get_fn_ext,
                              plug_holes_shortest_bout,
                              SimbaTimer)
from simba.utils.printing import stdout_success
from simba.enums import (ReadConfig,
                         Paths,
                         Dtypes)
from simba.drop_bp_cords import drop_bp_cords
from simba.rw_dfs import read_df, save_df
import os, glob
from copy import deepcopy
import pickle
import numpy as np
from simba.utils.errors import NoFilesFoundError

class RunModel(object):

    """
    Class for running classifier inference. Results are stored in the `project_folder/csv/machine_results`
    directory of the SimBA project.

    Parameters
    ----------
    config_path: str
        path to SimBA project config file in Configparser format

    Example
    ----------
    >>> inferencer = RunModel(config_path='MyConfigPath')
    >>> inferencer.run_models()
    """

    def __init__(self,
                 config_path: str):
        """
        Method to run classifier inference. Results are stored in the ``project_folder/csv/machine_results`` directory
        of the SimBA project.

        Returns
        ----------
        None

        """

        self.config = read_config_file(config_path)
        self.config_path = config_path
        self.project_path, self.file_type = read_project_path_and_file_type(config=self.config)
        self.model_cnt = read_config_entry(self.config, ReadConfig.SML_SETTINGS.value, ReadConfig.TARGET_CNT.value, data_type=Dtypes.INT.value)
        self.files_in_dir = os.path.join(self.project_path, Paths.FEATURES_EXTRACTED_DIR.value)
        self.files_out_dir = os.path.join(self.project_path, Paths.MACHINE_RESULTS_DIR.value)
        self.vid_info_df = read_video_info_csv(os.path.join(self.project_path, Paths.VIDEO_INFO.value))
        self.model_dict = get_model_info(self.config, self.model_cnt)
        self.files_found = glob.glob(self.files_in_dir + '/*.' + self.file_type)
        if len(self.files_found) == 0:
            raise NoFilesFoundError('Zero files found in the project_folder/csv/features_extracted directory. Create features before running classifier.')
        print('Analyzing {} file(s) with {} classifier(s)'.format(str(len(self.files_found)), str(len(self.model_dict))))
        self.timer = SimbaTimer()
        self.timer.start_timer()

    def run_models(self):
        for file_cnt, file_path in enumerate(self.files_found):
            _, file_name, _ = get_fn_ext(file_path)
            print('Analyzing video {}...'.format(file_name))
            file_save_path = os.path.join(self.files_out_dir, file_name + '.' + self.file_type)
            in_df = read_df(file_path, self.file_type)
            x_df = drop_bp_cords(in_df, self.config_path)
            _, px_per_mm, fps = read_video_info(self.vid_info_df, file_name)
            out_df = deepcopy(in_df)
            for m, m_hyp in self.model_dict.items():
                if not os.path.isfile(m_hyp['model_path']):
                    raise NoFilesFoundError(msg=f"{m_hyp['model_path']} is not a VALID model file path")
                clf = pickle.load(open(m_hyp['model_path'], 'rb'))
                probability_column = 'Probability_' + m_hyp['model_name']
                try:
                    p = clf.predict_proba(x_df)
                except ValueError as e:
                    print('FEATURE NUMBER ERROR: Mismatch in the number of features in input file and what is expected from the model in file ' + str(file_name) + ' and model ' + str(m))
                    print(e.args)
                    raise ValueError('FEATURE NUMBER ERROR: Mismatch in the number of features in input file and what is expected from the model in file ' + str(file_name) + ' and model ' + str(m))
                try:
                    out_df[probability_column] = p[:, 1]
                except IndexError as e:
                    print(e.args)
                    raise IndexError('SIMBA INDEX ERROR: Your classifier has not been created properly. See The SimBA GitHub FAQ page for more information and suggested fixes.')
                out_df[m_hyp['model_name']] = np.where(out_df[probability_column] > m_hyp['threshold'], 1, 0)
                out_df = plug_holes_shortest_bout(data_df=out_df, clf_name=m_hyp['model_name'], fps=fps, shortest_bout=m_hyp['minimum_bout_length'])
            save_df(out_df, self.file_type, file_save_path)
            print('Predictions created for {} ...'.format(file_name))
        self.timer.stop_timer()
        stdout_success(msg='Machine predictions complete. Files saved in project_folder/csv/machine_results directory', elapsed_time=self.timer.elapsed_time_str)

# test = RunModel(config_path='/Users/simon/Downloads/Automated PRT_test/project_folder/project_config.ini')
# test.run_models()

