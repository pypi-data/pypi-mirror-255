import numpy as np
import cv2
from matplotlib import pyplot as plt


def orb_find(target_img: [np.ndarray], main_img: np.ndarray):



    orb = cv2.ORB_create(nfeatures=10000)
    kp1, des1 = orb.detectAndCompute(target_img, None)
    kp2, des2 = orb.detectAndCompute(main_img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    good_matches = matches[:10]
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    h, w = target_img.shape[:2]
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    print(pts.shape)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 100.0)
    print(M)
    dst = cv2.perspectiveTransform(pts, M)

    img3 = cv2.polylines(main_img, [np.int32(dst)], True, (0, 0, 255), 10, cv2.LINE_AA)
    cv2.imshow('img3', img3)
    cv2.waitKey()

img1 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/6.png')          # query Image
img2 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/test_imgs/main_img.png')  # target Image
orb_find(img1, img2)


#
#
#
# # Initiate SIFT detector
# orb = cv2.ORB_create()
#
# # find the keypoints and descriptors with ORB
# kp1, des1 = orb.detectAndCompute(img1,None)
# kp2, des2 = orb.detectAndCompute(img2,None)
#
# # create BFMatcher object
# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
#
# # Match descriptors.
# matches = bf.match(des1,des2)
#
# # Sort them in the order of their distance.
# matches = sorted(matches, key = lambda x:x.distance)
#
# good_matches = matches[:10]
#
# src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches     ]).reshape(-1,1,2)
# dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
# M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
# matchesMask = mask.ravel().tolist()
#
#
# h,w = img1.shape[:2]
# pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
#
# dst = cv2.perspectiveTransform(pts,M)
# #dst += (w, 0)  # adding offset
#
# draw_params = dict(matchColor = (0,255,0), # draw matches in green color
#                singlePointColor = None,
#                matchesMask = matchesMask, # draw only inliers
#                flags = 2)
#
# #img3 = cv2.drawMatches(img1,kp1,img2,kp2,good_matches, None,**draw_params)
#
# # Draw bounding box in Red
# print(dst)
# img3 = cv2.polylines(img2, [np.int32(dst)], True, (0,0,255),10, cv2.LINE_AA)
#
# cv2.imshow("result", img3)
# cv2.waitKey()