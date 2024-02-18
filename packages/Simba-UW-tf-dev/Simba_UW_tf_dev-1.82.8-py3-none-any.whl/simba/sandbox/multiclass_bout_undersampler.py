import pandas as pd
from simba.utils.errors import SamplingError
from simba.utils.warnings import SamplingWarning
from typing import Union, Dict
from simba.utils.checks import check_int, check_float, check_that_column_exist
from simba.utils.data import detect_bouts_multiclass
from copy import deepcopy


def random_multiclass_bout_sampler(data: pd.DataFrame,
                                   target_field: str,
                                   target_var: int,
                                   sampling_ratio: Union[float, Dict[int, float]],
                                   raise_error: bool = False) -> pd.DataFrame:

    """
    Randomly sample multiclass behavioral bouts.

    This function performs random sampling on a multiclass dataset to balance the class distribution. From each class, the function selects a count of "bouts" where the count is computed as a ratio of a user-specified class variable count.
    All bout observations in the user-specified class is selected.

    :param pd.DataFrame data: A dataframe holding features and target column.
    :param str target_field: The name of the target column.
    :param int target_var: The variable in the target that should serve as baseline. E.g., ``0`` if ``0`` represents no behavior.
    :param Union[float, dict] sampling_ratio: The ratio of target_var bout observations that should be sampled of non-target_var observations.
                                              E.g., if float ``1.0``, and there are `10`` bouts of target_var observations in the dataset, then 10 bouts of each non-target_var observations will be sampled.
                                              If different under-sampling ratios for different class variables are needed, use dict with the class variable name as key and ratio relative to target_var as the value.
    :param bool raise_error: If True, then raises error if there are not enough observations of the non-target_var fullfilling the sampling_ratio. Else, takes all observations even though not enough to reach criterion.
    :raises SamplingError: If any of the following conditions are met:
                          - No bouts of the target class are detected in the data.
                          - The target variable is present in the sampling ratio dictionary.
                          - The sampling ratio dictionary contains non-integer keys or non-float values less than 0.0.
                          - The variable specified in the sampling ratio is not present in the DataFrame.
                          - The sampling ratio results in a sample size of zero or less.
                          - The requested sample size exceeds the available data and raise_error is True.

    :examples:
    >>> df = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/multilabel/project_folder/csv/targets_inserted/01.YC015YC016phase45-sample_sampler.csv', index_col=0)
    >>> undersampled_df = random_multiclass_bout_sampler(data=df, target_field='syllable_class', target_var=0, sampling_ratio={1: 1.0, 2: 1, 3: 1}, raise_error=True)
    """

    sampling_n, results_df_lst = None, []
    original_data = deepcopy(data)
    check_that_column_exist(df=data, column_name=target_field, file_name=None)
    bouts = detect_bouts_multiclass(data=data, target=target_field)
    target_bouts = bouts[bouts['Event'] == target_var]

    if len(target_bouts) == 0:
        raise SamplingError(msg=f'No bouts of target class {target_var} detected. Cannot perform bout sampling.')
    if type(sampling_ratio) == float:
        sampling_n = int(len(target_bouts) * sampling_ratio)
    if type(sampling_ratio) == dict:
        if target_var in sampling_ratio.keys():
            raise SamplingError(msg=f'The target variable {target_var} cannot feature in the sampling ratio dictionary')
        for k, v in sampling_ratio.items():
            check_int(name='Sampling ratio key', value=k)
            check_float(name='Sampling ratio value', value=v, min_value=0.0)

    target_annot_idx = list(target_bouts.apply(lambda x: list(range(int(x['Start_frame']), int(x['End_frame']) + 1)), 1))
    target_annot_idx = [item for sublist in target_annot_idx for item in sublist]
    results_df_lst.append(original_data.loc[target_annot_idx, :])

    target_vars = list(data[target_field].unique())
    target_vars.remove(target_var)
    for var in target_vars:
        var_bout_df = bouts[bouts['Event'] == var].reset_index(drop=True)
        if type(sampling_ratio) == dict:
            if var not in sampling_ratio.keys():
                raise SamplingError(msg=f'The variable {var} cannot be found in the sampling ratio dictionary')
            else:
                sampling_n = int(len(target_bouts) * sampling_ratio[var])

        if sampling_n <= 0:
            raise SamplingError(msg=f'The variable {var} has a sampling ratio of {sampling_ratio[var]} of observed class {target_var} bouts which gives a sample of zero or less sampled observations')

        if (len(var_bout_df) < sampling_n) and raise_error:
            raise SamplingError(msg=f'SimBA wanted to sample {sampling_n} bouts of behavior {var} but found {len(var_bout_df)} bouts. Change the sampling_ratio or set raise_error to False to sample the maximum number of present observations.', source='')

        if (len(var_bout_df) < sampling_n) and not raise_error:
            SamplingWarning(f'SimBA wanted to sample {sampling_n} examples of behavior {var} bouts but found {len(var_bout_df)}. Sampling {len(var_bout_df)} observations.')
            sample = var_bout_df
        else:
            sample = var_bout_df.sample(n=sampling_n)
        annot_idx = list(sample.apply(lambda x: list(range(int(x['Start_frame']), int(x['End_frame']) + 1)), 1))
        annot_idx = [item for sublist in annot_idx for item in sublist]
        results_df_lst.append(original_data.loc[annot_idx, :])

    return pd.concat(results_df_lst, axis=0)




#     if type(sampling_ratio) == float:
#         sampling_n = int(len(results_df_lst[0]) * sampling_ratio)
#     if type(sampling_ratio) == dict:
#         if target_var in sampling_ratio.keys():
#             raise SamplingError(msg=f'The target variable {target_var} cannot feature in the sampling ratio dictionary')
#         for k, v in sampling_ratio.items():
#             check_int(name='Sampling ratio key', value=k)
#             check_float(name='Sampling ratio value', value=v, min_value=0.0)
#
#     target_vars = list(data_df[target_field].unique())
#     target_vars.remove(target_var)
#
#     for var in target_vars:
#         var_df = data_df[data_df[target_field] == var].reset_index(drop=True)
#         if type(sampling_ratio) == dict:
#             if var not in sampling_ratio.keys():
#                 raise SamplingError(msg=f'The variable {var} cannot be found in the sampling ratio dictionary')
#             else:
#                 sampling_n = int(len(results_df_lst[0]) * sampling_ratio[var])
#
#         if (len(var_df) < sampling_n) and raise_error:
#             raise SamplingError(msg=f'SimBA wanted to sample {sampling_n} examples of behavior {var} but found {len(var_df)}. Change the sampling_ratio or set raise_error to False to sample the maximum number of present observations.', source='')
#         if (len(var_df) < sampling_n) and not raise_error:
#             SamplingWarning(f'SimBA wanted to sample {sampling_n} examples of behavior {var} but found {len(var_df)}. Sampling {len(var_df)} observations.')
#             sample = var_df
#         else:
#             sample = var_df.sample(n=sampling_n)
#         results_df_lst.append(sample)
#
#     return pd.concat(results_df_lst, axis=0)
#
#
#
df = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/multilabel/project_folder/csv/targets_inserted/01.YC015YC016phase45-sample_sampler.csv', index_col=0)


#random_multiclass_frm_undersampler(data_df=df, target_field='syllable_class', target_var=0, sampling_ratio=0.20)
x = random_multiclass_bout_sampler(data=df,
                               target_field='syllable_class',
                               target_var=0,
                               sampling_ratio={1: 1.0, 2: 1, 3: 1},
                               raise_error=True)