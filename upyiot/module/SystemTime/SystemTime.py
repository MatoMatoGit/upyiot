try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct
try:
    from machine import RTC
except:
    from stubs.RtcStub import RTC

import utime
from micropython import const

from upyiot.module.Service.Service import Service


class SystemTimeService(Service):
    SYS_TIME_SERVICE_MODE = Service.MODE_RUN_ONCE

    def __init__(self):
        super().__init__(self.SYS_TIME_SERVICE_MODE, ())


class SystemTime(SystemTimeService):
    
    # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
    NTP_DELTA       = 2208988800
    NTP_FMT         = "!I"
    NTP_HOST        = "pool.ntp.org"
    NTP_BUF_SIZE    = const(48)
    
    RTC_DATETIME_YEAR   = const(0)
    RTC_DATETIME_MONTH  = const(1)
    RTC_DATETIME_DAY    = const(2)
    RTC_DATETIME_HOUR   = const(4)
    RTC_DATETIME_MINUTE = const(5)
    RTC_DATETIME_SECOND = const(6)
       
    _Instance = None
    _Rtc = None

    def __init__(self):
        if SystemTime._Instance is None:
            # Initialize the SystemTimeService class.
            super().__init__()

            print("Creating SystemTime instance")
            SystemTime._Instance = self
            SystemTime._Rtc = RTC()
        else:
            raise Exception("Only a single instance of this class is allowed")

    @staticmethod
    def InstanceGet():
        print("[SysTime] Getting instance")
        if SystemTime._Instance is None:
            SystemTime()
        return SystemTime._Instance

    def Now(self):
        datetime = SystemTime._Rtc.now()
        return datetime

    def DateTime(self):
        datetime = SystemTime._Rtc.now()
        # Format the datetime tuple as such: YYYY-MM-DDThh:mm:ss
        datetime_str = str(datetime[SystemTime.RTC_DATETIME_YEAR]) + \
                       '-' + str(datetime[SystemTime.RTC_DATETIME_MONTH]) + \
                       '-' + str(datetime[SystemTime.RTC_DATETIME_DAY]) + \
                       'T' + str(datetime[SystemTime.RTC_DATETIME_HOUR]) + \
                       ':' + str(datetime[SystemTime.RTC_DATETIME_MINUTE]) + \
                       ':' + str(datetime[SystemTime.RTC_DATETIME_SECOND])
        return datetime_str

    def SvcRun(self):
        ntp_time = self._NtpTimeGet()
        print("NTP Time: {}".format(ntp_time))
        if ntp_time > 0:
            tm = utime.localtime(ntp_time)
            tm = tm[0:3] + (0,) + tm[3:6] + (0,)
            self._Rtc.datetime(tm)

    def _NtpTimeGet(self):
        ntp_query = bytearray(SystemTime.NTP_BUF_SIZE)
        ntp_query[0] = 0x1b
        try:
            addr = socket.getaddrinfo(SystemTime.NTP_HOST, 123)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.sendto(ntp_query, addr)
            msg = s.recv(SystemTime.NTP_BUF_SIZE)
            s.close()
            val = struct.unpack(SystemTime.NTP_FMT, msg[40:44])[0]
        except OSError:
            print("Failed to request NTP time.")
            return -1
        if val > 0:
            return val - SystemTime.NTP_DELTA
        return -1



