#!/usr/bin/env python
import grpc, urllib3, cv2
import numpy as np

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc

class CameraClient:
	def __init__(self, stub):
		self.stub = stub

	
	def get_image(self):
		resp = self.http.request('GET', self.image_url)
		image = np.asarray(bytearray(resp.data), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)
		return image