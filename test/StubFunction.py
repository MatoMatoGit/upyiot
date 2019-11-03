

class StubFunction:

    def __init__(self, func=None, exc=None):
        self.RaiseExc = False
        self.CallCount = 0
        self.Func = func
        self.Result = None
        self.Exc = exc

    def RaiseExcSet(self):
        self.RaiseExc = True

    def ResultSet(self, result):
        self.Result = result

    def __call__(self):
        self.CallCount += 1
        print("[StubFunc] Call count: {}".format(self.CallCount))
        if self.Func is not None:
            print("[StubFunc] Calling function: {}".format(self.Func))
            self.Func(self)
        if self.RaiseExc is True:
            print("[StubFunc] Raising exception")
            if self.Exc is None:
                raise Exception
            else:
                raise self.Exc
        return self.Result
