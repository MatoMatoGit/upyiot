

class Singleton:

    def __init__(self):
        self.Instance = None

    def InstanceSet(self, instance):
        if self.Instance is None:
            self.Instance = instance
        else:
            raise Exception("Attempt to create multiple instances of a Singleton class.")

    def InstanceGet(self):
        return self.Instance
