#!/usr/bin/env python
import grpc, urllib3, cv2
import numpy as np

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc

class WeatherClient:
	def __init__(self, stub):
		self.stub = stub

	def get_weather(self):
		return self._request_weather_()

	def _request_weather_(self):
		request = smartbox_resource_controller_pb2.WeatherRequest()
		return self.stub.weather_report(request)