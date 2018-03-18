from gpiozero import LED

class SmartBoxLight:
	def __init__(self):
		self.light = LED(19)

	def turn_on(self):
		self.light.on()

	def turn_off(self):
		self.light.off()

	def toggle(self):
		self.light.toggle()

	def is_light_on(self):
		return self.light.value