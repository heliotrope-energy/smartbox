#!/usr/bin/env python
from queue import Queue
from concurrent import futures
import time

import grpc

from smartbox.sb_tracker import SmartBoxTracker
from smartbox.sb_charge_controller import SmartBoxChargeController

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class SmartBoxResourceController(smartbox_resource_controller_pb2_grpc.SmartBoxResourceControllerServicer):
	accumulated_energy_at_control_start = 0.0
	controlling_security_level = -1
	security_level_queue = Queue()

	def __init__(self):
		self.charge_controller = SmartBoxChargeController()
		self.tracker_controller = SmartBoxTracker()
		self.energy_collected_at_start = 0.0
		self.energy_collected_at_current_time = 0.0
		self.energy_expended_at_start = 0.0
		self.energy_expended_at_current_time = 0.0

	def get_tracker_status(self, request, context):
		return self._get_tracker_status_message_()

	def request_control(self, request, context):
		if self.controlling_security_level == -1:
			self.controlling_security_level = request.security_level
			return smartbox_resource_controller_pb2.RequestControlResponse(message="Success")
		elif request.security_level < self.controlling_security_level:
			self.security_level_queue.put(self.controlling_security_level)
			self.controlling_security_level = request.security_level
			return smartbox_resource_controller_pb2.RequestControlResponse(message="Success")
		elif request.security_level >= self.controlling_security_level:
			return smartbox_resource_controller_pb2.RequestControlResponse(message="Failure", why_failure_id=smartbox_resource_controller_pb2.RequestControlResponse.INSUFFICIENT_SECURITY_LEVEL)

	def relinquish_control(self, request, context):
		self.controlling_security_level = -1
		return smartbox_resource_controller_pb2.RequestControlResponse(message="Success")

	def move_panel(self, request, context):
		move_type = request.move_type
		if move_type == smartbox_resource_controller_pb2.MoveRequest.DURATION:
			direction = request.direction
			if direction == smartbox_resource_controller_pb2.NORTH:
				self.tracker_controller.move_north()
			elif direction == smartbox_resource_controller_pb2.SOUTH:
				self.tracker_controller.move_south()
			elif direction == smartbox_resource_controller_pb2.EAST:
				self.tracker_controller.move_east()
			elif direction == smartbox_resource_controller_pb2.WEST:
				self.tracker_controller.move_west()

		elif move_type == smartbox_resource_controller_pb2.MoveRequest.POSITION:
			ns_position = request.position.ns
			ew_position = request.position.ew
			self.tracker_controller.move_panel_to_linear_position(ns_position, ew_position)
		elif move_type == smartbox_resource_controller_pb2.MoveRequest.ANGLE:
			ns_angle = request.angle.ns
			ew_angle = request.angle.ew
			self.tracker_controller.move_panel_to_angular_position(ns_angle, ew_angle)
		return smartbox_resource_controller_pb2.MoveResponse()


	def stop(self, request, context):
		self.tracker_controller.stop()
		return smartbox_resource_controller_pb2.StopResponse(message="Success")

	def stow(self, request, context):
		self.tracker_controller.stow()
		return smartbox_resource_controller_pb2.StowResponse(message="Success")

	def _get_tracker_status_message_(self):
		response = smartbox_resource_controller_pb2.TrackerSystemStatusResponse()
		_, charge_data = self.charge_controller.get_all_data()

		response.tracker.position.ns = self.tracker_controller.get_ns_position()
		response.tracker.position.ew = self.tracker_controller.get_ew_position()
		response.tracker.angle.ns = self.tracker_controller.get_ns_angle()
		response.tracker.angle.ew = self.tracker_controller.get_ew_angle()
		response.tracker.move_status.ns= self.tracker_controller.is_ns_moving()
		response.tracker.move_status.ns = self.tracker_controller.is_ew_moving()
		response.tracker.current_controlling_level = self.controlling_security_level

		response.charge_controller.battery_voltage = charge_data[SmartBoxChargeController.ADC_VB_F]
		response.charge_controller.array_voltage = charge_data[SmartBoxChargeController.ADC_VA_F]
		response.charge_controller.load_voltage = charge_data[SmartBoxChargeController.ADC_VL_F]
		response.charge_controller.charge_current = charge_data[SmartBoxChargeController.ADC_IC_F]
		response.charge_controller.load_current = charge_data[SmartBoxChargeController.ADC_IL_F]
		response.charge_controller.charge_state = charge_data[SmartBoxChargeController.CHARGE_STATE]
		response.charge_controller.energy_collected = self.energy_collected_at_current_time - \
			self.energy_collected_at_start
		response.charge_controller.energy_expended = self.energy_expended_at_current_time	- \
			self.energy_expended_at_start

		return response
				

	

def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	smartbox_resource_controller_pb2_grpc.add_SmartBoxResourceControllerServicer_to_server(SmartBoxResourceController(), server)
	server.add_insecure_port('[::]:50051')
	server.start()
	print("Starting resource controller server")
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)
	except KeyboardInterrupt:
		server.stop(0)


if __name__ == '__main__':
	serve()


