__author__ = "Simon Nilsson"

import os
import numpy as np
import pandas as pd
from sklearn.inspection import partial_dependence
from simba.rw_dfs import read_df
from simba.misc_tools import get_fn_ext
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import SMOTE
from sklearn.inspection import permutation_importance
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import precision_recall_curve
from sklearn.ensemble import RandomForestClassifier
from copy import deepcopy
from sklearn.tree import export_graphviz
from subprocess import call
from yellowbrick.classifier import ClassificationReport
import shap
from tabulate import tabulate
from simba.plotting.shap_agg_stats_visualizer import ShapAggregateStatisticsVisualizer
from simba.read_config_unit_tests import (check_int, check_str, check_if_dir_exists,
                                          check_float,
                                          read_config_entry)
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from itertools import repeat
from simba.misc_tools import (create_single_color_lst,
                              SimbaTimer,
                              detect_bouts,
                              find_core_cnt)
from simba.utils.errors import (ColumnNotFoundError,
                                FaultyTrainingSetError,
                                MissingColumnsError,
                                NoDataError,
                                SamplingError,
                                CorruptedFileError,
                                FeatureNumberMismatchError,
                                ClassifierInferenceError,
                                CountError)
from simba.utils.warnings import (NotEnoughDataWarning,
                                  NoModuleWarning,
                                  MissingUserInputWarning)
from simba.utils.printing import stdout_success
from simba.utils.lookups import get_meta_data_file_headers
import configparser
import platform
from sklearn.utils import parallel_backend
import pickle
from dtreeviz.trees import tree, dtreeviz
import matplotlib.pyplot as plt
from simba.enums import ReadConfig, Dtypes, MetaKeys
import multiprocessing
plt.switch_backend('agg')

def read_all_files_in_folder(file_paths: list,
                             file_type: str,
                             classifier_names=None):
    """

    Helper function to read in all data files in a folder to a single pd.DataFrame for downstream ML algorithm.
    Asserts that all classifiers have annotation fields present in concatenated dataframes.

    Parameters
    ----------
    file_paths: list
        List of file paths representing files to be read in.
    file_type: str
        Type of files in ``file_paths``. OPTIONS: csv or parquet.
    classifier_names: list or None
        List of classifier names representing fields of human annotations. If not None, then assert that classifier names
        are present in each data file.

    Returns
    -------
    df_concat: pd.DataFrame

    """

    timer = SimbaTimer()
    timer.start_timer()
    df_concat = pd.DataFrame()
    for file_cnt, file in enumerate(file_paths):
        print(f'Reading in file {str(file_cnt+1)}/{str(len(file_paths))}...')
        _, vid_name, _ = get_fn_ext(file)
        df = read_df(file, file_type).dropna(axis=0, how='all').fillna(0).astype(np.float16)
        if classifier_names != None:
            for clf_name in classifier_names:
                if not clf_name in df.columns:
                    raise MissingColumnsError(msg=f'Data for video {vid_name} does not contain any annotations for behavior {clf_name}. Delete classifier {clf_name} from the SimBA project, or add annotations for behavior {clf_name} to the video {vid_name}')
                else:
                    df_concat = pd.concat([df_concat, df], axis=0).astype(np.float16)
        else:
            df_concat = pd.concat([df_concat, df], axis=0).astype(np.float16)
    try:
        df_concat = df_concat.set_index('scorer').astype(np.float16)
    except KeyError:
        pass
    if len(df_concat) == 0:
        raise NoDataError(msg='SimBA found 0 annotated frames in the project_folder/csv/targets_inserted directory')
    df_concat = df_concat.loc[:, ~df_concat.columns.str.contains('^Unnamed')].astype(np.float16)
    timer.stop_timer()
    data_size = df_concat.memory_usage(index=True).sum()
    print(f'Dataset size: {round(data_size / 1000000, 6)}MB / {round(data_size / 1000000000, 6)}GB')
    print('{} file(s) read (elapsed time: {}s) ...'.format(str(len(file_paths)), timer.elapsed_time_str))
    return df_concat.reset_index(drop=True).astype(np.float16)


def read_in_all_model_names_to_remove(config, model_cnt, clf_name):
    """
    Helper to find all field names that contain annotations but are not the target.

    Parameters
    ----------
    config: Configparser,
        Configparser object holding data from the project_config.ini
    model_cnt: int,
        Number of classifiers in the SimBA project.
    clf_name
        Name of the classifier.

    Returns
    -------
    annotation_cols_to_remove: list
    """

    annotation_cols_to_remove = []
    for model_no in range(model_cnt):
        model_name = config.get(ReadConfig.SML_SETTINGS.value, 'target_name_' + str(model_no+1))
        if model_name != clf_name:
            annotation_cols_to_remove.append(model_name)
    return annotation_cols_to_remove

def delete_other_annotation_columns(df: pd.DataFrame,
                                    annotations_lst: list):
    """
    Helper to delete fields that contain annotations which are not the target.

    Parameters
    ----------
    df: pd.DataFrame
        pandas Dataframe holding features and annotations.
    annotations_lst: list
        Column fields to be removed from df

    Returns
    -------
    df: pd.DataFrame
    """

    for a_col in annotations_lst:
        df = df.drop([a_col], axis=1)
    return df

