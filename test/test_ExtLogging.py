import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from upyiot.system.ExtLogging import ExtLogging

# Other
import uos as os


class TestStream:

    def __init__(self):
        return

    def write(self, str):
        print("[TestStream] {}".format(str))


class test_ExtLogging(unittest.TestCase):

    DIR = '.'

    def setUp(arg):
        return

    def tearDown(arg):
        try:
            ExtLogging.Clear()
        except:
            pass
        return

    def test_LoggingToFileMaxLines(self):
        file = "extlog"
        name = "test"
        text = "hi"
        file_limit = 2
        line_limit = 10

        ExtLogging.ConfigGlobal(level=ExtLogging.INFO, stream=TestStream(), dir=self.DIR,
                                file_prefix=file, line_limit=line_limit, file_limit=file_limit,
                                print_enabled=True, timestamp_enabled=True)

        log = ExtLogging.Create(name)
        print(log)

        for f in range(0, file_limit):
            for l in range(0, line_limit):
                log.info(text + str(l))

        ExtLogging.Mngr.PrintList()

        file_list = ExtLogging.Mngr.List()
        print(file_list)

        count = ExtLogging.Mngr.Count()
        self.assertEqual(count, file_limit)
        for i in range(0, count):
            print("[UT] Checking file: {}".format(file_list[i]))
            f = open(file_list[i], 'r')
            for l in range(0, line_limit):
                exc_occurred = False
                try:
                    line = f.readline()
                    print("[UT] Read line: {}".format(line))
                except OSError:
                    exc_occurred = True

                self.assertFalse(exc_occurred)
                self.assertTrue(text in line)
                self.assertTrue(name in line)
                self.assertTrue("[" in line)

            f.close()

    def test_LoggingToFileOverFileLimit(self):
        file = "extlog"
        name = "test"
        text = "hi"
        file_limit = 2
        line_limit = 10

        ExtLogging.ConfigGlobal(level=ExtLogging.INFO, stream=TestStream(), dir=self.DIR,
                                file_prefix=file, line_limit=line_limit, file_limit=file_limit)

        log = ExtLogging.Create(name)
        print(log)

        for f in range(0, file_limit * 2):
            for l in range(0, line_limit):
                log.info(text + str(l))

        ExtLogging.Mngr.PrintList()

        file_list = ExtLogging.Mngr.List()
        print(file_list)

        count = ExtLogging.Mngr.Count()
        self.assertEqual(count, file_limit)
        for i in range(0, count):
            print("[UT] Checking file: {}".format(file_list[i]))
            f = open(file_list[i], 'r')
            for l in range(0, line_limit):
                exc_occurred = False
                try:
                    line = f.readline()
                    print("[UT] Read line: {}".format(line))
                except OSError:
                    exc_occurred = True

                self.assertFalse(exc_occurred)
                self.assertTrue(text in line)
                self.assertTrue(name in line)

            f.close()

    def test_Exit(self):
        try:
            os.remove(test_ExtLogging.DIR + ExtLogging.LogFileManager.COUNT_FILE_NAME)
        except:
            pass
