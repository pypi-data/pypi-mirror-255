import numpy as np
from typing import List, Optional, Union, Tuple
try:
    from typing import Literal
except:
    from typing_extensions import Literal
from shapely.geometry import Polygon
import pandas as pd
import cv2

from simba.utils.checks import check_instance, check_str, check_int
from simba.utils.enums import GeometryEnum
from simba.mixins.geometry_mixin import GeometryMixin

class ImageMixin(object):

    def __init__(self):
        pass

    @staticmethod
    def brightness_intensity(imgs: List[np.ndarray],
                             ignore_black: Optional[bool] = True) -> List[float]:
        """
        :example:
        >>> img = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/0.png').astype(np.uint8)
        >>> ImageMixin.brightness_intensity(imgs=[img], ignore_black=False)
        >>> [159.0]
        """
        results = []
        check_instance(source=f'{ImageMixin().brightness_intensity.__name__} imgs', instance=imgs, accepted_types=list)
        for cnt, img in enumerate(imgs):
            check_instance(source=f'{ImageMixin().brightness_intensity.__name__} img {cnt}', instance=img, accepted_types=np.ndarray)
            if ignore_black:
                results.append(np.ceil(np.average(img[img != 0])))
            else:
                results.append(np.ceil(np.average(img)))
        return results

    @staticmethod
    def get_histocomparison(img_1: np.ndarray,
                            img_2: np.ndarray,
                            method: Optional[Literal['chi_square', 'correlation', 'intersection', 'bhattacharyya', 'hellinger', 'chi_square_alternative', 'kl_divergence']] = 'correlation',
                            absolute: Optional[bool] = True):
        """
        :example:
        >>> img_1 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/0.png').astype(np.uint8)
        >>> img_2 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/3.png').astype(np.uint8)
        >>> ImageMixin.get_histocomparison(img_1=img_1, img_2=img_2, method='chi_square_alternative')
        """
        check_instance(source=f'{ImageMixin().get_histocomparison.__name__} img_1', instance=img_1, accepted_types=np.ndarray)
        check_instance(source=f'{ImageMixin().get_histocomparison.__name__} img_2', instance=img_2, accepted_types=np.ndarray)
        check_str(name=f'{ImageMixin().get_histocomparison.__name__} method', value=method, options=list(GeometryEnum.HISTOGRAM_CONTOUR_COMPARISON_MAP.value.keys()))
        method = GeometryEnum.HISTOGRAM_COMPARISON_MAP.value[method]
        if absolute:
            return abs(cv2.compareHist(img_1.astype(np.float32), img_2.astype(np.float32), method))
        else:
            return cv2.compareHist(img_1.astype(np.float32), img_2.astype(np.float32), method)


    @staticmethod
    def get_contourmatch(img_1: np.ndarray,
                         img_2: np.ndarray,
                         method: Optional[Literal['all', 'exterior']] = 'all',
                         absolute: Optional[bool] = True):

        """
        :example:
        >>> img_1 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/0.png').astype(np.uint8)
        >>> img_2 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/3.png').astype(np.uint8)
        >>> ImageMixin.get_contourmatch(img_1=img_1, img_2=img_2, method='exterior')
        """

        check_instance(source=f'{ImageMixin().get_contourmatch.__name__} img_1', instance=img_1, accepted_types=np.ndarray)
        check_instance(source=f'{ImageMixin().get_contourmatch.__name__} img_2', instance=img_2, accepted_types=np.ndarray)
        check_str(name=f'{ImageMixin().get_contourmatch.__name__} method', value=method, options=['all', 'exterior'])
        method = GeometryEnum.CONTOURS_MAP.value[method]
        img_1_contours = cv2.findContours(cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY), method, cv2.CHAIN_APPROX_SIMPLE)[0]
        img_2_contours = cv2.findContours(cv2.cvtColor(img_2, cv2.COLOR_BGR2GRAY), method, cv2.CHAIN_APPROX_SIMPLE)[0]
        if absolute:
            return abs(cv2.matchShapes(img_1_contours, img_2_contours, cv2.CONTOURS_MATCH_I1, 0.0))
        else:
            return cv2.matchShapes(img_1_contours, img_2_contours, cv2.CONTOURS_MATCH_I1, 0.0)


    @staticmethod
    def slice_shapes_in_img(img: Union[np.ndarray, Tuple[cv2.VideoCapture, int]],
                            shapes: List[Union[Polygon, np.ndarray]]):

        """
        Slice regions of interest (ROIs) from an image based on provided shapes.

        :param Union[np.ndarray, Tuple[cv2.VideoCapture, int]] img: Either an image in numpy array format OR a tuple with cv2.VideoCapture object and the frame index.
        :param List[Union[Polygon, np.ndarray]] img: A list of shapes either as vertices in a numpy array, or as shapely Polygons.
        :returns List[np.ndarray]: List of sliced ROIs from the input image.

        >>> img = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/img_comparisons_4/1.png')
        >>> img_video = cv2.VideoCapture('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4')
        >>> data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
        >>> data = pd.read_csv(data_path, nrows=4, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
        >>> shapes = []
        >>> for frm_data in data: shapes.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))
        >>> ImageMixin().slice_shapes_in_img(img=(img_video, 1), shapes=shapes)
        """

        result = []
        check_instance(source=f'{ImageMixin().slice_shapes_in_img.__name__} img', instance=img, accepted_types=(tuple, np.ndarray))
        check_instance(source=f'{ImageMixin().slice_shapes_in_img.__name__} shapes', instance=shapes, accepted_types=list)
        for shape_cnt, shape in enumerate(shapes): check_instance(source=f'{ImageMixin().slice_shapes_in_img.__name__} shapes {shape_cnt}', instance=shape,  accepted_types=(Polygon, np.ndarray))
        if isinstance(img, tuple):
            check_instance(source=f'{ImageMixin().slice_shapes_in_img.__name__} img tuple first entry', instance=img[0], accepted_types=cv2.VideoCapture)
            frm_cnt = int(img[0].get(cv2.CAP_PROP_FRAME_COUNT))
            check_int(name=f'{ImageMixin().slice_shapes_in_img.__name__} video frame count', value=img[1], max_value=frm_cnt, min_value=0)
            img[0].set(1, img[1])
            _, img = img[0].read()
        corrected_shapes = []
        for shape in shapes:
            if isinstance(shape, np.ndarray):
                corrected_shapes.append(shape)
            else:
                corrected_shapes.append(np.array(shape.exterior.coords).astype(np.int64))
        shapes = corrected_shapes; del corrected_shapes
        for shape_cnt, shape in enumerate(shapes):
            x, y, w, h = cv2.boundingRect(shape)
            roi_img = img[y:y + h, x:x + w].copy()
            mask = np.zeros(roi_img.shape[:2], np.uint8)
            cv2.drawContours(mask, [shape - shape.min(axis=0)], -1, (255, 255, 255), -1, cv2.LINE_AA)
            bg = np.ones_like(roi_img, np.uint8)
            cv2.bitwise_not(bg, bg, mask=mask)
            roi_img = bg + cv2.bitwise_and(roi_img, roi_img, mask=mask)
            if len(roi_img) > 2:
                roi_img = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
            result.append(roi_img)
        return result

# img = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/img_comparisons_4/1.png')
# img_video = cv2.VideoCapture('/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/videos/Example_1.mp4')
# data_path = '/Users/simon/Desktop/envs/troubleshooting/Emergence/project_folder/csv/outlier_corrected_movement_location/Example_1.csv'
# data = pd.read_csv(data_path, nrows=4, usecols=['Nose_x', 'Nose_y']).fillna(-1).values.astype(np.int64)
# shapes = []
# for frm_data in data: shapes.append(GeometryMixin().bodyparts_to_circle(frm_data, 100))
#
# ImageMixin().slice_shapes_in_img(img=(img_video, 1), shapes=shapes)


# img_2 = cv2.imread('/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched_frames/3.png').astype(np.uint8)
# ImageMixin.get_contourmatch(img_1=img_1, img_2=img_2, method='exterior')

# img = cv2.VideoCapture('/Users/simon/Desktop/envs/simba_dev/tests/data/test_projects/zebrafish/project_folder/videos/20200730_AB_7dpf_850nm_0003.mp4')
# ImageMixin.slice_shapes_in_img(img=(img, 1))