def split_df_to_x_y(df: pd.DataFrame,
                    clf_name: str):
    """
    Helper to split dataframe into features and target.

    Parameters
    ----------
    df: pd.DataFrame
        pandas Dataframe holding features and annotations.
    clf_name: str
        Name of target.

    Returns
    -------
    df: pd.DataFrame
    y: pd.DataFrame
    """

    df = deepcopy(df)
    y = df.pop(clf_name)
    return df, y

def random_undersampler(x_train: np.array,
                        y_train: np.array,
                        sample_ratio: float):
    """
    Helper to perform random undersampling of behavior-absent frames in a dataframe.

    Parameters
    ----------
    x_train: pd.DataFrame
        Features in train set
    y_train: pd.DataFrame
        Target in train set
    sample_ratio: float,
        Ratio of behavior-absent frames to keep relative to the behavior-present frames. E.g., ``1.0`` returns an equal
        count of behavior-absent and behavior-present frames. ``2.0`` returns twice as many behavior-absent frames as
        and behavior-present frames.

    Returns
    -------
    df: pd.DataFrame
    """

    print(f'Performing under-sampling at sample ratio {str(sample_ratio)}...')
    data_df = pd.concat([x_train, y_train], axis=1)
    present_df, absent_df = data_df[data_df[y_train.name] == 1], data_df[data_df[y_train.name] == 0]
    ratio_n = int(len(present_df) * sample_ratio)
    if len(absent_df) < ratio_n:
        raise SamplingError(msg=f'SIMBA UNDER SAMPLING ERROR: The under-sample ratio of {str(sample_ratio)} in classifier {y_train.name} demands {str(ratio_n)} behavior-absent annotations. This is more than the number of behavior-absent annotations in the entire dataset {str(len(absent_df))}. Please annotate more images or decrease the under-sample ratio.')
    data_df = pd.concat([present_df, absent_df.sample(n=ratio_n, replace=False)], axis=0)
    return split_df_to_x_y(data_df, y_train.name)

def smoteen_oversampler(x_train: pd.DataFrame,
                        y_train: pd.DataFrame,
                        sample_ratio: float):

    """
    Helper to perform smoteen oversampling of behavior-present frames in a dataframe

    Parameters
    ----------
    x_train: pd.DataFrame or array
        pandas Dataframe holding features and annotations.
    y_train: pd.DataFrame or array
        List of column fields to be removed from df
    sample_ratio:
        New behavior-present frames.

    Returns
    -------
    x_train: array
    y_train: array

    """

    print('Performing SMOTEEN oversampling...')
    smt = SMOTEENN(sampling_strategy=sample_ratio)
    return smt.fit_sample(x_train, y_train)

def smote_oversampler(x_train, y_train, sample_ratio):
    """
    Helper to perform smote oversampling of behavior-present frames in a dataframe

    Parameters
    ----------
    x_train: pd.DataFrame or np.array
        pandas Dataframe holding features and annotations.
    y_train: pd.DataFrame or np.array
        List of column fields to be removed from df
    sample_ratio:
        New behavior-present frames.

    Returns
    -------
    x_train: np.array
    y_train: np.array

    """
    print('Performing SMOTE oversampling...')
    smt = SMOTE(sampling_strategy=sample_ratio)
    return smt.fit_sample(x_train, y_train)

def calc_permutation_importance(x_test: np.array,
                                y_test: np.array,
                                clf: RandomForestClassifier,
                                feature_names: list,
                                clf_name: str,
                                save_dir: str,
                                save_file_no=None):
    """
    Helper to calculate feature permutation importance scores.

    Parameters
    ----------
    x_test: np.array,
        Array holding feature test data
    y_test: np.array
        Array holding target test data
    clf: object
        sklearn RandomForestClassifier object
    feature_names: list,
        list of feature names
    clf_name: str,
        Name of classifier
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None

    """
    print('Calculating feature permutation importances...')
    timer = SimbaTimer()
    timer.start_timer()
    p_importances = permutation_importance(clf, x_test, y_test, n_repeats=10, random_state=0)
    df = pd.DataFrame(np.column_stack([feature_names, p_importances.importances_mean, p_importances.importances_std]), columns=['FEATURE_NAME', 'FEATURE_IMPORTANCE_MEAN', 'FEATURE_IMPORTANCE_STDEV'])
    df = df.sort_values(by=['FEATURE_IMPORTANCE_MEAN'], ascending=False)
    if save_file_no != None:
        save_file_path = os.path.join(save_dir, clf_name + '_' + str(save_file_no+1) +'_permutations_importances.csv')
    else:
        save_file_path = os.path.join(save_dir, clf_name + '_permutations_importances.csv')
    df.to_csv(save_file_path, index=False)
    timer.stop_timer()
    print('Permutation importance calculation complete (elapsed time: {}s) ...'.format(timer.elapsed_time_str))

