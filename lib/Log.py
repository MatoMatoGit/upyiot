
class Log:
    
    def __init__(self, module, enabled):
        self.Module = module
        self.Enabled = enabled
    
    def Print(self, message, func = ""):
        if (self.Enabled == False):
            return 
        
        if (len(func) > 1):
            print("[{}] [{}] {}".format(self.Module, func, message))
        else:
            print("[{}] {}".format(self.Module, message))