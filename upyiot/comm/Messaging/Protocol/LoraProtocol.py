from upyiot.comm.Messaging.Protocol.MessagingProtocol import MessagingProtocol
from upyiot.comm.Messaging.MessageExchange import MessageExchange
from upyiot.comm.Network import LoRaWAN
from upyiot.comm.Network.LoRaWAN.MHDR import MHDR
from upyiot.middleware.StructFile import StructFile
from upyiot.drivers.Modems.SX127x.LoRa import *
from upyiot.drivers.Modems.SX127x.LoRaArgumentParser import LoRaArgumentParser
from upyiot.drivers.Modems.SX127x.board_config import BOARD
from upyiot.system.ExtLogging import ExtLogging

from time import sleep
from random import randrange
import machine

parser = LoRaArgumentParser("LoraProto")
Log = ExtLogging.Create("LoraProto")

ADDR_SIZE = 4
EUI_SIZE = 8
KEY_SIZE = 16


class LoRaWANParams:

    SESSION_DATA_FMT = "<4s16s16s"  # DevAddr, AppSKey, NwkSKey
    FCNT_DATA_FMT = "<I"

    def __init__(self, dir):
        self.SessionSFile = StructFile.StructFile(dir + '/session', self.SESSION_DATA_FMT)
        self.FrameCountSFile = StructFile.StructFile(dir + '/fcnt', self.FCNT_DATA_FMT)

        self.FrameCounter = self.FrameCountSFile.ReadData(0)[0]
        self.DevAddr, self.AppSKey, self.NwkSKey = self.SessionSFile.ReadData(0)

        if self.FrameCounter is None:
            self.FrameCounter = 0

        if self.HasSession() is False:
            Log.info("No LoRaWAN session info present")
            self.FrameCounter = 0
        else:
            Log.info("LoRaWAN session info loaded")
            Log.debug("NwSKey: {} | AppSKey: {} | DevAddr: {}".format(self.NwkSKey, self.AppSKey, self.DevAddr))

        Log.info("FrameCounter: {}".format(self.FrameCounter))

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
        self.SessionSFile.WriteData(0, self.DevAddr, self.AppSKey, self.NwkSKey)

    def ResetSession(self):
        self.SessionSFile.Clear()

    def HasSession(self):
        return self.DevAddr is not None \
               and self.AppSKey is not None \
               and self.NwkSKey is not None


class LoRaWANSend(LoRa):
    def __init__(self, params_obj, verbose = False):
        super(LoRaWANSend, self).__init__(verbose)
        self.Params = params_obj

    def on_tx_done(self):
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        Log.info("TxDone")
        sys.exit(0)

    def Start(self):
        Log.info("Sending LoRaWAN TX packet")

        lorawan = LoRaWAN.new(self.Params.NwkSkey, self.Params.AppSKey)

        Log.info("Frame counter: {}".format(self.Params.FrameCounter))

        lorawan.create(MHDR.UNCONF_DATA_UP, {'devaddr': self.Params.DevAddr, 'fcnt': self.Params.FrameCounter, 'data': list(map(ord, 'Python rules!')) })

        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)

        self.Params.IncrementFrameCounter()

        while True:
            sleep(1)


class LoRaWANReceive(LoRa):
    def __init__(self, params_obj, verbose = False):
        super(LoRaWANReceive, self).__init__(verbose)
        self.Params = params_obj

    def on_rx_done(self):
        Log.info("RxDone")

        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        Log.debug("".join(format(x, '02x') for x in bytes(payload)))

        lorawan = LoRaWAN.new(self.Params.NwkSkey, self.Params.AppSKey)
        lorawan.read(payload)
        Log.debug(lorawan.get_mhdr().get_mversion())
        Log.debug(lorawan.get_mhdr().get_mtype())
        Log.debug(lorawan.get_mic())
        Log.debug(lorawan.compute_mic())
        Log.debug(lorawan.valid_mic())
        Log.debug("".join(list(map(chr, lorawan.get_payload()))))

        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def Start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)