def calc_learning_curve(x_y_df: pd.DataFrame,
                  clf_name: str,
                  shuffle_splits: int,
                  dataset_splits: int,
                  tt_size: float,
                  rf_clf: RandomForestClassifier,
                  save_dir: str,
                  save_file_no=None):
    """
    Helper to compute random forest learning curves with cross-validation.

    Parameters
    ----------
    x_y_df: pd.DataFrame
        Pandas dataframe holding features and targets.
    clf_name: str,
        Name of the classifier
    shuffle_splits: int
        Number of cross-validation datasets at each data split.
    dataset_splits: int
        Number of data splits.
    tt_size: float
        dataset test size.
    rf_clf: RandomForestClassifier
        sklearn RandomForestClassifier object.
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None

    """

    print('Calculating learning curves...')
    timer = SimbaTimer()
    timer.start_timer()
    x_df, y_df = split_df_to_x_y(x_y_df, clf_name)
    cv = ShuffleSplit(n_splits=shuffle_splits, test_size=tt_size)
    if platform.system() == "Darwin":
        with parallel_backend("threading", n_jobs=-2):
            train_sizes, train_scores, test_scores = learning_curve(estimator=rf_clf, X=x_df, y=y_df, cv=cv,scoring='f1', shuffle=False, verbose=0, train_sizes=np.linspace(0.01, 1.0, dataset_splits), error_score='raise')
    else:
        train_sizes, train_scores, test_scores = learning_curve(estimator=rf_clf, X=x_df, y=y_df, cv=cv, scoring='f1', shuffle=False, n_jobs=-1, verbose=0, train_sizes=np.linspace(0.01, 1.0, dataset_splits), error_score='raise')
    results_df = pd.DataFrame()
    results_df['FRACTION TRAIN SIZE'] = np.linspace(0.01, 1.0, dataset_splits)
    results_df['TRAIN_MEAN_F1'] = np.mean(train_scores, axis=1)
    results_df['TEST_MEAN_F1'] = np.mean(test_scores, axis=1)
    results_df['TRAIN_STDEV_F1'] = np.std(train_scores, axis=1)
    results_df['TEST_STDEV_F1'] = np.std(test_scores, axis=1)
    if save_file_no != None:
        save_file_path = os.path.join(save_dir, clf_name + '_' + str(save_file_no+1) +'_learning_curve.csv')
    else:
        save_file_path = os.path.join(save_dir, clf_name + '_learning_curve.csv')
    results_df.to_csv(save_file_path, index=False)
    timer.stop_timer()
    print('Learning curve calculation complete (elapsed time: {}s) ...'.format(timer.elapsed_time_str))


def calc_pr_curve(rf_clf,
                  x_df,
                  y_df,
                  clf_name,
                  save_dir,
                  save_file_no=None):
    """
    Helper to compute random forest precision-recall curve.

    Parameters
    ----------
    rf_clf: RandomForestClassifier
        sklearn RandomForestClassifier object.
    x_df: pd.DataFrame
        Pandas dataframe holding test features.
    y_df: pd.DataFrame
        Pandas dataframe holding test target.
    clf_name: str
        Classifier name.
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None

    """

    print('Calculating PR curves...')
    timer = SimbaTimer()
    timer.start_timer()
    p = rf_clf.predict_proba(x_df)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_df, p, pos_label=1)
    pr_df = pd.DataFrame()
    pr_df['PRECISION'] = precision
    pr_df['RECALL'] = recall
    pr_df['F1'] = 2 * pr_df['RECALL'] * pr_df['PRECISION'] / (pr_df['RECALL'] + pr_df['PRECISION'])
    thresholds = list(thresholds)
    thresholds.insert(0, 0.00)
    pr_df['DISCRIMINATION THRESHOLDS'] = thresholds
    if save_file_no != None:
        save_file_path = os.path.join(save_dir, clf_name + '_' + str(save_file_no+1) +'_pr_curve.csv')
    else:
        save_file_path = os.path.join(save_dir, clf_name + '_pr_curve.csv')
    pr_df.to_csv(save_file_path, index=False)
    timer.stop_timer()
    print('Precision-recall curve calculation complete (elapsed time: {}s) ...'.format(timer.elapsed_time_str))


def create_example_dt(rf_clf: RandomForestClassifier,
                      clf_name: str,
                      feature_names: list,
                      class_names: list,
                      save_dir: str,
                      save_file_no=None):
    """
    Helper to produce visualization of random forest decision tree.

    Parameters
    ----------
    rf_clf: RandomForestClassifier
        sklearn RandomForestClassifier object.
    clf_name: str
        Classifier name.
    feature_names: list
        List of feature names.
    class_names
        List of classes. E.g., ['Attack absent', 'Attack present']
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None
    """

    print('Visualizing example decision tree using graphviz...')
    estimator = rf_clf.estimators_[3]
    if save_file_no != None:
        dot_name = os.path.join(save_dir, str(clf_name) + '_' + str(save_file_no) + '_tree.dot')
        file_name = os.path.join(save_dir, str(clf_name) + '_' + str(save_file_no) +'_tree.pdf')
    else:
        dot_name = os.path.join(save_dir, str(clf_name) + '_tree.dot')
        file_name = os.path.join(save_dir, str(clf_name) + '_tree.pdf')
    export_graphviz(estimator, out_file=dot_name, filled=True, rounded=True, special_characters=False, impurity=False, class_names=class_names, feature_names=feature_names)
    command = ('dot ' + str(dot_name) + ' -T pdf -o ' + str(file_name) + ' -Gdpi=600')
    call(command, shell=True)


