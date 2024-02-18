import pandas as pd


DATA_PATH = '/Users/simon/Desktop/envs/simba_dev/tests/data/test_projects/mouse_open_field/project_folder/csv/outlier_corrected_movement_location/Video1.csv'
VIDEO_PATH = '/Users/simon/Desktop/envs/simba_dev/tests/data/test_projects/mouse_open_field/project_folder/videos/Video1.mp4'
L_EAR_CORDS = ['Left_ear_x', 'Left_ear_y']
R_EAR_CORDS = ['Right_ear_x', 'Right_ear_y']
NOSE_CORDS = ['Nose_x', 'Nose_y']

df = pd.read_csv(DATA_PATH)

nose_data = df[NOSE_CORDS].values
l_ear_data = df[L_EAR_CORDS].values

