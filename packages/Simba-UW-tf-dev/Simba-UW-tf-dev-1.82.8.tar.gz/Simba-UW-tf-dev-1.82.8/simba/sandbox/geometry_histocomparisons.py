import glob
from typing import List, Union, Optional, Tuple
try:
    from typing import Literal
except:
    from typing_extensions import Literal
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from simba.utils.errors import InvalidInputError
from simba.utils.enums import GeometryEnum
from copy import deepcopy
from simba.utils.checks import check_iterable_length, check_instance, check_int, check_str
from simba.mixins.geometry_mixin import GeometryMixin
import cv2
import pandas as pd
from simba.utils.errors import CountError
from simba.mixins.image_mixin import ImageMixin


def geometry_contourcomparison(imgs: List[Union[np.ndarray, Tuple[cv2.VideoCapture, int]]],
                               geometry: Polygon = None,
                               method: Optional[Literal['all', 'exterior']] = 'all',
                               absolute: Optional[bool] = True) -> float:

    """
    Compare histogram similarities within a geometry in two images.

    For example, the polygon may represent an area around a rodents head. While the front paws are not pose-estimated, computing the histograms of the geometry in two sequential images gives indication of movement,

    .. note::
       If shapes is None, the two images in ``imgs`` will be compared.

       `Documentation <https://docs.opencv.org/4.x/d6/dc7/group__imgproc__hist.html#gga994f53817d621e2e4228fc646342d386ad75f6e8385d2e29479cf61ba87b57450>`__.

    .. important::
       If there is non-pose related noise in the environment (e.g., there are light sources that goes on and off, or waving window curtains causing changes in histgram values w/o affecting pose) this will negatively affect the realiability of the output feature values.

    .. image:: _static/img/geometry_histocomparison.png
       :width: 700
       :align: center

    :parameter List[Union[np.ndarray, Tuple[cv2.VideoCapture, int]]] imgs: List of two input images. Can be either an two image in numpy array format OR a two tuples with cv2.VideoCapture object and the frame index.
    :parameter Optional[Polygon] geometry: If Polygon, then the geometry in the two images that should be compared. If None, then entire images will be histocompared.
    :parameter Literal['correlation', 'chi_square'] method: The method used for comparison. E.g., if `correlation`, then small output values suggest large differences between the current versus prior image. If `chi_square`, then large output values  suggest large differences between the geometries.
    :parameter Optional[bool] absolute: If True, the absolute difference between the two histograms. If False, then (image2 histogram) - (image1 histogram)
    :return float: Value representing the histogram similarities between the geometry in the two images.

    :example:
    >>> frm_dir = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/img_comparisons_4'
    >>> data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
    >>> data = pd.read_csv(data_path, nrows=4, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
    >>> imgs, polygons = [], []
    >>> for file_path in sorted(glob.glob(frm_dir + '/*.png')): imgs.append(cv2.imread(file_path))
    >>> for frm_data in data: polygons.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))
    >>> GeometryMixin().geometry_histo_contour_comparison(imgs=imgs, shapes=polygons, method='correlation')
    """

    check_instance(source=f'{geometry_histocomparison.__name__} imgs', instance=imgs, accepted_types=list)
    check_iterable_length(f'{geometry_histocomparison.__name__} imgs', val=len(imgs), min=2, max=2)
    check_str(name=f'{geometry_histocomparison.__name__} method', value=method,options=list(GeometryEnum.HISTOGRAM_COMPARISON_MAP.value.keys()))
    corrected_imgs = []
    for i in range(len(imgs)):
        check_instance(source=f'{geometry_histocomparison.__name__} imgs {i}', instance=imgs[i], accepted_types=(np.ndarray, tuple))
        if isinstance(imgs[i], tuple):
            check_iterable_length(f'{geometry_histocomparison.__name__} imgs {i}', val=len(imgs), min=2, max=2)
            check_instance(source=f'{geometry_histocomparison.__name__} imgs {i} 0', instance=imgs[i][0], accepted_types=cv2.VideoCapture)
            frm_cnt = int(imgs[i][0].get(cv2.CAP_PROP_FRAME_COUNT))
            check_int(name=f'{geometry_histocomparison.__name__} video frame count', value=imgs[i][1], max_value=frm_cnt, min_value=0)
            imgs[i][0].set(1, imgs[i][1])
            _, img = imgs[i][0].read()
            corrected_imgs.append(img)
        else:
            corrected_imgs.append(imgs[i])
    imgs = corrected_imgs; del corrected_imgs
    if geometry is not None:
        sliced_imgs = []
        check_instance(source=f'{geometry_histocomparison.__name__} geometry', instance=geometry, accepted_types=Polygon)
        for img in imgs: sliced_imgs.append(ImageMixin().slice_shapes_in_img(img=img, geometries=[geometry])[0])
        imgs = sliced_imgs; del sliced_imgs
    print(imgs[0])
    return ImageMixin().get_histocomparison(img_1=imgs[0], img_2=imgs[1], method=method, absolute=absolute)


# img_1 = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1_frames/1.png'
# img_2 = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1_frames/41411.png'
#
# img_1 = cv2.imread(img_1)
# img_2 = cv2.imread(img_2)
#
# data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
# data = pd.read_csv(data_path, nrows=1, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
# polygons = []
# for frm_data in data: polygons.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))

geometry_histocomparison(imgs=[img_1, img_2], geometry=polygons[0], method='correlation')



# frm_dir = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/img_comparisons_4'
# data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
# data = pd.read_csv(data_path, nrows=4, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
# imgs, polygons = [], []
# for file_path in sorted(glob.glob(frm_dir + '/*.png')): imgs.append(cv2.imread(file_path))
# for frm_data in data: polygons.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))
# GeometryMixin().geometry_histo_contour_comparison(imgs=imgs, shapes=polygons, method='correlation')
