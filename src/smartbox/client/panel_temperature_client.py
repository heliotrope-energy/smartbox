#!/usr/bin/env python
import grpc, urllib3, cv2
import numpy as np

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc

class PanelTemperaturesClient:
	def __init__(self, stub):
		self.stub = stub

	def _request_panel_temperatures_(self):
		request = smartbox_resource_controller_pb2.PanelTemperatureRequest()
		return self.stub.panel_temperature(request)