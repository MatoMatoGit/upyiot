""" Defines the BOARD class that contains the board pin mappings. """

# Copyright 2015 Mayer Analytics Ltd.
#
# This file is part of pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.

from machine import Pin, SPI

import time


class SpiXfer():

    def __init__(self, spi, cs_pin):
        self.Spi = spi
        self.CsPin = cs_pin

    def xfer(self, data):
        response = bytearray(len(data))

        self.CsPin.value(0)

        self.Spi.write_readinto(bytearray(data), response)

        self.CsPin.value(1)

        return response



class BOARD:
    """ Board initialisation/teardown and pin configuration is kept here.
    This is the TTGO LoRa32 board with one LED.
    """

    PIN_SPI_SCK 	= 5
    PIN_SPI_MOSI 	= 27
    PIN_SPI_MISO 	= 19
    PIN_SPI_CS		= 18
    PIN_IRQ			= 26
    PIN_RST			= 14
    PIN_LED  		= 2
    PIN_DIO0		= 26

    # The spi object is kept here
    spi = None

    @staticmethod
    def setup():
        """ Configure the Raspberry GPIOs
        :rtype : None
        """
        
        # blink 2 times to signal the board is set up
        BOARD.blink(.1, 2)

    @staticmethod
    def teardown():
        """ Cleanup GPIO and SpiDev """

    @staticmethod
    def SpiDev(spi_bus=0, spi_cs=0):
        BOARD.SpiSck = Pin(BOARD.PIN_SPI_SCK, Pin.OUT, Pin.PULL_DOWN)
        BOARD.SpiMosi = Pin(BOARD.PIN_SPI_MOSI, Pin.OUT, Pin.PULL_UP)
        BOARD.SpiMiso = Pin(BOARD.PIN_SPI_MISO, Pin.OUT, Pin.PULL_UP)
        BOARD.SpiCs = Pin(BOARD.PIN_SPI_CS, Pin.OUT)
        BOARD.Dio0 = Pin(BOARD.PIN_DIO0, Pin.IN)
        BOARD.Led = Pin(BOARD.PIN_LED, Pin.OUT)

        BOARD.spi = SPI(baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB,
                        sck=BOARD.SpiSck,
                        mosi=BOARD.SpiMosi,
                        miso=BOARD.SpiMiso)

        return SpiXfer(BOARD.spi, BOARD.SpiCs)

    @staticmethod
    def add_event_detect(pin, callback):
        """ Wraps around the GPIO.add_event_detect function
        :param dio_number: DIO pin 0...5
        :param callback: The function to call when the DIO triggers an IRQ.
        :return: None
        """
        pin.irq(trigger=Pin.IRQ_RISING, handler=callback)

    @staticmethod
    def add_events(cb_dio0, cb_dio1, cb_dio2, cb_dio3, cb_dio4, cb_dio5, switch_cb=None):
        BOARD.add_event_detect(BOARD.Dio0, callback=cb_dio0)
        # BOARD.add_event_detect(BOARD.DIO1, callback=cb_dio1)
        # BOARD.add_event_detect(BOARD.DIO2, callback=cb_dio2)
        # BOARD.add_event_detect(BOARD.DIO3, callback=cb_dio3)
        # the modtronix inAir9B does not expose DIO4 and DIO5
        # if switch_cb is not None:
        #    GPIO.add_event_detect(BOARD.SWITCH, GPIO.RISING, callback=switch_cb, bouncetime=300)

    @staticmethod
    def led_on(value=1):
        """ Switch the proto shields LED
        :param value: 0/1 for off/on. Default is 1.
        :return: value
        :rtype : int
        """
        BOARD.Led.value(1)
        return value

    @staticmethod
    def led_off():
        """ Switch LED off
        :return: 0
        """
        BOARD.Led.value(0)
        return 0

    @staticmethod
    def blink(time_sec, n_blink):
        if n_blink == 0:
            return
        BOARD.led_on()
        for i in range(n_blink):
            time.sleep(time_sec)
            BOARD.led_off()
            time.sleep(time_sec)
            BOARD.led_on()
        BOARD.led_off()
