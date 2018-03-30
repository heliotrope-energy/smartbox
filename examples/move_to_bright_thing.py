"""
	This is a simple tracker that gets the current image from the server, and 
	tells the tracker to move so that the brightest thing in the image is centered.

"""


# Every program/tracker that wants to connect to the server needs to use the client
# even if it's running on the Pi.
from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
import cv2, time

class PointAtBrightThing():
	def __init__(self):
		# Connect to the client. Every invocation requires an authority level so that
		# the server can give priority access to the most important processes. 0 - 10
		# are reserved for processes running on the Pi itself. For trackers, let's use
		# something in the 100 - 200 range.
		self.client = SmartBoxResourceControllerClient(101)

		# All clients that want to move the panel need to request control. If you only
		# want data, then this is not necessary. Don't forget to relinquish control
		# on cleanup.
		if not self.client.request_control():
			raise Exception("Requesting control of tracker failed. Some other process must be using it")
		self.client.request_control()
		self.threshold = 10
		self.move_amount = 0.1

	def __del__(self):
		# After running your program, it is polite to relinquish control
		self.client.relinquish_control()

	def run(self):
		# This will grab an image as a cv2/numpy object.
		img = self.client.camera.get_image()
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		center_x = gray.shape[0] / 2.0
		center_y = gray.shape[1] / 2.0

		# Finding the brightest point in an image. This function is very problematic
		# as a noisy image or one that has a lot of whit will give it a confusing
		# signal
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

		self.processes_move(move_right, move_left, move_north, move_south)


	def process_move(self, move_right, move_left, move_north, move_south):
		# If you want the panel to move a specific amount in a direction, you will
		# need to do that calculation yourself. The panel will know how to move to 
		# an angle, move to a position, and move in a direction. It won't calculate
		# step moves for you. Use these two methods to get the current position, or 
		# similarly named methods for the angles.
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

		# The This 
		self.client.tracker.move_panel_to_linear_position(ns_pos, ew_pos)

if __name__ == "__main__":
	tracker = PointAtBrightThing()
	while True:
		tracker.run()
		time.sleep(60)