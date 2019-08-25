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

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 2208988800

TIME_SYNC_INTERVAL_SEC = 60#3600

host = "pool.ntp.org"


class SystemTime:
    
    __Instance = None
    __Rtc = None
    
    @staticmethod
    def InstanceGet():
        if SystemTime.__Instance is None:
            SystemTime() 
        return SystemTime.__Instance
    
    
    def Now(self):
        return SystemTime.__Rtc.now()
    
    def __init__(self):
        if SystemTime.__Instance is None:
            SystemTime.__Instance = self
            SystemTime.__Rtc = RTC()
        else:
            raise Exception("Only a single instance of this class is allowed")
    
    @staticmethod
    async def SystemTimeService():
        time_inst = SystemTime.InstanceGet()
        while True:
            ntp_time = SystemTime.__NtpTimeGet(time_inst)
            print("NTP Time: {}".format(ntp_time))
            #Time.__Rtc.datetime(ntp_time)
            await uasyncio.sleep(TIME_SYNC_INTERVAL_SEC)      
            
    
    def __NtpTimeGet(self):
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