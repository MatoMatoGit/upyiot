from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin
import time


class CapMoisture(SensorBase):

    PulseCount = 0

    def __init__(self, pulse_pin_nr, pwr_pin_nr):
        self.FreqCounterPin = Pin(pulse_pin_nr, mode=Pin.IN)
        self.FreqCounterPin.irq(trigger=Pin.IRQ_FALLING, handler=CapMoisture._IrqHandlerFreqCounterPin)
        self.PowerPin = Pin(pwr_pin_nr, Pin.OUT)
        return

    def Read(self):
        CapMoisture.PulseCount = 0
        self.PowerPin.on()
        time.sleep(1)
        self.PowerPin.off()
        return CapMoisture.PulseCount

    @staticmethod
    def _IrqHandlerFreqCounterPin(pin_obj):
        CapMoisture.PulseCount += 1

