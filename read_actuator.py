import Adafruit_ADS1x15

# I am not sure what to do with this info! 

adc = Adafruit_ADS1x15.ADS1115()

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
GAIN  = 2/3

scale = 6.144/32767
# figure out the min and max of the actuators
# max voltage of east west is 5.18
# min voltage of east west is at 0.5
# fully retracted min 5.181
# fully expanded is 0.687

#v_per_in = 6.0/4.25

def calculate_inches(pin_num, voltage): 
    if (pin_num == 1):
        # east-west
        v_per_in = -1.335*voltage + 6.917
    if (pin_num == 0):
        #south-north
        v_per_in = -2.67*voltage + 13.83
    return v_per_in

def get_position(pin):
    value = adc.read_adc(pin, gain=GAIN)
    voltage = value * scale
    inches =  calculate_inches(pin, voltage); 
    return inches, voltage, value

# reading the info from the ith channel

while True:
    ns_pos, ns_voltage, ns_value = get_position(0)
    ew_pos, ew_voltage, ew_value = get_position(1)
    print("\t\tNorth-South\t\t\t\tEast-West")
    print("{:5f} V {:2f} inches {:f}\t{:5f} V {:2f} inches {:f}".format(ns_voltage,ns_pos,ns_value,ew_voltage,ew_pos,ew_value)) 
    #print("East-West\n\tVoltage:\t{} V\n\tPosition:\t{} inches\n\tRaw Value:\t{}".format(*get_position(1)))
   



