import cv2
import numpy as np
import colorsys

def apply_sepia_tone(frame):
    sepia_matrix = np.array([[0.393, 0.769, 0.189],
                             [0.349, 0.686, 0.168],
                             [0.272, 0.534, 0.131]])

    sepia_frame = cv2.transform(frame, sepia_matrix.T)
    sepia_frame = np.clip(sepia_frame, 0, 255).astype(np.uint8)

    return sepia_frame

def rotate_hue_rgb(rgb_color, angle):
    r, g, b = rgb_color
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h = (h + angle / 360.0) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

# Replace 'your_input_image' with the path to your PNG image
input_image_path = '/Users/simon/Desktop/envs/simba_dev/docs/tutorials_rst/img/index/landing_page_1.png'
frame = cv2.imread(input_image_path)

# Ensure that the image is in the BGR format (OpenCV default)
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Video properties
fps = 30
width, height = frame.shape[1], frame.shape[0]

# Replace 'your_output_video' with the path to your output video file
output_video_path = '/Users/simon/Desktop/color_transition_video.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# Duration of the video in seconds
video_duration = 10

# Generate frames for the video
for t in range(int(fps * video_duration)):
    # Calculate hue rotation angle based on time
    hue_rotation_angle = (t / fps) * 180.0 / 2.0  # Rotate once every 2 seconds

    # Apply hue rotation and sepia tone
    rotated_frame = np.zeros_like(frame)
    for i in range(width):
        for j in range(height):
            print(i, j)
            rotated_frame[j, i, :] = rotate_hue_rgb(frame[j, i, :], hue_rotation_angle)

    sepia_frame = apply_sepia_tone(rotated_frame)

    # Write the frame to the video file
    out.write(sepia_frame)
    cv2.imshow('sdsd', sepia_frame)
    cv2.waitKey(33)

# Release the video writer
out.release()
