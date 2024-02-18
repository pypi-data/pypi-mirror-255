__author__ = "Simon Nilsson"

import os
import platform
from configparser import ConfigParser
import csv

import simba
from simba.utils.printing import stdout_success, SimbaTimer
from simba.utils.errors import DirectoryExistError
from simba.enums import (DirNames,
                         ReadConfig,
                         Dtypes,
                         Paths)

class ProjectConfigCreator(object):

    """
    Class for creating SimBA project directory tree and project_config.ini

    Parameters
    ----------
    project_path: str
        Path to directory where to save the SimBA project directory tree
    project_name: str
        Name of the SimBA project
    target_list: list
        Classifiers in the SimBA project
    pose_estimation_bp_cnt: str
        String representing the number of body-parts in the pose-estimation data used in the simba project. E.g.,
        '16' or 'user-defined'.
    body_part_config_idx: int
        The index of the SimBA GUI dropdown pose-estimation selection. E.g., ``1``.
    animal_cnt: int
        Number of animals tracked in the input pose-estimation data.
    file_type: str
        The SimBA project file type. OPTIONS: ``csv`` or ``parquet``.

    Notes
    ----------
    `Create project tutorials <https://github.com/sgoldenlab/simba/blob/master/docs/tutorial.md#part-1-create-a-new-project-1>`__.

    Examples
    ----------
    >>> _ = ProjectConfigCreator(project_path = 'project/path', project_name='project_name', target_list=['Attack'], pose_estimation_bp_cnt='16', body_part_config_idx=9, animal_cnt=2, file_type='csv')

    """

    def __init__(self,
                 project_path: str,
                 project_name: str,
                 target_list: list,
                 pose_estimation_bp_cnt: str,
                 body_part_config_idx: int,
                 animal_cnt: int,
                 file_type: str = 'csv'):

        self.simba_dir = os.path.dirname(simba.__file__)
        self.animal_cnt = animal_cnt
        self.os_platform = platform.system()
        self.project_path = project_path
        self.project_name = project_name
        self.target_list = target_list
        self.pose_estimation_bp_cnt = pose_estimation_bp_cnt
        self.body_part_config_idx = body_part_config_idx
        self.file_type = file_type
        self.timer = SimbaTimer()
        self.timer.start_timer()
        self.__create_directories()
        self.__create_configparser_config()


    def __create_directories(self):
        self.project_folder = os.path.join(self.project_path, self.project_name, DirNames.PROJECT.value)
        self.models_folder = os.path.join(self.project_path, self.project_name, DirNames.MODEL.value)
        self.config_folder = os.path.join(self.project_folder, DirNames.CONFIGS.value)
        self.csv_folder = os.path.join(self.project_folder, DirNames.CSV.value)
        self.frames_folder = os.path.join(self.project_folder, DirNames.FRAMES.value)
        self.logs_folder = os.path.join(self.project_folder, DirNames.LOGS.value)
        self.measures_folder = os.path.join(self.logs_folder, DirNames.MEASURES.value)
        self.pose_configs_folder = os.path.join(self.measures_folder, DirNames.POSE_CONFIGS.value)
        self.bp_names_folder = os.path.join(self.pose_configs_folder, DirNames.BP_NAMES.value)
        self.videos_folder = os.path.join(self.project_folder, DirNames.VIDEOS.value)
        self.features_extracted_folder = os.path.join(self.csv_folder, DirNames.FEATURES_EXTRACTED.value)
        self.input_csv_folder = os.path.join(self.csv_folder, DirNames.INPUT_CSV.value)
        self.machine_results_folder = os.path.join(self.csv_folder, DirNames.MACHINE_RESULTS.value)
        self.outlier_corrected_movement_folder = os.path.join(self.csv_folder, DirNames.OUTLIER_MOVEMENT.value)
        self.outlier_corrected_location_folder = os.path.join(self.csv_folder, DirNames.OUTLIER_MOVEMENT_LOCATION.value)
        self.targets_inserted_folder = os.path.join(self.csv_folder, DirNames.TARGETS_INSERTED.value)
        self.input_folder = os.path.join(self.frames_folder, DirNames.INPUT.value)
        self.output_folder = os.path.join(self.frames_folder, DirNames.OUTPUT.value)

        folder_lst = [self.project_folder, self.models_folder, self.config_folder, self.csv_folder, self.frames_folder, self.logs_folder,
                       self.videos_folder, self.features_extracted_folder, self.input_csv_folder, self.machine_results_folder,
                       self.outlier_corrected_movement_folder, self.outlier_corrected_location_folder, self.targets_inserted_folder,
                       self.input_folder,self.output_folder, self.measures_folder, self.pose_configs_folder, self.bp_names_folder]

        for folder_path in folder_lst:
            if os.path.isdir(folder_path):
                raise DirectoryExistError(msg=f'SimBA tried to create {folder_path}, but it already exists. Please create your SimBA project in a new path, or move/delete your previous SimBA project')
            else:
                os.makedirs(folder_path)

    def __create_configparser_config(self):
        self.config = ConfigParser(allow_no_value=True)
        self.config.add_section(ReadConfig.GENERAL_SETTINGS.value)
        self.config[ReadConfig.GENERAL_SETTINGS.value][ReadConfig.PROJECT_PATH.value] = self.project_folder
        self.config[ReadConfig.GENERAL_SETTINGS.value][ReadConfig.PROJECT_NAME.value] = self.project_name
        self.config[ReadConfig.GENERAL_SETTINGS.value][ReadConfig.FILE_TYPE.value] = self.file_type
        self.config[ReadConfig.GENERAL_SETTINGS.value][ReadConfig.ANIMAL_CNT.value] = str(self.animal_cnt)
        self.config[ReadConfig.GENERAL_SETTINGS.value][ReadConfig.OS.value] = self.os_platform

        self.config.add_section(ReadConfig.SML_SETTINGS.value)
        self.config[ReadConfig.SML_SETTINGS.value][ReadConfig.MODEL_DIR.value] = self.models_folder
        for clf_cnt in range(len(self.target_list)):
            self.config[ReadConfig.SML_SETTINGS.value]['model_path_{}'.format(str(clf_cnt+1))] = os.path.join(self.models_folder, str(self.target_list[clf_cnt]) + '.sav')

        self.config[ReadConfig.SML_SETTINGS.value][ReadConfig.TARGET_CNT.value] = str(len(self.target_list))
        for clf_cnt in range(len(self.target_list)):
            self.config[ReadConfig.SML_SETTINGS.value]['target_name_{}'.format(str(clf_cnt+1))] = str(self.target_list[clf_cnt])

        self.config.add_section(ReadConfig.THRESHOLD_SETTINGS.value)
        for clf_cnt in range(len(self.target_list)):
            self.config[ReadConfig.THRESHOLD_SETTINGS.value]['threshold_{}'.format(str(clf_cnt + 1))] = Dtypes.NONE.value
        self.config[ReadConfig.THRESHOLD_SETTINGS.value][ReadConfig.SKLEARN_BP_PROB_THRESH.value] = str(0.00)

        self.config.add_section(ReadConfig.MIN_BOUT_LENGTH.value)
        for clf_cnt in range(len(self.target_list)):
            self.config[ReadConfig.MIN_BOUT_LENGTH.value]['min_bout_{}'.format(str(clf_cnt+1))] = Dtypes.NONE.value

        self.config.add_section(ReadConfig.FRAME_SETTINGS.value)
        self.config[ReadConfig.FRAME_SETTINGS.value][ReadConfig.DISTANCE_MM.value] = 0.00
        self.config.add_section(ReadConfig.LINE_PLOT_SETTINGS.value)
        self.config.add_section(ReadConfig.PATH_PLOT_SETTINGS.value)
        self.config.add_section(ReadConfig.ROI_SETTINGS.value)
        self.config.add_section(ReadConfig.PROCESS_MOVEMENT_SETTINGS.value)

        self.config.add_section(ReadConfig.CREATE_ENSEMBLE_SETTINGS.value)
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.POSE_SETTING.value] = str(self.pose_estimation_bp_cnt)
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.CLASSIFIER.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.TT_SIZE.value] = str(0.20)
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.UNDERSAMPLE_SETTING.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.UNDERSAMPLE_RATIO.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.OVERSAMPLE_SETTING.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.OVERSAMPLE_RATIO.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.RF_ESTIMATORS.value] = str(2000)
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.MIN_LEAF.value] = str(1)
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.RF_MAX_FEATURES.value] = Dtypes.SQRT.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.RF_JOBS.value] = str(-1)
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.RF_CRITERION.value] = Dtypes.ENTROPY.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.RF_METADATA.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.EX_DECISION_TREE.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.EX_DECISION_TREE_FANCY.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.IMPORTANCE_LOG.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.IMPORTANCE_BAR_CHART.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.PERMUTATION_IMPORTANCE.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.LEARNING_CURVE.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.PRECISION_RECALL.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.IMPORTANCE_BARS_N.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.LEARNING_CURVE_K_SPLITS.value] = Dtypes.NONE.value
        self.config[ReadConfig.CREATE_ENSEMBLE_SETTINGS.value][ReadConfig.LEARNING_DATA_SPLITS.value] = Dtypes.NONE.value

        self.config.add_section(ReadConfig.MULTI_ANIMAL_ID_SETTING.value)
        self.config[ReadConfig.MULTI_ANIMAL_ID_SETTING.value][ReadConfig.MULTI_ANIMAL_IDS.value] = Dtypes.NONE.value

        self.config.add_section(ReadConfig.OUTLIER_SETTINGS.value)
        self.config[ReadConfig.OUTLIER_SETTINGS.value][ReadConfig.MOVEMENT_CRITERION.value] = Dtypes.NONE.value
        self.config[ReadConfig.OUTLIER_SETTINGS.value][ReadConfig.LOCATION_CRITERION.value] = Dtypes.NONE.value

        self.config_path = os.path.join(self.project_folder, 'project_config.ini')
        with open(self.config_path, 'w') as file:
            self.config.write(file)

        bp_dir_path = os.path.join(self.simba_dir, Paths.SIMBA_BP_CONFIG_PATH.value)
        with open(bp_dir_path, "r", encoding='utf8') as f:
            cr = csv.reader(f, delimiter=",")  # , is default
            rows = list(cr)  # create a list of rows for instance

        chosen_bps = rows[self.body_part_config_idx]
        chosen_bps = list(filter(None, chosen_bps))

        project_bp_file_path = os.path.join(self.bp_names_folder, 'project_bp_names.csv')
        f = open(project_bp_file_path, 'w+')
        for i in chosen_bps:
            f.write(i + '\n')
        f.close()
        self.timer.stop_timer()

        stdout_success(msg=f'Project directory tree and project_config.ini created in {self.project_folder}', elapsed_time=self.timer.elapsed_time_str)