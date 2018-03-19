import serial
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu

PORT = '/dev/ttyUSB0'


registers = {
    0x0008: ["Battery Voltage", "V",lambda n: (n * 100 * 2**-15)],
    0x0009: ["Array voltage", "V", lambda n: (n * 100 * 2**-15)],
    0x000A: ["Load Voltage", "V", lambda n: (n * 100 * 2 ** -15)],
    0x000B: ["Charging current", "A", lambda n: (n * 79.16 * 2**-15)],
    0x000C: ["Load Current", "C", lambda n: (n * 79.16 * 2 ** -15)],
    0x000D: ["Heatsink temperature","C", lambda n: (n)],
    0x000E: ["Battery temperature", "C", lambda n: (n)],
    0x000F: ["Ambient temperature", "C", lambda n: (n)],
    0x0010: ["Remote battery temperature", "C", lambda n: (n)],
    0x0011: ["Charge state", None, lambda n: n],
    0x0012: ["Array fault bitfield", None, lambda n: n],
    0x0013: ["Battery voltage, slow filter", "V", lambda n: n*100*2**-15],
    0x0014: ["Battery regulator reference voltage", "V", lambda n: n*96.667*2**-15],
    0x0015: ["Ah charge resetable, HI word", "Ah", lambda n: n * 0.1],
    0x0016: ["Ah charge resetable, LO word", None, lambda n: n],
    0x0017: ["Ah charge total, HI word", "Ah", lambda n: n * 0.1],
    0x0018: ["Ah charge total, LO word", None, lambda n: n],
    0x0019: ["kWh charge (resetable?)", "kWh", lambda n: n*0.1],
    0x001A: ["Load state", None, lambda n: n],
    0x001B: ["Load fault bitfield", None, lambda n: n],
    0x001C: ["Load current compensated LVD voltage", "V", lambda n: n*100*2**-15],
    0x001D: ["Ah load resetable, HI word", "Ah", lambda n: n*0.1],
    0x001E: ["Ah load resetable, LO word", None, lambda n: n],
    0x001F: ["Ah load total, HI word", "Ah", lambda n: n*0.1],
    0x0020: ["Ah load total, LO word", None, lambda n: n],
    0x0021: ["hourmeter, HI word","Ah", lambda n: n*0.1],
    0x0022: ["hourmeter, LO word", None, lambda n: n],
    0x0023: ["alarm bitfield - HI word", None, lambda n: n],
    0x0024: ["alarm bitfield - LO word", None, lambda n: n],
    0x0025: ["dip switch settings", None, lambda n: n],
    0x0026: ["SOC LED state", None, lambda n: n],
    0x0027: ["Charge output power", "W", lambda n: n*989.5*2**16],
    0x0028: ["Array Vmp found during sweep", "V", lambda n: n*100*2**-15],
    0x0029: ["Array Pmax(output) found during sweep", "W", lambda n: n*989.5 * 2**16],
    0x002A: ["Array Voc found during sweep", "V", lambda n: n * 100 * 2 **-15],
    0x002B: ["Vb minimum voltage - daily", "V", lambda n: n * 100 * 2**-15],
    0x002C: ["Vb maximum voltage - daily", "V", lambda n: n * 100 * 2 ** -15],
    0x002D: ["Ah charge - daily", "Ah", lambda n: n * 0.1],
    0x002E: ["Ah load - daily", "Ah", lambda n: n * 0.1],
    0x002F: ["Array fault bitfield - daily", None, lambda n: n],
    0x0030: ["Load fault bitfield - daily", None, lambda n: n],
    0x0031: ["alarm bitfield - daily, HI word", None, lambda n: n],
    0x0032: ["alarm bitfield - daily, LO word", None, lambda n: n],
    0x0033: ["Minimum battery voltage", "V", lambda n: n*100*2**-15],
    0x0034: ["Maximum battery voltage", "V", lambda n: n * 100 * 2 **-15],
}