def create_clf_report(rf_clf,
                      x_df,
                      y_df,
                      class_names,
                      save_dir,
                      save_file_no=None):
    """
    Helper to create classifier truth table report.

    Parameters
    ----------
    rf_clf: RandomForestClassifier
        sklearn RandomForestClassifier object.
    x_df: pd.DataFrame
        Pandas dataframe holding test features.
    y_df: pd.DataFrame
        Pandas dataframe holding test target.
    class_names: list
        List of classes. E.g., ['Attack absent', 'Attack present']
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None
    """

    print('Creating classification report visualization...')
    try:
        visualizer = ClassificationReport(rf_clf, classes=class_names, support=True)
        visualizer.score(x_df, y_df)
        if save_file_no != None:
            save_path = os.path.join(save_dir, class_names[1] + '_' + str(save_file_no) + '_classification_report.png')
        else:
            save_path = os.path.join(save_dir, class_names[1] + '_classification_report.png')
        visualizer.poof(outpath=save_path, clear_figure=True)
    except KeyError as e:
        NotEnoughDataWarning(msg=f'Not enough data to create classification report: {class_names[1]}')

def create_x_importance_log(rf_clf: RandomForestClassifier,
                            x_names: list,
                            clf_name: str,
                            save_dir: str,
                            save_file_no=None):
    """
    Helper to save gini or entropy based feature importance scores.

    Parameters
    ----------
    rf_clf: RandomForestClassifier
        sklearn RandomForestClassifier object.
    x_names: list
        Names of features.
    clf_name: str
        Name of classifier.
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None

    """

    print('Creating feature importance log...')
    importances = list(rf_clf.feature_importances_)
    feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(x_names, importances)]
    df = pd.DataFrame(feature_importances, columns=['FEATURE', 'FEATURE_IMPORTANCE']).sort_values(by=['FEATURE_IMPORTANCE'], ascending=False)
    if save_file_no != None:
        save_file_path = os.path.join(save_dir, clf_name + '_' + str(save_file_no) + '_feature_importance_log.csv')
    else:
        save_file_path = os.path.join(save_dir, clf_name + '_feature_importance_log.csv')
    df.to_csv(save_file_path, index=False)

def create_x_importance_bar_chart(rf_clf: RandomForestClassifier,
                                  x_names: list,
                                  clf_name: str,
                                  save_dir: str,
                                  n_bars: int,
                                  save_file_no=None):
    """
    Helper to create a bar chart displaying the top N gini or entropy feature importance scores.

    Parameters
    ----------
    rf_clf: RandomForestClassifier
        sklearn RandomForestClassifier object.
    x_names: list
        Names of features.
    clf_name: str
        Name of classifier.
    save_dir: str
        Directory where to save output in csv file format.
    n_bars: int
        Number of bars in the plot.
    save_file_no: str or None
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None
    """

    print('Creating feature importance bar chart...')
    create_x_importance_log(rf_clf, x_names, clf_name, save_dir)
    importances_df = pd.read_csv(os.path.join(save_dir, clf_name + '_feature_importance_log.csv'))
    importances_head = importances_df.head(n_bars)
    colors = create_single_color_lst(pallete_name='hot',increments=n_bars, as_rgb_ratio=True)
    colors = [x[::-1] for x in colors]
    ax = importances_head.plot.bar(x='FEATURE', y='FEATURE_IMPORTANCE', legend=False, rot=90, fontsize=6, color=colors)
    plt.ylabel("Feature importances' (mean decrease impurity)", fontsize=6)
    plt.tight_layout()
    if save_file_no != None:
        save_file_path = os.path.join(save_dir, clf_name + '_' + str(save_file_no) + '_feature_importance_bar_graph.png')
    else:
        save_file_path = os.path.join(save_dir, clf_name + '_feature_importance_bar_graph.png')
    plt.savefig(save_file_path, dpi=600)
    plt.close('all')

def dviz_classification_visualization(x_train: np.array,
                                      y_train: np.array,
                                      clf_name: str,
                                      class_names: list,
                                      save_dir: str):
    """
    Helper to create visualization of example decision tree.

    Parameters
    ----------
    x_train: np.array
        Array with training features
    y_train: np.array
        Array with training targets
    clf_name: str
        Name of classifier
    class_names:
        List of class names. E.g., ['Attack absent', 'Attack present']
    save_dir: str
        Directory where to save output in svg file format.

    Returns
    -------
    None
    """

    clf = tree.DecisionTreeClassifier(max_depth=5, random_state=666)
    clf.fit(x_train, y_train)
    try:
        svg_tree = dtreeviz(clf, x_train, y_train, target_name=clf_name, feature_names=x_train.columns, orientation="TD", class_names=class_names, fancy=True, histtype='strip', X=None, label_fontsize=12, ticks_fontsize=8, fontname="Arial")
        save_path = os.path.join(save_dir, clf_name + '_fancy_decision_tree_example.svg')
        svg_tree.save(save_path)
    except:
        NoModuleWarning(msg='Skipping dtreeviz example decision tree visualization. Make sure "graphviz" is installed.')


