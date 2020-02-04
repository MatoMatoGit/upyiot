from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin, ADC
from micropython import const
import time

class Mcp9700Temp(SensorBase):

    STABILIZE_TIME_MS = const(100)

    def __init__(self, temp_pin_nr, temp_en_pin_nr):
        self.TempAdc = ADC(Pin(temp_pin_nr))
        self.TempEn = Pin(temp_en_pin_nr, Pin.OUT)
        self.TempAdc.atten(ADC.ATTN_11DB)
        self.TempAdc.width(ADC.WIDTH_10BIT)

    def Read(self):
        self.TempEn.on()
        time.sleep_ms(self.STABILIZE_TIME_MS)
        val = self.TempAdc.read()
        self.TempEn.off()
        return val
