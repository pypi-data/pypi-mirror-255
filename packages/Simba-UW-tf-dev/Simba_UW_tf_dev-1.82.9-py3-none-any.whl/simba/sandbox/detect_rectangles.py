import numpy as np
import cv2
from typing import Optional, Tuple, List
from typing_extensions import Literal
from simba.mixins.image_mixin import ImageMixin
from shapely.geometry import Polygon
from copy import deepcopy
from simba.utils.checks import (check_instance,
                                check_iterable_length,
                                check_if_valid_input,
                                check_if_valid_img,
                                check_int)
from simba.utils.errors import CountError, InvalidInputError
from simba.mixins.geometry_mixin import GeometryMixin

def img_to_bw(img: np.ndarray,
              lower_thresh: Optional[int] = 20,
              upper_thresh: Optional[int] = 250,
              invert: Optional[bool] = True) -> np.ndarray:

    """
    Convert an image to black and white (binary).

    :param np.ndarray img: Input image as a NumPy array.
    :param Optional[int] lower_thresh: Lower threshold value for binary conversion. Pixels below this value become black. Default is 20.
    :param Optional[int] upper_thresh: Upper threshold value for binary conversion. Pixels above this value become white. Default is 250.
    :param Optional[bool] invert: Flag indicating whether to invert the binary image (black becomes white and vice versa). Default is True.
    :return np.ndarray: Binary black and white image.
    """

    if len(img) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if not invert: return cv2.threshold(img, lower_thresh, upper_thresh, cv2.THRESH_BINARY)[1]
    else: return ~cv2.threshold(img, lower_thresh, upper_thresh, cv2.THRESH_BINARY)[1]


def img_erode(img: np.ndarray,
              kernel_size: Optional[Tuple[int, int]] = (3, 3),
              iterations: Optional[int] = 3):

    kernel = np.ones(kernel_size, np.uint8)
    img = cv2.erode(img, kernel, iterations=iterations)
    return img

def img_dilate(img: np.ndarray,
               kernel_size: Optional[Tuple[int, int]] = (3, 3),
               iterations: Optional[int] = 3):

    kernel = np.ones(kernel_size, np.uint8)
    img = cv2.dilate(img, kernel, iterations=iterations)
    return img

def segment_img_horizontal(img: np.ndarray,
                           pct: int,
                           lower: Optional[bool] = True,
                           both: Optional[bool] = False) -> np.ndarray:
    """
    Segment a horizontal part of the input image.

    This function segments either the lower, upper, or both lower and upper part of the input image based on the specified percentage.

    :param np.ndarray img: Input image as a NumPy array.
    :param int pct: Percentage of the image to be segmented. If `lower` is True, it represents the lower part; if False, it represents the upper part.
    :param Optional[bool] lower: Flag indicating whether to segment the lower part (True) or upper part (False) of the image. Default is True.
    :return np.array: Segmented part of the image.
    """

    check_if_valid_img(data=img, source=segment_img_horizontal.__name__)
    check_int(name=f'{segment_img_horizontal.__name__} pct', value=pct, min_value=1, max_value=99)
    sliced_height = int(img.shape[0] * pct / 100)
    if both:
        return img[sliced_height:img.shape[0] - sliced_height, :]
    elif lower:
        return img[img.shape[0] - sliced_height:, :]
    else:
        return img[:sliced_height, :]

def segment_img_vertical(img: np.ndarray,
                         pct: int,
                         left: Optional[bool] = True,
                         both: Optional[bool] = False) -> np.ndarray:

    """
    Segment a vertical part of the input image.

    This function segments either the left, right or both the left and right part of  input image based on the specified percentage.

    :param np.ndarray img: Input image as a NumPy array.
    :param int pct: Percentage of the image to be segmented. If `lower` is True, it represents the lower part; if False, it represents the upper part.
    :param Optional[bool] lower: Flag indicating whether to segment the lower part (True) or upper part (False) of the image. Default is True.
    :return np.array: Segmented part of the image.
    """

    check_if_valid_img(data=img, source=segment_img_vertical.__name__)
    check_int(name=f'{segment_img_vertical.__name__} pct', value=pct, min_value=1, max_value=99)
    sliced_width = int(img.shape[1] * pct / 100)
    if both:
        return img[:, sliced_width:img.shape[1] - sliced_width]
    elif left:
        return img[:, :sliced_width]
    else:
        return img[:, img.shape[1] - sliced_width:]


