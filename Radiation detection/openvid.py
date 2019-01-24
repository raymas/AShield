import cv2
import sys
import os
import numpy as np

try:
    vidFile = cv2.VideoCapture(os.path.join(os.path.dirname( __file__ ) + "\\beam.mp4"))
except:
    print "problem opening input stream"
    sys.exit(1)
if not vidFile.isOpened():
    print "capture stream not open"
    sys.exit(1)

nFrames = int(vidFile.get(7)) # one good way of namespacing legacy openCV: cv2.cv.*
print "frame number: %s" %nFrames
fps = vidFile.get(5)
print "FPS value: %s" %fps

ret, frame = vidFile.read() # read first frame, and the return code of the function.
while ret:  # note that we don't have to use frame number here, we could read from a live written file.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_white = np.array([250,250,250])
    upper_white = np.array([255,255,255])

    mask = cv2.inRange(hsv, lower_white, upper_white)

    res = cv2.bitwise_and(frame,frame, mask=mask)

    cv2.imshow("frameWindow", hsv)
    cv2.waitKey(int(1/fps*1000)) # time to wait between frames, in mSec was 1000
    ret, frame = vidFile.read() # read next frame, get next return code
