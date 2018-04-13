import copy, time, logging, datetime, os
from queue import PriorityQueue
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

class ControllingClient:
	def __init__(self, description, client_id, authority_level, collected = 0.0, expended = 0.0):
		self.description = description
		self.client_id = client_id
		self.authority_level = authority_level
		self.collected = collected
		self.expended = expended

LEDGER_FILENAME = "ledger.csv"

class SmartBoxTrackerController(tracker_pb2_grpc.TrackerControllerServicer):
	def __init__(self, log_dir):
		self.charge_controller = SmartBoxChargeController()
		self.tracker_controller = SmartBoxTracker()
		self.energy_collected_at_start = 0.0
		self.energy_collected_at_current_time = 0.0
		self.energy_expended = 0.0
		self.load_amphours_at_previous = 0.0
		self.log_dir = log_dir
		
		self.logger = logging.getLogger("server.tracker")
		self.logger.propagate = True
		self.charge_controller_lock = RLock()
		self.control_ids = set()

		ledger_path = os.path.join(log_dir, LEDGER_FILENAME)
		if os.path.exists(ledger_path):
			self.energy_ledger = pd.read_csv(ledger_path)
		else:
			columns = ["ID", "Timestamp", "Collected", "Expended"] + list(SmartBoxChargeController.registers.keys())
			self.energy_ledger = pd.DataFrame(columns=columns)
		self.controlling_client = None
		self.authority_queue = PriorityQueue()

		self.charge_controller_poller = \
			Thread(target = self._get_charge_controller_data_)
		self.charge_controller_poller.start()
		self.count = 0

	def termination_cb(self):
		self.logger.info("Termination!")

	def echo(self, request_iterator, context):
		self.logger.info("Chat beginning")
		context.add_callback(self.termination_cb)
		for request in request_iterator:
			self.logger.info("Received {}".format(request.message))
			yield tracker_pb2.ChatMessageResponse(message = request.message)
		self.logger.info("Chat all done!")

	def get_tracker_status(self, request, context):
		return self._get_tracker_status_message_()

	def tracker_status(self, request, context):
		self.logger.info("Tracker status subscription received")
		rate = 10.0 if request.message_rate <= 0.0 else request.message_rate
		sleep_duration = 1.0 / rate
		while self._is_ok_():
			yield self._get_tracker_status_message_()
			time.sleep(sleep_duration)

	def _is_ok_(self):
		return True

	def tracker_control(self, request_iterator, context):
		"""
			TODO: There appears to be an issue with the handshaking. The for loop doesn't always enter.
			Also, I don't think the iterators are exiting properly.
		"""
		self.logger.info("Tracker control initiated")
		context.add_callback(self._process_relinquish_request_)

		self.logger.info("Processing initial request")
		initial_request = next(request_iterator)
		self.logger.info(initial_request)
		tracker_id = self._request_control_change_(initial_request)
		if tracker_id is None:
			self.logger.info("Control request failed, terminating connection")
			yield tracker_pb2.ControlResponse(message="Failure. Terminating connection", \
				success=tracker_pb2.INSUFFICIENT_SECURITY_LEVEL)
			context.cancel()
			return
		self.logger.info("Control request succeeded")
		yield tracker_pb2.ControlResponse(\
					message = "This client has control", \
					success = tracker_pb2.SUCCESS)
		self.count += 1
		for request in request_iterator:
			if tracker_id != self.controlling_client.client_id:
				self.logger.info("Client {} lost control, but it is still sending messages".format(tracker_id))
				yield tracker_pb2.ControlResponse(\
					message = "Failure. This client no longer has control, but it may be returned", \
					success = tracker_pb2.FAILURE)
			elif not self._is_ok_():
				self.count -= 1
				self.logger.info("Server detected an issue and is canceling this connection")
				yield tracker_pb2.ControlResponse(message="Server is definitely not ok", \
					success=tracker_pb2.FAILURE)
				context.cancel()
			else:
				yield self._process_move_request_(request)
		self.count -= 1

	def _request_control_change_(self, request):
		self.logger.info("Access control request initiated")
		if self.controlling_client is None:
			self.logger.info("No controlling client, this should be easy")
			new_id = self._process_control_change_(request)
			self.logger.info("Access control granted to {}".format(new_id))
			return new_id
		elif request.authority_level < self.controlling_client.authority_level:
			self.logger.info("There already exists a controlling client, stealing control")
			prev_id = self.controlling_client.client_id
			new_id = self._process_control_change_(request)
			self.logger.info("Access control granted to {}. Taken from {}".format(new_id, prev_id))
			return new_id
		self.logger.info("Access control denied. {} has control".format(self.controlling_client.client_id))
		return None
			
	def _get_unique_id_(self, description):
		count = 1
		unique_id = description + "_{}".format(count)
		while unique_id in self.control_ids:
			count += 1
			description + "_{}".format(count)
			unique_id = description + "_{}".format(count)
		self.control_ids.add(unique_id)
		return description

	def _get_tracker_status_message_(self):
		response = tracker_pb2.TrackerSystemStatusResponse()
		response.tracker.position.ns = self.tracker_controller.get_ns_position()
		response.tracker.position.ew = self.tracker_controller.get_ew_position()
		response.tracker.angle.ns = self.tracker_controller.get_ns_angle()
		response.tracker.angle.ew = self.tracker_controller.get_ew_angle()
		response.tracker.move_status.ns= self.tracker_controller.is_ns_moving()
		response.tracker.move_status.ns = self.tracker_controller.is_ew_moving()
		if self.controlling_client is not None:
			response.tracker.controlling_client = self.controlling_client.description
			response.tracker.controlling_authority = self.controlling_client.authority_level
		else:
			response.tracker.controlling_authority = -1
		with self.charge_controller_lock:
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
		now = pd.to_datetime('now')
		if self.last_update and (self.last_update - now < pd.Timedelta(minutes=1)):
			return

		filepath = os.path.join(self.log_dir, LEDGER_FILENAME)
		if not os.path.exists(filepath):
			self.energy_ledger.to_csv(filepath)
		else:
			self.energy_ledger.to_csv(filepath, mode='a', header=False)
		client_info = {}
		
		if self.controlling_client:
			self.controlling_client.collected = \
				self.energy_collected_at_current_time - self.energy_collected_at_start
			self.controlling_client.expended = self.energy_expended
		
			client_info = {
				"ID": self.controlling_client.client_id,
				"Timestamp": str(datetime.datetime.now()),
				"Collected": self.controlling_client.collected,
				"Expended": self.controlling_client.expended}

		self.energy_ledger = \
			self.energy_ledger.append( {**client_info, **self.charge_data}, ignore_index=True)
		self.last_update = pd.to_datetime('now')

	def _process_control_change_(self, request):
		self.logger.info("Processing control change")
		self.logger.info("Number unique ids {}".format(len(self.control_ids)))
		new_id = self._get_unique_id_(request.description)
		self.logger.info("Creating new ControllingClient")
		controlling_client = \
			ControllingClient(description=request.description, \
				client_id=new_id, authority_level = request.authority_level)
		
		if self.controlling_client is not None:
			self.authority_queue.put((self.controlling_client.authority_level, self.controlling_client))
		self.controlling_client = controlling_client
		self.logger.info("Setting new controlling client")

		self.logger.info("Acquiring lock")
		with self.charge_controller_lock:
			self.logger.info("Lock acquired")
		
			if "AHL_T" in self.charge_data:
				self.load_amphours_at_start = self.charge_data["AHL_T"][1]
			if "KWHC" in self.charge_data:
				self.energy_collected_at_start = self.charge_data["KWHC"][1]
		self.logger.info("Control change processed")
		return new_id

	def _process_move_request_(self, request):
		move_type = request.move_type
		if move_type == tracker_pb2.ControlRequest.STOP:
			self.tracker_controller.stop()
			self.logger.info("Tracker stopped")
		elif move_type == tracker_pb2.ControlRequest.STOW:
			self.tracker_controller.stow()
			self.logger.info("Tracker stowed")
		elif move_type == tracker_pb2.ControlRequest.DURATION:
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

		elif move_type == tracker_pb2.ControlRequest.POSITION:
			ns_position = request.position.ns
			ew_position = request.position.ew
			self.logger.info("Position move to {} {} called".format(ns_position, ew_position))
			self.tracker_controller.move_panel_to_linear_position(ns_position, ew_position)
		elif move_type == tracker_pb2.ControlRequest.ANGLE:
			ns_angle = request.angle.ns
			ew_angle = request.angle.ew
			self.logger.info("Angular move to {} {} called".format(ns_angle, ew_angle))
			self.tracker_controller.move_panel_to_angular_position(ns_angle, ew_angle)
		return tracker_pb2.ControlResponse()

	def _process_relinquish_request_(self):
		energy_collected = self.energy_collected_at_current_time - self.energy_collected_at_start
		energy_expended = self.energy_expended
		if self.controlling_client is None:
			self.logger.error("There is no controlling client to relinquish control. Spooky")
			return 0.0, 0.0
		previous = self.controlling_client
		self.logger.info("Control was relinquished by {} Collected {:.3f} Expended {:.3f}".format(\
			previous.description, previous.collected, previous.expended))
		
		if self.authority_queue.empty():
			self.controlling_client = None
		else:
			self.controlling_client = self.authority_queue.get()[1]
			self.energy_collected_at_start = \
				self.energy_collected_at_current_time - self.controlling_client.collected
			self.energy_expended = 0.0
			
			with self.charge_controller_lock:
				if "AHL_T" in self.charge_data:
					self.load_amphours_at_previous = self.charge_data["AHL_T"][1]
			self.logger.info("Control was returned to {}".format(self.controlling_client.description))
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
						
					if self.controlling_client:
						self.logger.info("Adding data to ledger")
						self._add_update_to_energy_ledger()
			except Exception as e:
				self.logger.error("Retrieving charge controller failed")
				self.logger.error(e, exc_info = True)
			time.sleep(0.05)
