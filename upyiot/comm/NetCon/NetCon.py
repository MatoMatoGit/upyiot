import uos as os
import utime
from micropython import const
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException


class NetConExceptionNoStationSettings(ServiceException):

    def __init__(self):
        super().__init__()


class NetConService(Service):
    NET_CON_SERVICE_MODE = Service.MODE_RUN_ONCE

    def __init__(self):
        super().__init__("NetCon", self.NET_CON_SERVICE_MODE, {})


class NetCon(NetConService):

    FILE_NET_CON = "net_con"
    PATH_NET_CON = "/" + FILE_NET_CON
    CONN_RETRIES = 5

    MODE_STATION        = const(0)
    MODE_ACCESS_POINT   = const(1)

    def __init__(self, net_con_dir, ap_cfg, mode=MODE_STATION, wlan_if_obj=None):
        # Initialize the NetConService class.
        super().__init__()
        self.WlanMode = mode
        self.NetIf = wlan_if_obj
        self.RootDir = net_con_dir
        self.ApSsid = ap_cfg["ssid"]
        self.ApPwd = ap_cfg["pwd"]
        self.ApIp = ap_cfg["ip"]

    def WlanInterface(self, wlan_if_obj, mode):
        self.NetIf = wlan_if_obj
        self.WlanMode = mode

    def SvcRun(self):
        if self.WlanMode is NetCon.MODE_ACCESS_POINT:
            self.AccessPointStart()
        else:
            self.StationStart()

    def SvcDeinit(self):
        if self.WlanMode is NetCon.MODE_ACCESS_POINT:
            self.AccessPointStop()
        else:
            self.StationStop()

    def AccessPointStart(self):
        if self.NetIf is None:
            return -1
        print("[NetCon] Starting AP mode. SSID: {}, IP: {}".format(self.ApSsid, self.ApIp))
        self.NetIf.ifconfig((self.ApIp, '255.255.255.0', '192.168.0.1', '192.168.0.1'))
        self.NetIf.active(True)
        self.NetIf.config(essid=self.ApSsid, password=self.ApPwd)

    def AccessPointStop(self):
        if self.NetIf is None:
            return -1
        print("[NetCon] Stopping AP mode.")
        self.NetIf.active(False)

    def StationSettingsStore(self, ssid, pwd):
        print("[NetCon] Storing station settings.")
        self._NetConFileWrite(ssid, pwd)

    def StationSettingsLoad(self):
        return self._NetConFileRead()

    def StationSettingsReset(self):
        print("[NetCon] Resetting station settings.")
        self._NetConFileDelete()

    def StationSettingsAreSet(self):
        return self._NetConFileExists()

    def StationStart(self):
        if self._NetConFileExists() is False:
            print("[NetCon] No station settings stored.")
            raise NetConExceptionNoStationSettings
        elif self.NetIf.isconnected() is True:
            print("[NetCon] Already connected.")
            self.SvcSuspend()
        else:
            ssid, pwd = self._NetConFileRead()
            print("[NetCon] Starting station mode. Connecting to SSID: {}".format(ssid))
            self.NetIf.active(True)

            # Attempt to connect to the configured AP, if
            # the attempt fails retry.
            i = 0
            while i < self.CONN_RETRIES:
                self.NetIf.connect(ssid, pwd)
                utime.sleep(5)
                if self.NetIf.isconnected() is True:
                    print("[NetCon] Connected. ifconfig: {}".format(self.NetIf.ifconfig()))
                    break
                else:
                    print("[NetCon] Failed to connect.")
                    i = i + 1
                    print("[NetCon] Connect retries remaining: {}".format((self.CONN_RETRIES - i)))

    def StationStop(self):
        self.NetIf.disconnect()
        self.NetIf.active(False)
        print("[NetCon] Stopping station mode.")

    def IsConnected(self):
        return self.NetIf.isconnected()

    def _NetConFileExists(self):
        f_exists = True
        try:
            f = open(self.RootDir + self.PATH_NET_CON)
            f.close()
        except OSError:
            f_exists = False

        return f_exists

    def _NetConFileWrite(self, ssid, pwd):
        f = open(self.RootDir + self.PATH_NET_CON, 'w')
        f.write(ssid + '\n')
        f.write(pwd + '\n')
        f.close()

    def _NetConFileRead(self):
        f = open(self.RootDir + self.PATH_NET_CON, 'r')
        ssid = f.readline().strip('\n')
        pwd = f.readline().strip('\n')
        f.close()
        print("[NetCon] SSID: {}, PWD: {}".format(ssid, pwd))
        return ssid, pwd

    def _NetConFileDelete(self):
        print("[NetCon] Deleting file {}".format(self.RootDir + self.PATH_NET_CON))
        try:
            os.remove(self.RootDir + self.PATH_NET_CON)
        except OSError:
            pass

