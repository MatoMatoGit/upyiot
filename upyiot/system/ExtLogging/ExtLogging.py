from upyiot.middleware.StructFile import StructFile

from micropython import const
import uos as os
import sys

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


def _FileOpenAppend(file_path):
    try:
        f = open(file_path, 'a')
        print("[ExtLog] Appending to file '{}'".format(file_path))
        return f
    except OSError:
        try:
            f = open(file_path, 'w')
            print("[ExtLog] File '{}' created".format(file_path))
            return f
        except OSError:
            print("[ExtLog] Failed to create file '{}'".format(file_path))
    return None


class LogFileManager:

    COUNT_FILE_NAME = "/log_meta"
    COUNT_FILE_FMT = "<III"
    COUNT_DATA_FIRST = const(0)
    COUNT_DATA_LAST = const(1)
    COUNT_DATA_LINES = const(2)

    def __init__(self, dir, prefix, file_limit):
        file_path = dir + self.COUNT_FILE_NAME
        self.SFile = StructFile.StructFile(file_path, self.COUNT_FILE_FMT)
        self.Last = 0
        self.First = 0
        self.LineCount = 0
        self.Max = file_limit
        self.Dir = dir
        self.Prefix = prefix
        self.File = None
        count_data = self.SFile.ReadData(0)
        if count_data is not None:
            self.Last = count_data[self.COUNT_DATA_LAST]
            self.First = count_data[self.COUNT_DATA_FIRST]
            self.LineCount = count_data[self.COUNT_DATA_LINES]
            print("[LogFileMngr] First: {} | Last: {} | LineCount: {}".format(self.Last, self.First, self.LineCount))

    def DeleteAll(self):
        for file in self.List():
            print("[LogFileMngr] Deleting {}".format(file))
            os.remove(file)

        self.Last = self.First = self.LineCount = 0
        self.SFile.WriteData(0, self.First, self.Last, self.LineCount)

    def Count(self):
        return self.Last - self.First + 1

    def OpenMostRecent(self):
        file_path = self._FilePath(self.Last)
        self.File = _FileOpenAppend(file_path)
        return self.File

    def Sync(self):
        self.SFile.WriteData(0, self.First, self.Last, self.LineCount)

    def New(self):
        self.File.close()

        self.Last += 1

        if self.Count() > self.Max:
            file_path = self._FilePath(self.First)
            os.remove(file_path)
            print("[LogFileMngr] Removed log file: {}".format(file_path))
            self.First += 1

        self.LineCount = 0
        self.Sync()

        return self.OpenMostRecent()

    def PrintList(self):
        print("[LogFileMngr] List of log files ({})".format(self.Count()))
        for file in self.List():
            print("[LogFileMngr] {}".format(file))

    def List(self):
        file_list = list()
        for i in range(self.First, self.Last + 1, 1):
            file_list.append(self._FilePath(i))

        return file_list

    def _FilePath(self, number):
        return self.Dir + '/' + self.Prefix + str(number)


class LogFile:

    def __init__(self, log_file_mngr, line_limit):
        self.Mngr = log_file_mngr
        self.File = self.Mngr.OpenMostRecent()
        self.LineLimit = line_limit

    def write(self, string):
        if self.Mngr.LineCount >= self.LineLimit:
            print("[LogFileMngr] Line limit reached")
            self.File = self.Mngr.New()

        self.Mngr.LineCount += 1
        self.File.write(string)

    def close(self):
        self.Mngr.Sync()
        self.File.close()


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

    def close(self):
        if self.File is not None:
            self.File.close()


class ExtLogger(Logger):

    def __init__(self, name):
        super().__init__(name)


_level = INFO
_loggers = {}
_Stream = None
_File = None
Mngr = None



def _ConfigBasic(level=INFO, stream=None):
    global _level, _stream
    _level = level
    if stream:
        _stream = stream
    print("[ExtLog] Configured.")


def ConfigGlobal(level=INFO, stream=None, dir=None, file_prefix=None, line_limit=1000, file_limit=10):
    global _Stream
    global _File
    global Mngr

    if dir is not None:
        if Mngr is None:
            Mngr = LogFileManager(dir, file_prefix, file_limit)
        _File = LogFile(Mngr, line_limit)

    _Stream = LoggerStream(stream, _File)
    _ConfigBasic(level=level, stream=_Stream)


def ConfigError(error_code_stream):
    return


def Stop():
    global _Stream
    _Stream.flush()
    _Stream.close()


def Create(name):
    if name in _loggers:
        return _loggers[name]
    print("[ExtLog] Creating new ExtLogger for \"{}\"".format(name))
    logger = ExtLogger(name)
    _loggers[name] = logger
    return logger


def Clear():
    global Mngr

    try:
        Mngr.DeleteAll()
    except OSError:
        print("[ExtLog] Failed to clear log file")


def info(msg, *args):
    Create(None).info(msg, *args)


def debug(msg, *args):
    Create(None).debug(msg, *args)

