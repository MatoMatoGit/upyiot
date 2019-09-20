
class RTC(object):
    
    DateTime = 0
    
    def __init__(self):
        return 
    
    def now(self):
        return self.DateTime
    
    def datetime(self, date_time):
        self.DateTime = date_time
        print(self.DateTime)
