import pandas as pd
import os, glob
import numpy as np
import pickle
import cv2
import itertools
from tqdm import tqdm
import networkx as nx

from simba.utils.read_write import get_fn_ext, get_video_meta_data
from simba.utils.data import find_ranked_colors
from simba.utils.enums import Formats
from simba.utils.lookups import get_color_dict
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.network_mixin import NetworkMixin

#PROJECT CONFIGURATION
PROJECT_DIR = '/Users/simon/Desktop/envs/troubleshooting/ARES_data/Termite Test/project'
SHAPES_SAVE_DIR = os.path.join(PROJECT_DIR, 'project_data/shapes')
VIDEOS_OUT_DIR = os.path.join(PROJECT_DIR, 'project_data/videos')
GRAPHS_DIR = os.path.join(PROJECT_DIR, 'project_data/graphs')
VIDEOS_IN_DIR = os.path.join(PROJECT_DIR, 'videos')
INPUT_DATA_DIR = os.path.join(PROJECT_DIR, 'input_data')
SHAPE_OVERLAP_DIR = os.path.join(PROJECT_DIR, 'project_data/shape_overlap_data')
DATA_FORMAT = 'csv'
FPS = 25
TRACK_COL = 'track'
FRAME_COL = 'frame_idx'
SCORE_SUFFIX = 'score'
COLORS = list(get_color_dict().values())[5:]
BUFFER_PX = 20


#FOR EACH VIDEO IN INPUT_DATA_DIR, COMPUTE THE FRAMEWISE BUFFERED BODY POLYGON AND
#FORCE THE POLYGONS TO RECTANGULES, SAVE THE DATA AS PICKLES

if not os.path.isdir(SHAPES_SAVE_DIR): os.makedirs(SHAPES_SAVE_DIR)
for file_path in tqdm(glob.glob(INPUT_DATA_DIR + '/*.csv')):
    video_name = get_fn_ext(filepath=file_path)[1]
    df = pd.read_csv(file_path).fillna(0)
    score_cols = [c for c in df.columns if c.endswith(f'.{SCORE_SUFFIX}')]
    score_df = df[score_cols]
    track_frm_df = df[[TRACK_COL, FRAME_COL]]
    df = df.drop(score_cols + [TRACK_COL, FRAME_COL], axis=1).astype(np.int32)
    data = df.values.reshape(len(df), -1, 2)
    shapes = GeometryMixin().multiframe_bodyparts_to_polygon(data=data, parallel_offset=BUFFER_PX, video_name=video_name)
    track_frm_df['shape'] = GeometryMixin().multiframe_minimum_rotated_rectangle(shapes=shapes, video_name=video_name)
    shapes = {}
    for track in track_frm_df[TRACK_COL].unique():
        shapes[track] = list(track_frm_df[track_frm_df[TRACK_COL] == track].drop(TRACK_COL, axis=1).set_index(FRAME_COL).to_dict().values())[0]
    with open(os.path.join(SHAPES_SAVE_DIR, f'{video_name}.pickle'), 'wb') as h:
        pickle.dump(shapes, h, protocol=pickle.HIGHEST_PROTOCOL)


#VISUALIZE THE BOUNDING BOXES IN A SINGLE VIDEO TO CONFIRM THEY LOOK OK
# VIDEO_NAME = 'Termite Test'
#
# with open(os.path.join(SHAPES_SAVE_DIR, f'{VIDEO_NAME}.pickle'), 'rb') as handle:
#     shapes = pickle.load(handle)
# fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
# video_input_path = os.path.join(VIDEOS_IN_DIR, f'{VIDEO_NAME}.mp4')
# video_output_path = os.path.join(VIDEOS_OUT_DIR, f'{VIDEO_NAME}.mp4')
# video_meta_data = get_video_meta_data(video_path=video_input_path)
# writer = cv2.VideoWriter(video_output_path, fourcc, video_meta_data['fps'], (video_meta_data['width'], video_meta_data['height']))
# cap = cv2.VideoCapture(video_input_path)
#
# frm_cnt = 0
# while (cap.isOpened()):
#     ret, img = cap.read()
#     try:
#         for trk_cnt, trk in enumerate(shapes.keys()):
#             cv2.polylines(img, [np.array(shapes[trk][frm_cnt].exterior.coords).astype(np.int64)], True, COLORS[trk_cnt][::-1], 2)
#         writer.write(img.astype(np.uint8))
#         frm_cnt += 1
#         #print(frm_cnt)
#     except:
#         break
# cap.release();  writer.release()
# print(f'Video {video_output_path} complete.')

