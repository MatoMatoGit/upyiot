

class DriverBase:

    def __init__(self, supply=None):
        self.En = supply

    def Enable(self):
        pass

    def Disable(self):
        pass

    def IsEnabled(self):
        return True
