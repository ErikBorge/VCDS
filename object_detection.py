# USAGE
# python deep_learning_object_detection.py --image images/example_01.jpg \
#	--prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
import numpy as np
import cv2

net = None

def initialize():
	global net
	prototxtpath = 'MobileNetSSD_deploy.prototxt.txt'
	modelpath = 'MobileNetSSD_deploy.caffemodel'

	# load our serialized model from disk
	print("[INFO] loading model...")
	net = cv2.dnn.readNetFromCaffe(prototxtpath, modelpath)
def detect(image):
	confidencedefault = 0.6
	#imgpath = 'images/example_01.jpg'

	# initialize the list of class labels MobileNet SSD was trained to
	# detect, then generate a set of bounding box colors for each class
	CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
		"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
		"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
		"sofa", "train", "tvmonitor"]
	#COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
	COLORS = (0, 255, 255)

	# load the input image and construct an input blob for the image
	# by resizing to a fixed 300x300 pixels and then normalizing it
	# (note: normalization is done via the authors of the MobileNet SSD
	# implementation)

	(h, w) = image.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

	# pass the blob through the network and obtain the detections and
	# predictions
	print("[INFO] computing object detections...")
	net.setInput(blob)
	detections = net.forward()

	# loop over the detections
	for i in np.arange(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the
		# prediction
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
		if confidence > confidencedefault:
			# extract the index of the class label from the `detections`,
			# then compute the (x, y)-coordinates of the bounding box for
			# the object
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# display the prediction
			label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
			print("[INFO] {}".format(label))
			y = startY - 35 if startY - 15 > 15 else startY + 35
			cv2.rectangle(image, (startX, startY), (endX, endY),
				COLORS, 2)	#switched COLORS[idx] to COLORS
			cv2.rectangle(image, (startX, y), (startX+150, startY),
				COLORS, -1)	#switched (startX, startY) 2nd arg with (startX, y)	***	switched COLORS[idx] to COLORS
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(image, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
	cv2.imwrite('images/newpic.jpg',image)
	# show the output image
	#cv2.imshow("Output", image)
	#cv2.waitKey(0)

