from upyiot.comm.Messaging.Protocol.MessagingProtocol import MessagingProtocol
from upyiot.comm.Messaging.MessageExchange import MessageExchange
from upyiot.comm.Network import LoRaWAN
from upyiot.comm.Network.LoRaWAN.MHDR import MHDR
from upyiot.middleware.StructFile import StructFile
from upyiot.drivers.Modems.SX127x.LoRa import *
from upyiot.drivers.Modems.SX127x.board_config import BOARD
from upyiot.system.ExtLogging import ExtLogging

from time import sleep
from random import randrange
import machine
from micropython import const

Log = ExtLogging.Create("LoraProto")

ADDR_SIZE = const(4)
EUI_SIZE = const(8)
KEY_SIZE = const(16)

TX_TIMEOUT_SEC = const(10)
RX_TIMEOUT_SEC = const(30)
TIMEOUT_POLL_SEC = const(1)


class LoRaWANParams:

    SESSION_DATA_FMT = "<4s16s16s"  # DevAddr, AppSKey, NwkSKey
    FCNT_DATA_FMT = "<I"

    def __init__(self, dir: str, dev_eui: str):
        # The session file is written once when a the device registers successfully.
        self.SessionSFile = StructFile.StructFile(dir + '/session_' + dev_eui,
                                                  self.SESSION_DATA_FMT)
        # The frame count file is written whenever an uplink message is sent.
        self.FrameCountSFile = StructFile.StructFile(dir + '/fcnt_' + dev_eui,
                                                     self.FCNT_DATA_FMT)

        try:
            self.FrameCounter = self.FrameCountSFile.ReadData(0)[0]
            Log.info("FrameCounter: {}".format(self.FrameCounter))
        except TypeError:
            Log.info("No LoRaWAN framecounter present.")
            self.FrameCounter = 0

        try:
            self.DevAddr, self.AppSKey, self.NwkSKey = self.SessionSFile.ReadData(0)
            self.DevAddr = list(self.DevAddr)
            self.AppSKey = list(self.AppSKey)
            self.NwkSKey = list(self.NwkSKey)

            Log.info("LoRaWAN session info loaded.")
            Log.debug("NwSKey: {} | AppSKey: {} | DevAddr: {}".format(
                self.NwkSKey, self.AppSKey, self.DevAddr))
        except TypeError:
            self.FrameCounter = 0
            self.DevAddr = None
            self.AppSKey = None
            self.NwkSKey = None
            Log.info("No LoRaWAN session present.")

    def IncrementFrameCounter(self):
        self.FrameCounter += 1
        Log.debug("Writing FrameCounter: {}".format(self.FrameCounter))
        self.FrameCountSFile.WriteData(0, self.FrameCounter)

    def ResetFrameCounter(self):
        self.FrameCountSFile.Clear()

    def StoreSession(self, dev_addr, app_skey, nwk_skey):
        self.DevAddr = dev_addr
        self.AppSKey = app_skey
        self.NwkSKey = nwk_skey
        Log.info("Storing LoRaWAN session")
        self.SessionSFile.WriteData(0, bytearray(self.DevAddr),
                                    bytearray(self.AppSKey),
                                    bytearray(self.NwkSKey))

    def ResetSession(self):
        self.SessionSFile.Clear()

    def HasSession(self):
        """
        Checks whether a LoRaWAN session has been stored. A session is stored
        on a successful network join or if it has been been pre-set.
        A session consists of:
        - The device address
        - The application session key
        - The network session key
        :return: True if a session exists, False if it does not.
        :rtype: boolean
        """
        return self.DevAddr is not None \
               and self.AppSKey is not None \
               and self.NwkSKey is not None


class LoRaWANSend(LoRa):
    def __init__(self, params_obj, payload, verbose=False):
        super(LoRaWANSend, self).__init__(verbose)
        self.Params = params_obj
        self.Payload = payload
        self.Done = False

    def on_tx_done(self):
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        Log.info("TxDone")
        self.Done = True

    def Start(self):
        Log.info("Sending LoRaWAN TX packet")

        lorawan = LoRaWAN.new(self.Params.NwkSKey, self.Params.AppSKey)

        Log.info("Frame counter: {}".format(self.Params.FrameCounter))

        lorawan.create(
            MHDR.UNCONF_DATA_UP, {
                'devaddr': self.Params.DevAddr,
                'fcnt': self.Params.FrameCounter,
                'data': list(self.Payload)
            })

        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)

        self.Params.IncrementFrameCounter()

        timeout = 0
        while self.Done is False and timeout < TX_TIMEOUT_SEC:
            sleep(TIMEOUT_POLL_SEC)
            timeout += TIMEOUT_POLL_SEC

        self.set_mode(MODE.SLEEP)


class LoRaWANReceive(LoRa):
    def __init__(self, params_obj, verbose=False):
        super(LoRaWANReceive, self).__init__(verbose)
        self.Params = params_obj
        self.Done = False

    def on_rx_done(self):
        Log.info("RxDone")

        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        Log.debug("".join(format(x, '02x') for x in bytes(payload)))

        lorawan = LoRaWAN.new(self.Params.NwkSKey, self.Params.AppSKey)
        lorawan.read(payload)
        Log.debug(lorawan.get_mhdr().get_mversion())
        Log.debug(lorawan.get_mhdr().get_mtype())
        Log.debug(lorawan.get_mic())
        Log.debug(lorawan.compute_mic())
        Log.debug(lorawan.valid_mic())
        Log.debug("".join(list(map(chr, lorawan.get_payload()))))

        self.set_mode(MODE.SLEEP)

        self.Done = True

    def Start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXSINGLE)

        timeout = 0
        while self.Done is False and timeout < RX_TIMEOUT_SEC:
            sleep(TIMEOUT_POLL_SEC)
            timeout += TIMEOUT_POLL_SEC

        self.set_mode(MODE.SLEEP)


