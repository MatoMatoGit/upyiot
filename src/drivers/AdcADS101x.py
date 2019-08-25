from machine import Pin
from micropython import const
import time  

class AdcADS101x(object):
    
    SIZE_REG_BYTES  = const(2)
    SUPPORTED_TYPES = (4, 5)
    MUX_BITS_LOOKUP = (0x04, 0x05, 0x06, 0x07)
    
    ADDR_REG_CONVERSION = const(0x00)
    ADDR_REG_CONFIG     = const(0x01)
    ADDR_REG_LO_THRESH  = const(0x02)
    ADDR_REG_HI_THRESH  = const(0x03)
        
    SHIFT_AMOUNT_CONVERSION_RESULT  = const(4)
    SHIFT_AMOUNT_LO_THRESH          = const(4)
    SHIFT_AMOUNT_HI_THRESH          = const(4)
    SHIFT_AMOUNT_OS                 = const(15)
    SHIFT_AMOUNT_MUX                = const(12)
    SHIFT_AMOUNT_PGA                = const(9)
    SHIFT_AMOUNT_OP_MODE            = const(8)
    SHIFT_AMOUNT_DATA_RATE          = const(5)
    SHIFT_AMOUNT_COMP_MODE          = const(4)
    SHIFT_AMOUNT_COMP_POL           = const(3)
    SHIFT_AMOUNT_COMP_LAT           = const(2)
    SHIFT_AMOUNT_COMP_QUEUE         = const(0)
    
    MASK_CONVERSION_RESULT  = const(0xFFF0) # Conversion result
    MASK_CONFIG_OS          = const(0x8000) # Operation status
    MASK_CONFIG_MUX         = const(0x7000) # Multiplexer control, 1015 only
    MASK_CONFIG_PGA         = const(0x0E00) # Programmable Gain Amplifier
    MASK_CONFIG_OP_MODE     = const(0x0100) # Operating mode
    MASK_CONFIG_DATA_RATE   = const(0x00E0) # Data rate
    MASK_CONFIG_COMP_MODE   = const(0x0010) # Comparator mode, 1014 and 1015 only
    MASK_CONFIG_COMP_POL    = const(0x0008) # Comparator polarity, 1014 and 1015 only
    MASK_CONFIG_COMP_LAT    = const(0x0004) # Comparator latch enable, 1014 and 1015 only
    MASK_CONFIG_COMP_QUEUE  = const(0x0003) # Comparator queue, 1014 and 1015 only
    
        
    
    def __init__(self, ads_type, i2c_addr, done_pin_obj, i2c_obj):
        
        if ads_type not in AdcADS101x.SUPPORTED_TYPES:
            return -1
        
        self.Type = ads_type
        self.Address = i2c_addr;
        
        # Copy the I2C and Pin objects.
        self.I2c = i2c_obj
        self.DonePin = done_pin_obj
        
        # Assign the IRQ handler to the Done pin.
        self.DonePin.irq(trigger=Pin.IRQ_FALLING, handler=self.__IrqHandlerDone)
        
        self.ScratchBuffer = 0x0000
        self.ConversionBuffer = 0x0000
        self.ConversionDone = True
        
        
        
    def ConversionStart(self, channel):
        if not self.ConversionDone:
            return -1
        if channel not in range(0, 4):
            return -1
        
        self.ConversionDone = False
        
        # Set the MUX bits derived from the selected channel.
        self.ScratchBuffer = AdcADS101x.__SetBits(self.__MuxBitsFromChannel(channel),
                                    AdcADS101x.SHIFT_AMOUNT_MUX, 
                                    AdcADS101x.MASK_CONFIG_MUX,
                                    self.ScratchBuffer)
        # Set the OS bit to start the conversion.  
        self.ScratchBuffer = AdcADS101x.__SetBits(1, AdcADS101x.SHIFT_AMOUNT_OS, 
                                    AdcADS101x.MASK_CONFIG_OS,
                                    self.ScratchBuffer)
        # Write the bits to the config register.
        self.__RegisterWrite(AdcADS101x.ADDR_REG_CONFIG, self.ScratchBuffer)
        self.ScratchBuffer = 0x0000
        
        return 0
    
    def ConversionIsDone(self):
        return self.ConversionDone
    
    def ConversionResult(self):
        # Read the conversion result from the conversion register.
        self.ScratchBuffer = self.__RegisterRead(AdcADS101x.ADDR_REG_CONVERSION)
        self.ConversionBuffer = (self.ScratchBuffer & AdcADS101x.MASK_CONVERSION_RESULT) >> AdcADS101x.SHIFT_AMOUNT_CONVERSION_RESULT
        self.ScratchBuffer = 0x0000
        
        return self.ConversionBuffer
    
    def Read(self, channel):
        """ Starts a new conversion and blocks until the conversion
            is done. The conversion result is returned.
        """
        if not self.ConversionDone:
            return 0
        if channel not in range(0, 4):
            return 0
        # Start the conversion.
        self.ConversionStart(channel)
        # Busy-wait until done.
        while not self.ConversionIsDone():
            time.sleep(.5)
        # Read and return the result.
        return self.ConversionResult()
    
    @staticmethod
    def __SetBits(bits, shift_amount, mask, data):
        bits = bits << shift_amount
        data = data | (bits & mask)
        return data
    
    def __MuxBitsFromChannel(self, channel):
        return AdcADS101x.MUX_BITS_LOOKUP[int(channel)]
    
    def __RegisterWrite(self, reg_addr, data):
        self.I2c.writeto_mem(self.Address, reg_addr, data) 
    
    def __RegisterRead(self, reg_addr):
        # Write the to-read register address.
        self.I2c.writeto(self.Address, reg_addr)
        # Read the selected register.
        data = self.I2c.readfrom(self.Address, AdcADS101x.SIZE_REG_BYTES)
        # Data is read as a byte array, MSB first. Shift the data into a 
        # 16-bits variable.
        reg_value = data[1] << 8 | data[0]
        return reg_value
    
    def __IrqHandlerDone(self):
        self.ConversionDone = True
        
        
class AdcChannel(object):
    
    def __init__(self, channel, adc_obj):
        self.Channel = channel
        self.Adc = adc_obj
        
    def Read(self):
        return self.Adc.Read(self.Channel)
        
    