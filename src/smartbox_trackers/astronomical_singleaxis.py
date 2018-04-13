#implementation of single-axis astronomical tracker on SmartBox
#NOTE: using PVLib functions for testing
#NOTE: move to Dave's Grena code for dual-axis
from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
from smartbox.client.tracker_controller import ControlDisruption
import cv2, time, pvlib, logging
import pandas as pd
from tracker import Tracker

class AstronomicalTrackerSingleAxis(Tracker):
    def __init__(self, latitude=41.8240, longitude=-71.4128, interval=60, method='nrel_numpy', *args, **kwargs):
        '''
        Initialize the client
        longitude: current longitude of panel
        latitude: current latitude of panels
        interval: how often the client moves, in seconds
        '''
        client = SmartBoxResourceControllerClient(101, "AstronomicalTrackerSingleAxis")
        super().__init__(client, latitude, longitude, interval)
        self.method = method
        self.name = 'astronomical-single-axis'
        self.logger = logging.getLogger("root.runner.astronomical-single-axis")
        self.logger.propagate = True
        print(self.logger.name)
        print(self.logger.parent.name)
        self.control = None

    #NOTE: override
    def run_step(self, *args):
        if self.control is None or not self.control.in_control():
            if not self.client.tracker.is_control_possible():
                self.logger.info("Attempting to get control of tracker, but it's not possible")
                return
            try:
                self.control = self.client.tracker.request_control()
            except ControlDisruption as e:
                self.logger.error("We tried to get control, but it failed")
                return

        now = pd.to_datetime('now').tz_localize('UTC')
        self.logger.info("Setting tracker position for UTC time {}".format(now))
        #get current date_time
        pos_data = pvlib.solarposition.get_solarposition(now, self.latitude, self.longitude)

        self.logger.info("Sun position is: Azimuth {} Elevation {}".format(pos_data['azimuth'], pos_data['elevation']))
        angle_pos = pvlib.tracking.singleaxis(pos_data['apparent_zenith'], pos_data['azimuth'], backtrack=False)

        self.logger.info("Moving panel to: {}".format(angle_pos['tracker_theta']))
        self.control.move_panel_to_angular_position(0.0, float(angle_pos['tracker_theta']))

        #testing
        # test = pd.to_datetime('2018-03-27 12:31:38-04:00').tz_localize('UTC').tz_convert("America/New_York")

        # print(test)

        #TODO: check sunrise or sunset times - avoid tracking when that's happening
        #calculate solar position
        # print(pos_data)
        #calculate single-axis tracker position
        #TODO: figure out why it returns nans sometime
        
        # print(angle_pos)

    def cleanup(self):
        if self.control:
            self.control.release()




if __name__ == "__main__":
    client = SmartBoxResourceControllerClient(101, "AstronomicalTrackerSingleAxis")
    tracker = AstronomicalTrackerSingleAxis(client, interval=10)
    while True:
        tracker.run_step()
        print("step finished")
        time.sleep(tracker.interval*60)
