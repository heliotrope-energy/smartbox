#!/usr/bin/env python
from smartbox_msgs import tracker_pb2
from smartbox_msgs import tracker_pb2_grpc
from smartbox.client.tracker_controller import TrackerController

import time
from threading import Thread
from queue import Queue
from collections import namedtuple

class TrackerClient:
	def __init__(self, channel, authority_level, description):
		self.channel = channel
		self.authority_level = authority_level
		self.description = description
		self.stub = tracker_pb2_grpc.TrackerControllerStub(self.channel)
		
	def request_control(self):
		"""
			Request control of the tracker for movement. This returns a context manager for your pythonic convenience.
			It throws an exception if your client can't get, or loses tracker control.

			with client.request_control() as control:
				control.move_north()

			params:
				control_success_cb: A callback for your program to understand if control is gained.
				control_termination_cb: A callback for your program to understand when control is lost, 
					which might be immediately.
				cb_args: Arguments provided to both callbacks

		"""

		return TrackerController(self.stub, self.authority_level, self.description)

	def is_control_possible(self):
		"""
			This will check the server to see if there is a controlling client with more authority than your client
		"""
		status = self._request_status_()
		if status.tracker.controlling_authority == -1:
			return True
		if status.tracker.controlling_authority > self.authority_level:
			return True
		return False

	def tracker_status(self, callback):
		self.tracker_status_thread = Thread(target = self._tracker_status_, \
			args=(callback,))

	def _tracker_status_(self, callback):
		for status in self.stub.tracker_status(tracker_pb2.TrackerSystemStatusRequest()):
			callback(status)

	def get_ns_position(self):
		"""
			Returns the position in inches of the North-South Actuator
		"""
		msg = self._request_status_()
		return msg.tracker.position.ns

	def get_ew_position(self):
		"""
			Returns the position in inches of the East-West Actuator
		"""
		msg = self._request_status_()
		return msg.tracker.position.ew

	def get_ns_angle(self):
		"""
			Returns the position in degrees of the North-south direction
		"""
		msg = self._request_status_()
		return msg.tracker.angle.ns

	def get_ew_angle(self):
		"""
			Returns the position in degrees of the East-West direction
		"""
		msg = self._request_status_()
		return msg.tracker.angle.ew

	def get_ns_limits(self):
		"""
			Returns safe limits of NS actuator
		"""
		return [0.0, 6.0]

	def get_ew_limits(self):
		"""
			Returns safe limits of the EW actuator
		"""
		return [0.0, 12.0]

	def is_panel_moving(self):
		"""
			Returns whether the panel is moving in either direction
		"""
		msg = self._request_status_()
		return msg.tracker.move_status.ns or msg.tracker.move_status.ew

	def is_ns_moving(self):
		"""
			Returns whether the panel is moving in the NS direction
		"""
		msg = self._request_status_()
		return msg.tracker.move_status.ns

	def is_ew_moving(self):
		"""
			Returns whether the panel is moving in the EW diretion
		"""
		msg = self._request_status_()
		return msg.tracker.move_status.ew

	def get_battery_voltage(self):
		"""
			Gets the current battery voltage as measured by the charge controller
		"""
		status = self._request_status_()
		return status.charge_controller.battery_voltage

	def get_solar_panel_voltage(self):
		"""
			Gets the current solar panel array voltage as measured by the charge controller
		"""
		status = self._request_status_()
		return status.charge_controller.array_voltage

	def get_load_voltage(self):
		"""
			Gets the current voltage applied to the load as measured by the charge controller
		"""
		status = self._request_status_()
		return status.charge_controller.load_voltage

	def get_charging_current(self):
		"""
			Gets the amount of current that is charging the battery
		"""
		status = self._request_status_()
		return status.charge_controller.charge_current

	def get_load_current(self):
		"""
			Gets the amount of current applied to the load
		"""
		status = self._request_status_()
		return status.charge_controller.load_current

	def get_charge_status(self):
		"""	
			Gets the current status of the charge controller. Check the smartbox_msgs
			for enum details.
		"""
		status = self._request_status_()
		return status.charge_controller.charge_state

	def get_charge_state_name(self):
		status = self._request_status_()
		state = status.charge_controller.charge_state
		return tracker_pb2.Name(state)

	def get_tracker_data(self):
		"""
			Returns the complete status message of the tracker. Check the smartbox_msgs
			for message details.
		"""
		return self._request_status_()

	def _request_status_(self):
		request = tracker_pb2.TrackerSystemStatusRequest()
		return self.stub.get_tracker_status(request)

	
