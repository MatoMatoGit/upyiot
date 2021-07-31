try:
    import machine
except ImportError:
    machine = None

import ubinascii

_DeviceId = None


def DeviceIdSet(device_id):
    global _DeviceId
    _DeviceId = device_id


def DeviceIdString():
    global _DeviceId

    if _DeviceId is None:
        return str(ubinascii.hexlify(machine.unique_id()).decode('utf-8'))
    return str(_DeviceId)


def DeviceId():
    global _DeviceId

    if _DeviceId is None:
        return ubinascii.hexlify(machine.unique_id()).decode('utf-8')
    return _DeviceId

