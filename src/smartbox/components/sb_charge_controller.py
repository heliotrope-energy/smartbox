import serial, logging
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
from collections import namedtuple
PORT = '/dev/ttyUSB0'

Register = namedtuple('Register', ['description', 'units', 'address', 'HI_address', 'LO_address', 'conversion_func'], verbose=True)
Register.__new__.__defaults__ = (None,) * len(Register._fields)
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

    registers = {
        "ADC_VB_F": Register(description = "Battery Voltage", units ="V", address=0x0008, conversion_func = lambda n: (n * 100 * 2**-15)),
        "ADC_VA_F": Register(description = "Array Voltage", units ="V", address=0x0009, conversion_func = lambda n: (n * 100 * 2**-15)),
        "ADC_VL_F": Register(description = "Load Voltage", units ="V", address=0x000A, conversion_func = lambda n: (n * 100 * 2**-15)),
        "ADC_IC_F": Register(description = "Charging current", units ="A", address=0x000B, conversion_func = lambda n: (n * 79.16 * 2**-15)),
        "ADC_IL_F": Register(description = "Load Current", units ="A", address=0x000C, conversion_func = lambda n: (n * 79.16 * 2**-15)),
        "T_HS": Register(description = "Heatsink temperature", units ="C", address=0x000D, conversion_func = lambda n: n),
        "T_BATT": Register(description = "Battery temperature", units ="C", address=0x000E, conversion_func = lambda n: n),
        "T_AMB": Register(description = "Ambient temperature", units ="C", address=0x000F, conversion_func = lambda n: n),
        "T_RTS": Register(description = "Remote battery temperature", units ="C", address=0x0010, conversion_func = lambda n: n),
        "CHARGE_STATE": Register(description = "Charge state", units ="C", address=0x0011, conversion_func = lambda n: n),
        "ARRAY_FAULT": Register(description = "Array fault bitfield", units ="C", address=0x0012, conversion_func = lambda n: n),
        "VB_F": Register(description = "Battery voltage, slow filter", units ="V", address=0x0013, conversion_func = lambda n: n*100*2**-15),
        "VB_REF": Register(description = "Battery regulator reference voltage", units ="V", address=0x0014, conversion_func = lambda n: n*96.667*2**-15),
        "AHC_R": Register(description = "Ah charge resettable", units ="Ah", HI_address=0x0015, LO_address=0x0016, conversion_func = lambda hi, lo: ((hi << 16) + lo) * 0.1),
        "AHC_T": Register(description = "Ah charge total", units ="Ah", HI_address=0x0017, LO_address=0x0018, conversion_func = lambda hi, lo: ((hi << 16) + lo) * 0.1),
        "KWHC": Register(description = "kWh charge (resetable?)", units ="KWh", address=0x0019, conversion_func = lambda n: n*0.1),
        "LOAD_STATE": Register(description = "Load state",  address=0x001A, conversion_func = lambda n: n),
        "LOAD_FAULT": Register(description = "Load fault bitfield",  address=0x001B, conversion_func = lambda n: n),
        "V_LVD": Register(description = "Load current compensated LVD voltage", units ="V", address=0x001C, conversion_func = lambda n: n*100*2**-15),
        "AHL_R": Register(description = "Ah load resettable", units ="Ah", HI_address=0x001D, LO_address=0x001E, conversion_func = lambda hi, lo: ((hi << 16) + lo) * 0.1),
        "AHL_T": Register(description = "Ah load total", units ="Ah", HI_address=0x001F, LO_address=0x0020, conversion_func = lambda hi, lo: ((hi << 16) + lo) * 0.1),
        "HOURMETER": Register(description = "Hourmeter", units ="h", HI_address=0x0021, LO_address=0x0022, conversion_func = lambda hi, lo: ((hi << 16) + lo) * 0.1),
        "ALARM": Register(description = "Alarm bitfield", HI_address=0x0023, LO_address=0x0024, conversion_func = lambda hi, lo: ((hi << 16) + lo)),
        "DIP_SWITCH": Register(description = "DIP switch settings",  address=0x0025, conversion_func = lambda n: n),
        "LED_STATE": Register(description = "SOC LED state",  address=0x0026, conversion_func = lambda n: n),
        "POWER_OUT": Register(description = "Charge output power",  units = "W", address=0x0027, conversion_func = lambda n: n*989.5*2**-16),
        "SWEEP_VMP": Register(description = "Array Vmp found during sweep", units="V",  address=0x0028, conversion_func = lambda n: n*100*2**-15),
        "SWEEP_PMAX": Register(description = "Array Pmax found during sweep", units="W",  address=0x0029, conversion_func = lambda n: n*989.5 * 2**-16),
        "SWEEP_VOC": Register(description = "Array Voc found during sweep", units="V",  address=0x002A, conversion_func = lambda n: n*100*2**-15),
        "VB_MIN_DAILY": Register(description = "Vb minimum voltage - daily", units="V",  address=0x002B, conversion_func = lambda n: n*100*2**-15),
        "VB_MAX_DAILY": Register(description = "Vb maximum voltage - daily", units="V",  address=0x002C, conversion_func = lambda n: n*100*2**-15),
        "AHC_DAILY": Register(description = "Ah charge - daily", units="V",  address=0x002D, conversion_func = lambda n: n * 0.1),
        "AHL_DAILY": Register(description = "Ah load - daily", units="V",  address=0x002E, conversion_func = lambda n: n * 0.1),
        "ARRAY_FAULT_DAILY": Register(description = "Array fault bitfield - daily", address=0x002F, conversion_func = lambda n: n),
        "LOAD_FAULT_DAILY": Register(description = "Load fault bitfield - daily",   address=0x0030, conversion_func = lambda n: n),
        "ALARM_DAILY": Register(description = "Alarm bitfield - daily", HI_address=0x0031, LO_address=0x0032, conversion_func = lambda hi, lo: ((hi << 16) + lo)),
        "VB_MIN": Register(description = "Minimum battery voltage", units="V",  address=0x0033, conversion_func = lambda n: n*100*2**-15),
        "VB_MAX": Register(description = "Maximum battery voltage", units="V",  address=0x0034, conversion_func = lambda n: n*100*2**-15),
        "LIGHTING_SHOULD_BE_ON": Register(description = "Lighting should be on", units="V",  address=0x0038, conversion_func = lambda n: n),
        "VA_REF_FIXED": Register(description = "Array Voltage Reference Fixed", units="V",  address=0x0039, conversion_func = lambda n: n*100*2**-15),
        "VA_REF_FIXED_PTC": Register(description = "Array Voltage Reference Fixed Percent", units="V",  address=0x003A, conversion_func = lambda n: n*100*2**-8),
    }

    def __init__(self):
        self.logger = logging.getLogger("server.components.charge_controller")
        self.logger.propagate = True
        try:
            self.server = modbus_rtu.RtuMaster(serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=2, xonxoff=0))
            self.server.set_timeout(5.0)
            self.server.set_verbose(True)
            self.start_addr=0x0008
            self.maximum_message_bytes = 256
        except modbus_tk.modbus.ModbusError as exc:
            logger.error("%s- Code=%d", exc, exc.get_exception_code())

    def is_connected(self):
        return self.server._serial.is_open

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

        for var_name, register in self.registers.items():
            if register.address is None:
                hi_offset = register.HI_address - self.start_addr
                lo_offset = register.LO_address - self.start_addr
                value = register.conversion_func(register_values[hi_offset], register_values[lo_offset])
            else:
                offset = register.address - self.start_addr
                reg_value = register_values[offset]
                value = register.conversion_func(reg_value)
            units_str = "" if register.units is None else register.units
            full_description = register.description + units_str
            data[var_name] = (full_description, value)
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
            self.logger.error("%s- Code=%d", exc, exc.get_exception_code())
        except Exception as e:
            self.logger.error("Exception thrown getting result")
            self.logger.error(e)
        return None

    def _get_all_register_values_(self):
        try:
            result = self.server.execute(1, cst.READ_HOLDING_REGISTERS, starting_address=0x0008, \
                quantity_of_x= 0x003A - self.start_addr + 1)
            return result
        except modbus_tk.modbus.ModbusError as exc:
            self.logger.error("%s- Code=%d", exc, exc.get_exception_code())
        except Exception as e:
            self.logger.error("Exception thrown getting result")
            self.logger.error(e)
        return None

    def _append_two_registers_(self, HI, LO, conversion_func):
        return conversion_func((HI << 16) + LO)


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