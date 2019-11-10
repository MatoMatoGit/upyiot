import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from upyiot.system.ExtLogging import ExtLogging

# Other


class TestStream:

    def __init__(self):
        return

    def write(self, str):
        print("[TestStream] {}".format(str))


class test_ExtLogging(unittest.TestCase):


    def setUp(arg):
        return

    def tearDown(arg):
        ExtLogging.Clear()
        return

    def test_ConfigGlobal(self):

        file = "./extlog"
        name = "test"
        text = "hi"

        ExtLogging.ConfigGlobal(level=ExtLogging.INFO, file=file, stream=TestStream())

        log = ExtLogging.LoggerGet(name)
        print(log)

        log.info(text)

        exc_occurred = False
        try:
            f = open(file, 'r')
            line = f.read()
            f.close()
        except OSError:
            exc_occurred = True

        self.assertFalse(exc_occurred)
        self.assertTrue(text in line)
        self.assertTrue(name in line)
