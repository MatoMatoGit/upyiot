import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from middleware.ExtLogging import ExtLogging
from middleware.ExtLogging.ExtLogging import ExtLogger

# Other

class test_ExtLogging(unittest.TestCase):


    def setUp(arg):
        return

    def tearDown(arg):
        return

    def test_ConfigGlobal(self):

        ExtLogging.ConfigGlobal(level=logging.INFO, file="./log")

        log = ExtLogger("test")

        log.info("hi")

ConfigGlobal(level=DEBUG, file="./log")

log = ExtLogger("test")

log.info("hi")

log.debug("hoi")