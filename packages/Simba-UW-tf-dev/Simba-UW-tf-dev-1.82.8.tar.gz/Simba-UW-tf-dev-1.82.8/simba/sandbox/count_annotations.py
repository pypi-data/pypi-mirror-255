import os
from typing import Union
from simba.utils.checks import check_file_exist_and_readable, check_that_column_exist
from simba.mixins.config_reader import ConfigReader
from simba.utils.read_write import read_df
from simba.utils.errors import NoFilesFoundError
from simba.utils.read_write import get_fn_ext
from simba.utils.printing import stdout_success, SimbaTimer
import pandas as pd

def print_project_annotation_counts(config_path: Union[str, os.PathLike]) -> None:
    """
    Retrieve and save annotation counts annotated videos within the SimBA project. Annotation
    counts are saved in a CSV within the `project_folder/logs` directory in with the
    annotation_counts_20240110185525.csv filename format.

    .. note::
        `Example output file <https://github.com/sgoldenlab/simba/blob/master/docs/ROI_tutorial.md#part-3-generating-features-from-roi-data>`__.

    :parameter Union[str, os.PathLike] config_path: Path to SimBA project config.
    :raises NoFilesFoundError: If no data files are found in the project targets_inserted directory.

    :example:
    >>> print_project_annotation_counts(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini')
    """


    timer = SimbaTimer(start=True)
    check_file_exist_and_readable(file_path=config_path)
    config_obj = ConfigReader(config_path=config_path, read_video_info=True, create_logger=False)
    if len(config_obj.target_file_paths) == 0:
        raise NoFilesFoundError(msg=f'No data files found in {config_obj.file_type} format the directory: {config_obj.targets_folder}', source=print_project_annotation_counts.__name__)
    column_names = ['VIDEO', 'VIDEO LENGTH (SECONDS)', 'VIDEO FPS']
    for clf in config_obj.clf_names:
        column_names.extend((f'{clf} FRAME COUNT PRESENT', f'{clf} SECONDS PRESENT', f'{clf} FRAME COUNT ABSENT', f'{clf} SECONDS ABSENT'))
    results = pd.DataFrame(columns=column_names)
    save_path = os.path.join(config_obj.logs_path, f'annotation_counts_{config_obj.datetime}.csv')
    for file_cnt, file_path in enumerate(config_obj.target_file_paths):
        _, file_name, _ = get_fn_ext(filepath=file_path)
        print(f'Reading {file_name} ({file_cnt+1}/{len(config_obj.target_file_paths)})...')
        df = read_df(file_path=file_path, file_type=config_obj.file_type, usecols=config_obj.clf_names)
        _, _, fps = config_obj.read_video_info(video_name=file_name, raise_error=True)
        video_results = {'VIDEO': file_name, "VIDEO LENGTH (SECONDS)": len(df) / fps, 'VIDEO FPS': fps}
        for clf_name in config_obj.clf_names:
            check_that_column_exist(df=df, column_name=clf_name, file_name=file_path)
            video_results[f'{clf_name} FRAME COUNT PRESENT'] = df[clf_name].sum()
            video_results[f'{clf_name} SECONDS PRESENT'] = df[clf_name].sum() / fps
            video_results[f'{clf_name} FRAME COUNT ABSENT'] = len(df) - df[clf_name].sum()
            video_results[f'{clf_name} SECONDS ABSENT'] = (len(df) - df[clf_name].sum()) / fps
        results = results.append(video_results, ignore_index=True)
    results.to_csv(save_path)
    timer.stop_timer()
    stdout_success(msg=f'Annotation data for {len(config_obj.target_file_paths)} videos saved at {save_path}', elapsed_time=timer.elapsed_time_str)

#print_project_annotation_counts(config_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini')

