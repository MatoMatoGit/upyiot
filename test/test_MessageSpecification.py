import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from module.Messaging.MessageSpecification import MessageSpecification

# Other
from micropython import const

class test_MessageSpecification(unittest.TestCase):

    UrlFields = {"<id>": "4a6f", "<pn>": "smartsensor"}

    TYPE        = const(0)
    SUBTYPE     = const(1)
    DATA_KEY_ARRAY  = "arr"
    DATA_KEY_N      = "n"
    DATA_DEF    = {DATA_KEY_ARRAY: "", DATA_KEY_N: 0}
    DIRECTION   = MessageSpecification.MSG_DIRECTION_BOTH

    def setUp(self):
        MessageSpecification.Config(self.UrlFields)
        return

    def tearDown(self):
        return

    def test_Config(self):
        self.assertEqual(MessageSpecification.UrlFields, self.UrlFields)

    def test_ConstructorNoUrlFieldSubstitution(self):
        url = "/sensor/temp"
        msg_spec = MessageSpecification(self.TYPE, self.SUBTYPE,
                                        self.DATA_DEF, url, self.DIRECTION)

        self.assertEqual(msg_spec.Type, self.TYPE)
        self.assertEqual(msg_spec.Subtype, self.SUBTYPE)
        self.assertEqual(msg_spec.DataDef, self.DATA_DEF)
        self.assertEqual(msg_spec.Url, url)
        self.assertEqual(msg_spec.Direction, self.DIRECTION)

    def test_ConstructorWithUrlFieldSubstitution(self):
        static_url = "/sensor/temp"
        url = "<pn>/<id>" + static_url
        msg_spec = MessageSpecification(self.TYPE, self.SUBTYPE,
                                        self.DATA_DEF, url, self.DIRECTION)

        self.assertEqual(msg_spec.Type, self.TYPE)
        self.assertEqual(msg_spec.Subtype, self.SUBTYPE)
        self.assertEqual(msg_spec.DataDef, self.DATA_DEF)
        self.assertEqual(msg_spec.Url, self.UrlFields["<pn>"] + '/' + self.UrlFields["<id>"] + static_url)
        self.assertEqual(msg_spec.Direction, self.DIRECTION)
