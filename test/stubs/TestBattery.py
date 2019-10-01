
class TestBattery:

    def __init__(self):
        self.Level = 100

    def LevelSet(self, level):
        self.Level = level

    def LevelRead(self):
        print("Battery level: {}%".format(self.Level))
        return self.Level
