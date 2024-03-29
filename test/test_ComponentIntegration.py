import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs import DummySensor
from stubs.network import WLAN

# Unit(s) Under Test
from upyiot.system.SystemTime.SystemTime import SystemTime
from upyiot.system.Service.Service import Service
from upyiot.system.Service.ServiceScheduler import ServiceScheduler
from upyiot.system.ExtLogging import ExtLogging
from upyiot.middleware.Sensor import Sensor
from upyiot.comm.NetCon.NetCon import NetCon
from upyiot.comm.Messaging.MessageExchange import MessageExchange
from upyiot.comm.Messaging.MessageExchange import Endpoint
from upyiot.comm.Messaging.MessageFormatAdapter import MessageFormatAdapter
from upyiot.comm.Messaging.MessageSpecification import MessageSpecification
from upyiot.drivers.Sleep.MachineDeepSleep import DeepSleepExceptionInitiated

# Other
from umqtt.simple import MQTTClient
from micropython import const


class SensorReport(MessageSpecification):

    TYPE_SENSOR_REPORT        = const(0)
    BASE_URL_SENSOR_REPORT         = "<pn>/<id>/"
    DATA_KEY_SENSOR_REPORT_ARRAY  = "smp"
    DIRECTION_SENSOR_REPORT   = MessageSpecification.MSG_DIRECTION_SEND

    def __init__(self, subtype, url_suffix):
        self.DataDef = {SensorReport.DATA_KEY_SENSOR_REPORT_ARRAY: []}
        super().__init__(SensorReport.TYPE_SENSOR_REPORT,
                         subtype,
                         self.DataDef,
                         SensorReport.BASE_URL_SENSOR_REPORT + url_suffix,
                         SensorReport.DIRECTION_SENSOR_REPORT)


class SensorReportTemp(SensorReport):

    NAME_TEMP = "temp"
    SUBTYPE_TEMP = const(1)

    def __init__(self):
        super().__init__(SensorReportTemp.SUBTYPE_TEMP, SensorReportTemp.NAME_TEMP)


class SensorReportMoist(SensorReport):

    NAME_MOIST = "moist"
    SUBTYPE_MOIST = const(2)

    def __init__(self):
        super().__init__(SensorReportMoist.SUBTYPE_MOIST, SensorReportMoist.NAME_MOIST)


class LogMessage(MessageSpecification):

    TYPE_LOG_MSG        = const(1)
    SUBTYPE_LOG_MSG     = const(1)
    URL_LOG_MSG         = "<pn>/<id>/log"
    DATA_KEY_LOG_MSG  = "msg"
    DATA_DEF_LOG_MSG    = {DATA_KEY_LOG_MSG: ""}
    DIRECTION_LOG_MSG   = MessageSpecification.MSG_DIRECTION_SEND

    def __init__(self):
        super().__init__(LogMessage.TYPE_LOG_MSG,
                         LogMessage.SUBTYPE_LOG_MSG,
                         LogMessage.DATA_DEF_LOG_MSG,
                         LogMessage.URL_LOG_MSG,
                         LogMessage.DIRECTION_LOG_MSG)