charge_states = {
    0: "START",
    1: "NIGHT_CHECK",
    2: "DISCONNECT",
    3: "NIGHT",
    4: "FAULT",
    5: "BULK_CHARGE",
    6: "ABSORBTION",
    7: "FLOAT",
    8: "EQUALIZE"
}

class SmartBoxChargeController:
    START = 0
    NIGHT_CHECK = 1
    DISCONNECT = 2
    NIGHT = 3
    FAULT = 4
    BULK_CHARGE = 5
    ABSORBTION = 6
    FLOAT = 7
    EQUALIZE = 8

    def __init__(self):
        self.server = modbus_rtu.RtuMaster(serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=2, xonxoff=0))
        self.server.set_timeout(5.0)
        self.server.set_verbose(True)
        self.start_addr=0x0008
        self.maximum_message_bytes = 256

    def get_battery_voltage(self):
        return self._get_register_(0x0008, registers[0x0008][2])

    def get_solar_panel_voltage(self):
        return self._get_register_(0x0009, registers[0x0009][2])

    def get_load_voltage(self):
        return self._get_register_(0x000A, registers[0x000A][2])

    def get_charging_current(self):
        return self._get_register_(0x000B, registers[0x000B][2])

    def get_load_current(self):
        return self._get_register_(0x000C, registers[0x000C][2])

    def get_charge_state_name(self):
        """
            TODO, this reg value actually hase 8 different states
        """
        value = self._get_register_(0x0011, registers[0x0011][2])
        return charge_states[value]

    def get_charge_state(self):
        value = self._get_register_(0x0011, registers[0x0011][2])
        return value

    def get_all_data(self):
        register_values = self._get_all_register_values_()
        data = {}
        if register_values is None:
            return data

        for addr, (desc, units, conversion) in registers.items():
            offset = addr - self.start_addr
            reg_value = register_values[offset]
            full_description = desc + " " + units
            data[full_description] = conversion(reg_value)
        return data

    def _get_register_(self, address, conversion_func, default_value = 0.0):
        reg_value = self._get_register_value_(address)
        if reg_value is not None:
            return conversion_func(reg_value)
        return default_value

    def _get_register_value_(self, address):
        try:
            result =self.server.execute(1, cst.READ_HOLDING_REGISTERS, starting_address=address, \
                quantity_of_x= 1)
            return result[0]
        except modbus_tk.modbus.ModbusError as exc:
            print("%s- Code=%d", exc, exc.get_exception_code())
        except Exception as e:
            print("Exception thrown getting result")
        return None

    def _get_all_register_values_(self):
        try:
            result = self.server.execute(1, cst.READ_HOLDING_REGISTERS, starting_address=0x0008, \
                quantity_of_x= 0x0034 - self.start_addr + 1)
            return result
        except modbus_tk.modbus.ModbusError as exc:
            print("%s- Code=%d", exc, exc.get_exception_code())
        except Exception as e:
            print("Exception thrown getting result")
        return None



def main():
    """main"""
    logger = modbus_tk.utils.create_logger("console")

    try:
        #Connect to the slave
        master = modbus_rtu.RtuMaster(
            serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        )
        master.set_timeout(5.0)
        master.set_verbose(True)
        logger.info("connected")

        logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 3))

        #send some queries
        logger.info(master.execute(1, cst.READ_COILS, 0, 10))
        logger.info(master.execute(1, cst.READ_DISCRETE_INPUTS, 0, 8))
        logger.info(master.execute(1, cst.READ_INPUT_REGISTERS, 100, 3))
        logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 100, 12))
        #logger.info(master.execute(1, cst.WRITE_SINGLE_COIL, 7, output_value=1))
        #logger.info(master.execute(1, cst.WRITE_SINGLE_REGISTER, 100, output_value=54))
        #logger.info(master.execute(1, cst.WRITE_MULTIPLE_COILS, 0, output_value=[1, 1, 0, 1, 1, 0, 1, 1]))
        #logger.info(master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 100, output_value=xrange(12)))

    except modbus_tk.modbus.ModbusError as exc:
        logger.error("%s- Code=%d", exc, exc.get_exception_code())

if __name__ == "__main__":
    main()