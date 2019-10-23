import sys
sys.path.append('../src/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from module.DataExchange.MessageFormatAdapter import MessageFormatAdapter

# Other


class EndpointStub:

    def __init__(self):
        return

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        print("[Endpoint] Put message of type {}.{}: {} ".format(msg_type, msg_subtype, msg_data_dict))

    def MessageGet(self, msg_type, msg_subtype):
        print("[Endpoint] Getting message")


class test_MessageFormatAdapter(unittest.TestCase):

    def setUp(arg):
        return

    def tearDown(arg):
        return

    def test_Constructor(self):
        msg_fmt = {"arr": "", "n": 0}
        ep = EndpointStub()
        adapt = MessageFormatAdapter(ep, msg_fmt, 1, 2, MessageFormatAdapter.SEND_ON_COMPLETE)

        observer = adapt.CreateObserver("n")
        stream = adapt.CreateStream("arr")

        observer.Update(3)
        stream.write([1, 2, 3])

        observer.Update(4)
        stream.write([1, 2, 3, 4])
        return

