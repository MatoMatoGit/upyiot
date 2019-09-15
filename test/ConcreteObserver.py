from SubjectObserver import Observer


class ConcreteObserver(Observer):
    """
    Implement the SubjectObserver updating interface to keep its state
    consistent with the subject's.
    Store state that should stay consistent with the subject's.
    """

    def Update(self, arg):
        self._observer_state = arg
        # ...
    
    
from SubjectObserver import Subject

subject = Subject()
concrete_observer = ConcreteObserver()
subject.attach(concrete_observer)
subject.State = 123