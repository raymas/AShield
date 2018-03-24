import cv2
import sys

try:
    vidFile = cv2.VideoCapture("beam.mp4")
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
    print "yes"
    cv2.imshow("frameWindow", frame)
    cv2.waitKey(int(1/fps*1000)) # time to wait between frames, in mSec
    ret, frame = vidFile.read() # read next frame, get next return code
