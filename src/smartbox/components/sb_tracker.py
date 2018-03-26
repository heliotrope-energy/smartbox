from gpiozero import Motor, CPUTemperature
from threading import Thread
import Adafruit_ADS1x15
import math
class SmartBoxTracker:
	def __init__(self):
		self.TOLERANCE = 0.1
		self.adc = Adafruit_ADS1x15.ADS1115()
		self.GAIN  = 2/3
		self.EW_PIN = 1
		self.NS_PIN = 0
		self.scale = 6.144/32767
		self.EW_retracted_length = 12.0
		self.NS_retracted_length = 6.0


		self.limits = {self.NS_PIN:[0,6.0], self.EW_PIN:[0,12.0]}
		self.ns_motor = Motor(26,20)
		self.ew_motor = Motor(21,16)
		self.actuators = {self.NS_PIN:self.ns_motor, self.EW_PIN:self.ew_motor}
		self.actuator_names = {self.NS_PIN: "North-South", self.EW_PIN: "East-West"}
		
		self.actuator_conversions = {
			self.NS_PIN: [-1.335, 6.917],
			self.EW_PIN: [-2.67, 13.83]}
		self.actuator_directions = {
			self.NS_PIN: ["North", "South"], 
			self.EW_PIN: ["East", "West"]}

		self.ew_thread = None
		self.ns_thread = None

	def get_ns_position(self):
		"""
			Returns the position in inches of the North-South Actuator
		"""
		return self._get_position_(self.NS_PIN)

	def get_ew_position(self):
		"""
			Returns the position in inches of the East-West Actuator
		"""
		return self._get_position_(self.EW_PIN)

	def get_ns_angle(self):
		"""
			Returns the position in degrees of the North-south direction
		"""
		pos_ns = self.get_ns_position()
		return self._calculate_ns_angle_from_position(pos_ns)
		
	def get_ew_angle(self):
		"""
			Returns the position in degrees of the East-West direction
		"""
		pos_ns = self.get_ew_position()
		return self._calculate_ew_angle_from_position(pos_ns)
		

	def get_ns_limits(self):
		return self.limits[self.NS_PIN]

	def get_ew_limits(self):
		return self.limits[self.EW_PIN]

	def is_panel_moving(self):
		"""
			TODO
			Returns status of 
		"""
		return self.is_ns_moving() or self.is_ew_moving()

	def is_ns_moving(self):
		"""

		"""
		return self.ns_motor.value > 0.0

	def is_ew_moving(self):
		"""

		"""
		return self.ew_motor.value > 0.0

	def move_panel_to_linear_position(self, ns_pos, ew_pos):
		"""
			Moves the panel to given linear actuator positions
			Params:
				ns_pos: The north-south position in inches from full-retraction
				ew_pos: The east-west position in inches from full-retraction
		"""
		self.ew_thread = \
			Thread(target = self._move_axis_to_linear_position_, \
				args = (self.EW_PIN, ew_pos))
		
		self.ns_thread = \
			Thread(target = self._move_axis_to_linear_position_, \
				args = (self.NS_PIN, ns_pos))
		
		self.ew_thread.start()
		self.ns_thread.start()

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

		self.ew_thread = \
			Thread(target = self._move_ew_axis_to_angular_position_, \
				args = (ew_angle,))
		
		self.ns_thread = \
			Thread(target = self._move_ns_axis_to_angular_position_, \
				args = (ns_angle,))
		
		self.ew_thread.start()
		self.ns_thread.start()

	def stow(self):
		"""
			Moves the panel to a safe wind-stow position
		"""
		self.move_panel_to_linear_position(4.5, 6.0)

	def move_north(self):
		"""
			Moves the panel to face north. Call stop_ns() or stop() to stop 
			the movement
		"""
		self._move_axis_(self.NS_PIN, True)

	def move_south(self):
		"""
			Moves the panel to face south. Call stop_ns() or stop() to stop 
			the movement
		"""

		self._move_axis_(self.NS_PIN, False)

	def move_east(self):
		"""
			Moves the panel to face east. Call stop_ew() or stop() to stop 
			the movement
		"""
		self._move_axis_(self.EW_PIN, True)

	def move_west(self):
		"""
			Moves the panel to face west. Call stop_ew() or stop() to stop 
			the movement
		"""
		self._move_axis_(self.EW_PIN, False)

	def stop_ns(self):
		"""
			Stops the movement of the north-south axis
		"""
		self._stop_axis_(self.NS_PIN)

	def stop_ew(self):
		"""
			Stops the movement of the east-west axis
		"""
		self._stop_axis_(self.EW_PIN)

	def stop(self):
		"""
			Stops the movement of both axes
		"""
		self.moving_canceled = True
		self.stop_ns()
		self.stop_ew()


	def _calculate_angle_from_position_(self, vert_dist, mount_point_dist, act_offset, total_length_actuator):
		panel_mount_point_to_mast = math.sqrt(vert_dist ** 2.0 + act_offset ** 2.0)
		angle1 = math.atan(act_offset / vert_dist)

		angle2 = math.acon((mount_point_dist ** 2.0 + panel_mount_point_to_mast ** 2.0 - total_length_actuator ** 2.0) / \
				(2 * mount_point_dist * panel_mount_point_to_mast))
		return 90.0 - (angle1 + angle2)

	def _calculate_ew_angle_from_position(self, extended_length):
		total_length = self.EW_retracted_length + extended_length
		return self._calculate_angle_from_position_(20, 6, 2, total_length)

	def _calculate_ns_angle_from_position(self, extended_length):
		total_length = self.NS_retracted_length + extended_length
		return self._calculate_angle_from_position_(20, 6, 2, total_length)

	def _calculate_ew_position_from_angle(self, desired_angle):
		a = 24.25
		b = 2.1875
		c = 8.625
		total_length = self._calculate_total_length_from_angle(desired_angle, a ,b ,c )

		extended_length = total_length - 18.125
		return extended_length

	def _calculate_ns_position_from_angle(self, desired_angle):
		a = 16.75
		b = 2.5
		c = 8.625
		total_length = self._calculate_total_length_from_angle(desired_angle, a ,b ,c )

		extended_length = total_length - 12.125
		return extended_length

	def _calculate_total_length_from_angle(self, desired_angle, a, b, c):
		# a: vertical distance
		# b: actuator offset
		# c: panel_mount_offset
		# desired_angle: 

		
		v = math.sqrt(a**2 + c**2.0 - 2.0 * a * c * math.cos(desired_angle))
		angle1 = math.acos((v**2.0 + a**2.0 - c**2.0) / (2 * v * a))
		total_length = math.sqrt(v**2.0 + b**2.0 - 2* v * b * math.cos(90.0 - angle1))
		return total_length

	def _actuator_voltage_to_position_(self, pin_num, voltage): 
		scale, offset = self.actuator_conversions[pin_num]
		position = voltage * scale + offset
		return position

	def _get_position_(self, direction_pin):
		value = self.adc.read_adc(direction_pin, gain=self.GAIN)
		voltage = value * self.scale
		inches =  self._actuator_voltage_to_position_(direction_pin, voltage); 
		return inches

	def _move_axis_to_linear_position_(self, direction_pin, pos):
		self.moving_canceled = False
		min_limit, max_limit = self.limits[direction_pin]
		current_position = self._get_position_(direction_pin)
		actuator = self.actuators[direction_pin]

		if pos < min_limit:
			pos = min_limit
		if pos > max_limit:
			pos = max_limit

		while abs(current_position - pos) > self.TOLERANCE:
			if self.moving_canceled:
				actuator.stop() 
				return
			current_position = self._get_position_(direction_pin)
			forward_or_backward = current_position > pos
			self._move_axis_(direction_pin, forward_or_backward)

		actuator.stop()

	def _move_ew_axis_to_angular_position_(self, angle):
		desired_position = self._calculate_ew_position_from_angle(angle)
		print("EW Position {}: Angle {}".format(desired_position, angle))
		self._move_axis_to_linear_position_(self.EW_PIN, desired_position)

	def _move_ns_axis_to_angular_position_(self, angle):
		desired_position = self._calculate_ns_position_from_angle(angle)
		print("NS Position {}: Angle {}".format(desired_position, angle))
		self._move_axis_to_linear_position_(self.NS_PIN, desired_position)
		

	def _move_axis_(self, direction_pin, forward_or_backward):
		actuator = self.actuators[direction_pin]
		forward_dir, backward_dir = self.actuator_directions[direction_pin]
		if forward_or_backward:
			actuator.forward(speed = 1)
		else:
			actuator.backward(speed = 1)

	def _stop_axis_(self, direction_pin):
		self.actuators[direction_pin].stop()

