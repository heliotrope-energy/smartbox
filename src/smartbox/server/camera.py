import cv2, logging

from smartbox_msgs import image_pb2
from smartbox_msgs import image_pb2_grpc

from smartbox.components.sb_camera import SmartBoxCamera

class SmartBoxCameraController(image_pb2_grpc.CameraControllerServicer):
	def __init__(self):
		self.camera = SmartBoxCamera()
		self.logger = logging.getLogger(__name__)

	def get_current_image(self, request, context):
		self.logger.info("Image request received")
		resp = image_pb2.CameraImageResponse()
		try:
			image = self.camera.get_image()
		except Exception as e:
			self.logger.error("Getting camera image failed, hope they are ok with an empty response")
			self.logger.error(e, exc_info=True)
			return resp
		resp.data = cv2.imencode('.png', image)[1].tostring()
		resp.height = 480
		resp.width = 640
		return resp