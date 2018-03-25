#!/usr/bin/env python
import grpc, urllib3, cv2
import numpy as np

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc

class ChargeControllerClient:
	def __init__(self, stub):
		self.stub = stub

	def get_battery_voltage(self):
		status = self._request_status_()
		return status.charge_controller.battery_voltage

	def get_solar_panel_voltage(self):
		status = self._request_status_()
		return status.charge_controller.array_voltage

	def get_load_voltage(self):
		status = self._request_status_()
		return status.charge_controller.load_voltage

	def get_charging_current(self):
		status = self._request_status_()
		return status.charge_controller.charge_current

	def get_load_current(self):
		status = self._request_status_()
		return status.charge_controller.load_current

	def get_charge_status(self):
		status = self._request_status_()
		return status.charge_controller.charge_state