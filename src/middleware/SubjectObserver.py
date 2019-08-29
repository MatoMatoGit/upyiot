"""
Define a one-to-many dependency between objects so that when one object
changes state, all its dependents are notified and updated automatically.
"""

import abc


class Subject:
    """
    Know its observers. Any number of Observer objects may observe a
    subject.
    Send a notification to its observers when its state changes.
    """

    def __init__(self):
        self._observers = set()
        self._subject_state = None

    def Attach(self, observer):
        observer._subject = self
        self._observers.add(observer)

    def Detach(self, observer):
        observer._subject = None
        self._observers.discard(observer)

    def __Notify(self):
        for observer in self._observers:
            observer.update(self._subject_state)

    @property
    def State(self):
        return self._subject_state

    @State.setter
    def State(self, arg):
        self._subject_state = arg
        self._notify()


class Observer(metaclass=abc.ABCMeta):
    """
    Define an updating interface for objects that should be notified of
    changes in a subject.
    """

    def __init__(self):
        self._subject = None
        self._observer_state = None

    @abc.abstractmethod
    def Update(self, arg):
        pass