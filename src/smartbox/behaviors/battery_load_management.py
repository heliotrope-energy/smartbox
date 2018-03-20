from smartbox.sb_charge_controller import SmartBoxChargeController
from smartbox.sb_light import SmartBoxLight

def process_for_state(controller, light):
	charge_state = controller.get_charge_state()
	if charge_state == SmartBoxChargeController.FLOAT and not light.is_light_on():
		print("Charging state has reached floating, turning on light")
		light.turn_on()
	if charge_state == SmartBoxChargeController.BULK_CHARGE:
		batt_voltage = controller.get_battery_voltage()
		if batt_voltage < 12.5:
			print("Battery has been sufficiently depleted, turning off light")
			light.turn_off()

def main():
	controller = SmartBoxChargeController()
	light = SmartBoxLight()

	while True:
		process_for_state(controller, light)

if __name__ == "__main__":
	main()
