from drivesr.Sensors.SensorBase import SensorBase
from machine import Pin
import time


class CapMoisture(SensorBase):

    PulseCount = 0

    def __init__(self, pulse_pin_nr, pwr_pin_nr):
        self.FreqCounterPin = Pin(pulse_pin_nr, mode=Pin.OUT)
        self.FreqCounterPin.irq(trigger=Pin.IRQ_FALLING, handler=self._IrqHandlerFreqCounterPin, hard=True)
        self.PowerPin = Pin(pwr_pin_nr, Pin.OUT)
        return

    def Read(self):
        self.PulseCount = 0
        self.PowerPin.on()
        time.sleep(1)
        self.PowerPin.off()
        return PulseCount

    @staticmethod
    def _IrqHandlerFreqCounterPin(pin_obj):
        global PulseCount

        PulseCount += 1
