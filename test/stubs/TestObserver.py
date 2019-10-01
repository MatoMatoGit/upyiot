from middleware.SubjectObserver.SubjectObserver import Observer

class TestObserver(Observer):
    """
    Implement the SubjectObserver updating interface to keep its state
    consistent with the subject's.
    Store state that should stay consistent with the subject's.
    """
    
    def Update(self, arg):
        self.State = arg
