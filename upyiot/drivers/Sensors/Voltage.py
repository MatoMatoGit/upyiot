from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC
from micropython import const


class VoltageSensor(SensorBase):

    RANGE_MAX = const(1024)

    def __init__(self, pin_nr, en_supply_obj):
        self.VoltAdc = ADC(Pin(pin_nr))
        self.Supply = en_supply_obj
        self.VoltAdc.atten(ADC.ATTN_11DB)
        self.VoltAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        self.Supply.Enable()
        val = self.VoltAdc.read()
        val = self._RawToVoltage(val)
        self.Supply.Disable()
        return val

    def Enable(self):
        self.Supply.Enable()

    def Disable(self):
        self.Supply.Disable()

    def _RawToVoltage(self, raw):
        volt = raw * (self.Supply.Voltage / self.RANGE_MAX)
        return volt
