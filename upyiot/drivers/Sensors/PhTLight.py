from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC


class PhTLight(SensorBase):

    def __init__(self, pht_pin_nr, pht_pin_en_nr):
        self.PhTAdc = ADC(Pin(pht_pin_nr))
        self.PhTEn = Pin(pht_pin_en_nr, Pin.OUT)
        self.PhTAdc.atten(ADC.ATTN_11DB)
        self.PhTAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        self.PhTEn.on()
        val = self.PhTAdc.read()
        self.PhTEn.off()
        return val

