from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient
import tracker_pb2

def process_for_state(client):
	charge_state = client.tracker.get_charge_status()
	is_light_on = client.light.get_light_status()
	batt_voltage = client.tracker.get_battery_voltage()

	if charge_state == tracker_pb2.FLOAT and not is_light_on:
		print("Charging state has reached floating, turning on light")
		client.light.set_light_status(True)
	if charge_state == tracker_pb2.BULK_CHARGE:
		if batt_voltage < 12.5:
			print("Battery has been sufficiently depleted, turning off light")
			client.light.set_light_status(False)

def main():
	client = SmartBoxResourceControllerClient(10)

	while True:
		process_for_state(client)

if __name__ == "__main__":
	main()
