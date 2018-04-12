from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
from smartbox_msgs import tracker_pb2
import time, logging, os, argparse

LIGHT_OFF_VOLTAGE = 12.5
LIGHT_ON_VOLTAGE = 13.7

def get_tracker_data(client):
	data = client.tracker.get_tracker_data()
	return data.charge_controller.battery_voltage, \
			data.charge_controller.charge_current, \
				data.charge_controller.charge_state

def process_for_state(client, logger):
	batt_voltage, charge_current, charge_state = get_tracker_data(client)
	charge_state_name = tracker_pb2.ChargeState.Name(charge_state)
	is_light_on = client.light.get_light_status()
	logger.info("Battery {:.3f} Charge Current {:.3f} Charge State {} Light on? {}".format(\
		batt_voltage, charge_current, charge_state_name, is_light_on))
	
	if charge_state == tracker_pb2.FLOAT and not is_light_on:
		if batt_voltage > LIGHT_ON_VOLTAGE:
			logger.info("Charging state has reached floating, turning on light")
			client.light.set_light_status(True)
	if charge_state == tracker_pb2.BULK_CHARGE:
		if batt_voltage < LIGHT_OFF_VOLTAGE:
			logger.info("Battery has been sufficiently depleted, turning off light")
			client.light.set_light_status(False)
	if is_light_on and batt_voltage < LIGHT_OFF_VOLTAGE:
		logger.info("Battery has been sufficiently depleted, turning off light")
		client.light.set_light_status(False)

def main():
	parser = argparse.ArgumentParser(description='Battery Manager')
	parser.add_argument('--log_dir', metavar='-l', type=str, default="$HOME",
					help='Logging directory, defaults to $HOME')

	args = parser.parse_args()
	log_dir = os.path.expandvars(args.log_dir)
	log_dir = os.path.expandvars(log_dir)
	log_path = os.path.join(log_dir, "battery_manager.log")
	
	client = SmartBoxResourceControllerClient(10, "Battery Manager")
	logging.basicConfig(filename=log_path, \
		format='[%(asctime)s] %(name)s %(levelname)s: %(message)s', level=logging.INFO)
	logger = logging.getLogger(__name__)
	
	while True:
		process_for_state(client, logger)
		time.sleep(10.0)

if __name__ == "__main__":
	main()
