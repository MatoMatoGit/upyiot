from lib import AdcADS101x
from ut import PinStub
from ut import I2cStub

DonePin = PinStub.PinStub(1)

def CallbackI2cWrite():
    DonePin.set(0)
    DonePin.set(1)

AdcI2c = I2cStub.I2cStub(write_callback=CallbackI2cWrite)

Adc = AdcADS101x.AdcADS101x(5, 0xBE, DonePin, AdcI2c)

for i in range(0, 4):
    print("Reading channel {}: {}".format(i, Adc.Read(i)))



