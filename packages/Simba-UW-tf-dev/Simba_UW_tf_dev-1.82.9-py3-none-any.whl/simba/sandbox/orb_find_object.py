import os
from collections import ChainMap
import cv2
from typing import List, Optional, Union, Tuple
from simba.utils.enums import Defaults
from copy import deepcopy
try:
    from typing import Literal
except:
    from typing_extensions import Literal
import numpy as np
from simba.utils.checks import check_file_exist_and_readable, check_if_valid_img
import multiprocessing
from simba.utils.read_write import get_video_meta_data, find_core_cnt, read_frm_of_video
import functools
from shapely.geometry import Polygon

def find_objects(target_imgs: List[np.ndarray],
                 main_img: np.ndarray):

    orb = cv2.ORB_create(nfeatures=1500)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    main_kp, main_des = orb.detectAndCompute(main_img, None)
    results = {}
    final_img = deepcopy(main_img)
    for i in range(len(target_imgs)):
        print(i)
        target_kp, target_des = orb.detectAndCompute(target_imgs[i], None)
        matches = sorted(bf.match(main_des, target_des), key=lambda x: x.distance)[:50]
        src_pts = np.float32([main_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([target_kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 10.0)
        h, w = target_imgs[i].shape[:2]
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        try:
            dst = cv2.perspectiveTransform(pts, M)
            results[i] = Polygon(dst[:, 0])
            cv2.polylines(final_img, [np.int32(dst)], True, (0, 0, 255), 10, cv2.LINE_AA)

        except:
            results[i] = Polygon()
            print(i)




        cv2.imshow('main_img', final_img)
        cv2.waitKey(10000)
        #return results


main_img = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/main_img.png')
target_img_1 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/1.png')
target_img_2 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/2.png')
target_img_3 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/3.png')
target_img_4 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/4.png')
target_img_5 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/5.png')
target_img_6 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/6.png')



main_img = cv2.cvtColor(main_img, cv2.COLOR_BGR2GRAY)
# target_img_1 = cv2.cvtColor(target_img_1, cv2.COLOR_BGR2GRAY)
# target_img_2 = cv2.cvtColor(target_img_2, cv2.COLOR_BGR2GRAY)
#

cap = cv2.VideoCapture('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/08102021_DOT_Rat7_8(2).mp4')
for i in range(1):
    cap.set(1, i)
    _, main_img = cap.read()

    find_objects(main_img=main_img, target_imgs=[target_img_1,
                                                 target_img_2,
                                                 target_img_3,
                                                 target_img_4,
                                                 target_img_5,
                                                 target_img_6])

#print(max_value)
    #print(results[max_frm], max_frm)




    #h, w, _ = img.shape
    #with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:

#
# img = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/videos/Screenshot 2024-01-17 at 12.45.55 PM.png')
# results = find_cropped_frame(video_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/videos/Together_1.avi', img=img, return_img=True)




#
#
#
# img_1 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/0.png').astype(np.uint8)
# img_2 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/10.png').astype(np.uint8)
# orb_matching_similarity_(img_1=img_1, img_2=img_2, method='radius')



#
#
#
#
# orb = cv2.ORB_create()
# kp1, des1 = orb.detectAndCompute(img_1, None)
# kp2, des2 = orb.detectAndCompute(img_2, None)
# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
# bf = cv2.BFMatcher()
# matches = bf.knnMatch(des1, des2, k=2)
#
# good_matches = []
# for m, n in matches:
#     if m.distance < 0.75 * n.distance:
#         good_matches.append(m)
#
#
# img_matches = cv2.drawMatches(img_1, kp1, img_2, kp2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
# cv2.imshow('ORB Matches', img_matches)
# cv2.waitKey(0)
# cv2.destroyAllWindows()