import cv2, logging

class SmartBoxCamera:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.logger.propagate = True
		self.cap = cv2.VideoCapture(0)
		if not self.cap.isOpened():
			self.logger.error("Imaging camera could not be opened. Calling get_image() will try " + \
				"to open it again, but this does not portend well.")
		
	def get_image(self):
		if not selp.cap.isOpened() and not self.cap.open(0):
			self.logger.error("Imaging camera could not be opened. Returning a NoneType")
			return None
		ok, fr = self.cap.read()
		fr  = cv2.flip(fr, 1) 
		cv2image = cv2.cvtColor(fr, cv2.COLOR_BGR2RGBA)
		return cv2image