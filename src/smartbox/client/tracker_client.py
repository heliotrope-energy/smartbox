#!/usr/bin/env python
from smartbox_msgs import tracker_pb2
from smartbox_msgs import tracker_pb2_grpc

import time
from threading import Thread
from queue import Queue

class TrackerClient:
	def __init__(self, channel, authority_level):
		self.channel = channel
		self.authority_level = authority_level
		self.stub = tracker_pb2_grpc.TrackerControllerStub(self.channel)
		self.retain_control = False

	def request_control(self, control_success_cb = None, control_termination_cb = None, cb_args=None):
		"""
			Request control of the tracker for movement. Call this method to get the server to recognize 
			your program's control. If you don't call this method, it will be done for you when you call
			a movement method, but those will fail silently if you can't get control.

			params:
				control_success_cb: A callback for your program to understand if control is gained.
				control_termination_cb: A callback for your program to understand when control is lost, 
					which might be immediately.
				cb_args: Arguments provided to both callbacks

		"""
		self.control_thread = Thread(target = self._tracker_control_, args=(control_success_cb, control_termination_cb, cb_args,))
		self.control_requests_queue = Queue()
		self.retain_control = True
		self.control_thread.start()
		
		#resp = self._request_control_()
		#return resp.success == tracker_pb2.SUCCESS

	def relinquish_control(self):
		"""
			Relinquishes control of the tracker. Be a polite user and please relinquish. It will be done
			for you by the server when the connection closes (i.e. when your program exits).

			returns: True if request was success, which it should always be
		"""
		self.retain_control = False
		
		# resp = self._relinquish_control_()
		# return resp.success == tracker_pb2.SUCCESS

	def tracker_status(callback):
		for status in self.stub.TrackerStatus(tracker_pb2.TrackerSystemStatusRequest()):
			callback(status)

	def _is_ok_(self):
		return True

	def _retain_control_(self):
		return self.retain_control

	def _tracker_control_(self, connection_cb, termination_cb, cb_args):
		class ControlIterator:
			def __init__(self, client):
				self.client = client

			def __iter__(self):
				return self

			def __next__(self):
				if self.client._is_ok_() and self.client._retain_control_()
					if self.client.control_requests_queue.empty():
						time.sleep(0.05)
					else:
						yield self.client.control_requests_queue.get()
				else raise StopIteration()

		control_iterator = ControlIterator(self)
		connection_success = False
		for response in self.stub.TrackerControl(control_iterator):
			if response.success == tracker_pb2.SUCCESS and not connection_success:
				connection_success = True
				connection_cb(*cb_args)

		self.retain_control = False
		if termination_cb is not None:
			termination_cb(*cb_args)
		#return self.stub.request_control(request)

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

	def move_panel_to_linear_position(self, ns_pos, ew_pos):
		"""
			Moves the panel to given linear actuator positions
			Params:
				ns_pos: The north-south position in inches from full-retraction
				ew_pos: The east-west position in inches from full-retraction
		"""
		if not self._retain_control_():
			self.request_control(self._request_position_move_, args = (ns_pos, ew_pos))
		else:		
			self._request_position_move_(ns_pos, ew_pos)

	def move_panel_to_angular_position(self, ns_angle, ew_angle):
		"""
			TODO
			Moves the panel to the given North-South and East-West angles
			Params:
				ns_angle: The angle to move the panel from the north-south axis.
						  North is positive
				ew_angle: The angle to move the panel from the east-west axis.
						  West is positive
		"""
		if not self._retain_control_():
			self.request_control(self._request_angular_move_, args = (ns_angle, ew_angle))
		else:
			self._request_angular_move_(ns_angle, ew_angle)

		
	def stow(self):
		"""
			Moves the panel to a safe wind-stow position
		"""
		if not self._retain_control_():
			self.request_control(self._stow_)
		else:
			self._stow_()

	def move_north(self):
		"""
			Moves the panel to face north. Call stop_ns() or stop() to stop 
			the movement
		"""
		if not self._retain_control_():
			self.request_control(self._request_direction_move_, args = (tracker_pb2.NORTH))
		else:
			self._request_direction_move_(direction=tracker_pb2.NORTH)
		

	def move_south(self):
		"""
			Moves the panel to face south. Call stop_ns() or stop() to stop 
			the movement
		"""

		if not self._retain_control_():
			self.request_control(self._request_direction_move_, args = (tracker_pb2.SOUTH))
		else:
			self._request_direction_move_(direction=tracker_pb2.SOUTH)
		
	def move_east(self):
		"""
			Moves the panel to face east. Call stop_ew() or stop() to stop 
			the movement
		"""
		if not self._retain_control_():
			self.request_control(self._request_direction_move_, args = (tracker_pb2.EAST))
		else:
			self._request_direction_move_(direction=tracker_pb2.EAST)
		
	def move_west(self):
		"""
			Moves the panel to face west. Call stop_ew() or stop() to stop 
			the movement
		"""
		if not self._retain_control_():
			self.request_control(self._request_direction_move_, args = (tracker_pb2.WEST))
		else:
			self._request_direction_move_(direction=tracker_pb2.WEST)

	def stop(self):
		"""
			Stops the movement of both axes
		"""
		if not self._retain_control_():
			self.request_control(self._stop_)
		else:
			self._stop_()

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

	def get_tracker_data(self):
		"""
			Returns the complete status message of the tracker. Check the smartbox_msgs
			for message details.
		"""
		return self._request_status_()

	def _stow_(self):
		request = tracker_pb2.StowRequest(message="Flat please")
		self.stub.stow(request)

	def _stop_(self):
		request = tracker_pb2.StopRequest(message="stop")
		self.stub.stop(request)

	def _request_status_(self):
		request = tracker_pb2.TrackerSystemStatusRequest(message = "hello")
		return self.stub.get_tracker_status(request)

	def _request_control_(self):
		request = tracker_pb2.RequestControlRequest(message="Control please", security_level = self.security_level)
		return self.stub.request_control(request)

	def _relinquish_control_(self):
		request = tracker_pb2.RelinquishControl(message="All done")
		return self.stub.request_control(request)

	def _request_direction_move_(self, direction):
		request = tracker_pb2.MoveRequest(move_type = tracker_pb2.MoveRequest.DURATION)
		request.direction = direction
		return self.stub.move_panel(request)

	def _request_position_move_(self, pos_ns, pos_ew):
		request = tracker_pb2.MoveRequest(move_type = tracker_pb2.MoveRequest.POSITION)
		request.position.ns = pos_ns
		request.position.ew = pos_ew
		return self.stub.move_panel(request)

	def _request_angular_move_(self, angle_ns, angle_ew):
		request = tracker_pb2.MoveRequest(move_type = tracker_pb2.MoveRequest.ANGLE)
		request.angle.ns = angle_ns
		request.angle.ew = angle_ew
		return self.stub.move_panel(request)
