from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC
from micropython import const


class VoltageSensor(SensorBase):

    RANGE_MAX = const(1024)

    VoltageToAttnMap = {
        1.0: ADC.ATTN_0DB,
        1.34: ADC.ATTN_2_5DB,
        2.0: ADC.ATTN_6DB,
        3.6: ADC.ATTN_11DB
    }

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
        for v in self.VoltageToAttnMap.keys():
            if voltage <= v:
                return self.VoltageToAttnMap[v]
        raise Exception("Voltage too high for ADC input. No attenuation level found.")
