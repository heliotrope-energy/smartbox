#class running trackers
#one thread collecting data, one thread running trackers

import multiprocessing as mp
import random
from astronomical_singleaxis import AstronomicalTrackerSingleAxis
import time
import pandas as pd
from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
import os
import pvlib #for weather forecast and modeling

os.environ['GRPC_ENABLE_FORK_SUPPORT'] = "false"


class TrackerRunner():
    def __init__(self, trackers, datafolder, modelfolder, time_per_tracker=2, data_collection_interval = 0.05, save_interval=1, randomize=True):
        '''
            trackers: dict containing tracker classes to be run.
            datafile: folder containing data files (CSV)
            modelfolder: folder for saving models - model will be in modelfolder/trackername/timestamp
            time_per_tracker: interval for each tracker before switching
            data_collection_interval: interval for data collection, minutes
            randomize: pick trackers randomly.
        '''


        self.trackers = trackers
        self.datafolder = datafolder
        self.modelfolder = modelfolder
        self.time_per_tracker = time_per_tracker
        self.data_collection_interval = data_collection_interval
        self.randomize = randomize
        # self.save_interval = save_interval

        #list of saved dicts
        self.data = []


        self.client = SmartBoxResourceControllerClient(101)
        self.current_tracker = random.choice(list(self.trackers.keys()))

        #initialize trackers:
        for tracker_id, tracker in self.trackers.items():
            self.trackers[tracker_id] = tracker(client=self.client)


        #use this to determine when to flush data
        self.max_interval = max([self.trackers[tracker].interval for tracker in trackers.keys()])
        #
        self.save_interval = 1 # self.max_interval*2






    def compute_reward(self, start, end):
        '''
        Computes the net energy production for the given interval.
        '''
        print("computing reward from {} to {}".format(start, end))


    def collect_data(self, save_interval=60):


        data = {'time':pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York")}

        #getting charge controller data
        data['panel_voltage'] = [self.client.tracker.get_solar_panel_voltage()]
        data['charging_current'] = [self.client.tracker.get_charging_current()]
        data['battery_voltage'] = [self.client.tracker.get_battery_voltage()]
        data['load_voltage'] = [self.client.tracker.get_load_voltage()]
        data['load_current'] = [self.client.tracker.get_load_current()]
        #trackers state data
        data['current_tracker'] = [self.current_tracker]
        data['ew_angle'] = self.client.tracker.get_ew_angle()
        data['ns_angle'] = self.client.tracker.get_ns_angle()
        #TODO: weather data

        # print(self.client.weather.get_weather())

        data['wind_speed'] = None
        data['wind_direction'] = None
        data['weather_last_updated'] = None

        #TODO: weather forecast + satellite data

        return data


    def save_and_flush(self):
        '''
        Saves data to disk, flushes records.
        '''

        df = pd.DataFrame(self.data).set_index('time')
        outfile = "{}/{}.csv".format(self.datafolder, loop_counter)
        #appending
        with open(outfile, 'a') as f:
            df.to_csv(f, header=f.tell()==0)

        self.data = []

    def start(self):


        #loops collecting data, moves, saving, etc when neccessary

        loop_counter = 0

        save_interval = int(self.save_interval/self.data_collection_interval)

        #TODO: update this when tracker shifts
        tracker_interval = int(self.trackers[self.current_tracker].interval/self.data_collection_interval)

        tracker_switch_interval = int(self.time_per_tracker/self.data_collection_interval)

        #tracker interval tracking for reward function calculation

        start = pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York")

        end =  pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York")



        while True:
            dat = self.collect_data()
            self.data.append(dat)
            print(self.data)

            if loop_counter % save_interval == 0:
                print("saving data and flushing")
                self.save_and_flush()

            if loop_counter % tracker_interval == 0:
                print("doing tracker things")

                # reward = self.compute_reward(start, end)
                #
                # #update model
                # #need to save more states for SARSA?
                # # self.trackers[self.current_tracker].update_model(state, reward)
                # end = pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York")
                #
                #
                # #get environmental data from dataframe + camera archive
                # #create state object
                # state = None
                #
                # #record start time
                # start = pd.to_datetime('now').tz_localize('UTC').tz_convert("America/New_York")
                #
                # #run tracker
                # self.trackers[self.current_tracker].run_step(state)


            if loop_counter % tracker_switch_interval == 0:
                print("switching trackers")
                self.current_tracker = random.choice(list(self.trackers.keys()))
                print("new tracker: {}".format(self.current_tracker))



            loop_counter += 1
            time.sleep(self.data_collection_interval*60)
















if __name__=="__main__":
    trackers = {'astro_single': AstronomicalTrackerSingleAxis}
    runner = TrackerRunner(trackers, "data", "")
    runner.start()