def create_shap_log(ini_file_path: str,
                    rf_clf: RandomForestClassifier,
                    x_df: pd.DataFrame,
                    y_df: pd.DataFrame,
                    x_names: list,
                    clf_name: str,
                    cnt_present: int,
                    cnt_absent: int,
                    save_path: str,
                    save_it: int=100,
                    save_file_no=None):

    """
    Helper to compute SHAP values.

    Parameters
    ----------
    ini_file_path: str
        Path to the SimBA project_config.ini
    rf_clf: RandomForestClassifier
        sklearn random forest classifier
    x_df: pd.DataFrame
        Pandas dataframe holding test features.
    y_df: pd.DataFrame
        Pandas dataframe holding test target.
    x_names: list
        Feature names.
    clf_name:
        Classifier name.
    cnt_present: int
        Number of behavior-present frames to calculate SHAP values for.
    cnt_absent: int
        Number of behavior-absent frames to calculate SHAP values for.
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------

    """

    print('Calculating SHAP values...')
    shap_timer = SimbaTimer(start=True)
    data_df = pd.concat([x_df, y_df], axis=1)
    if save_file_no == None:
        out_df_shap_path = os.path.join(save_path, f'SHAP_values_{clf_name}.csv')
        out_df_raw_path = os.path.join(save_path, f'RAW_SHAP_feature_values_{clf_name}.csv')
    else:
        out_df_shap_path = os.path.join(save_path, f'SHAP_values_{str(save_file_no)}_{clf_name}.csv')
        out_df_raw_path = os.path.join(save_path, f'RAW_SHAP_feature_values_{str(save_file_no)}_{clf_name}.csv')

    target_df, nontarget_df = data_df[data_df[y_df.name] == 1], data_df[data_df[y_df.name] == 0]
    if len(target_df) < cnt_present:
        NotEnoughDataWarning(msg=f'Train data contains {str(len(target_df))} behavior-present annotations. This is less the number of frames you specified to calculate shap values for {str(cnt_present)}. SimBA will calculate shap scores for the {str(len(target_df))} behavior-present frames available')
        cnt_present = len(target_df)
    if len(nontarget_df) < cnt_absent:
        NotEnoughDataWarning(msg=f'Train data contains {str(len(nontarget_df))} behavior-absent annotations. This is less the number of frames you specified to calculate shap values for {str(cnt_absent)}. SimBA will calculate shap scores for the {str(len(target_df))} behavior-absent frames available')
        cnt_absent = len(nontarget_df)
    non_target_for_shap = nontarget_df.sample(cnt_absent, replace=False)
    targets_for_shap = target_df.sample(cnt_present, replace=False)
    shap_df = pd.concat([targets_for_shap, non_target_for_shap], axis=0)
    y_df = shap_df.pop(clf_name).values
    explainer = shap.TreeExplainer(rf_clf, data=None, model_output='raw', feature_perturbation='tree_path_dependent')
    expected_value = explainer.expected_value[1]
    out_df_raw = pd.DataFrame(columns=x_names)
    shap_headers = list(x_names)
    shap_headers.extend(('Expected_value', 'Sum', 'Prediction_probability', clf_name))
    out_df_shap = pd.DataFrame(columns=shap_headers)
    for cnt, frame in enumerate(range(len(shap_df))):
        shap_frm_timer = SimbaTimer(start=True)
        frame_data = shap_df.iloc[[frame]]
        frame_shap = explainer.shap_values(frame_data, check_additivity=False)[1][0].tolist()
        frame_shap.extend((expected_value, sum(frame_shap), rf_clf.predict_proba(frame_data)[0][1], y_df[cnt]))
        out_df_raw.loc[len(out_df_raw)] = list(shap_df.iloc[frame])
        out_df_shap.loc[len(out_df_shap)] = frame_shap
        if (cnt % save_it == 0) or (cnt == len(shap_df)-1) and (cnt != 0):
            print(f'Saving SHAP data after {cnt} iterations...')
            out_df_shap.to_csv(out_df_shap_path)
            out_df_raw.to_csv(out_df_raw_path)
        shap_frm_timer.stop_timer()
        print(f'SHAP frame: {cnt+1} / {len(shap_df)}, elapsed time: {shap_frm_timer.elapsed_time_str}...')

    shap_timer.stop_timer()
    stdout_success(msg='SHAP calculations complete', elapsed_time=shap_timer.elapsed_time_str)
    _ = ShapAggregateStatisticsVisualizer(config_path=ini_file_path,
                                          classifier_name=clf_name,
                                          shap_df=out_df_shap,
                                          shap_baseline_value=int(expected_value * 100),
                                          save_path=save_path)



def print_machine_model_information(model_dict: dict):
    """
    Helper to print model information in tabular form.

    Parameters
    ----------
    model_dict: dict
        Python dictionary holding model meta data in SimBA meta-config format.

    Returns
    -------
    None
    """

    table_view = [["Model name", model_dict[MetaKeys.CLF_NAME.value]], ["Ensemble method", 'RF'],
                 ["Estimators (trees)", model_dict[MetaKeys.RF_ESTIMATORS.value]], ["Max features", model_dict[MetaKeys.RF_MAX_FEATURES.value]],
                 ["Under sampling setting", model_dict[ReadConfig.UNDERSAMPLE_SETTING.value]], ["Under sampling ratio", model_dict[ReadConfig.UNDERSAMPLE_RATIO.value]],
                 ["Over sampling setting", model_dict[ReadConfig.OVERSAMPLE_SETTING.value]], ["Over sampling ratio", model_dict[ReadConfig.OVERSAMPLE_RATIO.value]],
                 ["criterion", model_dict[MetaKeys.CRITERION.value]], ["Min sample leaf", model_dict[MetaKeys.MIN_LEAF.value]]]
    headers = ["Setting", "value"]
    print(tabulate(table_view, headers, tablefmt="grid"))

