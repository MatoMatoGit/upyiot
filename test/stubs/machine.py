from micropython import const

DEEPSLEEP_RESET = const(0)
RTC_WAKE = const(1)

Asleep = False
SleepDuration = 0

def reset_cause():
    return DEEPSLEEP_RESET

def wake_reason():
    return RTC_WAKE

def deepsleep(t=None):
    global Asleep
    global SleepDuration

    print("Going to sleep")
    if t is not None:
        print("for %d seconds" % t)
    Asleep = True
    SleepDuration = t


def is_asleep():
    global Asleep

    return Asleep


def wake_up():
    global Asleep
    global SleepDuration

    Asleep = False
    SleepDuration = 0


def asleep_for():
    global SleepDuration

    return SleepDuration
