import time
from typing import Optional, Tuple, Dict, Iterable, Union
try:
    from typing import Literal
except:
    from typing_extensions import Literal
import numpy as np
import cv2
import math
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.strtree import STRtree
from simba.utils.checks import check_int, check_float, check_instance, check_iterable_length
from simba.utils.errors import InvalidInputError
from simba.mixins.geometry_mixin import GeometryMixin
from simba.utils.read_write import get_pkg_version

OLDER_SHAPELY = '1.7.1'
NEWER_SHAPELY = '2.0.1'

class SpatialTree(GeometryMixin):
    def __init__(self):
        GeometryMixin.__init__(self)
        self.shapely_version = get_pkg_version(pkg='shapely')
        if self.shapely_version == OLDER_SHAPELY:
            self.old_shapely = True
        else:
            self.old_shapely = False

    def fit(self,
            geometries: Iterable[Union[Polygon, MultiPolygon, Point]],
            node_capacity: Optional[int] = 10):

        check_instance(source=f'{SpatialTree.__name__} geometries', instance=geometries, accepted_types=(np.ndarray, list, tuple))
        check_iterable_length(source=f'{SpatialTree.__name__} geometries', val=len(geometries), min=2)
        if self.old_shapely:
            return STRtree(geometries)
        else:
            return STRtree(geometries, node_capacity=node_capacity)

    def query_point_nearest(self,
                            query_points: Iterable[Point],
                            geometries: dict,
                            spatial_tree: STRtree):

        if self.old_shapely:
            nearest_geo = spatial_tree.nearest(query_points)
            nearest_geo.take()
        #     return [x for x, y in geometries.items() if y == nearest_geo][0]
        # pass



    #def query




        # start = time.time()
        # print
        # print(time.time() - start)


        #print(self.shapely_version)




img = cv2.imread('/Users/simon/Desktop/Screenshot 2024-01-21 at 10.15.55 AM.png', 1)
polygons, aspect_ratio = GeometryMixin.bucket_img_into_grid_square(bucket_grid_size=(300, 100), img_size=(img.shape[1], img.shape[0]), px_per_mm=5.0)
spatial_tree = SpatialTree().fit(geometries=list(polygons.values()))
nearest_polygon = SpatialTree().query_point_nearest(query_points=Point(55.91, 10.48), spatial_tree=spatial_tree, geometries=polygons)

res = spatial_tree.query([Point(55.91, 10.48), Point(55.91, 10.48)])
print(res)