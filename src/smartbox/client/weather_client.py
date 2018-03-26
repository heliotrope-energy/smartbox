#!/usr/bin/env python
from smartbox_msgs import weather_pb2
from smartbox_msgs import weather_pb2_grpc

class WeatherClient:
	def __init__(self, channel):
		self.channel = channel
		self.stub = weather_pb2_grpc.WeatherControllerStub(self.channel)

	def get_weather(self):
		"""
			Returns the message as a protobuf message. Check smartbox_msgs 
			for message details
		"""
		return self._request_weather_()

	def _request_weather_(self):
		request = weather_pb2.WeatherRequest()
		return self.stub.weather_report(request)