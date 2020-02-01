

class State:

    def __init__(self, enum, transitions):
        """

        :param enum: Enumeration, a unique number to identify this state.
        :param transitions: (opt.) State transition dictionary. Must have the following
        structure:
        { <to_state_0>: [<event_id>, ..],
          <to_state_1>: [<event_id>, ..],
        }

        """
        self.Id = enum
        self.Transitions = transitions
        return

    def Enter(self):
        pass

    def Execute(self):
        pass

    def Exit(self):
        pass

