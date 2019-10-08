import logging
import uio as io
from micropython import const

LOGGER_STREAM_BUFFER_SIZE = const(400)

class LoggerStream(object):

    def __init__(self, file_global):
        self.StreamGlobal = io.StringIO(LOGGER_STREAM_BUFFER_SIZE)
        self.FileGlobal = file_global
        self.FileLevels = {}
        self.StreamLevel = {}
        return

    def LevelStreamAdd(self, level, file):
        self.FileLevels[level] = file
        self.StreamLevel[level] = io.StringIO(LOGGER_STREAM_BUFFER_SIZE)

    def write(self, string):
        level_sep_index = string.find(':')
        level = string[0:level_sep_index]
        if level in self.FileLevels:
            self.StreamLevel[level].write(string)
        else:
            self.StreamGlobal.write(string)

    def flush(self):

        return


class ExtLogger(logging.Logger):

    def __init__(self, name):
        super.__init__(name)


_Stream = None


def ConfigGlobal(level=logging.INFO, file=None):
    logging.basicConfig(level=level, stream=_Stream)
    LoggerStream(file)


def ConfigLevel(level, file=None):
    _Stream.LevelStreamAdd(level, file)


def Flush():
    return
