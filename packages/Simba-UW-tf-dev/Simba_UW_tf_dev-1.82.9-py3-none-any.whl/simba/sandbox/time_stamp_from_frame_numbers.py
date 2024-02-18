from typing import List

from simba.utils.checks import check_int, check_float
from simba.utils.errors import FrameRangeError

def find_time_stamp_from_frame_numbers(start_frame: int, end_frame: int, fps: float) -> List[str]:
    """
    Given start and end frame numbers and frames per second (fps), return a list of formatted time stamps
    corresponding to the frame range.

    :param int start_frame: The starting frame index.
    :param int end_frame: The ending frame index.
    :param float fps: Frames per second.
    :return List[str]: A list of time stamps in the format 'HH:MM:SS:MS'.

    :example:
    >>> find_time_stamp_from_frame_numbers(start_frame=11, end_frame=20, fps=3.4)
    >>> ['00:00:03:235', '00:00:05:882']
    """
    def get_time(frame_index, fps):
        total_seconds = frame_index / fps
        milliseconds = int((total_seconds % 1) * 1000)
        total_seconds = int(total_seconds)
        seconds = total_seconds % 60
        total_seconds //= 60
        minutes = total_seconds % 60
        hours = total_seconds // 60
        return "{:02d}:{:02d}:{:02d}:{:03d}".format(hours, minutes, seconds, milliseconds)

    check_int(name='start_frame', value=start_frame, min_value=0)
    check_int(name='end_frame', value=end_frame, min_value=0)
    check_float(name='FPS', value=fps, min_value=1)
    if start_frame > end_frame:
        raise FrameRangeError(msg=f'Start frame ({start_frame}) cannot be before end frame ({end_frame})')

    return [get_time(start_frame, fps), get_time(end_frame, fps)]


