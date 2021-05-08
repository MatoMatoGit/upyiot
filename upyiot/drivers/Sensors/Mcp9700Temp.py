from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC
from micropython import const


class Mcp9700Temp(SensorBase):

    V_SUPPLY = 3.3
    RANGE_MAX = 1024
    OFFSET = 0.4
    DIV = 0.01

    def __init__(self, temp_pin_nr, en_supply_obj):
        self.TempAdc = ADC(Pin(temp_pin_nr))
        self.TempEn = en_supply_obj
        self.TempAdc.atten(ADC.ATTN_11DB)
        self.TempAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        val = self.TempAdc.read()
        # val = self._RawToCelsius(val)
        return val

    def Enable(self):
        self.TempEn.Enable()

    def Disable(self):
        self.TempEn.Disable()

    @staticmethod
    def _RawToCelsius(raw_temp):
        cel_temp = raw_temp * (Mcp9700Temp.V_SUPPLY / Mcp9700Temp.RANGE_MAX)
        cel_temp -= Mcp9700Temp.OFFSET
        cel_temp /= Mcp9700Temp.DIV
        return cel_temp
