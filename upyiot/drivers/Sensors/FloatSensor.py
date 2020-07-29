from machine import Pin
from upyiot.drivers.Sensors.SensorBase import SensorBase


class FloatSensor(SensorBase):

    FloatState = 0

    def __init__(self, pin_nr):
        self.FloatPin = Pin(pin_nr, mode=Pin.IN)
        self.FloatPin.irq(trigger=(Pin.IRQ_RISING | Pin.IRQ_FALLING), handler=FloatSensor._IrqHandlerFloatSensor)
        return

    def Read(self):
        return FloatSensor.FloatState

    def Enable(self):
        FloatSensor.FloatState = self.FloatPin.value()
        return

    def Disable(self):
        return

    @staticmethod
    def _IrqHandlerFloatSensor(pin_obj):
        FloatSensor.FloatState = pin_obj.value()
