from smartbox_msgs import tracker_pb2
import time, logging
from threading import Thread
from queue import Queue

class ControlDisruption(Exception):
	pass

class TrackerController:
	def __init__(self, server, authority_level, description, client_response_cb = None, timeout = 10.0):
		self.authority_level = authority_level
		self.description = description
		self.stub = server
		self.have_tracker_control = False
		self._move_response_callback_ = None
		self.client_response_cb = client_response_cb
		self.logger = logging.getLogger(__name__)

		self.retain_control = True
		self.control_thread = Thread(target = self._tracker_control_, \
			args=(self.on_response,))
		self.control_requests_queue = Queue()
		self.control_thread.start()
		count = 0.0
		while not self.have_tracker_control and count < timeout:
			count += 1
			request = tracker_pb2.ControlRequest(authority_level = self.authority_level, description = self.description)
			self.control_requests_queue.put(request)
			time.sleep(1.0)
		if not self.have_tracker_control:
			raise ControlDisruption("Getting tracker control failed")
		self.logger.info("Tracker control succeeded")
		
	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.retain_control = False

	def _is_ok_(self):
		return True

	def in_control(self):
		request = tracker_pb2.ControlRequest(\
			authority_level = self.authority_level, description = self.description)
		self._request_move_and_block_(request)
		return self.have_tracker_control

	def release(self):
		self.retain_control = False

	def on_response(self, response):
		if self._move_response_callback_:
			self._move_response_callback_(response)
		if self.client_response_cb:
			self.client_response_cb(response)

	def _control_iterator_(self):
		self.logger.info("Sending initial control request")
		yield tracker_pb2.ControlRequest(authority_level = self.authority_level, description = self.description)
		while self._is_ok_() and self.retain_control:
			if self.control_requests_queue.empty():
				time.sleep(1.0)
			else:
				request = self.control_requests_queue.get()
				yield request

	def _tracker_control_(self, response_cb):
		self.logger.info("Beginning tracker control")
		self.retain_control = True
		control_iterator = self._control_iterator_()
		count = 0
		for response in self.stub.tracker_control(control_iterator):
			if response_cb:
				response_cb(response)
			self.have_tracker_control = (response.success == tracker_pb2.SUCCESS)
			if not self.have_tracker_control:
				break
			if not self.retain_control:
				break

		self.logger.info("Ending tracker control")
		self.retain_control = False

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
		self._stow_()

	def move_north(self):
		"""
			Moves the panel to face north. Call stop_ns() or stop() to stop 
			the movement
		"""
		self._request_direction_move_(direction=tracker_pb2.NORTH)
		

	def move_south(self):
		"""
			Moves the panel to face south. Call stop_ns() or stop() to stop 
			the movement
		"""

		self._request_direction_move_(direction=tracker_pb2.SOUTH)
		
	def move_east(self):
		"""
			Moves the panel to face east. Call stop_ew() or stop() to stop 
			the movement
		"""
		self._request_direction_move_(direction=tracker_pb2.EAST)
		
	def move_west(self):
		"""
			Moves the panel to face west. Call stop_ew() or stop() to stop 
			the movement
		"""
		self._request_direction_move_(direction=tracker_pb2.WEST)

	def stop(self):
		"""
			Stops the movement of both axes
		"""
		self._stop_()

	def _stow_(self):
		request = tracker_pb2.ControlRequest(\
			authority_level = self.authority_level, description = self.description, \
			move_type = tracker_pb2.ControlRequest.STOW)
		self._request_move_and_block_(request)

	def _stop_(self):
		request = tracker_pb2.ControlRequest(\
			authority_level = self.authority_level, description = self.description, \
			move_type = tracker_pb2.ControlRequest.STOP)
		self._request_move_and_block_(request)

	def _request_direction_move_(self, direction):
		request = tracker_pb2.ControlRequest(\
			authority_level = self.authority_level, description = self.description, \
			move_type = tracker_pb2.ControlRequest.DURATION)
		request.direction = direction
		self._request_move_and_block_(request)
		
	def _request_position_move_(self, pos_ns, pos_ew):
		request = tracker_pb2.ControlRequest(\
			authority_level = self.authority_level, description = self.description, \
			move_type = tracker_pb2.ControlRequest.POSITION)
		request.position.ns = pos_ns
		request.position.ew = pos_ew
		self._request_move_and_block_(request)
		
	def _request_angular_move_(self, angle_ns, angle_ew):
		request = tracker_pb2.ControlRequest(\
			authority_level = self.authority_level, description = self.description, \
			move_type = tracker_pb2.ControlRequest.ANGLE)
		request.angle.ns = angle_ns
		request.angle.ew = angle_ew
		self._request_move_and_block_(request)

	def _add_response_callback_(self, cb):
		self._move_response_callback_ = cb

	def _request_move_and_block_(self, request, timeout = 1.0):
		while not self.control_requests_queue.empty():
			time.sleep(0.05)

		received_response = None
		def move_response_cb(response):
			received_response = response

		self._add_response_callback_(move_response_cb)
		self.control_requests_queue.put(request)
		
		count = 0
		while not received_response and count < 20:
			time.sleep(0.05)
			count += 1

		if received_response:
			return received_response.success == tracker_pb2.SUCCESS
		else:
			return False
