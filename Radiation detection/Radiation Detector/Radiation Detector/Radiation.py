import cv2
import numpy
import logging
from multiprocessing import Queue
import threading
import time

class Radiation :

    def __init__(self) :
        # logging creation
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='[%d/%m/%y - %H:%M:%S]')
        self.logger = logging.getLogger(__name__)

        # stream variables
        self.stream = None
        self.baseMask = None
        self.correctedFrame = None
        self.lastFrame = None

        self.width = 320
        self.height = 640

        # multiprocessing variable two image enters in -> one out
        self.inputQueue = Queue(maxsize=1)
        self.outputQueue = Queue(maxsize=1)

        # radiation level init
        self.radiationLevel = 0

    #
    #   calibrating stream for no radiation level
    #
    def calibrateWithoutRadiation(self) :
        """Taking one picture and add a black mask on it"""
        if self.stream.isOpened() :
            self.logger.debug("Stream is up : calibrating...")
            ret, frame = self.stream.read()
            if ret :
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.baseMask = frame
                self.logger.debug("Calibration done !")
                return 0
            else :
                self.logger.error("Calibration failed ret is not correct")
                self.calibrateWithoutRadiation()
                return 1
        else :
            self.logger.warn("Stream is NOT Opened")
            return 1

    def calibrateWithRadiation(self, level) :
        """Calibration function"""
        if self.stream.isOpened() :
            ret, frame = self.stream.read()
            if ret :
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.logger.debug("Calibration done with radiation !")
                return 0
            else :
                self.logger.error("Calibration with radiation failed : ret is not correct")
                self.calibrateWithRadiation(level)
                return 1
        else :
            return 1

    def mse(self, imageA, imageB):
	    # the 'Mean Squared Error' between the two images is the
	    # sum of the squared difference between the two images;
	    # NOTE: the two images must have the same dimension
        err = numpy.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])

        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err

    #
    #   processing radiation level from stream
    #
    def process(self) :
        """Processing radiation level from stream"""
        computedRad = None
        #self.calibrateWithoutRadiation()
        while True :
            if self.stream.isOpened() or self.stream is not None :
                ret, frame = self.stream.read()
            else :
                self.logger.error("Stream is NOT opened retrying")
                time.sleep(2)
                self.openStream()
                self.process()
                return 1

            if ret :
                self.logger.debug(frame)
                if self.inputQueue.empty() :
                    self.inputQueue.put(frame)

                thread = threading.Thread(target=self.computeRadiationLevel, args=(self.inputQueue, ))
                thread.deamon = True
                thread.start()
            else :
                pass

            if not self.outputQueue.empty() :
                computedRad = self.outputQueue.get()

            if computedRad is not None :
                self.radiationLevel = computedRad
                self.logger.debug("Computed radiation is :" + str(computedRad))
                cv2.putText(frame, "Radiation level is " + str(computedRad), (5, int(self.height - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
                cv2.imshow('Corrected', frame)

            if cv2.waitKey(1) >= 0:
                break
        cv2.destroyAllWindows()

    #
    #   Computing radiation level
    #
    def computeRadiationLevel(self, inQueue) :
        frame_1 = inQueue.get()
        frame_2 = self.lastFrame

        if frame_2 is None :
            frame_2 = self.baseMask

        self.logger.debug("Loading frame")

        if frame_1.shape > 2 :
            frame_1 = cv2.cvtColor(frame_1, cv2.COLOR_BGR2GRAY)
        # TODO: must find an other way to perform this shit
        #
        # INPUTQUEUE -> cv2.range() -> bitwise_xor() -> cv2.nonZero() -> OUTPUTQUEUE !
        #
        # 1. Correct the frame with a Range or brightnest and HSV (https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv) ?
        # 2. bitwise_xor between the calibrated image and captured one
        # 3. non-zero function applies to the single row matrix
        # Use a tensor flow ?

        # Comparing the two arrays for differences

        #self.logger.debug(frame_1)
        nonZero = cv2.countNonZero(frame_1)
        mseResult = self.mse(frame_1, frame_2)
        self.outputQueue.put(mseResult)
        return 0

    #
    # Picture function
    #
    def openPicture(self, path) :
        """Open a picture to process it"""
        frame = cv2.imread(path, flags=cv2.IMREAD_COLOR)
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = cv2.inRange(grayscale, numpy.array([100]), numpy.array([255]))
        cv2.imshow('Mask', mask)

        if cv2.waitKey(ord('q')) >= 0:
            pass

        numberOfWhiteDot = cv2.countNonZero(mask)

        return numberOfWhiteDot

    #
    # Video function
    #
    def openVideo(self, path) :
        try :
            self.stream = cv2.VideoCapture(path)
        except :
            self.logger.error("Error while opening video file")
        return 0

    #
    #   Stream functions
    #
    def openStream(self, streamNumber=0) :
        """Safely openning stream with VideoCapture"""
        try :
            self.stream = cv2.VideoCapture(streamNumber)
        except :
            self.logger.error("Error while starting video capture : Is device busy ?")
            return 1

        if self.stream.isOpened() :
            self.width = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
            self.height = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
            #self.stream.set(11, 10) # set brigthness to 0 -> creating bullshit STOPPING THAT NOW
            return 0
        else :
            self.logger.warn("Could not open stream : retrying...")
            self.openStream(streamNumber)
            return 1

    def closeStream(self) :
        if self.stream.isOpened() :
            self.stream.release()

if __name__ == '__main__' :
    r = Radiation()
    r.openVideo("beam.mp4")
    r.process()
