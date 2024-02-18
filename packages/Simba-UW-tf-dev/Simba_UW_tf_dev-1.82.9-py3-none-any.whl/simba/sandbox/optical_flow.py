import os
import cv2
import numpy as np
from typing import Union, Optional
from copy import deepcopy
from simba.utils.read_write import get_video_meta_data, read_frm_of_video

# https://docs.opencv.org/3.0-beta/modules/video/doc/motion_analysis_and_object_tracking.html#calcopticalflowfarneback

def optical_flow(video_path: Union[str, os.PathLike],
                 lag: Optional[int] = 1):

    video_meta_data = get_video_meta_data(video_path=video_path)
    cap = cv2.VideoCapture(video_path)


    ref_img = read_frm_of_video(video_path=cap, frame_index=0, greyscale=True)
    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
    p0 = cv2.goodFeaturesToTrack(ref_img, mask=None, **feature_params)

    mask = np.zeros_like(ref_img)
    mask[..., 1] = 255
    lk_params = dict(winSize=(5, 5), maxLevel=10, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    for i in range(lag, 50):
        current_img = read_frm_of_video(video_path=cap, frame_index=i, greyscale=True)
        p1, st, err = cv2.calcOpticalFlowPyrLK(ref_img, current_img, p0, None, **lk_params)

        motion_vectors = p1[st == 1] - p0[st == 1]

        result_image = np.zeros(ref_img.shape, dtype=np.uint8)
        result_image[:] = 255
        # cv2.imshow('result_image', result_image)
        # print('s')
        # cv2.waitKey()
        if motion_vectors is not None:
            for i, (new, old) in enumerate(zip(p1[st == 1], p0[st == 1])):
                a, b = new.ravel()
                c, d = old.ravel()
                print(a, b, c, d)
                print(result_image.shape)
                cv2.line(result_image, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 5)
                cv2.circle(result_image, (int(a), int(b)), 30, (155, 255, 0), -1)

        #flow = np.array(np.gradient(prev_gray), dtype=np.float32)
        #flow = cv2.calcOpticalFlowFarneback(ref_img, current_img, None, pyr_scale=0.5, levels=5, winsize=11, iterations=5, poly_n=5, poly_sigma=1.1, flags=0)
        #magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        # hsv = np.full((ref_img.shape[0], ref_img.shape[1], 3), 0.0)
        # hsv[..., 1] = 255
        # hsv[..., 0] = angle * 180 / np.pi / 2
        # hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        # flow_image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        #
        #result_image = cv2.resize(result_image, (800, 600), interpolation=cv2.INTER_LINEAR)
        cv2.imshow('Optical Flow', result_image)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        ref_img = deepcopy(current_img)


optical_flow(video_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/videos/Together_1.avi')