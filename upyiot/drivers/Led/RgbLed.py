from upyiot.drivers.Led.Led import Led
from micropython import const


class RgbLed:

    RGB_COLOR_RED   = const(0)
    RGB_COLOR_GREEN = const(1)
    RGB_COLOR_BLUE  = const(2)

    def __init__(self, pin_red, pin_green, pin_blue):
        self.Red = Led(pin_red, True)
        self.Green = Led(pin_green, True)
        self.Blue = Led(pin_blue, True)

    def ColorSet(self, color, value):
        if color is self.RGB_COLOR_RED:
            self.Red.Intensity(value)
        elif color is self.RGB_COLOR_GREEN:
            self.Green.Intensity(value)
        elif color is self.RGB_COLOR_BLUE:
            self.Blue.Intensity(value)

    def ColorsSet(self, red, green, blue):
        self.Red.Intensity(red)
        self.Green.Intensity(green)
        self.Blue.Intensity(blue)

    def On(self):
        self.Red.On()
        self.Green.On()
        self.Blue.On()

    def Off(self):
        self.Red.Off()
        self.Green.Off()
        self.Blue.Off()
