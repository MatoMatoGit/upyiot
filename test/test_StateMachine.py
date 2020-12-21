import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil
from StubFunction import StubFunction

# Unit Under Test
from upyiot.middleware.StateMachine.StateMachine import StateMachine
from upyiot.middleware.StateMachine.StateMachine import Transition
from upyiot.middleware.StateMachine.State import State

# Other


class TestState(State):

    def __init__(self, enum, transitions):
        super().__init__(enum ,transitions)
        self.Enter = StubFunction()
        self.Exit = StubFunction()


class test_StateMachine(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_ServiceInit(self):

        return

