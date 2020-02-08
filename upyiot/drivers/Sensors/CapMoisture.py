from upyiot.drivers.Sensors.SensorBase import SensorBase
from machine import Pin
from micropython import const
import time


class CapMoisture(SensorBase):

    MEASURE_TIME_MS = const(50)
    PulseCount = 0

    def __init__(self, pulse_pin_nr, en_supply_obj):
        self.FreqCounterPin = Pin(pulse_pin_nr, mode=Pin.IN)
        self.FreqCounterPin.irq(trigger=Pin.IRQ_FALLING, handler=CapMoisture._IrqHandlerFreqCounterPin)
        self.TimerEn = en_supply_obj
        return

    def Read(self):
        CapMoisture.PulseCount = 0
        self.TimerEn.Enable()
        time.sleep_ms(self.MEASURE_TIME_MS)
        self.TimerEn.Disable()
        return CapMoisture.PulseCount

    def Enable(self):
        self.TimerEn.Enable()

    def Disable(self):
        self.TimerEn.Disable()

    @staticmethod
    def _IrqHandlerFreqCounterPin(pin_obj):
        CapMoisture.PulseCount += 1

