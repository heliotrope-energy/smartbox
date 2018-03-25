#!/usr/bin/env python
import urllib3, cv2
import numpy as np

import camera_pb2
import camera_pb2_grpc

class CameraClient:
	def __init__(self, channel):
		self.channel = channel
		self.stub = camera_pb2_grpc.CameraControllerStub(self.channel)
		self.http = urllib3.PoolManager()
		self.image_url = "http://138.16.161.117/images/image.png"
		


	
	def get_image(self):
		resp = self.http.request('GET', self.image_url)
		image = np.asarray(bytearray(resp.data), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)
		return image