#testing MODBUS interface with python

#querying battery voltage
#PDU Address: 0x0008
#Logical Addr: 9
#Variable Name: Adc_va_f
#Read Holding Registers (0x03) and Read Input Registers (0x04)
#  Modbus RTU, the request message is sent from the master in this format:
#
# Slave address [1 Byte]
# Function code [1 Byte]. Allowed range is 1 to 127 (in decimal).
# Payload data [0 to 252 Bytes]
# CRC [2 Bytes]. It is a Cyclic Redundancy Check code, for error checking of the message

#ok trying again
import serial
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu

server = modbus_rtu.RtuMaster(serial.Serial(port='/dev/tty.usbserial-DO00156H', baudrate=9600, bytesize=8, parity='N', stopbits=2, xonxoff=0))
server.set_timeout(5.0)
server.set_verbose(True)

start_addr=0x0008

res = server.execute(1, cst.READ_HOLDING_REGISTERS, starting_address=start_addr,quantity_of_x=20)
vscale=100.0/32768.0
ascale=79.16/32768.0

print("battery voltage (V): {}".format(res[0]*vscale))
print("load current (A): {}".format(res[4]*ascale))
print("heatsink temp (deg C): {}".format(res[5]))
print("ambient temp (deg C): {}".format(res[6]))
