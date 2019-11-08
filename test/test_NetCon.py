import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs.network import WLAN

# Unit Under Test
from upyiot.comm.NetCon.NetCon import NetCon
from upyiot.comm.NetCon.NetCon import NetConService
from upyiot.comm.NetCon.NetCon import NetConExceptionNoStationSettings

# Other
from upyiot.module.Service.Service import Service
from upyiot.module.Service.Service import ServiceExceptionSuspend


class test_NetCon(unittest.TestCase):

    DIR = "./"
    ApCfg = {"ssid": "test", "pwd": "123", "ip": "127.0.0.1"}

    def setUp(self):

        return

    def tearDown(self):
        return

    def test_Constructor(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_ACCESS_POINT, wlan_ap)

        self.assertIsInstance(netcon, NetCon)
        self.assertIsInstance(netcon, Service)
        self.assertEqual(netcon.WlanMode, NetCon.MODE_ACCESS_POINT)
        self.assertEqual(netcon.SvcMode, NetConService.NET_CON_SERVICE_MODE)

        netcon.StationSettingsReset()

    def test_RunApMode(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_ACCESS_POINT, wlan_ap)

        netcon.SvcRun()

        self.assertTrue(wlan_ap.active())

        netcon.StationSettingsReset()

    def test_DeinitApMode(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_ACCESS_POINT, wlan_ap)

        netcon.SvcRun()
        netcon.SvcDeinit()

        self.assertFalse(wlan_ap.active())
        self.assertFalse(wlan_ap.isconnected())

        netcon.StationSettingsReset()

    def test_StationSettingsStoreLoad(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_ACCESS_POINT, wlan_ap)

        netcon.StationSettingsStore(self.ApCfg["ssid"], self.ApCfg["pwd"])

        ssid, pwd = netcon.StationSettingsLoad()

        self.assertEqual(self.ApCfg["ssid"], ssid)
        self.assertEqual(self.ApCfg["pwd"], pwd)
        self.assertTrue(TestUtil.FileExists(netcon.RootDir + NetCon.PATH_NET_CON))

        netcon.StationSettingsReset()

    def test_RunStationModeConnectOnFirstTry(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_STATION, wlan_ap)

        netcon.StationSettingsStore(self.ApCfg["ssid"], self.ApCfg["pwd"])
        netcon.SvcRun()

        self.assertTrue(wlan_ap.active())
        self.assertTrue(netcon.IsConnected())

        netcon.StationSettingsReset()

    def test_RunStationModeConnectAfterRetries(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_STATION, wlan_ap)

        wlan_ap.retries_set(NetCon.CONN_RETRIES - 1)
        netcon.StationSettingsStore(self.ApCfg["ssid"], self.ApCfg["pwd"])
        netcon.SvcRun()

        self.assertTrue(wlan_ap.active())
        self.assertTrue(netcon.IsConnected())

        netcon.StationSettingsReset()

    def test_RunStationModeConnectFailed(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_STATION, wlan_ap)

        wlan_ap.retries_set(NetCon.CONN_RETRIES)
        netcon.StationSettingsStore(self.ApCfg["ssid"], self.ApCfg["pwd"])
        netcon.SvcRun()

        self.assertTrue(wlan_ap.active())
        self.assertFalse(netcon.IsConnected())

        netcon.StationSettingsReset()

    def test_RunStationModeAlreadyConnected(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_STATION, wlan_ap)

        netcon.StationSettingsStore(self.ApCfg["ssid"], self.ApCfg["pwd"])
        netcon.SvcRun()

        exc_occurred = False
        try:
            netcon.SvcRun()
        except ServiceExceptionSuspend:
            exc_occurred = True

        self.assertTrue(exc_occurred)
        self.assertTrue(wlan_ap.active())
        self.assertTrue(netcon.IsConnected())

        netcon.StationSettingsReset()

    def test_RunStationModeNoSettings(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_STATION, wlan_ap)

        exc_occurred = False
        try:
            netcon.SvcRun()
        except NetConExceptionNoStationSettings:
            exc_occurred = True

        self.assertTrue(exc_occurred)

        netcon.StationSettingsReset()

    def test_DeinitStationMode(self):
        wlan_ap = WLAN()
        netcon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_STATION, wlan_ap)

        netcon.StationSettingsStore(self.ApCfg["ssid"], self.ApCfg["pwd"])
        netcon.SvcRun()
        netcon.SvcDeinit()

        self.assertFalse(wlan_ap.active())
        self.assertFalse(netcon.IsConnected())

        netcon.StationSettingsReset()