class LoRaWANOtaa(LoRa):
    def __init__(self,
                 devnonce,
                 dev_eui,
                 app_eui,
                 app_key,
                 params_obj,
                 verbose=False):
        self.DevNonce = devnonce
        self.Params = params_obj
        self.DevEui = dev_eui
        self.AppEui = app_eui
        self.AppKey = app_key
        self.Done = False
        super(LoRaWANOtaa, self).__init__(verbose=verbose,
                                          do_calibration=True,
                                          calibration_freq=868.1)

    def on_rx_done(self):
        Log.info("RxDone")

        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)

        lorawan = LoRaWAN.new([], self.AppKey)
        lorawan.read(payload)
        Log.debug(str(lorawan.get_payload()))
        Log.debug(str(lorawan.get_mhdr().get_mversion()))

        if lorawan.get_mhdr().get_mtype() == MHDR.JOIN_ACCEPT:
            Log.info("Got LoRaWAN join accept")

            nwks_key = lorawan.derive_nwskey(self.DevNonce)

            apps_key = lorawan.derive_appskey(self.DevNonce)

            dev_addr = lorawan.get_devaddr()
            Log.debug("NwSKey: {} | AppSKey: {} | DevAddr: {}".format(
                nwks_key, apps_key, dev_addr))

            self.Params.StoreSession(dev_addr, apps_key, nwks_key)

        self.Done = True

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        Log.info("TxDone")

        self.set_mode(MODE.STDBY)
        self.set_dio_mapping([0, 0, 0, 0, 0, 0])
        self.set_invert_iq(1)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

        Log.info("Waiting for LoRaWAN join accept")

    def Start(self):

        Log.info("Sending LoRaWAN join request")

        lorawan = LoRaWAN.new(self.AppKey)
        lorawan.create(
            MHDR.JOIN_REQUEST, {
                'deveui': self.DevEui,
                'appeui': self.AppEui,
                'devnonce': self.DevNonce
            })

        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)

        timeout = 0
        while self.Done is False and timeout < RX_TIMEOUT_SEC:
            sleep(TIMEOUT_POLL_SEC)
            timeout += TIMEOUT_POLL_SEC

        self.set_mode(MODE.SLEEP)


class LoraProtocol(MessagingProtocol):

    LORA_MTU = const(51)
    LORA_SEND_INTERVAL = const(10)  # 600

    _Instance = None

    def __init__(self,
                 config,
                 directory="/",
                 send_interval=LORA_SEND_INTERVAL):
        super().__init__(client=None,
                         mtu=self.LORA_MTU,
                         send_interval=send_interval)
        LoraProtocol._Instance = self
        self.AppKey = config["app_key"]
        self.DevEui = config["dev_eui"]
        self.AppEui = config["app_eui"]
        self.Config = config
        self.Lora = None
        self.Params = LoRaWANParams(directory, config["dev_eui_str"])
        Log.info("DevEUI: {} | AppEUI: {} | AppKey: {}".format(
            self.DevEui, self.AppEui, self.AppKey))
        Log.info("MTU: {} bytes | Send interval: {} sec".format(
            self.Mtu, self.SendInterval))
        return

    def Setup(self, recv_callback, msg_mappings):
        MessagingProtocol.Setup(self, recv_callback, msg_mappings)
        BOARD.setup()
        return

    def Send(self, msg_map, payload, size):
        if self.Params.HasSession() is False:
            return

        self.Lora = LoRaWANSend(self.Params, payload, verbose=True)
        self._ConfigureLora()
        self.Lora.Start()
        return

    def Receive(self):
        if self.Params.HasSession() is False:
            return

        self.Lora = LoRaWANReceive(self.Params, verbose=True)
        self._ConfigureLora()
        self.Lora.Start()

        return

    def Connect(self):
        if self.Params.HasSession() is False:
            dev_nonce = [randrange(256), randrange(256)]

            self.Lora = LoRaWANOtaa(dev_nonce,
                                    self.DevEui,
                                    self.AppEui,
                                    self.AppKey,
                                    self.Params,
                                    verbose=True)
            self._ConfigureLora()
            self.Lora.Start()

        if self.Params.HasSession() is False:
            raise OSError

    def Disconnect(self):
        pass

    def HasSession(self):
        return self.Params.HasSession()

    @staticmethod
    def _ReceiveCallback(lora, outgoing):
        payload = lora.read_payload()
        Log.debug("Received: {}".format(payload))
        LoraProtocol._Instance.RecvCallback("none", payload)

    def _ConfigureLora(self):
        self.Lora.set_mode(MODE.SLEEP)
        self.Lora.set_dio_mapping([1, 0, 0, 0, 0, 0])
        self.Lora.set_freq(self.Config["freq"])
        self.Lora.set_pa_config(pa_select=1)
        self.Lora.set_spreading_factor(self.Config["sf"])
        self.Lora.set_low_data_rate_optim(self.Config["ldro"])
        self.Lora.set_bw(7)  # 7=125k
        self.Lora.set_pa_config(max_power=0x0F, output_power=0x0F)
        self.Lora.set_sync_word(0x34)
        self.Lora.set_rx_crc(True)
        self.Lora.set_detect_optimize(0x03)  # 0x03 for SF7-SF12
        self.Lora.set_detection_threshold(0x0A)  # 0x0A for SF7-SF12
        #self.Lora.set_agc_auto_on(1)

        Log.debug(str(self.Lora))
