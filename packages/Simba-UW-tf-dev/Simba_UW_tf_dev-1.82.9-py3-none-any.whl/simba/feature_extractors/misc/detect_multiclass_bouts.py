import pandas as pd
from typing import List, Dict

from simba.utils.checks import check_int


def detect_bouts_multiclass(data: pd.DataFrame,
                            target: str,
                            fps: int = 1,
                            classifier_map: Dict[int, str] = None) -> pd.DataFrame:

    """
    Detect bouts in a multiclass time series dataset and return the bout event types, their start times, end times and duration.

    :param pd.DataFrame data: A Pandas DataFrame containing multiclass time series data.
    :param str target: Name of the target column in ``data``.
    :param int fps: Frames per second of the video used to collect ``data``. Default is 1.
    :param Dict[int, str] classifier_map: A dictionary mapping class labels to their names. Used to replace numeric labels with descriptive names. If None, then numeric event labels are kept.

    :example:
    >>> df = pd.DataFrame({'value': [0, 0, 0, 2, 2, 1, 1, 1, 3, 3]})
    >>> detect_bouts_multiclass(data=df, target='value', fps=3, classifier_map={0: 'None', 1: 'sharp', 2: 'track', 3: 'sync'})
    >>>    'Event'  'Start_time'  'End_time'  'Start_frame'  'End_frame'  'Bout_time'
    >>> 0   'None'    0.000000  1.000000          0.0        2.0   1.000000
    >>> 1   'sharp'   1.666667  2.666667          5.0        7.0   1.000000
    >>> 2   'track'   1.000000  1.666667          3.0        4.0   0.666667
    >>> 3   'sync '   2.666667  3.333333          8.0        9.0   0.666667
    """

    check_int(name='FPS', value=fps, min_value=1.0)
    results = pd.DataFrame(columns=['Event', 'Start_time', 'End_time', 'Start_frame', 'End_frame', 'Bout_time'])
    data['is_new_bout'] = (data[target] != data[target].shift(1)).cumsum()
    bouts = data.groupby([target, 'is_new_bout']).apply(lambda x: (x.index[0], x.index[-1]))
    for start_idx, end_idx in bouts:
        if start_idx != 0:
            start_time = start_idx / fps
        else:
            start_time = 0
        if end_idx != 0:
            end_time = (end_idx+1) / fps
        else:
            end_time = 0
        bout_time = ((end_time - start_time))
        event = data.at[start_idx, target]
        results.loc[len(results)] = [event, start_time, end_time, start_idx, end_idx, bout_time]

    if classifier_map:
        results['Event'] = results['Event'].map(classifier_map)

    return results

# Sample DataFrame
# df = pd.DataFrame({'value': [0, 0, 0, 2, 2, 1, 1, 1, 3, 3]})
# detect_bouts_multiclass(data=df, target='value', fps=3, classifier_map={0: 'None', 1: 'sharp', 2: 'track', 3: 'sync'})
