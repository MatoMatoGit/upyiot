from micropython import const
import uos as os
import sys

WRITES_PER_LOG = const(2)

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
            log_entry = "%s:%s:" % (self._level_str(level), self.name)
            if not args:
                log_entry += msg
            else:
                log_entry += msg % args

            print("%s" % log_entry)
            log_entry += '\n'
            _stream.write(log_entry)

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


class LoggerStream(object):

    def __init__(self, stream, file):
        self.Stream = stream
        self.File = file
        return

# #### IO stream API ####

    def write(self, string):
        if self.Stream is not None:
            self.Stream.write(string)

        if self.File is not None:
            try:
                self.File.write(string)
            except OSError:
                print("[ExtLog] Failed to write to file.")

        return 1

    def flush(self):

        return


class ExtLogger(Logger):

    def __init__(self, name):
        super().__init__(name)


_level = INFO
_loggers = {}
_Stream = None
_File = None


def _FileCreate(file_path):
    try:
        f = open(file_path, 'a')
        print("[ExtLog] Log file '{}' exists".format(file_path))
        return f
    except OSError:
        try:
            f = open(file_path, 'w')
            print("[ExtLog] Log file '{}' created".format(file_path))
            return f
        except OSError:
            print("[ExtLog] Failed to create log file '{}'".format(file_path))
    return None


def _basicConfig(level=INFO, stream=None):
    global _level, _stream
    _level = level
    if stream:
        _stream = stream
    print("[ExtLog] Configured.")


def ConfigGlobal(level=INFO, stream=None, file_path=None):
    global _Stream
    global _File

    if file_path is not None:
        _File = _FileCreate(file_path)
    _Stream = LoggerStream(stream, _File)
    _basicConfig(level=level, stream=_Stream)


def Stop():
    global _File
    _File.close()


def LoggerGet(name):
    if name in _loggers:
        return _loggers[name]
    print("[ExtLog] Creating new ExtLogger for \"{}\"".format(name))
    logger = ExtLogger(name)
    _loggers[name] = logger
    return logger


def Clear():
    try:
        os.remove(_File)
        _FileCreate(_File)
    except OSError:
        print("[ExtLog] Failed to clear log file")


def info(msg, *args):
    LoggerGet(None).info(msg, *args)


def debug(msg, *args):
    LoggerGet(None).debug(msg, *args)

