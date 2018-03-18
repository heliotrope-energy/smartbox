from gpiozero import Motor, CPUTemperature
import Adafruit_ADS1x15

class SmartBoxTracker:
	def __init__(self):
		self.TOLERANCE = 0.1
		self.adc = Adafruit_ADS1x15.ADS1115()
		self.GAIN  = 2/3
		self.EW_PIN = 1
		self.NS_PIN = 0
		self.scale = 6.144/32767

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
			TODO
			Returns the position in degrees of the North-south direction
		"""
		return 0.0

	def get_ew_angle(self):
		"""
			TODO
			Returns the position in degrees of the East-West direction
		"""
		return 0.0

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
		return self.ns_motor.value

	def is_ew_moving(self):
		"""

		"""
		return self.ew_motor.value

	def move_panel_to_linear_position(self, ns_pos, ew_pos):
		"""
			Moves the panel to given linear actuator positions
			Params:
				ns_pos: The north-south position in inches from full-retraction
				ew_pos: The east-west position in inches from full-retraction
		"""
		self._move_axis_to_linear_position_(self.EW_PIN, ew_pos)
		self._move_axis_to_linear_position_(self.NS_PIN, ns_pos)

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
		self.stop_ns()
		self.stop_ew()


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
		min_limit, max_limit = self.limits[direction_pin]
		current_position = self._get_position_(direction_pin)
		actuator = self.actuators[direction_pin]

		if pos < min_limit:
			pos = min_limit
		if pos > max_limit:
			pos = max_limit

		while abs(current_position - pos) > self.TOLERANCE: 
			current_position = self._get_position_(direction_pin)
			direction_pin = current_position > pos
			self._move_axis_(direction_pin, direction_pin)

		actuator.stop()

	def _move_axis_(self, direction_pin, forward_or_backward):
		actuator = self.actuators[direction_pin]
		forward_dir, backward_dir = self.actuator_directions[direction_pin]
		if forward_or_backward:
			actuator.forward(speed = 1)
		else:
			actuator.backward(speed = 1)

	def _stop_axis_(self, direction_pin):
		self.actuators[direction_pin].stop()

