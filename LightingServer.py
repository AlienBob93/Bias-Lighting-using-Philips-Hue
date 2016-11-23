#!/usr/bin/env python
#-*- coding:utf-8 -*-

import cv2
import time
import socket
import struct
import binascii
import json
import urllib2
import numpy as np
import webcolors as wc

# ifttt keys
IF_Key = 'sd65T1VEgqTJSl6TjGtv12' # add your key from the IFTTT maker channel
IF_trigger = 'https://maker.ifttt.com/trigger/lights/with/key/' + IF_Key	# trigger event url

# create socket
rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

#Number of frames to throw away while the camera adjusts to light levels
ramp_frames = 30

# camera port on RPi
camera_port = 0
camera = cv2.VideoCapture(camera_port)

# function to send the trigger url
def trigger_url(url, value1):

	data = '{ "value1" : "' + value1 + '", "value2" : "' + time.strftime("%H:%M") + '" }'
	req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    	f = urllib2.urlopen(req)
    	response = f.read()
    	f.close()

	return response

# Captures a single image from the camera and returns it in PIL format
def get_image():
	# read is the easiest way to get a full image out of a VideoCapture object.
	retval, im = camera.read()
	
	return im

	
# main

# Ramp the camera - these frames will be discarded and are only used to allow v4l2
# to adjust light levels, if necessary
flag = 1
for i in xrange(ramp_frames):
	temp = get_image()	
try:
	while flag:
		# capture image for processing
		camera_capture = get_image()

		# crop from top left (240, 230) till bottom right (385, 300)
		cropped_capture = camera_capture[230:300, 240:385]

		#r, g, b = cv2.split(cropped_capture)
		b, g, r = cv2.split(cropped_capture)
		avg_b = b.mean()
		avg_g = g.mean()
		avg_r = r.mean()
		print "avg_b = " + str(int(round(avg_b, -1))) + "\navg_g = " + str(int(round(avg_g, -1))) + "\navg_r = " + str(int(round(avg_r, -1))) + "\n"

		RGB_BiasColor = max(avg_r, max(avg_g, avg_b))
		if RGB_BiasColor == avg_r:
			avg_r = 255#avg_r
			avg_g = 0
			avg_b = 0
		elif RGB_BiasColor == avg_g:
			avg_r = 0
			avg_g = 255#avg_g
			avg_b = 0
		elif RGB_BiasColor == avg_b:
			avg_r = 0
			avg_g = 0
			avg_b = 255#avg_b
		BiasColor = wc.rgb_to_hex((avg_r, avg_g, avg_b))
		print "HEX COLOR = " + BiasColor + "\n"
		
		print "calling trigger " + trigger_url(IF_trigger, BiasColor) + "\n"
		#flag = 0
	
		# sample time in seconds
		time.sleep(10)
		
except KeyboardInterrupt:
	print 'interrupted!'
	del(camera)
