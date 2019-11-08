from micropython import const


class Pin(object):
    IRQ_FALLING = const(0)
    IRQ_RISING  = const(1)
    
    OUT = const(0)
    IN = const(1)
    
    def __init__(self, pin_nr, mode):
        self.PinNr = pin_nr
        self.Mode = mode
        self.State = 0
        self.PrevState = 0
        self.Handler = None
        return 
    
    def irq(self, trigger, handler):
        self.Trigger = trigger
        self.Handler = handler
    
    def set(self, state):
        self.PrevState = self.State
        self.State = state
        print("Prev state: {}, State: {}".format(self.PrevState, self.State))
        if self.Handler is None:
            return
        if self.PrevState and not self.State:
            if self.Trigger is Pin.IRQ_FALLING:
                print("IRQ Falling")
                self.Handler()
                
        elif not self.PrevState and self.State:
            if self.Trigger is Pin.IRQ_RISING:
                print("IRQ Rising")
                self.Handler()
 
    def get(self):
        return self.State