def create_meta_data_csv_training_one_model(meta_data_lst: list,
                                            clf_name: str,
                                            save_dir: str):
    """
    Helper to save single model meta data (hyperparameters, sampling settings etc.) into SimBA
    compatible CSV config file.

    Parameters
    ----------
    meta_data_lst: list
        list of meta data
    clf_name: str
        name of classifier
    save_dir: str,
        Directory where to save output in csv file format.

    Returns
    -------
    None
    """
    print('Saving model meta data file...')
    save_path = os.path.join(save_dir, clf_name + '_meta.csv')
    out_df = pd.DataFrame(columns=get_meta_data_file_headers())
    out_df.loc[len(out_df)] = meta_data_lst
    out_df.to_csv(save_path)


def create_meta_data_csv_training_multiple_models(meta_data,
                                                  clf_name,
                                                  save_dir,
                                                  save_file_no=None):
    print('Saving model meta data file...')
    save_path = os.path.join(save_dir,  f'{clf_name}_{str(save_file_no)}_meta.csv')
    out_df = pd.DataFrame.from_dict(meta_data, orient='index').T
    out_df.to_csv(save_path)

def save_rf_model(rf_clf: RandomForestClassifier,
                  clf_name: str,
                  save_dir: str,
                  save_file_no=None):
    """
    Helper to save pickled classifier object to disk.

    Parameters
    ----------
    rf_clf: RandomForestClassifier
        sklearn random forest classifier
    clf_name: str
        Classifier name
    save_dir: str,
        Directory where to save output in csv file format.
    save_file_no: int or None.
        If integer, represents the count of the classifier within a grid search. If none, the classifier is not
        part of a grid search.

    Returns
    -------
    None
    """

    if save_file_no != None:
        save_path = os.path.join(save_dir, clf_name + '_' + str(save_file_no) + '.sav')
    else:
        save_path = os.path.join(save_dir, clf_name + '.sav')
    pickle.dump(rf_clf, open(save_path, 'wb'))

def get_model_info(config: configparser.ConfigParser,
                   model_cnt: int):
    """
    Helper to read in N SimBA random forest config meta files to python dict memory.

    Parameters
    ----------
    config:  configparser.ConfigParser
        Parsed SimBA project_config.ini
    model_cnt
        Count of models

    Returns
    -------
    model_dict: dict
    """

    model_dict = {}
    for n in range(model_cnt):
        try:
            model_dict[n] = {}
            if config.get('SML settings', 'model_path_' + str(n+1)) == '':
                MissingUserInputWarning(msg=f'Skipping {str(config.get("SML settings", "target_name_" + str(n + 1)))} classifier analysis: no path set to model file')
                continue
            if config.get('SML settings', 'model_path_' + str(n+1)) == 'No file selected':
                MissingUserInputWarning(msg=f'Skipping {str(config.get("SML settings", "target_name_" + str(n + 1)))} classifier analysis: The classifier path is set to "No file selected')
                continue
            model_dict[n]['model_path'] = config.get(ReadConfig.SML_SETTINGS.value, 'model_path_' + str(n+1))
            model_dict[n]['model_name'] = config.get(ReadConfig.SML_SETTINGS.value, 'target_name_' + str(n+1))
            check_str('model_name', model_dict[n]['model_name'])
            model_dict[n]['threshold'] = config.getfloat(ReadConfig.THRESHOLD_SETTINGS.value, 'threshold_' + str(n+1))
            check_float('threshold', model_dict[n]['threshold'], min_value=0.0, max_value=1.0)
            model_dict[n]['minimum_bout_length'] = config.getfloat(ReadConfig.MIN_BOUT_LENGTH.value, 'min_bout_' + str(n+1))
            check_int('minimum_bout_length', model_dict[n]['minimum_bout_length'])
        except ValueError:
            MissingUserInputWarning(msg=f'Skipping {str(config.get("SML settings", "target_name_" + str(n+1)))} classifier analysis: missing information (e.g., no discrimination threshold and/or minimum bout set in the project_config.ini')

    if len(model_dict.keys()) == 0:
        raise NoDataError(msg=f'There are no models with accurate data specified in the RUN MODELS menu. Speficy the model information to SimBA RUN MODELS menu to use them to analyze videos')
    else:
        return model_dict

def get_all_clf_names(config: configparser.ConfigParser,
                      target_cnt: int):
    """
    Helper to get all classifier names in a SimBA project.

    Parameters
    ----------
    config:  configparser.ConfigParser
        Parsed SimBA project_config.ini
    target_cnt
        Count of models

    Returns
    -------
    model_names: list
    """

    model_names = []
    for i in range(target_cnt):
        entry_name = 'target_name_{}'.format(str(i+1))
        model_names.append(read_config_entry(config, ReadConfig.SML_SETTINGS.value, entry_name, data_type=Dtypes.STR.value))
    return model_names


