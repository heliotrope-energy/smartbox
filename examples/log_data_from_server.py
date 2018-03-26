from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
import sys, argparse, os, datetime, time
import pandas as pd

from smartbox_msgs import tracker_pb2


def get_tracker_data(client):
	msg = client.tracker.get_tracker_data()
	data = {}
	data['battery_voltage'] = msg.charge_controller.battery_voltage
	data['array_voltage'] = msg.charge_controller.array_voltage
	data['load_voltage'] = msg.charge_controller.load_voltage
	data['charge_current'] = msg.charge_controller.charge_current
	data['load_current'] = msg.charge_controller.load_current

	data['charge_state'] = msg.charge_controller.charge_state
	data['charge_state_label'] = \
		tracker_pb2.ChargeState.Name(msg.charge_controller.charge_state)


	data['ns_position'] = msg.tracker.position.ns
	data['ew_position'] = msg.tracker.position.ew
	data['ns_angle'] = msg.tracker.angle.ns
	data['ew_angle'] = msg.tracker.angle.ew
	data['ns_moving'] = msg.tracker.move_status.ns
	data['ew_moving'] = msg.tracker.move_status.ew 

	return data

def collect_data(output_dir, image_dir, wait_time):
	client = SmartBoxResourceControllerClient(101)
	data_frame = pd.DataFrame(columns = 
		['timestamp', 'from_epoch', 'filename',
		'battery_voltage', 'array_voltage', 'load_voltage', 
		'charge_current', 'load_current', 'charge_state',
		'charge_state_label', 'ns_position', 'ew_position',
		'ns_angle', 'ew_angle', 'ns_moving', 'ew_moving'])
	data_frame.index.names = ['index']

	while True:
		data = get_tracker_data(client)
		img = client.camera.get_image()
		
		epoch = time.time()
		dt = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
		image_filename = dt + ".np"
		data['from_epoch'] = epoch
		data['timestamp'] = dt
		data['filename'] = image_filename
		
		full_path = os.path.join(image_dir, image_filename)
		img.tofile(full_path)
		
		data_frame = data_frame.append(data, ignore_index=True)
		data_path = os.path.join(output_dir, 'data.csv')
		data_frame.to_csv(data_path)
		
		time.sleep(wait_time)

def main():
	parser = argparse.ArgumentParser(description='Store tracker data to a directory')
	parser.add_argument('--output_dir', metavar='-o', type=str,
					help='Output directory for data')
	parser.add_argument('--wait', metavar='-w', type=float, default = 60.0,
					help='Time in seconds in between data samples')
	

	args = parser.parse_args()

	output_dir = os.path.expanduser(args.output_dir)
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)
	image_dir = os.path.join(output_dir, "images")
	if not os.path.exists(image_dir):
		os.mkdir(image_dir)
	wait_time = args.wait
	collect_data(output_dir, image_dir, wait_time)


if __name__ == "__main__":
	main()
