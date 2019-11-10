from micropython import const
from upyiot.comm.Messaging.MessageSpecification import MessageSpecification


class ExampleMessage(MessageSpecification):

    TYPE        = const(0)
    SUBTYPE     = const(1)
    URL         = "<pn>/<id>/example"
    DATA_KEY_ARRAY  = "arr"
    DATA_KEY_N      = "n"
    DATA_DEF    = {DATA_KEY_ARRAY: "", DATA_KEY_N: 0}
    DIRECTION   = MessageSpecification.MSG_DIRECTION_BOTH

    def __init__(self):
        super().__init__(ExampleMessage.TYPE,
                         ExampleMessage.SUBTYPE,
                         ExampleMessage.DATA_DEF,
                         ExampleMessage.URL,
                         ExampleMessage.DIRECTION)

