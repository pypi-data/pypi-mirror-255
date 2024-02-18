__author__ = "Simon Nilsson"

import pandas as pd
import os, ast
import webbrowser
from tkinter import *
from simba.ui.tkinter_functions import (DropDownMenu,
                                        FileSelect,
                                        Entry_Box,
                                        CreateLabelFrameWithIcon)
from simba.utils.enums import (Options,
                               Formats,
                               Keys,
                               Links,
                               TagNames,
                               ConfigKey,
                               Dtypes,
                               MLParamKeys)
from simba.utils.read_write import find_files_of_filetypes_in_directory, get_fn_ext, read_config_entry
from simba.utils.printing import stdout_success, stdout_trash, stdout_warning, log_event
from simba.utils.errors import InvalidHyperparametersFileError, NoFilesFoundError
from simba.utils.checks import (check_int, check_float, check_file_exist_and_readable)
from simba.mixins.pop_up_mixin import PopUpMixin
from simba.mixins.config_reader import ConfigReader

class MachineModelSettingsPopUp(PopUpMixin, ConfigReader):
    """
    Launch GUI window for specifying ML model training parameters.
    """

    def __init__(self,
                 config_path: str):

        ConfigReader.__init__(self, config_path=config_path)
        PopUpMixin.__init__(self, title="MACHINE MODEL SETTINGS", size=(450, 700))
        log_event(logger_name=str(__class__.__name__), log_type=TagNames.CLASS_INIT.value, msg=self.create_log_msg_from_init_args(locals=locals()))
        if not os.path.exists(self.configs_meta_dir): os.makedirs(self.configs_meta_dir)
        self.clf_options = Options.CLF_MODELS.value
        self.max_features_options = Options.CLF_MAX_FEATURES.value
        self.criterion_options = Options.CLF_CRITERION.value
        self.under_sample_options = Options.UNDERSAMPLE_OPTIONS.value
        self.over_sample_options = Options.OVERSAMPLE_OPTIONS.value
        self.class_weighing_options = Options.CLASS_WEIGHT_OPTIONS.value
        self.train_test_sizes_options = Options.CLF_TEST_SIZE_OPTIONS.value
        self.class_weights_options = list(range(1, 11, 1))
        load_meta_data_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header='LOAD META-DATA', icon_name=Keys.DOCUMENTATION.value, icon_link=Links.TRAIN_ML_MODEL.value)
        self.select_config_file = FileSelect(load_meta_data_frm, 'CONFIG PATH:', file_types=[('CSV', '*.csv')], initialdir=self.configs_meta_dir)
        load_config_btn = Button(load_meta_data_frm, text='LOAD', fg='blue', command= lambda: self.load_config())
        label_link = Label(load_meta_data_frm,text='[MODEL SETTINGS TUTORIAL]', fg='blue')
        label_link.bind('<Button-1>', lambda e: webbrowser.open_new(Links.TRAIN_ML_MODEL.value))

        machine_model_frm = LabelFrame(self.main_frm, text='MACHINE MODEL ALGORITHM', font=Formats.LABELFRAME_HEADER_FORMAT.value)
        self.machine_model_dropdown = DropDownMenu(machine_model_frm, 'ALGORITHM: ', self.clf_options, '25')
        self.machine_model_dropdown.popupMenu['menu'].entryconfigure(self.clf_options[1], state="disabled")
        self.machine_model_dropdown.popupMenu['menu'].entryconfigure(self.clf_options[2], state="disabled")
        self.machine_model_dropdown.setChoices(self.clf_options[0])

        behavior_frm = LabelFrame(self.main_frm, text='BEHAVIOR', font=Formats.LABELFRAME_HEADER_FORMAT.value)
        self.behavior_name_dropdown = DropDownMenu(behavior_frm, 'BEHAVIOR: ', self.clf_names, '25')
        self.behavior_name_dropdown.setChoices(self.clf_names[0])

        self.hyperparameters_frm = LabelFrame(self.main_frm, text='HYPER-PARAMETERS', font=Formats.LABELFRAME_HEADER_FORMAT.value)
        self.estimators_entrybox = Entry_Box(self.hyperparameters_frm, 'Random forest estimators:', '25', validation='numeric')
        n_estimators = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.RF_ESTIMATORS.value, data_type=Dtypes.INT.value, default_value=2000)
        self.estimators_entrybox.entry_set(val=n_estimators)

        self.max_features_dropdown = DropDownMenu(self.hyperparameters_frm, 'Max features: ', self.max_features_options, '25')
        max_features = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.RF_MAX_FEATURES.value, data_type=Dtypes.STR.value, default_value=self.max_features_options[0])
        self.max_features_dropdown.setChoices(max_features)
        self.criterion_dropdown = DropDownMenu(self.hyperparameters_frm, 'Criterion: ', self.criterion_options, '25')
        self.criterion_dropdown.setChoices(self.criterion_options[0])
        self.train_test_size_dropdown = DropDownMenu(self.hyperparameters_frm, 'Test Size: ', self.train_test_sizes_options, '25')
        train_test_size = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.TT_SIZE.value, data_type=Dtypes.STR.value, default_value="0.2")
        self.train_test_size_dropdown.setChoices(str(train_test_size))
        train_test_split_type = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.TRAIN_TEST_SPLIT_TYPE.value, data_type=Dtypes.STR.value, default_value=Options.TRAIN_TEST_SPLIT.value[0])
        self.train_test_type_dropdown = DropDownMenu(self.hyperparameters_frm, 'Train-test Split Type: ', Options.TRAIN_TEST_SPLIT.value, '25')
        self.train_test_type_dropdown.setChoices(str(train_test_split_type))
        min_sample_leaf = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.MIN_LEAF.value, data_type=Dtypes.INT.value, default_value=1)
        self.min_sample_leaf_eb = Entry_Box(self.hyperparameters_frm, 'Minimum sample leaf:', '25', validation='numeric')
        self.min_sample_leaf_eb.entry_set(val=min_sample_leaf)
        max_depth = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.RF_MAX_DEPTH.value, data_type=Dtypes.INT.value, default_value=Dtypes.NONE.value)
        max_depth_dropdown_vals = ['None']
        max_depth_dropdown_vals.extend([str(x) for x in list(range(1, 26))])
        self.max_depth_dropdown = DropDownMenu(self.hyperparameters_frm, 'Max depth: ', max_depth_dropdown_vals, '25')
        self.max_depth_dropdown.setChoices(max_depth)
        self.under_sample_ratio_entrybox = Entry_Box(self.hyperparameters_frm, 'UNDER-sample ratio: ', '25', status=DISABLED)
        undersample_settings = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.UNDERSAMPLE_SETTING.value, data_type=Dtypes.STR.value, default_value='None')
        self.undersample_settings_dropdown = DropDownMenu(self.hyperparameters_frm, 'UNDER-sample setting: ', self.under_sample_options, '25', com=lambda x: self.dropdown_switch_entry_box_state(self.under_sample_ratio_entrybox, self.undersample_settings_dropdown))
        self.undersample_settings_dropdown.setChoices(undersample_settings)
        if undersample_settings != 'None':
            self.under_sample_ratio_entrybox.set_state(NORMAL)
            undersample_ratio = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.UNDERSAMPLE_RATIO.value, data_type=Dtypes.FLOAT.value, default_value=0.0)
            self.under_sample_ratio_entrybox.entry_set(val=undersample_ratio)
        else:
            self.under_sample_ratio_entrybox.set_state(DISABLED)

        self.over_sample_ratio_entrybox = Entry_Box(self.hyperparameters_frm, 'OVER-sample ratio: ', '25', status=DISABLED)
        oversample_settings = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.OVERSAMPLE_SETTING.value, data_type=Dtypes.STR.value, default_value='None')
        self.oversample_settings_dropdown = DropDownMenu(self.hyperparameters_frm, 'OVER-sample setting: ', self.over_sample_options, '25', com=lambda x: self.dropdown_switch_entry_box_state(self.over_sample_ratio_entrybox, self.oversample_settings_dropdown))
        self.oversample_settings_dropdown.setChoices(oversample_settings)

        if oversample_settings != 'None':
            self.over_sample_ratio_entrybox.set_state(NORMAL)
            oversample_ratio = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.OVERSAMPLE_RATIO.value, data_type=Dtypes.FLOAT.value, default_value=0.0)
            self.over_sample_ratio_entrybox.entry_set(val=oversample_ratio)
        else:
            self.over_sample_ratio_entrybox.set_state(DISABLED)


        class_weights_settings = read_config_entry(self.config, ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.CLASS_WEIGHTS.value, data_type=Dtypes.STR.value, default_value='None')
        self.class_weights_dropdown = DropDownMenu(self.hyperparameters_frm, 'Class-weights setting: ', self.class_weighing_options, '25', com=lambda x: self.create_class_weight_table())
        self.class_weights_dropdown.setChoices(class_weights_settings)


        self.evaluations_frm = LabelFrame(self.main_frm, text='MODEL EVALUATION SETTINGS', font=Formats.LABELFRAME_HEADER_FORMAT.value)
        self.create_train_test_log_var = BooleanVar()
        self.create_example_decision_tree_graphviz_var = BooleanVar()
        self.create_example_decision_tree_dtreeviz_var = BooleanVar()
        self.create_clf_report_var = BooleanVar()
        self.create_clf_importance_bars_var = BooleanVar()
        self.feature_permutation_importance_var = BooleanVar()
        self.create_pr_curve_var = BooleanVar()
        self.partial_dependency_var = BooleanVar()
        self.calc_shap_scores_var = BooleanVar()
        self.learning_curve_var = BooleanVar()
        self.create_meta_data_file_var = BooleanVar()

        self.meta_data_file_cb = Checkbutton(self.evaluations_frm,text='Create model meta data file', variable=self.create_meta_data_file_var)
        self.create_train_test_log_cb = Checkbutton(self.evaluations_frm,text='Create train/test video and frame index log', variable=self.create_train_test_log_var)
        self.decision_tree_graphviz_cb = Checkbutton(self.evaluations_frm, text='Create Example Decision Tree (requires "graphviz")', variable=self.create_example_decision_tree_graphviz_var)
        self.decision_tree_dtreeviz_cb = Checkbutton(self.evaluations_frm, text='Create Fancy Example Decision Tree (requires "dtreeviz")', variable=self.create_example_decision_tree_dtreeviz_var)
        self.clf_report_cb = Checkbutton(self.evaluations_frm, text='Create Classification Report', variable=self.create_clf_report_var)
        self.n_features_bars_entry_dropdown = DropDownMenu(self.evaluations_frm, '# Features: ', list(range(5, 105, 5)), '25')
        self.n_features_bars_entry_dropdown.setChoices(20)
        self.n_features_bars_entry_dropdown.disable()
        self.bar_graph_cb = Checkbutton(self.evaluations_frm, text='Create Features Importance Bar Graph', variable=self.create_clf_importance_bars_var, command=lambda: self.enable_dropdown_from_checkbox(check_box_var=self.create_clf_importance_bars_var, dropdown_menus=[self.n_features_bars_entry_dropdown]))
        self.feature_permutation_cb = Checkbutton(self.evaluations_frm, text='Compute Feature Permutation Importances (Note: CPU intensive)', variable=self.feature_permutation_importance_var)
        self.learning_curve_k_splits_dropdown = DropDownMenu(self.evaluations_frm, 'Learning Curve Shuffle K Splits: ', list(range(2, 21)), '25')
        self.learning_curve_k_splits_dropdown.disable()
        self.learning_curve_k_splits_dropdown.setChoices(5)
        self.learning_curve_data_splits_dropdown = DropDownMenu(self.evaluations_frm, 'Learning Curve Shuffle Data Splits: ', list(range(2, 21)), '25')
        self.learning_curve_data_splits_dropdown.disable()
        self.learning_curve_data_splits_dropdown.setChoices(5)
        self.learning_curve_cb = Checkbutton(self.evaluations_frm, text='Create Learning Curves (Note: CPU intensive)', variable=self.learning_curve_var, command=lambda: self.enable_dropdown_from_checkbox(check_box_var=self.learning_curve_var, dropdown_menus=[self.learning_curve_k_splits_dropdown, self.learning_curve_data_splits_dropdown]))
        self.create_pr_curve_cb = Checkbutton(self.evaluations_frm, text='Create Precision Recall Curves', variable=self.create_pr_curve_var)
        self.shap_present = Entry_Box(self.evaluations_frm, '# target present', '25', status=DISABLED, validation='numeric')
        self.shap_absent = Entry_Box(self.evaluations_frm, '# target absent', '25', status=DISABLED,  validation='numeric')
        self.shap_save_it_dropdown = DropDownMenu(self.evaluations_frm, 'SHAP save cadence: ', [1, 10, 100, 1000, 'ALL FRAMES'],  '25')
        self.shap_save_it_dropdown.setChoices('ALL FRAMES')
        self.shap_save_it_dropdown.disable()
        self.shap_multiprocess_dropdown = DropDownMenu(self.evaluations_frm, 'Multi-process SHAP values: ', ['True', 'False'], '25', com=lambda x: self.change_shap_cadence_options(x))
        self.shap_multiprocess_dropdown.setChoices('False')
        self.shap_multiprocess_dropdown.disable()


        self.partial_dependency_cb = Checkbutton(self.evaluations_frm, text='Calculate partial dependencies (Note: CPU intensive)', variable=self.partial_dependency_var)
        self.calculate_shap_scores_cb = Checkbutton(self.evaluations_frm, text='Calculate SHAP scores', variable=self.calc_shap_scores_var, command=lambda: [self.enable_entrybox_from_checkbox(check_box_var=self.calc_shap_scores_var, entry_boxes=[self.shap_present,self.shap_absent]),
                                                                                                                                                             self.enable_dropdown_from_checkbox(check_box_var=self.calc_shap_scores_var, dropdown_menus=[self.shap_save_it_dropdown, self.shap_multiprocess_dropdown])])
        self.save_frame = LabelFrame(self.main_frm, text='SAVE', font=Formats.LABELFRAME_HEADER_FORMAT.value)
        save_global_btn = Button(self.save_frame, text='SAVE SETTINGS (GLOBAL ENVIRONMENT)', font=Formats.LABELFRAME_HEADER_FORMAT.value, fg='blue', command=lambda: self.save_global())
        save_meta_btn = Button(self.save_frame, text='SAVE SETTINGS (SPECIFIC MODEL)', font=Formats.LABELFRAME_HEADER_FORMAT.value, fg='green', command=lambda: self.save_config())
        clear_cache_btn = Button(self.save_frame,text='CLEAR CACHE', font=Formats.LABELFRAME_HEADER_FORMAT.value,fg='red', command=lambda: self.clear_cache())

        load_meta_data_frm.grid(row=0, column=0, sticky=NW)
        self.select_config_file.grid(row=0, column=0, sticky=NW)
        load_config_btn.grid(row=1, column=0, sticky=NW)
        label_link.grid(row=2, column=0, sticky=NW)

        machine_model_frm.grid(row=1, column=0, sticky=NW)
        self.machine_model_dropdown.grid(row=0, column=0, sticky=NW)

        behavior_frm.grid(row=2, column=0, sticky=NW)
        self.behavior_name_dropdown.grid(row=0, column=0, sticky=NW)

        self.hyperparameters_frm.grid(row=3, column=0, sticky=NW)
        self.estimators_entrybox.grid(row=0, column=0, sticky=NW)
        self.max_features_dropdown.grid(row=1, column=0, sticky=NW)
        self.criterion_dropdown.grid(row=2, column=0, sticky=NW)
        self.train_test_size_dropdown.grid(row=3, column=0, sticky=NW)
        self.train_test_type_dropdown.grid(row=4, column=0, sticky=NW)
        self.min_sample_leaf_eb.grid(row=5, column=0, sticky=NW)
        self.max_depth_dropdown.grid(row=6, column=0, sticky=NW)
        self.undersample_settings_dropdown.grid(row=7, column=0, sticky=NW)
        self.under_sample_ratio_entrybox.grid(row=8, column=0, sticky=NW)
        self.oversample_settings_dropdown.grid(row=9, column=0, sticky=NW)
        self.over_sample_ratio_entrybox.grid(row=10, column=0, sticky=NW)
        self.class_weights_dropdown.grid(row=11, column=0, sticky=NW)

        self.evaluations_frm.grid(row=4, column=0, sticky=NW)
        self.meta_data_file_cb.grid(row=0, column=0, sticky=NW)
        self.create_train_test_log_cb.grid(row=1, column=0, sticky=NW)
        self.decision_tree_graphviz_cb.grid(row=2, column=0, sticky=NW)
        self.decision_tree_dtreeviz_cb.grid(row=3, column=0, sticky=NW)
        self.clf_report_cb.grid(row=4, column=0, sticky=NW)
        self.bar_graph_cb.grid(row=5, column=0, sticky=NW)
        self.n_features_bars_entry_dropdown.grid(row=6, column=0, sticky=NW)
        self.feature_permutation_cb.grid(row=7, column=0, sticky=NW)
        self.learning_curve_cb.grid(row=8, column=0, sticky=NW)
        self.learning_curve_k_splits_dropdown.grid(row=9, column=0, sticky=NW)
        self.learning_curve_data_splits_dropdown.grid(row=10, column=0, sticky=NW)
        self.create_pr_curve_cb.grid(row=11, column=0, sticky=NW)
        self.partial_dependency_cb.grid(row=12, column=0, sticky=NW)
        self.calculate_shap_scores_cb.grid(row=13, column=0, sticky=NW)
        self.shap_present.grid(row=14, column=0, sticky=NW)
        self.shap_absent.grid(row=15, column=0, sticky=NW)
        self.shap_save_it_dropdown.grid(row=16, column=0, sticky=NW)
        self.shap_multiprocess_dropdown.grid(row=17, column=0, sticky=NW)

        self.save_frame.grid(row=5, column=0, sticky=NW)
        save_global_btn.grid(row=0, column=0, sticky=NW)
        save_meta_btn.grid(row=1, column=0, sticky=NW)
        clear_cache_btn.grid(row=2, column=0, sticky=NW)

        self.main_frm.mainloop()

    def dropdown_switch_entry_box_state(self,
                                        box,
                                        dropdown):

        if dropdown.getChoices() != 'None':
            box.set_state(NORMAL)
        else:
            box.set_state(DISABLED)

    def create_class_weight_table(self):
        if hasattr(self, 'class_weight_frm'):
            self.weight_present.destroy()
            self.weight_absent.destroy()
            self.class_weight_frm.destroy()

        if self.class_weights_dropdown.getChoices() == 'custom':
            self.class_weight_frm = LabelFrame(self.hyperparameters_frm, text='CLASS WEIGHTS', font=Formats.LABELFRAME_HEADER_FORMAT.value, pady=10)
            self.weight_present = DropDownMenu(self.class_weight_frm, '{} PRESENT: '.format(self.behavior_name_dropdown.getChoices()), self.class_weights_options, '25')
            self.weight_present.setChoices(2)
            self.weight_absent = DropDownMenu(self.class_weight_frm, '{} ABSENT: '.format(self.behavior_name_dropdown.getChoices()), self.class_weights_options, '25')
            self.weight_absent.setChoices(1)

            self.class_weight_frm.grid(row=12, column=0, sticky=NW)
            self.weight_present.grid(row=0, column=0, sticky=NW)
            self.weight_absent.grid(row=1, column=0, sticky=NW)

    def __checks(self):
        check_int(name='Random forest estimators', value=self.estimators_entrybox.entry_get)
        check_int(name='Minimum sample leaf', value=self.min_sample_leaf_eb.entry_get)
        if self.undersample_settings_dropdown.getChoices() != 'None':
            check_float(name='UNDER SAMPLE RATIO', value=self.under_sample_ratio_entrybox.entry_get)
        if self.oversample_settings_dropdown.getChoices() != 'None':
            check_float(name='OVER SAMPLE RATIO', value=self.over_sample_ratio_entrybox.entry_get)
        if self.create_clf_importance_bars_var.get():
            check_int(name='# FEATURES', value=self.n_features_bars_entry_dropdown.getChoices(), min_value=1)
        if self.learning_curve_var.get():
            check_int(name='LEARNING CURVE K SPLITS', value=self.learning_curve_k_splits_dropdown.getChoices())
            check_int(name='LEARNING CURVE DATA SPLITS', value=self.learning_curve_data_splits_dropdown.getChoices())
        if self.calc_shap_scores_var.get():
            check_int(name='SHAP TARGET PRESENT', value=self.shap_present.entry_get, min_value=1)
            check_int(name='SHAP TARGET ABSENT', value=self.shap_absent.entry_get, min_value=1)


    def __get_variables(self):
        self.algorithm = self.machine_model_dropdown.getChoices()
        self.behavior_name = self.behavior_name_dropdown.getChoices()
        self.n_estimators = self.estimators_entrybox.entry_get
        self.max_features = self.max_features_dropdown.getChoices()
        self.criterion = self.criterion_dropdown.getChoices()
        self.test_size = self.train_test_size_dropdown.getChoices()
        self.train_test_type = self.train_test_type_dropdown.getChoices()
        self.min_sample_leaf = self.min_sample_leaf_eb.entry_get
        self.max_depth = self.max_depth_dropdown.getChoices()
        self.under_sample_setting = self.undersample_settings_dropdown.getChoices()
        self.under_sample_ratio = 'NaN'
        if self.undersample_settings_dropdown.getChoices() != 'None':
            self.under_sample_ratio = self.under_sample_ratio_entrybox.entry_get
        self.over_sample_setting = self.oversample_settings_dropdown.getChoices()
        self.over_sample_ratio = 'NaN'
        if self.oversample_settings_dropdown.getChoices() != 'None':
            self.over_sample_ratio = self.over_sample_ratio_entrybox.entry_get
        self.class_weight_method = self.class_weights_dropdown.getChoices()
        self.class_custom_weights = {}
        if self.class_weight_method == 'custom':
            self.class_custom_weights[0] = self.weight_absent.getChoices()
            self.class_custom_weights[1] = self.weight_present.getChoices()

        self.meta_info_file = self.create_meta_data_file_var.get()
        self.example_graphviz = self.create_example_decision_tree_graphviz_var.get()
        self.example_dtreeviz = self.create_example_decision_tree_dtreeviz_var.get()
        self.clf_report = self.create_clf_report_var.get()
        self.clf_importance_bars = self.create_clf_importance_bars_var.get()
        self.clf_importance_bars_n = 0
        if self.clf_importance_bars:
            self.clf_importance_bars_n = int(self.n_features_bars_entry_dropdown.getChoices())
        self.permutation_importances = self.feature_permutation_importance_var.get()
        self.pr_curve = self.create_pr_curve_var.get()
        self.shap_scores_absent = 0
        self.shap_scores_present = 0
        self.shap_save_it = 'ALL FRAMES'
        self.shap_multiprocess = False
        self.shap_scores = self.calc_shap_scores_var.get()
        if self.shap_scores:
            self.shap_scores_absent = self.shap_absent.entry_get
            self.shap_scores_present = self.shap_present.entry_get
            self.shap_save_it = self.shap_save_it_dropdown.getChoices()
            self.shap_multiprocess = self.shap_multiprocess_dropdown.getChoices()
        self.learning_curve = self.learning_curve_var.get()
        self.partial_dependency = self.partial_dependency_var.get()
        self.learning_curve_k_split = 0
        self.learning_curve_data_split = 0
        if self.learning_curve:
            self.learning_curve_k_split = int(self.learning_curve_k_splits_dropdown.getChoices())
            self.learning_curve_data_split = int(self.learning_curve_data_splits_dropdown.getChoices())
        self.create_train_test_log = self.create_train_test_log_var.get()

    def find_meta_file_cnt(self):
        self.meta_file_cnt = 0
        self.total_meta_files = find_files_of_filetypes_in_directory(directory=self.configs_meta_dir, extensions=['.csv'], raise_warning=False)
        for f in os.listdir(self.configs_meta_dir):
            if f.__contains__('_meta') and f.__contains__(str(self.behavior_name)):
                self.meta_file_cnt += 1

    def change_shap_cadence_options(self, x):
        if x == 'True':
            self.shap_save_it_dropdown.setChoices('ALL FRAMES')
            self.shap_save_it_dropdown.disable()
        else:
            self.shap_save_it_dropdown.enable()

    def save_global(self):
        self.__checks()
        self.__get_variables()
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.MODEL_TO_RUN.value, self.algorithm)
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.RF_ESTIMATORS.value, str(self.n_estimators))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.RF_MAX_FEATURES.value, str(self.max_features))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.RF_CRITERION.value, self.criterion)
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.TT_SIZE.value, str(self.test_size))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.TRAIN_TEST_SPLIT_TYPE.value, str(self.train_test_type))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.MIN_LEAF.value, str(self.min_sample_leaf))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.UNDERSAMPLE_RATIO.value, str(self.under_sample_ratio))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.UNDERSAMPLE_SETTING.value, str(self.under_sample_setting))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.OVERSAMPLE_RATIO.value, str(self.over_sample_ratio))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.OVERSAMPLE_SETTING.value, str(self.over_sample_setting))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.CLASSIFIER.value, self.behavior_name)
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.RF_METADATA.value, str(self.meta_info_file))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.EX_DECISION_TREE.value, str(self.example_graphviz))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.CLF_REPORT.value, str(self.clf_report))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.IMPORTANCE_LOG.value, str(self.clf_importance_bars))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.IMPORTANCE_BAR_CHART.value, str(self.clf_importance_bars))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.N_FEATURE_IMPORTANCE_BARS.value, str(self.clf_importance_bars_n))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.PERMUTATION_IMPORTANCE.value, str(self.permutation_importances))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.LEARNING_CURVE.value, str(self.learning_curve))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.PRECISION_RECALL.value, str(self.pr_curve))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.LEARNING_CURVE_K_SPLITS.value, str(self.learning_curve_k_split))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.LEARNING_CURVE_DATA_SPLITS.value, str(self.learning_curve_data_split))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.EX_DECISION_TREE_FANCY.value, str(self.example_dtreeviz))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.SHAP_SCORES.value, str(self.shap_scores))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.SHAP_PRESENT.value, str(self.shap_scores_present))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.SHAP_ABSENT.value, str(self.shap_scores_absent))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.SHAP_SAVE_ITERATION.value, str(self.shap_save_it))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.SHAP_MULTIPROCESS.value, str(self.shap_multiprocess))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.PARTIAL_DEPENDENCY.value, str(self.partial_dependency))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.CLASS_WEIGHTS.value, str(self.class_weight_method))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.CLASS_CUSTOM_WEIGHTS.value, str(self.class_custom_weights))
        self.config.set(ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, MLParamKeys.SAVE_TRAIN_TEST_FRM_IDX.value, str(self.create_train_test_log))

        with open(self.config_path, 'w') as f:
            self.config.write(f)

        stdout_success(msg='Global model settings saved in the project_folder/project_config.ini', source=self.__class__.__name__)

    def save_config(self):
        self.__checks()
        self.__get_variables()

        meta = {MLParamKeys.RF_ESTIMATORS.value: self.n_estimators,
                MLParamKeys.RF_MAX_FEATURES.value: self.max_features,
                MLParamKeys.RF_CRITERION.value: self.criterion,
                MLParamKeys.TT_SIZE.value: self.test_size,
                MLParamKeys.TRAIN_TEST_SPLIT_TYPE.value: self.train_test_type,
                MLParamKeys.MIN_LEAF.value: self.min_sample_leaf,
                MLParamKeys.UNDERSAMPLE_RATIO.value: self.under_sample_ratio,
                MLParamKeys.UNDERSAMPLE_SETTING.value: self.under_sample_setting,
                MLParamKeys.OVERSAMPLE_RATIO.value: self.over_sample_ratio,
                MLParamKeys.OVERSAMPLE_SETTING.value: self.over_sample_setting,
                MLParamKeys.RF_METADATA.value: self.meta_info_file,
                MLParamKeys.EX_DECISION_TREE.value: self.example_graphviz,
                MLParamKeys.CLF_REPORT.value:self.clf_report,
                MLParamKeys.IMPORTANCE_LOG.value: self.clf_importance_bars,
                MLParamKeys.IMPORTANCE_BAR_CHART.value: self.clf_importance_bars,
                MLParamKeys.IMPORTANCE_BARS_N.value: self.clf_importance_bars_n,
                MLParamKeys.PERMUTATION_IMPORTANCE.value: self.permutation_importances,
                MLParamKeys.LEARNING_CURVE.value: self.learning_curve,
                MLParamKeys.PRECISION_RECALL.value: self.pr_curve,
                MLParamKeys.LEARNING_CURVE_K_SPLITS.value: self.learning_curve_k_split,
                MLParamKeys.LEARNING_CURVE_DATA_SPLITS.value: self.learning_curve_data_split,
                MLParamKeys.SHAP_SCORES.value: self.shap_scores,
                MLParamKeys.SHAP_PRESENT.value: self.shap_scores_present,
                MLParamKeys.SHAP_ABSENT.value: self.shap_scores_absent,
                MLParamKeys.SHAP_SAVE_ITERATION.value: self.shap_save_it,
                MLParamKeys.SHAP_MULTIPROCESS.value: self.shap_multiprocess,
                MLParamKeys.PARTIAL_DEPENDENCY.value: self.partial_dependency,
                MLParamKeys.CLASS_WEIGHTS.value: self.class_weight_method,
                MLParamKeys.CLASS_CUSTOM_WEIGHTS.value: str(self.class_custom_weights),
                MLParamKeys.SAVE_TRAIN_TEST_FRM_IDX.value: self.create_train_test_log,
                MLParamKeys.RF_MAX_DEPTH.value: self.max_depth}

        meta_df = pd.DataFrame(meta, index=[0])
        meta_df.insert(0, MLParamKeys.CLASSIFIER.value, self.behavior_name)
        self.find_meta_file_cnt()
        file_name = f'{self.behavior_name}_meta_{self.meta_file_cnt}.csv'
        save_path = os.path.join(self.configs_meta_dir, file_name)
        meta_df.to_csv(save_path, index=FALSE)
        stdout_success(msg=f'Hyper-parameter config saved ({str(len(self.total_meta_files)+1)} saved in project_folder/configs folder).', source=self.__class__.__name__)

    def clear_cache(self):
        self.behavior_name = self.behavior_name_dropdown.getChoices()
        self.find_meta_file_cnt()
        if len(self.total_meta_files) == 0:
            raise NoFilesFoundError(msg=f'No config meta files found to delete inside {self.config_path} directory', source=self.__class__.__name__)
        for file_path in self.total_meta_files:
            os.remove(os.path.join(file_path))
            print(f'Deleted hyperparameters config {get_fn_ext(file_path)[1]} ...')
        stdout_trash(msg=f'{str(len(self.total_meta_files))} config files deleted', source=self.__class__.__name__)

    def check_meta_data_integrity(self):
        self.meta = {k.lower(): v for k, v in self.meta.items()}
        for i in MLParamKeys:
            if i not in self.meta.keys():
                stdout_warning(msg=f'The file does not contain an expected entry for {i} parameter')
                self.meta[i] = None
            else:
                if type(self.meta[i]) == str:
                    if self.meta[i].lower().strip() == 'yes':
                        self.meta[i] = True

    def load_config(self):
        config_file_path = self.select_config_file.file_path
        _, config_name, _ = get_fn_ext(config_file_path)
        check_file_exist_and_readable(file_path=config_file_path)
        try:
            meta_df = pd.read_csv(config_file_path, index_col=False)
        except pd.errors.ParserError:
            raise InvalidHyperparametersFileError(msg=f'SIMBA ERROR: {config_name} is not a valid SimBA meta hyper-parameters file.', source=self.__class__.__name__)
        self.meta = {}
        for m in meta_df.columns:
            self.meta[m] = meta_df[m][0]
        self.check_meta_data_integrity()
        self.behavior_name_dropdown.setChoices(self.meta[MLParamKeys.CLASSIFIER.value])
        self.estimators_entrybox.entry_set(val=self.meta[MLParamKeys.RF_ESTIMATORS.value])
        self.max_features_dropdown.setChoices(self.meta[MLParamKeys.RF_MAX_FEATURES.value])
        self.criterion_dropdown.setChoices(self.meta[MLParamKeys.RF_CRITERION.value])
        self.train_test_size_dropdown.setChoices(self.meta[MLParamKeys.TT_SIZE.value])
        self.min_sample_leaf_eb.entry_set(val=self.meta[MLParamKeys.MIN_LEAF.value])
        self.undersample_settings_dropdown.setChoices(self.meta[MLParamKeys.UNDERSAMPLE_SETTING.value])
        if self.undersample_settings_dropdown.getChoices() != 'None':
            self.under_sample_ratio_entrybox.entry_set(val=self.meta[MLParamKeys.UNDERSAMPLE_RATIO.value])
            self.under_sample_ratio_entrybox.set_state(NORMAL)
        else:
            self.under_sample_ratio_entrybox.set_state(DISABLED)
        self.oversample_settings_dropdown.setChoices(self.meta[MLParamKeys.OVERSAMPLE_SETTING.value])
        if self.oversample_settings_dropdown.getChoices() != 'None':
            self.over_sample_ratio_entrybox.entry_set(val=self.meta[MLParamKeys.OVERSAMPLE_RATIO.value])
            self.over_sample_ratio_entrybox.set_state(NORMAL)
        else:
            self.over_sample_ratio_entrybox.set_state(DISABLED)

        if self.meta[MLParamKeys.RF_METADATA.value]:
            self.create_meta_data_file_var.set(value=True)
        else:
            self.create_meta_data_file_var.set(value=False)
        if self.meta[MLParamKeys.EX_DECISION_TREE.value]:
            self.create_example_decision_tree_graphviz_var.set(value=True)
        else:
            self.create_example_decision_tree_graphviz_var.set(value=False)
        if self.meta[MLParamKeys.CLF_REPORT.value]:
            self.create_clf_report_var.set(value=True)
        else:
            self.create_clf_report_var.set(value=False)
        if self.meta[MLParamKeys.IMPORTANCE_LOG.value] or self.meta[MLParamKeys.IMPORTANCE_BAR_CHART.value]:
            self.create_clf_importance_bars_var.set(value=True)
            self.n_features_bars_entry_dropdown.enable()
            self.n_features_bars_entry_dropdown.setChoices(choice=self.meta[MLParamKeys.N_FEATURE_IMPORTANCE_BARS.value])
        else:
            self.create_clf_importance_bars_var.set(value=False)
            self.n_features_bars_entry_dropdown.disable()

        if self.meta[MLParamKeys.PERMUTATION_IMPORTANCE.value]:
            self.feature_permutation_importance_var.set(value=True)

        if self.meta[MLParamKeys.LEARNING_CURVE.value]:
            self.learning_curve_var.set(value=True)
            self.learning_curve_k_splits_dropdown.enable()
            self.learning_curve_data_splits_dropdown.enable()
            self.learning_curve_k_splits_dropdown.setChoices(choice=self.meta[MLParamKeys.LEARNING_CURVE_K_SPLITS.value])
            self.learning_curve_data_splits_dropdown.setChoices(choice=self.meta[MLParamKeys.LEARNING_CURVE_DATA_SPLITS.value])
        else:
            self.learning_curve_var.set(value=False)
            self.learning_curve_k_splits_dropdown.disable()
            self.learning_curve_data_splits_dropdown.disable()

        if self.meta[MLParamKeys.SHAP_SCORES.value]:
            self.calc_shap_scores_var.set(value=True)
            self.shap_present.set_state(NORMAL)
            self.shap_absent.set_state(NORMAL)
            self.shap_absent.set_state(NORMAL)
            self.shap_save_it_dropdown.enable()
            self.shap_multiprocess_dropdown.enable()
            self.shap_present.entry_set(val=self.meta[MLParamKeys.SHAP_PRESENT.value])
            self.shap_absent.entry_set(val=self.meta[MLParamKeys.SHAP_ABSENT.value])
            if MLParamKeys.SHAP_SAVE_ITERATION.value in self.meta.keys():
                self.shap_save_it_dropdown.setChoices(self.meta[MLParamKeys.SHAP_SAVE_ITERATION.value])
            else:
                self.shap_save_it_dropdown.setChoices('ALL FRAMES')
            if MLParamKeys.SHAP_MULTIPROCESS.value in self.meta.keys():
                self.shap_multiprocess_dropdown.setChoices(self.meta[MLParamKeys.SHAP_MULTIPROCESS.value])
        else:
            self.calc_shap_scores_var.set(value=False)
            self.shap_present.set_state(DISABLED)
            self.shap_absent.set_state(DISABLED)
            self.shap_save_it_dropdown.enable()
            self.shap_multiprocess_dropdown.disable()

        if MLParamKeys.TRAIN_TEST_SPLIT_TYPE.value in self.meta.keys():
            self.train_test_type_dropdown.setChoices(self.meta[MLParamKeys.TRAIN_TEST_SPLIT_TYPE.value])
        else:
            self.train_test_type_dropdown.setChoices(Options.TRAIN_TEST_SPLIT.value[0])
        if MLParamKeys.SHAP_SAVE_ITERATION.value in self.meta.keys():
            self.shap_save_it_dropdown.setChoices(self.meta[MLParamKeys.SHAP_SAVE_ITERATION.value])
        else:
            self.shap_save_it_dropdown.setChoices('None')
        if MLParamKeys.SAVE_TRAIN_TEST_FRM_IDX.value in self.meta.keys():
            if self.meta[MLParamKeys.SAVE_TRAIN_TEST_FRM_IDX.value]:
                self.create_train_test_log_var.set(value=str(self.meta[MLParamKeys.SAVE_TRAIN_TEST_FRM_IDX.value]))
        else:
            self.create_train_test_log_var.set(value='False')
        if MLParamKeys.PARTIAL_DEPENDENCY.value in self.meta.keys():
            if self.meta[MLParamKeys.PARTIAL_DEPENDENCY.value] in Options.RUN_OPTIONS_FLAGS.value:
                self.partial_dependency_var.set(value=True)
        if MLParamKeys.CLASS_WEIGHTS.value in self.meta.keys():
            if self.meta[MLParamKeys.CLASS_WEIGHTS.value] not in Options.CLASS_WEIGHT_OPTIONS.value:
                self.meta[MLParamKeys.CLASS_WEIGHTS.value] = 'None'
            self.class_weights_dropdown.setChoices(self.meta[MLParamKeys.CLASS_WEIGHTS.value])
            if self.meta['class_weights'] == 'custom':
                self.create_class_weight_table()
                weights = ast.literal_eval(self.meta[MLParamKeys.CLASS_CUSTOM_WEIGHTS.value])
                self.weight_present.setChoices(weights[1])
                self.weight_absent.setChoices(weights[0])
        else:
            self.class_weights_dropdown.setChoices('None')
            self.create_class_weight_table()

        if MLParamKeys.RF_MAX_DEPTH.value in self.meta.keys():
            self.max_depth_dropdown.setChoices(self.meta[MLParamKeys.CLASS_CUSTOM_WEIGHTS.value])

        print(f'Loaded parameters from config {config_name}...')

#_ = MachineModelSettingsPopUp(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini')