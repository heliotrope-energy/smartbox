import temperature_pb2
import temperature_pb2_grpc

class SmartBoxTemperatureController(temperature_pb2_grpc.TemperatureControllerServicer):
	def __init__(self):
		pass

	def panel_temperature(self, request, context):
		response = smartbox_resource_controller_pb2.PanelTemperatureResponse()
		return response;

