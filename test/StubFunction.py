

class StubFunction:

    def __init__(self):
        self.RaiseExc = False
        self.CallCount = 0
        self.Result = None

    def SetRaiseExc(self):
        self.RaiseExc = True

    def SetResult(self, result):
        self.Result = result

    def __call__(self):
        self.CallCount += 1
        if self.RaiseExc is True:
            raise Exception
        return self.Result
