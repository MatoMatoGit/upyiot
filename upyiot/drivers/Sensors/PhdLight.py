from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC


class PhdLight(SensorBase):

    def __init__(self, phd_pin_nr):
        self.PhdAdc = ADC(Pin(phd_pin_nr))
        self.PhdAdc.atten(ADC.ATTN_11DB)
        self.PhdAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        return self.PhdAdc.read()
