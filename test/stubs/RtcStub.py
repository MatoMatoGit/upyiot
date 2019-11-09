
class RTC(object):
    
    DateTime = 0
    
    def __init__(self):
        self.DateTime = 0
        return 

    def datetime(self, date_time):
        if date_time is None:
            return self.DateTime
        self.DateTime = date_time
        print(self.DateTime)
