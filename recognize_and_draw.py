from gesturedetector import GestureDetector
from motiondetector import MotionDetector
import threading
import numpy as np
import imutils
import cv2
import socket
import time


check_stopped = None
# 5 cols by 3 rows
row_count = 0
col_count = 0

has_robot_stopped = threading.Event()

bounding_box = "10, 370, 225, 600"

# Grab the reference to the webcam
camera = cv2.VideoCapture(0)

# unpack the hand ROI, then initialize the motion detector and gesture detector
(top, right, bot, left) = np.int32(bounding_box.split(","))
gd = GestureDetector()
md = MotionDetector()

# initialize the total number of frames read thus far, a bookkeeping variable used to
# keep track of the number of consecutive frames a gesture has appeared in, along
# with the values recognized by the gesture detector
numFrames = 0
gesture = None
# values list to keep track of previous recognized gestures
values = []
# init number of recognized digits
digits = -1
# initialize moves played
cell_list = []

reg_200_i = 1

# get the value stored in MODBUS register 200 of the UR Controller
def get_register_200():

    global reg_200_i

    while True:
        try:
            host = "192.168.1.125"
            port = 502
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c.connect((host, port))

            # pause script, and loop until reg_200 is 0 (robot has finished drawing and moved to home)
            while reg_200_i == 1:
                c.send(b"\x00\x04\x00\x00\x00\x06\x00\x03\x00\xC8\x00\x01")
                reg_200_i = c.recv(256)
                reg_200_i = reg_200_i.replace(b"\x00\x04\x00\x00\x00\x05\x00\x03\x02", b"")
                reg_200_i = int(reg_200_i.hex(), 16)

            break
        except:
            continue

    # then, set the flag so that we can continue with the video capture
    if reg_200_i == 0:
        has_robot_stopped.set()


# Set register 202 to 1 to get robot moving
def set_register_202_high():
    while True:
        try:
            host = "192.168.1.125"
            port = 502
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c.connect((host, port))

            c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xCA\x00\x01")
            time.sleep(0.5)

            break
        except:
            continue

# Set register 202 to 0 to get robot to wait (stop)
def set_register_202_low():
    while True:
        try:
            host = "192.168.1.125"
            port = 502
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c.connect((host, port))

            c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xCA\x00\x00")
            time.sleep(0.5)

            break
        except:
            continue


# Set register 201 to the value recognized by the hand gesture algorithm
def set_register_201(digit):

    while True:
        try:
            host = "192.168.1.125"
            port = 502
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c.connect((host, port))
            # print(digit)

            if digit == 1:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x01")
            elif digit == 2:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x02")
            elif digit == 3:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x03")
            elif digit == 4:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x04")
            elif digit == 5:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x05")
            elif digit == 6:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x06")
            elif digit == 7:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x07")
            elif digit == 8:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x08")
            elif digit == 9:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x09")
            else:
                c.send(b"\x00\x01\x00\x00\x00\x06\x00\x06\x00\xC9\x00\x00")

            time.sleep(0.5)
            print("Digit: {}".format(digit))

            break

        except:
            continue


set_register_202_low()
set_register_201(0)

while True:

    digits = -1
    (grabbed, frame) = camera.read()

    if grabbed:

        # resize the frame and flip
        frame = imutils.resize(frame, width=600)
        frame = cv2.flip(frame, 1)
        clone = frame.copy()
        (frameH, frameW) = frame.shape[:2]

        # extract the ROI, passing in right:left since the image is mirrored, then
        # blur it slightly
        roi = frame[top:bot, right:left]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # if we have not reached 32 initial frames, then calibrate the skin detector
        if numFrames < 32:
            md.update(gray)
        else:
            # detect motion, then hand (skin), then number of fingers
            skin = md.detect(gray)

            if skin is not None:
                (thresh, c) = skin
                cv2.drawContours(clone, [c + (right, top)], -1, (0, 255, 0), 2)

                # call the gesture detector to count the fingers
                num_fingers = gd.detect(thresh, c)

                # if the current gesture is None, initialize it
                if gesture is None:
                    gesture = [1, num_fingers]

                # otherwise, the finger count has already been initialized
                else:
                    if gesture[1] == num_fingers:
                        gesture[0] += 1

                        # if we have reached a sufficient number of consecutive frames,
                        # then it is implied that our detector has correctly recognized the
                        # number of fingers. Then, show number on screen
                        if gesture[0] > 45:
                            # if the values list (for arithmetic) is already full, reset it
                            if len(values) == 2:
                                values = []

                            # update the values list
                            values.append(num_fingers)
                            gesture = None

                    else:
                        # if the finger counts do not match the gesture, then reset the gesture bookeeping variable
                        gesture = None

            else:
                values = []
                digits = -1

    else:
        continue

    if len(values) > 0:
        # draw the first digit and the plus sign
        # GestureDetector.drawBox(clone, 0)
        GestureDetector.drawText(clone, 0, values[0])
        GestureDetector.drawText(clone, 1, "+")

    if len(values) == 2:
        digits = values[0] + values[1]
        # draw the second digit, the equal sign, and finally the answer
        GestureDetector.drawText(clone, 2, values[1])
        GestureDetector.drawText(clone, 3, "=")
        GestureDetector.drawText(clone, 4, "PROG ", color=(0, 255, 0))
        GestureDetector.drawText(clone, 6, digits, color=(0, 255, 0))

        if digits == 0 or digits == 10 or digits in cell_list:
            values = []
            print("Invalid digit {}, cell_list: {}".format(digits, cell_list))
            continue
        else:
            # set register 202 to high to initiate robot movement
            set_register_202_high()
            # set register 201 to send the cell location to the robot
            set_register_201(digits)
            print("GO ROBOT GO")

    # draw the hand ROI and increment the number of processed frames
    cv2.rectangle(clone, (left, top), (right, bot), (0, 0, 255), 2)
    numFrames += 1

    if digits > -1:

        # initialize the thread
        thread = threading.Thread(target=get_register_200())
        # start the background thread
        thread.start()
        # wait here for the robot to stop before continuing
        has_robot_stopped.wait()

        # update list of cells marked
        cell_list.append(digits)

        # reset values
        values = []
        digits = -1

        # stop robot
        set_register_202_low()

    # show the frame on our screen
    cv2.imshow("Frame", clone)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# clean up the camera and close any open windows
camera.release()
cv2.destroyAllWindows()