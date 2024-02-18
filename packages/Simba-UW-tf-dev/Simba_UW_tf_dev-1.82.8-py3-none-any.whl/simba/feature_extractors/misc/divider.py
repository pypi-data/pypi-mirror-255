import pandas as pd
from simba.mixins.geometry_mixin import GeometryMixin
import cv2
import numpy as np
import imutils
from simba.utils.lookups import get_color_dict
from simba.utils.enums import Formats


fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
video_save_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/csv/machine_results/extend_line_to_bounding_box_edges.mp4'

video_size = (562, 566)

writer = cv2.VideoWriter(video_save_path, fourcc, 25, video_size)

colors = list(get_color_dict().values())[5:]

colors = [(0, 165, 255), (255, 0, 0)]

video_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/videos/08102021_DOT_Rat7_8(2).mp4'
data_path = '/Users/simon/Desktop/envs/troubleshooting/Rat_NOR/project_folder/csv/machine_results/08102021_DOT_Rat7_8(2).csv'
video_size = (562, 566)

body_parts = ['Zebrafish_LeftEye_x', 'Zebrafish_LeftEye_y', 'Zebrafish_Tail4_x', 'Zebrafish_Tail4_y']
body_parts = ['Nose_x', 'Nose_y', 'Tail_base_x', 'Tail_base_y']

data = pd.read_csv(data_path).head(1000)


data = data[body_parts].astype(int)

line_points = data.values.reshape(len(data), 2, 2).astype(np.int64)
lines = []
shape_collections = []

for i in line_points:
    lines.append(GeometryMixin().extend_line_to_bounding_box_edges(line_points=i, bounding_box=np.array([0, 0, video_size[0], video_size[1]]).astype(np.int64)))

for i in lines:
    shape_collections.append(GeometryMixin().line_split_bounding_box(intersections=i, bounding_box=np.array([0, 0, video_size[0], video_size[1]])))

alpha = 0.5
beta = (1.0 - alpha)
cap = cv2.VideoCapture(video_path)
for i in range(len(shape_collections)):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ret, img = cap.read()
    img_copy = np.copy(img)
    for geom_cnt, geom in enumerate(shape_collections[i].geoms):
        hull = np.array(geom.convex_hull.exterior.coords).astype(np.int)
        cv2.circle(img_copy, (line_points[i][0][0], line_points[i][0][1]), 0, (0, 255, 0), 20)
        cv2.circle(img_copy, (line_points[i][1][0], line_points[i][1][1]), 0, (0, 0, 255), 20)
        cv2.fillConvexPoly(img, hull, (colors[geom_cnt][::-1]), 0)
    img = cv2.addWeighted(img_copy, alpha, img, beta, 0.0)
    writer.write(np.uint8(img))
    print(i)

cap.release()
writer.release()
    # img = imutils.resize(img, width=600)
    # cv2.imshow('asd', img)
    # cv2.waitKey(10)




