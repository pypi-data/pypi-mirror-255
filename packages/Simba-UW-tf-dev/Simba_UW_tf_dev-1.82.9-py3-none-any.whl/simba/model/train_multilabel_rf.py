import os
from typing import Union, Dict
import ast

from simba.utils.enums import TagNames, ConfigKey

from simba.mixins.config_reader import ConfigReader
from simba.mixins.train_model_mixin import TrainModelMixin
from simba.utils.printing import stdout_success, SimbaTimer, log_event
from simba.utils.checks import check_if_filepath_list_is_empty
from simba.utils.read_write import read_config_entry


class TrainMultiLabelRandomForestClassifier(ConfigReader, TrainModelMixin):
    def __init__(self,
                 config_path: Union[str, os.PathLike]):

        ConfigReader.__init__(self, config_path=config_path)
        TrainModelMixin.__init__(self)
        log_event(logger_name=str(self.__class__.__name__), log_type=TagNames.CLASS_INIT.value, msg=self.create_log_msg_from_init_args(locals=locals()))
        self.read_model_settings_from_config(config=self.config)

        check_if_filepath_list_is_empty(filepaths=self.target_file_paths, error_msg='Zero annotation files found in project_folder/csv/targets_inserted, cannot create model.')
        print(f'Reading in {len(self.target_file_paths)} annotated files...')
        self.data_df = self.read_all_files_in_folder_mp_futures(self.target_file_paths, self.file_type, [self.clf_name])

        self.check_raw_dataset_integrity(df=self.data_df, logs_path=self.logs_path)
        self.data_df_wo_cords = self.drop_bp_cords(df=self.data_df)
        annotation_cols_to_remove = self.read_in_all_model_names_to_remove(self.config, self.clf_cnt, self.clf_name)
        self.x_y_df = self.delete_other_annotation_columns(df=self.data_df_wo_cords, annotations_lst=list(annotation_cols_to_remove), raise_error=False)
        self.classifier_map = ast.literal_eval(read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, 'classifier_map', data_type='str'))

        self.x_df, self.y_df = self.split_df_to_x_y(self.x_y_df, self.clf_name)
        self.feature_names = self.x_df.columns
        self.check_sampled_dataset_integrity(x_df=self.x_df, y_df=self.y_df)
        print(f'Number of features in dataset: {len(self.feature_names)}')
        for k, v in self.classifier_map.items():
            print(self.y_df[self.y_df == k])
            #print(len(self.y_df[self.y_df[self.clf_name] == v]))






        print('Number of {} frames in dataset: {} ({}%)'.format(self.clf_name, str(self.y_df.sum()), str(round(self.y_df.sum() / len(self.y_df), 4) * 100)))
        print('Training and evaluating model...')


        print(self.x_y_df)


TrainMultiLabelRandomForestClassifier(config_path='/Users/simon/Desktop/envs/troubleshooting/multilabel/project_folder/project_config.ini')
