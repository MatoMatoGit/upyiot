from upyiot.middleware.StateMachine.State import State
from upyiot.system.Service.Service import Service


class StateMachineService(Service):

    STATEMACHINE_SERVICE_MODE = Service.MODE_RUN_ONCE

    def __init__(self):
        super().__init__("statemachine", self.STATEMACHINE_SERVICE_MODE, {})


class Transition:

    def __init__(self, event_id, state_enum):
        self.EventId = event_id
        self.StateEnum = state_enum


class StateMachine(StateMachineService):

    def __init__(self, states, init_state):
        super().__init__()

        self.States = states.copy()
        self.CurrentState = init_state
        self.Pending = list()
        return

    def SvcInit(self):
        self.CurrentState.Enter()
        return

    def SvcRun(self):
        if self.Pending.count() is 0:
            return

        # Save the current list count in case new transitions are added
        # during an exit or enter function call.
        count = self.Pending.count()

        for i in range(0, count):
            # The pending transition is always removed,
            # even if it not executed.
            trans = self.Pending.pop(0)

            # Transition to the next state from an event.
            if trans.StateEnum is None:
                # Get the next state if there is one.
                next_state = self._NextStateFromEvent(trans.EventId)
                if next_state is not None:
                    self._ExecuteTransition(next_state)
                    break
            # Transition to the next state from a request.
            else:
                # Check if the transition is valid.
                if self._CheckTransition(trans.StateEnum) is True:
                    self._ExecuteTransition(trans.StateEnum)
                    break

        return

    def RegisterState(self, state):
        self.States[state] = state

    def RequestTransition(self, state_enum):
        self.Pending.append(Transition(None, state_enum))
        return

    def TransitionOnEvent(self, event_id):
        self.Pending.append(Transition(event_id, None))
        return

    def _NextStateFromEvent(self, event_id):
        for trans in self.CurrentState.Transitions.keys():
            for event in self.CurrentState.Transitions[trans]:
                if event is event_id:
                    return trans
        return None

    def _CheckTransition(self, next_state):
        for trans in self.CurrentState.Transitions.keys():
            if trans is next_state:
                return 0
        return -1

    def _ExecuteTransition(self, next_state):
        self.CurrentState.Exit()
        self.CurrentState = next_state
        self.CurrentState.Enter()
