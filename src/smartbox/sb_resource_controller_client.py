#!/usr/bin/env python
import grpc

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc

class SmartBoxResourceControllerClient():
	def __init__(self, security_level):
		self.channel = grpc.insecure_channel('138.16.161.117:50051')
		self.stub = smartbox_resource_controller_pb2_grpc.SmartBoxResourceControllerStub(self.channel)
		self.security_level = security_level

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
			TODO
			Returns the position in degrees of the North-south direction
		"""
		msg = self._request_status_()
		return msg.tracker.angle.ns

	def get_ew_angle(self):
		"""
			TODO
			Returns the position in degrees of the East-West direction
		"""
		msg = self._request_status_()
		return msg.tracker.angle.ew

	def get_ns_limits(self):
		"""
			TODO
		"""
		return [0.0, 6.0]

	def get_ew_limits(self):
		"""
			TODO
		"""
		return [0.0, 12.0]

	def is_panel_moving(self):
		"""
			TODO
			Returns status of 
		"""
		msg = self._request_status_()
		return msg.tracker.move_status.ns or msg.tracker.move_status.ew

	def is_ns_moving(self):
		"""

		"""
		msg = self._request_status_()
		return msg.tracker.move_status.ns

	def is_ew_moving(self):
		"""

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
		self._request_angular_move_(ns_angle, ew_angle)

	def stow(self):
		"""
			Moves the panel to a safe wind-stow position
		"""
		request = smartbox_resource_controller_pb2.StowRequest(message="Flat please")
		self.stub.stow(request)

	def move_north(self):
		"""
			Moves the panel to face north. Call stop_ns() or stop() to stop 
			the movement
		"""
		self._request_direction_move_(direction=smartbox_resource_controller_pb2.MovePanelRequest.NORTH)
		

	def move_south(self):
		"""
			Moves the panel to face south. Call stop_ns() or stop() to stop 
			the movement
		"""

		self._request_direction_move_(direction=smartbox_resource_controller_pb2.MovePanelRequest.SOUTH)
		
	def move_east(self):
		"""
			Moves the panel to face east. Call stop_ew() or stop() to stop 
			the movement
		"""
		self._request_direction_move_(direction=smartbox_resource_controller_pb2.MovePanelRequest.EAST)
		
	def move_west(self):
		"""
			Moves the panel to face west. Call stop_ew() or stop() to stop 
			the movement
		"""
		self._request_direction_move_(direction=smartbox_resource_controller_pb2.MovePanelRequest.WEST)

	def stop(self):
		"""
			Stops the movement of both axes
		"""
		request = smartbox_resource_controller_pb2.StopRequest(message="stop")
		self.stub.stop(request)

	def get_light_status(self):
		request = smartbox_resource_controller_pb2.StopRequest()
		response = self.stub.stop(request)
		status = response.status == smartbox_resource_controller_pb2.LightResponse.ON
		return status

	def set_light_status(self, turn_light_on):
		status = smartbox_resource_controller_pb2.LightRequest.ON if turn_light_on else smartbox_resource_controller_pb2.LightRequest.OFF
		request = smartbox_resource_controller_pb2.StopRequest(light = status)
		response = self.stub.stop(request)
		status = response.status == smartbox_resource_controller_pb2.LightResponse.ON
		return status

	def _request_status_(self):
		request = smartbox_resource_controller_pb2.TrackerSystemStatusRequest(message = "hello")
		return self.stub.get_tracker_status(request)

	def _request_control_(self):
		request = smartbox_resource_controller_pb2.RequestControlRequest(message="Control please", security_level = self.security_level)
		return self.stub.request_control(request)

	def _relinquish_control_(self):
		request = smartbox_resource_controller_pb2.RelinquishControl(message="All done")
		return self.stub.request_control(request)

	def _request_direction_move_(self, direction):
		request = smartbox_resource_controller_pb2.MoveRequest(move_type = smartbox_resource_controller_pb2.MoveRequest.DIRECTION)
		request.direction = direction
		return self.stub.move_panel(request)

	def _request_position_move_(self, pos_ns, pos_ew):
		request = smartbox_resource_controller_pb2.MoveRequest(move_type = smartbox_resource_controller_pb2.MoveRequest.POSITION)
		request.position.ns = pos_ns
		request.position.ew = pos_ew
		return self.stub.move_panel(request)

	def _request_angular_move_(self, angle_ns, angle_ew):
		request = smartbox_resource_controller_pb2.MoveRequest(move_type = smartbox_resource_controller_pb2.MoveRequest.ANGLE)
		request.angle.ns = angle_ns
		request.angle.ew = angle_ew
		return self.stub.move_panel(request)

if __name__ == "__main__":
	client = SmartBoxResourceControllerClient(101)
	print(client.get_ns_position())
	print(client.get_ew_position())
	print(client.get_ew_angle())
	print(client.get_ew_angle())
	print(client.is_ew_moving())
	print(client.is_ns_moving())
	print(client.move_panel_to_linear_position(0.0, 0.0))
	print(client.move_panel_to_angular_position(0.0, 0.0))
	print(client.stow())
	print(client.stop())
	print(client.get_light_status())
	print(client.set_light_status(True))
	print(client.get_light_status())
	print(client.set_light_status(False))
	print(client.get_light_status())
	




