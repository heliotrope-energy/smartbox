#implementation of single-axis astronomical tracker on SmartBox
#NOTE: using PVLib functions for testing
#NOTE: move to Dave's Grena code for dual-axis
from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient

import cv2, time, pvlib
import pandas as pd
from tracker import Tracker

class AstronomicalTrackerSingleAxis(Tracker):
    def __init__(self, client, latitude=41.8240, longitude=-71.4128, interval=10, method='nrel_numpy'):
        '''
        Initialize the client
        longitude: current longitude of panel
        latitude: current latitude of panels
        interval: how often the client moves, in minutes
        '''
        super().__init__(client, latitude, longitude, interval)
        self.method = method
        self.name = 'astronomical-single-axis'

    #NOTE: override
    def run_step(self, state=None):
        #get current date_time
        now = pd.to_datetime('now').tz_localize('UTC')

        #testing
        # test = pd.to_datetime('2018-03-27 12:31:38-04:00').tz_localize('UTC').tz_convert("America/New_York")

        # print(test)

        #TODO: check sunrise or sunset times - avoid tracking when that's happening
        #calculate solar position
        pos_data = pvlib.solarposition.get_solarposition(now, self.latitude, self.longitude)
        # print(pos_data)
        #calculate single-axis tracker position
        #TODO: figure out why it returns nans sometime
        angle_pos = pvlib.tracking.singleaxis(pos_data['apparent_zenith'], pos_data['azimuth'], backtrack=False)

        # print(angle_pos)
        print ("Desired angle: {}".format(float(angle_pos['tracker_theta'])))

        print("Moving to position")
        self.client.tracker.move_panel_to_angular_position(0.0, float(angle_pos['tracker_theta']))





if __name__ == "__main__":
    client = SmartBoxResourceControllerClient(101)
    tracker = AstronomicalTrackerSingleAxis(client, interval=10)
    while True:
        tracker.run_step()
        print("step finished")
        time.sleep(tracker.interval*60)
