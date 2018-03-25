#!/usr/bin/env python
import grpc

from sb_tracker_client import TrackerClient
from sb_charge_controller_client import ChargeControllerClient
from sb_weather_client import WeatherClient
from sb_light_client import LightClient
from sb_panel_temperature_client import PanelTemperatureClient
from sb_camera import CameraClient


class SmartBoxResourceControllerClient():
	def __init__(self, security_level):
		self.channel = grpc.insecure_channel('138.16.161.117:50051')
		#self.stub = smartbox_resource_controller_pb2_grpc.SmartBoxResourceControllerStub(self.channel)
		
		self.tracker = TrackerClient(self.channel)
		self.weather = WeatherClient(self.channel)
		self.light = LightClient(self.channel)
		self.panel_temps = PanelTemperatureClient(self.channel)
		self.camera = CameraClient(self.channel)

if __name__ == "__main__":
	client = SmartBoxResourceControllerClient(101)
	print(client.tracker.get_ns_position())
	print(client.tracker.get_ew_position())
	print(client.tracker.get_ew_angle())
	print(client.tracker.get_ew_angle())
	print(client.tracker.is_ew_moving())
	print(client.tracker.is_ns_moving())
	# print(client.tracker.move_panel_to_linear_position(4.4, 1))
	# print(client.tracker.move_panel_to_angular_position(0.0, 0.0))
	# print(client.tracker.stow())
	# print(client.tracker.stop())
	print(client.light.get_light_status())
	print(client.light.set_light_status(True))
	print(client.light.get_light_status())
	print(client.light.set_light_status(False))
	print(client.light.get_light_status())
	print(client.tracker.get_battery_voltage())
	print(client.tracker.get_solar_panel_voltage())
	print(client.tracker.get_load_voltage())
	print(client.tracker.get_charging_current())
	print(client.tracker.get_load_current())
	print(client.tracker.get_charge_status())

	



