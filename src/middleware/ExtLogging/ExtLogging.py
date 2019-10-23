import uio as io
from micropython import const
import sys

LOGGER_STREAM_BUFFER_SIZE = const(400)

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
    CRITICAL: "CRIT",
    ERROR: "ERROR",
    WARNING: "WARN",
    INFO: "INFO",
    DEBUG: "DEBUG",
}


_stream = sys.stderr


class Logger:

    level = NOTSET

    def __init__(self, name):
        self.name = name

    def _level_str(self, level):
        l = _level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= (self.level or _level)

    def log(self, level, msg, *args):
        if level >= (self.level or _level):
            _stream.write("%s:%s:" % (self._level_str(level), self.name))
            if not args:
                _stream.write(msg + '\n')
            else:
                _stream.write(msg + '\n' % args)

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)

    def exc(self, e, msg, *args):
        self.log(ERROR, msg, *args)
        sys.print_exception(e, _stream)

    def exception(self, msg, *args):
        self.exc(sys.exc_info()[1], msg, *args)


_level = INFO
_loggers = {}


def getLogger(name):
    if name in _loggers:
        return _loggers[name]
    l = Logger(name)
    _loggers[name] = l
    return l


def info(msg, *args):
    getLogger(None).info(msg, *args)


def debug(msg, *args):
    getLogger(None).debug(msg, *args)


def basicConfig(level=INFO, filename=None, stream=None, format=None):
    global _level, _stream
    _level = level
    if stream:
        _stream = stream
    if filename is not None:
        print("logging.basicConfig: filename arg is not supported")
    if format is not None:
        print("logging.basicConfig: format arg is not supported")


class LoggerStream(object):

    def __init__(self, file_global):
        self.StreamGlobal = io.StringIO(LOGGER_STREAM_BUFFER_SIZE)
        self.FileGlobal = file_global
        self.FileLevels = {}
        self.StreamLevel = {}
        self.Stream = None
        print(self.StreamGlobal)
        return

    def LevelStreamAdd(self, level, file):
        self.FileLevels[level] = file
        self.StreamLevel[level] = io.StringIO(LOGGER_STREAM_BUFFER_SIZE)

# #### IO stream API ####

    def write(self, string):
        level_sep_index = string.find(':')
        if level_sep_index > 0:
            level = string[0:level_sep_index]
            print("Log level: {}".format(level))
            if level in self.StreamLevel:
                self.Stream = self.StreamLevel[level]
                print("Using level stream")
            else:
                self.Stream = self.StreamGlobal
                print("Using global stream")

        self.Stream.write(string)
        self.Stream.seek(0)
        print(self.Stream.read())
        return 1

    def flush(self):

        return


class ExtLogger(Logger):

    def __init__(self, name):
        super().__init__(name)


_Stream = None


def ConfigGlobal(level=INFO, file=None):
    global _Stream

    if file is not None:
        _Stream = LoggerStream(file)
    basicConfig(level=level, stream=_Stream)


def ConfigLevel(level, file):
    global _Stream

    if _Stream is None:
        return
    _Stream.LevelStreamAdd(level, file)


def GetLogger(name):
    if name in _loggers:
        return _loggers[name]
    l = Logger(name)
    _loggers[name] = l
    return l


def Flush():
    return


ConfigGlobal(level=DEBUG, file="./log")

log = ExtLogger("test")

log.info("hi")

log.debug("hoi")

ConfigLevel(CRITICAL, file="./crit")

log.info("hi")

log.critical("crit")


log1 = getLogger("test")

log1.debug("new")

log1.exception("Error!")
