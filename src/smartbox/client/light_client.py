#!/usr/bin/env python
from smartbox_msgs import lights_pb2
from smartbox_msgs import lights_pb2_grpc

class LightClient:
	def __init__(self, channel):
		self.channel = channel
		self.stub = lights_pb2_grpc.LightControllerStub(channel)

	def get_light_status(self):
		request = light_pb2.LightRequest()
		response = self.stub.set_light(request)
		status = response.status == light_pb2.LightResponse.ON
		return status

	def set_light_status(self, turn_light_on):
		status = light_pb2.LightRequest.ON if turn_light_on else light_pb2.LightRequest.OFF
		request = light_pb2.LightRequest(light = status)
		response = self.stub.set_light(request)
		status = response.status == light_pb2.LightResponse.ON
		return status

	
