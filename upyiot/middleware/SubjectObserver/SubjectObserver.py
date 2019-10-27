"""
Define a one-to-many dependency between objects so that when one object
changes state, all its dependents are notified and updated automatically.
"""

class Subject(object):
    """
    Know its observers. Any number of Observer objects may observe a
    subject.
    Send a notification to its observers when its state changes.
    """

    def __init__(self):
        self._Observers = set()
        self._State = None

    def Attach(self, observer):
        observer._Subject = self
        self._Observers.add(observer)

    def Detach(self, observer):
        observer._Subject = None
        self._Observers.discard(observer)
    
    @property
    def ObserverCount(self):
        return len(self._Observers)
    
    @property
    def State(self):
        return self._State
    
    @State.setter
    def State(self, value):
        self._State = value
        self._Notify()
        
    def _Notify(self):
        for observer in self._Observers:
            observer.Update(self._State)

class Observer(object):
    """
    Define an updating interface for objects that should be notified of
    changes in a subject.
    """

    def __init__(self):
        self._Subject = None

    def Update(self, arg):
        pass
    
    def Subject(self):
        return self._Subject