# COMPUTE POLYGON OVERLAPS. FOR EVERY FRAME IN EVERY VIDEO, CHECK EVERY COMBINATION OF
# TWO ANIMAL BOUNDING BOXES AND COMPUTE IF THEIR RECTANGULAR BOUNDING BOXES ARE OVERLAPPING.
WINDOW_SIZE = None

SHAPE_FILES = glob.glob(SHAPES_SAVE_DIR + '/*.pickle')
if not os.path.isdir(SHAPE_OVERLAP_DIR): os.makedirs(SHAPE_OVERLAP_DIR)
for shape_file in tqdm(SHAPE_FILES):
    file_name = get_fn_ext(shape_file)[1]
    save_path = os.path.join(SHAPE_OVERLAP_DIR, f'{file_name}.pickle')
    with open(shape_file, 'rb') as handle:
        shapes = pickle.load(handle)
    results = {}
    for c in itertools.combinations(shapes.keys(), 2):
        animal_1, animal_2 = list(shapes[c[0]].values()), list(shapes[c[1]].values())
        results[(c[0], c[1])] = GeometryMixin().multiframe_compute_shape_overlap(shape_1=animal_1, shape_2=animal_2, names=(c[0], c[1], file_name))
    if WINDOW_SIZE is None:
        results = {key: sum(values) for key, values in results.items()}
    if type(WINDOW_SIZE) == int:
        results_binned = {}
        for k, v in results.items():
            results_binned[k] = [sum(v[i:i + WINDOW_SIZE]) for i in range(0, len(v), WINDOW_SIZE)]
        results = results_binned
    with open(save_path, 'wb') as h:
        pickle.dump(results, h, protocol=pickle.HIGHEST_PROTOCOL)

### CREATE GRAPHS FROM OVERLAP DATA, USING THE OVERLAP TIME AS EDGE WEIGHTS, AND SAVE THE GRAPHS TO DISK
if not os.path.isdir(GRAPHS_DIR): os.makedirs(GRAPHS_DIR)
OVERLAP_FILES = glob.glob(SHAPE_OVERLAP_DIR + '/*.pickle')
for overlap_file in tqdm(OVERLAP_FILES):
    file_name = get_fn_ext(shape_file)[1]
    save_path = os.path.join(GRAPHS_DIR, f'{file_name}.pickle')
    with open(overlap_file, 'rb') as handle:
        data = pickle.load(handle)
    data = {k: float(v) for k,v in data.items()}
    graph = NetworkMixin.create_graph(data=data)
    nx.write_gpickle(graph, save_path)


### GRAB A GRAPH AND COMPUTE THE PAGE RANK, CENTRALITY, AND PLOT A GRAPH
VIDEO_NAME = 'Termite Test'

graph_path = os.path.join(GRAPHS_DIR, f'{VIDEO_NAME}.pickle')
graph = nx.read_gpickle(graph_path)
page_ranks = NetworkMixin().graph_page_rank(graph=graph)
katz_centrality = NetworkMixin().graph_katz_centrality(graph=graph)

clrs = find_ranked_colors(data=page_ranks, palette='magma', as_hex=True)
graph = NetworkMixin().visualize(graph=graph, palette=clrs, save_path='/Users/simon/Desktop/envs/troubleshooting/ARES_data/Termite Test/project/project_data/network_html/edge_0.html')
