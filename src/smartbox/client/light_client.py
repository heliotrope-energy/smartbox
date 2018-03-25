#!/usr/bin/env python
import grpc, urllib3, cv2
import numpy as np

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc

class LightClient:
	def __init__(self, stub):
		self.stub = stub

	def get_light_status(self):
		request = smartbox_resource_controller_pb2.LightRequest()
		response = self.stub.set_light(request)
		status = response.status == smartbox_resource_controller_pb2.LightResponse.ON
		return status

	def set_light_status(self, turn_light_on):
		status = smartbox_resource_controller_pb2.LightRequest.ON if turn_light_on else smartbox_resource_controller_pb2.LightRequest.OFF
		request = smartbox_resource_controller_pb2.LightRequest(light = status)
		response = self.stub.set_light(request)
		status = response.status == smartbox_resource_controller_pb2.LightResponse.ON
		return status

	