def insert_column_headers_for_outlier_correction(data_df: pd.DataFrame,
                                                 new_headers:list,
                                                 filepath: str):
    """
    Helper to insert new column headers onto a dataframe.

    Parameters
    ----------
    data_df:  pd.DataFrame
        Dataframe where headers to to-bo replaced.
    new_headers: list
        Names of new headers.
    filepath: str
        Path to where ``data_df`` is stored on disk

    Returns
    -------
    data_df: pd.DataFrame
        Dataframe with new headers
    """

    if len(new_headers) != len(data_df.columns):
        difference = int(len(data_df.columns) - len(new_headers))
        bp_missing = int(abs(difference) / 3)
        if difference < 0:

            print('SIMBA ERROR: SimBA expects {} columns of data inside the files within project_folder/csv/input_csv directory. However, '
                  'within file {} file, SimBA found {} columns. Thus, there is {} missing data columns in the imported data, which may represent {} '
                  'bodyparts if each body-part has an x, y and p value. Either revise the SimBA project pose-configuration with {} less body-part, or '
                  'include {} more body-part in the imported data'.format(str(len(new_headers)), filepath, str(len(data_df.columns)), str(abs(difference)),
                                                                      str(int(bp_missing)), str(bp_missing), str(bp_missing)))
        else:
            print('SIMBA ERROR: SimBA expects {} columns of data inside the files within project_folder/csv/input_csv directory. However, '
                'within file {} file, SimBA found {} columns. Thus, there is {} more data columns in the imported data than anticipated, which may represent {} '
                'bodyparts if each body-part has an x, y and p value. Either revise the SimBA project pose-configuration with {} more body-part, or '
                'include {} less body-part in the imported data'.format(str(len(new_headers)), filepath,
                                                                        str(len(data_df.columns)), str(abs(difference)),
                                                                        str(int(bp_missing)), str(bp_missing),
                                                                        str(bp_missing)))
        raise ValueError()
    else:
        data_df.columns = new_headers
        return data_df

def read_pickle(file_path: str) -> object:
    try:
        clf = pickle.load(open(file_path, 'rb'))
    except pickle.UnpicklingError:
        raise CorruptedFileError(msg=f'Can not read {file_path} as a classifier file (pickle).')
    return clf


def bout_train_test_splitter(x_df: pd.DataFrame,
                             y_df: pd.Series,
                             test_size: float):
    """
    Helper to split train and test based on annotated `bouts`.

    Parameters
    ----------
    x_df:  pd.DataFrame
        Features
    y_df: pd.Series
        Target
    test_size: float
        Size of test as ratio of all annotated bouts.

    Returns
    -------
    x_train, x_test, y_train, y_test
    """

    print('Using bout sampling...')
    def find_bouts(s: pd.Series, type: str):
        test_bouts_frames, train_bouts_frames = [], []
        bouts = detect_bouts(pd.DataFrame(s), target_lst=pd.DataFrame(s).columns, fps=-1)
        print(f'{str(len(bouts))} {type} bouts found...')
        bouts = list(bouts.apply(lambda x: list(range(int(x['Start_frame']), int(x['End_frame']) + 1)), 1).values)
        test_bouts_idx = np.random.choice(np.arange(0, len(bouts)), int(len(bouts) * test_size))
        train_bouts_idx = np.array([x for x in list(range(len(bouts))) if x not in test_bouts_idx])
        for i in range(0, len(bouts)):
            if i in test_bouts_idx:
                test_bouts_frames.append(bouts[i])
            if i in train_bouts_idx:
                train_bouts_frames.append(bouts[i])
        return [i for s in test_bouts_frames for i in s], [i for s in train_bouts_frames for i in s]

    test_bouts_frames, train_bouts_frames = find_bouts(s=y_df, type='behavior present')
    test_nonbouts_frames, train_nonbouts_frames = find_bouts(s=np.logical_xor(y_df, 1).astype(int), type='behavior absent')
    x_train = x_df[x_df.index.isin(train_bouts_frames + train_nonbouts_frames)]
    x_test = x_df[x_df.index.isin(test_bouts_frames + test_nonbouts_frames)]
    y_train = y_df[y_df.index.isin(train_bouts_frames + train_nonbouts_frames)]
    y_test = y_df[y_df.index.isin(test_bouts_frames + test_nonbouts_frames)]

    return x_train, x_test, y_train, y_test

def check_dataset_integrity(x_df: pd.DataFrame, y_df: pd.DataFrame):
    x_df = x_df.replace([np.inf, -np.inf, None], np.nan)
    x_nan_cnt = x_df.isna().sum()
    x_nan_cnt = x_nan_cnt[x_nan_cnt > 0]

    if len(x_nan_cnt) > 0:
        if len(x_nan_cnt) < 10:
            raise FaultyTrainingSetError(msg=f'{str(len(x_nan_cnt))} feature column(s) exist in some files within the project_folder/csv/targets_inserted directory, but missing in others. ' \
                  f'SimBA expects all files within the project_folder/csv/targets_inserted directory to have the same number of features: the ' \
                  f'column names with mismatches are: {list(x_nan_cnt.index)}', source=check_dataset_integrity.__name__)
        else:
            raise FaultyTrainingSetError(
                msg=f'{str(len(x_nan_cnt))} feature columns exist in some files, but missing in others. The feature files are found in the project_folder/csv/targets_inserted directory. ' \
                    f'SimBA expects all files within the project_folder/csv/targets_inserted directory to have the same number of features: the first 10 ' \
                    f'column names with mismatches are: {list(x_nan_cnt.index)[0:9]}', source=check_dataset_integrity.__name__)

    if len(y_df.unique()) == 1:
        if y_df.unique()[0] == 0:
            raise FaultyTrainingSetError(msg=f'All training annotations for classifier {str(y_df.name)} is labelled as ABSENT. A classifier has be be trained with both behavior PRESENT and ABSENT ANNOTATIONS.', source=check_dataset_integrity.__name__)
        if y_df.unique()[0] == 1:
            raise FaultyTrainingSetError(msg=f'All training annotations for classifier {str(y_df.name)} is labelled as PRESENT. A classifier has be be trained with both behavior PRESENT and ABSENT ANNOTATIONS.', source=check_dataset_integrity.__name__)


