from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin
from micropython import const
import time


class CapMoisture(SensorBase):

    STABILIZE_TIME_MS = const(100)
    MEASURE_TIME_MS = const(200)
    PulseCount = 0

    def __init__(self, pulse_pin_nr, pwr_pin_nr):
        self.FreqCounterPin = Pin(pulse_pin_nr, mode=Pin.IN)
        self.FreqCounterPin.irq(trigger=Pin.IRQ_FALLING, handler=CapMoisture._IrqHandlerFreqCounterPin)
        self.PowerPin = Pin(pwr_pin_nr, Pin.OUT)
        return

    def Read(self):
        CapMoisture.PulseCount = 0
        time.sleep_ms(self.STABILIZE_TIME_MS)
        self.PowerPin.on()
        time.sleep_ms(self.MEASURE_TIME_MS)
        self.PowerPin.off()
        return CapMoisture.PulseCount

    @staticmethod
    def _IrqHandlerFreqCounterPin(pin_obj):
        CapMoisture.PulseCount += 1

