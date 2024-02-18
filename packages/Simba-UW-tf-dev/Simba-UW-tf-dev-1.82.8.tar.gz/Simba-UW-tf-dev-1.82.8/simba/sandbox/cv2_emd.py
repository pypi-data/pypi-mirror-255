import time

import cv2
import numpy as np
from typing import List, Union, Optional, Tuple
from shapely.geometry import Polygon
from simba.mixins.image_mixin import ImageMixin
from simba.mixins.geometry_mixin import GeometryMixin
import pandas as pd
from simba.utils.checks import check_instance, check_valid_array, check_int
from simba.utils.errors import ArrayError
from simba.utils.read_write import find_core_cnt
from simba.utils.enums import Defaults
import multiprocessing
from numba import njit, uint8, jit, prange


def _slice_shapes_in_imgs_helper(data: Tuple[np.ndarray, np.ndarray]) -> List[np.ndarray]:
    """ Private multiprocess helper called from ``simba.mixins.image_mixin.ImageMixins.slice_shapes_in_imgs()`` to slice shapes from images."""
    img, in_shapes = data[0], data[1]
    shapes, results = [], []
    for shape in in_shapes:
        shape = np.array(shape.exterior.coords).astype(np.int64)
        shape[shape < 0] = 0
        shapes.append(shape)
    for shape_cnt, shape in enumerate(shapes):
        x, y, w, h = cv2.boundingRect(shape)
        roi_img = img[y:y + h, x:x + w].copy()
        mask = np.zeros(roi_img.shape[:2], np.uint8)
        cv2.drawContours(mask, [shape - shape.min(axis=0)], -1, (255, 255, 255), -1, cv2.LINE_AA)
        bg = np.ones_like(roi_img, np.uint8)
        cv2.bitwise_not(bg, bg, mask=mask)
        roi_img = bg + cv2.bitwise_and(roi_img, roi_img, mask=mask)
        results.append(roi_img)
    return results

def slice_shapes_in_imgs(imgs: np.ndarray,
                         shapes: np.ndarray,
                         core_cnt: Optional[int] = -1) -> List[np.ndarray]:

    """
    Slice regions from a stack of images, where the regions are based on defined shapes. Uses multiprocessing.

    For example, given a stack of N images, and N*X geometries representing the region around the animal body-part(s),
    slice out the X geometries from each of the N images and return the sliced areas.

    :example:
    #READ A SET OF 11 IMAGES AND CREATE ARRAY TO STORE THEM IN, AND CONEVRT THEM TO GREYSCALE (OPTIONAL)
    >>> imgs = ImageMixin().read_img_batch_from_video( video_path='/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4', start_frm=0, end_frm=10)
    >>> imgs = np.stack(list(imgs.values()))
    >>> imgs_gray = img_stack_to_greyscale(imgs=imgs)
    # READ A SET OF BODY-PARTS LOCATIONS FOR CORRECSPONDING 11 FRAMES
    >>> data = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv', nrows=11).fillna(-1)
    >>> nose_array, tail_array = data.loc[0:10, ['Nose_x', 'Nose_y']].values.astype(np.float32), data.loc[0:10, ['Tail_base_x', 'Tail_base_y']].values.astype(np.float32)
    #CREATE CIRCLE GEOMETRIES AROUND THE TWO BODY-PART LOCATIONS AND STACK THEM IN A 2D array.
    >>> nose_shapes, tail_shapes = [], []
    >>> for frm_data in nose_array: nose_shapes.append(GeometryMixin().bodyparts_to_circle(frm_data, 80))
    >>> for frm_data in tail_array: tail_shapes.append(GeometryMixin().bodyparts_to_circle(frm_data, 80))
    >>> shapes = np.array(np.vstack([nose_shapes, tail_shapes]).T)
    #RETURN AN ITERABLE OF SIZE 11x2 HOLDING THE 2 SLICED IMAGE GEOMETRIES IN THE 11 IMAGES.
    >>> sliced_images = slice_shapes_in_imgs(imgs=imgs_gray, shapes=shapes)
    """

    check_instance(source=slice_shapes_in_imgs.__name__, instance=imgs, accepted_types=(np.ndarray))
    check_valid_array(data=imgs, source=slice_shapes_in_imgs.__name__, accepted_ndims=(4, 3))
    check_instance(source=slice_shapes_in_imgs.__name__, instance=shapes, accepted_types=(np.ndarray))
    check_valid_array(data=shapes, source=slice_shapes_in_imgs.__name__, accepted_ndims=(2, ), accepted_dtypes=[Polygon])
    if shapes.shape[0] != imgs.shape[0]: raise ArrayError(msg=f'The image array ({imgs.shape[0]}) and shapes array ({shapes.shape[0]}) have unequal length.', source=slice_shapes_in_imgs.__name__)
    check_int(name=f'{slice_shapes_in_imgs.__name__} core count', value=core_cnt, min_value=-1)
    if core_cnt == -1: core_cnt = find_core_cnt()[0]
    results = []
    with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
        for cnt, result in enumerate(pool.imap(_slice_shapes_in_imgs_helper, zip(imgs, shapes), chunksize=1)):
            results.append(result)
    return results

@njit('(uint8[:, :, :, :],)', fastmath=True)
def img_stack_to_greyscale(imgs: np.ndarray):
    """
    Jitted conversion of a 4D stack of color images (RGB format) to grayscale.

    :parameter np.ndarray imgs: A 4D array representing color images. It should have the shape (num_images, height, width, 3) where the last dimension represents the color channels (R, G, B).
    :returns np.ndarray: A 3D array containing the grayscale versions of the input images. The shape of the output array is (num_images, height, width).

    :example:
    >>> imgs = ImageMixin().read_img_batch_from_video( video_path='/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/videos/Together_1.avi', start_frm=0, end_frm=100)
    >>> imgs = np.stack(list(imgs.values()))
    >>> imgs_gray = img_stack_to_greyscale(imgs=imgs)
    """
    results = np.full((imgs.shape[0], imgs.shape[1], imgs.shape[2]), np.nan).astype(np.uint8)
    for i in prange(imgs.shape[0]):
        vals = 0.07 * imgs[i][:, :, 2] + 0.72 * imgs[i][:, :, 1] + 0.21 * imgs[i][:, :, 0]
        results[i] = vals.astype(np.uint8)
    return results





# imgs = ImageMixin().read_img_batch_from_video( video_path='/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4', start_frm=0, end_frm=10)
# imgs = np.stack(list(imgs.values()))
# imgs_gray = img_stack_to_greyscale(imgs=imgs)
# data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
# data = pd.read_csv(data_path, nrows=11).fillna(-1)
# nose_array = data.loc[0:10, ['Nose_x', 'Nose_y']].values.astype(np.float32)
# tail_array = data.loc[0:10, ['Tail_base_x', 'Tail_base_y']].values.astype(np.float32)
# nose_shapes, tail_shapes = [], []
# for frm_data in nose_array: nose_shapes.append(GeometryMixin().bodyparts_to_circle(frm_data, 80))
# for frm_data in tail_array: tail_shapes.append(GeometryMixin().bodyparts_to_circle(frm_data, 80))
# shapes = np.array(np.vstack([nose_shapes, tail_shapes]).T)
#
# #
# results = slice_shapes_in_imgs(imgs=imgs_gray, shapes=shapes)
#
# cv2.imshow('results', results[0][0])
# cv2.waitKey(5000)
# cv2.imshow('results', results[0][1])
# cv2.waitKey(5000)
