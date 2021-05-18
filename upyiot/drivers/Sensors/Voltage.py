from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC
from micropython import const


class VoltageSensor(SensorBase):

    RANGE_MAX = const(1024)

    NUM_VOLTAGES = const(4)
    VoltageList = [1.0, 1.34, 2.0, 3.6]
    AttenuationList = [ADC.ATTN_0DB, ADC.ATTN_2_5DB, ADC.ATTN_6DB, ADC.ATTN_11DB]

    def __init__(self, pin_nr: int, en_supply_obj=None, max_voltage: float = 3.3):
        self.VoltAdc = ADC(Pin(pin_nr))
        self.Supply = en_supply_obj

        self.VoltAdc.atten(self._VoltageToAttenuation(max_voltage))
        self.VoltAdc.width(ADC.WIDTH_12BIT)

    def Read(self):
        val = self.VoltAdc.read()
        # val = self._RawToVoltage(val)
        return val

    def Enable(self):
        self._EnableSupply()

    def Disable(self):
        self._DisableSupply()

    def _RawToVoltage(self, raw):
        volt = raw * (3.3 / self.RANGE_MAX)
        return volt

    def _EnableSupply(self):
        if self.Supply is not None:
            self.Supply.Enable()

    def _DisableSupply(self):
        if self.Supply is not None:
            self.Supply.Disable()

    def _VoltageToAttenuation(self, voltage: float):
        for i in range(0, self.NUM_VOLTAGES):
            if voltage <= self.VoltageList[i]:
                print("[VoltSensor] Selected attenuation {}, max voltage {}".format(self.AttenuationList[i], self.VoltageList[i]))
                return self.AttenuationList[i]
        raise Exception("Voltage too high for ADC input. No attenuation level found.")
