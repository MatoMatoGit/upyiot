from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC
from micropython import const


class Mcp9700Temp(SensorBase):

    def __init__(self, temp_pin_nr, en_supply_obj):
        self.TempAdc = ADC(Pin(temp_pin_nr))
        self.TempEn = en_supply_obj
        self.TempAdc.atten(ADC.ATTN_11DB)
        self.TempAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        self.TempEn.Enable()
        val = self.TempAdc.read()
        self.TempEn.Disable()
        return val

    def Enable(self):
        self.TempEn.Enable()

    def Disable(self):
        self.TempEn.Disable()
