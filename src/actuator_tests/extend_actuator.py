import RPi.GPIO as g
import signal
import sys

import Adafruit_ADS1x15 as ads

def sigint_handler(signum, frame):
	g.cleanup()
	print "cleaning up and exiting"
	sys.exit(0)
	
	
signal.signal(signal.SIGINT, sigint_handler)

direction = raw_input('e for extend, r for retract, anything else for nothing: ')


GAIN = 2/3

scale = 6.144/32767

v_per_in = 6.0/4.25

EXTEND_PIN = 21
RETRACT_PIN = 16

g.setmode(g.BCM)

adc = ads.ADS1115()

g.setup(EXTEND_PIN, g.OUT)
g.setup(RETRACT_PIN, g.OUT)

g.output(RETRACT_PIN, g.HIGH)
g.output(EXTEND_PIN, g.HIGH)

if direction == 'e':
	g.output(EXTEND_PIN, g.LOW)
elif direction == 'r':
	g.output(RETRACT_PIN, g.LOW)




while True:
	feedback = adc.read_adc(0, gain=GAIN)

	voltage = feedback * scale
	inches = voltage * v_per_in - 0.013
	print "feedback reading: {} V, {} in".format(voltage, inches)
	
