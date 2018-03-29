import copy, time, logging
from queue import Queue
from threading import Thread, RLock

from smartbox_msgs import tracker_pb2
from smartbox_msgs import tracker_pb2_grpc

from smartbox.components.sb_charge_controller import SmartBoxChargeController
from smartbox.components.sb_tracker import SmartBoxTracker

class SmartBoxTrackerController(tracker_pb2_grpc.TrackerControllerServicer):
	def __init__(self):
		self.charge_controller = SmartBoxChargeController()
		self.tracker_controller = SmartBoxTracker()
		self.energy_collected_at_start = 0.0
		self.energy_collected_at_current_time = 0.0
		self.energy_expended_at_start = 0.0
		self.energy_expended_at_current_time = 0.0
		self.charge_controller_poller = \
			Thread(target = self._get_charge_controller_data)
		self.charge_controller_poller.start()
		self.controlling_security_level = -1

		self.logger = logging.getLogger(__name__)
		self.charge_controller_lock = RLock()
		

	def get_tracker_status(self, request, context):
		return self._get_tracker_status_message_()

	def request_control(self, request, context):
		if self.controlling_security_level == -1:
			self.controlling_security_level = request.security_level
			self.logger.info("Someone requested access control and it was granted because no one had control")
			return tracker_pb2.RequestControlResponse(message="Success", success=tracker_pb2.SUCCESS)
		elif request.security_level < self.controlling_security_level:
			self.security_level_queue.put(self.controlling_security_level)
			self.controlling_security_level = request.security_level
			self.logger.info("Someone requested access, it was granted and it was taken from someone else")
			return tracker_pb2.RequestControlResponse(message="Success", success=tracker_pb2.SUCCESS)
		elif request.security_level >= self.controlling_security_level:
			self.logger.info("Someone requested access control but another process has control")
			return tracker_pb2.RequestControlResponse(message="Failure", success=tracker_pb2.INSUFFICIENT_SECURITY_LEVEL)

	def relinquish_control(self, request, context):
		self.controlling_security_level = -1
		self.logger.info("Control was relinquished")
		return tracker_pb2.RequestControlResponse(message="Success")

	def move_panel(self, request, context):
		move_type = request.move_type
		if move_type == tracker_pb2.MoveRequest.DURATION:
			direction = request.direction
			if direction == tracker_pb2.NORTH:
				self.logger.info("Moving north called")
				self.tracker_controller.move_north()
			elif direction == tracker_pb2.SOUTH:
				self.logger.info("Moving south called")
				self.tracker_controller.move_south()
			elif direction == tracker_pb2.EAST:
				self.logger.info("Moving east called")
				self.tracker_controller.move_east()
			elif direction == tracker_pb2.WEST:
				self.logger.info("Moving west called")
				self.tracker_controller.move_west()

		elif move_type == tracker_pb2.MoveRequest.POSITION:
			ns_position = request.position.ns
			ew_position = request.position.ew
			self.logger.info("Position move to {} {} called".format(ns_position, ew_position))
			self.tracker_controller.move_panel_to_linear_position(ns_position, ew_position)
		elif move_type == tracker_pb2.MoveRequest.ANGLE:
			ns_angle = request.angle.ns
			ew_angle = request.angle.ew
			self.logger.info("Angular move to {} {} called".format(ns_angle, ew_angle))
			self.tracker_controller.move_panel_to_angular_position(ns_angle, ew_angle)
		return tracker_pb2.MoveResponse()


	def stop(self, request, context):
		self.tracker_controller.stop()
		self.logger.info("Stop called")
		return tracker_pb2.StopResponse(message="Success")

	def stow(self, request, context):
		self.tracker_controller.stow()
		self.logger.info("Stow called")
		return tracker_pb2.StowResponse(message="Success")


	def _get_tracker_status_message_(self):
		response = tracker_pb2.TrackerSystemStatusResponse()
		with self.charge_controller_lock:
			response.tracker.position.ns = self.tracker_controller.get_ns_position()
			response.tracker.position.ew = self.tracker_controller.get_ew_position()
			response.tracker.angle.ns = self.tracker_controller.get_ns_angle()
			response.tracker.angle.ew = self.tracker_controller.get_ew_angle()
			response.tracker.move_status.ns= self.tracker_controller.is_ns_moving()
			response.tracker.move_status.ns = self.tracker_controller.is_ew_moving()
			response.tracker.current_controlling_level = self.controlling_security_level

			response.charge_controller.battery_voltage = self.charge_data[SmartBoxChargeController.ADC_VB_F]
			response.charge_controller.array_voltage = self.charge_data[SmartBoxChargeController.ADC_VA_F]
			response.charge_controller.load_voltage = self.charge_data[SmartBoxChargeController.ADC_VL_F]
			response.charge_controller.charge_current = self.charge_data[SmartBoxChargeController.ADC_IC_F]
			response.charge_controller.load_current = self.charge_data[SmartBoxChargeController.ADC_IL_F]
			response.charge_controller.charge_state = self.charge_data[SmartBoxChargeController.CHARGE_STATE]
			response.charge_controller.energy_collected = self.energy_collected_at_current_time - \
				self.energy_collected_at_start
			response.charge_controller.energy_expended = self.energy_expended_at_current_time	- \
				self.energy_expended_at_start

		return response

	def _get_charge_controller_data(self):
		while True:
			try:
				with self.charge_controller_lock:
					self.data, self.charge_data = self.charge_controller.get_all_data()
			except Exception as e:
				self.logger.error("Retrieving charge controller failed")
				self.logger.error(e, exc_info = True)
			time.sleep(1)