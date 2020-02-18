# HandGesture-Universal-Robots
Controlling a UR5 Robot based on Hand Gestures

## Background
The [Universal Robots'](https://www.universal-robots.com/) Collaborative robot is widely used in various industries ranging from manufacturing, medical, retail, etc. It is known to be user-friendly in terms of programming ease and its in-built safety features.

It supports common communication protocols such as TCP/IP, PROFINET and EtherNet IP, which allows it to communicate with other peripheral devices and perform operations based on sent instructions over these protocols.

The code in this repository is meant to be a fun way to prove the ability of the Universal Robot to perform operations based on instructions sent over the TCP/IP from a python code on a Windows laptop. In this case, moving the robot based on hand gestures recognized from the python codes in this repository. 

## Required Packages
You will need these Python packages to proceed:
  * threading
  * numpy
  * imutils
  * cv2
  * socket
  * time
  * sklearn

## Required Hardware
 * USB webcam
 * Laptop / PC / RaspberryPi
 * Universal Robots
 * Black background (recommended for better segmentation of hand and fingers in captured image)

## Description of Files

  * `recognize_and_draw.py` : contains the code to update the Universal Robot's MODBUS registers based on the recognized hand gestures. Imports the `MotionDetector` and `GestureDetector` classes.
  * `motiondetector.py` : `MotionDetector` class that detects motion within a specified region of interest
  * `gesturedetector.py` : `GestureDetector` class that counts the number of fingers in the specified region of interest when motion is detected

## Instructions of Usage

*Details on how to set up modbus registers and establish a connection between the laptop and robot controller will not be discussed here as I assume you have a working knowledge on the Universal Robot.*

It is recommended to have all 3 files in the same directory

First, in the `recognize_and_draw.py` file, modify the socket send addresses in the `get_register_##` and `set_register_##` functions,  where '##' is the MODBUS register number set in the UR PolyScope software:

`c.send(b"\x00\x04\x00\x00\x00\x06\x00\x03\x00\xC8\x00\x01")`

Register addresses take up the last 2 bytes in this send string, in ASCII format. Be sure to use the correct ASCII code for read/write modes.

Next, in these read/write functions, ensure that the ip address reflects that of your robot:

`host = "192.168.1.125"`

In this case, the IP address of my robot is '192.168.1.125'. Ensure that the IP address of your machine hosting this python code is in the same subnet.

Finally, run the `recognize_and_draw.py` file. Face the connected webcam and start your hand gestures.

## Parameters to Modify

### `recognize_and_draw.py`
  * `host` and `port` variables 
  * MODBUS command strings
  
### `motiondetector.py`
  * `accumWeight`: default value of 0.5. Defined in the `__init__` function. The larger the value, the less significant the contribution of the old background when calculating the weighted average. The smaller the value, the greater the contribution (more older frames contribute to running average)
  * `tVal`: default value of 75. Defined within the `detect` function. Change it for better segmentation of skin from background.
  
### `gesturedetector.py`
  * `r = int(0.7*maxDist)` (Line 30): Consider to modify the radius factor to suit the size of your hand


## Acknowledgements
Special thanks to Adrian Rosebrock, author and owner of the [PyImageSearch](https://www.pyimagesearch.com/) blog, for providing the motivation behind the motion detector and hand gesture detector codes.
