import cv2

class SmartBoxCamera:
	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		
	def get_image(self):
		ok, fr = self.cap.read()
		fr  = cv2.flip(fr, 1) 
		cv2image = cv2.cvtColor(fr, cv2.COLOR_BGR2RGBA)
		return cv2image