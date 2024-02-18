import pandas as pd
import cv2
import numpy as np
from simba.mixins.circular_statistics import CircularStatisticsMixin


DATA_PATH = '/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/csv/outlier_corrected_movement_location/stitched.csv'
VIDEO_PATH = '/Users/simon/Desktop/envs/troubleshooting/khan/project_folder/videos/stitched.mp4'
L_EAR_CORDS = ['shaved_Left_Ear_1_x', 'shaved_Left_Ear_1_y']
R_EAR_CORDS = ['shaved_Right_Ear_1_x', 'shaved_Right_Ear_1_y']
NOSE_CORDS = ['shaved_Nose_1_x', 'shaved_Nose_1_y']

df = pd.read_csv(DATA_PATH)

nose_data = df[NOSE_CORDS].values.astype(np.float32)
l_ear_data = df[L_EAR_CORDS].values.astype(np.float32)
r_ear_data = df[R_EAR_CORDS].values.astype(np.float32)

cap = cv2.VideoCapture(VIDEO_PATH)

out_angles = CircularStatisticsMixin().direction_three_bps(nose_loc=nose_data, left_ear_loc=l_ear_data, right_ear_loc=r_ear_data)

for i in range(nose_data.shape[0]):
    left_ear_to_nose = np.arctan2(nose_data[i][0] - l_ear_data[i][0], l_ear_data[i][1] - nose_data[i][1])
    right_ear_nose = np.arctan2(nose_data[i][0] - r_ear_data[i][0], r_ear_data[i][1] - nose_data[i][1])

    mean_angle_rad = np.arctan2(np.sin(left_ear_to_nose) + np.sin(right_ear_nose), np.cos(left_ear_to_nose) + np.cos(right_ear_nose))
    out_angle = (np.degrees(mean_angle_rad) + 360) % 360

    print(out_angle, out_angles[i])

    #out_angle = ((left_ear_to_nose + right_ear_nose) / 2)

    x_mid, y_mid = int((l_ear_data[i][0] + r_ear_data[i][0]) / 2), int((l_ear_data[i][1] + r_ear_data[i][1]) / 2)
    #print(x_mid, y_mid)
    cap.set(1, i)
    _, img = cap.read()


    cv2.circle(img, tuple(nose_data[i]), 0, (155, 155, 0), 10)
    cv2.circle(img, tuple(l_ear_data[i]), 0, (155, 255, 0), 10)
    cv2.circle(img, tuple(r_ear_data[i]), 0, (10, 10, 155), 10)
    cv2.circle(img, (int(x_mid), int(y_mid)), 0, (50, 50, 155), 10)

    cv2.putText(img, str(out_angles[i]), (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 10), 1)
    cv2.putText(img, str(left_ear_to_nose), (100, 200), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 10), 1)


    cv2.imshow('111', img)
    cv2.waitKey(33)
