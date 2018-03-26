#!/usr/bin/env python
import temperature_pb2
import temperature_pb2_grpc

class PanelTemperatureClient:
	def __init__(self, channel):
		self.channel = channel
		self.stub = temperature_pb2_grpc.TemperatureControllerStub(self.channel)

	def _request_panel_temperatures_(self):
		request = temperature_pb2.PanelTemperatureRequest()
		return self.stub.panel_temperature(request)