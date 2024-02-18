import cv2
import numpy as np

# Create a VideoCapture object to capture video from a webcam (you can also provide a video file path)
cap = cv2.VideoCapture('/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/videos/Together_1.avi')

# Create a background subtractor using MOG2
background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25)

while True:
    # Read a frame from the video source
    ret, frame = cap.read()

    # Apply the background subtractor to get the foreground mask
    fg_mask = background_subtractor.apply(frame)
    fg_mask = cv2.resize(fg_mask, (800, 600), interpolation=cv2.INTER_LINEAR)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    mask = np.zeros((fg_mask.shape[0] + 2, fg_mask.shape[1] + 2), dtype=np.uint8)
    fg_mask = cv2.floodFill(fg_mask, mask=mask, seedPoint=(0, 0), newVal=(255, 255, 255))[1]

    # Display the original frame and the foreground mask
    #cv2.imshow('Original Frame', frame)
    cv2.imshow('Foreground Mask', fg_mask)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Release the VideoCapture and close all windows
cap.release()
cv2.destroyAllWindows()