class LoRaWANOtaa(LoRa):
    def __init__(self, devnonce, dev_eui, app_eui, app_key, params_obj, verbose = False):
        self.DevNonce = devnonce
        self.Params = params_obj
        self.DevEui = dev_eui
        self.AppEui = app_eui
        self.AppKey = app_key
        super(LoRaWANOtaa, self).__init__(verbose=verbose, do_calibration=True, calibration_freq=869.25)

    def on_rx_done(self):
        Log.info("RxDone")

        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)

        lorawan = LoRaWAN.new([], self.AppKey)
        lorawan.read(payload)
        Log.debug(lorawan.get_payload())
        Log.debug(lorawan.get_mhdr().get_mversion())

        if lorawan.get_mhdr().get_mtype() == MHDR.JOIN_ACCEPT:
            Log.info("Got LoRaWAN join accept")

            nws_key = lorawan.derive_nwskey(self.DevNonce)

            apps_key = lorawan.derive_appskey(self.DevNonce)

            dev_addr = lorawan.get_devaddr()
            Log.debug("NwSKey: {} | AppSKey: {} | DevAddr: {}".format(nws_key, apps_key, dev_addr))

            self.Params.StoreSession(dev_addr, apps_key, nws_key)

        else:
            raise OSError

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        Log.info("TxDone")

        self.set_mode(MODE.STDBY)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.set_invert_iq(1)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def Start(self):

        Log.info("Sending LoRaWAN join request")

        lorawan = LoRaWAN.new(self.AppKey)
        lorawan.create(MHDR.JOIN_REQUEST, {'deveui': self.DevEui,
                                           'appeui': self.AppEui, 'devnonce': self.DevNonce})

        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)


class LoraProtocol(MessagingProtocol):

    _Instance = None

    def __init__(self, dev_eui, app_eui, app_key, dir="/"):
        super().__init__(None)
        LoraProtocol._Instance = self
        self.AppKey = app_key
        self.DevEui = dev_eui
        self.AppEui = app_eui
        self.Lora = None
        self.Params = LoRaWANParams(dir)
        Log.debug("DevEUI: {} | AppEUI: {} | AppKey: {}".format(self.DevEui, self.AppEui, self.AppKey))
        return

    def Setup(self, recv_callback, msg_mappings):
        MessagingProtocol.Setup(self, recv_callback, msg_mappings)
        self.Client.on_receive(LoraProtocol._ReceiveCallback)
        BOARD.setup()
        return

    def Send(self, msg_map, payload, size):
        if self.Params.HasSession() is False:
            return

        self.Lora = LoRaWANSend(self.Params, verbose=True)
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
            self.Lora = LoRaWANOtaa([randrange(256), randrange(256)], self.DevEui,
                                    self.AppEui, self.AppKey, self.Params, verbose=True)
            self._ConfigureLora()
            self.Lora.Start()

    def Disconnect(self):
        pass

    @staticmethod
    def _ReceiveCallback(lora, outgoing):
        payload = lora.read_payload()
        Log.debug("Received: {}".format(payload))
        LoraProtocol._Instance.RecvCallback("none", payload)

    def _ConfigureLora(self):
        self.Lora.set_mode(MODE.SLEEP)
        self.Lora.set_dio_mapping([1, 0, 0, 0, 0, 0])
        self.Lora.set_freq(868.1)
        self.Lora.set_pa_config(pa_select=1)
        self.Lora.set_spreading_factor(12)  # 7
        self.Lora.set_low_data_rate_optim(1)
        self.Lora.set_bw(7)  # 7=125k
        self.Lora.set_pa_config(max_power=0x0F, output_power=0x0F)
        self.Lora.set_sync_word(0x34)
        self.Lora.set_rx_crc(True)
        self.Lora.set_agc_auto_on(1)

        Log.debug(self.Lora)

