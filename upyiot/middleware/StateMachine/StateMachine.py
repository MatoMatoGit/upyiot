from upyiot.middleware.StateMachine.State import State
from upyiot.system.Service.Service import Service


class StateMachineService(Service):

    SENSOR_SERVICE_MODE = Service.MODE_RUN_ONCE

    def __init__(self):
        super().__init__("statemachine", self.SENSOR_SERVICE_MODE, {})


class StateMachine(StateMachineService):

    def __init__(self, states):
        super().__init__()

        self.States = states.copy()
        return

    def SvcInit(self):
        return

    def SvcRun(self):


    def RegisterState(self, state):
        self.States[state] = state

    def RequestTransition(self, state_enum):
        return

    def TransitionOnEvent(self, event_id):
        return
