#class running trackers
#one thread collecting data, one thread running trackers

import multiprocessing as mp
import random, argparse, logging, logging.handlers, time, os
import pandas as pd
import pvlib #for weather forecast and modeling
from threading import RLock
from queue import Queue
from astronomical_singleaxis import AstronomicalTrackerSingleAxis
from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient

os.environ['GRPC_ENABLE_FORK_SUPPORT'] = "false"


class TrackerRunner():
    #def __init__(self, trackers, log_dir, datafolder, modelfolder, time_per_tracker=2, data_collection_interval = 0.05, save_interval=1, randomize=True):
    def __init__(self, trackers, log_dir, data_dir, model_dir, tracker_eval_duration, randomize):
        '''
            trackers: dict containing tracker classes to be run.
            datafile: folder containing data files (CSV)
            modelfolder: folder for saving models - model will be in modelfolder/trackername/timestamp
            time_per_tracker: interval for each tracker before switching in seconds
            randomize: pick trackers randomly.
        '''
        if trackers is None or len(trackers) == 0:
            raise Exception("Not sure what you wanted me to do without any trackers")

        self.logger = logging.getLogger(__name__)

        print("Logging data to {}".format(log_path))
        self.logger.info("Initializing tracker runner")
        self.trackers = trackers
        self.logger.info("Saving data to {}".format(data_dir))
        self.data_dir = data_dir
        self.logger.info("Saving models to {}".format(model_dir))
        self.model_dir = model_dir
        self.logger.info("Tracker eval duration {}".format(tracker_eval_duration))
        self.time_per_tracker = tracker_eval_duration
        self.logger.info("Randomize? {}".format(randomize))
        self.randomize = randomize
        
        self.data = Queue()
        self.weather_lock = RLock()
        self.tracker_status_lock = RLock()
        self.current_weather = None
        self.current_tracker_status = None

        self.current_tracker = None

        for tracker_id, tracker in self.trackers.items():
            self.trackers[tracker_id] = tracker(model_dir = self.model_dir)

        self.client = SmartBoxResourceControllerClient(11, "Tracker Runner")

    def save_and_flush(self):
        '''
        Saves data to disk, flushes records.
        '''
        data = []
        while not self.data.empty():
            data.append(self.data.get())
            print(data[-1])
        if len(data) == 0:
            return

        df = pd.DataFrame(data).set_index('time')
        path = os.path.join(self.data_dir, "data.csv")
        self.logger.info("Saving data to {}".format(path))
        if os.path.exists(path):
            df.to_csv(path, mode='a', header = False)
        else:
            df.to_csv(path)

    def on_weather(self, weather):
        with self.weather_lock:
            self.current_weather = weather

    def on_tracker_status(self, tracker_data):
        with self.tracker_status_lock:
            self.current_tracker_status = tracker_data
        data = pd.Series({'time':pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York")})

        #getting charge controller data
        data['energy_collected'] = tracker_data.charge_controller.energy_collected
        data['energy_expended'] = tracker_data.charge_controller.energy_expended
        data['panel_voltage'] = tracker_data.charge_controller.array_voltage
        data['charging_current'] = tracker_data.charge_controller.charge_current
        data['battery_voltage'] = tracker_data.charge_controller.battery_voltage
        data['load_voltage'] = tracker_data.charge_controller.load_voltage
        data['load_current'] = tracker_data.charge_controller.load_current
        #trackers state data
        data['current_tracker'] = self.current_tracker
        data['ew_angle'] = tracker_data.tracker.angle.ew
        data['ns_angle'] = tracker_data.tracker.angle.ns

        with self.weather_lock:
            weather = self.current_weather
        if weather is not None:
            data['wind_speed'] = weather.wind.speed
            data['wind_direction'] = weather.wind.direction
            data['weather_last_updated'] = weather.date

        self.data.put(data)

    def should_switch_trackers(self, start_time):
        duration = self.time_per_tracker
        time_delta = pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York") - start_time
        return time_delta.total_seconds() > duration

    def switch_current_tracker(self):
        self.logger.info("Saving remaining data")
        self.save_and_flush()
        
        if self.current_tracker:
            self.logger.info("Cleaning up previous tracker")
            old_tracker = self.trackers[self.current_tracker]
            old_tracker.cleanup()

        self.logger.info("Switching tracker from {}".format(self.current_tracker))
        self.current_tracker = random.choice(list(self.trackers.keys()))
        self.logger.info("to new tracker: {}".format(self.current_tracker))

        tracker = self.trackers[self.current_tracker]
        sleep_time = tracker.interval
        tracker_start = pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York")
        return tracker, sleep_time, tracker_start

    def check_at_night(self):
        latitude=41.8240
        longitude=-71.4128
        now = pd.to_datetime('now').tz_localize('UTC')
        tomorrow = pd.Timedelta(days=1) + now
        sunrise_set_today = pvlib.solarposition.get_sun_rise_set_transit(now, latitude, longitude)
        sunrise_set_tomorrow = pvlib.solarposition.get_sun_rise_set_transit(tomorrow, latitude, longitude)

        if (now > sunrise_set_today['sunset'] - pd.Timedelta(minutes=10))[0] or \
            (now < sunrise_set_today['sunrise'] + pd.Timedelta(minutes=10))[0]:
            return True, sunrise_set_tomorrow['sunrise'] - now + pd.Timedelta(minutes=15)
        return False, 0

    def run_nighttime_procedure(self):
        latitude=41.8240
        longitude=-71.4128

        if self.current_tracker is not None:
            tracker = self.trackers[self.current_tracker]
            self.logger.info("Cleaning up tracker {}".format(self.current_tracker))
            tracker.cleanup()
            self.current_tracker = None

        count = 0
        while not self.client.tracker.is_control_possible() and count < 10:
            count += 1
            self.logger.info("Waiting for tracker to relinquish control")
            time.sleep(1.0)

        if not self.client.tracker.is_control_possible():
            self.logger.info("I lost patience, taking control")

        with self.client.tracker.request_control() as control:
            control.stow()
        
        now = pd.to_datetime('now').tz_localize('UTC')
        tomorrow = pd.Timedelta(days=1) + now
        sunrise_set_tomorrow = pvlib.solarposition.get_sun_rise_set_transit(tomorrow, latitude, longitude)

        self.logger.info("Sunset detected, going to sleep until {}".format(sunrise_set_tomorrow['sunrise']))
        time_til_sunrise = sunrise_set_tomorrow['sunrise'] - now + pd.Timedelta(minutes=20)

        time.sleep(time_til_sunrise[0].total_seconds())

    def start(self):
        #loops collecting data, moves, saving, etc when neccessary
        self.logger.info("Subscribing to tracker status messages")
        self.client.tracker.tracker_status(self.on_tracker_status)

        self.logger.info("Subscribing to weather messages")
        self.client.weather.subscribe_weather(self.on_weather)
        
        #tracker interval tracking for reward function calculation
        self.logger.info("Selecting first tracker")
        tracker, sleep_time, tracker_start = self.switch_current_tracker()
        loop_counter = 0

        while True:
            at_night, time_til_sunrise = self.check_at_night()
            if at_night:
                self.run_nighttime_procedure()
                self.logger.info("Waking up, starting with a new tracking algorithm")
                tracker, sleep_time, tracker_start = self.switch_current_tracker()
                continue
            loop_counter += 1
            self.save_and_flush()
            self.logger.info("Running tracker step {} for tracker {}".format(loop_counter, self.current_tracker))

            with self.tracker_status_lock:
                tracker_status = self.current_tracker_status
            with self.weather_lock:
                weather = self.current_weather

            try:
                tracker.run_step(tracker_status, weather)
            except Exception as e:
                self.logger.error("Tracker {} encountered an exception during operation".format(self.current_tracker))
                self.logger.error(e, exc_info=True)

            if self.should_switch_trackers(tracker_start):
                loop_counter = 0
                tracker, sleep_time, tracker_start = self.switch_current_tracker()
            self.logger.info("Sleeping for {} seconds".format(sleep_time))
            time.sleep(sleep_time)

def expand_directory(directory):
    directory = os.path.expanduser(directory)
    return os.path.expandvars(directory)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Tracker Runner')
    parser.add_argument('--log_dir', metavar='-l', type=str, default="$HOME",
                    help='Logging directory, defaults to $HOME')
    parser.add_argument('--model_dir', metavar='-m', type=str, help="Directory for saving models", required=True)
    parser.add_argument('--data_dir', metavar='-d', type=str, help="Directory containing data files", required=True)
    parser.add_argument('--eval_duration', metavar='-e', type=float, default = 3600 , help="Duration for the evaluation of each tracker (seconds)")
    parser.add_argument('--randomize', action='store_true')
    
    args = parser.parse_args()
    log_dir = expand_directory(args.log_dir)
    model_dir = expand_directory(args.model_dir)
    data_dir = expand_directory(args.data_dir)
    eval_duration = args.eval_duration
    randomize = args.randomize

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    log_path = os.path.join(log_dir, "tracker_runner.log")
    logging.basicConfig(format='[%(asctime)s] %(name)s line: %(lineno)s %(levelname)s: %(message)s', level=logging.INFO)
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=20000000, backupCount=5)
    
    logger = logging.getLogger("root")
    logger.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s line: %(lineno)s %(levelname)s: %(message)s'))
    logger.addHandler(handler)

    trackers = {'astro_single': AstronomicalTrackerSingleAxis}
    logger.info("Initializing runner")
    runner = TrackerRunner(trackers, log_dir, data_dir, model_dir, eval_duration, randomize)
    logger.info("Starting it all")
    runner.start()
