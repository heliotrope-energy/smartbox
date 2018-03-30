from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
import cv2, time

class PointAtBrightThing():
	def __init__(self):
		self.client = SmartBoxResourceControllerClient()
		self.threshold = 10
		self.move_amount = 0.1

	def run(self):
		img = self.client.camera.get_image()
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		center_x = gray.shape[0] / 2.0
		center_y = gray.shape[1] / 2.0

		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

		move_right = False
		move_left = False
		move_north = False
		move_south = False
		if maxLoc[0] > center_x + self.threshold:
			move_right = True
		elif maxLoc[0] < center_x - self.threshold:
			move_left = True

		if maxLoc[1] > center_y + self.threshold:
			move_north = True
		if maxLoc[1] < center_y - self.threshold:
			move_south = True


	def process_move(self, move_right, move_left, move_north, move_south):
		ns_pos = self.client.tracker.get_ns_position()
		ew_pos = self.client.tracker.get_ew_position()
		if move_right:
			ew_pos += self.move_amount
		if move_left:
			ew_pos -= self.move_amount
		if move_north:
			ns_pos += self.move_amount
		if move_south:
			ns_pos -= self.move_amount
		self.client.move_panel_to_linear_position(ns_pos, ew_pos)

if __name__ == "__main__":
	tracker = PointAtBrightThing()
	while True:
		tracker.run()
		time.sleep(60)