try:
    import machine
except:
    from stubs import machine
from micropython import const

RESET_REASON_RESET = const(0)
RESET_REASON_PIN = const(1)
RESET_REASON_RTC = const(2)


def ResetReason():
    # Check the wake-reason to determine if the device was
    # woken from sleep.
    if machine.reset_cause() is machine.DEEPSLEEP_RESET:
        if machine.wake_reason() is machine.PIN_WAKE:
            return RESET_REASON_PIN
        else:
            return RESET_REASON_RTC
    else:
        return RESET_REASON_RESET


def ResetReasonToString(rst_reason):
    if rst_reason is RESET_REASON_RESET:
        return "Reset"
    elif rst_reason is RESET_REASON_RTC:
        return "RTC"
    elif rst_reason is RESET_REASON_PIN:
        return "Pin"
    else:
        return "Unknown"

