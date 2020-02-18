import cv2
import imutils


class MotionDetector:
    def __init__(self, accumWeight=0.5):

        # store the accumulated weight factor
        # The larger the value, the less significant the contribution of the old background when calculating the weighted average
        # The smaller the value, the greater the contribution (more older frames contribute to running average)"""
        self.accumWeight = accumWeight

        # initialize the background model
        self.bg = None

    def update(self, image):
        # initialize the background model if it is None
        if self.bg is None:
            self.bg = image.copy().astype("float")
            return

        # update the background model by accumulating the weighted average
        cv2.accumulateWeighted(image, self.bg, self.accumWeight)

    # Change tVal for better segmentation of skin from background
    def detect(self, image, tVal=75):
        """Compute the absolute difference between the background model and the image passed in. This leaves us
        with the Delta, which is used to find regions in the image that contain substantial variation in pixel
        value"""
        delta = cv2.absdiff(self.bg.astype("uint8"), image)
        thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]
        cv2.imshow("Thresh", thresh)

        # find contours in the thresholded image
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # if no contours found, means no motion detected
        if len(cnts) == 0:
            return None

        # otherwise we return the thresholded image and the largest contour in the cnts list
        return (thresh, max(cnts, key=cv2.contourArea))


