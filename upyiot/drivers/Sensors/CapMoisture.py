from machine import Pin
import time


class CapMoisture:

    PulseCount = 0

    def __init__(self, pulse_pin_obj, pwr_pin_obj):
        self.FreqCounterPin = pulse_pin_obj
        self.FreqCounterPin.irq(trigger=Pin.IRQ_FALLING, handler=self._IrqHandlerPinPulse)
        self.PowerPin = pwr_pin_obj
        return

    def Read(self):
        self.PulseCount = 0
        self.PowerPin.on()
        time.sleep(1)
        self.PowerPin.off()
        return PulseCount

    @staticmethod
    def _IrqHandlerPinPulse(pin):
        global PulseCount

        PulseCount += 1
