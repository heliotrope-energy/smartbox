import logging

from smartbox_msgs import lights_pb2
from smartbox_msgs import lights_pb2_grpc

from smartbox.components.sb_light import SmartBoxLight

class SmartBoxLightController(lights_pb2_grpc.LightControllerServicer):
	def __init__(self):
		self.light = SmartBoxLight()
		self.logger = logging.getLogger(__name__)

	def set_light(self, request, context):
		if request.light == lights_pb2.LightRequest.ON:
			self.logger.info("Light turned on")
			self.light.turn_on()
		elif request.light == lights_pb2.LightRequest.OFF:
			self.logger.info("Light turned off")
			self.light.turn_off()
		if self.light.is_light_on():
			status = lights_pb2.LightResponse.ON
		else:
			status = lights_pb2.LightResponse.OFF
		return lights_pb2.LightResponse(status = status)