def add_img_border_and_flood_fill(img: np.array,
                                  invert: Optional[bool] = False,
                                  size: Optional[int] = 1) -> np.ndarray:
    """
    Add a border to the input image and perform flood fill.

    E.g., Used to remove any black pixel areas connected to the border of the image. Used to remove noise
    if noise is defined as being connected to the edges of the image.

    .. image:: _static/img/add_img_border_and_flood_fill.png
       :width: 400
       :align: center

    :param np.ndarray img: Input image as a numpy array.
    :param Optional[bool] invert: If false, make black border and floodfill black pixels with white. If True, make white border and floodfill white pixels with black. Default False.
    :param Optional[bool] size: Size of border. Default 1 pixel.
    """

    check_if_valid_img(data=img, source=add_img_border_and_flood_fill.__name__)
    check_int(name=f'{add_img_border_and_flood_fill.__name__} size', value=size, min_value=1)
    if len(img.shape) > 2: raise InvalidInputError(msg='Floodfill requires 2d image', source=add_img_border_and_flood_fill.__name__)
    if not invert:
        img = cv2.copyMakeBorder(img, size, size, size, size, cv2.BORDER_CONSTANT, value=0)
        mask = np.zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=np.uint8)
        img = cv2.floodFill(img, mask=mask, seedPoint=(0, 0), newVal=(255, 255, 255))[1]

    else:
        img = cv2.copyMakeBorder(img, size, size, size, size, cv2.BORDER_CONSTANT, value=255)
        mask = np.zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=np.uint8)
        img = cv2.floodFill(img, mask=mask, seedPoint=(0, 0), newVal=(0, 0, 0))[1]

    return img[size:-size, size:-size]


def find_contour_rectangles(contours: np.ndarray,
                            epsilon_constant: Optional[float] = 0.02) -> List[Polygon]:

    """
    Convert contours into a list of shapely Polygons.

    :param np.ndarray contours: Image contours. Produced by :meth:`simba.mixins.image_mixins.ImageMixins.find_contours`.
    :param float epsilon_constant: Smaller constants produce smoother rectangles.

    :example:
    >>> img = cv2.imread('img/path.png', cv2.COLOR_BGR2GRAY)
    >>> contours = ImageMixin().find_contours(img=img, mode='all', canny=True)
    >>> recatngles = find_contour_rectangles(contours=contours)
    """

    results, seen = [], set()
    for contour in contours:
        epsilon = epsilon_constant * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        x, y, w, h = cv2.boundingRect(approx)
        if (x, y, w, h) not in seen:
            seen.add((x, y, w, h))
            results.append(Polygon([(point[0][0], point[0][1]) for point in approx]))
    return results

def rank_shapes(shapes: List[Polygon],
                method: Literal['area', 'min_distance', 'max_distance', 'mean_distance', 'left_to_right', 'top_to_bottom'],
                deviation: Optional[bool] = False,
                descending: Optional[bool] = True) -> List[Polygon]:

    """
    Rank a list of polygon geometries based on a specified method. E.g., order the list of geometries according to sizes or distances to each other.

    :param List[Polygon] shapes: List of Shapely polygons to be ranked. List has to contain two or more shapes.
    :param Literal['area', 'min_center_distance', 'max_center_distance', 'mean_shape_distance'] method: The ranking method to use.
    :param Optional[bool] deviation: If True, rank based on absolute deviation from the mean. Default: False.
    :param Optional[bool] descending: If True, rank in descending order; otherwise, rank in ascending order. Default: False.
    :return: A input list of Shapely polygons sorted according to the specified ranking method.
    """

    check_instance(source=rank_shapes.__name__, instance=shapes, accepted_types=list)
    check_iterable_length(source=rank_shapes.__name__, val=len(shapes), min=2)
    for i, shape in enumerate(shapes): check_instance(source=f'{rank_shapes.__name__ } {i}', instance=shape, accepted_types=Polygon)
    check_if_valid_input(name=f'{rank_shapes.__name__} method', input=method, options=['area', 'min_distance', 'max_distance', 'mean_distance', 'left_to_right', 'top_to_bottom'])
    ranking_vals = {}
    if method == 'area':
        for shp_cnt, shape in enumerate(shapes):
            ranking_vals[shp_cnt] = int(shape.area)
            print(ranking_vals[shp_cnt])
    elif method == 'min_center_distance':
        for shp_cnt_1, shape_1 in enumerate(shapes):
            shape_1_loc, shape_min_distance = shape_1.centroid, np.inf
            for shp_cnt_2, shape_2 in enumerate(shapes):
                if not shape_2.equals(shape_1):
                    shape_min_distance = min(shape_1.centroid.distance(shape_2.centroid), shape_min_distance)
            ranking_vals[shp_cnt_1] = shape_min_distance
    elif method == 'max_distance':
        for shp_cnt_1, shape_1 in enumerate(shapes):
            shape_1_loc, shape_min_distance = shape_1.centroid, -np.inf
            for shp_cnt_2, shape_2 in enumerate(shapes):
                if not shape_2.equals(shape_1):
                    shape_min_distance = max(shape_1.centroid.distance(shape_2.centroid), shape_min_distance)
            ranking_vals[shp_cnt_1] = shape_min_distance
    elif method == 'mean_distance':
        for shp_cnt_1, shape_1 in enumerate(shapes):
            shape_1_loc, shape_distances = shape_1.centroid, []
            for shp_cnt_2, shape_2 in enumerate(shapes):
                if not shape_2.equals(shape_1):
                    shape_distances.append(shape_1.centroid.distance(shape_2.centroid))
            ranking_vals[shp_cnt_1] = np.mean(shape_distances)
    elif method == 'left_to_right':
        for shp_cnt, shape in enumerate(shapes):
            ranking_vals[shp_cnt] = np.array(shape.centroid)[0]
    elif method == 'top_to_bottom':
        for shp_cnt, shape in enumerate(shapes):
            ranking_vals[shp_cnt] = np.array(shape.centroid)[1]
    if deviation:
        new_ranking_vals, m = {}, sum(ranking_vals.values()) / len(ranking_vals)
        for k, v in ranking_vals.items():
            new_ranking_vals[k] = abs(v - m)
        ranking_vals = new_ranking_vals

    ranked = sorted(ranking_vals, key=ranking_vals.get, reverse=descending)
    return [shapes[idx] for idx in ranked]

