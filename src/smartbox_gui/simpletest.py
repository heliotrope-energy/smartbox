# Trying to read the actuator's position
# The north/south actuator is pin 0 on the ADC (an ADS1115),
# and the east/west actuator is pin 1.

import Adafruit_ADS1x15

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

