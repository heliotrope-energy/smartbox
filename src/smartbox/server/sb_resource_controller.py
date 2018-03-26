#!/usr/bin/env python
from concurrent import futures

import time, grpc
from smartbox_msgs import tracker_pb2_grpc, weather_pb2_grpc, temperature_pb2_grpc, lights_pb2_grpc
from smartbox.server import tracker, light, weather, temperature


_ONE_DAY_IN_SECONDS = 60 * 60 * 24	

def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	tracker_pb2_grpc.add_TrackerControllerServicer_to_server(tracker.SmartBoxTrackerController(), server)
	weather_pb2_grpc.add_WeatherControllerServicer_to_server(weather.SmartBoxWeatherController(), server)
	temperature_pb2_grpc.add_TemperatureControllerServicer_to_server(temperature.SmartBoxTemperatureController(), server)
	lights_pb2_grpc.add_LightControllerServicer_to_server(light.SmartBoxLightController(), server)
	
	server.add_insecure_port('[::]:50051')
	server.start()
	print("Starting resource controller server")
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)
	except KeyboardInterrupt:
		server.stop(0)


if __name__ == '__main__':
	serve()


