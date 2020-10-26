import machine

_DeviceId = None

def DeviceIdSet(device_id):
    _DeviceId = device_id

def DeviceIdString():
    if _DeviceId is None:
        return str(ubinascii.hexlify(machine.unique_id()).decode('utf-8'))
    return str(_DeviceId)

def DeviceId():
    if _DeviceId is None:
        return machine.unique_id()
    return _DeviceId