def adjust_geometries(geometries: List[Polygon],
                      shift: Tuple[int, int]) -> List[Polygon]:
    """
    Shift geometries specified distance in the x and/or y-axis

    :param  List[Polygon] geometries: List of input polygons to be adjusted.
    :param Tuple[int, int] shift: Tuple specifying the shift distances in the x and y-axis.
    :return List[Polygon]: List of adjusted polygons.

    :example:
    >>> shapes = adjust_geometries(geometries=shapes, shift=(0, 333))
    """

    check_instance(source=f'{adjust_geometries.__name__} geometries', instance=geometries, accepted_types=list)
    if len(geometries) == 0:
        raise CountError(msg='Geometry list is empty', source=adjust_geometries.__name__)
    for i in range(len(geometries)): check_instance(source=f'{adjust_geometries.__name__} geometries {i}', instance=geometries[i], accepted_types=Polygon)
    results = []
    for shape_cnt, shape in enumerate(geometries):
        results.append(Polygon([(int(abs(x + shift[0])), int(abs(y + shift[1]))) for x, y in list(shape.exterior.coords)]))
    return results

def adaptive_threshold(img: np.ndarray, block_size: Optional[int] = 11, constant: Optional[int] = 2):
    check_if_valid_img(data=img, source=adaptive_threshold.__name__)
    check_int(name=f'{adaptive_threshold.__name__} block_size', value=block_size, min_value=1)
    check_int(name=f'{adaptive_threshold.__name__} constant', value=constant, min_value=1)
    if len(img.shape) > 2: img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if not block_size % 2 == 1: block_size = block_size + 1
    return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, constant)


img = cv2.imread('/Users/simon/Desktop/Screenshot 2024-01-20 at 2.41.50 PM.png', cv2.COLOR_BGR2GRAY)
original_img = deepcopy(img)
img = segment_img_horizontal(img=img, lower=True, pct=25)
img = segment_img_vertical(img=img, both=True, pct=15)
# cv2.imshow('img', img)
# cv2.waitKey()


# img = segment_horizontal_img_part(img, pct=25)
#




img = img_to_bw(img=img, invert=False)
img = img_erode(img=img, iterations=2)
img = adaptive_threshold(img=img)
img = img_erode(img=img, iterations=6)
img = img_dilate(img=img, iterations=1)
#cv2.imshow('img', img)
#cv2.waitKey()
img = add_img_border_and_flood_fill(img=img)
# cv2.imshow('img', img)
# cv2.waitKey()

contours = ImageMixin().find_contours(img=img, mode='all')
shapes = find_contour_rectangles(contours=contours)

shapes = GeometryMixin().multiframe_minimum_rotated_rectangle(shapes=shapes)
shapes = adjust_geometries(geometries=shapes, shift=(120, 333))
shapes = rank_shapes(shapes=shapes, method='left_to_right', deviation=False, descending=False)[:6]

for shape in shapes:
    coords = np.array(shape.exterior.coords).astype(np.int)
    cv2.polylines(original_img, [coords], False, (0, 0, 255), 2)
    centrer = (int(np.array(shape.centroid)[0]), int(np.array(shape.centroid)[1]))
    cv2.circle(original_img, centrer, 5, (0, 0, 255), 2)
#
    cv2.imshow('img', original_img)
    cv2.waitKey(2000)

