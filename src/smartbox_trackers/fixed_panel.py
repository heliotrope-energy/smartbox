#not really a tracker, but a good baseline.
from tracker import Tracker
from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
import time

class FixedPanel(Tracker):

    def __init__(self, client, angle, threshold=1, latitude=41.8240, longitude=-71.4128, interval = 10):
        '''
        Initializes fixedpanel
        angle: desired angle
        threshold: acceptable threshold for not moving
        '''

        super().__init__(client, latitude, longitude, interval)
        self.angle = angle
        self.threshold = threshold


    def run_step(self, state, prev_reward):
        '''
        Moves panel to angle.
        '''

        current_angle = self.client.tracker.get_ew_angle()

        #check current angle, only move if it's a threshold
        if abs(current_angle - self.angle) > self.threshold:
            print("moving to {} deg".format(self.angle))
            self.client.tracker.move_panel_to_angular_position(0.0, self.angle)

        return True


if __name__=="__main__":
    client = SmartBoxResourceControllerClient(101, "Fixed Panel")
    tracker = FixedPanel(client, angle = 30, interval=10)
    while True:
        tracker.run_step(None, None)
        print("step finished")
        time.sleep(tracker.interval*60)
