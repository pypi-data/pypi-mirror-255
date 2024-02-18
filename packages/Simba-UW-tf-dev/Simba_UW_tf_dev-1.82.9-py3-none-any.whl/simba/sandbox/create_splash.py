import cv2
import numpy as np
from simba.utils.enums import Formats
import imutils
from vidgear.gears import WriteGear

LENGTH_S = 3
FPS = 10
IMAGE_PATH = '/Users/simon/Desktop/splash_2024.png'
ALPHA = list(range(0, 120, 20))
ZOOM_CORD = 264.5, 275
ZOOM_STEP = list(range(0, 103, 3))
ANGLE = 1.5
FRAME_COUNT = int(FPS * LENGTH_S)
SAVE_PATH = '/Users/simon/Desktop/splash_2024_1.mp4'
for i in range(FRAME_COUNT-len(ALPHA)): ALPHA.append(100)
fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)


original_img = cv2.imread(IMAGE_PATH)
white_image = np.ones((original_img.shape[0], original_img.shape[1], 3), dtype=np.uint8) * 255
writer = cv2.VideoWriter(SAVE_PATH, fourcc, FPS, (800, 397))

output_params = {"-vcodec":"libx264", "-crf": 0, "-preset": "fast"} #define (Codec,CRF,preset) FFmpeg tweak parameters for writer

#writer = WriteGear(output_filename = SAVE_PATH, compression_mode = True, logging = True, **output_params) #Define writer with output filename 'Output.mp4'


for frm_cnt in range(int(FPS * LENGTH_S)):
    current_image = np.copy(original_img)
    img_alpha = ALPHA[frm_cnt] / 100
    blended = cv2.addWeighted(white_image, 1 - img_alpha, original_img, img_alpha, 0).astype(np.uint8)
    #img = imutils.resize(blended, width=800)
    height, width = blended.shape[:2]

    # Calculate the crop size based on the percentage
    crop_size_height = int(height * (0.004 *frm_cnt))
    crop_size_width = int(width * (0.004 * frm_cnt))

    # Calculate the crop region
    top = crop_size_height // 2
    bottom = height - crop_size_height // 2
    left = crop_size_width // 2
    right = width - crop_size_width // 2


    # Crop the image
    cropped_image = blended[top:bottom, left:right]

    #crop_size = int(height * 1.5)
    #img = img[crop_size:height-crop_size, :]




    #zoomed_image = img[:, crop_left:width-crop_left]

    img = cv2.resize(cropped_image, (800, 400))


    if frm_cnt == 0:
        writer = cv2.VideoWriter(SAVE_PATH, fourcc, FPS, (img.shape[1], img.shape[0]))

    # cy, cx = [i / 2 for i in img.shape[:-1]] if ZOOM_CORD is None else ZOOM_CORD[::-1]
    # rot_mat = cv2.getRotationMatrix2D((cx, cy), ANGLE, ZOOM_STEP[frm_cnt])
    # result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)

    print(cropped_image.shape)
    writer.write(img)
    #cv2.waitKey(33)

writer.release()


