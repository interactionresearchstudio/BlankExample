#!/usr/bin/env python
import cv2
import json
import time
import datetime
import os

# pi specific imports
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
# end of imports

# load configuration file
os.chdir("/home/pi/BlankExample")
config = json.load(open("config.json"))

cv2.namedWindow("Output", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Output", cv2.WND_PROP_FULLSCREEN, 1)

# camera
camera = PiCamera()
camera.resolution = (2592,1944)
camera.framerate = 32
hiResCapture = PiRGBArray(camera, size=(2592,1944))
rawCapture = PiRGBArray(camera, size=(320,240))
hiResStream = camera.capture_continuous(hiResCapture, format="bgr", use_video_port=True, splitter_port=1, resize=(2592,1944))
lowResStream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True, splitter_port=2, resize=(320,240))

time.sleep(config["camera_warmup"])

# buttons
btn1 = 17
btn2 = 22
btn3 = 23
btn4 = 27
btnShutter = btn1
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(btn1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn3, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn4, GPIO.IN, GPIO.PUD_UP)

def takePhoto(image):
    timestamp = datetime.datetime.now()
    filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    filename = filename + ".jpg"
    cv2.imwrite(filename, image)

# main loop
#for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True, splitter_port=2, resize=(320,240)):
while True:
    # get new frame
    #image = frame.array
    lrs = lowResStream.next()
    image = lrs.array
    rawCapture.truncate(0)

    hrs = hiResStream.next()
    hiresImage = hrs.array
    hiResCapture.truncate(0)
    # end of new frame

    cv2.imshow("Output", image)

    if GPIO.input(btnShutter) == False:
        takePhoto(hiresImage)
        time.sleep(0.5)

    # clear buffer
    key = cv2.waitKey(10)
    # end of loop

# cleanup
cv2.destroyWindow("Output")
