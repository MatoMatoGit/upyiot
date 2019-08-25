

class I2cStub(object):
    
    def __init__(self, write_callback=None, read_callback=None):
        self.CallbackWrite = write_callback
        self.CallbackRead = read_callback
        return
    
    def writeto_mem(self, i2c_addr, mem_addr, data):
        print("I2C write-to-memory")
        print("I2C addr: {}".format(hex(i2c_addr)))
        print("Memory addr: {}".format(hex(mem_addr)))
        print("Data: {}".format(hex(data)))
        if self.CallbackWrite is not None:
            self.CallbackWrite()
        
    def writeto(self, i2c_addr, data):
        print("I2C write-to")
        print("I2C addr: {}".format(hex(i2c_addr)))
        print("Data: {}".format(hex(data)))
        if self.CallbackWrite is not None:
            self.CallbackWrite() 
    
    def readfrom(self, i2c_addr, num_bytes):
        data = bytearray(2)
        data[0] = 0xF0
        data[1]= 0xFF
    
        print("I2C read-from")
        print("I2C addr: {}".format(hex(i2c_addr)))
        print("Number of bytes: {}".format(num_bytes))
        print("Data: ")
        print("".join("\\x%02x" % i for i in data))
        if self.CallbackRead is not None:
            self.CallbackRead()
        return data
    