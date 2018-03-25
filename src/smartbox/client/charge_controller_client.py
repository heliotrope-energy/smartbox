#!/usr/bin/env python
import grpc, urllib3, cv2
import numpy as np

import tracker_pb2
import tracker_pb2_grpc

class ChargeControllerClient:
	def __init__(self, channel):
		self.stub = tracker_pb2.TrackerControllerStub(self.channel)

	