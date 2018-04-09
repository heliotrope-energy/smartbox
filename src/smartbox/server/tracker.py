import copy, time, logging
from queue import Queue
from threading import Thread, RLock

from smartbox_msgs import tracker_pb2
from smartbox_msgs import tracker_pb2_grpc

from smartbox.components.sb_charge_controller import SmartBoxChargeController
from smartbox.components.sb_tracker import SmartBoxTracker

import pandas as pd
"""
Clients choose their own authority level

Clients with a lower value for authority have higher priority

If no client is currently controlling, then access is granted

If a client is controlling it, then access is only granted if the requesting
client has a higher priority

If the higher controlling authority relinquishes control then is authority
handed back, or just reset?


"""
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
		self.controlling_authority = -1

		self.logger = logging.getLogger(__name__)
		self.charge_controller_lock = RLock()

		self.energy_ledger = pd.DataFrame(columns=["ID","Authority","KWH Collected", "Ah Total Load", "V Load"])
		

	def get_tracker_status(self, request, context):
		return self._get_tracker_status_message_()

	def request_control(self, request, context):
		if self.controlling_authority == -1:
			self._process_control_change_(request.security_level)
			self.logger.info("Someone requested access control and it was granted because no one had control")
			return tracker_pb2.RequestControlResponse(message="Success", success=tracker_pb2.SUCCESS)
		elif request.security_level < self.controlling_authority:
			
			self._process_control_change_(request.security_level)
			self.logger.info("Someone requested access, it was granted and it was taken from someone else")
			return tracker_pb2.RequestControlResponse(message="Success", success=tracker_pb2.SUCCESS)
		elif request.security_level >= self.controlling_authority:
			self.logger.info("Someone requested access control but another process has control")
			return tracker_pb2.RequestControlResponse(message="Failure", success=tracker_pb2.INSUFFICIENT_SECURITY_LEVEL)

		
	def relinquish_control(self, request, context):
		self.controlling_authority = -1
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
			response.tracker.current_controlling_level = self.controlling_authority

			response.charge_controller.battery_voltage = self.charge_data["ADC_VB_F"]
			response.charge_controller.array_voltage = self.charge_data["ADC_VA_F"]
			response.charge_controller.load_voltage = self.charge_data["ADC_VL_F"]
			response.charge_controller.charge_current = self.charge_data["ADC_IC_F"]
			response.charge_controller.load_current = self.charge_data["ADC_IL_F"]
			response.charge_controller.charge_state = self.charge_data["CHARGE_STATE"]


			response.charge_controller.details.t_hs = self.charge_data["T_HS"]
			response.charge_controller.details.t_batt = self.charge_data["T_BATT"]
			response.charge_controller.details.t_amb = self.charge_data["T_AMB"]
			response.charge_controller.details.t_rts = self.charge_data["T_RTS"]
			response.charge_controller.details.array_fault = self.charge_data["ARRAY_FAULT"]
			response.charge_controller.details.vb_f = self.charge_data["VB_F"]
			response.charge_controller.details.vb_ref = self.charge_data["VB_REF"]

			response.charge_controller.details.ahc_r = self.charge_data["AHC_R"]
			response.charge_controller.details.ahc_t = self.charge_data["AHC_T"]

			response.charge_controller.details.kwhc = self.charge_data["KWHC"]
			response.charge_controller.details.load_state = self.charge_data["LOAD_STATE"]
			response.charge_controller.details.load_fault = self.charge_data["LOAD_FAULT"]
			response.charge_controller.details.v_lvd = self.charge_data["V_LVD"]

			response.charge_controller.details.ahl_r = self.charge_data["AHL_R"]
			response.charge_controller.details.ahl_t = self.charge_data["AHL_T"]
			response.charge_controller.details.hourmeter = self.charge_data["HOURMETER"]
			response.charge_controller.details.alarm = self.charge_data["ALARM"]


			response.charge_controller.details.dip_switch = self.charge_data["DIP_SWITCH"]
			response.charge_controller.details.led_state = self.charge_data["LED_STATE"]
			response.charge_controller.details.power_out = self.charge_data["POWER_OUT"]
			response.charge_controller.details.sweep_vmp = self.charge_data["SWEEP_VMP"]
			response.charge_controller.details.sweep_pmax = self.charge_data["SWEEP_PMAX"]
			response.charge_controller.details.sweep_voc = self.charge_data["SWEEP_VOC"]
			response.charge_controller.details.vb_min_daily = self.charge_data["VB_MIN_DAILY"]
			response.charge_controller.details.vb_max_daily = self.charge_data["VB_MAX_DAILY"]
			response.charge_controller.details.ahc_daily = self.charge_data["AHC_DAILY"]
			response.charge_controller.details.ahl_daily = self.charge_data["AHL_DAILY"]
			response.charge_controller.details.array_fault_daily = self.charge_data["ARRAY_FAULT_DAILY"]
			response.charge_controller.details.load_fault_daily = self.charge_data["LOAD_FAULT_DAILY"]

			response.charge_controller.details.alarm = self.charge_data["ALARM_DAILY"]
			response.charge_controller.details.vb_min = self.charge_data["VB_MIN"]
			response.charge_controller.details.vb_max = self.charge_data["VB_MAX"]
			
			response.charge_controller.lighting_should_be_on = self.charge_data["LIGHTING_SHOULD_BE_ON"]
			response.charge_controller.va_ref_fixed = self.charge_data["VA_REF_FIXED"]
			response.charge_controller.va_ref_fixed_ptc = self.charge_data["VA_REF_FIXED_PTC"]
			
    
			response.charge_controller.energy_collected = self.energy_collected_at_current_time - \
				self.energy_collected_at_start
			response.charge_controller.energy_expended = self.energy_expended_at_current_time	- \
				self.energy_expended_at_start

		return response

	def _get_cc_attr_safe_(self, attr):
		with self.charge_controller_lock:
			if attr in self.charge_data:
				return self.charge_data[attr]
		return None

	def _add_update_to_energy_ledger(self):
		self.energy_ledger.to_csv("/home/brawner/ledger.csv")
		["ID","Authority","KWH Collected", "Ah Total Load", "V Load"]


		self.energy_ledger = self.energy_ledger.append({
			"ID": self.controlling_id,
			"Authority": self.controlling_authority,
			"KWH Collected": self.charge_data(SmartBoxChargeController.KWHC), 
			"Ah Total Load": self.charge_data(SmartBoxChargeController.ADC_I_F), 
			"V Load": self.charge_data(SmartBoxChargeController.ADC_V_F),
			})

	def _process_control_change_(self, authority_level, context):
		if self.controlling_authority != -1:
			self.authority_queue.put((self.controlling_security_level, self.energy_ledger, self.controlling_context))

		with self.charge_controller_lock:		
			self.controlling_context = context
			self.controlling_authority = authority_level

			self.energy_expended_at_start = 0.0
			self.energy_collected_at_start = self.charge_data["KWHC"]
	

	def _get_charge_controller_data(self):
		while True:
			try:
				with self.charge_controller_lock:
					self.charge_data = self.charge_controller.get_all_data()
					self.energy_collected_at_current_time = self.charge_data["KWHC"]
			except Exception as e:
				self.logger.error("Retrieving charge controller failed")
				self.logger.error(e, exc_info = True)
			time.sleep(0.05)