def partial_dependence_calculator(clf: RandomForestClassifier,
                                  x_df: pd.DataFrame,
                                  clf_name: str,
                                  save_dir: str,
                                  clf_cnt: int or None=None):

    print(f'Calculating partial dependencies for {len(x_df.columns)} features...')
    clf.verbose = 0
    check_if_dir_exists(save_dir)
    if clf_cnt:
        save_dir = os.path.join(save_dir, f'partial_dependencies_{clf_name}_{clf_cnt}')
    else:
        save_dir = os.path.join(save_dir, f'partial_dependencies_{clf_name}')
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    for feature_cnt, feature_name in enumerate(x_df.columns):
        save_path = os.path.join(save_dir, f'{feature_name}.csv')
        pdp, axes = partial_dependence(clf, features=[feature_name], X=x_df, percentiles=(0, 1), grid_resolution=30)
        df = pd.DataFrame({'partial dependence': pdp[0], 'feature value': axes[0]})
        df.to_csv(save_path)
        print(f'Partial dependencies for {feature_name} complete...')


def _read_data_file_helper(file_path, file_type, clf_names):
    """ Private function called by ``simba.train_model_functions.read_all_files_in_folder_mp`` """

    timer = SimbaTimer()
    timer.start_timer()
    _, vid_name, _ = get_fn_ext(file_path)
    df = read_df(file_path, file_type).dropna(axis=0, how='all').fillna(0).astype(np.float16)
    if clf_names != None:
        for clf_name in clf_names:
            if not clf_name in df.columns:
                raise ColumnNotFoundError(column_name=clf_name, file_name=file_path)
    timer.stop_timer()
    print(f'Reading complete {vid_name} (elapsed time: {timer.elapsed_time_str}s)...')
    return df


def clf_predict_proba(clf: RandomForestClassifier,
                      x_df: pd.DataFrame, model_name: str or None=None,
                      data_path: str or None=None):
    if len(x_df.columns) != clf.n_features_:
        raise FeatureNumberMismatchError(f'Mismatch in the number of features in input file {data_path}, and what is expected by the model {model_name}. The model expects {str(clf.n_features_)} features. The data contains {len(x_df.columns)} features.')
    p_vals = clf.predict_proba(x_df)
    if p_vals.shape[1] != 2:
        raise ClassifierInferenceError(msg='The classifier {model_name} has not been created properly. See The SimBA GitHub FAQ page or Gitter for more information and suggested fixes.')
    return p_vals[:, 1]


def clf_fit(clf: RandomForestClassifier, x_df: pd.DataFrame, y_df: pd.DataFrame):
    nan_features = x_df[~x_df.applymap(np.isreal).all(1)]
    nan_target = y_df.loc[pd.to_numeric(y_df).isna()]
    if len(nan_features) > 0:
        raise FaultyTrainingSetError(msg=f'{len(nan_features)} frame(s) in your project_folder/csv/targets_inserted directory contains FEATURES with non-numerical values', source=clf_fit.__name__)
    if len(nan_target) > 0:
        raise FaultyTrainingSetError(msg=f'{len(nan_target)} frame(s) in your project_folder/csv/targets_inserted directory contains ANNOTATIONS with non-numerical values', source=clf_fit.__name__)
    return clf.fit(x_df, y_df)




def read_all_files_in_folder_mp(file_paths: list,
                                file_type: str,
                                classifier_names: list or None = None):
    """

    Multiprocessing helper function to read in all data files in a folder to a single
    pd.DataFrame for downstream ML. Defaults to ceil(CPU COUNT / 2) cores. Asserts that all classifiers
    have annotation fields present in each dataframe.

    Parameters
    ----------
    file_paths: list
        List of file paths representing files to be read in.
    file_type: str
        Type of files in ``file_paths``. OPTIONS: csv or parquet.
    classifier_names: list or None
        List of classifier names representing fields of human annotations. If not None, then assert that classifier names
        are present in each data file.

    Returns
    -------
    pd.DataFrame

    """
    if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn', force=True)
    cpu_cnt, _ = find_core_cnt()
    df_lst = []
    try:
        with ProcessPoolExecutor(int(np.ceil(cpu_cnt/2))) as pool:
            for res in pool.map(_read_data_file_helper, file_paths, repeat(file_type), repeat(classifier_names)):
                df_lst.append(res)
        df_concat = pd.concat(df_lst, axis=0).astype(np.float16)
        if 'scorer' in df_concat.columns:
            df_concat = df_concat.set_index('scorer')
        if len(df_concat) == 0:
            raise ValueError('ANNOTATION ERROR: SimBA found 0 observations (frames) in the project_folder/csv/targets_inserted directory')
        df_concat = df_concat.loc[:, ~df_concat.columns.str.contains('^Unnamed')].astype(np.float16)
        data_size = df_concat.memory_usage(index=True).sum()
        print(f'Dataset size: {round(data_size/1000000, 6)}MB / {round(data_size/1000000000, 6)}GB')
        return df_concat.reset_index(drop=True)

    except BrokenProcessPool:
        return read_all_files_in_folder(file_paths=file_paths,
                                        file_type=file_type,
                                        classifier_names=classifier_names)