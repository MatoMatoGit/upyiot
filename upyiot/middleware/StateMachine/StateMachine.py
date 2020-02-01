from upyiot.middleware.StateMachine.State import State
from upyiot.system.Service.Service import Service


class StateMachineService(Service):

    def __init__(self):
        return


class StateMachine:

    def __init__(self, states):
        self.States = states.copy()
        return

    def RegisterState(self, state):
        self.States[state] = state

    def RequestTransition(self, state_enum):
        return

    def TransitionOnEvent(self, event_id):
        return
