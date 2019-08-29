import Led

class RgbLed(object):
    
    def __init__(self, pin_red, pin_green, pin_blue):
        self.Red = Led(pin_red, True)
        self.Green = Led(pin_green, True)
        self.Blue = Led(pin_blue, True)
        

    def Color(self, red, green, blue):
        self.Red.Intensity(red)
        self.Green.Intensity(green)
        self.Blue.Intensity(blue)