#!/usr/bin/env python
from smartbox_msgs import image_pb2
from smartbox_msgs import image_pb2_grpc

import cv2
import numpy as np

# from smartbox_msgs import camera_pb2
# from smartbox_msgs import camera_pb2_grpc

class CameraClient:
	def __init__(self, channel):
		self.channel = channel
		self.stub = image_pb2_grpc.CameraControllerStub(self.channel)
		
	def get_image(self):
		"""
			Gets the current image from the tracker. If for some reason the images
			are stale, this method will return a None.
		"""
		msg = self.stub.get_current_image(image_pb2.CameraImageRequest())
		nparr = np.fromstring(msg.data, np.uint8)
		image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
		return image