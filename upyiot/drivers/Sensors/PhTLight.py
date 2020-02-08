from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC


class PhTLight(SensorBase):

    def __init__(self, pht_pin_nr, en_supply_obj):
        self.PhTAdc = ADC(Pin(pht_pin_nr))
        self.PhTEn = en_supply_obj
        self.PhTAdc.atten(ADC.ATTN_11DB)
        self.PhTAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        self.PhTEn.Enable()
        val = self.PhTAdc.read()
        self.PhTEn.Disable()
        return val


    def Enable(self):
        self.PhTEn.Enable()

    def Disable(self):
        self.PhTEn.Disable()
