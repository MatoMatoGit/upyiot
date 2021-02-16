

class DeepSleepExceptionFailed(Exception):

    def __init__(self):
        super().__init__()


class DeepSleepBase:

    def __init__(self):
        return

    def DeepSleep(self, msec):
        raise NotImplementedError

    def DeepSleepForever(self):
        raise NotImplementedError
