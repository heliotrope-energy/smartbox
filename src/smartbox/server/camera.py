import cv2

from smartbox_msgs import image_pb2
from smartbox_msgs import image_pb2_grpc

from smartbox.components.sb_camera import SmartBoxCamera

class SmartBoxCameraController(image_pb2_grpc.CameraImageControllerServicer):
	def __init__(self):
		self.camera = SmartBoxCamera()

	def get_current_image(self, request, context):
		resp = image_pb2.CameraImageResponse()
		image = self.camera.get_image()
		resp.data = cv2.imencode('.png', image)[1].tostring()
		resp.height = 480
		resp.width = 640
		return resp