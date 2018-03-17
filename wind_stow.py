from gpiozero import Motor, CPUTemperature
import Adafruit_ADS1x15

TOLERANCE = 0.1
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
EW_PIN = 1
NS_PIN = 0

scale = 6.144/32767

ns_motor  = Motor(26,20)
ew_motor  = Motor(21,16)
# figure out the min and max of the actuators
# max voltage of east west is 5.18
# min voltage of east west is at 0.5
# fully retracted min 5.181
# fully expanded is 0.687

#v_per_in = 6.0/4.25

def calculate_inches(pin_num, voltage): 
    if (pin_num == NS_PIN):
        v_per_in = -1.335*voltage + 6.917
    if (pin_num == EW_PIN):
        v_per_in = -2.67*voltage + 13.83
    return v_per_in



# reading the info from the ith channel

def get_position(direction):
    value = adc.read_adc(direction, gain=GAIN)
    voltage = value * scale
    inches =  calculate_inches(direction, voltage); 
    return inches
  #  print "feedback reading: {} V, {} in {} value".format(voltage, inches, value)


def move_to_position(direction, pos):
    current_position = get_position(direction)
    motor = ew_motor if direction else ns_motor
    while abs(current_position - pos) > TOLERANCE: 
        current_position = get_position(direction)
        print("Current Pos {}\nDesired pos {}".format(current_position, pos))
        if current_position > pos:
            motor.forward(speed = 1)
        else:
            motor.backward(speed = 1)
    motor.stop()


#2.63708047731 V, 3.39649756279 in 14064 value
#feedback reading: 1.52404651021 V, 9.76079581774 in 8128 value

def stow():
    move_to_position(EW_PIN, 12/2.0)
    move_to_position(NS_PIN, 4.5)

if __name__ == "__main__":
    stow()
