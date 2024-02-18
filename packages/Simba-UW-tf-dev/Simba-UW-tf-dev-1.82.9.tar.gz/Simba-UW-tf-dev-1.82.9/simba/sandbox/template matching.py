from typing import Union, Optional, Tuple
import numpy as np
import multiprocessing
import functools
import os
import cv2
from simba.utils.enums import Defaults
from collections import ChainMap

from simba.utils.checks import check_if_valid_img
from simba.utils.read_write import find_core_cnt, get_video_meta_data

def _template_matching_cpu_helper(data: np.ndarray,
                                  video_path: Union[str, os.PathLike],
                                  target_frm: np.ndarray):
    cap = cv2.VideoCapture(video_path)
    start, end, current = data[0], data[-1], data[0]
    cap.set(1, start); results = {}
    while current < end:
        print(f'Processing frame {current}...')
        _, img = cap.read()
        result = cv2.matchTemplate(img, target_frm, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        results[current] = {'p': np.max(result), 'loc': max_loc}
        current += 1
    return results




def template_matching_cpu(video_path: Union[str, os.PathLike],
                          img: np.ndarray,
                          core_cnt: Optional[int] = -1,
                          return_img: Optional[bool] = False) -> Tuple[int, dict, Union[None, np.ndarray]]:

    results, found_img = [], None
    check_if_valid_img(data=img)
    if core_cnt == -1: core_cnt = find_core_cnt()[0]
    frame_cnt = get_video_meta_data(video_path=video_path)['frame_count']
    frm_idx = np.arange(0, frame_cnt + 1)
    chunk_size = len(frm_idx) // core_cnt
    remainder = len(frm_idx) % core_cnt
    split_frm_idx = [frm_idx[i * chunk_size + min(i, remainder):(i + 1) * chunk_size + min(i + 1, remainder)] for i in range(core_cnt)]
    print(img)
    with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
        constants = functools.partial(_template_matching_cpu_helper, video_path=video_path, target_frm=img)
        for cnt, result in enumerate(pool.imap(constants, split_frm_idx, chunksize=1)):
            results.append(result)
    pool.terminate(); pool.join()
    results = dict(ChainMap(*results))
    print(results)


    #

    #
    #     for cnt, result in enumerate(pool.imap(constants, split_frm_idx, chunksize=1)):
    #         results.append(result)
    # pool.terminate(); pool.join()
    # results = dict(ChainMap(*results))

img = cv2.imread('/Users/simon/Desktop/Screenshot 2024-01-20 at 2.41.50 PM 1.png')
template_matching_cpu(video_path='/Users/simon/Downloads/1B_Touch_5CSRT_MouseTraining1_s1_a2-grey_clipped.mp4',
                      img=img)