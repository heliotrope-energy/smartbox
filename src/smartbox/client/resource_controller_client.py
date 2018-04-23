#!/usr/bin/env python
import grpc, time

from smartbox.client.tracker_client import TrackerClient
from smartbox.client.tracker_controller import ControlDisruption
from smartbox.client.weather_client import WeatherClient
from smartbox.client.light_client import LightClient
from smartbox.client.panel_temperature_client import PanelTemperatureClient
from smartbox.client.camera_client import CameraClient

class SmartBoxResourceControllerClient():
	def __init__(self, authority_level, description):
		self.channel = grpc.insecure_channel('138.16.161.117:50051')
		#self.stub = smartbox_resource_controller_pb2_grpc.SmartBoxResourceControllerStub(self.channel)
		
		self.tracker = TrackerClient(self.channel, authority_level, description)
		self.weather = WeatherClient(self.channel)
		self.light = LightClient(self.channel)
		self.panel_temps = PanelTemperatureClient(self.channel)
		self.camera = CameraClient(self.channel)



if __name__ == "__main__":
	client = SmartBoxResourceControllerClient(101, "Basic client")
	#client.tracker.chat([str(i) for i in range(10)])
	# print(client.tracker.get_ns_position())
	# print(client.tracker.get_ew_position())
	# print(client.tracker.get_ew_angle())
	# print(client.tracker.get_ew_angle())
	# print(client.tracker.is_ew_moving())
	# print(client.tracker.is_ns_moving())
	if not client.tracker.is_control_possible():
		print("Control is not currently feasible")
	else:
		try:
			control = client.tracker.request_control()
			print(control.move_panel_to_linear_position(4.4, 1))
			print(control.move_panel_to_angular_position(0.0, 0.0))
			print(control.stow())
			print(control.stop())
			print(control.move_west())
			control.release()

		except ControlDisruption:
			print("Control takeover failed")

	# with client.tracker.request_control() as control:
	# 	print(control.move_panel_to_linear_position(4.4, 1))
	# 	print(control.move_panel_to_angular_position(0.0, 0.0))
	# 	print(control.stow())
	# 	print(control.stop())
	# 	print(control.move_west())
	print("All done")
	#client.tracker.relinquish_control()
	# print(client.tracker.does_client_have_control())
	# print(client.light.get_light_status())
	# print(client.light.set_light_status(True))
	# print(client.light.get_light_status())
	# print(client.light.set_light_status(False))
	# print(client.light.get_light_status())
	# print(client.tracker.get_battery_voltage())
	# print(client.tracker.get_solar_panel_voltage())
	# print(client.tracker.get_load_voltage())
	# print(client.tracker.get_charging_current())
	# print(client.tracker.get_load_current())
	# print(client.tracker.get_charge_status())

	




