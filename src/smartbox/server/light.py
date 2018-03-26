from smartbox_msgs import light_pb2
from smartbox_msgs import light_pb2_grpc

class SmartBoxLightController(light_pb2_grpc.LightControllerServicer):
	def __init(self):
		self.light = SmartBoxLight()

	def set_light(self, request, context):
		if request.light == smartbox_resource_controller_pb2.LightRequest.ON:
			self.light.turn_on()
		elif request.light == smartbox_resource_controller_pb2.LightRequest.OFF:
			self.light.turn_off()
		if self.light.is_light_on():
			status = smartbox_resource_controller_pb2.LightResponse.ON
		else:
			status = smartbox_resource_controller_pb2.LightResponse.OFF
		return smartbox_resource_controller_pb2.LightResponse(status = status)