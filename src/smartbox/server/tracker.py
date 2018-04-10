import copy, time, logging, datetime, os
from queue import PriorityQueue
from threading import Thread, RLock
from collections import namedtuple

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

ControllingClient = namedtuple('ControllingClient', ['description', 'id', 'authority_level', 'collected', 'expended'])
LEDGER_PATH = "/home/brawner/ledger.csv"

class SmartBoxTrackerController(tracker_pb2_grpc.TrackerControllerServicer):
	def __init__(self):
		self.charge_controller = SmartBoxChargeController()
		self.tracker_controller = SmartBoxTracker()
		self.energy_collected_at_start = 0.0
		self.energy_collected_at_current_time = 0.0
		self.energy_expended = 0.0
		self.load_amphours_at_previous = 0.0
		
		self.logger = logging.getLogger(__name__)
		self.charge_controller_lock = RLock()
		self.control_ids = set()

		if os.path.exists(LEDGER_PATH):
			self.energy_ledger = pd.read_csv(LEDGER_PATH)
		else:
			self.energy_ledger = pd.DataFrame(columns=\
				["ID", "Timestamp", 'KWHC', 'ADC_I_F','ADC_V_F'])
		self.controlling_client = None
		self.authority_queue = PriorityQueue()

		self.charge_controller_poller = \
			Thread(target = self._get_charge_controller_data_)
		self.charge_controller_poller.start()

	def get_tracker_status(self, request, context):
		return self._get_tracker_status_message_()

	def tracker_status(self, request, context):
		sleep_duration = 1.0 / request.rate
		while self.is_ok():
			yield self._get_tracker_status_message_()
			time.sleep(sleep_duration)

	def _is_ok_(self):
		return True

	def tracker_control(self, request_iterator, context):
		tracker_id = None
		
		for request in request_iterator:
			if tracker_id is None:
				tracker_id = self._request_control_change_(request)
				if tracker_id is None:
					return tracker_pb2.MoveResponse(message="Failure", \
				success=tracker_pb2.INSUFFICIENT_SECURITY_LEVEL)
			if tracker_id != self.controlling_client.id:
				yield tracker_pb2.MoveResponse(\
					message = "Failure. This client no longer has control, but it may be returned", \
					success = tracker_pb2.FAILURE)
			else:
				yield self._process_move_request_(request)
		self._process_relinquish_request_()

	def _request_control_change_(self, request):
		if self.controlling_client is None:
			new_id = self._process_control_change_(request)
			self.logger.info("Access control granted to {}".format(new_id))
			return new_id
		elif request.authority_level < self.controlling_client.authority_level:
			prev_id = self.controlling_client.id
			new_id = self._process_control_change_(request)
			self.logger.info("Access control granted to {}. Taken from {}".format(new_id, prev_id))
			return new_id
		elif request.authority_level >= self.controlling_authority:
			self.logger.info("Access control denied. {} has control".format(self.controlling_client.id))
			return None
			

	# def request_control(self, request, context):
	# 	if self.controlling_client is None:
	# 		new_id = self._process_control_change_(request)
	# 		self.logger.info("Access control granted to {}".format(new_id))
	# 		return tracker_pb2.RequestControlResponse(message="Success", control_id=new_id, \
	# 			success=tracker_pb2.SUCCESS)
	# 	elif request.authority_level < self.controlling_client.authority_level:
	# 		prev_id = self.controlling_client.id
	# 		new_id = self._process_control_change_(request)
	# 		self.logger.info("Access control granted to {}. Taken from {}".format(new_id, prev_id))
	# 		return tracker_pb2.RequestControlResponse(message="Success", control_id=new_id, \
	# 			success=tracker_pb2.SUCCESS)
	# 	elif request.security_level >= self.controlling_authority:
	# 		self.logger.info("Access control denied. {} has control".format(self.controlling_client.id))
	# 		return tracker_pb2.RequestControlResponse(message="Failure", \
	# 			success=tracker_pb2.INSUFFICIENT_SECURITY_LEVEL)

		
	# def relinquish_control(self, request, context):
	# 	if self.controlling_client is None:
	# 		self.logger.warn("A relinquish request was received but no one currently had control. Spooky")
	# 		return tracker_pb2.RequestControlResponse(message="Error", success=tracker_pb2.ERROR)
	# 	if request.control_id != self.controlling_client.id:
	# 		self.logger.warn("A client requested to relinquish control but a different client had control. Bad robot")
	# 		return tracker_pb2.RequestControlResponse(message="Error", success=tracker_pb2.ERROR)
		
	# 	collected, expended = self._process_relinquish_request_()
	# 	return tracker_pb2.RequestControlResponse(message="Success",\
	# 		energy_expended = expended, energy_collected = collected, success=tracker_pb2.SUCCESS)
	
	

	# def move_panel(self, request, context):
	# 	if self.controlling_client is None:
	# 		self.logger.warn("A move request was received but no one currently had control. Bad robot")
	# 		return tracker_pb2.MoveResponse(message="Error", success=tracker_pb2.ERROR)
	# 	if request.control_id != self.controlling_client.id:
	# 		self.logger.warn("A client requested to move the panel but a different client had control. Bad robot")
	# 		return tracker_pb2.MoveResponse(message="Error", success=tracker_pb2.ERROR)	

	# 	self._process_move_request_(request)
	# 	return tracker_pb2.MoveResponse(message="Success")

	def stop(self, request, context):
		tracker_id = self._request_control_change_(request)
		if tracker_id is None:
			self.logger.warn("A client requested to stop the panel but a different client had control. Bad robot")
			return tracker_pb2.StopResponse(message="Error", success=tracker_pb2.ERROR)
		
		self.tracker_controller.stop()
		self.logger.info("Stop called")
		return tracker_pb2.StopResponse(message="Success")

	def stow(self, request, context):
		tracker_id = self._request_control_change_(request)
		if tracker_id is None:
			self.logger.warn("A client requested to stow the panel but a different client had control. Bad robot")
			return tracker_pb2.StowResponse(message="Error", success=tracker_pb2.ERROR)
		
		self.tracker_controller.stow()
		self.logger.info("Stow called")
		return tracker_pb2.StowResponse(message="Success")

	def _get_unique_id_(self, description):
		count = 1
		unique_id = description + "_{}".format(count)
		while unique_id in self.control_ids:
			count += 1
			description + "_{}".format(count)
		self.control_ids.add(unique_id)
		return description

	def _get_tracker_status_message_(self):
		response = tracker_pb2.TrackerSystemStatusResponse()
		with self.charge_controller_lock:
			response.tracker.position.ns = self.tracker_controller.get_ns_position()
			response.tracker.position.ew = self.tracker_controller.get_ew_position()
			response.tracker.angle.ns = self.tracker_controller.get_ns_angle()
			response.tracker.angle.ew = self.tracker_controller.get_ew_angle()
			response.tracker.move_status.ns= self.tracker_controller.is_ns_moving()
			response.tracker.move_status.ns = self.tracker_controller.is_ew_moving()
			if self.controlling_client is not None:
				response.tracker.controlling_client = self.controlling_client.description
				response.tracker.controlling_authority = self.controlling_client.authority_level

			if len(self.charge_data) == 0:
				return response

			response.charge_controller.battery_voltage = self.charge_data["ADC_VB_F"][1]
			response.charge_controller.array_voltage = self.charge_data["ADC_VA_F"][1]
			response.charge_controller.load_voltage = self.charge_data["ADC_VL_F"][1]
			response.charge_controller.charge_current = self.charge_data["ADC_IC_F"][1]
			response.charge_controller.load_current = self.charge_data["ADC_IL_F"][1]
			response.charge_controller.charge_state = self.charge_data["CHARGE_STATE"][1]


			response.charge_controller.details.t_hs = self.charge_data["T_HS"][1]
			response.charge_controller.details.t_batt = self.charge_data["T_BATT"][1]
			response.charge_controller.details.t_amb = self.charge_data["T_AMB"][1]
			response.charge_controller.details.t_rts = self.charge_data["T_RTS"][1]
			response.charge_controller.details.array_fault = self.charge_data["ARRAY_FAULT"][1]
			response.charge_controller.details.vb_f = self.charge_data["VB_F"][1]
			response.charge_controller.details.vb_ref = self.charge_data["VB_REF"][1]

			response.charge_controller.details.ahc_r = self.charge_data["AHC_R"][1]
			response.charge_controller.details.ahc_t = self.charge_data["AHC_T"][1]

			response.charge_controller.details.kwhc = self.charge_data["KWHC"][1]
			response.charge_controller.details.load_state = self.charge_data["LOAD_STATE"][1]
			response.charge_controller.details.load_fault = self.charge_data["LOAD_FAULT"][1]
			response.charge_controller.details.v_lvd = self.charge_data["V_LVD"][1]

			response.charge_controller.details.ahl_r = self.charge_data["AHL_R"][1]
			response.charge_controller.details.ahl_t = self.charge_data["AHL_T"][1]
			response.charge_controller.details.hourmeter = self.charge_data["HOURMETER"][1]
			response.charge_controller.details.alarm = self.charge_data["ALARM"][1]


			response.charge_controller.details.dip_switch = self.charge_data["DIP_SWITCH"][1]
			response.charge_controller.details.led_state = self.charge_data["LED_STATE"][1]
			response.charge_controller.details.power_out = self.charge_data["POWER_OUT"][1]
			response.charge_controller.details.sweep_vmp = self.charge_data["SWEEP_VMP"][1]
			response.charge_controller.details.sweep_pmax = self.charge_data["SWEEP_PMAX"][1]
			response.charge_controller.details.sweep_voc = self.charge_data["SWEEP_VOC"][1]
			response.charge_controller.details.vb_min_daily = self.charge_data["VB_MIN_DAILY"][1]
			response.charge_controller.details.vb_max_daily = self.charge_data["VB_MAX_DAILY"][1]
			response.charge_controller.details.ahc_daily = self.charge_data["AHC_DAILY"][1]
			response.charge_controller.details.ahl_daily = self.charge_data["AHL_DAILY"][1]
			response.charge_controller.details.array_fault_daily = \
				self.charge_data["ARRAY_FAULT_DAILY"][1]
			response.charge_controller.details.load_fault_daily = \
				self.charge_data["LOAD_FAULT_DAILY"][1]

			response.charge_controller.details.alarm = self.charge_data["ALARM_DAILY"][1]
			response.charge_controller.details.vb_min = self.charge_data["VB_MIN"][1]
			response.charge_controller.details.vb_max = self.charge_data["VB_MAX"][1]
			
			response.charge_controller.details.lighting_should_be_on = \
				self.charge_data["LIGHTING_SHOULD_BE_ON"][1]
			response.charge_controller.details.va_ref_fixed = \
				self.charge_data["VA_REF_FIXED"][1]
			response.charge_controller.details.va_ref_fixed_ptc = \
				self.charge_data["VA_REF_FIXED_PTC"][1]
			
	
			response.charge_controller.energy_collected = self.energy_collected_at_current_time - \
				self.energy_collected_at_start
			response.charge_controller.energy_expended = self.energy_expended
			
		return response

	def _get_cc_attr_safe_(self, attr):
		with self.charge_controller_lock:
			if attr in self.charge_data:
				return self.charge_data[attr]
		return None

	def _add_update_to_energy_ledger(self):
		self.energy_ledger.to_csv("/home/brawner/ledger.csv")
		self.controlling_client.collected = self.energy_collected_at_current_time - \
				self.energy_collected_at_start
		self.controlling_client.expended = self.energy_expended
		if len(self.charge_data) == 0:
			return
		self.energy_ledger = self.energy_ledger.append({
			"ID": self.controlling_client.id,
			"Timestamp": str(datetime.datetime.now()),
			"KWHC": self.charge_data["KWHC"], 
			"ADC_I_F": self.charge_data["ADC_I_F"], 
			"ADC_V_F": self.charge_data["ADC_V_F"],
			})

	def _process_control_change_(self, request):
		new_id = self._get_unique_id_(request.description)
		controlling_client = \
			ControllingClient(description=request.description, \
				id=new_id, authority_level = request.authority_level, collected = 0.0, expended = 0.0)
		with self.charge_controller_lock:
			if self.controlling_client is not None:
				self.authority_queue.put((self.controlling_client.authority_level, self.controlling_client))
			self.controlling_client = controlling_client
			if "AHL_T" in self.charge_data:
				self.load_amphours_at_start = self.charge_data["AHL_T"][1]
			if "KWHC" in self.charge_data:
				self.energy_collected_at_start = self.charge_data["KWHC"][1]

		return new_id

	def _process_move_request_(self, request):
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

	def _process_relinquish_request_(self):
		energy_collected = self.energy_collected_at_current_time - self.energy_collected_at_start
		energy_expended = self.energy_expended
		if self.controlling_client is None:
			self.logger.error("There is no controlling client to relinquish control. Spooky")
			return 0.0, 0.0
		previous = self.controlling_client
		self.logger.info("Control was relinquished by {} Collected {:.3f} Expended {:.3f}".format(\
			previous.description, previous.collected, previous.expended))
		with self.charge_controller_lock:
			if not self.authority_queue.empty():
				self.controlling_client = self.authority_queue.get()
				self.energy_collected_at_start = \
					self.energy_collected_at_current_time - self.controlling_client.collected
				self.energy_expended = 0.0
				if "AHL_T" in self.charge_data:
					self.load_amphours_at_previous = self.charge_data["AHL_T"][1]
				self.logger.info("Control was returned to {}".format(self.controlling_client.description))
			else:
				self.controlling_client = None
		return energy_collected, energy_expended
	

	def _calculate_incremental_energy_expended_(self):
		if len(self.charge_data) > 0:
			increment = self.charge_data["ADC_VL_F"][1] * \
				(self.charge_data["AHL_T"][1] - self.load_amphours_at_previous)
			self.load_amphours_at_previous = self.charge_data["AHL_T"][1]
		return increment

	def _get_charge_controller_data_(self):
		while True:
			try:
				with self.charge_controller_lock:
					self.charge_data = self.charge_controller.get_all_data()
					if "KWHC" in self.charge_data:
						self.energy_collected_at_current_time = self.charge_data["KWHC"][1]
						self.energy_expended += self._calculate_incremental_energy_expended_()
						
					if self.controlling_client is not None:
						self._add_update_to_energy_ledger()
			except Exception as e:
				self.logger.error("Retrieving charge controller failed")
				self.logger.error(e, exc_info = True)
			time.sleep(0.05)