class test_ComponentIntegration(unittest.TestCase):

    PRODUCT_NAME = "smartsensor"
    DIR = "./"
    ID = '3f7e12c9'
    RETRIES = 3
    BROKER = '192.168.0.103'
    PORT = 1883
    ApCfg = {"ssid": "test", "pwd": "123", "ip": "127.0.0.1"}

    MqttClient = None
    MsgEx = None
    Time = None
    UrlFields = {MessageSpecification.URL_FIELD_DEVICE_ID: ID,
                 MessageSpecification.URL_FIELD_PRODUCT_NAME: PRODUCT_NAME}

    TempSamples = [20, 21, 25, 30, 35, 35, 20, 12, 10, 40]
    MoistSamples = [200, 300, 350, 360, 290, 500, 250, 300, 240, 320]

    SamplesPerMessage   = const(1)
    MsgExInterval       = const(20)
    SensorReadInterval  = const(10)

    RecvTopic = None
    RecvMsg = None
    RecvMsgCount = 0

    def setUp(self):
        # Configure the URL fields.
        MessageSpecification.Config(self.UrlFields)

        # Create objects.
        filter_depth = len(self.TempSamples) / 2
        dummy_temp_sensor = DummySensor.DummySensor(self.TempSamples)
        dummy_moist_sensor = DummySensor.DummySensor(self.MoistSamples)
        wlan_ap = WLAN()
        self.Time = SystemTime.InstanceGet()
        self.NetCon = NetCon(self.DIR, self.ApCfg, NetCon.MODE_STATION, wlan_ap)
        self.TempSensor = Sensor.Sensor(self.DIR,
                                        SensorReportTemp.NAME_TEMP,
                                        filter_depth, dummy_temp_sensor)
        self.MoistSensor = Sensor.Sensor(self.DIR,
                                         SensorReportMoist.NAME_MOIST,
                                         filter_depth, dummy_moist_sensor)
        self.MqttClient = MQTTClient(self.ID,
                                     self.BROKER,
                                     self.PORT)
        self.MsgEx = MessageExchange(self.DIR,
                                     self.MqttClient,
                                     self.ID,
                                     self.RETRIES)
        self.MsgEp = Endpoint()
        self.Scheduler = ServiceScheduler()

        # Set service dependencies.
        self.Time.SvcDependencies({self.NetCon: Service.DEP_TYPE_RUN_ALWAYS_BEFORE_RUN})
        self.MsgEx.SvcDependencies({self.Time: Service.DEP_TYPE_RUN_ONCE_BEFORE_RUN,
                                    self.NetCon: Service.DEP_TYPE_RUN_ALWAYS_BEFORE_INIT})
        self.TempSensor.SvcDependencies({self.Time: Service.DEP_TYPE_RUN_ONCE_BEFORE_RUN})
        self.MoistSensor.SvcDependencies({self.Time: Service.DEP_TYPE_RUN_ONCE_BEFORE_RUN})

        # Register all services to the scheduler.
        self.Scheduler.ServiceRegister(self.Time)
        self.Scheduler.ServiceRegister(self.NetCon)
        self.Scheduler.ServiceRegister(self.MsgEx)
        self.Scheduler.ServiceRegister(self.TempSensor)
        self.Scheduler.ServiceRegister(self.MoistSensor)

        # Create message specifications.
        self.TempMsgSpec = SensorReportTemp()
        self.MoistMsgSpec = SensorReportMoist()
        self.LogMsgSpec = LogMessage()

        # Create a Messaging Endpoint and MessageFormatAdapters.
        self.TempAdapt = MessageFormatAdapter(self.MsgEp, MessageFormatAdapter.SEND_ON_COMPLETE, self.TempMsgSpec)
        self.MoistAdapt = MessageFormatAdapter(self.MsgEp, MessageFormatAdapter.SEND_ON_COMPLETE, self.MoistMsgSpec)
        self.LogAdapt = MessageFormatAdapter(self.MsgEp, MessageFormatAdapter.SEND_ON_COMPLETE, self.LogMsgSpec)

        # Register message specs.
        self.MsgEx.RegisterMessageType(self.TempMsgSpec)
        self.MsgEx.RegisterMessageType(self.MoistMsgSpec)
        self.MsgEx.RegisterMessageType(self.LogMsgSpec)

        # Create observers for the sensor data.
        self.TempObserver = self.TempAdapt.CreateObserver(
            SensorReportTemp.DATA_KEY_SENSOR_REPORT_ARRAY, self.SamplesPerMessage)
        self.MoistObserver = self.MoistAdapt.CreateObserver(
            SensorReportMoist.DATA_KEY_SENSOR_REPORT_ARRAY, self.SamplesPerMessage)

        # Link the observers to the sensors.
        self.TempSensor.ObserverAttachNewSample(self.TempObserver)
        self.MoistSensor.ObserverAttachNewSample(self.MoistObserver)

        # Create a stream for the log messages.
        self.LogStream = self.LogAdapt.CreateStream(LogMessage.DATA_KEY_LOG_MSG, ExtLogging.WRITES_PER_LOG)

        # Configure the ExtLogging class.
        ExtLogging.ConfigGlobal(level=ExtLogging.INFO, stream=self.LogStream)

        # Configure the station settings to connect to a WLAN AP.
        self.NetCon.StationSettingsStore(self.ApCfg["ssid"], self.ApCfg["pwd"])

        # Declare test variables.
        self.RecvMsgCount = 0
        self.RecvTopic = None
        self.RecvMsg = None

    def tearDown(self):
        self.MsgEx.Reset()
        self.TempSensor.SamplesDelete()
        self.MoistSensor.SamplesDelete()
        self.NetCon.StationSettingsReset()
        self.Scheduler.Memory.Delete()

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_ComponentIntegration.RecvTopic = topic
        test_ComponentIntegration.RecvMsg = msg
        test_ComponentIntegration.RecvMsgCount = test_ComponentIntegration.RecvMsgCount + 1

    def test_RunComponentIntegration(self):

        self.MsgEx.SvcIntervalSet(self.MsgExInterval)
        self.MoistSensor.SvcIntervalSet(self.SensorReadInterval)
        self.TempSensor.SvcIntervalSet(self.SensorReadInterval)

        n_deepsleep = 0
        deepsleep = True
        n = 10
        while deepsleep is True:
            deepsleep = False
            try:
                self.Scheduler.Run(n)
            except DeepSleepExceptionInitiated:
                n = self.Scheduler.Cycles
                deepsleep = True
                n_deepsleep += 1

        self.assertNotEqual(self.MsgEx.SvcLastRun, -1)
        self.assertNotEqual(self.NetCon.SvcLastRun, -1)
        self.assertNotEqual(self.Time.SvcLastRun, -1)
        self.assertNotEqual(self.TempSensor.SvcLastRun, -1)
        self.assertNotEqual(self.MoistSensor.SvcLastRun, -1)

        self.assertNotEqual(n_deepsleep, 0)


