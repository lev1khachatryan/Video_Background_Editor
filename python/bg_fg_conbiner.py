from __future__ import print_function
import numpy as np
import cv2
import configparser
import os

# Find OpenCV version
(MAJOR_VER, MINOR_VER, SUBMINOR_VER) = (cv2.__version__).split('.')

def bg_subtractor(path):
	# Open Video
	cap = cv2.VideoCapture(cv2.samples.findFileOrKeep(path))

	if not cap.isOpened:
	    print('Unable to open: ' + path)
	    exit(0)

	# Randomly select 25 frames
	frame_ids = cap.get(cv2.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=25)
	
	# Store selected frames in an array
	frames = []
	for fid in frame_ids:
	    cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
	    ret, frame = cap.read()
	    frames.append(frame)
	
	# Calculate the median along the time axis
	median_frame = np.median(frames, axis=0)
	# cv2.imwrite('background.jpg', median_frame)
	
	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

	return median_frame


def fg_bg_combiner(path, bg_frame, save_dir):
	file_name = path.split('/')[-1].split('.')[0]

	# Open video and check if it successfully opened
	cap = cv2.VideoCapture(cv2.samples.findFileOrKeep(path))
	if not cap.isOpened:
	    print('Unable to open: ' + path)
	    exit(0)

	# Get fps and shape of the video
	if int(MAJOR_VER)  < 3:
		fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
	else:
		fps = cap.get(cv2.CAP_PROP_FPS)
	size = (int(cap.get(3)),int(cap.get(4)))

	# Create video writer
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	out = cv2.VideoWriter(save_dir + file_name + '.avi', fourcc, fps, size)

	background = cv2.resize(bg_frame, size, interpolation=cv2.INTER_AREA)

	while True:
	    _, frame = cap.read()
	    if frame is None:
	    	break

	    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	    mask = np.zeros(frame.shape[:2], np.uint8)
	    bgdModel = np.zeros((1, 65), np.float64)
	    fgdModel = np.zeros((1, 65), np.float64)
	    rect = (200, 50, 300, 400)
	    cv2.grabCut(frame, mask, rect, bgdModel, fgdModel, 1, cv2.GC_INIT_WITH_RECT)
	    mask2 = np.where((mask == 2) | (mask == 0), (0,), (1,)).astype('uint8')
	    frame = frame * mask2[:, :, np.newaxis]

	    mask_1 = frame > 0
	    mask_2 = frame <= 0
	    combination = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) * mask_1 + background * mask_2

	    combination = combination.astype(dtype=np.uint8)

	    out.write(combination)

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()


def main():

	# Read config file
	config = configparser.ConfigParser()
	config.read('config.INI')
	# Get necessary information from config file
	INPUT_PATH = config['paths']['INPUT_PATH']
	OUTPUT_PATH = config['paths']['OUTPUT_PATH']
	BG_VIDEO_NAME = config['addition']['BG_VIDEO_NAME']

	background = bg_subtractor(INPUT_PATH + BG_VIDEO_NAME)

	for file in os.listdir(INPUT_PATH):
	    if file.endswith(".mp4"):
	        path=os.path.join(INPUT_PATH, file)
	        fg_bg_combiner(path, background, OUTPUT_PATH)
	        break


if __name__ == '__main__':
    main()