#!/usr/bin/env python
import grpc, urllib3, cv2
import numpy as np

import smartbox_resource_controller_pb2
import smartbox_resource_controller_pb2_grpc

from sb_tracker_client import TrackerClient
from sb_charge_controller_client import ChargeControllerClient
from sb_weather_client import WeatherClient
from sb_light_client import LightClient
from sb_panel_temperature_client import PanelTemperatureClient
from sb_camera import CameraClient


class SmartBoxResourceControllerClient():
	def __init__(self, security_level):
		self.channel = grpc.insecure_channel('138.16.161.117:50051')
		self.image_url = "http://138.16.161.117/images/image.png"
		self.stub = smartbox_resource_controller_pb2_grpc.SmartBoxResourceControllerStub(self.channel)
		self.security_level = security_level
		self.http = urllib3.PoolManager()

		self.tracker = TrackerClient(self.stub)
		self.charge_controller = ChargeControllerClient(self.stub)
		self.weather = WeatherClient()
		self.light = LightClient()
		self.panel_temps = PanelTemperatureClient()
		self.camera = CameraClient()

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
	print(client.charge_controller.get_battery_voltage())
	print(client.charge_controller.get_solar_panel_voltage())
	print(client.charge_controller.get_load_voltage())
	print(client.charge_controller.get_charging_current())
	print(client.charge_controller.get_load_current())
	print(client.charge_controller.get_charge_status())

	




