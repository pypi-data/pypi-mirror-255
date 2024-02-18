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
from simba.utils.read_write import read_frm_of_video
from simba.utils.checks import check_iterable_length, check_instance, check_str
from simba.mixins.geometry_mixin import GeometryMixin
import cv2
import pandas as pd
from simba.utils.errors import CountError
from simba.mixins.image_mixin import ImageMixin

def geometry_contourcomparison(imgs: List[Union[np.ndarray, Tuple[cv2.VideoCapture, int]]],
                               geometry: Optional[Polygon] = None,
                               method: Optional[Literal['all', 'exterior']] = 'all',
                               canny: Optional[bool] = True) -> float:

    """
    Compare contours between a geometry in two images using shape matching.

    .. image:: _static/img/geometry_contourcomparison.png
       :width: 700
       :align: center

    .. important::
       If there is non-pose related noise in the environment (e.g., there are non-experiment related intermittant light or shade sources that goes on and off, this will negatively affect the reliability of contour comparisons.

       Used to pick up very subtle changes around pose-estimated body-part locations.

    :parameter List[Union[np.ndarray, Tuple[cv2.VideoCapture, int]]] imgs: List of two input images. Can be either be two images in numpy array format OR a two tuples with cv2.VideoCapture object and the frame index.
    :parameter Optional[Polygon] geometry: If Polygon, then the geometry in the two images that should be compared. If None, then entire images will be contourcompared.
    :parameter Literal['all', 'exterior'] method: The method used for contour comparison.
    :parameter Optional[bool] canny: If True, applies Canny edge detection before contour comparison. Helps reduce noise and enhance contours.  Default is True.
    :returns float: Contour matching score between the two images. Lower scores indicate higher similarity.


    :example:
    >>> img_1 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1_frames/1978.png').astype(np.uint8)
    >>> img_2 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1_frames/1977.png').astype(np.uint8)
    >>> data = pd.read_csv('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv', nrows=1, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
    >>> geometry = GeometryMixin().bodyparts_to_circle(data[0, :], 100)
    >>> geometry_contourcomparison(imgs=[img_1, img_2], geometry=geometry, canny=True, method='exterior')
    >>> 22.54
    """

    check_instance(source=f'{geometry_contourcomparison.__name__} imgs', instance=imgs, accepted_types=list)
    check_iterable_length(f'{geometry_contourcomparison.__name__} imgs', val=len(imgs), min=2, max=2)
    check_str(name=f'{geometry_contourcomparison.__name__} method', value=method, options=list(GeometryEnum.CONTOURS_MAP.value.keys()))
    corrected_imgs = []
    for i in range(len(imgs)):
        check_instance(source=f'{geometry_contourcomparison.__name__} imgs {i}', instance=imgs[i], accepted_types=(np.ndarray, tuple))
        if isinstance(imgs[i], tuple):
            check_iterable_length(f'{geometry_contourcomparison.__name__} imgs {i}', val=len(imgs), min=2, max=2)
            check_instance(source=f'{geometry_contourcomparison.__name__} imgs {i} 0', instance=imgs[i][0], accepted_types=cv2.VideoCapture)
            corrected_imgs.append(read_frm_of_video(video_path=imgs[i][0], frame_index=imgs[i][1]))
        else: corrected_imgs.append(imgs[i])
    imgs = corrected_imgs; del corrected_imgs
    if geometry is not None:
        sliced_imgs = []
        check_instance(source=f'{geometry_contourcomparison.__name__} geometry', instance=geometry, accepted_types=Polygon)
        for img in imgs:
            sliced_imgs.append(ImageMixin().slice_shapes_in_img(img=img, geometries=[geometry])[0])

        imgs = sliced_imgs; del sliced_imgs

    return ImageMixin().get_contourmatch(img_1=imgs[0], img_2=imgs[1], canny=canny, method=method)


