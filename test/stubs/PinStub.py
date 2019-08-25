from machine import Pin

class PinStub(object):
    
    def __init__(self, default_state):
        self.State = default_state
        self.PrevState = default_state
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