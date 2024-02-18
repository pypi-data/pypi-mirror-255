import pandas as pd
from simba.utils.errors import SamplingError
from simba.utils.warnings import SamplingWarning
from typing import Union, Dict
from simba.utils.checks import check_int, check_float


def random_multiclass_frm_undersampler(data_df: pd.DataFrame,
                                       target_field: str,
                                       target_var: int,
                                       sampling_ratio: Union[float, Dict[int, float]],
                                       raise_error: bool = False):
    """
    Random multiclass undersampler.

    This function performs random under-sampling on a multiclass dataset to balance the class distribution.
    From each class, the function selects a number of frames computed as a ratio relative to a user-specified class variable.

    All the observations in the user-specified class is selected.

    :param pd.DataFrame data_df: A dataframe holding features and a target column.
    :param str target_field: The name of the target column.
    :param int target_var: The variable in the target that should serve as baseline. E.g., ``0`` if ``0`` represents no behavior.
    :param Union[float, dict] sampling_ratio: The ratio of target_var observations that should be sampled of non-target_var observations.
                                              E.g., if float ``1.0``, and there are `10`` target_var observations in the dataset, then 10 of each non-target_var observations will be sampled.
                                              If different under-sampling ratios for different class variables are needed, use dict with the class variable name as key and ratio raletive to target_var as the value.
    :param bool raise_error: If True, then raises error if there are not enough observations of the non-target_var fullfilling the sampling_ratio. Else, takes all observations even though not enough to reach criterion.

    :examples:
    >>> df = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/multilabel/project_folder/csv/targets_inserted/01.YC015YC016phase45-sample_sampler.csv', index_col=0)
    >>> random_multiclass_frm_undersampler(data_df=df, target_field='syllable_class', target_var=0, sampling_ratio=0.20)
    """


    results_df_lst = [data_df[data_df[target_field] == target_var]]
    sampling_n = None
    if len(results_df_lst[0]) == 0:
        raise SamplingError(msg=f'No observations found in field {target_field} with value {target_var}.', source='')
    if type(sampling_ratio) == float:
        sampling_n = int(len(results_df_lst[0]) * sampling_ratio)
    if type(sampling_ratio) == dict:
        if target_var in sampling_ratio.keys():
            raise SamplingError(msg=f'The target variable {target_var} cannot feature in the sampling ratio dictionary')
        for k, v in sampling_ratio.items():
            check_int(name='Sampling ratio key', value=k)
            check_float(name='Sampling ratio value', value=v, min_value=0.0)

    target_vars = list(data_df[target_field].unique())
    target_vars.remove(target_var)

    for var in target_vars:
        var_df = data_df[data_df[target_field] == var].reset_index(drop=True)
        if type(sampling_ratio) == dict:
            if var not in sampling_ratio.keys():
                raise SamplingError(msg=f'The variable {var} cannot be found in the sampling ratio dictionary')
            else:
                sampling_n = int(len(results_df_lst[0]) * sampling_ratio[var])

        if (len(var_df) < sampling_n) and raise_error:
            raise SamplingError(msg=f'SimBA wanted to sample {sampling_n} examples of behavior {var} but found {len(var_df)}. Change the sampling_ratio or set raise_error to False to sample the maximum number of present observations.', source='')
        if (len(var_df) < sampling_n) and not raise_error:
            SamplingWarning(f'SimBA wanted to sample {sampling_n} examples of behavior {var} but found {len(var_df)}. Sampling {len(var_df)} observations.')
            sample = var_df
        else:
            sample = var_df.sample(n=sampling_n)
        results_df_lst.append(sample)

    return pd.concat(results_df_lst, axis=0)



df = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/multilabel/project_folder/csv/targets_inserted/01.YC015YC016phase45-sample_sampler.csv', index_col=0)


#random_multiclass_frm_undersampler(data_df=df, target_field='syllable_class', target_var=0, sampling_ratio=0.20)
random_multiclass_frm_undersampler(data_df=df,
                                   target_field='syllable_class',
                                   target_var=0,
                                   sampling_ratio={1: 0.1, 2: 0.2, 3: 0.3})