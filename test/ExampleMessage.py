from micropython import const
from module.DataExchange.MessageSpecification import MessageSpecification


class ExampleMessage(MessageSpecification):

    TYPE        = const(0)
    SUBTYPE     = const(1)
    URL         = "<pn>/<id>/example"
    DATA_DEF    = {"arr": "", "n": 0}
    DIRECTION   = const(1)

    def __init__(self):
        super().__init__(ExampleMessage.TYPE,
                         ExampleMessage.SUBTYPE,
                         ExampleMessage.DATA_DEF,
                         ExampleMessage.URL,
                         ExampleMessage.DIRECTION)

