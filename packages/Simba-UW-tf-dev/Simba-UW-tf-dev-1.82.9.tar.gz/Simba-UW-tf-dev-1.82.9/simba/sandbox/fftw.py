from scipy.spatial import Voronoi, voronoi_plot_2d
import pandas as pd
import matplotlib.pyplot as plt
from simba.mixins.geometry_mixin import GeometryMixin
import numpy as np
from shapely.geometry import LineString, MultiPoint, Point, MultiPolygon, Polygon
from typing import List
from shapely import ops
from simba.utils.errors import InvalidInputError
import cv2
from simba.utils.lookups import get_color_dict
from simba.utils.enums import Formats


fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)

video_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/08102021_DOT_Rat7_8(2).mp4'
video_save_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/csv/machine_results/tesselate.mp4'
video_size = (562, 566)
writer = cv2.VideoWriter(video_save_path, fourcc, 25, video_size)

colors = [(240, 0, 0), (0, 0, 240), (0, 240, 0), (0, 165, 255), (203, 192, 255), (0, 255, 255), (255, 0, 255)]


data_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/csv/machine_results/08102021_DOT_Rat7_8(2).csv'
data = pd.read_csv(data_path, index_col=0).iloc[:, 0:21]
data = data[data.columns.drop(list(data.filter(regex='_p')))]
animal_data = data.values.reshape(len(data), -1, 2).astype(int)
triangles = GeometryMixin().multiframe_triangulate_keypoints(data=animal_data)

cap = cv2.VideoCapture(video_path)
for i in range(len(triangles)):
    img_tri = triangles[i][0:7]
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ret, img = cap.read()
    for geom_cnt, geom in enumerate(img_tri):
        hull = np.array(geom.convex_hull.exterior.coords).astype(np.int)
        cv2.fillConvexPoly(img, hull, (colors[geom_cnt]), 0)
    writer.write(np.uint8(img))
    print(i)

cap.release()
writer.release()







#polygon = GeometryMixin().bodyparts_to_polygon(data=animal_data, parallel_offset=1)


# voronoi = Voronoi(animal_data)
# lines = [LineString(voronoi.vertices[line])for line in voronoi.ridge_vertices if -1 not in line]
# convex_hull = MultiPoint([Point(i) for i in animal_data]).convex_hull.buffer(2)
# result = MultiPolygon(
#     [poly.intersection(convex_hull) for poly in ops.polygonize(lines)])
# result = MultiPolygon([p for p in result] + [p for p in convex_hull.difference(ops.unary_union(result))])
# img =  GeometryMixin().view_shapes(shapes=result)
# cv2.imshow('sdfsdf', img)
# cv2.waitKey(5000)

# tringles = ops.triangulate(multipoint)
# img =  GeometryMixin().view_shapes(shapes=tringles)
#cv2.imshow('sdfsdf', img)
#cv2.waitKey(50000)

#
# video_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/08102021_DOT_Rat7_8(2).mp4'
# data_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/csv/machine_results/08102021_DOT_Rat7_8(2).csv'
# body_parts = ['Nose_x', 'Nose_y', 'Tail_base_x', 'Tail_base_y']
# colors = list(get_color_dict().values())
#
# cap = cv2.VideoCapture(video_path)
# cap.set(cv2.CAP_PROP_POS_FRAMES, 750)
# ret, img = cap.read()
# for geom_cnt, geom in enumerate(result.geoms):
#     print(geom_cnt)
#     cv2.fillConvexPoly(img, np.array(geom.exterior.coords).astype(np.int64),
#                        (colors[geom_cnt+2][::-1] ), 0)
#
# cv2.imshow('sdfsdf', img)
# cv2.waitKey(50000)

# plt.plot(animal_data[:,0], animal_data[:,1], 'ko')
# for r in result:
#     plt.fill(*zip(*np.array(list(
#         zip(r.boundary.coords.xy[0][:-1], r.boundary.coords.xy[1][:-1])))),
#         alpha=0.4)
# plt.show()
# #

#print(vor.ridge_vertices)

#fig = voronoi_plot_2d(voronoi)


#voronoi_diagram