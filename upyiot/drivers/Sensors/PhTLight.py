from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC


class PhTLight(SensorBase):

    def __init__(self, pht_pin_nr):
        self.PhTAdc = ADC(Pin(pht_pin_nr))
        self.PhTAdc.atten(ADC.ATTN_11DB)
        self.PhTAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        return self.PhTAdc.read()
