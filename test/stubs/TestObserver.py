from upyiot.middleware.SubjectObserver.SubjectObserver import Observer


class TestObserver(Observer):

    def __init__(self):
        super().__init__()
        self.UpdateCount = 0
    """
    Implement the SubjectObserver updating interface to keep its state
    consistent with the subject's.
    Store state that should stay consistent with the subject's.
    """
    
    def Update(self, arg):
        self.UpdateCount += 1
        self.State = arg
