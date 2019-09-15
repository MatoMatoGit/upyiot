try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct
    
from machine import RTC
import uasyncio
import utime
 
# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 2208988800

host = "pool.ntp.org"


class SystemTime:
    
    _Instance = None
    _Rtc = None
    
    @staticmethod
    def InstanceGet():
        if SystemTime._Instance is None:
            SystemTime() 
        return SystemTime._Instance
    
    
    def Now(self):
        return SystemTime._Rtc.now()
    
    def _init_(self):
        if SystemTime._Instance is None:
            SystemTime._Instance = self
            SystemTime._Rtc = RTC()
        else:
            raise Exception("Only a single instance of this class is allowed")
    
    @staticmethod
    async def Service(t_sleep_sec):
        time_inst = SystemTime.InstanceGet()
        while True:
            ntp_time = SystemTime._NtpTimeGet(time_inst)
            print("NTP Time: {}".format(ntp_time))
            tm = utime.localtime(ntp_time)
            tm = tm[0:3] + (0,) + tm[3:6] + (0,)
            SystemTime._Rtc.datetime(tm)
            await uasyncio.sleep(t_sleep_sec)      
            
    
    def _NtpTimeGet(self):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1b
        try:
            addr = socket.getaddrinfo(host, 123)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
            s.close()
            val = struct.unpack("!I", msg[40:44])[0]
        except OSError:
            print("Failed to request NTP time.")
            val = -1
        return val - NTP_DELTA