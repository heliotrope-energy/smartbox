#class for lin-ucb tracker
from tracker import Tracker
import simple_rl as rl
from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
import numpy as np

class LinUCBSingleAxis(Tracker):
    def __init__(self, client, context_size, limits = (-70, 70), alpha=0.3, bins=20,latitude=41.8240, longitude=-71.4128, interval=10):
        '''
        Initializes tracker
        '''
        super().__init__(client, latitude, longitude, interval)
        self.bins = bins
        self.name = "lin_ucb_single_axis"



        #params
        self.alpha = alpha
        self.context_size = context_size

        self.angles = np.linspace(limits[0], limits[1], num=bins)

        self.action_dict = {str(angle):angle for angle in self.angles}

        self.actions = list(self.action_dict.keys())
        #initialize learning agent
        self.agent = rl.agents.LinUCBAgent(self.actions, context_size=self.context_size, alpha=alpha)


    def run_step(self, state, prev_reward):
        '''
        Abstract method for running step
        state: OOMDPstate
        prev_reward: float
        '''
        action = self.agent.act(state, prev_reward)

        angle = self.action_dict[action]

        #move panel to location

        self.client.tracker.move_panel_to_angular_position(0.0, angle)

        return True

    def update_model(self, reward):
        '''
        updates model. The model keeps track of the previous state.
        reward: float, energy recieved in previous timestep.
        '''

        self.agent.update(reward)
        return True

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

if __name__=="__main__":
    client = SmartBoxResourceControllerClient(101, "LinUCBSingleAxis")
    tracker = LinUCBSingleAxis(client, 10, interval=3)
    #TODO: observation to state interface
    # while True:
    #     tracker.run_step(None, None)
    #     print("step finished")
    #     time.sleep(tracker.interval*60)
