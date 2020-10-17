import machine

_DeviceId = ""

def DeviceIdSet(device_id):
    _DeviceId = device_id

def DeviceId():
    if _DeviceId is "":
        return str(ubinascii.hexlify(machine.unique_id()).decode('utf-8'))
    return _DeviceId