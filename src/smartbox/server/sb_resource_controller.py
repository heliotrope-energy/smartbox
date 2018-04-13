#!/usr/bin/env python
from concurrent import futures
import argparse, os

import time, grpc
from smartbox_msgs import tracker_pb2_grpc, weather_pb2_grpc, temperature_pb2_grpc, \
	lights_pb2_grpc, image_pb2_grpc
from smartbox.server import tracker, light, weather, temperature, camera
import logging, logging.handlers
from tls_smtp_handler import TlsSMTPHandler
_ONE_DAY_IN_SECONDS = 60 * 60 * 24	

def serve(log_dir):
	log_path = os.path.join(log_dir, "resource_controller.log")
	logging.basicConfig(format='[%(asctime)s] %(name)s %(levelname)s: %(message)s', level=logging.INFO)
	handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=20000000, backupCount=5)
	
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s'))
	logger.addHandler(handler)
	# gm = TlsSMTPHandler(("smtp.gmail.com", 587), 'heliotrope.bugger@gmail.com', ['brawner@gmail.com'], 'Server is not having a good day', ('heliotrope.bugger@gmail.com', 's6u#jW^8gMYUV^bf'))
	# gm.setLevel(logging.ERROR)
	# logger.addHandler(gm)

	
	logger.info("Initializing gRPC server")
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

	logger.info("Adding TrackerControllerServicer")
	tracker_pb2_grpc.add_TrackerControllerServicer_to_server(tracker.SmartBoxTrackerController(), server)
	
	logger.info("Adding WeatherControllerServicer")
	weather_pb2_grpc.add_WeatherControllerServicer_to_server(weather.SmartBoxWeatherController(), server)
	
	logger.info("Adding TemperatureControllerServicer")
	temperature_pb2_grpc.add_TemperatureControllerServicer_to_server(temperature.SmartBoxTemperatureController(), server)
	
	logger.info("Adding LightControllerServicer")
	lights_pb2_grpc.add_LightControllerServicer_to_server(light.SmartBoxLightController(), server)
	
	logger.info("Adding CameraControllerServicer")
	image_pb2_grpc.add_CameraControllerServicer_to_server(camera.SmartBoxCameraController(), server)
	
	logger.info("Binding port 50051")
	server.add_insecure_port('[::]:50051')
	server.start()
	
	logger.info("Starting resource controller server")
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)
	except KeyboardInterrupt:
		server.stop(0)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Store tracker data to a directory')
	parser.add_argument('--log_dir', metavar='-l', type=str, default="$HOME",
					help='Logging directory, defaults to $HOME')

	args = parser.parse_args()
	log_dir = os.path.expanduser(args.log_dir)
	log_dir = os.path.expandvars(log_dir)
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	serve(log_dir)