#
# rectangles = []
# for contour in contours:
#     # Approximate the contour to a polygon
#     epsilon = 0.02 * cv2.arcLength(contour, True)
#     approx = cv2.approxPolyDP(contour, epsilon, True)
#
#     # Convert the polygon to a rectangle
#     x, y, w, h = cv2.boundingRect(approx)
#     if (x, y, w, h) not in rectangles:
#         rectangles.append((x, y, w, h))
# #
# #








#img = cv2.bilateralFilter(img, 100, 70, 300)




#img = img_erode(img=img, iterations=2)
#img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
#img = ImageMixin().canny_edge_detection(img)

#img = img_to_bw(img=img)
#img = img_erode(img=img)



#img = cv2.bilateralFilter(img, 100, 70, 300)

#img = cv2.bilateralFilter(img, 100, 70, 300)
#th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)

#img = img_erode(img=img, iterations=2)
#_, img = cv2.threshold(img,100,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


# img = img_erode(img=img, iterations=2)
# img = img_to_bw(img=img)

# cv2.imshow('img', img)
# cv2.waitKey()

#img = img_to_bw(img=img)
#img = cv2.GaussianBlur(img, (5, 5), 0)
#img = cv2.bilateralFilter(img, 100, 70, 300)

#img = ImageMixin().canny_edge_detection(img)

#lines = cv2.HoughLines(img, 1, np.pi / 180, threshold=100)
#print(lines)



#img = cv2.fastNlMeansDenoisingColored(img, None, h=10, hColor=10, templateWindowSize=20, searchWindowSize=21)
#smoothed_image = cv2.ximgproc.createBilateralFilter(cv2.CV_8U, 9, 75, 75).apply(image)


# cv2.imshow('img', img)
# cv2.waitKey()


#denoised_image = cv2.ximgproc.anisotropicDiffusion(img, 0.006, 5, 1)




# def img_floodfill(img: np.ndarray):
#     h, w = img.shape[:2]
#     mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
#     cv2.floodFill(img, mask, (10, 10), 0)
#     cv2.imshow('img', img)
#     cv2.waitKey()
#
#
# def img_gaussian_blur(img: np.ndarray):
#     img = cv2.GaussianBlur(img, (5, 5), 0)
#     return img
#     # cv2.imshow('img', img)
#     # cv2.waitKey()
#
# img = cv2.imread('/Users/simon/Desktop/Screenshot 2024-01-20 at 2.41.50 PM.png')
# orig_img = deepcopy(img)
#
# # Get the height and width of the image
# height, width = img.shape[:2]
#
# # Define the lower third of the image
# lower_third_start = int(5 * height / 6)
# lower_third_end = height
#
# # Extract the lower third of the image
# img = img[lower_third_start:lower_third_end, :]
#
# img = img_to_bw(img=img)
# img = img_erode(img=img)
# img = img_gaussian_blur(img=img)
# img = ImageMixin().canny_edge_detection(img=img)
#
# contours = ImageMixin().find_contours(img=img)
# edge_threshold = 8
#
# mask = np.zeros_like(img)
# mask[:edge_threshold, :] = 255  # Top edge
# mask[-edge_threshold:, :] = 255  # Bottom edge
# mask[:, :edge_threshold] = 255  # Left edge
# mask[:, -edge_threshold:] = 255  # Right edge
# print(contours)
# for contour in contours:
#     x, y, w, h = cv2.boundingRect(contour)
#
#     # Check if the contour is near any edge
#     if any([
#         np.any(mask[y:y + h, x:x + w] == 255),
#         np.any(mask[max(0, y - edge_threshold):min(height, y + h + edge_threshold), max(0, x - edge_threshold):min(width, x + w + edge_threshold)] == 255)
#     ]):
#         continue  # Skip contours near the edges
#
#     # Draw the contour on the original image
#     print('c')
#     cv2.drawContours(orig_img, [contour], -1, (0, 255, 0), 2)
#
#
# #
# result_image = remove_contours_near_edges(input_image, threshold_distance)
#
#
#
# print(len(contours))
# filtered_contours = []
# for contour in contours:
#     x, y, w, h = cv2.boundingRect(contour)
#     if x > 50 and y > 50 and (width - x - w) > 50 and ( height - y - h) > 50:
#         filtered_contours.append(contour)
# print(len(filtered_contours))
#
# rectangles = [cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True) for cnt in filtered_contours]
# for rect in rectangles:
#     # Adjust the y-coordinate of the rectangles to match the lower fourth in the original image
#     rect[:, 0, 1] += lower_third_start
#     cv2.drawContours(img, [rect], 0, (0, 255, 0), 2)
#
# #
# cv2.imshow('img', orig_img)
# cv2.waitKey()



#img = img_floodfill(img=img)


