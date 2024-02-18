import math
import time

from numba import njit, prange
import numpy as np
import cv2


@njit('(uint8[:,:,:],)')
def rotate_img(img: np.ndarray):
    rotated_image = np.transpose(img, (1, 0, 2))
    rotated_image = np.fliplr(rotated_image)
    return rotated_image


img = cv2.imread('/Users/simon/Desktop/sliding_line_length.png')
# rotated_image = np.transpose(img, (1, 0, 2))
# rotated_image = np.flip(rotated_image, axis=1)

start = time.time()
for i in range(1000):
    rotated_img = rotate_img(img)
end = time.time()
print(end-start)



# height,width = img.shape[:2] #get width and height of image
# rotated_img = rotate(img, change_angle_to_radius_unit(90), (0,0), (height,width))

#
# cv2.imshow('sdfsdf', rotated_img)
# cv2.waitKey(5000)