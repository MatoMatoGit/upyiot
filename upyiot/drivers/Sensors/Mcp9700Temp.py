from drivesr.Sensors.SensorBase import SensorBase
from machine import Pin, ADC


class Mcp9700Temp(SensorBase):

    def __init__(self, temp_pin_nr):
        self.TempAdc = ADC(Pin(temp_pin_nr))
        self.TempAdc.atten(ADC.ATTN_11DB)
        self.TempAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        return self.TempAdc.read()
