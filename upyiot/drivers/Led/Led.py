from machine import Pin, PWM

class Led(object):
    PWM_FREQ = 500
    PWM_DUTY_MAX = 1023
    PWM_DUTY_MIN = 0
    
    def __init__(self, pin_nr, pwm=False):
        self.Pwm = pwm
        self.IsOn = False
        self.Pin = Pin(pin_nr, Pin.OUT)
        
        if pwm is True:
            self.Pin = PWM(self.Pin, freq=self.PWM_FREQ, duty=0)
        else:
            self.Off()
        
    def PwmFreq(self):
        return self.PWM_FREQ
    
    def PwmDutyMax(self):
        return self.PWM_DUTY_MAX
    
    def PwmDutyMin(self):
        return self.PWM_DUTY_MIN
    
    def On(self):
        if self.Pwm is True:
            self.Pin.duty(self.PWM_DUTY_MAX)
        else:
            self.Pin.on()
        
        self.IsOn = True
    
    def Off(self):
        if self.Pwm is True:
            self.Pin.duty(0)
        else:
            self.Pin.off()
            
        self.IsOn = False
        
    def Toggle(self):
        if self.IsOn is False:
            self.On()
            self.IsOn = True
        else:
            self.Off()
            self.IsOn = False
            
    def State(self):
        if self.IsOn is True:
            return 1
        else:
            return 0
    
    # Get or set the LED intensity.
    def Intensity(self, value=None):
        # Check if the LED is configured in PWM mode.
        if self.Pwm is True:
            # If a value argument is passed set the duty 
            # cycle.
            if value is not None:
                if value > self.PWM_DUTY_MAX:
                    value = self.PWM_DUTY_MAX
                elif value < self.PWM_DUTY_MIN:
                    value = self.PWM_DUTY_MIN
                self.Pin.duty(value)
            # If no value is passed get the duty cycle.
            else:
                return self.Pin.duty()
        else:
            return -1
