#superclass for all tracker methods


class Tracker():
        def __init__(self, client, latitude, longitude, interval):
            self.client = client
            self.longitude = longitude
            self.latitude = latitude
            self.interval = interval
            self.name = 'TRACKER ABSTRACT'

        def run_step(self, state):
            '''
            Abstract method for running step
            '''
            return False

        def update_model(self, state, reward):
            '''
            updates model. .
            '''
            return False

        def save_model(self, outfile):
            '''
            saves the current model to outfile
            '''
            return False

        def load_model(self, outfile):
            '''
            loads model from file
            '''
            return False
